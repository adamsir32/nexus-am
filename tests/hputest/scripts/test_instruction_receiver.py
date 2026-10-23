"""裸指令门禁不能混用SEAL密文、伪优化报告或不完整scenario结果。"""
import unittest

from import_package import instruction_contract, package_profile


class InstructionReceiverTests(unittest.TestCase):
    def setUp(self):
        self.spec = dict(case_id="03_010_padd_l1_n128", kind="instruction", profile="instruction",
                         operation="padd", scheme="raw", degree=128, level=1,
                         program_stem="instruction_padd_l1_n128", memory_base="0x87000000",
                         minimum_ram_bytes=268435456)
        q = [2013265921]
        self.parameters = dict(test_layer="instruction", encrypted=False, plain_modulus=0,
                               input_rns_components=1, context_moduli=q, key_moduli=q,
                               levels=[{"moduli": q}])
        self.graph = dict(test_layer="instruction", component_semantics="scenario_not_ciphertext",
                          component_count=4, terminal_psync_count=1, timing_verified=False,
                          irq_rearm_verified=False, operations=[{"kind": "padd"}],
                          scenario_outputs=[dict(component=i, modulus_id=0, scenario=f"padd/{i}")
                                            for i in range(4)])
        self.report = {key: True for key in ("oracle_verified", "golden_matches_oracle", "model_verified",
                       "raw_physical_words_equal", "readonly_and_guard_verified", "host_instruction_model_verified")}
        self.report.update(test_layer="instruction", overall_status="pass",
                           oracle="independent_u64_modular_and_C_stage_golden",
                           host_instruction_model=dict(required=True, verified=True, status="pass",
                               ntt_contract="legacy_raw_stage", hardware_contract_verified=False, compared_words=512),
                           instruction_execution_verified=False, rtl_verified=False, hardware_verified=False)

    def check(self):
        return instruction_contract(self.spec, self.parameters, self.graph, self.report)

    def test_raw_identity_and_independent_oracle_contract_are_explicit(self):
        package_profile(self.spec)
        moduli, scenarios = self.check()
        self.assertEqual((moduli, len(scenarios)), ([2013265921], 4))

    def test_encrypted_alias_or_fake_optimizer_report_is_rejected(self):
        self.parameters["encrypted"] = True
        with self.assertRaisesRegex(ValueError, "not encrypted SEAL"):
            self.check()
        self.parameters["encrypted"] = False
        for key, value in (("compiler_resources", {}), ("optimization_equivalence_verified", True)):
            with self.subTest(key=key):
                self.report[key] = value
                with self.assertRaisesRegex(ValueError, "must not fabricate"):
                    self.check()
                del self.report[key]

    def test_missing_rns_scenario_and_incomplete_model_comparison_are_rejected(self):
        scenarios = self.graph["scenario_outputs"]
        self.graph["scenario_outputs"] = scenarios[:-1]
        with self.assertRaisesRegex(ValueError, "every RNS/context"):
            self.check()
        self.graph["scenario_outputs"] = scenarios
        self.report["host_instruction_model"]["compared_words"] = 128
        with self.assertRaisesRegex(ValueError, "coverage differs"):
            self.check()

    def test_cannot_claim_hardware_timing_or_seal_scheme(self):
        self.graph["timing_verified"] = True
        with self.assertRaisesRegex(ValueError, "graph/scenario"):
            self.check()
        with self.assertRaisesRegex(ValueError, "instruction identity"):
            package_profile({**self.spec, "scheme": "ckks"})


if __name__ == "__main__":
    unittest.main()
