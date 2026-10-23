"""独立07用例的源码身份、参数断言及静默/摘要编译检查。"""
import csv
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def cases():
    with (ROOT / "cases.tsv").open() as stream:
        return [row for row in csv.DictReader(stream, delimiter="\t")
                if row["kind"] == "performance"]


class SeparatedPerformanceTests(unittest.TestCase):
    def test_every_case_has_unique_complete_source_and_failure_location(self):
        rows = cases()
        self.assertEqual(len(rows), 72)
        self.assertEqual(len({row["source"] for row in rows}), len(rows))
        for row in rows:
            with self.subTest(case=row["case_id"]):
                path = ROOT / row["source"]
                self.assertEqual(path.stem, row["case_id"])
                code = path.read_text()
                self.assertIn("int main(void)", code)
                self.assertIn("prepare_image();", code)
                self.assertIn("csr_write(CSR_COMMIT, COMMIT);", code)
                self.assertIn("check_results();", code)
                self.assertIn("check_memory();", code)
                self.assertIn("case_fail_at(__FILE__, __LINE__)", code)
                self.assertNotIn("return case_fail(__LINE__)", code)
                self.assertNotIn("native_case_run", code)
                self.assertIn(f"N={row['degree']}", code)
                self.assertIn(f"level={row['level']}", code)
                self.assertIn(row["case_id"] + ".asm", code)

    @unittest.skipUnless(shutil.which("gcc"), "gcc is required for source syntax checks")
    def test_all_sources_compile_at_silent_and_summary_log_levels(self):
        parent = ROOT / "build/host-tests"
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="separated-perf-", dir=parent) as temporary:
            include = Path(temporary)
            # 只替代硬件/布局声明，日志宏使用项目真实实现；不伪造硬件执行通过。
            (include / "workload.h").write_text(
                "#include <stdint.h>\n"
                "#define MEM_BASE UINT64_C(0x90000000)\n"
                "#define WINDOW_LINES 64U\n"
                "#define CASE_ID \"host-syntax-check\"\n"
                "#define SCHEDULE_PROFILE \"optimized\"\n"
                "#define INSTRUCTION_COUNT 1U\n#define DMA_COUNT 1U\n"
                "enum { PHASE_PREPARE, PHASE_CONFIGURE, PHASE_ISSUE, PHASE_COMPARE };\n"
                "enum { CSR_FAULT, CSR_BASE_LO, CSR_BASE_HI, CSR_SIZE_LO, CSR_SIZE_HI,"
                " CSR_COMMIT, CSR_STATUS };\n"
                "enum { FAULT_VALID=1U, COMMIT=1U, STATUS_VALID=1U,"
                " STATUS_BUSY=2U, STATUS_FAULT=4U };\n"
                "struct progress { uint64_t cycle_start, cycle_end; };\n"
                "extern volatile struct progress workload_trace;\n"
                "void phase_mark(unsigned); void prepare_image(void);\n"
                "void csr_write(unsigned, uint32_t); uint32_t csr_read(unsigned);\n"
                "int clear_completion(void); int expect_csr(unsigned, uint32_t);\n"
                "int wait_window(void); int check_results(void); int check_memory(void);\n"
                "int case_fail_at(const char *, unsigned); int case_pass(void);\n")
            (include / "performance.h").write_text(
                "void perf_cycle_enable(void); uint64_t perf_cycle_read(void);\n"
                "int performance_wait(void);\n")
            (include / "klib.h").write_text("int printf(const char *, ...);\n")
            rows = cases()
            (include / "program.h").write_text("".join(
                f"int hpu_validate_{row['program_stem']}(void);\n"
                f"int hpu_run_{row['program_stem']}(void);\n" for row in rows))
            for row in rows:
                for level in (0, 1):
                    with self.subTest(case=row["case_id"], log_level=level):
                        subprocess.run([
                            "gcc", "-std=gnu11", "-fsyntax-only", "-Wall", "-Wextra", "-Werror",
                            f"-DHPU_LOG_LEVEL={level}", f"-DDEGREE={row['degree']}U",
                            f"-DLEVEL={row['level']}U", "-I" + str(include),
                            "-I" + str(ROOT / "include"), str(ROOT / row["source"])],
                            check=True, capture_output=True, text=True)
            # 源文件中的固定参数断言必须真能拦住错误目录/布局配对。
            first = rows[0]
            mismatch = subprocess.run([
                "gcc", "-std=gnu11", "-fsyntax-only", "-DHPU_LOG_LEVEL=0",
                "-DDEGREE=8192U", "-DLEVEL=1U", "-I" + str(include),
                "-I" + str(ROOT / "include"), str(ROOT / first["source"])],
                capture_output=True, text=True)
            self.assertNotEqual(mismatch.returncode, 0)
            self.assertIn("static assertion failed", mismatch.stderr)


if __name__ == "__main__":
    unittest.main()
