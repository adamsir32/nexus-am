"""精简清单：03～05固定N1024/L4，07固定两种N和三算法L4。"""
import csv
import itertools
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DEGREES = (1024,)
LEVELS = (4,)
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

    def test_instruction_matrix_keeps_nine_operations_at_n1024_l4(self):
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

    def test_library_matrix_keeps_five_operations_per_scheme_at_n1024_l4(self):
        self.assertEqual(self.matrix("library", ("degree", "level", "scheme", "operation")),
                         set(itertools.product(DEGREES, LEVELS, SCHEMES,
                                               ("hadd", "hmul", "reline", "modswitch", "rotate"))))

    def test_functional_groups_have_exactly_thirty_cases_and_no_legacy_matrix(self):
        selected = [row for row in self.rows if row["group"] in ("03", "04", "05")]
        self.assertEqual(len(selected), 30)
        self.assertEqual([sum(row["group"] == group for row in selected) for group in ("03", "04", "05")],
                         [9, 6, 15])
        self.assertTrue(all(row["degree"] == "1024" and row["level"] == "4" for row in selected))
        self.assertEqual({row["profile"] for row in selected}, {"instruction", "primitive", "kernel", "library"})

    def test_performance_matrix_has_thirty_six_cases_and_all_three_schemes_use_l4(self):
        selected = [row for row in self.rows if row["group"] == "07"]
        self.assertEqual(len(selected), 36)
        self.assertTrue(all(row["profile"] == "baseline" and row["kind"] == "performance" for row in selected))
        self.assertEqual(self.matrix("baseline", ("degree", "level", "scheme", "operation")),
                         set(itertools.product((1024, 8192), (4,), SCHEMES,
                                               ("keyswitch", "hadd", "hmul", "reline", "modswitch", "rotate"))))

    def test_names_sources_and_optional_api_scope_are_unambiguous(self):
        self.assertEqual(len(self.rows), len({row["case_id"] for row in self.rows}))
        for group in (f"{number:02}" for number in range(8)):
            numbers = [row["case_id"].split("_")[1] for row in self.rows if row["group"] == group]
            self.assertEqual(list(map(int, numbers)), list(range(1, len(numbers) + 1)))
            self.assertTrue(all(len(number) == 2 for number in numbers))
        self.assertTrue(all((ROOT / row["source"]).is_file() for row in self.rows))
        api = [row for row in self.rows if row["suite"] == "api"]
        self.assertEqual(len(api), 6)
        self.assertEqual({(row["scheme"], int(row["degree"])) for row in api},
                         set(itertools.product(SCHEMES, (128, 4096))))
        self.assertTrue(all(row["group"] == "06" for row in api))

if __name__ == "__main__":
    unittest.main()
