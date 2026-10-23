"""旧路径恢复为单运行包入口，但不得自动重启旧多版本交付流水线。"""
import os
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT.parent / "hputest"


class LegacyEntryRetirementTests(unittest.TestCase):
    def test_default_entries_delegate_to_the_single_runtime_builder(self):
        environment = {key: value for key, value in os.environ.items()
                       if key not in ("MAKEFLAGS", "MFLAGS", "GNUMAKEFLAGS", "HPU_BUILD_SCOPE")}
        for directory, targets in ((BASELINE, (None, "all")), (ROOT, (None, "all", "minimal"))):
            for target in targets:
                with self.subTest(directory=directory.name, target=target or "default"):
                    command = ["make", "--no-print-directory", "-n", "-C", str(directory)]
                    if target is not None:
                        command.append(target)
                    result = subprocess.run(command, text=True, env=environment,
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("build-runtime.py", result.stdout)
                    self.assertNotIn("RETIRED:", result.stdout + result.stderr)
                    for old_builder in ("prepare-inline-asm-mm.sh", "scripts/build.sh", "package-unified.py",
                                        "scripts/build.py", "scripts/build_performance.py"):
                        self.assertNotIn(old_builder, result.stdout)

    def test_old_group_and_case_selectors_delegate_without_legacy_generation(self):
        environment = {key: value for key, value in os.environ.items()
                       if key not in ("MAKEFLAGS", "MFLAGS", "GNUMAKEFLAGS", "HPU_BUILD_SCOPE")}
        for target, option, value in (("group", "GROUP", "00"), ("one", "CASE", "00_02_mmio_rw")):
            with self.subTest(target=target):
                command = ["make", "--no-print-directory", "-n", "-C", str(BASELINE)]
                if target is not None:
                    command.append(target)
                command.append(f"{option}={value}")
                result = subprocess.run(command, text=True, env=environment,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("build-runtime.py", result.stdout)
                self.assertIn("--group" if target == "group" else "--case", result.stdout)
                self.assertIn(value, result.stdout)
                self.assertNotIn("prepare-inline-asm-mm.sh", result.stdout)

    def test_frontend_can_still_use_shared_support_and_case_makefile(self):
        for shared in ("tools/hpu-scheme-cases/fixture.hpp", "runtime/it_perf.c",
                       "runtime/it_log_silent.c", "include/hpu/log.h",
                       "scripts/verify-silent-elf.py", "perf-cases.tsv"):
            with self.subTest(shared=shared):
                self.assertTrue((BASELINE / shared).is_file())

        environment = {key: value for key, value in os.environ.items()
                       if key not in ("MAKEFLAGS", "MFLAGS", "GNUMAKEFLAGS")}
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
