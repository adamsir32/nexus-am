"""同名发令源码是实际构建门禁，不是无人引用的展示副本。"""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import case_program


class CaseProgramTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hpu-case-program-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / "package"
        (self.package / "program").mkdir(parents=True)
        (self.package / "package.json").write_text(json.dumps({"program_asm": "program/op.asm"}))
        (self.package / "program/op.asm").write_text("padd p2, p0, p1\npsync\n")
        self.source = self.root / "src/05_library/01_n128/05_001_ckks_hadd_l1_n128.c"
        self.source.parent.mkdir(parents=True)
        self.source.write_text("int main(void) { return 0; }\n")
        self.source.with_suffix(".asm").write_text("padd p2, p0, p1\npsync\n")
        self.spec = dict(source=self.source.relative_to(self.root).as_posix(),
                         case_id=self.source.stem, kind="native")
        self.patcher = patch.object(case_program, "ROOT", self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_same_program_is_accepted_without_writing_source(self):
        source = self.source.with_suffix(".asm")
        before = source.stat().st_mtime_ns
        self.assertEqual(case_program.verify_case_program(self.package, self.spec), source)
        self.assertEqual(source.stat().st_mtime_ns, before)

    def test_missing_or_different_program_is_rejected(self):
        self.source.with_suffix(".asm").write_text("psub p2, p0, p1\npsync\n")
        with self.assertRaisesRegex(ValueError, "发令序列"):
            case_program.verify_case_program(self.package, self.spec)
        self.source.with_suffix(".asm").unlink()
        with self.assertRaisesRegex(ValueError, "缺失"):
            case_program.verify_case_program(self.package, self.spec)

    def test_noopt_requires_its_own_reviewed_program(self):
        spec = dict(self.spec, kind="performance", variant="noopt")
        with self.assertRaisesRegex(ValueError, "缺失"):
            case_program.verify_case_program(self.package, spec)
        self.source.with_suffix(".noopt.asm").write_text("padd p2, p0, p1\npsync\n")
        self.assertEqual(case_program.verify_case_program(self.package, spec),
                         self.source.with_suffix(".noopt.asm"))

    def test_mismatched_name_and_escaping_paths_are_rejected(self):
        for spec in (dict(self.spec, case_id="05_002_other"),
                     dict(self.spec, source="../" + self.spec["source"])):
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                case_program.verify_case_program(self.package, spec)
        (self.package / "package.json").write_text(json.dumps({"program_asm": "../op.asm"}))
        with self.assertRaisesRegex(ValueError, "安全"):
            case_program.verify_case_program(self.package, self.spec)


if __name__ == "__main__":
    unittest.main()
