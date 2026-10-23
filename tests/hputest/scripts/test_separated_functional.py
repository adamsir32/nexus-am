"""逐用例源码必须能直接审阅、定位失败，不退化成共享main转发壳。"""
import csv
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
DEGREE_DIRECTORIES = {128: "01_n128", 1024: "02_n1024", 2048: "03_n2048",
                      4096: "04_n4096", 8192: "05_n8192"}
GROUP_DIRECTORIES = {"03": "03_instructions", "04": "04_operators", "05": "05_library"}


def expected_source(row):
    if row["group"] == "06":
        return Path("src/06_applications") / (row["case_id"] + ".c")
    directory = ("06_parameter_regression" if row["profile"] == "regression"
                 else DEGREE_DIRECTORIES[int(row["degree"])])
    return Path("src") / GROUP_DIRECTORIES[row["group"]] / directory / (row["case_id"] + ".c")


class SeparatedFunctionalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "cases.tsv").open() as stream:
            cls.rows = [row for row in csv.DictReader(stream, delimiter="\t")
                        if row["group"] in ("03", "04", "05", "06") and row["kind"] != "lowlevel"]

    def sources(self):
        for row in self.rows:
            path = expected_source(row)
            yield row, path, (ROOT / path).read_text()

    def test_every_case_has_a_unique_named_main_and_catalog_source(self):
        self.assertEqual(len(self.rows), 601)
        self.assertEqual(len({str(expected_source(row)) for row in self.rows}), len(self.rows))
        for row, path, source in self.sources():
            with self.subTest(case=row["case_id"]):
                self.assertEqual(row["source"], path.as_posix())
                self.assertEqual(path.stem, row["case_id"])
                self.assertEqual(source.count("int main(void)"), 1)
                self.assertGreater(len(source.splitlines()), 60, "不得仅转发共享主函数")
                self.assertNotIn("native_case_run", source)
                self.assertNotIn("WORKLOAD_RUN", source)

    def test_parameters_program_and_reference_are_case_specific(self):
        for row, _, source in self.sources():
            with self.subTest(case=row["case_id"]):
                self.assertIn(f"用例：{row['case_id']}", source)
                self.assertIn(row["purpose"], source)
                self.assertIn(f"_Static_assert(DEGREE == {row['degree']}U,", source)
                self.assertIn(f"_Static_assert(LEVEL == {row['level']}U,", source)
                self.assertIn(f"hpu_run_{row['program_stem']}();", source)
                self.assertIn(f"{row['case_id']}.asm", source)
                self.assertIn("参考：", source)

    def test_stages_checks_and_failure_locations_are_explicit(self):
        expected_order = ("phase_mark(PHASE_PREPARE);", "prepare_image();",
                          "phase_mark(PHASE_CONFIGURE);", "csr_write(CSR_FAULT, FAULT_VALID);",
                          "csr_write(CSR_BASE_LO,", "csr_write(CSR_BASE_HI,",
                          "csr_write(CSR_SIZE_LO,", "csr_write(CSR_SIZE_HI,",
                          "csr_write(CSR_COMMIT, COMMIT);", "if (wait_window() != 0)",
                          "phase_mark(PHASE_ISSUE);", "phase_mark(PHASE_WAIT);",
                          "if (wait_program() != 0)", "phase_mark(PHASE_COMPARE);",
                          "const int data_rc = check_results();",
                          "const int memory_rc = check_memory();", "return case_pass();")
        for row, _, source in self.sources():
            with self.subTest(case=row["case_id"]):
                offsets = [source.index(step) for step in expected_order]
                self.assertEqual(offsets, sorted(offsets))
                self.assertEqual(source.count("if (clear_completion() != 0)"), 2)
                for register in ("CSR_BASE_LO", "CSR_BASE_HI", "CSR_SIZE_LO", "CSR_SIZE_HI"):
                    self.assertIn(f"if (expect_csr({register},", source)
                self.assertIn("if (data_rc != 0)\n        return case_fail_at(__FILE__, __LINE__);", source)
                self.assertIn("if (memory_rc != 0)\n        return case_fail_at(__FILE__, __LINE__);", source)
                failures = re.findall(r"return (case_fail[^;]*);", source)
                self.assertEqual(len(failures), 11)
                self.assertEqual(set(failures), {"case_fail_at(__FILE__, __LINE__)"})
                self.assertNotIn(" || ", source, "多个失败判据不能再压在同一行")
                self.assertNotRegex(source, r"\bpsync\s*\(", "主程序不得额外插入PSYNC")

    @unittest.skipUnless(shutil.which("cc"), "需要主机C编译器检查显式主程序语法")
    def test_representative_mains_compile_with_declared_concrete_programs(self):
        # 全部主程序只有参数和具体程序名不同；每个层级/特殊入口各抽一项检查C接口。
        selected = []
        seen = set()
        for row in self.rows:
            key = (row["group"], row["profile"], row["suite"])
            if key not in seen:
                selected.append(row)
                seen.add(key)
        with tempfile.TemporaryDirectory(prefix="hpu-separated-main-") as temporary:
            include = Path(temporary)
            (include / "hpu").mkdir()
            (include / "hpu/log.h").write_text(
                "#define LOG_EVENT(...) ((void)0)\n#define LOG_DEBUG(...) ((void)0)\n"
                "#define LOG_ERROR(...) ((void)0)\n")
            (include / "workload.h").write_text(
                "#include <stdint.h>\n"
                "enum { PHASE_PREPARE, PHASE_CONFIGURE, PHASE_ISSUE, PHASE_WAIT, PHASE_COMPARE };\n"
                "enum { CSR_FAULT, FAULT_VALID, CSR_BASE_LO, CSR_BASE_HI, CSR_SIZE_LO, CSR_SIZE_HI, CSR_COMMIT, COMMIT };\n"
                "#define MEM_BASE UINT64_C(0x87000000)\n"
                "#define WINDOW_LINES 100U\n"
                "void phase_mark(unsigned); void prepare_image(void);\n"
                "void csr_write(unsigned, uint32_t); int clear_completion(void);\n"
                "int expect_csr(unsigned, uint32_t); int wait_window(void); int wait_program(void);\n"
                "int check_results(void); int check_memory(void);\n"
                "int case_fail_at(const char *, unsigned); int case_pass(void);\n")
            for row in selected:
                with self.subTest(case=row["case_id"]):
                    (include / "program.h").write_text(
                        f"#define DEGREE {row['degree']}U\n#define LEVEL {row['level']}U\n"
                        f"int hpu_run_{row['program_stem']}(void);\n")
                    result = subprocess.run(
                        ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-fsyntax-only", "-I", str(include),
                         str(ROOT / expected_source(row))], text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
