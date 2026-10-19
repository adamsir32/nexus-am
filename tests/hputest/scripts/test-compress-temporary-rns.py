#!/usr/bin/env python3
"""验证单文件压缩的边界、恢复以及失败时保留原始数据。"""

import gzip
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("compress-temporary-rns.py")
SPEC = importlib.util.spec_from_file_location("compress_temporary_rns", SCRIPT)
COMPRESS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COMPRESS)


class TemporaryRnsCompressionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hpu-rns-compress-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.generation = self.root / "large.test"
        self.source = self.generation / "n65536/outputs/ntt/test_data/hardware/image.bin"
        self.source.parent.mkdir(parents=True)
        self.data = bytes(range(256)) * 8192
        self.source.write_bytes(self.data)
        self.destination = self.source.with_name(self.source.name + ".gz")

    def test_roundtrip_and_only_explicit_file_is_removed(self):
        sibling = self.source.with_name("keep.bin")
        sibling.write_bytes(b"keep")
        destination, before, after = COMPRESS.compress_one(self.source, self.generation)
        self.assertEqual(destination, self.destination)
        self.assertEqual(before, len(self.data))
        self.assertEqual(after, destination.stat().st_size)
        self.assertFalse(self.source.exists())
        self.assertEqual(gzip.decompress(destination.read_bytes()), self.data)
        self.assertEqual(sibling.read_bytes(), b"keep")

    def test_legacy_raw_path_is_supported(self):
        source = self.generation / "legacy-n4096/outputs/auto/test_data/image.bin"
        source.parent.mkdir(parents=True)
        self.source.rename(source)
        destination, _, _ = COMPRESS.compress_one(source, self.generation)
        self.assertEqual(gzip.decompress(destination.read_bytes()), self.data)

    def test_small_input_is_left_untouched(self):
        self.source.write_bytes(b"A" * COMPRESS.MINIMUM_BYTES)
        self.assertIsNone(COMPRESS.compress_one(self.source, self.generation))
        self.assertTrue(self.source.exists())
        self.assertFalse(self.destination.exists())

    def test_existing_compressed_file_is_preserved(self):
        self.destination.write_bytes(b"keep existing gzip")
        with self.assertRaises(FileExistsError):
            COMPRESS.compress_one(self.source, self.generation)
        self.assertEqual(self.destination.read_bytes(), b"keep existing gzip")
        self.assertEqual(self.source.read_bytes(), self.data)

    def test_delivery_and_outside_generation_are_rejected(self):
        for relative in ("delivery/ntt/image.bin", "n2048/outputs/image.bin", "n4096/application/image.bin"):
            with self.subTest(path=relative):
                candidate = self.generation / relative
                candidate.parent.mkdir(parents=True, exist_ok=True)
                candidate.write_bytes(self.data)
                with self.assertRaisesRegex(ValueError, "nN/outputs"):
                    COMPRESS.compress_one(candidate, self.generation)
                self.assertTrue(candidate.exists())
        outside = self.root / "outside.bin"
        outside.write_bytes(self.data)
        with self.assertRaisesRegex(ValueError, "outside generation root"):
            COMPRESS.compress_one(outside, self.generation)
        self.assertTrue(outside.exists())

    def test_non_generation_root_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "plain large"):
            COMPRESS.compress_one(self.source, self.root)
        self.assertTrue(self.source.exists())

    def test_source_and_ancestor_symlinks_are_rejected(self):
        original = self.source.with_name("original.bin")
        self.source.rename(original)
        self.source.symlink_to(original)
        with self.assertRaisesRegex(ValueError, "symlink"):
            COMPRESS.compress_one(self.source, self.generation)
        self.assertTrue(original.exists())
        alias_root = self.generation / "legacy-n4096"
        alias_root.symlink_to(self.generation / "n65536", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            COMPRESS.compress_one(alias_root / "outputs/ntt/test_data/hardware/original.bin", self.generation)
        self.assertTrue(original.exists())

    def test_empty_misaligned_and_temporary_files_are_rejected(self):
        for content in (b"", b"incomplete"):
            self.source.write_bytes(content)
            with self.assertRaisesRegex(ValueError, "incomplete"):
                COMPRESS.compress_one(self.source, self.generation)
        partial = self.source.with_name("image.partial.bin")
        partial.write_bytes(self.data)
        with self.assertRaisesRegex(ValueError, "incomplete"):
            COMPRESS.compress_one(partial, self.generation)
        self.assertTrue(partial.exists())

    def test_write_failure_keeps_original_and_removes_only_own_partial_output(self):
        with patch.object(COMPRESS.shutil, "copyfileobj", side_effect=OSError("simulated disk full")):
            with self.assertRaisesRegex(OSError, "disk full"):
                COMPRESS.compress_one(self.source, self.generation)
        self.assertEqual(self.source.read_bytes(), self.data)
        self.assertFalse(self.destination.exists())

    def test_mutation_during_compression_keeps_original(self):
        real_copy = shutil.copyfileobj
        def change_after_read(raw, stream, length):
            real_copy(raw, stream, length)
            self.source.write_bytes(b"new source")
        with patch.object(COMPRESS.shutil, "copyfileobj", side_effect=change_after_read):
            with self.assertRaisesRegex(ValueError, "changed during compression"):
                COMPRESS.compress_one(self.source, self.generation)
        self.assertEqual(self.source.read_bytes(), b"new source")
        self.assertFalse(self.destination.exists())

    def test_cli_accepts_exactly_one_explicit_file(self):
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.source), str(self.source),
                                 "--generation-root", str(self.generation)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertTrue(self.source.exists())
        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
