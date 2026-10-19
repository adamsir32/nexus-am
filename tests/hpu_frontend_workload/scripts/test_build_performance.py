"""只验证新07的构建/发布/ELF门禁；测试夹具不是硬件执行结果。"""
import json
import os
from pathlib import Path
import struct
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

import build_performance as build


STEM = "probe"
CFG = """00001000 <main>:
    1000: 000000ef jal 2000 <hpu_validate_probe>
    1004: 00000063 bnez a0,1034 <main+0x34>
    1008: 000000ef jal 2100 <perf_cycle_read>
    100c: 000000ef jal 2200 <hpu_run_probe>
    1010: 00000063 beqz a0,1020 <main+0x20>
    1014: 000000ef jal 2100 <perf_cycle_read>
    1018: 0000006f j 3000 <case_fail>
    1020: 000000ef jal 2300 <performance_wait>
    1024: 000000ef jal 2100 <perf_cycle_read>
    1028: 000000ef jal 2400 <check_results>
    102c: 000000ef jal 2500 <check_memory>
    1030: 0000006f j 3100 <case_pass>
    1034: 0000006f j 3000 <case_fail>
00002000 <hpu_validate_probe>:
    2000: 00008067 ret
00002200 <hpu_run_probe>:
    2200: 7000005b .word 0x7000005b
    2204: 00008067 ret
00002300 <performance_wait>:
    2300: 00008067 ret
"""


class TimingTests(unittest.TestCase):
    def test_gcc_copied_failure_stop_does_not_add_a_success_sample(self):
        build.verify_timing(CFG, STEM)

    def test_pass_path_cannot_skip_wait(self):
        broken = CFG.replace("1010: 00000063 beqz a0,1020", "1010: 00000063 beqz a0,1024")
        with self.assertRaisesRegex(ValueError, "ordering differs"):
            build.verify_timing(broken, STEM)

    def test_a_second_pass_path_cannot_bypass_the_measurement(self):
        broken = CFG.replace("1004: 00000063 bnez a0,1034", "1004: 00000063 bnez a0,1030")
        with self.assertRaisesRegex(ValueError, "ordering differs"):
            build.verify_timing(broken, STEM)

    def test_logging_between_issue_and_stop_is_rejected(self):
        broken = CFG.replace("1020: 000000ef jal 2300 <performance_wait>",
                             "1020: 000000ef jal 2300 <performance_wait>\n"
                             "1022: 000000ef jal 3200 <printf_>")
        with self.assertRaisesRegex(ValueError, "ordering differs"):
            build.verify_timing(broken, STEM)

    def test_extra_cycle_on_success_is_rejected(self):
        broken = CFG.replace("1028: 000000ef jal 2400 <check_results>",
                             "1026: 000000ef jal 2100 <perf_cycle_read>\n"
                             "1028: 000000ef jal 2400 <check_results>")
        with self.assertRaisesRegex(ValueError, "ordering differs"):
            build.verify_timing(broken, STEM)

    def test_preflight_must_not_issue_hpu(self):
        broken = CFG.replace("2000: 00008067 ret", "2000: 7000005b .word 0x7000005b")
        with self.assertRaisesRegex(ValueError, "preflight issues"):
            build.verify_timing(broken, STEM)


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="frontend-perf-build-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_twelve_scopes_cover_72_cases_without_overlap(self):
        rows = [row for degree in (4096, 8192) for profile in ("baseline", "l16")
                for scheme in ("ckks", "bfv", "bgv") for row in build.select_specs(degree, profile, scheme)]
        self.assertEqual(len(rows), 72)
        self.assertEqual(len({row["case_id"] for row in rows}), 72)

    def test_cache_cannot_switch_producer_or_fixture_recipe(self):
        marker = self.root / "request.json"
        build.cache_request(marker, {"producer_commit": "one", "shared_fixture_source": "recipe one"})
        with self.assertRaisesRegex(ValueError, "existing cache differs"):
            build.cache_request(marker, {"producer_commit": "one", "shared_fixture_source": "recipe two"})
        self.assertEqual(json.loads(marker.read_text())["shared_fixture_source"], "recipe one")

    def test_native_validator_is_an_explicit_build_target(self):
        args = SimpleNamespace(producer=self.root / "producer", output=self.root, jobs=2, producer_build=None)
        commands = []
        with patch.object(build, "output", side_effect=["pin", ""]), \
                patch.object(build, "run", side_effect=lambda command: commands.append(command)):
            build.prepare_producer(args, "pin")
        self.assertIn("hpu_validate_package", commands[-1])
        self.assertIn("hpu_frontend_operator_generator", commands[-1])

    def test_case_paths_do_not_leak_to_recursive_am_make(self):
        args = SimpleNamespace(work=self.root, am_home=build.ROOT.parents[1], arch="riscv64-xs",
                               cross="riscv64-linux-gnu-", wait_cycles=999)
        spec = {**build.select_specs(4096, "baseline", "ckks")[0], "variant": "optimized"}
        recorded = []
        def stop(command, **kwargs):
            recorded.extend(command)
            raise RuntimeError("captured")
        with patch.object(build, "run", side_effect=stop):
            with self.assertRaisesRegex(RuntimeError, "captured"):
                build.build_case(args, spec, self.root / "data", {}, "minimal")
        self.assertTrue(any(str(value).startswith("CASE_OBJ_DIR=") for value in recorded))
        self.assertTrue(any(str(value).startswith("CASE_BINARY=") for value in recorded))
        self.assertFalse(any(str(value).startswith(("DST_DIR=", "BINARY=")) for value in recorded))

    def test_zip_streams_native_and_target_once_and_keeps_resource_evidence(self):
        spec = build.select_specs(4096, "baseline", "ckks")[0]
        selected = {**spec, "variant": "optimized"}
        args = SimpleNamespace(output=self.root, work=self.root / "work", degree=4096,
                               profile="baseline", scheme="ckks", am_home=build.ROOT.parents[1])
        source, data = self.root / "package/optimized/upstream", self.root / "data"
        source.mkdir(parents=True); data.mkdir()
        (source / "package.json").write_text('{"test":true}')
        for name in ("PERF_FIXTURE.json", "RESOURCE_REPORT.json"):
            (source.parent / name).write_text('{"test":true}')
        (data / "image.u32.bin").write_bytes(b"image")
        files = {}
        for key, extension in (("elf", ".elf"), ("bin", ".bin"), ("disassembly", ".txt")):
            path = args.work / "artifact" / (spec["case_id"] + extension)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"test artifact")
            files[key] = str(path.relative_to(args.work))
        with patch.object(build, "output", side_effect=["am-revision", " M local-change"]):
            archive = build.publish(args, [(selected, source, data, {}, {})], [{**selected, **files}], "pin", [spec])
        self.assertFalse((args.work / "artifact/delivery").exists())
        with zipfile.ZipFile(archive) as zipped:
            names = zipped.namelist()
            self.assertEqual(len(names), len(set(names)))
            self.assertIn("tools/parse_performance.py", names)
            self.assertIn("PERFORMANCE.md", names)
            self.assertIn("performance-baseline.json", names)
            self.assertEqual(sum(name.endswith("RESOURCE_REPORT.json") for name in names), 1)
            self.assertEqual(json.loads(zipped.read("index.json"))["nexus_am_worktree_state"], "dirty")


class EmbeddedDataTests(unittest.TestCase):
    def test_readonly_embedded_payload_is_compared_byte_for_byte(self):
        with tempfile.TemporaryDirectory(prefix="frontend-perf-elf-test-") as temporary:
            root = Path(temporary)
            contents = (("initial_image", "image.u32.bin", b"IMG0"),
                        ("golden_words", "golden.u32.bin", b"GLD0"),
                        ("writable_lines", "writable.u8.bin", b"\x01"))
            blob = bytearray(0x209)
            blob[:6] = b"\x7fELF\x02\x01"
            struct.pack_into("<H", blob, 18, 243)
            struct.pack_into("<QQ", blob, 32, 64, 120)
            struct.pack_into("<HHHH", blob, 54, 56, 1, 64, 2)
            struct.pack_into("<IIQQQQQQ", blob, 64, 1, 4, 0, 0x80000000, 0x80000000, len(blob), len(blob), 256)
            struct.pack_into("<IIQQQQIIQQ", blob, 184, 0, 1, 2, 0x80000100, 0x200, 9, 0, 0, 256, 0)
            listing, offset = [], 0
            for symbol, filename, payload in contents:
                (root / filename).write_bytes(payload)
                blob[0x200 + offset:0x200 + offset + len(payload)] = payload
                listing.append(f"{0x80000100 + offset:016x} {len(payload):016x} R {symbol}")
                offset += len(payload)
            elf = root / "probe.elf"
            elf.write_bytes(blob)
            meta = {"memory_base": "0x90000000", "minimum_ram_bytes": 536870912}
            with patch.object(build, "output", return_value="\n".join(listing)):
                build.verify_embedded(elf, root, meta, "unused-")
                (root / "golden.u32.bin").write_bytes(b"bad!")
                with self.assertRaisesRegex(ValueError, "embedded data differs"):
                    build.verify_embedded(elf, root, meta, "unused-")


if __name__ == "__main__":
    unittest.main()
