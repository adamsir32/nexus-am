"""源码审计只识别清单/案例参数，不把架构常数当作IT测试规模。"""
import csv
from pathlib import Path
import tempfile
import unittest

from audit_sources import references, validate_catalogs


class SourceAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="hpu-source-audit-")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.root = Path("tests/hputest")
        (self.repo / self.root).mkdir(parents=True)
        self.catalog = self.root / "cases.tsv"

    def check(self, rows, extra=()):
        fields = ("group", "case_id", "source", "scheme", "operation", "degree", "level", "profile", "program_stem")
        with (self.repo / self.catalog).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)
        files = {str(self.root / row["source"]) for row in rows} | set(extra)
        return validate_catalogs(self.repo, self.root, [self.catalog], files)[2]

    def row(self, number, degree=1024, level=4, profile="library", operation="hadd"):
        return {"group": "05", "case_id": f"05_{number:02}_ckks_{operation}_n{degree}_l{level}",
                "source": f"src/group_{number}.c", "scheme": "ckks", "operation": operation,
                "degree": degree, "level": level, "profile": profile,
                "program_stem": f"ckks_{operation}_n{degree}_l{level}"}

    def test_two_digit_ids_with_separate_sources_are_valid_and_three_digits_are_rejected(self):
        rows = []
        for number in range(1, 16):
            row = self.row(number)
            row["operation"] = f"directed_{number}"
            row["program_stem"] = f"program_{number}"
            rows.append(row)
        self.assertEqual(self.check(rows), [])
        row = self.row(100)
        self.assertTrue(any("非法case_id" in error for error in self.check([row])))

    def test_shared_main_is_rejected_even_when_parameters_differ(self):
        first, second = self.row(1), self.row(2, operation="hmul")
        second["source"] = first["source"]
        self.assertTrue(any("不能复用" in error for error in self.check([first, second])))

    def test_retired_parameters_are_rejected_independently_of_profile(self):
        for profile in ("library", "regression"):
            for degree, level in ((128, 4), (1024, 1), (2048, 4), (4096, 4), (8192, 4)):
                with self.subTest(profile=profile, degree=degree, level=level):
                    errors = self.check([self.row(1, degree, level, profile)])
                    self.assertTrue(any("N1024/L4" in error for error in errors))

    def test_two_performance_scales_are_l4_but_application_scales_are_preserved(self):
        for degree, level in ((1024, 4), (8192, 4), (2048, 4), (4096, 4), (1024, 3)):
            row = self.row(1, degree, level)
            row.update(group="07", case_id=row["case_id"].replace("05_", "07_", 1))
            with self.subTest(group="07", degree=degree, level=level):
                errors = self.check([row])
                self.assertEqual(bool(errors), (degree, level) not in ((1024, 4), (8192, 4)))
        for degree in (128, 4096, 8192):
            row = self.row(1, degree, 3, "application")
            row.update(group="06", case_id=row["case_id"].replace("05_", "06_", 1))
            with self.subTest(group="06", degree=degree):
                self.assertEqual(self.check([row]), [])

    def test_holes_duplicates_large_parameters_and_l1_drop_are_rejected(self):
        scenarios = ([self.row(2)], [self.row(1), self.row(2)],
                     [self.row(1, 16384)], [self.row(1, 8192, 16)],
                     [self.row(1, level=1, operation="modswitch")])
        for rows in scenarios:
            with self.subTest(rows=rows):
                self.assertTrue(self.check(rows))

    def test_orphan_case_source_is_rejected_but_architecture_constant_is_not_a_case(self):
        extra = str(self.root / "src/03_instructions/03_99_padd_n65536.c")
        errors = self.check([self.row(1)], [extra])
        self.assertTrue(any("未被canonical" in error for error in errors))
        self.assertTrue(any("文件名参数" in error for error in errors))
        path = self.root / "scripts/architecture.py"
        (self.repo / path.parent).mkdir()
        (self.repo / path).write_text("MAX_ADDRESS = 65536\n")
        self.assertEqual(references(self.repo, {str(path)})[1], [])

    def test_missing_local_legacy_import_and_explicit_owned_reference_are_rejected(self):
        path = self.root / "scripts/helper.py"
        (self.repo / path.parent).mkdir()
        (self.repo / path).write_text("import case_catalog\nSOURCE = 'tests/hputest/src/missing.c'\n")
        errors = references(self.repo, {str(path)})[1]
        self.assertTrue(any("本地模块" in error for error in errors))
        self.assertTrue(any("悬空项目" in error for error in errors))

    def test_relative_reference_resolves_even_when_basenames_repeat(self):
        caller = self.root / "tools/operator_perf/CMakeLists.txt"
        target = self.root / "tools/group_cases/generator.cpp"
        other = self.root / "tools/instruction_cases/generator.cpp"
        (self.repo / caller.parent).mkdir(parents=True)
        (self.repo / caller).write_text("add_executable(group ../group_cases/generator.cpp)\n")
        for source in (target, other):
            (self.repo / source.parent).mkdir(parents=True)
            (self.repo / source).write_text("// reference fixture\n")
        edges, errors = references(self.repo, {str(caller), str(target), str(other)})
        self.assertEqual(errors, [])
        self.assertEqual(edges[str(caller)], {str(target)})


if __name__ == "__main__":
    unittest.main()
