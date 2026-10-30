#!/usr/bin/env python3
"""Optional 08 application delivery; the default 109-case catalog is untouched."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from types import SimpleNamespace

from build import build_case, run, verify_elf
from import_package import import_package, read_json, read_rows, require
from pir_unified_layout import generate, STAGE0_STEM, STAGE1_STEM


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRODUCER_COMMIT = "22c08dcdf08b57fcb6505ff6b7942ffad5f42849"
CASES = {
    "08_01_psi_single": ("psi_single", "bfv_apsi_concentrated_application", 8192, 4),
    "08_02_pir_stage0": ("pir_stage0", "bfv_sealpir_2d_small_stage0_concentrated_000", 4096, 3),
    "08_03_pir_stage1": ("pir_stage1", "bfv_sealpir_2d_small_stage1_concentrated_000", 4096, 3),
}
UNIFIED = "08_04_pir_unified"


def case_spec(case):
    operation, stem, degree, level = CASES[case]
    return {
        "kind": "application", "profile": "application", "case_id": case,
        "source": f"src/08_pir_psi/{case}.c", "operation": operation,
        "program_stem": stem, "scheme": "bfv", "degree": degree, "level": level,
        "memory_base": "0x87000000", "minimum_ram_bytes": 268435456,
        "purpose": f"Trident {operation} fixed input, independent HPU target check",
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
    require(re.fullmatch(r"[0-9a-f]{40}", args.producer_commit) is not None,
            "expected producer commit must be a full lowercase SHA-1")
    args.output = args.output.resolve()
    args.validator = args.validator.resolve()
    if args.case == UNIFIED:
        return build_unified(args)
    require(args.package is not None, "single-stage build requires --package")
    package = args.package.resolve()
    require(package.is_dir() and not package.is_symlink(), "application package directory missing")
    spec = case_spec(args.case)
    require((ROOT / spec["source"]).is_file(), "target C source missing")
    subprocess.run([str(args.validator), str(package)], check=True)
    delivery = args.output / "imported" / args.case
    delivery.parent.mkdir(parents=True, exist_ok=True)
    metadata = import_package(package, delivery, spec, args.producer_commit,
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
        "case_id": args.case, "producer_commit": args.producer_commit,
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


def build_unified(args):
    require(args.stage0_package is not None and args.stage1_package is not None and
            args.cpu_parameters is not None and args.dynamic_input_map is not None,
            "unified build requires both packages, --cpu-parameters and --dynamic-input-map")
    packages = [args.stage0_package.resolve(), args.stage1_package.resolve()]
    parameter_file = args.cpu_parameters.resolve()
    dynamic_map = args.dynamic_input_map.resolve()
    require(parameter_file.is_file() and not parameter_file.is_symlink(),
            "CPU parameter fixture missing")
    require(dynamic_map.is_file() and not dynamic_map.is_symlink(),
            "producer dynamic input map missing")
    delivery = args.output / "imported" / UNIFIED
    delivery.mkdir(parents=True, exist_ok=True)
    metadata = []
    for stage, case, package in zip(("stage0", "stage1"),
                                    ("08_02_pir_stage0", "08_03_pir_stage1"), packages):
        require(package.is_dir() and not package.is_symlink(), "stage package missing")
        subprocess.run([str(args.validator), str(package)], check=True)
        metadata.append(import_package(package, delivery / stage, case_spec(case),
                                       args.producer_commit, verify_existing=args.verify_existing))
    layout = generate(delivery, packages[0], packages[1], metadata[0], metadata[1],
                      parameter_file, dynamic_map,
                      verify_existing=args.verify_existing)
    binary_dir = args.output / "artifact" / "normal" / UNIFIED
    binary_dir.mkdir(parents=True, exist_ok=True)
    binary = binary_dir / UNIFIED
    objects = args.output / "objects" / "normal" / str(args.wait_cycles) / UNIFIED
    run(["make", "-s", "-C", ROOT, "-f", "Makefile.native.case", "image",
         f"AM_HOME={args.am_home.resolve()}", f"ARCH={args.arch}",
         f"CROSS_COMPILE={args.cross}", f"CASE_ID={UNIFIED}",
         f"CASE_SOURCE={ROOT / 'src' / '08_pir_psi' / (UNIFIED + '.c')}",
         f"DATA_DIR={delivery}", f"STAGE0_STEM={STAGE0_STEM}",
         f"STAGE1_STEM={STAGE1_STEM}", "PROGRAM_STEM=pir_unified",
         "LOG_LEVEL=1", f"WAIT_CYCLES={args.wait_cycles}",
         f"CASE_OBJ_DIR={objects}", f"CASE_BINARY={binary}"])
    elf = binary.with_suffix(".elf")
    image = binary.with_suffix(".bin")
    run([args.cross + "strip", "--strip-debug", elf])
    require(elf.is_file() and image.is_file(), "unified ELF/BIN pair missing")
    words = {}
    for stage, meta in zip(("stage0", "stage1"), metadata):
        actual = verify_elf(elf, args.cross, meta)
        expected = [int(word, 2) for word in
                    (delivery / stage / (meta["program_stem"] + ".inst32")).read_text().split()]
        require(actual == expected, f"{stage} ELF HPU machine words/order mismatch")
        words[stage] = {"count": len(actual), "inst32_sha256":
                        sha256(delivery / stage / (meta["program_stem"] + ".inst32")),
                        "dma_count": meta["DMA_COUNT"]}
    symbols = subprocess.check_output([args.cross + "nm", "--defined-only", elf], text=True)
    for name in ("main", "pir_cpu_decompose", "pir_cpu_encode", "irq_rearm",
                 "hpu_run_" + STAGE0_STEM, "hpu_run_" + STAGE1_STEM,
                 "stage0_initial_image", "stage1_initial_image"):
        require(any(line.split()[-1] == name for line in symbols.splitlines()),
                f"unified ELF lacks required symbol {name}")
    receipt = {
        "case_id": UNIFIED, "status": "TARGET_BUILD_AND_STATIC_CHECK_PASS",
        "producer_commit": args.producer_commit,
        "source_package_tree_sha256": {stage: tree_sha256(package) for stage, package in
                                       zip(("stage0", "stage1"), packages)},
        "cpu_parameters_sha256": sha256(parameter_file),
        "dynamic_input_map_sha256": sha256(dynamic_map), "layout": layout,
        "hpu_programs": words, "dma_manifest_validation": "PASS: import_package.validate_dma",
        "load_segments_below_ddr": "PASS: verify_elf for each program",
        "elf": str(elf), "bin": str(image),
        "elf_sha256": sha256(elf), "bin_sha256": sha256(image),
        "elf_bytes": elf.stat().st_size, "bin_bytes": image.stat().st_size,
        "rtl_hardware_execution": "NOT RUN",
    }
    (binary_dir / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True, choices=(*CASES, UNIFIED))
    parser.add_argument("--producer-commit", default=DEFAULT_PRODUCER_COMMIT,
                        help="exact producer revision expected in both package provenances")
    parser.add_argument("--package", type=Path)
    parser.add_argument("--stage0-package", type=Path)
    parser.add_argument("--stage1-package", type=Path)
    parser.add_argument("--cpu-parameters", type=Path)
    parser.add_argument("--dynamic-input-map", type=Path)
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
