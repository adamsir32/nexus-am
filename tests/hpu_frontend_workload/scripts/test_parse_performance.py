"""以下cycle数字只用于解析器单测，不是HPU/FPGA实测性能。"""

import csv
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from parse_performance import find_catalog, load_catalog, parse, summarize


ROOT = Path(__file__).resolve().parents[1]
CASE = "07_38_ckks_hadd_l4_n4096"
REVISION = "unit-fixture-only;not-a-hardware-result"


def record(case=CASE, variant="optimized", degree=4096, level=4, start=100, end=180, cycles=80):
    return (f"[HPU][NEWAPI-PERF] case={case} variant={variant} N={degree} level={level} "
            f"metric=issue_to_done_v2 start={start} end={end} cycles={cycles} verified=1\n")


class ParsePerformanceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="frontend-perf-parser-test-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.log = self.directory / "unit-fixture.log"
        self.catalog = load_catalog(ROOT / "performance-cases.tsv")

    def read(self, content):
        self.log.write_text(content)
        return parse([self.log], self.catalog, REVISION)

    def test_multiple_rounds_keep_variants_separate_and_compare_means(self):
        samples = self.read("UART start\n[HPU][NEWAPI-PERF][START] not timed\n" + record() + record(start=200, end=320, cycles=120) +
                            record(variant="noopt", start=100, end=280, cycles=180) +
                            record(variant="noopt", start=300, end=520, cycles=220))
        result = summarize(samples)
        optimized, noopt = result
        self.assertEqual((optimized["rounds"], optimized["average_cycles"], optimized["minimum_cycles"],
                          optimized["maximum_cycles"], optimized["spread_cycles"]), (2, 100, 80, 120, 40))
        self.assertEqual(optimized["noopt_over_optimized"], 2)
        self.assertEqual(noopt["average_cycles"], 200)
        self.assertIsNone(noopt["noopt_over_optimized"])
        self.assertTrue(all(row["revision"] == REVISION for row in samples + result))
        self.assertEqual(samples[0]["line"], 3)

    def test_missing_variant_does_not_create_samples_or_zero_ratio(self):
        result = summarize(self.read(record(variant="noopt")))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["variant"], "noopt")
        self.assertIsNone(result[0]["noopt_over_optimized"])
        result = summarize(self.read(record()))
        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0]["noopt_over_optimized"])

    def test_wrong_case_or_parameter_is_rejected(self):
        for content in (record(case="unknown_l4_n4096"), record(level=16), record(degree=8192)):
            with self.subTest(content=content), self.assertRaisesRegex(ValueError, "case/N/level"):
                self.read(content)

    def test_unsigned_endpoints_wrap_and_reject_invalid_differences(self):
        samples = self.read(record(start=(1 << 64) - 4, end=6, cycles=10))
        self.assertEqual(samples[0]["cycles"], 10)
        for content in (record(end=181), record(end=100, cycles=0),
                        record(start=1 << 64), record(end=1 << 64), record(cycles=1 << 64)):
            with self.subTest(content=content), self.assertRaisesRegex(ValueError, "64-bit"):
                self.read(content)

    def test_incomplete_unverified_or_old_metric_is_not_accepted(self):
        for content in (record().replace("verified=1", "verified=0"),
                        record().replace("issue_to_done_v2", "issue_to_done"),
                        record().replace("variant=optimized", "variant=unknown"),
                        record().replace(" cycles=80 verified=1", "")):
            with self.subTest(content=content), self.assertRaisesRegex(ValueError, "incomplete"):
                self.read(content)
        with self.assertRaisesRegex(ValueError, "no verified"):
            self.read("[HPU][NEWAPI-PERF][START] not a completed measurement\n")

    def test_mixed_revision_is_not_compared(self):
        samples = self.read(record() + record(variant="noopt"))
        samples[1]["revision"] = "another-unit-fixture"
        with self.assertRaisesRegex(ValueError, "different parameters or revisions"):
            summarize(samples)

    def test_repository_and_unpacked_package_catalog_discovery(self):
        self.assertEqual(find_catalog(), ROOT / "performance-cases.tsv")
        package = self.directory / "package"
        (package / "tools").mkdir(parents=True)
        manifest = package / "performance-cases.tsv"
        manifest.write_text((ROOT / "performance-cases.tsv").read_text())
        self.assertEqual(find_catalog(package / "tools/parse_performance.py"), manifest)
        self.assertEqual(load_catalog(manifest)[CASE], {"degree": 4096, "level": 4})

    def test_cli_records_revision_and_leaves_absent_ratio_blank(self):
        self.log.write_text(record())
        output = self.directory / "result"
        subprocess.run([sys.executable, str(ROOT / "scripts/parse_performance.py"), str(self.log),
                        "--output", str(output), "--revision", REVISION], check=True,
                       stdout=subprocess.PIPE, text=True)
        with (output / "summary.csv").open() as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["noopt_over_optimized"], "")
        self.assertEqual(rows[0]["revision"], REVISION)
        with (output / "samples.csv").open() as stream:
            sample = next(csv.DictReader(stream))
        self.assertEqual(sample["log"], str(self.log))


if __name__ == "__main__":
    unittest.main()
