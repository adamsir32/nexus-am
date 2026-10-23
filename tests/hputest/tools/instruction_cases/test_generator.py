#!/usr/bin/env python3
"""检查03参数矩阵的真实RNS切换、定向场景及native包边界。"""

import argparse
from pathlib import Path
import json
import subprocess
import tempfile


def run(command, success=True):
    result = subprocess.run([str(value) for value in command], capture_output=True, text=True)
    assert (result.returncode == 0) == success, result.stdout + result.stderr
    return result


def check_package(generator, validator, directory, operation, n, level):
    run([generator, operation, n, level, directory])
    run([validator, directory])
    package = json.loads((directory / "package.json").read_text())
    parameters = json.loads((directory / "metadata/parameters.json").read_text())
    graph = json.loads((directory / "metadata/operation_graph.json").read_text())
    report = json.loads((directory / "oracle/report.json").read_text())
    assert parameters["test_layer"] == "instruction" and parameters["encrypted"] is False
    assert parameters["poly_modulus_degree"] == n
    qs = parameters["levels"][0]["moduli"]
    assert len(qs) == len(set(qs)) == parameters["input_rns_components"] == level
    assert qs == parameters["key_moduli"] == parameters["context_moduli"]
    assert graph["operations"][0]["kind"] == operation
    assert graph["operations"][0]["exported"] is True
    assert graph["operations"][0]["golden_object_id"] == "step_0"
    assert graph["terminal_psync_count"] == 1
    assert graph["timing_verified"] is False and graph["irq_rearm_verified"] is False
    assert report["readonly_and_guard_verified"] is True
    assert report["host_instruction_model_verified"] is True
    assert report["host_instruction_model"]["ntt_contract"] == "legacy_raw_stage"
    assert all(report[key] is False for key in
               ("hardware_verified", "rtl_verified", "instruction_execution_verified"))
    assert "optimization_equivalence_verified" not in report
    words = [int(row, 2) for row in (directory / package["program_inst32"]).read_text().splitlines() if row]
    assert words[-1] == 0x7000005B and words.count(0x7000005B) == 1
    # 从实际机器字读取PMODLD的mod_id，不能仅根据metadata声称覆盖L个模数。
    selections = {(word >> 8) & 255 for word in words if word & 0xF000007F == 0x6000005B}
    assert selections == set(range(level)), selections
    expected_components = {"pmodld": 4, "pmul": 10, "pintt": 6}[operation]
    assert graph["component_count"] == expected_components
    scenarios = graph["scenario_outputs"]
    assert {(row["component"], row["modulus_id"]) for row in scenarios} == {
        (component, modulus) for component in range(expected_components) for modulus in range(level)}
    if operation == "pmul":
        online = [word for word in words if word & 127 == 0x5B and word >> 28 == 2
                  and word & 128 == 0 and word >> 14 & 3 == 1]
        assert len(online) == 2 * level
        immediates = {word >> 8 & 255 for word in words
                      if word & 127 == 0x5B and word >> 28 == 2 and word & 128}
        assert {0, 1, 7, 64, 192, 255} <= immediates
    before = (directory / "package.json").read_bytes()
    run([generator, operation, n, level, directory], success=False)
    assert (directory / "package.json").read_bytes() == before


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generator", required=True, type=Path)
    parser.add_argument("--validator", required=True, type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="instruction-native-") as temporary:
        root = Path(temporary)
        for operation, n, level in (("pmodld", 128, 1), ("pmul", 1024, 4), ("pintt", 8192, 4)):
            check_package(args.generator, args.validator, root / operation, operation, n, level)
        for operation, n, level in (("padd", 256, 1), ("padd", 16384, 1),
                                    ("padd", 128, 0), ("padd", 128, 5), ("bad", 128, 1)):
            destination = root / "rejected"
            run([args.generator, operation, n, level, destination], success=False)
            assert not destination.exists()
        destination = root / "verified-not-published"
        run([args.generator, "pfree", 128, 1, destination, "--verify-only"])
        assert not destination.exists()
    print("03 native package/real RNS/online PMUL/physical-stage/negative CLI checks: PASS")


if __name__ == "__main__":
    main()
