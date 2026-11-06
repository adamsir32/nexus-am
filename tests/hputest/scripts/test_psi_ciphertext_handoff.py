#!/usr/bin/env python3
"""Verify model -> target C DDR export -> client SEAL decrypt/recovery."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def run(command, log):
    result = subprocess.run([str(x) for x in command], capture_output=True, text=True)
    log.write_text("COMMAND " + json.dumps([str(x) for x in command]) + "\n" +
                   result.stdout + "\n[stderr]\n" + result.stderr +
                   f"\nRETURN_CODE {result.returncode}\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("example", "delivery", "executed-image", "package", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    root = args.output.resolve()
    if root.exists():
        raise RuntimeError("refusing to overwrite PSI handoff evidence")
    root.mkdir(parents=True)
    image = root / "target-c-output.u32.bin"
    host = run([sys.executable,
        Path(__file__).with_name("test_psi_single_main_integration.py"),
        "--delivery", args.delivery, "--executed-image", args.executed_image,
        "--output-image", image], root / "host.log")
    if host.returncode or not image.is_file():
        raise RuntimeError("target C host program did not export its DDR output")
    command = [args.example, "--profile", "small", "--scenario", "single",
               "--match-mode", "trident", "--client-readback-image", image]
    client = run(command, root / "client.log")
    if client.returncode or "AUDIT_PSI_CLIENT_CIPHERTEXT_PASS" not in client.stderr:
        raise RuntimeError("client did not decrypt target C output")
    package = args.package.resolve(strict=True)
    manifest = json.loads((package / "package.json").read_text())
    with (package / manifest["golden_manifest"]).open(newline="") as stream:
        line = int(next(csv.DictReader(stream))["line_offset"])
    corrupt = root / "target-c-output-corrupt.u32.bin"
    data = bytearray(image.read_bytes())
    data[line * 256] ^= 1
    corrupt.write_bytes(data)
    negative = run(command[:-1] + [corrupt], root / "corrupt.log")
    if negative.returncode == 0 or "PSI C readback" not in negative.stderr:
        raise RuntimeError("corrupt target C ciphertext was accepted")
    summary = {"status": "PASS", "host_rc": host.returncode,
               "client_rc": client.returncode, "corrupt_rc": negative.returncode,
               "source": "HPU encoded instruction software executor via Mock HPU",
               "target_c_ddr_sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
               "client_decrypt": "SEAL secret key and APSI CPU intersection reference",
               "rtl": "NOT RUN", "hardware": "NOT RUN"}
    (root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
