"""04原语接收合同：无伪parms_id、固定用例身份、完整基转换输出。"""
import copy
import csv
from pathlib import Path
import unittest

from import_package import NTT_ABI, package_profile, primitive_outputs, validate_ntt_contract

ROOT = Path(__file__).resolve().parents[1]


class PrimitiveGroupTests(unittest.TestCase):
    def setUp(self):
        with (ROOT / "runtime-groups.tsv").open() as stream:
            self.specs = list(csv.DictReader(stream, delimiter="\t"))
        self.bconv = {**self.specs[0], "kind": "group"}
        self.parameters = {"levels": [{"moduli": [50061313, 50077697, 50307073, 50552833]}],
                           "key_moduli": [50061313, 50077697, 50307073, 50552833,
                                          90062849, 90095617, 90218497]}
        self.operations = [{"id": "tested", "kind": "bconv", "operation_index": 0,
                            "output": "output/result", "exported": True,
                            "golden_object_id": "step_0"}]

    def test_catalog_restores_all_supported_functional_groups(self):
        self.assertEqual(len(self.specs), 54)
        self.assertEqual(len({row["case_id"] for row in self.specs}), 54)
        self.assertEqual([sum(row["case_id"].startswith(group) for row in self.specs)
                          for group in ("04_", "05_", "06_")], [9, 37, 8])
        self.assertTrue(all(int(row["degree"]) <= 8192 and int(row["level"]) <= 4 for row in self.specs))
        self.assertFalse(any("pending" in row["case_id"] or "legacy_auto" in row["case_id"] for row in self.specs))
        self.assertEqual(self.specs[-8]["case_id"], "06_01_ckks_x2_add1_n8192")

    def test_primitive_identity_cannot_be_used_for_another_group_or_size(self):
        package_profile(self.bconv)
        for key, value in (("case_id", "05_01_ckks_hadd_n128"), ("degree", "8192"),
                           ("scheme", "bfv"), ("level", "1"), ("kind", "performance"),
                           ("program_stem", "some_other_kernel")):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "primitive identity"):
                package_profile({**self.bconv, key: value})

    def test_bconv_accepts_q4_to_p3_without_fabricated_ciphertext_metadata(self):
        moduli, domain = primitive_outputs(self.bconv, self.parameters, self.operations)
        self.assertEqual(moduli, {4: 90062849, 5: 90095617, 6: 90218497})
        self.assertEqual(domain, "coefficient")
        self.assertNotIn("parms_id", self.parameters["levels"][0])
        self.assertNotIn("parms_id", self.operations[0])

    def test_bconv_rejects_changed_basis_and_graph(self):
        changed = copy.deepcopy(self.parameters)
        changed["key_moduli"][6] = 90218499
        with self.assertRaisesRegex(ValueError, "original Q4"):
            primitive_outputs(self.bconv, changed, self.operations)
        changed_ops = copy.deepcopy(self.operations)
        changed_ops[0]["kind"] = "rotate"
        with self.assertRaisesRegex(ValueError, "graph mismatch"):
            primitive_outputs(self.bconv, self.parameters, changed_ops)

    def test_ntt_and_intt_have_explicit_opposite_output_domains(self):
        parameters = {"key_moduli": [133881857, 133963777, 134012929, 134111233, 134176769],
                      "levels": [{"moduli": [133881857]}]}
        for index, operation, domain in ((1, "ntt", "canonical_ntt_physical"), (2, "intt", "coefficient")):
            spec = {**self.specs[index], "kind": "group"}
            package_profile(spec)
            ops = [{**self.operations[0], "kind": operation}]
            self.assertEqual(primitive_outputs(spec, parameters, ops), ({0: 133881857}, domain))

    def test_ntt_pre_and_post_use_online_pmul_templates_not_full_vectors(self):
        self.assertEqual(NTT_ABI["version"], 3)
        parameters = {"ntt_table_abi": dict(NTT_ABI)}
        allocations = [
            {"allocation_id": "constants/q0/" + suffix, "kind": "twiddle",
             "read_only": "true", "payload_words": "128", "padded_words": "128",
             "line_count": "2"}
            for suffix in ("pre_twist", "post_untwist_scale", "ntt/stage0", "intt/stage11")
        ]
        validate_ntt_contract(parameters, dict(NTT_ABI), allocations, 4096)
        for index in (0, 1):
            changed = copy.deepcopy(allocations)
            changed[index].update(payload_words="4096", padded_words="4096", line_count="64")
            with self.subTest(parameter=changed[index]["allocation_id"]), self.assertRaises(ValueError):
                validate_ntt_contract(parameters, dict(NTT_ABI), changed, 4096)

    def test_ntt_rejects_an_old_or_missing_online_pmul_contract(self):
        parameters = {"ntt_table_abi": dict(NTT_ABI)}
        for field, value in (("version", 2), ("online_pmul_mode", 0),
                             ("online_pmul_parameter_lines", 64),
                             ("online_pmul_format", "hpu-twiddle-k8-v1")):
            changed = copy.deepcopy(parameters)
            changed["ntt_table_abi"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_ntt_contract(changed, dict(NTT_ABI), [], 4096)


if __name__ == "__main__":
    unittest.main()
