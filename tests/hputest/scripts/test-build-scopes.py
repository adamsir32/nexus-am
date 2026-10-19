#!/usr/bin/env python3
"""分片必须互斥且完整覆盖原用例，不能用空包或重复包掩盖遗漏。"""
import collections
import os
from pathlib import Path
import subprocess
import unittest

from case_catalog import application_specs, large_specs, performance_specs, select_cases


class BuildScopes(unittest.TestCase):
    def test_functional_and_twenty_one_performance_shards_partition_all_cases(self):
        counts = collections.Counter(row["case_id"] for row in select_cases("functional"))
        self.assertEqual(len(counts), 140)
        scopes = []
        for degree in (4096, 8192, 16384, 32768, 65536):
            profiles = ["baseline", "l16-ckks", "l16-bgv"]
            profiles += ["l16-bfv-a", "l16-bfv-b"] if degree == 65536 else ["l16-bfv"]
            scopes.extend(f"performance:{degree}:{profile}" for profile in profiles)
        self.assertEqual(len(scopes), 21)
        for scope in scopes:
            cases = select_cases(scope)
            self.assertEqual(len(performance_specs(scope)), len(cases))
            counts.update(row["case_id"] for row in cases)
            producer_stems = set(application_specs(scope)) | {r["program_stem"] for r in large_specs(scope)}
            self.assertEqual(producer_stems, {r["program_stem"] for r in performance_specs(scope)})
        self.assertEqual(set(counts), {r["case_id"] for r in select_cases()})
        self.assertEqual(set(counts.values()), {1})

    def test_functional_does_not_generate_performance_only_data(self):
        self.assertEqual(performance_specs("functional"), [])
        self.assertEqual(len(large_specs("functional")), 13)
        self.assertTrue(all("_l16_" not in stem for stem in application_specs("functional")))
        self.assertTrue(all(r["case_id"].startswith(("04_", "05_", "06_"))
                            for r in application_specs("functional").values()))

    def test_scope_cli_uses_environment_and_preserves_empty_columns(self):
        script = Path(__file__).with_name("case_catalog.py")
        result = subprocess.check_output(["python3", str(script), "--table", "performance"],
                                         env=dict(os.environ, HPU_BUILD_SCOPE="performance:4096:l16-bfv"), text=True)
        lines = result.splitlines()
        self.assertEqual(len(lines), 7)
        self.assertTrue(all(len(line.split("\t")) == 10 for line in lines))
        self.assertTrue(all(line.split("\t")[1] == "" for line in lines[1:]))

    def test_invalid_or_empty_shards_fail(self):
        for scope in ("", "performance:1024:baseline", "performance:4096:unknown", "performance:4096:l16-bfv-a",
                      "performance:65536:l16-ckks-b", "../functional"):
            with self.subTest(scope=scope), self.assertRaises(ValueError):
                select_cases(scope)


if __name__ == "__main__":
    unittest.main()
