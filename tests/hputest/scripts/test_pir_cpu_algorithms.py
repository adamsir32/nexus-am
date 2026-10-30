#!/usr/bin/env python3
"""Compare target C decompose/encode against same-run SEAL and HPU fixtures."""

import argparse
import csv
import ctypes as C
import hashlib
import json
from pathlib import Path
import subprocess
import struct
import sys

from pir_unified_layout import read_dynamic_input_map


N = 4096
ROOT = Path(__file__).resolve().parents[1]


class OutputLimb(C.Structure):
    _fields_ = [(name, C.c_uint32) for name in
                ("line", "words", "reply", "component", "modulus_id", "modulus")]


class InputLimb(C.Structure):
    _fields_ = [(name, C.c_uint32) for name in
                ("line", "words", "plaintext_index", "modulus_id", "modulus")]


class Parameters(C.Structure):
    _fields_ = [("degree", C.c_uint32), ("plain_modulus", C.c_uint32),
                ("stage0_moduli", C.c_uint32 * 2),
                ("stage1_moduli", C.c_uint32 * 3),
                ("stage1_psi", C.c_uint32 * 3)]


class Encoder(C.Structure):
    _fields_ = [("twiddles", ((C.c_uint32 * 2048) * 12) * 3),
                ("values", C.c_uint32 * N), ("labels", C.c_uint32 * N),
                ("moduli", C.c_uint32 * 3), ("psi", C.c_uint32 * 3),
                ("plain_modulus", C.c_uint32), ("ready", C.c_uint32)]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package(path):
    manifest = json.loads((path / "package.json").read_text())
    line_map = list(csv.DictReader((path / manifest["line_map"]).open(newline="")))
    golden = list(csv.DictReader((path / manifest["golden_manifest"]).open(newline="")))
    config = json.loads((path / manifest["memory_config"]).read_text())
    return manifest, line_map, golden, config


def output_limbs(golden, moduli):
    identities = list(dict.fromkeys(row["object_id"] for row in golden))
    require(len(identities) == 4 and len(golden) == 16,
            "stage0 output objects/limbs changed")
    values = []
    for row in golden:
        reply = identities.index(row["object_id"])
        basis = int(row["modulus_id"])
        require(basis < 2 and int(row["modulus"]) == moduli[basis] and
                row["domain"] == "coefficient_bit_reversed", "stage0 limb ABI")
        values.append(OutputLimb(int(row["line_offset"]), int(row["payload_words"]),
                                 reply, int(row["component"]), basis, int(row["modulus"])))
    return (OutputLimb * len(values))(*values)


def input_limbs(rows, moduli, stage1_image, dynamic_input_map):
    plaintext_rows = [row for row in rows if row["kind"] == "plaintext"]
    values, by_id = [], {}
    for row, rank, basis in read_dynamic_input_map(
            dynamic_input_map, plaintext_rows, stage1_image, moduli):
        plain_index = (rank // 3) // 4 + ((rank // 3) % 4) * 8
        item = InputLimb(int(row["line_offset"]), N, plain_index, basis, moduli[basis])
        values.append(item)
        by_id[row["allocation_id"]] = item
    require(len(values) == 96, "stage1 dynamic physical limb count")
    return (InputLimb * len(values))(*values), by_id


def load_lib(output):
    source = ROOT / "runtime" / "pir"
    library = output / "libpir_cpu_algorithms.so"
    subprocess.run(["gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                    "-fPIC", "-shared", str(source / "pir_cpu_decompose.c"),
                    str(source / "pir_cpu_encode.c"), "-I", str(source),
                    "-o", str(library)], check=True)
    api = C.CDLL(str(library))
    u32 = C.POINTER(C.c_uint32)
    api.pir_cpu_decompose.argtypes = [u32, C.c_uint32, C.POINTER(OutputLimb),
                                       C.c_size_t, C.POINTER(Parameters), u32, C.c_size_t]
    api.pir_cpu_decompose.restype = C.c_int
    api.pir_cpu_encoder_init.argtypes = [C.POINTER(Encoder), C.POINTER(Parameters)]
    api.pir_cpu_encoder_init.restype = C.c_int
    api.pir_cpu_encode.argtypes = [u32, C.c_size_t, u32, C.c_uint32,
                                    C.POINTER(InputLimb), C.c_size_t,
                                    C.POINTER(Parameters), C.POINTER(Encoder)]
    api.pir_cpu_encode.restype = C.c_int
    return api


def run_case(label, fixture, params, api, encoder, stage1_image, stage1_lines,
             limbs, by_id, output):
    stage0_path = (fixture / "stage0-executed.u32.bin" if label == "baseline" else
                   fixture / "replay" / "changed-stage0-executed.u32.bin")
    stage0_package = (fixture / "packages" / "stage0_concentrated_000" if label == "baseline" else
                      fixture / "replay" / "changed-stage0-packages" / "stage0_concentrated_000")
    _, _, golden, config = package(stage0_package)
    outputs = output_limbs(golden, list(params.stage0_moduli))
    stage0_bytes = stage0_path.read_bytes()
    require(len(stage0_bytes) == config["used_lines"] * 256, "actual stage0 DDR length")
    stage0_words = (C.c_uint32 * (len(stage0_bytes) // 4)).from_buffer_copy(stage0_bytes)
    plains = (C.c_uint32 * (32 * N))()
    rc = api.pir_cpu_decompose(stage0_words, config["used_lines"], outputs, 16,
                               C.byref(params), plains, len(plains))
    require(rc == 0, f"{label} CPU decomposition failed: {rc}")
    expected_plain = (fixture / "replay" / "cpu-fixture" /
                      (label + "-plains.u32.bin")).read_bytes()
    require(bytes(plains) == expected_plain,
            f"{label} CPU decomposition differs from C++/SEAL plaintext coefficients")

    patched = bytearray(stage1_image)
    words = (C.c_uint32 * (len(patched) // 4)).from_buffer(patched)
    rc = api.pir_cpu_encode(plains, len(plains), words, stage1_lines,
                            limbs, len(limbs), C.byref(params), C.byref(encoder))
    require(rc == 0, f"{label} CPU physical encoding failed: {rc}")
    dynamic = fixture / "replay" / label / "dynamic"
    mapping = dict(line.split("\t") for line in
                   (dynamic / "dynamic_inputs.tsv").read_text().splitlines())
    require(set(mapping) == set(by_id), "C++ dynamic input binding differs from C binding")
    for allocation, name in mapping.items():
        item = by_id[allocation]
        start = item.line * 256
        require(patched[start:start + N * 4] == (dynamic / name).read_bytes(),
                f"{label} C physical NTT differs from compiler at {allocation}")
    expected_patched = (fixture / "replay" / label / "stage1-patched.u32.bin").read_bytes()
    require(patched == expected_patched,
            f"{label} C encoding changed a fixed/non-input byte")
    path = output / (label + "-stage1-cpu-patched.u32.bin")
    path.write_bytes(patched)
    return path, plains, stage0_words, outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dynamic-input-map", type=Path)
    parser.add_argument("--replay-executable", type=Path,
                        help="encoded HPU model runner; replays target-C patched images")
    args = parser.parse_args()
    require(not args.output.exists(), "refusing to overwrite CPU test output")
    args.output.mkdir(parents=True)
    fixture = args.fixture.resolve()
    parameters = json.loads((fixture / "replay" / "cpu-fixture" /
                             "parameters.json").read_text())
    require(parameters["degree"] == N and parameters["plain_bits"] == 20,
            "CPU fixture profile mismatch")
    params = Parameters(N, parameters["plain_modulus"],
                        (C.c_uint32 * 2)(*parameters["stage0_output_moduli"]),
                        (C.c_uint32 * 3)(*parameters["stage1_input_moduli"]),
                        (C.c_uint32 * 3)(*parameters["stage1_psi"]))
    stage1_package = fixture / "packages" / "stage1_concentrated_000"
    manifest, rows, _, config = package(stage1_package)
    stage1_image = (stage1_package / manifest["image"]).read_bytes()
    require(len(stage1_image) == config["used_lines"] * 256,
            "source stage1 image length mismatch")
    dynamic_map = (args.dynamic_input_map or
                   fixture / "replay/baseline/dynamic/dynamic_inputs.tsv")
    limbs, by_id = input_limbs(rows, list(params.stage1_moduli),
                              stage1_image, dynamic_map)
    api = load_lib(args.output)
    encoder = Encoder()
    require(api.pir_cpu_encoder_init(C.byref(encoder), C.byref(params)) == 0,
            "target C NTT initialization failed")
    baseline, baseline_plains, baseline_words, baseline_outputs = run_case(
        "baseline", fixture, params, api, encoder, stage1_image, config["used_lines"],
        limbs, by_id, args.output)
    changed, changed_plains, _, _ = run_case(
        "changed", fixture, params, api, encoder, stage1_image, config["used_lines"],
        limbs, by_id, args.output)
    require(bytes(baseline_plains) != bytes(changed_plains),
            "two stage0 inputs produced identical CPU decomposition")

    replay = {}
    if args.replay_executable is not None:
        manifest = json.loads((stage1_package / "package.json").read_text())
        dma_rows = list(csv.DictReader((stage1_package /
                                        manifest["dma_relocation_manifest"]).open(newline="")))
        dma_file = args.output / "stage1-dma-spans.u32x2.bin"
        dma_file.write_bytes(b"".join(struct.pack("<II", int(row["line_offset"]),
                                                    int(row["line_count"])) for row in dma_rows))
        for label, patched in (("baseline", baseline), ("changed", changed)):
            command = [str(args.replay_executable.resolve()),
                       str(stage1_package / manifest["program_inst32"]),
                       str(dma_file), str(patched),
                       str(fixture / "replay" / label / "stage1-executed.u32.bin")]
            result = subprocess.run(command, capture_output=True, text=True)
            (args.output / (label + "-encoded-replay.log")).write_text(
                result.stdout + result.stderr)
            require(result.returncode == 0 and "PIR_CPU_ENCODED_REPLAY_PASS" in result.stdout,
                    f"{label} target-C image encoded replay failed: {result.stderr}")
            replay[label] = result.stdout.strip()

    # Rejected before use or before any stage1 DDR mutation.
    bad_outputs = (OutputLimb * 16)(*baseline_outputs)
    bad_outputs[1] = bad_outputs[0]
    aliased_outputs = (OutputLimb * 16)(*baseline_outputs)
    alias_index = next(i for i in range(1, 16)
                       if aliased_outputs[i].modulus_id == aliased_outputs[0].modulus_id)
    aliased_outputs[alias_index].line = aliased_outputs[0].line
    corrupted_stage0 = (C.c_uint32 * len(baseline_words))(*baseline_words)
    corrupted_stage0[baseline_outputs[0].line * 64] = baseline_outputs[0].modulus
    negative = {
        "duplicate-output-limb": api.pir_cpu_decompose(
            baseline_words, len(baseline_words) // 64, bad_outputs, 16,
            C.byref(params), baseline_plains, len(baseline_plains)),
        "overlapping-output-limb": api.pir_cpu_decompose(
            baseline_words, len(baseline_words) // 64, aliased_outputs, 16,
            C.byref(params), baseline_plains, len(baseline_plains)),
        "short-output-window": api.pir_cpu_decompose(
            baseline_words, 1, baseline_outputs, 16,
            C.byref(params), baseline_plains, len(baseline_plains)),
        "noncanonical-stage0-output": api.pir_cpu_decompose(
            corrupted_stage0, len(corrupted_stage0) // 64, baseline_outputs, 16,
            C.byref(params), baseline_plains, len(baseline_plains)),
    }
    invalid_plain = (C.c_uint32 * len(changed_plains))(*changed_plains)
    invalid_plain[0] = params.plain_modulus
    scratch = bytearray(stage1_image)
    scratch_words = (C.c_uint32 * (len(scratch) // 4)).from_buffer(scratch)
    negative["noncanonical-plaintext"] = api.pir_cpu_encode(
        invalid_plain, len(invalid_plain), scratch_words, config["used_lines"],
        limbs, len(limbs), C.byref(params), C.byref(encoder))
    bad_limbs = (InputLimb * 96)(*limbs)
    bad_limbs[1] = bad_limbs[0]
    negative["duplicate-input-limb"] = api.pir_cpu_encode(
        changed_plains, len(changed_plains), scratch_words, config["used_lines"],
        bad_limbs, 96, C.byref(params), C.byref(encoder))
    out_of_bounds = (InputLimb * 96)(*limbs)
    out_of_bounds[0].line = config["used_lines"]
    negative["out-of-window-input-limb"] = api.pir_cpu_encode(
        changed_plains, len(changed_plains), scratch_words, config["used_lines"],
        out_of_bounds, 96, C.byref(params), C.byref(encoder))
    require(all(rc != 0 for rc in negative.values()) and scratch == stage1_image,
            f"target C accepted invalid input or changed DDR on validation failure: {negative}")
    summary = {"status": "PASS", "cpu_decomposition": "32 x 4096 coefficients exact",
               "cpu_encoding": "96 x 4096 words exact", "negative_return_codes": negative,
               "baseline_patched_sha256": sha(baseline),
               "changed_patched_sha256": sha(changed),
               "target_c_encoded_replay": replay,
               "fixture": str(fixture)}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"target PIR CPU algorithms: FAIL: {error}", file=sys.stderr)
        raise
