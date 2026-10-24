#!/usr/bin/env python3
"""用真实am/Makefile的单源探针检查HPU标志和CPU/HPU缓存切换。

只在临时目录编译一个主机对象，不修改共享am/build或运行AM全包构建。
"""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]


class AmBuildModeTests(unittest.TestCase):
    def test_mode_propagation_and_incremental_rebuild(self):
        with tempfile.TemporaryDirectory(prefix="am-build-mode-") as temporary:
            directory = Path(temporary)
            (directory / "probe.c").write_text(
                "int am_probe_mode(void) {\n"
                "#ifdef LINKNAN_HPU_IT\nreturn LINKNAN_HPU_IT;\n"
                "#else\nreturn 0;\n#endif\n}\n")
            (directory / "main.c").write_text(
                "int am_probe_mode(void);\n"
                "int main(void) { return am_probe_mode(); }\n")
            object_path = directory / "build/native/probe.o"
            archive = directory / "build/am-native.a"
            stamp = directory / "build/native/.hpu-mode"
            command = ["make", "--no-print-directory", "-s", "-f", str(ROOT / "am/Makefile"),
                       f"AM_HOME={ROOT}", "ARCH=native", "SRCS=probe.c", "CC=cc", "AR=ar",
                       f"LIB_DIR={directory}", f"DST_DIR={object_path.parent}",
                       f"ARCHIVE={archive}"]
            environment = dict(os.environ)
            for name in ("CFLAGS", "MAKEFLAGS", "MFLAGS", "MAKEOVERRIDES"):
                environment.pop(name, None)

            def build(mode):
                if mode is None:
                    environment.pop("LINKNAN_HPU_IT", None)
                    expected = 0
                else:
                    environment["LINKNAN_HPU_IT"] = str(mode)
                    expected = mode
                output = subprocess.check_output(command, cwd=directory,
                                                 env=environment, text=True)
                executable = directory / "probe"
                subprocess.run(["cc", str(directory / "main.c"), str(archive), "-o", str(executable)],
                               check=True)
                self.assertEqual(subprocess.run([str(executable)]).returncode, expected)
                self.assertEqual(stamp.read_text(), f"LINKNAN_HPU_IT={expected}\n")
                return output

            first = build(1)
            self.assertIn("+ CC probe.c", first)
            before = (object_path.stat().st_mtime_ns, archive.stat().st_mtime_ns,
                      stamp.stat().st_mtime_ns)
            repeated = build(1)
            self.assertNotIn("+ CC", repeated)
            self.assertNotIn("+ AR", repeated)
            self.assertEqual(before, (object_path.stat().st_mtime_ns, archive.stat().st_mtime_ns,
                                      stamp.stat().st_mtime_ns))
            for mode in (0, 1, None):
                changed = build(mode)
                self.assertIn("+ CC probe.c", changed)
                self.assertIn("+ AR", changed)
            # 默认CPU模式重复执行也必须是增量命中。
            self.assertNotIn("+ CC", build(None))


if __name__ == "__main__":
    unittest.main()
