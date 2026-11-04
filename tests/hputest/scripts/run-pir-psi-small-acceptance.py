#!/usr/bin/env python3
"""Rebuild and verify both Small applications and four Nexus-AM target images."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CASES = ("08_01_psi_single", "08_02_pir_stage0",
         "08_03_pir_stage1", "08_04_pir_unified")
SCENARIOS = {"empty": 0, "single": 1, "multi": 2, "boundary": 2}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_release_tool(producer):
    path = producer / "tools/verified_pir_psi_delivery.py"
    spec = importlib.util.spec_from_file_location("verified_pir_psi_delivery", path)
    require(spec is not None and spec.loader is not None, "release guard missing")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(summary, name, command, *, cwd=None, timeout=1800):
    log = Path(summary["output"]) / "logs" / (name + ".log")
    started = time.monotonic()
    with log.open("w", encoding="utf-8") as out:
        out.write("COMMAND " + json.dumps([str(x) for x in command]) + "\n")
        out.flush()
        try:
            result = subprocess.run([str(x) for x in command], cwd=cwd,
                                    env=summary["environment"], stdout=out,
                                    stderr=subprocess.STDOUT, timeout=timeout,
                                    check=False)
            rc = result.returncode
        except subprocess.TimeoutExpired:
            rc = "TIMEOUT"
    row = {"name": name, "command": [str(x) for x in command],
           "cwd": str(cwd) if cwd else None, "returncode": rc,
           "seconds": round(time.monotonic() - started, 3),
           "log": str(log.relative_to(summary["output"]))}
    summary["steps"].append(row)
    require(rc == 0, f"{name} failed ({rc}); see {log}")


def expect_failure(summary, name, command, fragment, *, timeout=30):
    log = Path(summary["output"]) / "logs" / (name + ".log")
    started = time.monotonic()
    with log.open("w", encoding="utf-8") as out:
        try:
            result = subprocess.run([str(x) for x in command],
                                    env=summary["environment"], stdout=out,
                                    stderr=subprocess.STDOUT, timeout=timeout,
                                    check=False)
            rc = result.returncode
        except subprocess.TimeoutExpired:
            rc = "TIMEOUT"
    summary["steps"].append({"name": name, "command": [str(x) for x in command],
                             "returncode": rc,
                             "seconds": round(time.monotonic() - started, 3),
                             "log": str(log.relative_to(summary["output"])),
                             "expected": "rejection"})
    require(rc != 0, f"{name} unexpectedly accepted malformed input")
    require(fragment in log.read_text(encoding="utf-8", errors="replace"),
            f"{name} rejected without the expected diagnostic: {fragment}")


def expect_timeout(summary, name, command):
    log = Path(summary["output"]) / "logs" / (name + ".log")
    started = time.monotonic()
    with log.open("w", encoding="utf-8") as out:
        try:
            result = subprocess.run([str(x) for x in command],
                                    env=summary["environment"], stdout=out,
                                    stderr=subprocess.STDOUT, timeout=0.001,
                                    check=False)
            rc = result.returncode
        except subprocess.TimeoutExpired:
            rc = "TIMEOUT"
    summary["steps"].append({"name": name, "command": [str(x) for x in command],
                             "returncode": rc, "expected": "TIMEOUT",
                             "seconds": round(time.monotonic() - started, 3),
                             "log": str(log.relative_to(summary["output"]))})
    require(rc == "TIMEOUT", f"{name} did not enforce its execution time limit")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def inspect_psi(summary, root, scenario):
    manifest = read_json(root / "pipeline_manifest.json")
    data = read_json(root / "set_test_data.json")
    for key in ("seal_oracle_per_node_verified", "hpu_software_executor_verified",
                "host_instruction_model_verified", "intersection_match",
                "apsi_reference_match"):
        require(manifest.get(key) is True, f"PSI {scenario} {key} failed")
    require(manifest.get("profile") == "small" and manifest.get("scenario") == scenario,
            f"PSI {scenario} profile mismatch")
    require(manifest.get("poly_modulus_degree") == 8192,
            f"PSI {scenario} degree changed")
    require(manifest.get("sender_size") == 10 and manifest.get("receiver_size") == 5,
            f"PSI {scenario} set size changed")
    require(len(data["recovered_intersection"]) == SCENARIOS[scenario],
            f"PSI {scenario} unexpected intersection count")
    require(data["recovered_intersection"] == data["apsi_reference_matches"],
            f"PSI {scenario} CPU reference mismatch")
    summary["psi_scenarios"][scenario] = {
        "sender": data["sender"], "receiver": data["receiver"],
        "expected_raw": data["expected_intersection"],
        "apsi_reference": data["apsi_reference_matches"],
        "recovered": data["recovered_intersection"],
        "instructions": manifest["encoded_instructions"],
        "dma": manifest["dma_spans"],
        "seal_oracle": "PASS", "hpu_software": "PASS",
        "instruction_model": "PASS", "hardware": "NOT RUN"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--producer-root", required=True, type=Path)
    parser.add_argument("--nexus-root", required=True, type=Path)
    parser.add_argument("--producer-commit", required=True)
    parser.add_argument("--nexus-commit", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--prefix", required=True, type=Path)
    parser.add_argument("--am-home", required=True, type=Path)
    parser.add_argument("--cross", default="/opt/riscv/bin/riscv64-unknown-elf-")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--cmake-arg", action="append", default=[])
    args = parser.parse_args()

    producer = args.producer_root.resolve(strict=True)
    nexus = args.nexus_root.resolve(strict=True)
    output = args.output.absolute()
    require(ROOT == nexus / "tests/hputest", "runner belongs to another Nexus-AM checkout")
    require(re.fullmatch(r"[0-9a-f]{40}", args.nexus_commit) is not None,
            "Nexus-AM commit must be a full lowercase SHA-1")
    require(not output.exists() and not output.is_symlink(),
            "acceptance output must be a new directory")
    require(producer not in output.parents and nexus not in output.parents,
            "acceptance output must be outside both source checkouts")
    require(args.jobs > 0, "jobs must be positive")
    release = load_release_tool(producer)
    release.clean_revision(producer, args.producer_commit)
    require(subprocess.check_output(["git", "-C", str(nexus), "rev-parse", "HEAD"],
                                    text=True).strip() == args.nexus_commit,
            "Nexus-AM HEAD differs from the requested commit")
    require(not subprocess.check_output(["git", "-C", str(nexus), "status",
                                         "--porcelain=v1", "--untracked-files=normal"],
                                        text=True).strip(), "Nexus-AM source tree is dirty")
    prefix = args.prefix.resolve(strict=True)
    am_home = args.am_home.resolve(strict=True)
    output.mkdir(parents=True)
    (output / "logs").mkdir()
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["HPU_DELIVERY_COMMIT"] = args.producer_commit
    environment["HPU_DELIVERY_WORKTREE_STATE"] = "clean-at-configure"
    summary = {"schema": "pir-psi-small-acceptance-v1", "status": "RUNNING",
               "producer_commit": args.producer_commit, "nexus_commit": args.nexus_commit,
               "output": str(output), "environment": environment,
               "parameters": {"pir_degree": 4096, "psi_degree": 8192,
                              "psi_sender": 10, "psi_receiver": 5},
               "steps": [], "psi_scenarios": {}, "packages": [], "targets": {}}
    build = output / "build"
    pir = output / "pir"
    psi = output / "psi"
    targets = output / "targets"
    psi.mkdir()
    try:
        cmake = ["cmake", "-S", producer, "-B", build,
                 "-DCMAKE_BUILD_TYPE=Release", "-DBUILD_TESTING=ON",
                 "-DHPU_ENABLE_SEAL_INTEGRATION=ON", "-DHPU_ENABLE_TRIDENT_PSI=ON",
                 f"-DHPU_SEAL_SOURCE_DIR={producer / 'third_party/modified-SEAL'}",
                 f"-DHPU_TEST_CONFIG={producer / 'config/fhe_test.conf'}",
                 f"-DCMAKE_PREFIX_PATH={prefix}", *args.cmake_arg]
        run(summary, "configure", cmake)
        run(summary, "build", ["cmake", "--build", build, "-j", str(args.jobs)])
        pir_example = build / "hpu_bfv_sealpir_2d_concentrated_example"
        psi_example = build / "hpu_bfv_apsi_concentrated_example"
        validator = build / "hpu_validate_package"
        replay = build / "pir_cpu_encoded_replay"
        for executable in (pir_example, psi_example):
            release.configured_binary(build, producer, executable, args.producer_commit)
        run(summary, "producer_related_ctest", ["ctest", "--test-dir", build,
            "--output-on-failure", "-R",
            "hpu_bfv_sealpir_2d_concentrated_small_record_(0|8|9|64|127)$|"
            "bfv_sealpir_2d_concentrated_small_delivery_test$|"
            "hpu_bfv_sealpir_stage0_readback_adapter$|"
            "hpu_bfv_apsi_concentrated_small_(empty|single|multi|boundary)$|"
            "bfv_apsi_concentrated_small_delivery_test$|"
            "hpu_bfv_apsi_trident_small_(multi|truncation|cross_felt)$|"
            "hpu_bfv_apsi_trident_native_cross_felt$|"
            "hpu_bfv_apsi_trident_duplicate_input$|"
            "hpu_bfv_apsi_senderdb_driver_failures$|"
            "bfv_sealpir_2d_concentrated_seed_manifest_test$|"
            "pir_physical_binding_test$|verified_pir_psi_delivery_guard_test$|"
            "^application_package_test$"])
        require("0 tests failed out of 22" in
                (output / "logs/producer_related_ctest.log").read_text(),
                "producer related CTest selection differs from 22 expected tests")
        run(summary, "pir_dynamic", [sys.executable,
            producer / "test/pir_dynamic_stage_handoff_test.py", "--example", pir_example,
            "--stage1-patch-script", nexus / "tests/hputest/scripts/stage1_patch.py",
            "--output", pir])
        manifest_pir = read_json(pir / "packages/pipeline_manifest.json")
        require(manifest_pir.get("poly_modulus_degree") == 4096 and
                manifest_pir.get("semantic_record_match") is True,
                "PIR Small parameters or record result changed")
        for scenario in SCENARIOS:
            destination = psi / scenario
            command = [sys.executable, producer / "test/apsi_concentrated_delivery_test.py",
                       "--example", psi_example, "--validator", validator,
                       "--output", destination, "--profile", "small",
                       "--scenario", scenario]
            if scenario == "single":
                command.extend(("--executed-image", psi / "single-executed.u32.bin"))
            run(summary, "psi_" + scenario, command)
            inspect_psi(summary, destination, scenario)
        for name, root in (("pir", pir), *((scenario, psi / scenario)
                                               for scenario in SCENARIOS)):
            packages = release.validate_packages(root, validator, args.producer_commit)
            require(packages, f"{name} produced no verified packages")
            for item in packages:
                package = root / item["package"]
                summary["packages"].append({"case": name,
                    "path": str(package.relative_to(output)),
                    "bytes": sum(p.stat().st_size for p in package.rglob("*") if p.is_file()),
                    **item})
        stage0 = pir / "packages/stage0_concentrated_000"
        stage1 = pir / "packages/stage1_concentrated_000"
        psi_single = psi / "single/hpu_query"
        common = [sys.executable, nexus / "tests/hputest/scripts/build-pir-psi.py",
                  "--producer-commit", args.producer_commit,
                  "--package-validator", validator, "--output", targets,
                  "--am-home", am_home, "--cross", args.cross]
        for case, package in ((CASES[0], psi_single), (CASES[1], stage0),
                              (CASES[2], stage1)):
            run(summary, "build_" + case,
                common + ["--case", case, "--package", package])
        cpu_parameters = pir / "replay/cpu-fixture/parameters.json"
        dynamic_map = pir / "replay/baseline/dynamic/dynamic_inputs.tsv"
        run(summary, "build_" + CASES[3], common + ["--case", CASES[3],
            "--stage0-package", stage0, "--stage1-package", stage1,
            "--cpu-parameters", cpu_parameters, "--dynamic-input-map", dynamic_map])
        run(summary, "pir_cpu_encoded", [sys.executable,
            nexus / "tests/hputest/scripts/test_pir_cpu_algorithms.py",
            "--fixture", pir, "--output", output / "pir-cpu",
            "--dynamic-input-map", dynamic_map, "--replay-executable", replay])
        run(summary, "pir_target_main_host", [sys.executable,
            nexus / "tests/hputest/scripts/test_pir_unified_main_integration.py",
            "--delivery", targets / "imported/08_04_pir_unified", "--fixture", pir])
        run(summary, "psi_target_main_host", [sys.executable,
            nexus / "tests/hputest/scripts/test_psi_single_main_integration.py",
            "--delivery", targets / "imported/08_01_psi_single",
            "--executed-image", psi / "single-executed.u32.bin"])
        run(summary, "package_and_dynamic_negatives", [sys.executable,
            nexus / "tests/hputest/scripts/test-pir-psi-negative.py",
            "--psi-package", psi_single, "--stage1-package", stage1,
            "--validator", validator])
        expect_failure(summary, "pir_bad_query", [pir_example, "--profile", "small",
            "--record-index", "128"], "--record-index is outside")
        expect_failure(summary, "pir_bad_database_seed", [pir_example,
            "--profile", "small", "--record-index", "8",
            "--test-database-seed", "123x"], "has an invalid integer value")
        expect_failure(summary, "psi_bad_scenario", [psi_example,
            "--profile", "small", "--scenario", "invalid"], "small --scenario")
        expect_timeout(summary, "pir_execution_timeout",
                       [pir_example, "--profile", "small", "--record-index", "8"])
        expect_timeout(summary, "psi_execution_timeout",
                       [psi_example, "--profile", "small", "--scenario", "single"])
        for case in CASES:
            receipt = read_json(targets / "artifact/normal" / case / "receipt.json")
            require(receipt["producer_commit"] == args.producer_commit,
                    f"{case} producer commit mismatch")
            for kind in ("elf", "bin"):
                path = Path(receipt[kind])
                require(path.is_file() and sha256(path) == receipt[kind + "_sha256"],
                        f"{case} {kind} hash mismatch")
            summary["targets"][case] = {"elf": receipt["elf"],
                "elf_sha256": receipt["elf_sha256"], "bin": receipt["bin"],
                "bin_sha256": receipt["bin_sha256"], "hardware": "NOT RUN"}
        release.clean_revision(producer, args.producer_commit)
        require(not subprocess.check_output(["git", "-C", str(nexus), "status",
             "--porcelain=v1", "--untracked-files=normal"], text=True).strip(),
             "Nexus-AM source tree changed during acceptance")
        summary["status"] = "PASS"
    except Exception as error:
        summary["status"] = "FAIL"
        summary["error"] = str(error)
        raise
    finally:
        summary.pop("environment")
        (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n",
                                              encoding="utf-8")
    print("PIR_PSI_SMALL_ACCEPTANCE_PASS", output)


if __name__ == "__main__":
    main()
