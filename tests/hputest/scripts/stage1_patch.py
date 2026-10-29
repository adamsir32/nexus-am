#!/usr/bin/env python3
"""Prepare physical stage1 plaintext bytes without changing its HPU program."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct

from import_package import read_json, read_rows, require, safe_file


STEM = "bfv_sealpir_2d_small_stage1_concentrated_000"
SCHEMA = "hpu-pir-stage1-physical-input-v1"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def context(package):
    manifest = read_json(package / "package.json")
    require(manifest.get("case_name") == STEM and manifest.get("scheme") == "bfv",
            "not the fixed small PIR stage1 package")
    parameters = read_json(safe_file(package, manifest["parameters"]))
    moduli = parameters["levels"][0]["moduli"]
    image = safe_file(package, manifest["image"]).read_bytes()
    config = read_json(safe_file(package, manifest["memory_config"]))
    require(len(image) == config["used_lines"] * 256, "truncated stage1 source image")
    rows = [row for row in read_rows(safe_file(package, manifest["line_map"]))
            if row["kind"] == "plaintext"]
    require(rows and len({row["allocation_id"] for row in rows}) == len(rows),
            "missing or duplicate stage1 plaintext allocations")
    return manifest, moduli, image, rows


def span(row, moduli, image):
    match = re.search(r"/mod(\d+)$", row["allocation_id"])
    require(match is not None, "plaintext allocation lacks modulus identifier")
    mod_id = int(match.group(1))
    require(0 <= mod_id < len(moduli), "plaintext modulus identifier outside Q chain")
    first, count = int(row["line_offset"]), int(row["line_count"])
    require(count > 0 and int(row["padded_words"]) == count * 64 and
            int(row["payload_words"]) == count * 64 and
            (first + count) * 256 <= len(image), "plaintext physical span malformed")
    return first * 256, count * 256, moduli[mod_id]


def snapshot(package, directory):
    manifest, moduli, image, rows = context(package)
    require(not directory.exists(), "snapshot destination already exists")
    directory.mkdir(parents=True)
    entries = []
    for index, row in enumerate(rows):
        offset, size, modulus = span(row, moduli, image)
        data = image[offset:offset + size]
        require(all(value < modulus for value, in struct.iter_unpack("<I", data)),
                "noncanonical source plaintext")
        name = f"input_{index:03d}.u32.bin"
        (directory / name).write_bytes(data)
        entries.append({"allocation_id": row["allocation_id"], "path": name,
                        "sha256": sha256(data)})
    result = {"schema": SCHEMA, "source_package_sha256": sha256((package / "package.json").read_bytes()),
              "encoding": "native_physical_u32_le", "inputs": entries}
    (directory / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def apply(package, patch_dir, output):
    manifest, moduli, source_image, rows = context(package)
    patch = read_json(patch_dir / "manifest.json")
    require(patch.get("schema") == SCHEMA and patch.get("encoding") == "native_physical_u32_le" and
            patch.get("source_package_sha256") == sha256((package / "package.json").read_bytes()),
            "stage1 dynamic input format/source mismatch")
    entries = patch.get("inputs")
    require(isinstance(entries, list) and len(entries) == len(rows) and
            [entry.get("allocation_id") for entry in entries] ==
            [row["allocation_id"] for row in rows], "stage1 dynamic input coverage/order mismatch")
    image = bytearray(source_image)
    for row, entry in zip(rows, entries):
        offset, size, modulus = span(row, moduli, source_image)
        data = safe_file(patch_dir, entry["path"]).read_bytes()
        require(len(data) == size and sha256(data) == entry.get("sha256"),
                "stage1 dynamic input size/checksum mismatch")
        require(all(value < modulus for value, in struct.iter_unpack("<I", data)),
                "noncanonical stage1 dynamic input")
        image[offset:offset + size] = data
    require(not output.exists(), "refusing to overwrite stage1 image")
    output.write_bytes(image)
    return {"source_image_sha256": sha256(source_image),
            "patched_image_sha256": sha256(image), "input_spans": len(rows),
            "program_inst32_sha256": sha256(safe_file(package, manifest["program_inst32"]).read_bytes()),
            "numerical_execution": "NOT RUN"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("snapshot", "apply"))
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = snapshot(args.package, args.directory) if args.action == "snapshot" else apply(
        args.package, args.directory, args.output)
    print(json.dumps(result if args.action == "apply" else
                     {"input_spans": len(result["inputs"]), "schema": result["schema"]}, indent=2))


if __name__ == "__main__":
    main()
