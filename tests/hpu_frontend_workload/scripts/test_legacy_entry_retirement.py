"""停用旧顶层入口时不能停用新前端依赖的共用支持。"""
import os
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT.parent / "hputest"


class LegacyEntryRetirementTests(unittest.TestCase):
    def test_old_entry_stops_before_work_and_frontend_case_still_parses(self):
        environment = {key: value for key, value in os.environ.items()
                       if key not in ("MAKEFLAGS", "MFLAGS", "GNUMAKEFLAGS")}
        for target in (None, "all", "performance-shard", "prepare-inline-asm-mm"):
            with self.subTest(target=target or "default"):
                command = ["make", "--no-print-directory", "-n", "-C", str(BASELINE)]
                if target is not None:
                    command.append(target)
                result = subprocess.run(command, text=True, env=environment,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("RETIRED:", result.stderr)
                self.assertIn("tests/hpu_frontend_workload", result.stderr)
                self.assertIn("backup/master-before-1019-20261023@9016ef9c", result.stderr)
                self.assertEqual(result.stdout, "", "old prepare/build recipes must not start")

        for shared in ("tools/hpu-scheme-cases/fixture.hpp", "runtime/it_perf.c",
                       "runtime/it_log_silent.c", "include/hpu/log.h",
                       "scripts/verify-silent-elf.py", "perf-cases.tsv"):
            with self.subTest(shared=shared):
                self.assertTrue((BASELINE / shared).is_file())

        # 使用真实新前端Makefile.case和既有的免构建AM探针，
        # 同时覆盖性能版与静默版的共用源码选择。
        result = subprocess.run([
            "make", "--no-print-directory", "-n", "-C", str(ROOT),
            "-f", "Makefile.case", "image",
            f"AM_HOME={ROOT / 'test/build-isolation'}",
            "CASE_ID=RETIREMENT_PROBE", f"DATA_DIR={ROOT / 'test'}",
            "CASE_OBJ_DIR=retirement-probe-objects", "CASE_BINARY=retirement-probe",
            "CASE_SOURCE=src/ckks_n128.c", "PROGRAM_STEM=probe",
            "PERFORMANCE=1", "CASE_MEM_BASE=0x90000000", "LOG_LEVEL=0",
        ], text=True, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("parent_dst=", result.stdout)
        self.assertNotIn("RETIRED:", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
