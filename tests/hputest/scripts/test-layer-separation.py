#!/usr/bin/env python3
"""04只做基本/组合算子，05做算法库；防止重复条目重新混入默认清单。"""
import csv
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def rows(name):
    with (ROOT / name).open() as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


class LayerTests(unittest.TestCase):
    def test_numeric_names_and_lossless_migration(self):
        cases = rows("cases.tsv")
        children = rows("subtests/cases.tsv")
        migration = rows("case-migration.tsv")
        aliases = {r["previous_case_id"]: r["case_id"] for r in rows("case-aliases.tsv")}
        current = {r["case_id"]: r for r in cases}
        current.update({r["subtest_id"]: dict(r, qualifier="software-self-check") for r in children})
        self.assertEqual((len(cases), len(children), len(migration)), (115, 37, 152))
        self.assertEqual({r["case_id"] for r in migration}, set(current))
        self.assertEqual(len({r["previous_case_id"] for r in migration}), 152)
        self.assertEqual(sum(r["qualifier"] == "blocked-not-issued" for r in cases), 11)
        for row in migration:
            with self.subTest(case=row["case_id"]):
                self.assertRegex(row["case_id"], r"^0[0-7]_[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
                self.assertEqual(row["case_id"][:2], Path(row["source"]).parts[1][:2])
                self.assertEqual(current[row["case_id"]]["source"], row["source"])
                self.assertEqual(current[row["case_id"]]["qualifier"], row["qualifier"])
                self.assertEqual(aliases[row["previous_case_id"]], row["case_id"])
                self.assertFalse((ROOT / row["previous_source"]).exists())
        self.assertFalse(set(aliases) & set(current), "aliases must not shadow current names")

    def test_normal_paths_and_boundary_interaction_are_separate(self):
        ownership = {r["case_id"]: Path(r["source"]).parts[1][:2] for r in rows("cases.tsv")}
        self.assertEqual(sum(group == "01" for group in ownership.values()), 8)
        self.assertEqual(sum(group == "02" for group in ownership.values()), 22)
        for name in ("01_mmio_rw", "01_window_commit", "01_cmd_handshake", "01_dma_arg_pair",
                     "01_dma_loopback", "01_compute_writeback", "01_channel_loopback",
                     "01_dma_busy_transition"):
            self.assertEqual(ownership[name], "01")
        for name, group in ownership.items():
            if any(word in name for word in ("watchdog", "cpu_hpu", "cmd_burst", "window_bounds",
                                             "object_isolation", "dload_window_fault")):
                self.assertEqual(group, "02")

    def test_chapter_and_subdirectory_numbers_are_contiguous(self):
        # 按源码/下载清单检查；切分支遗留的未跟踪空目录不是交付目录。
        paths = [Path(row["source"]) for row in rows("cases.tsv")]
        chapters = sorted({path.parts[1] for path in paths})
        self.assertEqual([int(re.match(r"^(\d+)_", name)[1]) for name in chapters], list(range(8)))
        for chapter in chapters:
            with self.subTest(chapter=chapter):
                children = sorted({path.parts[2] for path in paths if path.parts[1] == chapter})
                self.assertEqual([int(re.match(r"^(\d+)_", name)[1]) for name in children],
                                 list(range(1, len(children) + 1)))

    def test_04_contains_only_basic_operators_and_orchestration(self):
        cases = [r for r in rows("cases.tsv") if r["source"].startswith("src/04_")]
        self.assertEqual(len(cases), 11)
        self.assertTrue(all("/02_algorithm_library_operators/" not in r["source"] for r in cases))
        specs = [r for r in rows("scheme-cases.tsv") if r["source"].startswith("src/04_")]
        self.assertEqual(len(specs), 6)
        self.assertEqual({r["role"] for r in specs}, {"keyswitch"})
        self.assertTrue(all(not r["case_id"].startswith("HPU_IT_LIB_") for r in cases))

    def test_05_has_seal_matrix_distinct_parameter_regressions_and_pending(self):
        cases = [r for r in rows("cases.tsv") if r["source"].startswith("src/05_")]
        self.assertEqual(len(cases), 39)
        self.assertTrue(all(r["case_id"].startswith("05_") for r in cases))
        self.assertTrue(all(r["source"].startswith("src/05_algorithm_library/") for r in cases))
        specs = [r for r in rows("scheme-cases.tsv") if r["source"].startswith("src/05_")]
        seal = [r for r in specs if r["program_stem"].startswith("seal_")]
        regression = [r for r in specs if not r["program_stem"].startswith("seal_")]
        self.assertEqual(len(seal), 30)
        self.assertEqual({(r["scheme"], r["degree"], r["role"]) for r in seal},
                         {(s, n, op) for s in ("ckks", "bfv", "bgv") for n in ("128", "4096")
                          for op in ("hadd", "hmul", "reline", "modswitch", "rotate")})
        self.assertEqual({r["program_stem"] for r in regression},
                         {"bgv_hadd_n4096", "bgv_hmul_n4096", "bgv_reline_n4096",
                          "bgv_modswitch_n4096", "ckks_rotate_n4096", "bfv_rotate_n4096",
                          "bgv_rotate_n4096"})
        for row in regression:
            self.assertIn("/04_parameter_regression/", row["source"])
            self.assertTrue("_cf" in row["case_id"] or "_gen3_step1_" in row["case_id"])
            self.assertIn("主机参考为SEAL", (ROOT / row["source"]).read_text())
        pending = [r for r in cases if r["qualifier"] == "blocked-not-issued"]
        self.assertEqual(len(pending), 2)
        for row in pending:
            self.assertIn("/05_pending_interfaces/", row["source"])
            self.assertIn("case_not_qualified(__FILE__)", (ROOT / row["source"]).read_text())

    def test_removed_duplicates_have_direct_aliases_and_no_second_source(self):
        live = {r["case_id"]: r for r in rows("cases.tsv")}
        aliases = rows("case-aliases.tsv")
        self.assertEqual(len({r["previous_case_id"] for r in aliases}), len(aliases))
        current_ids = set(live) | {r["subtest_id"] for r in rows("subtests/cases.tsv")}
        self.assertTrue(all(r["case_id"] in current_ids for r in aliases))
        alias_map = {r["previous_case_id"]: r["case_id"] for r in aliases}
        migrations = rows("layer-migration.tsv")
        self.assertEqual(len(migrations), 17)
        duplicates = [r for r in migrations if r["disposition"] == "DEDUPLICATED"]
        self.assertEqual(len(duplicates), 8)
        for row in migrations:
            self.assertEqual(alias_map[row["previous_case_id"]], row["case_id"])
            self.assertEqual(live[row["case_id"]]["source"], row["source"])
            self.assertFalse((ROOT / row["previous_source"]).exists())
        active_stems = {r["program_stem"] for r in rows("scheme-cases.tsv")}
        self.assertFalse(active_stems & {f"{s}_{op}_n4096" for s in ("ckks", "bfv")
                                       for op in ("hadd", "hmul", "reline", "modswitch")})

    def test_keyswitch_is_not_reline_or_hmul(self):
        fixture = (ROOT / "tools/hpu-scheme-cases/fixture.hpp").read_text()
        self.assertIn('if (op == "keyswitch")', fixture)
        self.assertIn("std::fill(input.data(0), input.data(0) + 2 * words, 0)", fixture)
        self.assertTrue(all(r["source"].startswith("src/05_") for r in rows("scheme-cases.tsv")
                            if r["role"] in ("reline", "hmul")))


if __name__ == "__main__":
    unittest.main()
