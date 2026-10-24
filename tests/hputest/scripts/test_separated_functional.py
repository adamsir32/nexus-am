"""逐用例源码必须能直接审阅、定位失败，不退化成共享main转发壳。"""
import csv
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
GROUP_DIRECTORIES = {"03": "03_instructions", "04": "04_operators", "05": "05_library"}
PSYNC_REGRESSION = "03_08_psync_l4_n1024"


def expected_source(row):
    if row["group"] == "06":
        return Path("src/06_applications") / (row["case_id"] + ".c")
    return Path("src") / GROUP_DIRECTORIES[row["group"]] / (row["case_id"] + ".c")


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
        self.assertEqual(len(self.rows), 44)
        self.assertEqual([sum(row["group"] == group for row in self.rows)
                          for group in ("03", "04", "05", "06")], [9, 6, 15, 14])
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
                if row["case_id"] == PSYNC_REGRESSION:
                    for prefix in ("idle", "dma", "compute"):
                        self.assertIn(f"hpu_run_{row['program_stem']}_{prefix}();", source)
                    self.assertNotIn(f"hpu_run_{row['program_stem']}();", source)
                else:
                    self.assertIn(f"hpu_run_{row['program_stem']}();", source)
                self.assertIn(f"{row['case_id']}.asm", source)
                self.assertIn("参考：", source)

    def test_stages_checks_and_failure_locations_are_explicit(self):
        expected_order = ("phase_mark(PHASE_PREPARE);", "prepare_image();",
                          "phase_mark(PHASE_CONFIGURE);", "csr_write(CSR_FAULT, FAULT_VALID);",
                          "csr_write(CSR_BASE_LO,", "csr_write(CSR_BASE_HI,",
                          "csr_write(CSR_SIZE_LO,", "csr_write(CSR_SIZE_HI,",
                          "csr_write(CSR_COMMIT, COMMIT);", "if (wait_window() != 0)",
                          "if (irq_reset_events() != 0)", "if (irq_open() != 0)",
                          "if (irq_event_count() != 0U)", "if (irq_handler_count() != 0U)",
                          "phase_mark(PHASE_ISSUE);", "phase_mark(PHASE_WAIT);",
                          "const int wait_rc = wait_program();", "if (wait_rc != 0)",
                          "if (irq_event_count() != 1U)", "if (irq_handler_count() != 1U)",
                          "if ((csr_read(CSR_IRQ) & IRQ_LEVEL) != 0U)", "phase_mark(PHASE_COMPARE);",
                          "const int data_rc = check_results();",
                          "const int memory_rc = check_memory();", "return case_pass();")
        for row, _, source in self.sources():
            with self.subTest(case=row["case_id"]):
                if row["case_id"] == PSYNC_REGRESSION:
                    continue  # 三个真实prefix的六轮流程由独立验收检查。
                offsets = [source.index(step) for step in expected_order]
                self.assertEqual(offsets, sorted(offsets))
                # 只允许COMMIT前清旧状态；本轮完成后不能用main补清掩盖ISR遗漏。
                self.assertEqual(source.count("if (clear_completion() != 0)"), 1)
                self.assertLess(source.index("clear_completion()"), source.index("csr_write(CSR_COMMIT, COMMIT);"))
                wait = source.index("const int wait_rc = wait_program();")
                close = source.index("irq_close();", wait)
                self.assertLess(close, source.index("if (wait_rc != 0)"))
                self.assertLess(close, source.index('irq_diagnose("program-wait", 0U);'))
                self.assertEqual(source.count("irq_open()"), 1)
                self.assertEqual(source.count("irq_close();"), 5)
                self.assertIn("if (program_rc != 0) {\n        irq_close();", source)
                for register in ("CSR_BASE_LO", "CSR_BASE_HI", "CSR_SIZE_LO", "CSR_SIZE_HI"):
                    self.assertIn(f"if (expect_csr({register},", source)
                self.assertIn("if (data_rc != 0)\n        return case_fail_at(__FILE__, __LINE__);", source)
                self.assertIn("if (memory_rc != 0)\n        return case_fail_at(__FILE__, __LINE__);", source)
                failures = re.findall(r"return (case_fail[^;]*);", source)
                self.assertEqual(len(failures), 17)
                self.assertEqual(set(failures), {"case_fail_at(__FILE__, __LINE__)"})
                self.assertNotIn(" || ", source, "多个失败判据不能再压在同一行")
                self.assertNotRegex(source, r"\bpsync\s*\(", "主程序不得额外插入PSYNC")

    def test_psync_root_cause_regression_uses_three_real_prefixes_and_six_isr_events(self):
        row = next(row for row in self.rows if row["case_id"] == PSYNC_REGRESSION)
        source = (ROOT / expected_source(row)).read_text()
        self.assertIn("scenario < 3U", source)
        self.assertIn("round < 2U", source)
        self.assertIn("arm_rc = round == 0U ? irq_open() : irq_rearm();", source)
        self.assertIn("if (round == 1U) irq_close();", source)
        self.assertEqual(source.count("irq_reset_events()"), 1)
        self.assertLess(source.index("irq_reset_events()"), source.index("for (unsigned scenario"))
        self.assertIn("if (irq_event_count() != before)", source)
        self.assertIn("if (irq_handler_count() != before)", source)
        self.assertIn("if (irq_poll() != 0)", source)
        self.assertIn("if (irq_event_count() != before + 1U)", source)
        self.assertIn("if (irq_handler_count() != before + 1U)", source)
        self.assertIn("if (irq_cte_init_count() != 1U)", source)
        self.assertIn("if (irq_event_count() != 6U)", source)
        self.assertIn("if (irq_handler_count() != 6U)", source)
        self.assertEqual(source.count("clear_completion()"), 1)
        self.assertLess(source.index("clear_completion()"), source.index("csr_write(CSR_COMMIT, COMMIT);"))
        self.assertIn("if ((csr_read(CSR_IRQ) & IRQ_LEVEL) != 0U)", source)
        self.assertIn("golden_words[out->golden_word + word]", source)
        self.assertIn("initial_image[out->line * LINE_WORDS + word]", source)
        self.assertLess(source.index("invalidate_lines(IMAGE_LINES);"), source.index("actual[word]"))
        self.assertIn("const int memory_rc = check_memory();", source)
        self.assertNotRegex(source, r"\bpsync\s*\(")
        self.assertNotIn(".word", source)

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
        selected.append(next(row for row in self.rows if row["case_id"] == PSYNC_REGRESSION))
        with tempfile.TemporaryDirectory(prefix="hpu-separated-main-") as temporary:
            include = Path(temporary)
            (include / "hpu").mkdir()
            (include / "hpu/log.h").write_text(
                "#define LOG_EVENT(...) ((void)0)\n#define LOG_DEBUG(...) ((void)0)\n"
                "#define LOG_ERROR(...) ((void)0)\n")
            (include / "workload.h").write_text(
                "#include <stdint.h>\n"
                "enum { PHASE_PREPARE, PHASE_CONFIGURE, PHASE_ISSUE, PHASE_WAIT, PHASE_COMPARE };\n"
                "enum { CSR_FAULT, FAULT_VALID, CSR_BASE_LO, CSR_BASE_HI, CSR_SIZE_LO, CSR_SIZE_HI, CSR_COMMIT, COMMIT, CSR_IRQ, IRQ_LEVEL };\n"
                "#define MEM_BASE UINT64_C(0x87000000)\n"
                "#define WINDOW_LINES 100U\n"
                "#define LINE_WORDS 64U\n#define IMAGE_LINES 100U\n#define OUTPUT_COUNT 8U\n"
                "struct output_span { unsigned line, words, golden_word, modulus, step, component, modulus_id; };\n"
                "extern const struct output_span outputs[OUTPUT_COUNT];\n"
                "extern const uint32_t initial_image[], golden_words[];\n"
                "struct progress { uint32_t errors, first_line, first_word, actual, expected; };\n"
                "extern volatile struct progress workload_trace;\n"
                "void invalidate_lines(unsigned); volatile uint32_t *line_ptr(unsigned);\n"
                "void phase_mark(unsigned); void prepare_image(void);\n"
                "void csr_write(unsigned, uint32_t); uint32_t csr_read(unsigned); int clear_completion(void);\n"
                "int expect_csr(unsigned, uint32_t); int wait_window(void); int wait_program(void);\n"
                "int check_results(void); int check_memory(void);\n"
                "int case_fail_at(const char *, unsigned); int case_pass(void);\n")
            for row in selected:
                with self.subTest(case=row["case_id"]):
                    (include / "program.h").write_text(
                        f"#define DEGREE {row['degree']}U\n#define LEVEL {row['level']}U\n"
                        f"int hpu_run_{row['program_stem']}(void);\n")
                    if row["case_id"] == PSYNC_REGRESSION:
                        for prefix in ("idle", "dma", "compute"):
                            (include / f"{row['program_stem']}_{prefix}.h").write_text(
                                f"int hpu_run_{row['program_stem']}_{prefix}(void);\n")
                    result = subprocess.run(
                        ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-fsyntax-only", "-I", str(include),
                         "-I", str(ROOT / "include"),
                         str(ROOT / expected_source(row))], text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
