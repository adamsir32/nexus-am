import csv
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT.parent / "hputest"
FIELDS = ["case_id", "baseline_case_id", "scheme", "operation", "degree", "level",
          "program_stem", "source", "memory_base", "minimum_ram_bytes", "metric"]


def catalog():
    with (ROOT / "performance-cases.tsv").open() as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if reader.fieldnames != FIELDS:
            raise ValueError("unexpected frontend performance columns")
        return list(reader)


class PerformanceCaseTests(unittest.TestCase):
    def test_default_performance_entry_uses_n8192_and_baseline(self):
        environment = {key: value for key, value in os.environ.items()
                       if key not in ("DEGREE", "PROFILE", "MAKEFLAGS")}
        command = subprocess.check_output(
            ["make", "-s", "-n", "-C", str(ROOT), "performance"],
            text=True, env=environment)
        self.assertIn('--degree "8192" --profile "baseline"', command)

    def test_catalog_matches_baseline_operation_parameters_and_memory(self):
        cases = catalog()
        with (BASELINE / "perf-cases.tsv").open() as stream:
            baseline = {row["case_id"]: row for row in csv.DictReader(stream, delimiter="\t")}
        self.assertEqual(len(cases), 36)
        self.assertEqual([int(row["case_id"].split("_")[1]) for row in cases], list(range(1, 19)) + list(range(37, 55)))
        self.assertEqual(len({row["baseline_case_id"] for row in cases}), 36)
        expected = []
        for degree in (4096, 8192):
            for profile in ("baseline",):
                for scheme in ("ckks", "bfv", "bgv"):
                    for operation in ("keyswitch", "hadd", "hmul", "reline", "modswitch", "rotate"):
                        level = 3 if scheme == "bgv" else 4
                        expected.append((str(degree), str(level), scheme, operation))
        self.assertEqual([(r["degree"], r["level"], r["scheme"], r["operation"]) for r in cases], expected)
        for row in cases:
            original = baseline[row["baseline_case_id"]]
            for field in ("degree", "level", "memory_base", "minimum_ram_bytes", "metric"):
                self.assertEqual(row[field], original[field], (row["case_id"], field))
            expected_stem = f"frontend_{row['scheme']}_{row['operation']}_l{row['level']}_n{row['degree']}"
            self.assertEqual(row["program_stem"], expected_stem)
            display = "hmul_reline" if row["operation"] == "hmul" else \
                      "rescale" if row["scheme"] == "ckks" and row["operation"] == "modswitch" else row["operation"]
            self.assertTrue(row["case_id"].endswith(f"_{row['scheme']}_{display}_l{row['level']}_n{row['degree']}"))
            self.assertEqual(Path(row["source"]).stem, row["case_id"])
            self.assertTrue((ROOT / row["source"]).is_file())

    def test_one_program_and_timing_order_in_every_case(self):
        for row in catalog():
            text = (ROOT / row["source"]).read_text()
            stem = row["program_stem"]
            self.assertEqual(text.count(f"hpu_validate_{stem}();"), 1)
            self.assertEqual(text.count(f"hpu_run_{stem}();"), 1)
            self.assertEqual(text.count("performance_wait();"), 1)
            self.assertEqual(text.count("perf_cycle_read();"), 2)
            self.assertIsNone(re.search(r"\b(for|while)\s*\(", text))
            start = text.index("cycle_start = perf_cycle_read();")
            end = text.index("cycle_end = perf_cycle_read();")
            self.assertLess(text.index(f"hpu_validate_{stem}();"), text.index("csr_write(CSR_COMMIT, COMMIT);"))
            self.assertLess(text.index("csr_write(CSR_COMMIT, COMMIT);"), start)
            self.assertLess(start, text.index(f"hpu_run_{stem}();"))
            self.assertLess(text.index(f"hpu_run_{stem}();"), text.index("performance_wait();"))
            self.assertLess(text.index("performance_wait();"), end)
            timed = text[start:end]
            for forbidden in ("LOG_", "phase_mark", "hpu_validate_", "clear_completion", "check_results", "check_memory"):
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
                            "-I" + str(BASELINE / "include"),
                            str(ROOT / "test/host/performance_test.c"),
                            str(ROOT / "runtime/performance.c"), "-o", str(binary)], check=True)
            subprocess.run([str(binary)], check=True)
        finally:
            if binary.exists():
                binary.unlink()
            directory.rmdir()

    def test_make_selects_timed_program_only_for_performance_cases(self):
        args = ["make", "-s", "-C", str(ROOT), "-f", "Makefile.case", "performance-probe",
                f"AM_HOME={ROOT / 'test/build-isolation'}", "CASE_ID=timing-probe", "CASE_SOURCE=probe.c",
                "DATA_DIR=/probe", "PROGRAM_STEM=producer", "CASE_OBJ_DIR=/probe/objects",
                "CASE_BINARY=/probe/output", "LOG_LEVEL=1", "WAIT_CYCLES=1024",
                "--eval=performance-probe: ; @printf 'sources=%s\\nflags=%s\\n' '$(SRCS)' '$(CFLAGS)'"]
        regular = subprocess.check_output(args, text=True)
        timed = subprocess.check_output(args + ["PERFORMANCE=1", "CASE_MEM_BASE=0xc0000000"], text=True)
        self.assertIn("/probe/producer.c", regular)
        self.assertNotIn("producer_perf.c", regular)
        self.assertNotIn("runtime/performance.c", regular)
        self.assertIn("/probe/producer_perf.c", timed)
        self.assertNotIn("/probe/producer.c", timed)
        self.assertIn("runtime/it_perf.c", timed)
        self.assertIn("runtime/performance.c", timed)
        self.assertIn("-DMEM_BASE=0xc0000000ULL", timed)


if __name__ == "__main__":
    unittest.main()
