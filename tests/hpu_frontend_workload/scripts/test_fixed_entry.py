"""六项应用的ELF门禁必须检查实际执行的fixed入口，而非未调用的dynamic副本。"""
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

import build


class FixedEntryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="frontend-fixed-entry-test-")
        self.addCleanup(self.temp.cleanup)
        self.elf = Path(self.temp.name) / "probe.elf"
        header = bytearray(64)
        header[:6] = b"\x7fELF\x02\x01"
        struct.pack_into("<H", header, 18, 243)
        self.elf.write_bytes(header)

    def test_fixed_entry_takes_priority_over_unused_dynamic_body(self):
        commands = []

        def output(command):
            commands.append(command)
            if command[0].endswith("nm"):
                return "80000100 00000004 T hpu_run_probe\n80000200 00000004 T hpu_program_probe"
            self.assertIn("--disassemble=hpu_run_probe", command)
            return "    80000100: 7000005b .word 0x7000005b"

        with patch.object(build, "output", side_effect=output):
            self.assertEqual(build.verify_elf(self.elf, "riscv-", {"program_stem": "probe"}), [0x7000005b])
        self.assertEqual(len(commands), 2)

    def test_old_wrapper_can_fall_back_to_its_dynamic_callee(self):
        def output(command):
            if command[0].endswith("nm"):
                return "80000100 00000004 T hpu_run_probe\n80000200 00000004 T hpu_program_probe"
            if "--disassemble=hpu_run_probe" in command:
                return "    80000100: 1000006f j 80000200 <hpu_program_probe>"
            self.assertIn("--disassemble=hpu_program_probe", command)
            return "    80000200: 7000005b .word 0x7000005b"

        with patch.object(build, "output", side_effect=output):
            self.assertEqual(build.verify_elf(self.elf, "riscv-", {"program_stem": "probe"}), [0x7000005b])

    def test_native_build_does_not_enable_optional_dependency_or_oracle_checks(self):
        commands = []
        with patch.object(build, "output", side_effect=["pin", ""]), \
                patch.object(build, "read_json", return_value={"commit": "pin"}), \
                patch.object(build, "run", side_effect=lambda command: commands.append(command)):
            self.assertEqual(build.prepare_producer(Path("producer"), Path("native"), 2), "pin")
        for setting in ("BUILD_TESTING", "SEAL_USE_MSGSL", "SEAL_USE_ZLIB", "SEAL_USE_ZSTD",
                        "SEAL_USE_INTEL_HEXL", "HPU_ENABLE_SEAL_DIFFERENTIAL_ORACLE"):
            self.assertIn(f"-D{setting}=OFF", commands[0])
        self.assertIn("hpu_validate_package", commands[1])


if __name__ == "__main__":
    unittest.main()
