#!/usr/bin/env python3
"""Optional 08 application delivery; the default 109-case catalog is untouched."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

from build import build_case
from import_package import import_package, read_json, read_rows, require


ROOT = Path(__file__).resolve().parents[1]
PRODUCER_COMMIT = "22c08dcdf08b57fcb6505ff6b7942ffad5f42849"
CASES = {
    "08_01_psi_single": ("psi_single", "bfv_apsi_concentrated_application", 8192, 4),
    "08_02_pir_stage0": ("pir_stage0", "bfv_sealpir_2d_small_stage0_concentrated_000", 4096, 3),
    "08_03_pir_stage1": ("pir_stage1", "bfv_sealpir_2d_small_stage1_concentrated_000", 4096, 3),
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_sha256(directory):
    digest = hashlib.sha256()
    for path in sorted(directory.rglob("*")):
        require(not path.is_symlink(), "package tree contains a symlink")
        if path.is_file():
            digest.update(path.relative_to(directory).as_posix().encode() + b"\0")
            digest.update(bytes.fromhex(sha256(path)))
    return digest.hexdigest()


def build(args):
    args.output = args.output.resolve()
    args.validator = args.validator.resolve()
    operation, stem, degree, level = CASES[args.case]
    package = args.package.resolve()
    require(package.is_dir() and not package.is_symlink(), "application package directory missing")
    spec = {
        "kind": "application", "profile": "application", "case_id": args.case,
        "source": f"src/08_pir_psi/{args.case}.c", "operation": operation,
        "program_stem": stem, "scheme": "bfv", "degree": degree, "level": level,
        "memory_base": "0x87000000", "minimum_ram_bytes": 268435456,
        "purpose": f"Trident {operation} fixed input, independent HPU target check",
    }
    require((ROOT / spec["source"]).is_file(), "target C source missing")
    subprocess.run([str(args.validator), str(package)], check=True)
    delivery = args.output / "imported" / args.case
    delivery.parent.mkdir(parents=True, exist_ok=True)
    metadata = import_package(package, delivery, spec, PRODUCER_COMMIT,
                              verify_existing=args.verify_existing)
    target = SimpleNamespace(output=args.output, am_home=args.am_home.resolve(),
                             arch=args.arch, cross=args.cross, wait_cycles=args.wait_cycles)
    result = build_case(target, spec, delivery, metadata, "normal")
    elf = args.output / "artifact" / "normal" / args.case / (args.case + ".elf")
    binary = elf.with_suffix(".bin")
    require(elf.is_file() and binary.is_file(), "target ELF/BIN pair missing")
    manifest = read_json(package / "package.json")
    allocations = read_rows(package / manifest["line_map"])
    compiler_version = subprocess.check_output([args.cross + "gcc", "--version"], text=True).splitlines()[0]
    receipt = {
        "case_id": args.case, "producer_commit": PRODUCER_COMMIT,
        "nexus_am_base_commit": "631f9970003b27ca82eb13549c830c02bea78215",
        "package": str(package), "source_package_tree_sha256": tree_sha256(package),
        "source_package_json_sha256": sha256(package / "package.json"),
        "source_image_sha256": sha256(package / manifest["image"]),
        "source_line_map": str(package / manifest["line_map"]),
        "input_object_count": sum(row["kind"] in ("ciphertext", "plaintext") for row in allocations),
        "compiler_version": compiler_version,
        "imported_image_sha256": sha256(delivery / "image.u32.bin"),
        "imported_golden_sha256": sha256(delivery / "golden.u32.bin"),
        "elf_sha256": sha256(elf), "bin_sha256": sha256(binary),
        "elf": str(elf), "bin": str(binary),
        "instruction_count": metadata["INSTRUCTION_COUNT"], "dma_count": metadata["DMA_COUNT"],
        "window_lines": metadata["WINDOW_LINES"], "output_count": metadata["OUTPUT_COUNT"],
        "elf_instruction_words_verified": result["elf_instruction_words_verified"],
        "rtl_hardware_execution": "NOT RUN",
    }
    report = args.output / "artifact" / "normal" / args.case / "receipt.json"
    report.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True, choices=CASES)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--package-validator", dest="validator", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--am-home", default=ROOT.parents[1], type=Path)
    parser.add_argument("--arch", default="riscv64-xs")
    parser.add_argument("--cross", default="riscv64-linux-gnu-")
    parser.add_argument("--wait-cycles", default=25000000, type=int)
    parser.add_argument("--verify-existing", action="store_true")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
