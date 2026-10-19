#!/usr/bin/env python3
"""接收多规模交付；复用上游编码器和数据，不改变既有N4096导入路径。"""
import argparse
import csv
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess

from hpu_ntt_layout import bit_reverse, stage_reference
from program_adaptation import add_dma_trace

N = 65536
POLY_LINES = N // 64
GUARD_LINES = 64


def rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def u32(blob):
    return list(struct.unpack(f"<{len(blob)//4}I", blob))


def packed(words):
    return struct.pack(f"<{len(words)}I", *words)


def physical64(path):
    blob = path.read_bytes()
    words = struct.unpack(f"<{len(blob)//8}Q", blob)
    require(len(words) % N == 0 and all(x <= 0xffffffff for x in words), "golden width")
    order = [bit_reverse(i, N) for i in range(N)]
    return [words[base+i] for base in range(0, len(words), N) for i in order]


def emit(root, stem, assembly, image, bindings, outputs, metadata, renderer, model):
    """outputs: (line, words, q, component, modulus_id)，所有golden独立于指令复放。"""
    destination = root / stem
    require(not destination.exists(), f"refuse to overwrite existing delivery: {destination}")
    destination.mkdir(parents=True)
    asm = destination / f"{stem}.asm"
    asm.write_text(assembly)
    used = len(image)//256
    subprocess.run([str(renderer), str(asm), stem, str(used), str(destination)], check=True)
    dma = rows(destination / "dma_relocation_manifest.csv")
    require(len(dma) == len(bindings), f"{stem}: DMA binding count")
    writable, first_access = set(), {}
    for entry, (line, count) in zip(dma, bindings):
        require(0 <= line < used and 0 < count <= used-line, "DMA exceeds window")
        entry.update(line_offset=str(line), line_count=str(count))
        for at in range(line, line+count):
            first_access.setdefault(at, entry["direction"])
        if entry["direction"] == "dstore":
            writable.update(range(line, line+count))
    # 只毒化写入前不会读取的行，不能破坏原位运算的输入。
    for at, direction in first_access.items():
        if direction == "dstore":
            image[at*256:(at+1)*256] = b"\xff"*256
    image += packed([0xA5A55A5A]*64*GUARD_LINES)
    mask = bytes(int(i in writable) for i in range(used+GUARD_LINES))
    golden, declarations, model_rows = bytearray(), [], []
    for index, (line, words, modulus, component, modulus_id) in enumerate(outputs):
        require(len(words) == N and all(0 <= v < modulus for v in words), "golden shape/canonical")
        require(all(i in writable for i in range(line, line+POLY_LINES)), "golden not written")
        offset = len(golden)//4
        blob = packed(words)
        golden.extend(blob)
        declarations.append((line, POLY_LINES, N, offset, modulus, 0, component, modulus_id))
        name = f"model-{index}.u32.bin"
        (destination/name).write_bytes(blob)
        model_rows.append(dict(object_id=f"result_{index}", path=name, line_offset=line))
    for name, blob in (("application_window.u32.bin", image),
                       ("application_golden.u32.bin", golden),
                       ("application_writable.u8.bin", mask)):
        (destination/name).write_bytes(blob)
    with (destination/"dma_relocation_manifest.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(dma[0]))
        writer.writeheader(); writer.writerows(dma)
    header = destination/f"{stem}.h"
    header.write_text(header.read_text()+f"\nint hpu_run_{stem}(void);\n")
    code = (destination/f"{stem}.c").read_text()
    code = add_dma_trace(code, dma)
    spans = ",\n".join(f"    {{UINT32_C({line}), UINT32_C({count})}}" for line, count in bindings)
    code = '#include <hpu/trace.h>\n'+code+f"\nint hpu_run_{stem}(void) {{\n"+f"    static const hpu_dma_span_t spans[] = {{\n{spans}\n    }};\n"+f"    return hpu_program_{stem}(spans, sizeof(spans)/sizeof(spans[0]));\n}}\n"
    (destination/f"{stem}.c").write_text(code)
    instructions = len((destination/f"{stem}.inst32").read_text().split())
    fields = "unsigned line, lines, padded_words, golden_word, modulus, step, component, modulus_id;"
    (destination/"application_layout.h").write_text(
        "#ifndef HPU_APPLICATION_LAYOUT_H\n#define HPU_APPLICATION_LAYOUT_H\n"+
        f"enum {{ HPU_APPLICATION_IMAGE_LINES={used}, HPU_APPLICATION_CAPACITY_LINES={used},\n"+
        f"HPU_APPLICATION_LINES={used+GUARD_LINES}, HPU_APPLICATION_GUARD_LINES={GUARD_LINES},\n"+
        f"HPU_APPLICATION_GOLDEN_COUNT={len(outputs)}, HPU_APPLICATION_GOLDEN_WORDS={len(golden)//4},\n"+
        f"HPU_APPLICATION_INSTRUCTION_COUNT={instructions}, HPU_APPLICATION_DMA_COUNT={len(dma)} }};\n"+
        f"struct hpu_application_output {{ {fields} }};\n"+
        "static const struct hpu_application_output hpu_application_outputs[] = {\n"+
        "\n".join("    {"+", ".join(f"{v}U" for v in entry)+"}," for entry in declarations)+"\n};\n#endif\n")
    with (destination/"model_golden.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(model_rows[0]))
        writer.writeheader(); writer.writerows(model_rows)
    result_path = destination/"model_result.u32.bin"
    with (destination/"PROGRAM_MODEL.log").open("w") as log:
        subprocess.run([str(model), str(asm), str(destination/"application_window.u32.bin"),
                        str(destination/"dma_relocation_manifest.csv"), str(destination/"model_golden.csv"),
                        str(destination), str(result_path)], stdout=log, stderr=log, check=True)
    actual = result_path.read_bytes()
    require(len(actual) == len(image), "model image size")
    require(all(actual[i*256:(i+1)*256] == image[i*256:(i+1)*256]
                for i, mutable in enumerate(mask) if not mutable), "model modified readonly/guard")
    result_path.unlink()
    for entry in model_rows:
        (destination/entry["path"]).unlink()
    (destination/"model_golden.csv").unlink()
    metadata.update(degree=N, program_stem=stem, instruction_count=instructions,
                    dma_count=len(dma), used_lines=used, capacity_lines=used,
                    guard_lines=GUARD_LINES, memory_base="0x90000000", minimum_ram_bytes=536870912,
                    model_verified=True, rtl_verified=False)
    (destination/"PARAMETERS.json").write_text(json.dumps(metadata, indent=2)+"\n")
    print(f"{stem}: model PASS, commands={instructions}, DMA={len(dma)}, lines={used}", flush=True)


def primitives(source, root, renderer, model, commit, selected):
    hw = source/"mm/test_data/hardware"
    a = u32((hw/"images/input_a.u32.bin").read_bytes())
    b = u32((hw/"images/input_b.u32.bin").read_bytes())
    params = json.loads((source/"bconv/test_data/params.json").read_text())
    q, q1 = params["moduli"][:2]
    require(len(a) == len(b) == N and all(v < q for v in a+b), f"N{N} input geometry")
    mod = (source/"bconv/test_data/hardware/constants/mod_ctx.u32.bin").read_bytes()
    for operation in ("padd", "psub", "pmul", "pmac", "pntt", "pintt", "pmodld", "psync", "pfree"):
        if selected and operation not in selected: continue
        image, bindings, commands, outputs = bytearray(), [], [], []
        def allocate(blob):
            require(len(blob) % 256 == 0, "unaligned input")
            first = len(image)//256; image.extend(blob)
            return first, len(blob)//256
        def load(slot, span, mod_table=False):
            commands.append(f"dload x10, x11, p{slot}, {2 if mod_table else 1}, {1 if mod_table else 0}")
            bindings.append(span)
        def store(slot, words, modulus=q, release=True):
            span = allocate(b"\xff"*(N*4))
            commands.append(f"dstore x10, x11, p{slot}, {int(release)}")
            bindings.append(span)
            outputs.append((span[0], words, modulus, len(outputs), 0))
        span_a, span_b = allocate(packed(a)), allocate(packed(b))
        span_mod = allocate(mod)
        if operation not in ("pfree", "psync"):
            load(3, span_mod, True); commands.append("pmodld 0")
        load(0, span_a)
        if operation == "psync":
            store(0, a)
        elif operation == "pfree":
            commands.append("pfree p0"); load(0, span_b); store(0, b)
        elif operation in ("pntt", "pintt"):
            direction = operation[1:]
            stage = N.bit_length() - 2
            twiddle = (source/direction/f"test_data/hardware/constants/twiddle/{direction}/basis_00/stage_{stage:02d}.u32.bin").read_bytes()
            load(1, allocate(twiddle))
            commands.append(f"{operation} p0, p1, {stage}, 0, 0")
            store(0, stage_reference(a, u32(twiddle), q, stage, inverse=operation=="pintt"))
            commands.append("pfree p1")
        else:
            load(1, span_b)
            if operation == "pmac":
                load(2, allocate(packed([q-1]*N)))
                commands.append("pmac p2, p0, p1")
                store(2, [(q-1+x*y)%q for x,y in zip(a,b)])
            elif operation == "pmodld":
                for mod_id, modulus in ((0,q), (1,q1), (0,q)):
                    commands += [f"pmodld {mod_id}", "padd p2, p0, p1"]
                    store(2, [(x+y)%modulus for x,y in zip(a,b)], modulus)
            else:
                commands.append(f"{operation} p2, p0, p1")
                result = [(x+y)%q if operation=="padd" else (x-y)%q if operation=="psub" else x*y%q for x,y in zip(a,b)]
                store(2, result)
                if operation == "pmul":
                    commands.append("pmul p2, p0, 255")
                    store(2, [x*255%q for x in a])
            commands += ["pfree p0", "pfree p1"]
        if operation not in ("pfree", "psync"):
            commands.append("pfree p3")
        commands.append("psync")
        metadata = dict(operation=operation, scheme="RNS primitive", q_moduli=[q,q1] if operation=="pmodld" else [q],
                        p_moduli=[], dnum=None, stage=N.bit_length()-2 if operation in ("pntt","pintt") else None,
                        input_source="inline-asm/mm", golden_source="independent modular/stage reference",
                        legacy_commit=commit, security_level_bits=0)
        emit(root, f"{operation}_n{N}", "\n".join(commands)+"\n", image, bindings, outputs, metadata, renderer, model)


def composite(source, root, renderer, model, commit, selected):
    for operation in ("ntt", "intt", "bconv", "auto"):
        if selected and operation not in selected: continue
        package = source/operation
        hw = package/"test_data/hardware"
        params = json.loads((package/"test_data/params.json").read_text())
        require(params["N"] == N, "legacy degree mismatch")
        line_map = {row["path"]: row for row in rows(hw/"line_map.csv")}
        image = bytearray((hw/"hpu_mem_image.u32.bin").read_bytes())
        program = [asm for _,asm in re.findall(r"/\* (\d+): (.*?) \*/", (package/f"{operation}.c").read_text())]
        require(program and program[-1] == "psync" and program.count("psync")==1, "terminal PSYNC")
        q = params["moduli"]
        outputs = []
        if operation in ("ntt", "intt"):
            paths = ["constants/mod_ctx.u32.bin", "images/input.u32.bin"]
            factor = f"constants/twiddle/{operation}/basis_00/"+("pre_twist.u32.bin" if operation=="ntt" else "post_untwist_scale.u32.bin")
            if operation == "ntt": paths.append(factor)
            paths += [f"constants/twiddle/{operation}/basis_00/stage_{i:02d}.u32.bin" for i in range(N.bit_length()-1)]
            if operation == "intt": paths.append(factor)
            paths.append("images/expected.u32.bin")
            bindings = [(int(line_map[path]["line_offset"]), int(line_map[path]["line_count"])) for path in paths]
            outputs = [(bindings[-1][0], u32((hw/paths[-1]).read_bytes()), q[0], 0, 0)]
        else:
            plan = rows(package/"test_data/dma_plan.csv")
            require(all(row["status"]=="RESOLVED" for row in plan), "unresolved legacy DMA")
            bindings = [(int(row["line_offset"]), int(row["line_count"])) for row in plan]
            if operation == "bconv":
                golden = physical64(package/"test_data/expected_p.bin")
                first = int(line_map["images/runtime/output_p.u32.bin"]["line_offset"])
                outputs = [(first+i*POLY_LINES, golden[i*N:(i+1)*N], q[4+i], 0, i) for i in range(3)]
            else:
                golden = physical64(package/"test_data/expected/ciphertext_q.bin")
                final = [row for row in plan if row["direction"]=="dstore" and row["logical_object"].startswith("output.ciphertext_q[")]
                final.sort(key=lambda row:int(row["logical_object"].split("[")[1].split("]")[0]))
                require(len(final)==8, "Auto output count")
                outputs = [(int(row["line_offset"]), golden[i*N:(i+1)*N], q[i%4], i//4, i%4) for i,row in enumerate(final)]
        metadata = dict(operation=operation, scheme="legacy RNS", q_moduli=q[:4], p_moduli=q[4:],
                        dnum=2 if operation=="auto" else None, legacy_commit=commit,
                        golden_source="inline-asm independent FHE reference", security_level_bits=0,
                        producer_parameters=params)
        if operation=="auto":
            metadata["auto_layout"] = json.loads((package/"test_data/AUTO_LAYOUT.json").read_text())
            require(metadata["auto_layout"].get("host_preprocess") is False,
                    "full Auto requires on-HPU permutation, not CPU-preprocessed KeySwitch")
        emit(root, f"{operation}_n{N}", "\n".join(program)+"\n", image, bindings, outputs, metadata, renderer, model)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("source", "destination", "renderer", "model"):
        parser.add_argument("--"+key, type=Path, required=True)
    parser.add_argument("--legacy-commit", required=True)
    parser.add_argument("--degree", type=int, choices=(4096, 8192, 16384, 32768, 65536), default=65536)
    parser.add_argument("--only", help="逗号分隔的操作列表；用于独立交付/受影响项重验")
    args = parser.parse_args()
    N = args.degree
    POLY_LINES = N // 64
    selected = set(args.only.split(",")) if args.only else None
    primitives(args.source, args.destination, args.renderer, args.model, args.legacy_commit, selected)
    composite(args.source, args.destination, args.renderer, args.model, args.legacy_commit, selected)
