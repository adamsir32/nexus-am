#!/usr/bin/env python3
"""用临时伪产物验证统一 HPU 下载包，不调用交叉编译器。"""

import csv
import importlib.util
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from immutable_staging import LARGE_FILE_BYTES


SCRIPT = Path(__file__).with_name("package-unified.py")
SPEC = importlib.util.spec_from_file_location("package_unified", SCRIPT)
PACKAGER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGER)
RUNNER_SCRIPT = Path(__file__).with_name("run-subtests.py")
RUNNER_SPEC = importlib.util.spec_from_file_location("run_subtests_for_unified_test", RUNNER_SCRIPT)
RUNNER = importlib.util.module_from_spec(RUNNER_SPEC)
RUNNER_SPEC.loader.exec_module(RUNNER)
TEST_ROOT = Path(__file__).resolve().parents[1]


class UnifiedPackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hpu-unified-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.workloads = self.make_workloads("workloads", silent=False)
        self.silent_workloads = self.make_workloads("silent-workloads", silent=True)
        self.subtests = self.make_subtests("subtests", silent=False)
        self.silent_subtests = self.make_subtests("silent-subtests", silent=True)
        self.output = self.root / "unified"

    @staticmethod
    def rows(path):
        with path.open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream, delimiter="\t"))

    @staticmethod
    def write_tsv(path, fields, rows):
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def write_artifacts(release, base, identity, silent):
        paths = {}
        for field, extension in PACKAGER.FILE_FIELDS:
            relative = base.with_suffix(extension)
            target = release / Path(relative.as_posix())
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(f"{identity}:{'silent' if silent else 'normal'}:{field}".encode())
            paths[field] = relative.as_posix()
        return paths

    @staticmethod
    def common_tree(release, subtests=False, functional=False):
        provenance = release / "provenance"
        provenance.mkdir()
        (provenance / "PRODUCER_COMMIT").write_text("producer-commit\n", encoding="utf-8")
        tools = release / "tools"
        tools.mkdir()
        (tools / "parse-uart-results.py").write_text("# parser\n", encoding="utf-8")
        if subtests:
            (tools / "run-subtests.py").write_text("# runner\n", encoding="utf-8")
        else:
            shutil.copy2(TEST_ROOT / "scripts/parse-perf-results.py", tools)
            (provenance / "testplan").mkdir()
            if functional:
                (provenance / "testplan/perf-cases.tsv").write_text(
                    (TEST_ROOT / "perf-cases.tsv").read_text().splitlines()[0] + "\n")
            else:
                shutil.copy2(TEST_ROOT / "perf-cases.tsv", provenance / "testplan")
            shutil.copy2(TEST_ROOT / "perf-migration.tsv", provenance / "testplan")

    def make_workloads(self, name, silent, functional=False):
        release = self.root / name / "release"
        release.mkdir(parents=True)
        self.common_tree(release, functional=functional)
        mode = "silent" if silent else "minimal"
        uart = "none" if silent else "brief"
        level = "0" if silent else "1"
        (release / "MANIFEST.txt").write_text(
            "repository=test/repository\nrevision=am-revision\narch=riscv64-xs\n"
            f"selection={'functional' if functional else 'all'}\nmainargs=all\n"
            f"log_level={level}\nlog_mode={mode}\nuart_results={uart}\n"
            f"hpu_dump_results=0\ncase_count={140 if functional else 340}\nnot_qualified_count=7\n"
            "inline_asm_commit=producer-commit\n"
            "hpu_seal_commit=hpu-seal-producer-commit\n"
            "hpu_applications_commit=hpu-applications-producer-commit\n"
            "golden_backend=inline-asm/modified-SEAL\n", encoding="utf-8")
        rows = []
        for source in self.rows(TEST_ROOT / "cases.tsv"):
            if functional and source["source"].startswith("src/07_performance/"):
                continue
            relative_source = PurePosixPath(source["source"])
            chapter = relative_source.parts[1]
            base = PurePosixPath(*relative_source.parts[1:]).with_suffix("")
            blocked = source["qualifier"] == "blocked-not-issued"
            row = {
                "chapter": chapter, "case_id": source["case_id"],
                "qualifier": source["qualifier"],
                "publish_status": "BLOCKED_NOT_PUBLISHED" if blocked else "BUILD_READY_NOT_IT_PASS",
                "source": source["source"], "elf": "", "bin": "", "disassembly": "",
                "notes": "blocked reason" if blocked else f"{mode} test artifact",
            }
            if not blocked:
                row.update(self.write_artifacts(release, base, source["case_id"], silent))
            rows.append(row)
        self.write_tsv(release / "INDEX.tsv", PACKAGER.WORKLOAD_FIELDS, rows)
        return release

    def make_subtests(self, name, silent):
        release = self.root / name / "release"
        release.mkdir(parents=True)
        self.common_tree(release, subtests=True)
        mode = "silent" if silent else "minimal"
        uart = "none" if silent else "brief"
        level = "0" if silent else "1"
        (release / "MANIFEST.txt").write_text(
            "format=hpu-subtests-v1\nrevision=am-revision\ninline_asm_commit=producer-commit\n"
            "arch=riscv64-xs\nparent_cases=9\nsubtests=37\nprograms=40\n"
            f"hpu_dump_results=0\nuart_results={uart}\nlog_level={level}\nlog_mode={mode}\n"
            "execution=one-independent-simv-per-elf\nqualification=BUILD_READY_NOT_IT_PASS\n",
            encoding="utf-8")
        catalog = self.rows(TEST_ROOT / "subtests" / "cases.tsv")
        self.write_tsv(release / "cases.tsv", PACKAGER.SUBTEST_FIELDS[:6], catalog)
        rows = []
        for source in catalog:
            base = PurePosixPath("03_compute_instructions") / source["subtest_id"]
            row = dict(source)
            row.update({
                "mainargs": f"subcase={source['subcase']}",
                "build_status": "BUILD_READY_NOT_IT_PASS",
                "log_level": level, "log_mode": mode,
            })
            row.update(self.write_artifacts(release, base, source["subtest_id"], silent))
            rows.append(row)
        self.write_tsv(release / "INDEX.tsv", PACKAGER.SUBTEST_FIELDS, rows)
        return release

    def package(self, functional=False):
        return PACKAGER.package(self.workloads, self.silent_workloads,
                                self.subtests, self.silent_subtests, self.output, functional=functional)

    def use_functional_workloads(self):
        self.workloads = self.make_workloads("functional-workloads", False, functional=True)
        self.silent_workloads = self.make_workloads("functional-silent-workloads", True, functional=True)

    def test_functional_package_keeps_subtests_and_excludes_07(self):
        self.use_functional_workloads()
        package = self.package(functional=True) / "hputest"
        rows = PACKAGER.read_tsv(package / "INDEX.tsv", PACKAGER.INDEX_FIELDS)
        self.assertEqual(len(rows), 329)
        self.assertEqual(sum(bool(row["elf"]) for row in rows), 322)
        self.assertEqual(len(list(package.rglob("*.elf"))), 322)
        self.assertEqual(sum(row["publish_status"] == "BLOCKED_NOT_PUBLISHED" for row in rows), 7)
        self.assertEqual({row["chapter"][:2] for row in rows}, {f"{number:02d}" for number in range(7)})
        self.assertFalse((package / "07_performance").exists())
        self.assertEqual(sum(row["kind"] == "subtest" for row in rows), 74)
        self.assertFalse(any(row["test_id"] in PACKAGER.INSTRUCTION_IDS for row in rows))
        self.assertEqual(self.rows(package / "provenance/testplan/perf-cases.tsv"), [])
        metadata = PACKAGER.read_manifest(package)
        self.assertEqual(metadata["selection"], "functional")
        self.assertEqual(metadata["published_test_identities"], "161")
        self.assertEqual(metadata["published_variant_sets"], "322")
        readme = (package / "README.md").read_text()
        self.assertIn("0x90000000，RAM至少512MiB", readme)
        self.assertNotIn("RAM至少2GiB", readme)

    def test_functional_mode_rejects_full_workload_selection(self):
        with self.assertRaisesRegex(ValueError, "wrong build mode"):
            self.package(functional=True)

    def test_functional_mode_rejects_an_injected_07_row(self):
        self.use_functional_workloads()
        rows = self.rows(self.workloads / "INDEX.tsv")
        injected = next(row for row in self.rows(self.root / "workloads/release/INDEX.tsv")
                        if row["chapter"] == "07_performance")
        rows[0] = injected
        self.write_tsv(self.workloads / "INDEX.tsv", PACKAGER.WORKLOAD_FIELDS, rows)
        with self.assertRaisesRegex(ValueError, "must not contain chapter 07"):
            self.package(functional=True)

    def test_one_tree_contains_normal_and_silent_and_replaces_03_parents(self):
        release = self.package()
        package = release / "hputest"
        self.assertEqual(len(list(package.rglob("*.elf"))), 722)
        normal = package / "01_configuration_and_data_paths/01_mmio_and_window/01_01_mmio_rw.elf"
        silent = normal.with_name("01_01_mmio_rw_silent.elf")
        self.assertTrue(normal.is_file())
        self.assertTrue(silent.is_file())
        self.assertFalse(any(path.name == "03_01_padd.elf"
                             for path in (package / "03_compute_instructions").rglob("*.elf")))
        subtest = "03_01_01_padd_dst_p2"
        self.assertTrue((package / "03_compute_instructions" / f"{subtest}.elf").is_file())
        self.assertTrue((package / "03_compute_instructions" / f"{subtest}_silent.elf").is_file())
        rows = PACKAGER.read_tsv(package / "INDEX.tsv", PACKAGER.INDEX_FIELDS)
        self.assertEqual(len(rows), 729)
        self.assertEqual(sum(bool(row["elf"]) for row in rows), 722)
        self.assertEqual(sum(row["publish_status"] == "BLOCKED_NOT_PUBLISHED" for row in rows), 7)
        perf_rows = [row for row in rows if row["chapter"] == "07_performance"]
        perf_catalog = {row["case_id"]: row
                        for row in self.rows(package / "provenance/testplan/perf-cases.tsv")}
        for degree in (4096, 8192, 16384, 32768, 65536):
            for variant in ("normal", "silent"):
                selected = [row for row in perf_rows
                            if perf_catalog[row["test_id"]]["degree"] == str(degree)
                            and row["variant"] == variant]
                self.assertEqual(len(selected), 40)
                self.assertTrue(all(row["elf"] for row in selected))
        metadata = PACKAGER.read_manifest(package)
        self.assertEqual(metadata["published_test_identities"], "361")
        self.assertEqual(metadata["published_variant_sets"], "722")
        self.assertEqual((package / "provenance/testplan/perf-migration.tsv").read_bytes(),
                         (TEST_ROOT / "perf-migration.tsv").read_bytes())
        three_digit_rows = [row for row in perf_rows
                            if int(row["test_id"].split("_")[1]) >= 100]
        self.assertEqual(len(three_digit_rows), 202)
        n4096_numbers = [int(row["test_id"].split("_")[1]) for row in perf_rows
                        if perf_catalog[row["test_id"]]["degree"] == "4096" and row["variant"] == "normal"]
        self.assertEqual(n4096_numbers, list(range(1, 41)))
        perf_numbers = [int(row["test_id"].split("_")[1]) for row in perf_rows
                        if row["variant"] == "normal"]
        self.assertEqual(perf_numbers, list(range(1, 201)))
        watchdog = package / "02_boundaries_and_cpu_interaction/05_faults_and_watchdog/02_17_watchdog_failstop.elf"
        self.assertTrue(watchdog.is_file())
        self.assertTrue(watchdog.with_name(watchdog.stem + "_silent.elf").is_file())
        for name in ("02_18_watchdog_compute_before_dload", "02_19_watchdog_pmodld_before_dload"):
            case = watchdog.with_name(name + ".elf")
            self.assertTrue(case.is_file())
            self.assertTrue(case.with_name(case.stem + "_silent.elf").is_file())
        self.assertEqual({row["variant"] for row in rows if row["elf"]}, {"normal", "silent"})
        normal_cases = RUNNER.read_index(package, "normal")
        silent_cases = RUNNER.read_index(package, "silent")
        self.assertEqual((len(normal_cases), len(silent_cases)), (37, 37))
        self.assertTrue(all(name.endswith("_silent.elf") for _case_id, name, _path in silent_cases))

    def test_downloaded_performance_parser_supports_all_five_scales(self):
        package = self.package() / "hputest"
        catalog = self.rows(package / "provenance/testplan/perf-cases.tsv")
        log = self.root / "uart.log"
        log.write_text("\n".join(
            f"[HPU][PERF] case={row['case_id']} N={row['degree']} level={row['level']} "
            "metric=issue_to_done_v2 start=10 end=210 cycles=200 verified=1"
            for row in catalog) + "\n", encoding="utf-8")
        output = self.root / "performance-results"
        result = subprocess.run(
            [sys.executable, str(package / "tools/parse-perf-results.py"), str(log),
             "--output", str(output), "--revision", "test-only", "--cpu-hz", "100"],
            cwd=self.root, text=True, capture_output=True, check=True)
        self.assertIn("200 verified samples, 200 cases", result.stdout)
        with (output / "summary.csv").open(newline="", encoding="utf-8") as stream:
            summaries = list(csv.DictReader(stream))
        self.assertEqual(len(summaries), 200)
        self.assertEqual({row["degree"] for row in summaries}, {"4096", "8192", "16384", "32768", "65536"})
        self.assertEqual({(row["case_id"], row["degree"], row["level"]) for row in summaries},
                         {(row["case_id"], row["degree"], row["level"]) for row in catalog})
        self.assertEqual(sum(row["level"] == "16" for row in summaries), 90)
        self.assertTrue(all(float(row["average_seconds"]) == 2 for row in summaries))

    def test_optional_hardlinks_share_large_release_and_provenance(self):
        relative = Path("01_configuration_and_data_paths/01_mmio_and_window/01_01_mmio_rw.elf")
        original = self.workloads / relative
        quiet = self.silent_workloads / relative
        original.write_bytes(b"N" * LARGE_FILE_BYTES)
        quiet.write_bytes(b"S" * LARGE_FILE_BYTES)
        for release in (self.workloads, self.silent_workloads):
            (release / "provenance/image.bin").write_bytes(b"I" * LARGE_FILE_BYTES)
        with patch.dict(os.environ, {"HPU_HARDLINK_STAGING": "1"}):
            package = self.package() / "hputest"
        self.assertTrue(original.samefile(package / relative))
        self.assertTrue(quiet.samefile(package / relative.with_name("01_01_mmio_rw_silent.elf")))
        self.assertTrue((self.workloads / "provenance/image.bin").samefile(package / "provenance/image.bin"))
        self.assertFalse((self.workloads / "MANIFEST.txt").samefile(
            package / "provenance/build-manifests/workloads.txt"))

    def test_wrong_input_mode_is_rejected(self):
        manifest = self.silent_workloads / "MANIFEST.txt"
        manifest.write_text(manifest.read_text(encoding="utf-8").replace(
            "log_level=0", "log_level=1"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "wrong build mode"):
            self.package()

    def test_inconsistent_hpu_seal_commit_is_rejected(self):
        manifest = self.silent_workloads / "MANIFEST.txt"
        manifest.write_text(manifest.read_text(encoding="utf-8").replace(
            "hpu_seal_commit=hpu-seal-producer-commit",
            "hpu_seal_commit=other-hpu-seal-producer-commit"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "hpu_seal_commit"):
            self.package()

    def test_inconsistent_hpu_applications_commit_is_rejected(self):
        manifest = self.silent_workloads / "MANIFEST.txt"
        manifest.write_text(manifest.read_text(encoding="utf-8").replace(
            "hpu_applications_commit=hpu-applications-producer-commit",
            "hpu_applications_commit=other-hpu-applications-producer-commit"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "hpu_applications_commit"):
            self.package()

    def test_inconsistent_subtest_row_mode_is_rejected(self):
        rows = PACKAGER.read_tsv(self.silent_subtests / "INDEX.tsv", PACKAGER.SUBTEST_FIELDS)
        rows[0]["log_level"] = "1"
        self.write_tsv(self.silent_subtests / "INDEX.tsv", PACKAGER.SUBTEST_FIELDS, rows)
        with self.assertRaisesRegex(ValueError, "inconsistent row mode"):
            self.package()

    def test_revision_mismatch_is_rejected(self):
        manifest = self.subtests / "MANIFEST.txt"
        manifest.write_text(manifest.read_text(encoding="utf-8").replace(
            "revision=am-revision", "revision=other"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "disagree on revision"):
            self.package()

    def test_missing_input_file_is_rejected(self):
        next(self.silent_subtests.rglob("*.bin")).unlink()
        with self.assertRaisesRegex(ValueError, "missing or empty"):
            self.package()

    def test_index_drift_is_rejected(self):
        rows = PACKAGER.read_tsv(self.silent_subtests / "INDEX.tsv", PACKAGER.SUBTEST_FIELDS)
        rows[0]["description"] = "different meaning"
        self.write_tsv(self.silent_subtests / "INDEX.tsv", PACKAGER.SUBTEST_FIELDS, rows)
        with self.assertRaisesRegex(ValueError, "do not describe the same cases"):
            self.package()

    def test_provenance_drift_is_rejected(self):
        (self.silent_workloads / "provenance" / "PRODUCER_COMMIT").write_text(
            "other\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "workload provenance differs"):
            self.package()

    def test_unowned_output_is_preserved(self):
        self.output.mkdir()
        note = self.output / "user-note.txt"
        note.write_text("keep me", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unowned"):
            self.package()
        self.assertEqual(note.read_text(encoding="utf-8"), "keep me")

    def test_output_cannot_overlap_an_input_release(self):
        with self.assertRaisesRegex(ValueError, "must not overlap"):
            PACKAGER.package(self.workloads, self.silent_workloads,
                             self.subtests, self.silent_subtests,
                             self.workloads / "nested-output")
        self.assertFalse((self.workloads / "nested-output").exists())

    def test_generated_release_with_extra_file_is_preserved(self):
        release = self.package()
        extra = release / "hputest" / "user-note.txt"
        extra.write_text("keep me", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "untracked"):
            self.package()
        self.assertEqual(extra.read_text(encoding="utf-8"), "keep me")


if __name__ == "__main__":
    unittest.main()
