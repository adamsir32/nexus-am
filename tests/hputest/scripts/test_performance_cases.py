import csv
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def catalog():
    with (ROOT / "cases.tsv").open() as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        return [row for row in reader if row["kind"] == "performance"]


class PerformanceCaseTests(unittest.TestCase):
    def test_catalog_has_each_performance_operator_once_per_degree_scheme(self):
        cases = catalog()
        expected = {(str(degree), str(3 if scheme == "bgv" else 4), scheme, operation)
                    for degree in (1024, 2048, 4096, 8192)
                    for scheme in ("ckks", "bfv", "bgv")
                    for operation in ("keyswitch", "hadd", "hmul", "reline", "modswitch", "rotate")}
        actual = {(r["degree"], r["level"], r["scheme"], r["operation"]) for r in cases}
        self.assertEqual(actual, expected)
        self.assertEqual(len(cases), len(actual))
        for row in cases:
            self.assertEqual(row["source"], "src/07_performance/main.c")
            self.assertTrue((ROOT / row["source"]).is_file())

    def test_one_shared_program_keeps_timing_order_without_per_case_source_copies(self):
        sources = {row["source"] for row in catalog()}
        self.assertEqual(sources, {"src/07_performance/main.c"})
        text = (ROOT / next(iter(sources))).read_text()
        self.assertEqual(text.count("WORKLOAD_VALIDATE()"), 1)
        self.assertEqual(text.count("WORKLOAD_RUN()"), 1)
        self.assertEqual(text.count("performance_wait();"), 1)
        self.assertEqual(text.count("perf_cycle_read();"), 2)
        self.assertIsNone(re.search(r"\b(for|while)\s*\(", text))
        self.assertIn("CASE_DEGREE", text)
        self.assertIn("CASE_LEVEL", text)
        start = text.index("cycle_start = perf_cycle_read();")
        end = text.index("cycle_end = perf_cycle_read();")
        self.assertLess(text.index("WORKLOAD_VALIDATE()"), text.index("csr_write(CSR_COMMIT, COMMIT);"))
        self.assertLess(text.index("csr_write(CSR_COMMIT, COMMIT);"), start)
        self.assertLess(start, text.index("WORKLOAD_RUN()"))
        self.assertLess(text.index("WORKLOAD_RUN()"), text.index("performance_wait();"))
        self.assertLess(text.index("performance_wait();"), end)
        timed = text[start:end]
        for forbidden in ("LOG_", "phase_mark", "WORKLOAD_VALIDATE", "clear_completion", "check_results", "check_memory"):
            self.assertNotIn(forbidden, timed)
        self.assertGreater(text.index("workload_trace.cycle_start ="), end)
        self.assertGreater(text.index("workload_trace.cycle_end ="), end)
        self.assertGreater(text.index("verified=1"), text.index("if (data_rc != 0 || memory_rc != 0)"))
        self.assertIn("SCHEDULE_PROFILE", text)

    def test_mmio_wait_order_timeout_and_sparse_trace(self):
        parent = ROOT / "build/host-tests"
        parent.mkdir(parents=True, exist_ok=True)
        directory = Path(tempfile.mkdtemp(prefix="performance-", dir=parent))
        binary = directory / "performance-test"
        try:
            subprocess.run(["gcc", "-std=gnu11", "-O2", "-Wall", "-Wextra", "-Werror",
                            "-DWORKLOAD_HOST_TEST", "-DWAIT_CYCLES=1024",
                            "-I" + str(ROOT / "test/host/include"), "-I" + str(ROOT / "include"),
                            str(ROOT / "test/host/performance_test.c"),
                            str(ROOT / "runtime/native/performance.c"), "-o", str(binary)], check=True)
            subprocess.run([str(binary)], check=True)
        finally:
            if binary.exists():
                binary.unlink()
            directory.rmdir()

    def test_make_selects_timed_program_only_for_performance_cases(self):
        args = ["make", "-s", "-C", str(ROOT), "-f", "Makefile.native.case", "performance-probe",
                f"AM_HOME={ROOT / 'test/build-isolation'}", "CASE_ID=timing-probe", "CASE_SOURCE=probe.c",
                "DATA_DIR=/probe", "PROGRAM_STEM=producer", "CASE_OBJ_DIR=/probe/objects",
                "CASE_BINARY=/probe/output", "LOG_LEVEL=1", "WAIT_CYCLES=1024",
                "CASE_DEGREE=4096", "CASE_LEVEL=4",
                "--eval=performance-probe: ; @printf 'sources=%s\\nflags=%s\\n' '$(SRCS)' '$(CFLAGS)'"]
        regular = subprocess.check_output(args, text=True)
        timed = subprocess.check_output(args + ["PERFORMANCE=1", "CASE_MEM_BASE=0xc0000000"], text=True)
        self.assertIn("/probe/producer.c", regular)
        self.assertNotIn("producer_perf.c", regular)
        self.assertNotIn("runtime/native/performance.c", regular)
        self.assertIn("/probe/producer_perf.c", timed)
        self.assertNotIn("/probe/producer.c", timed)
        self.assertIn("runtime/it_perf.c", timed)
        self.assertIn("runtime/native/performance.c", timed)
        self.assertIn("-DMEM_BASE=0xc0000000ULL", timed)


if __name__ == "__main__":
    unittest.main()
