#!/usr/bin/env python3
"""检查分片发布边界、证据裁剪和实际ELF校验器调用；不伪称硬件回归。"""

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("build-performance-shard.py")
SPEC = importlib.util.spec_from_file_location("performance_shard_builder", SCRIPT)
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class PerformanceShardTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hpu-perf-shard-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_scope_cannot_publish_functional_cases(self):
        with self.assertRaisesRegex(ValueError, "performance"):
            builder.selection("functional")
        selected = builder.selection("performance:65536:l16-bfv-a")
        self.assertEqual(len(selected), 3)
        self.assertTrue(all(row["level"] == "16" and row["degree"] == "65536" and
                            "_bfv_" in row["case_id"] for row in selected))
        self.assertEqual({row["memory_base"] for row in selected}, {"0xc0000000"})

    def test_output_refuses_existing_content_links_and_generated_overlap(self):
        generated = self.root / "generated"
        generated.mkdir()
        existing = self.root / "existing"
        existing.mkdir()
        note = existing / "user.txt"
        note.write_text("preserve")
        with self.assertRaisesRegex(ValueError, "nonempty"):
            builder.prepare_output(existing, generated)
        self.assertEqual(note.read_text(), "preserve")
        alias = self.root / "alias"
        alias.symlink_to(existing, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            builder.prepare_output(alias, generated)
        for path in (generated, generated / "output", self.root):
            with self.assertRaisesRegex(ValueError, "separate"):
                builder.prepare_output(path, generated)

    def test_evidence_keeps_parameters_and_instructions_without_raw_bins(self):
        source, target = self.root / "source", self.root / "evidence"
        (source / "upstream/provenance").mkdir(parents=True)
        (source / "fixture.inst32").write_text("010101\n")
        (source / "FIXTURE_PARAMETERS.json").write_text('{"Q":[17]}')
        (source / "PROGRAM_MODEL.log").write_text("model PASS\n")
        (source / "application_window.u32.bin").write_bytes(b"small test fixture")
        (source / "upstream/provenance/files.csv").write_text("upstream file inventory")
        copied = builder.copy_evidence(source, target)
        self.assertEqual(set(copied), {"fixture.inst32", "FIXTURE_PARAMETERS.json", "PROGRAM_MODEL.log"})
        self.assertEqual(json.loads((target / "FIXTURE_PARAMETERS.json").read_text()), {"Q": [17]})
        self.assertFalse(list(target.rglob("*.bin")))

    def test_stale_or_unverified_perf_adaptation_is_rejected_before_link(self):
        row = builder.selection("performance:4096:baseline")[0]
        generated = self.root / "generated"
        directory = generated / row["delivery"] / row["program_stem"]
        directory.mkdir(parents=True)
        stem = row["program_stem"]
        names = [f"{stem}.{suffix}" for suffix in ("c", "h", "asm", "inst32", "cmd26")]
        names += [f"{stem}_perf.c", f"{stem}_perf.h", "application_layout.h",
                  "dma_relocation_manifest.csv", "PROGRAM_MODEL.log"] + list(builder.EMBEDDED_FILES)
        for name in names:
            (directory / name).write_text("test placeholder")
        adaptation = {"schema_version": 1, "metric": "issue_to_done_v2", "program_stem": stem,
                      "instruction_words_unchanged": True, "preflight_emits_hpu": False,
                      "timed_parameter_checks": True, "timed_trace_writes": False}
        (directory / "PERF_ADAPTATION.json").write_text(json.dumps(adaptation))
        with self.assertRaisesRegex(ValueError, "invalid performance adaptation"):
            builder.validate_delivery(generated, row, {"hpu-applications": "a" * 40})

    def test_original_parameter_fallback_checks_actual_degree_and_input_level(self):
        directory = self.root / "delivery"
        (directory / "upstream/metadata").mkdir(parents=True)
        original = directory / "upstream/metadata/parameters.json"
        original.write_text(json.dumps({"poly_modulus_degree": 4096,
                                        "levels": [{"moduli": [17, 97, 113, 193]}]}))
        row = {"case_id": "test", "delivery": "application-data", "degree": "4096", "level": "4"}
        values = builder.delivery_parameters(directory, row)
        self.assertEqual(values["evidence_file"], "upstream/metadata/parameters.json")
        self.assertEqual(values["levels"][0]["moduli"], [17, 97, 113, 193])
        with self.assertRaisesRegex(ValueError, "input level"):
            builder.delivery_parameters(directory, dict(row, level="16"))

    def run_variant(self, variant, elf_only=False, failed_verifier=None):
        row = builder.selection("performance:4096:baseline")[0]
        package = self.root / "package"
        output = self.root / "build"
        commands = []

        def fake_run(command, **kwargs):
            commands.append(command)
            if command[0] == "make":
                binary = Path(next(arg.split("=", 1)[1] for arg in command if arg.startswith("BINARY=")))
                binary.with_suffix(".elf").write_bytes(b"unit-test ELF placeholder")
            elif command[0].endswith("objcopy"):
                Path(command[-1]).write_bytes(b"unit-test BIN placeholder")
            elif command[0].endswith("objdump"):
                kwargs["stdout"].write("unit-test disassembly placeholder\n")
            elif failed_verifier and any(str(arg).endswith(failed_verifier) for arg in command):
                raise subprocess.CalledProcessError(1, command)
            return subprocess.CompletedProcess(command, 0)

        with patch.object(builder, "run", side_effect=fake_run), \
                patch.object(builder, "discard_fixture_object") as discard:
            result = builder.build_variant(row, variant, self.root / "delivery", self.root / "generated",
                                           package, output, "riscv64-xs", "riscv64-linux-gnu-", 2,
                                           elf_only, "performance:4096:baseline")
        return row, result, commands, discard

    def test_normal_and_silent_run_required_validators_and_release_only_own_fixture(self):
        for variant in ("normal", "silent"):
            with self.subTest(variant=variant):
                row, result, commands, discard = self.run_variant(variant)
                invoked = [Path(command[1]).name for command in commands if command[0] == builder.sys.executable]
                self.assertIn("verify-operator-elf.py", invoked)
                self.assertIn("verify-perf-elf.py", invoked)
                self.assertEqual("verify-silent-elf.py" in invoked, variant == "silent")
                discard.assert_called_once()
                objects, test_root, elf, image = discard.call_args.args
                self.assertEqual(objects.name, elf.stem)
                self.assertEqual(image, elf.with_suffix(".bin"))
                self.assertEqual(test_root, builder.ROOT)
                self.assertTrue(result["elf"].startswith(variant + "/07_performance/01_n4096/"))
                self.assertEqual(result["build_status"], "BUILD_READY_NOT_IT_PASS")
                self.assertTrue((self.root / "package" / result["bin"]).is_file())

    def test_elf_only_removes_only_its_derived_bin_after_validation(self):
        row, result, commands, discard = self.run_variant("silent", elf_only=True)
        elf = self.root / "package" / result["elf"]
        self.assertTrue(elf.exists())
        self.assertTrue(elf.with_suffix(".txt").exists())
        self.assertFalse(elf.with_suffix(".bin").exists())
        self.assertEqual(result["bin"], "")
        discard.assert_called_once()

    def test_verifier_failure_is_not_returned_as_publishable_index_row(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_variant("normal", failed_verifier="verify-perf-elf.py")
        self.assertFalse((self.root / "build/release").exists())
        logs = list((self.root / "package/build-logs").rglob("*.log"))
        self.assertEqual(len(logs), 1)


if __name__ == "__main__":
    unittest.main()
