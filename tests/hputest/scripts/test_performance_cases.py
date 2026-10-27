import csv
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
DEGREE_DIRECTORIES = {"1024": "01_n1024", "8192": "02_n8192"}

# 官方renderer的共享C ABI；仅供无生成包的host语法/状态机fixture使用。
PROFILE_ABI_HEADER = """#include <stddef.h>
#include <stdint.h>
#ifndef HPU_EXECUTION_PROFILE_TYPES_DEFINED
#define HPU_EXECUTION_PROFILE_TYPES_DEFINED
typedef struct hpu_execution_profile_hooks {
    void *user;
    uint64_t (*read_cycles)(void *user);
    int (*wait_complete)(void *user, size_t sync_index);
} hpu_execution_profile_hooks_t;
typedef struct hpu_execution_profile_sample {
    uint64_t start_cycles;
    uint64_t end_cycles;
    int valid;
} hpu_execution_profile_sample_t;
#endif
"""


def catalog():
    with (ROOT / "cases.tsv").open() as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        return [row for row in reader if row["kind"] == "performance"]


class PerformanceCaseTests(unittest.TestCase):
    def test_catalog_has_each_performance_operator_once_per_degree_scheme(self):
        cases = catalog()
        expected = {(str(degree), "4", scheme, operation)
                    for degree in (1024, 8192)
                    for scheme in ("ckks", "bfv", "bgv")
                    for operation in ("keyswitch", "hadd", "hmul", "reline", "modswitch", "rotate")}
        actual = {(r["degree"], r["level"], r["scheme"], r["operation"]) for r in cases}
        self.assertEqual(actual, expected)
        self.assertEqual(len(cases), len(actual))
        self.assertEqual(len(cases), 36)
        self.assertEqual([row["case_id"].split("_")[1] for row in cases],
                         [f"{number:02d}" for number in range(1, 37)])
        for row in cases:
            expected_source = (f"src/07_performance/{DEGREE_DIRECTORIES[row['degree']]}/"
                               f"{row['case_id']}.c")
            self.assertEqual(row["source"], expected_source)
            self.assertTrue((ROOT / row["source"]).is_file())

    def test_each_source_calls_the_official_continuous_profiled_entry(self):
        cases = catalog()
        self.assertEqual(len({row["source"] for row in cases}), len(cases))
        for row in cases:
            with self.subTest(case=row["case_id"]):
                text = (ROOT / row["source"]).read_text()
                runner = "hpu_run_" + row["program_stem"] + "_profiled(&state.hooks, &sample)"
                self.assertEqual(text.count(runner), 1)
                self.assertNotIn("hpu_validate_", text)
                self.assertNotIn("hpu_run_" + row["program_stem"] + "()", text)
                self.assertNotIn("WORKLOAD_RUN", text)
                self.assertNotIn("WORKLOAD_VALIDATE", text)
                self.assertNotIn("native_case_run", text)
                self.assertNotIn("performance_wait();", text)
                self.assertNotIn("perf_cycle_read();", text)
                self.assertIsNone(re.search(r"\b(for|while)\s*\(", text))
                self.assertIn("_Static_assert(DEGREE == " + row["degree"] + "U", text)
                self.assertIn("_Static_assert(LEVEL == " + row["level"] + "U", text)
                self.assertIn(row["case_id"] + ".asm", text)
                self.assertIn("case_fail_at(__FILE__, __LINE__)", text)
                start = text.index("rc = " + runner + ";")
                end = text.index("irq_close();", start)
                self.assertLess(text.index("csr_write(CSR_COMMIT, COMMIT);"), start)
                self.assertLess(text.index("perf_cycle_enable();"), text.index("irq_open()"))
                self.assertLess(text.index("wait_window()"), text.index("irq_reset_events()"))
                self.assertLess(text.index("irq_reset_events()"), text.index("irq_open()"))
                self.assertLess(text.index("irq_open()"), text.index("if (irq_event_count() != 0U)"))
                self.assertLess(text.index("if (irq_event_count() != 0U)"), start)
                self.assertLess(text.index("if (irq_handler_count() != 0U)"), start)
                self.assertLess(text.index("performance_profile_init(&state, PROFILE_SYNC_COUNT)"), start)
                self.assertEqual(text.count("clear_completion()"), 1)
                self.assertLess(text.index("clear_completion()"), text.index("csr_write(CSR_COMMIT, COMMIT);"))
                # 完整profiled入口内由官方两次callback决定窗口，main不增加端点或分段等待。
                timed = re.sub(r"\s+", " ", text[start:end]).strip()
                self.assertEqual(timed, "rc = " + runner + ";")
                for forbidden in ("LOG_", "phase_mark", "validate_", "clear_completion",
                                  "prepare_image", "check_results", "check_memory", "irq_open",
                                  "irq_close", "irq_event_count", "irq_handler_count", "irq_diagnose"):
                    self.assertNotIn(forbidden, timed)
                close = end
                self.assertLess(close, text.index("performance_profile_finish(&state, &sample, rc)"))
                self.assertLess(close, text.index('irq_diagnose("execution-profile", 0U);'))
                self.assertGreater(text.index("csr_read(CSR_IRQ)"), close)
                self.assertGreater(text.index("workload_trace.cycle_start ="), end)
                self.assertGreater(text.index("workload_trace.cycle_end ="), end)
                self.assertGreater(text.index("verified=1"), text.index("if (memory_rc != 0)"))
                self.assertIn("metric=execution_window_irq_v1 completion=plic_irq profile=continuous", text)
                self.assertIn("prefix_dstore_count=%u", text)
                self.assertIn("suffix_dload_count=%u", text)
                for name in ("PROFILE_SYNC_COUNT", "PROFILE_WINDOW_DLOAD_COUNT", "PROFILE_WINDOW_DSTORE_COUNT",
                             "PROFILE_PREFIX_DLOAD_COUNT", "PROFILE_PREFIX_DSTORE_COUNT",
                             "PROFILE_SUFFIX_DLOAD_COUNT", "PROFILE_SUFFIX_DSTORE_COUNT"):
                    self.assertIn(name, text)
                self.assertIn("workload_trace.cycle_start = sample.start_cycles;", text)
                self.assertIn("workload_trace.cycle_end = sample.end_cycles;", text)
                self.assertIn("SCHEDULE_PROFILE", text)

    def test_irq_wait_order_timeout_and_sparse_trace(self):
        parent = ROOT / "build/host-tests"
        parent.mkdir(parents=True, exist_ok=True)
        directory = Path(tempfile.mkdtemp(prefix="performance-", dir=parent))
        binary = directory / "performance-test"
        try:
            (directory / "program.h").write_text(PROFILE_ABI_HEADER)
            subprocess.run(["gcc", "-std=gnu11", "-O2", "-Wall", "-Wextra", "-Werror",
                            "-DWORKLOAD_HOST_TEST", "-DWAIT_CYCLES=1024",
                            "-I" + str(directory),
                            "-I" + str(ROOT / "test/host/include"), "-I" + str(ROOT / "include"),
                            str(ROOT / "test/host/performance_test.c"),
                            str(ROOT / "runtime/native/wait.c"),
                            str(ROOT / "runtime/native/performance.c"), "-o", str(binary)], check=True)
            subprocess.run([str(binary)], check=True)
        finally:
            if binary.exists():
                binary.unlink()
            (directory / "program.h").unlink()
            directory.rmdir()

    def test_make_links_official_profiled_source_for_performance_cases(self):
        args = ["make", "-s", "-C", str(ROOT), "-f", "Makefile.native.case", "performance-probe",
                f"AM_HOME={ROOT / 'test/build-isolation'}", "CASE_ID=timing-probe", "CASE_SOURCE=probe.c",
                "DATA_DIR=/probe", "PROGRAM_STEM=producer", "CASE_OBJ_DIR=/probe/objects",
                "CASE_BINARY=/probe/output", "LOG_LEVEL=1", "WAIT_CYCLES=1024",
                "CASE_DEGREE=1024", "CASE_LEVEL=4",
                "--eval=performance-probe: ; @printf 'sources=%s\\nflags=%s\\n' '$(SRCS)' '$(CFLAGS)'"]
        regular = subprocess.check_output(args, text=True)
        timed = subprocess.check_output(args + ["PERFORMANCE=1", "CASE_MEM_BASE=0xc0000000"], text=True)
        self.assertIn("/probe/producer.c", regular)
        self.assertNotIn("producer_perf.c", regular)
        self.assertNotIn("runtime/native/performance.c", regular)
        self.assertIn("/probe/producer.c", timed)
        self.assertNotIn("producer_perf.c", timed)
        self.assertIn("runtime/it_perf.c", timed)
        self.assertIn("runtime/native/performance.c", timed)
        self.assertIn("-DMEM_BASE=0xc0000000ULL", timed)


if __name__ == "__main__":
    unittest.main()
