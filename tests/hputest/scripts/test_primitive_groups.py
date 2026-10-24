"""04原语矩阵合同：QL→P3、全Q的NTT/INTT，不伪造密文parms_id。"""
import copy
import csv
import itertools
from pathlib import Path
import unittest

from import_package import NTT_ABI, package_profile, primitive_outputs, validate_ntt_contract

ROOT = Path(__file__).resolve().parents[1]


class PrimitiveGroupTests(unittest.TestCase):
    def specification(self, operation="bconv", degree=1024, level=4):
        return dict(case_id=f"04_01_{operation}_l{level}_n{degree}", kind="native", profile="primitive",
                    scheme="raw", operation=operation, degree=degree, level=level,
                    program_stem=f"{operation}_l{level}_n{degree}", memory_base="0x87000000",
                    minimum_ram_bytes=268435456)

    def operations(self, operation):
        return [dict(id="tested", kind=operation, operation_index=0, output="output/result",
                     exported=True, golden_object_id="step_0")]

    def test_catalog_primitive_matrix_has_all_degrees_and_levels(self):
        with (ROOT / "cases.tsv").open() as stream:
            rows = [row for row in csv.DictReader(stream, delimiter="\t") if row["profile"] == "primitive"]
        expected = {(operation, 1024, 4) for operation in ("bconv", "ntt", "intt")}
        actual = {(r["operation"], int(r["degree"]), int(r["level"])) for r in rows}
        self.assertEqual(actual, expected)
        self.assertEqual(len(rows), len(actual))

    def test_primitive_identity_rejects_other_layers_schemes_and_mismatched_stems(self):
        spec = self.specification()
        package_profile(spec)
        for key, value in (("case_id", "05_01_ckks_hadd_l4_n1024"), ("scheme", "bfv"),
                           ("program_stem", "some_other_kernel")):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "primitive identity"):
                package_profile({**spec, key: value})

    def test_bconv_uses_only_declared_q_prefix_and_all_three_p_outputs(self):
        for level in range(1, 5):
            q = [50061313, 50077697, 50307073, 50552833][:level]
            p = [90062849, 90095617, 90218497]
            parameters = {"levels": [{"moduli": q}], "key_moduli": q + p}
            moduli, domain = primitive_outputs(self.specification(level=level), parameters, self.operations("bconv"))
            self.assertEqual(moduli, dict(enumerate(p, level)))
            self.assertEqual(domain, "coefficient")
            parameters["key_moduli"][-1] += 2
            with self.assertRaisesRegex(ValueError, "Q-prefix"):
                primitive_outputs(self.specification(level=level), parameters, self.operations("bconv"))

    def test_unsupported_l1_library_operations_are_rejected_at_the_receiver_boundary(self):
        for scheme, operation in (("ckks", "modswitch"), ("bfv", "modswitch"),
                                  ("bgv", "modswitch"), ("bfv", "hmul")):
            spec = dict(case_id=f"05_01_{scheme}_{operation}_l1_n128", kind="native", profile="library",
                        scheme=scheme, operation=operation, degree=128, level=1,
                        program_stem=f"seal_{scheme}_{operation}_n128", memory_base="0x87000000",
                        minimum_ram_bytes=268435456)
            with self.subTest(scheme=scheme, operation=operation), self.assertRaisesRegex(ValueError, "N1024/L4"):
                package_profile(spec)

    def test_ntt_intt_check_every_q_limb_and_opposite_output_domains(self):
        for level in range(1, 5):
            q = [133881857, 133963777, 134012929, 134111233][:level]
            parameters = {"key_moduli": q + [134176769], "levels": [{"moduli": q}]}
            for operation, domain in (("ntt", "canonical_ntt_physical"), ("intt", "coefficient_bit_reversed")):
                actual = primitive_outputs(self.specification(operation, level=level), parameters,
                                           self.operations(operation))
                self.assertEqual(actual, (dict(enumerate(q)), domain))

    def test_ntt_pre_and_post_use_online_pmul_templates_not_full_vectors(self):
        parameters = {"ntt_table_abi": dict(NTT_ABI)}
        allocations = [{"allocation_id": "constants/q0/" + suffix, "kind": "twiddle",
                        "read_only": "true", "payload_words": "128", "padded_words": "128",
                        "line_count": "2"}
                       for suffix in ("pre_twist", "post_untwist_scale", "ntt/stage0", "intt/stage11")]
        validate_ntt_contract(parameters, dict(NTT_ABI), allocations, 4096)
        for index in (0, 1):
            changed = copy.deepcopy(allocations)
            changed[index].update(payload_words="4096", padded_words="4096", line_count="64")
            with self.assertRaises(ValueError):
                validate_ntt_contract(parameters, dict(NTT_ABI), changed, 4096)


if __name__ == "__main__":
    unittest.main()
