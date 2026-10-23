"""唯一清单的功能矩阵与例外：覆盖由参数集合定义，不锁死包内总数量。"""
import csv
import itertools
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DEGREES = (128, 1024, 2048, 4096, 8192)
LEVELS = range(1, 5)
SCHEMES = ("ckks", "bfv", "bgv")


class CatalogMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "cases.tsv").open() as stream:
            cls.rows = list(csv.DictReader(stream, delimiter="\t"))

    def matrix(self, profile, fields):
        selected = [row for row in self.rows if row["profile"] == profile]
        values = {tuple(int(row[key]) if key in ("degree", "level") else row[key] for key in fields)
                  for row in selected}
        self.assertEqual(len(values), len(selected), "参数矩阵不得通过重复案例充数")
        return values

    def test_instruction_matrix_covers_nine_operations_at_every_n_and_level(self):
        operations = ("padd", "psub", "pmul", "pmac", "pntt", "pintt", "pmodld", "psync", "pfree")
        self.assertEqual(self.matrix("instruction", ("degree", "level", "operation")),
                         set(itertools.product(DEGREES, LEVELS, operations)))
        self.assertTrue(all(row["scheme"] == "raw" and row["group"] == "03" for row in self.rows
                            if row["profile"] == "instruction"))

    def test_operator_matrix_keeps_raw_primitives_and_three_scheme_keyswitch_separate(self):
        self.assertEqual(self.matrix("primitive", ("degree", "level", "operation")),
                         set(itertools.product(DEGREES, LEVELS, ("bconv", "ntt", "intt"))))
        self.assertEqual(self.matrix("kernel", ("degree", "level", "scheme", "operation")),
                         set(itertools.product(DEGREES, LEVELS, SCHEMES, ("keyswitch",))))
        self.assertTrue(all(row["scheme"] == "raw" for row in self.rows if row["profile"] == "primitive"))

    def test_library_matrix_documents_unsupported_l1_operations_without_fake_cases(self):
        expected = {(degree, level, scheme, operation)
                    for degree, level, scheme, operation in itertools.product(
                        DEGREES, LEVELS, SCHEMES, ("hadd", "hmul", "reline", "modswitch", "rotate"))
                    if not (level == 1 and (operation == "modswitch" or scheme == "bfv" and operation == "hmul"))}
        self.assertEqual(self.matrix("library", ("degree", "level", "scheme", "operation")), expected)
        self.assertEqual(self.matrix("regression", ("scheme", "operation", "degree", "level")),
                         {("bgv", op, 4096, 3) for op in ("hadd", "hmul", "reline", "modswitch", "rotate")} |
                         {("ckks", "rotate", 4096, 4), ("bfv", "rotate", 4096, 4)})

    def test_names_sources_and_optional_api_scope_are_unambiguous(self):
        self.assertEqual(len(self.rows), len({row["case_id"] for row in self.rows}))
        for group in (f"{number:02}" for number in range(8)):
            numbers = [row["case_id"].split("_")[1] for row in self.rows if row["group"] == group]
            self.assertEqual(list(map(int, numbers)), list(range(1, len(numbers) + 1)))
            self.assertTrue(all(len(number) == (3 if group in ("03", "04", "05") else 2) for number in numbers))
        self.assertTrue(all((ROOT / row["source"]).is_file() for row in self.rows))
        api = [row for row in self.rows if row["suite"] == "api"]
        self.assertEqual({(row["scheme"], int(row["degree"])) for row in api},
                         set(itertools.product(SCHEMES, (128, 4096))))
        self.assertTrue(all(row["group"] == "06" for row in api))

    def test_directed_and_regression_profiles_have_independent_n_level_order(self):
        for group in ("03", "04", "05"):
            profiles = {row["profile"] for row in self.rows if row["group"] == group}
            for profile in profiles:
                selected = [(int(row["degree"]), int(row["level"])) for row in self.rows
                            if row["group"] == group and row["profile"] == profile]
                with self.subTest(group=group, profile=profile):
                    self.assertEqual(selected, sorted(selected))


if __name__ == "__main__":
    unittest.main()
