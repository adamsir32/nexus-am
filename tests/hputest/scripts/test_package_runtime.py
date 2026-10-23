"""小夹具验证运行文件交付边界；不是硬件运行结果。"""
import csv
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
import zipfile


SPEC = importlib.util.spec_from_file_location("package_runtime", Path(__file__).with_name("package-runtime.py"))
runtime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime)


class RuntimePackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hpu-runtime-test-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.roots = {name: self.directory / name for name in ("legacy", "frontend")}
        for root in self.roots.values():
            root.mkdir()
        self.catalog = self.directory / "runtime-cases.tsv"
        self.output = self.directory / "delivery/hpu.zip"

    def case(self, group="00", case_id="00_01_probe", producer="legacy", degree="", level=""):
        row = dict(group=group, case_id=case_id, producer=producer, degree=degree, level=level)
        for key, suffix in (("elf", ".elf"), ("bin", ".bin")):
            row[key] = f"artifact/optimized/minimal/{case_id}/{case_id}{suffix}"
            path = self.roots[producer] / row[key]
            path.parent.mkdir(parents=True, exist_ok=True)
            header = bytearray(64)
            header[:6] = b"\x7fELF\x02\x01"
            struct.pack_into("<H", header, 18, 243)
            path.write_bytes(header if key == "elf" else b"runtime-bin")
        return row

    def write_catalog(self, rows):
        with self.catalog.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=runtime.FIELDS, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def package(self, rows):
        self.write_catalog(rows)
        return runtime.package_runtime(self.catalog, self.roots, self.output)

    def test_only_explicit_elf_and_bin_are_exported_once_by_group(self):
        rows = [self.case(f"0{group}", f"0{group}_01_probe") for group in range(7)]
        rows += [self.case("07_performance", f"07_{number}_ckks_l4_n{degree}", "frontend", str(degree), "4")
                 for number, degree in enumerate((1024, 2048, 4096, 8192), 1)]
        frontend = self.roots["frontend"]
        for name in ("case.c", "golden.bin", "old_l16_n65536.elf", "report.json", "program.inst32"):
            (frontend / name).write_text("must not ship")
        for variant in ("noopt/minimal", "optimized/silent", "noopt/silent"):
            ignored = frontend / "artifact" / variant / "07_1_ckks_l4_n1024"
            ignored.mkdir(parents=True)
            for suffix in (".elf", ".bin"):
                (ignored / ("07_1_ckks_l4_n1024" + suffix)).write_text("extra variant")
        archive, count = self.package(rows)
        self.assertEqual(count, 11)
        with zipfile.ZipFile(archive) as zipped:
            self.assertEqual(zipped.namelist(), sorted(f"{row['case_id'][:2]}/{row['case_id']}{suffix}"
                                                     for row in rows for suffix in (".elf", ".bin")))
            self.assertEqual(zipped.read("07/07_1_ckks_l4_n1024.bin"), b"runtime-bin")

    def test_missing_bin_does_not_publish_partial_archive(self):
        row = self.case()
        (self.roots["legacy"] / row["bin"]).unlink()
        with self.assertRaisesRegex(ValueError, "missing or empty .bin"):
            self.package([row])
        self.assertFalse(self.output.exists())

    def test_duplicate_case_is_rejected(self):
        row = self.case()
        with self.assertRaisesRegex(ValueError, "duplicate runtime case"):
            self.package([row, row])

    def test_07_larger_degrees_and_retired_l16_are_rejected(self):
        for degree, level in ((16384, 4), (65536, 4), (4096, 16)):
            with self.subTest(degree=degree, level=level):
                row = self.case("07", "07_01_probe", "frontend", str(degree), str(level))
                with self.assertRaisesRegex(ValueError, "07 requires"):
                    self.package([row])
        self.assertFalse(self.output.exists())

    def test_group_mismatch_and_undeclared_producer_are_rejected(self):
        row = self.case()
        for fields, message in ((dict(group="07"), "invalid group/case"),
                                (dict(producer="not-declared"), "unknown producer")):
            with self.subTest(fields=fields):
                with self.assertRaisesRegex(ValueError, message):
                    self.package([{**row, **fields}])

    def test_directory_escape_and_symlink_are_rejected(self):
        row = self.case()
        with self.assertRaisesRegex(ValueError, "invalid .elf path"):
            self.package([{**row, "elf": "../other.elf"}])
        target = self.roots["legacy"] / row["elf"]
        alias = self.roots["legacy"] / "alias.elf"
        alias.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink is not allowed"):
            self.package([{**row, "elf": "alias.elf"}])

    def test_wrong_elf_and_empty_bin_are_rejected(self):
        row = self.case()
        elf = self.roots["legacy"] / row["elf"]
        elf.write_bytes(b"source is not an executable")
        with self.assertRaisesRegex(ValueError, "expected little-endian RV64 ELF"):
            self.package([row])
        row = self.case()
        (self.roots["legacy"] / row["bin"]).write_bytes(b"")
        with self.assertRaisesRegex(ValueError, "missing or empty .bin"):
            self.package([row])

    def test_existing_archive_is_not_overwritten(self):
        row = self.case()
        self.output.parent.mkdir()
        self.output.write_bytes(b"existing user delivery")
        with self.assertRaisesRegex(ValueError, "output already exists"):
            self.package([row])
        self.assertEqual(self.output.read_bytes(), b"existing user delivery")

    def test_direct_upload_tree_must_match_the_catalog_exactly(self):
        row = self.case()
        self.write_catalog([row])
        files = runtime.prepare_files(self.catalog, self.roots, check_tree=True)
        self.assertEqual(len(files), 2)
        (self.roots["legacy"] / "old_l16_n65536.elf").write_text("must not upload")
        with self.assertRaisesRegex(ValueError, "runtime tree differs"):
            runtime.prepare_files(self.catalog, self.roots, check_tree=True)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
