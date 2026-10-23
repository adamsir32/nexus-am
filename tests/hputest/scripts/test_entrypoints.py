"""两个顶层路径只转发同一构建器，case路径不污染递归AM构建。"""
import os
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT
FRONTEND = ROOT.parent / "hpu_frontend_workload"


class UnifiedEntrypointTests(unittest.TestCase):
    def test_default_entries_delegate_to_the_single_runtime_builder(self):
        environment = {key: value for key, value in os.environ.items()
                       if key not in ("MAKEFLAGS", "MFLAGS", "GNUMAKEFLAGS", "HPU_BUILD_SCOPE")}
        for directory, targets in ((BASELINE, (None, "all")), (FRONTEND, (None, "all"))):
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

    def test_native_case_makefile_uses_local_case_paths_and_shared_support(self):
        for shared in ("tools/common/fixture.hpp", "runtime/it_perf.c",
                       "runtime/it_log_silent.c", "include/hpu/log.h",
                       "scripts/verify-silent-elf.py", "cases.tsv"):
            with self.subTest(shared=shared):
                self.assertTrue((BASELINE / shared).is_file())

        environment = {key: value for key, value in os.environ.items()
                       if key not in ("MAKEFLAGS", "MFLAGS", "GNUMAKEFLAGS")}
        # 使用真实新前端Makefile.case和既有的免构建AM探针，
        # 同时覆盖性能版与静默版的共用源码选择。
        result = subprocess.run([
            "make", "--no-print-directory", "-n", "-C", str(ROOT),
            "-f", "Makefile.native.case", "image",
            f"AM_HOME={ROOT / 'test/build-isolation'}",
            "CASE_ID=RETIREMENT_PROBE", f"DATA_DIR={ROOT / 'test'}",
            "CASE_OBJ_DIR=retirement-probe-objects", "CASE_BINARY=retirement-probe",
            "CASE_SOURCE=src/06_applications/06_02_ckks_rotate_conj_mul_add_n128.c", "PROGRAM_STEM=probe",
            "PERFORMANCE=1", "CASE_MEM_BASE=0x90000000", "LOG_LEVEL=0",
            "CASE_DEGREE=4096", "CASE_LEVEL=4",
        ], text=True, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("parent_dst=", result.stdout)
        self.assertNotIn("RETIRED:", result.stdout + result.stderr)

    def test_native_makefile_links_the_explicit_main_with_generated_header_dependencies(self):
        text = (ROOT / "Makefile.native.case").read_text()
        self.assertIn("SRCS := $(CASE_SOURCE)", text)
        self.assertIn("$(CASE_SOURCE:.c=.o)): $(DATA_DIR)/layout.h $(DATA_DIR)/program.h", text)
        self.assertNotIn("runtime/native_case.c", text)
        self.assertNotIn("WORKLOAD_RUN", text)
        self.assertNotIn("WORKLOAD_VALIDATE", text)

    def test_legacy_directed_03_cannot_reenter_lowlevel_makefile(self):
        result = subprocess.run([
            "make", "--no-print-directory", "-n", "-C", str(ROOT), "-f", "Makefile.case", "image",
            f"AM_HOME={ROOT.parents[1]}", "CASE_ID=03_001_padd", "CASE_SOURCE=removed-directed.c",
            "HPU_DST_DIR=unused-probe", "CASE_BINARY=unused-probe"],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a supported directed 00/01/02 testcase", result.stderr)


if __name__ == "__main__":
    unittest.main()
