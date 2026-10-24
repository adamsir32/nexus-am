#!/usr/bin/env python3
"""检查真实PSYNC sidecar的三个不同prefix、原包绑定及未写分量覆盖。"""
import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from performance_adapter import instruction_words, resolved_spans, validate_fixed_entry


def read_rows(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def verify(package, previous=None):
    descriptor = json.loads((package / "package.json").read_text())
    parameters = json.loads((package / descriptor["parameters"]).read_text())
    provenance = json.loads((package / "provenance/build.json").read_text())
    sidecar = package.with_name(package.name + ".psync-prefixes")
    manifest = json.loads((sidecar / "manifest.json").read_text())
    assert manifest["schema"] == "hpu-psync-prefixes" and manifest["schema_version"] == 1
    assert manifest["producer_commit"] == provenance["commit"]
    assert manifest["base_program_stem"] == descriptor["case_name"]
    assert manifest["degree"] == parameters["poly_modulus_degree"]
    assert manifest["level"] == parameters["input_rns_components"]
    assert manifest["initial_output_poison"] == 0xffffffff
    assert manifest["source_format"] == "upstream_fixed_entry_only"
    assert manifest["hardware_verified"] is False
    assert all(manifest[key] is True for key in ("verified", "model_verified", "read_only_guard_verified"))
    base_dma = read_rows(package / descriptor["dma_relocation_manifest"])
    allocations = {row["allocation_id"]: row for row in read_rows(package / descriptor["memory_manifest"])}
    used = json.loads((package / descriptor["memory_config"]).read_text())["used_lines"]
    level, degree = manifest["level"], manifest["degree"]
    prefixes = manifest["prefixes"]
    assert [row["name"] for row in prefixes] == ["idle", "dma", "compute"]
    files = {"manifest.json"}
    verified = []
    for row in prefixes:
        name = row["name"]
        stem = descriptor["case_name"] + "_" + name
        assert row["entry"] == "hpu_run_" + stem
        expected_components = {"idle": [], "dma": [0], "compute": [1]}[name]
        assert row["expected_components"] == expected_components
        for field, extension in (("asm_file", ".asm"), ("source_file", ".c"),
                                 ("header_file", ".h"), ("words_file", ".inst32")):
            assert row[field] == stem + extension
            files.add(row[field])
        words = [int(value, 2) for value in (sidecar / row["words_file"]).read_text().split()]
        assembly = (sidecar / row["asm_file"]).read_text().splitlines()
        assert len(words) == len(assembly) == row["instruction_count"]
        assert words[-1] == 0x7000005b and words.count(0x7000005b) == 1
        assert assembly[-1] == "psync" and assembly.count("psync") == 1
        assert row["compared_output_words"] == degree * level * len(expected_components)
        assert row["unchanged_words"] == used * 64 - row["compared_output_words"]
        assert all(row[key] is True for key in ("verified", "model_verified", "read_only_guard_verified"))
        if name == "idle":
            assert assembly == ["psync"]
            expected_dma = []
        elif name == "dma":
            expected_dma = [item for index, item in enumerate(base_dma)
                            if index > 0 and (index - 1) % 5 < 2]
            assert assembly == [line for _ in range(level) for line in
                                ("dload x10, x11, p0, 0, 0, 0", "dstore x10, x11, p0, 1, 0")] + ["psync"]
        else:
            expected_dma = [item for index, item in enumerate(base_dma)
                            if index == 0 or (index - 1) % 5 >= 2]
            expected_asm = ["dload x10, x11, p63, 1, 0, 32"]
            for q in range(level):
                expected_asm += [f"pmodld {q}", "dload x10, x11, p0, 0, 0, 0",
                                 "dload x10, x11, p1, 0, 0, 0", "pmul p2, p0, p1",
                                 "dstore x10, x11, p2, 1, 0", "pfree p0", "pfree p1"]
            assert assembly == expected_asm + ["pfree p63", "psync"]
        spans = row["dma_spans"]
        assert len(spans) == len(expected_dma)
        assert [item["instruction_index"] for item in spans] == [
            index for index, word in enumerate(words) if word & 127 == 0x2b]
        for item, original in zip(spans, expected_dma):
            assert (item["allocation_id"], item["line_offset"], item["line_count"]) == (
                original["allocation_id"], int(original["line_offset"]), int(original["line_count"]))
            allocation = allocations[item["allocation_id"]]
            assert int(allocation["line_offset"]) <= item["line_offset"]
            assert item["line_offset"] + item["line_count"] <= (
                int(allocation["line_offset"]) + int(allocation["line_count"]))
        source = (sidecar / row["source_file"]).read_text()
        fixed_spans = [(item["line_offset"], item["line_count"]) for item in spans]
        assert instruction_words(source) == words and resolved_spans(source) == fixed_spans
        validate_fixed_entry(source, stem, words, fixed_spans)
        assert "int " + row["entry"] + "(void);" in (sidecar / row["header_file"]).read_text()
        verified.append(dict(name=name, instruction_count=len(words), dma_count=len(spans),
                             expected_components=expected_components,
                             compared_output_words=row["compared_output_words"],
                             unchanged_words=row["unchanged_words"]))
    assert {path.name for path in sidecar.iterdir()} == files
    assert all(path.is_file() and not path.is_symlink() for path in sidecar.iterdir())
    if previous:
        old = {path.relative_to(previous) for path in previous.rglob("*") if path.is_file()}
        new = {path.relative_to(package) for path in package.rglob("*") if path.is_file()}
        assert old == new
        assert all((previous / path).read_bytes() == (package / path).read_bytes() for path in old)
    return dict(base_package=str(package), sidecar=str(sidecar), prefixes=verified,
                base_package_byte_identical=previous is not None, hardware_verified=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = verify(args.package, args.previous)
    if args.report:
        args.report.write_text(json.dumps(result, indent=2) + "\n")
    print("PSYNC idle/DMA/compute distinct native prefixes, fixed C, bindings and base preservation: PASS")
