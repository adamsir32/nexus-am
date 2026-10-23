"""新07接收策略测试；不调用native生成器，不把格式夹具当作FHE验证。"""
import json
from pathlib import Path
import tempfile
import unittest

from build_performance import validate_fixture
from import_package import NTT_ABI, expected_operations, package_profile, store_or_verify, validate_capacity


def specification(level=4):
    return {"case_id": "07_39_ckks_hmul_reline_l4_n4096", "kind": "performance", "profile": "baseline", "scheme": "ckks", "degree": 4096, "operation": "hmul", "level": level,
            "variant": "optimized", "program_stem": f"frontend_ckks_hmul_l{level}_n4096",
            "memory_base": "0xc0000000" if level == 16 else "0x90000000",
            "minimum_ram_bytes": 2147483648 if level == 16 else 536870912}


class PerformanceReceiverTests(unittest.TestCase):
    def test_active_profile_uses_explicit_ram_contract(self):
        validate_capacity(specification(), 200 * 1024 * 1024 // 256)
        with self.assertRaisesRegex(ValueError, "explicit 07 RAM"):
            validate_capacity(specification(), 268435456 // 256)

    def test_retired_level16_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported degree/level"):
            package_profile(specification(16))

    def test_memory_and_stem_cannot_be_silently_mismatched(self):
        spec = specification()
        spec["memory_base"] = "0x87000000"
        with self.assertRaisesRegex(ValueError, "memory contract"):
            package_profile(spec)
        spec = specification()
        spec["program_stem"] = "different_operator"
        with self.assertRaisesRegex(ValueError, "stem mismatch"):
            package_profile(spec)

    def test_hmul_means_multiply_then_relinearize(self):
        self.assertEqual(expected_operations("bfv", "hmul"), ["multiply", "relinearize"])
        self.assertEqual(expected_operations("ckks", "modswitch"), ["rescale"])

    def test_cached_binary_is_verified_without_rewriting(self):
        with tempfile.TemporaryDirectory(prefix="frontend-perf-cache-test-") as temporary:
            path = Path(temporary) / "image.bin"
            path.write_bytes(b"correct")
            store_or_verify(path, b"correct", True)
            with self.assertRaisesRegex(ValueError, "cached delivery content differs"):
                store_or_verify(path, b"changed", True)
            self.assertEqual(path.read_bytes(), b"correct")

    def test_fixture_requires_actual_q_p_and_strict_native_verification(self):
        spec = specification()
        fixture = {**spec, "schema_version": 1, "producer_commit": "pin", "producer_worktree_state": "clean-at-configure",
                   "verified": True, "instruction_verified": True, "fixture_words_equal": True,
                   "fixture_metadata_equal": True, "native_package_written": True, "hardware_verified": False,
                   "ntt_contract": "natural_coefficient_boundaries", "ntt_table_abi": NTT_ABI,
                   "node_operations": ["multiply", "relinearize"], "Q": [17, 19, 23, 29], "P": [31]}
        with tempfile.TemporaryDirectory(prefix="frontend-perf-fixture-test-") as temporary:
            path = Path(temporary) / "PERF_FIXTURE.json"
            path.write_text(json.dumps(fixture))
            validate_fixture(path, spec, "pin")
            del fixture["Q"]
            path.write_text(json.dumps(fixture))
            with self.assertRaisesRegex(ValueError, "Q/P moduli"):
                validate_fixture(path, spec, "pin")


if __name__ == "__main__":
    unittest.main()
