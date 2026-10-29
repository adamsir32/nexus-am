#!/usr/bin/env python3
"""Reject corrupt application deliveries and malformed stage1 physical inputs."""
import argparse
import csv
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from import_package import read_json
from stage1_patch import apply, snapshot


def mutate_package(copy, key, operation):
    package = read_json(copy / "package.json")
    target = copy / package[key]
    operation(target)


def change_json(target, field, value):
    data = read_json(target)
    data[field] = value
    target.write_text(json.dumps(data))


def bad_dma(target):
    with target.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    rows[0]["line_count"] = "99999999"
    with target.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def corrupt_first_golden(package, manifest_path):
    with manifest_path.open(newline="") as stream:
        row = next(csv.DictReader(stream))
    target = package / row["path"]
    data = bytearray(target.read_bytes())
    data[0] ^= 1
    target.write_bytes(data)


def corruption_cases():
    return {
        "missing_file": lambda p: mutate_package(p, "program_header", lambda x: x.unlink()),
        "abi_mismatch": lambda p: mutate_package(p, "memory_abi",
            lambda x: change_json(x, "instruction_isa", "invalid-isa")),
        "instruction_mismatch": lambda p: mutate_package(p, "program_inst32",
            lambda x: x.write_text("0" * 32 + "\n" + x.read_text())),
        "dma_manifest_error": lambda p: mutate_package(p, "dma_relocation_manifest", bad_dma),
        "window_too_small": lambda p: mutate_package(p, "memory_config",
            lambda x: change_json(x, "capacity_lines", read_json(x)["used_lines"] - 1)),
        "golden_corrupt": lambda p: mutate_package(p, "golden_manifest",
            lambda x: corrupt_first_golden(p, x)),
        "image_truncated": lambda p: mutate_package(p, "image",
            lambda x: x.write_bytes(x.read_bytes()[:-4])),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--psi-package", type=Path, required=True)
    parser.add_argument("--stage1-package", type=Path, required=True)
    parser.add_argument("--validator", type=Path, required=True)
    args = parser.parse_args()
    results = {}
    with tempfile.TemporaryDirectory(prefix="nexus-pir-psi-negative-") as temp:
        root = Path(temp)
        for name, change in corruption_cases().items():
            case = root / name
            shutil.copytree(args.psi_package, case)
            change(case)
            proc = subprocess.run([str(args.validator.resolve()), str(case)],
                                  text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            results[name] = {"status": "PASS" if proc.returncode != 0 else "FAIL",
                             "returncode": proc.returncode,
                             "message": proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""}
        patch = root / "stage1_snapshot"
        snapshot(args.stage1_package, patch)
        metadata = read_json(patch / "manifest.json")
        metadata["inputs"].pop()
        (patch / "manifest.json").write_text(json.dumps(metadata))
        try:
            apply(args.stage1_package, patch, root / "rejected-image.bin")
        except ValueError as error:
            results["dynamic_input_format_error"] = {"status": "PASS", "message": str(error)}
        else:
            results["dynamic_input_format_error"] = {"status": "FAIL"}
    print(json.dumps(results, indent=2))
    raise SystemExit(0 if all(item["status"] == "PASS" for item in results.values()) else 1)


if __name__ == "__main__":
    main()
