#!/usr/bin/env python3
"""验证可选硬链接、跨盘复制及重建时历史交付的隔离。"""

import errno
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import immutable_staging as staging


class ImmutableStagingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hpu-staging-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source.bin"
        self.source.write_bytes(b"A" * staging.LARGE_FILE_BYTES)
        self.target = self.root / "target.bin"

    def test_default_copy_is_independent(self):
        with patch.dict(os.environ, {"HPU_HARDLINK_STAGING": "0"}):
            staging.immutable_copy_function()(self.source, self.target)
        self.assertFalse(self.source.samefile(self.target))
        self.source.write_bytes(b"new source")
        self.assertEqual(self.target.read_bytes(), b"A" * staging.LARGE_FILE_BYTES)

    def test_same_disk_large_file_shares_inode(self):
        with patch.dict(os.environ, {"HPU_HARDLINK_STAGING": "1"}):
            staging.immutable_copy_function()(self.source, self.target)
        self.assertTrue(self.source.samefile(self.target))
        self.assertEqual(self.source.stat().st_nlink, 2)

    def test_small_metadata_stays_independent(self):
        self.source.write_text("immutable metadata\n")
        with patch.dict(os.environ, {"HPU_HARDLINK_STAGING": "1"}):
            staging.immutable_copy_function()(self.source, self.target)
        self.assertFalse(self.source.samefile(self.target))
        self.assertEqual(self.source.read_bytes(), self.target.read_bytes())

    def test_cross_device_falls_back_to_copy(self):
        with patch.dict(os.environ, {"HPU_HARDLINK_STAGING": "1"}), \
                patch.object(staging.os, "link", side_effect=OSError(errno.EXDEV, "cross-device")):
            staging.immutable_copy_function()(self.source, self.target)
        self.assertFalse(self.source.samefile(self.target))
        self.assertEqual(self.source.read_bytes(), self.target.read_bytes())

    def test_other_link_failure_is_not_hidden(self):
        with patch.object(staging.os, "link", side_effect=PermissionError(errno.EACCES, "denied")):
            with self.assertRaises(PermissionError):
                staging.link_or_copy_immutable(self.source, self.target)
        self.assertFalse(self.target.exists())

    def test_existing_destination_is_never_overwritten(self):
        self.target.write_bytes(b"preserve user content")
        with self.assertRaises(FileExistsError):
            staging.link_or_copy_immutable(self.source, self.target)
        self.assertEqual(self.target.read_bytes(), b"preserve user content")

    def test_symlink_source_is_rejected(self):
        alias = self.root / "alias.bin"
        alias.symlink_to(self.source)
        with self.assertRaisesRegex(ValueError, "plain immutable file"):
            staging.link_or_copy_immutable(alias, self.target)
        self.assertFalse(self.target.exists())

    def test_rebuild_preserves_old_artifact_and_published_link(self):
        artifact = self.root / "artifact"
        artifact.mkdir()
        original = artifact / "case.bin"
        self.source.rename(original)
        note = artifact / "user-note.txt"
        note.write_text("keep me")
        staging.link_or_copy_immutable(original, self.target)
        previous = staging.prepare_artifact_directory(artifact)
        self.assertEqual(list(artifact.iterdir()), [])
        self.assertTrue((previous / "case.bin").samefile(self.target))
        self.assertEqual((previous / "user-note.txt").read_text(), "keep me")
        (artifact / "case.bin").write_bytes(b"new build")
        self.assertEqual(self.target.read_bytes(), b"A" * staging.LARGE_FILE_BYTES)
        self.assertEqual((previous / "case.bin").read_bytes(), b"A" * staging.LARGE_FILE_BYTES)

    def test_artifact_symlink_is_not_moved(self):
        external = self.root / "other"
        external.mkdir()
        artifact = self.root / "artifact"
        artifact.symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "plain directory"):
            staging.prepare_artifact_directory(artifact)
        self.assertTrue(artifact.is_symlink())
        self.assertTrue(external.is_dir())

    def test_invalid_mode_is_rejected(self):
        with patch.dict(os.environ, {"HPU_HARDLINK_STAGING": "unexpected"}):
            with self.assertRaisesRegex(ValueError, "must be 0 or 1"):
                staging.immutable_copy_function()


class FixtureObjectCleanupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hpu-fixture-cleanup-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.test_root = self.root / "repository/tests/hputest"
        self.object_dir = self.root / "objects/07_01_probe_l4_n4096"
        self.object_dir.mkdir(parents=True)
        self.fixture = self.object_dir / Path(*self.test_root.parts[1:]) / "src/common/it_application_fixture.o"
        self.fixture.parent.mkdir(parents=True)
        self.fixture.write_bytes(b"rebuildable object")
        self.other = self.fixture.with_name("it_application.o")
        self.other.write_bytes(b"keep other object")
        self.elf = self.root / "07_01_probe_l4_n4096.elf"
        self.binary = self.elf.with_suffix(".bin")
        self.elf.write_bytes(b"linked ELF")
        self.binary.write_bytes(b"linked BIN")

    def discard(self):
        return staging.discard_fixture_object(self.object_dir, self.test_root, self.elf, self.binary)

    def test_only_exact_fixture_object_is_removed(self):
        self.assertEqual(self.discard(), (self.fixture, len(b"rebuildable object")))
        self.assertFalse(self.fixture.exists())
        self.assertEqual(self.other.read_bytes(), b"keep other object")
        self.assertEqual(self.elf.read_bytes(), b"linked ELF")
        self.assertEqual(self.binary.read_bytes(), b"linked BIN")
        self.assertIsNone(self.discard())

    def test_empty_elf_prevents_cleanup(self):
        self.elf.write_bytes(b"")
        with self.assertRaisesRegex(ValueError, "nonempty plain product"):
            self.discard()
        self.assertTrue(self.fixture.is_file())

    def test_default_cli_mode_does_not_remove_fixture(self):
        environment = os.environ.copy()
        environment.pop("HPU_HARDLINK_STAGING", None)
        result = subprocess.run(
            [sys.executable, str(Path(staging.__file__)), "--discard-fixture-object", str(self.object_dir),
             "--test-root", str(self.test_root), "--elf", str(self.elf), "--bin", str(self.binary)],
            env=environment, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("requires HPU_HARDLINK_STAGING=1", result.stderr)
        self.assertTrue(self.fixture.is_file())

    def test_missing_binary_prevents_cleanup(self):
        self.binary.rename(self.root / "preserved.bin")
        with self.assertRaisesRegex(ValueError, "nonempty plain product"):
            self.discard()
        self.assertTrue(self.fixture.is_file())

    def test_wrong_case_directory_is_rejected(self):
        wrong = self.root / "objects/other_case"
        wrong.mkdir()
        with self.assertRaisesRegex(ValueError, "matching case"):
            staging.discard_fixture_object(wrong, self.test_root, self.elf, self.binary)
        self.assertTrue(self.fixture.is_file())

    def test_fixture_symlink_is_rejected(self):
        original = self.fixture.with_name("preserved.o")
        self.fixture.rename(original)
        self.fixture.symlink_to(original)
        with self.assertRaisesRegex(ValueError, "refuses a symlink"):
            self.discard()
        self.assertTrue(original.is_file())
        self.assertTrue(self.fixture.is_symlink())

    def test_ancestor_symlink_is_rejected(self):
        directory = self.fixture.parent
        original = directory.with_name("preserved-common")
        directory.rename(original)
        directory.symlink_to(original, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "refuses a symlink"):
            self.discard()
        self.assertTrue((original / self.fixture.name).is_file())


class ProvenanceReuseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hpu-provenance-reuse-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "normal/artifact"
        self.target = self.root / "silent/artifact"
        self.source.mkdir(parents=True)
        self.target.mkdir(parents=True)
        self.revision = 'a' * 40
        for artifact in (self.source, self.target):
            (artifact / 'CASE_MANIFEST.tsv').write_text('group\tqualifier\tcase_id\tsource\ncore\tsoftware-self-check\tcase\tsrc/case.c\n')
        (self.source / 'MANIFEST.txt').write_text(f'log_level=1\nrevision={self.revision}\n')
        self.provenance = self.source / 'provenance'
        self.provenance.mkdir()
        (self.provenance / 'image.bin').write_bytes(b'I' * staging.LARGE_FILE_BYTES)
        (self.provenance / 'metadata.json').write_text('{"immutable":true}\n')

    def reuse(self, level=0):
        with patch.dict(os.environ, {'HPU_HARDLINK_STAGING': '1'}):
            return staging.reuse_provenance(self.source, self.target, self.revision, level)

    def test_matching_normal_snapshot_shares_large_data_only(self):
        destination = self.reuse()
        self.assertTrue((self.provenance / 'image.bin').samefile(destination / 'image.bin'))
        self.assertFalse((self.provenance / 'metadata.json').samefile(destination / 'metadata.json'))
        self.assertFalse((self.target / 'MANIFEST.txt').exists())

    def test_mismatched_cases_are_rejected_before_copy(self):
        (self.target / 'CASE_MANIFEST.tsv').write_text('different case set\n')
        with self.assertRaisesRegex(ValueError, 'CASE_MANIFEST.tsv differ'):
            self.reuse()
        self.assertFalse((self.target / 'provenance').exists())

    def test_wrong_revision_and_non_normal_source_are_rejected(self):
        for metadata in ('log_level=1\nrevision=other\n', f'log_level=0\nrevision={self.revision}\n'):
            (self.source / 'MANIFEST.txt').write_text(metadata)
            with self.assertRaisesRegex(ValueError, 'current revision'):
                self.reuse()
            self.assertFalse((self.target / 'provenance').exists())

    def test_reuse_requires_silent_and_enabled_mode(self):
        with self.assertRaisesRegex(ValueError, 'log_level=0'):
            self.reuse(level=1)
        with patch.dict(os.environ, {'HPU_HARDLINK_STAGING': '0'}):
            with self.assertRaisesRegex(ValueError, 'hardlink staging'):
                staging.reuse_provenance(self.source, self.target, self.revision, 0)
        self.assertFalse((self.target / 'provenance').exists())

    def test_symlinked_provenance_content_is_rejected(self):
        (self.provenance / 'alias.bin').symlink_to(self.provenance / 'image.bin')
        with self.assertRaisesRegex(ValueError, 'symlink or special'):
            self.reuse()
        self.assertFalse((self.target / 'provenance').exists())

    def test_overlapping_artifact_paths_are_rejected(self):
        self.target = self.source
        with self.assertRaisesRegex(ValueError, 'must not overlap'):
            self.reuse()

    def test_existing_target_provenance_is_preserved(self):
        destination = self.target / 'provenance'
        destination.mkdir()
        note = destination / 'user-note'
        note.write_text('keep')
        with self.assertRaises(FileExistsError):
            self.reuse()
        self.assertEqual(note.read_text(), 'keep')


if __name__ == "__main__":
    unittest.main()
