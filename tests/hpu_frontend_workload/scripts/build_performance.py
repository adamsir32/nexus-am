#!/usr/bin/env python3
"""独立构建1019新API的一个算子分片；不生成或修改主线hputest基线。"""
import argparse
import csv
import io
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
import uuid
import zipfile

from import_package import (NTT_ABI, expected_operations, import_package, package_profile,
                            read_json, require)

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ("optimized", "noopt")
OPS = ("keyswitch", "hadd", "hmul", "reline", "modswitch", "rotate")


def run(command, **kwargs):
    subprocess.run([str(value) for value in command], check=True, **kwargs)


def output(command):
    return subprocess.check_output([str(value) for value in command], text=True).strip()


def select_specs(degree, profile, scheme, case_id=None):
    require(degree in (1024, 2048, 4096, 8192) and profile == "baseline", "1019 requires N<=8192 and level<=4")
    with (ROOT / "performance-cases.tsv").open(newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    require(len(rows) == 72 and len({row["case_id"] for row in rows}) == 72, "invalid experimental roster")
    result = []
    for source in rows:
        row = dict(source)
        for key in ("degree", "level", "minimum_ram_bytes"):
            row[key] = int(row[key])
        relative = Path(row["source"])
        require(not relative.is_absolute() and ".." not in relative.parts and
                row["source"].startswith("src/07_performance/") and
                relative.name == row["case_id"] + ".c" and (ROOT / relative).is_file(), "invalid case source")
        package_profile({**row, "variant": "optimized"})
        require(row["metric"] == "issue_to_done_v2", "unknown measurement contract")
        if row["degree"] == degree and row["scheme"] == scheme and \
                profile == "baseline" and \
                (case_id is None or row["case_id"] == case_id):
            result.append(row)
    require(len(result) == (1 if case_id else 6), "scope/case does not select the expected operator set")
    if not case_id:
        require({row["operation"] for row in result} == set(OPS), "incomplete operator shard")
    return result


def cache_request(path, expected):
    if path.exists():
        require(not path.is_symlink() and read_json(path) == expected,
                "existing cache differs in producer/scope/source/options; use a fresh OUTPUT_ROOT")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x") as stream:
            json.dump(expected, stream, indent=2)
            stream.write("\n")


def prepare_producer(args, pin):
    require(output(["git", "-C", args.producer, "rev-parse", "HEAD"]) == pin, "producer pin mismatch")
    require(not output(["git", "-C", args.producer, "status", "--porcelain", "--untracked-files=no"]),
            "producer must be clean")
    if args.producer_build is not None:
        build = args.producer_build
        cache = {}
        for line in (build / "CMakeCache.txt").read_text().splitlines():
            if "=" in line and not line.startswith(("#", "//")):
                key, value = line.split("=", 1)
                cache[key.split(":", 1)[0]] = value
        require(Path(cache.get("INLINE_ASM_ROOT", "")).resolve() == args.producer and
                Path(cache.get("CMAKE_HOME_DIRECTORY", "")).resolve() == ROOT / "tools/operator_perf",
                "external native build belongs to another producer/project")
        generator, validator = build / "hpu_frontend_operator_generator", build / "inline-asm/hpu_validate_package"
        require(generator.is_file() and validator.is_file(), "external native build is incomplete")
        return generator, validator
    build = args.output / "producer-build" / pin
    run(["cmake", "-S", ROOT / "tools/operator_perf", "-B", build,
         "-DINLINE_ASM_ROOT=" + str(args.producer), "-DCMAKE_BUILD_TYPE=Release",
         "-DHPU_ENABLE_SEAL_DIFFERENTIAL_ORACLE=OFF", "-DHPU_ENABLE_SEAL_BFV_ORACLE=OFF"])
    run(["cmake", "--build", build, "--parallel", args.jobs, "--target",
         "hpu_frontend_operator_generator", "hpu_validate_package"])
    return build / "hpu_frontend_operator_generator", build / "inline-asm/hpu_validate_package"


def validate_fixture(path, spec, pin):
    fixture = read_json(path)
    for key in ("scheme", "operation", "degree", "level", "variant", "program_stem"):
        require(fixture.get(key) == spec[key], f"fixture identity differs: {key}")
    require(fixture.get("schema_version") == 1 and fixture.get("producer_commit") == pin and
            fixture.get("producer_worktree_state") == "clean-at-configure", "fixture producer differs")
    require(all(fixture.get(key) is True for key in
                ("verified", "instruction_verified", "fixture_words_equal", "fixture_metadata_equal", "native_package_written")),
            "fixture/native instruction model has not passed")
    require(fixture.get("hardware_verified") is False and
            fixture.get("ntt_contract") == "natural_coefficient_boundaries" and
            fixture.get("ntt_table_abi") == NTT_ABI, "fixture NTT/hardware contract differs")
    require(fixture.get("node_operations") == expected_operations(spec["scheme"], spec["operation"]),
            "fixture operator graph differs")
    require(isinstance(fixture.get("Q"), list) and len(fixture["Q"]) == spec["level"] and
            isinstance(fixture.get("P"), list) and len(fixture["P"]) == 1,
            "fixture Q/P moduli are missing or inconsistent")
    return fixture


def perf_adapter():
    # 新版固定入口复用x11，不能再套用主线动态spans的旧C模板。
    import performance_adapter
    return performance_adapter


def prepare_case(args, spec, pin, generator, validator, request):
    container = args.work / "packages" / spec["case_id"]
    marker = container / "BUILD_REQUEST.json"
    case_request = {**request, "case": spec}
    if container.exists():
        require(marker.is_file() and read_json(marker) == case_request,
                "existing native package is incomplete or belongs to another request")
    else:
        container.parent.mkdir(parents=True, exist_ok=True)
        logs = args.work / "logs"
        logs.mkdir(exist_ok=True)
        with (logs / (spec["case_id"] + ".log")).open("x") as log:
            run([generator, spec["scheme"], spec["operation"], spec["degree"], args.profile, container],
                stdout=log, stderr=subprocess.STDOUT)
        cache_request(marker, case_request)
    deliveries = []
    for variant in VARIANTS:
        selected = {**spec, "variant": variant}
        source = container / variant / "upstream"
        fixture = validate_fixture(container / variant / "PERF_FIXTURE.json", selected, pin)
        run([validator, source])
        destination = args.work / "generated" / spec["case_id"] / variant
        meta = import_package(source, destination, selected, pin, verify_existing=True)
        # 复用已审核的严格模板适配器；未知上游控制流直接拒收，不盲删参数检查。
        perf_adapter().prepare(destination, spec["program_stem"])
        deliveries.append((selected, source, destination, meta, fixture))
    comparable = ("scheme", "operation", "degree", "level", "program_stem", "profile", "Q", "P", "seed")
    require(all(key in deliveries[0][4] and key in deliveries[1][4] and
                deliveries[0][4][key] == deliveries[1][4][key] for key in comparable),
            "optimized and noopt fixtures use different parameters")
    return deliveries


def disassembled_functions(text):
    result, active = {}, None
    for line in text.splitlines():
        if line.startswith("Disassembly of section "):
            active = None
        label = re.match(r"^[0-9a-f]+ <([^>]+)>:$", line)
        if label:
            active = label[1]
            result[active] = []
        elif active:
            result[active].append(line)
    return {name: "\n".join(lines) for name, lines in result.items()}


def verify_success_timing(main, stem):
    """沿main控制流检查所有case_pass路径；GCC可复制失败路径的停止rdcycle。"""
    wanted = ("hpu_validate_" + stem, "perf_cycle_read", "hpu_run_" + stem,
              "performance_wait", "perf_cycle_read", "check_results", "check_memory")
    instructions = {}
    for line in main.splitlines():
        match = re.match(r"^\s*([0-9a-f]+):\s+[0-9a-f]{4,8}\s+([\w.]+)(?:\s+(.*))?$", line)
        if match:
            instructions[int(match[1], 16)] = (match[2], match[3] or "")
    require(bool(instructions), "missing main instructions")
    addresses = sorted(instructions)
    following = dict(zip(addresses, addresses[1:] + [None]))
    branches = {"beq", "bne", "blt", "bltu", "bge", "bgeu", "beqz", "bnez",
                "bgtz", "blez", "bltz", "bgez", "bgtu", "bleu", "bgt", "ble"}
    pending, seen, passed = [(addresses[0], (), False)], set(), 0
    while pending:
        address, events, forbidden = pending.pop()
        state = (address, events, forbidden)
        if state in seen:
            continue
        seen.add(state)
        require(address in instructions and len(events) <= len(wanted) + 2, "unbounded/unresolved main control flow")
        opcode, operands = instructions[address]
        label = re.search(r"([0-9a-f]+)\s+<([^>]+)>", operands)
        destination = int(label[1], 16) if label else None
        symbol = label[2].split("+", 1)[0] if label else ""

        def finish(target):
            nonlocal passed
            if target == "case_fail":
                return
            require(target == "case_pass", "unresolved main exit")
            require(events == wanted and not forbidden, "preflight/issue/wait/cycle/check ordering differs on a PASS path")
            passed += 1

        if opcode in ("jal", "jalr"):
            require(label is not None, "unresolved indirect main call")
            if symbol in ("case_pass", "case_fail"):
                finish(symbol)
                continue
            if events.count("perf_cycle_read") == 1 and symbol not in (wanted[2], "performance_wait", "perf_cycle_read"):
                forbidden = True
            if symbol in wanted:
                events += (symbol,)
        elif opcode in ("j", "tail"):
            require(label is not None, "unresolved main jump")
            if destination not in instructions:
                finish(symbol)
                continue
            pending.append((destination, events, forbidden))
            continue
        elif opcode in branches:
            require(label is not None and destination in instructions, "unresolved main branch")
            pending.append((destination, events, forbidden))
        elif opcode in ("ret", "jr"):
            raise ValueError("main return bypasses explicit PASS/FAIL reporting")
        require(following[address] is not None, "main control flow falls outside function")
        pending.append((following[address], events, forbidden))
    require(passed > 0, "no proven case_pass path")


def verify_timing(text, stem):
    functions = disassembled_functions(text)
    verify_success_timing(functions.get("main", ""), stem)
    timed = {name: body for name, body in functions.items()
             if name.startswith(("hpu_program_" + stem, "hpu_run_" + stem)) and "_preflight" not in name}
    require(bool(timed), "missing timed native entry")
    for name, body in timed.items():
        require(re.search(r"\s(?:beq|bne|blt|bltu|bge|bgeu|beqz|bnez|bgtz|blez|bltz|bgez|bgtu|bleu)\s", body) is None,
                f"parameter validation remains in timed function: {name}")
        require(not any(token in body for token in ("trace_issue", "_preflight", "hpu_validate_")),
                "preflight/trace leaked into timed function")
    wait = functions.get("performance_wait", "")
    require(wait and not any(token in wait for token in ("printf", "phase_mark")), "wait path contains UART/phase logging")
    for name, body in functions.items():
        if name.startswith(("hpu_validate_" + stem, "hpu_program_" + stem + "_preflight")):
            require(not hpu_words(body), "preflight issues HPU instructions")


def hpu_words(body):
    words = re.findall(r"^\s*[0-9a-f]+:\s+([0-9a-f]{8})\s", body, re.M)
    return [int(word, 16) for word in words if int(word, 16) & 0x7f in (0x0b, 0x2b, 0x5b)]


def verify_embedded(elf, data, meta, cross):
    listing = output([cross + "nm", "-S", "--defined-only", elf])
    with elf.open("rb") as stream:
        header = stream.read(64)
        require(header[:6] == b"\x7fELF\x02\x01" and struct.unpack_from("<H", header, 18)[0] == 243,
                "expected little-endian RV64 ELF")
        base, ram_end = int(meta["memory_base"], 0), 0x80000000 + int(meta["minimum_ram_bytes"])
        require(base + (data / "image.u32.bin").stat().st_size <= ram_end, "runtime image exceeds RAM")
        phoff, shoff = struct.unpack_from("<QQ", header, 32)
        phsize, phcount, shsize, shcount = struct.unpack_from("<HHHH", header, 54)
        require(phsize == 56 and shsize == 64, "invalid ELF table layout")
        for index in range(phcount):
            stream.seek(phoff + phsize * index)
            kind, flags, offset, va, pa, filesz, memsz, align = struct.unpack("<IIQQQQQQ", stream.read(56))
            require(kind != 1 or not memsz or pa + memsz <= base, "ELF LOAD overlaps DDR")
        for symbol, filename in (("initial_image", "image.u32.bin"), ("golden_words", "golden.u32.bin"),
                                 ("writable_lines", "writable.u8.bin")):
            matches = re.findall(r"^([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+[Rr]\s+" + symbol + r"$", listing, re.M)
            require(len(matches) == 1, "missing/duplicate readonly symbol: " + symbol)
            address, length = (int(value, 16) for value in matches[0])
            require(length == (data / filename).stat().st_size, "embedded size differs: " + symbol)
            found = False
            for index in range(shcount):
                stream.seek(shoff + shsize * index)
                _, kind, flags, start, offset, size, *_ = struct.unpack("<IIQQQQIIQQ", stream.read(64))
                if kind == 1 and flags & 2 and not flags & 1 and start <= address and address + length <= start + size:
                    stream.seek(offset + address - start)
                    with (data / filename).open("rb") as expected:
                        remaining = length
                        while remaining:
                            count = min(remaining, 1024 * 1024)
                            require(stream.read(count) == expected.read(count), "embedded data differs: " + symbol)
                            remaining -= count
                    found = True
                    break
            require(found, "symbol is not in a readonly PROGBITS section: " + symbol)


def verify_elf(elf, disassembly, data, meta, cross):
    text = disassembly.read_text()
    functions = disassembled_functions(text)
    stem = meta["program_stem"]
    actual = []
    for prefix in ("hpu_run_" + stem, "hpu_program_" + stem):
        actual = [word for name, body in functions.items() if name == prefix or name.startswith(prefix + ".")
                  for word in hpu_words(body)]
        if actual:
            break
    expected = [int(word, 2) for word in (data / (stem + ".inst32")).read_text().split()]
    require(expected and actual == expected and expected[-1] == 0x7000005b and expected.count(0x7000005b) == 1,
            "ELF native word sequence/terminal PSYNC differs")
    verify_embedded(elf, data, meta, cross)
    verify_timing(text, stem)


def build_case(args, spec, data, meta, mode):
    case_dir = args.work / "artifact" / spec["variant"] / mode / spec["case_id"]
    case_dir.mkdir(parents=True, exist_ok=True)
    binary = case_dir / spec["case_id"]
    objects = args.work / "objects" / spec["variant"] / mode / str(args.wait_cycles) / spec["case_id"]
    run(["make", "-s", "-C", ROOT, "-f", "Makefile.case", "image",
         f"AM_HOME={args.am_home}", f"ARCH={args.arch}", f"CROSS_COMPILE={args.cross}",
         f"CASE_ID={spec['case_id']}", f"CASE_SOURCE={ROOT / spec['source']}", f"DATA_DIR={data}",
         f"PROGRAM_STEM={spec['program_stem']}", "PERFORMANCE=1", f"CASE_MEM_BASE={spec['memory_base']}",
         f"LOG_LEVEL={int(mode != 'silent')}", f"WAIT_CYCLES={args.wait_cycles}",
         f"CASE_OBJ_DIR={objects}", f"CASE_BINARY={binary}"])
    elf, binfile, disassembly = (Path(str(binary) + suffix) for suffix in (".elf", ".bin", ".txt"))
    run([args.cross + "strip", "--strip-debug", elf])
    run([args.cross + "objcopy", "-O", "binary", elf, binfile])
    with disassembly.open("w") as stream:
        run([args.cross + "objdump", "-d", elf], stdout=stream)
    verify_elf(elf, disassembly, data, meta, args.cross)
    if mode == "silent":
        run(["python3", args.am_home / "tests/hputest/scripts/verify-silent-elf.py", "--elf", elf, "--cross-compile", args.cross])
    return {**meta, "mode": mode, "wait_cycle_budget": args.wait_cycles,
            "elf_instruction_words_verified": True, "embedded_data_verified": True, "timing_verified": True,
            "elf": str(elf.relative_to(args.work)), "bin": str(binfile.relative_to(args.work)),
            "disassembly": str(disassembly.relative_to(args.work)), "measured_cycles": None}


def tree_entries(directory):
    require(not directory.is_symlink() and directory.is_dir(), "expected plain delivery directory")
    for path in sorted(directory.rglob("*")):
        require(not path.is_symlink(), "symlink is not publishable")
        if path.is_file():
            yield path, path.relative_to(directory)
        else:
            require(path.is_dir(), "special file is not publishable")


def publish(args, deliveries, rows, pin, specs):
    scope = f"n{args.degree}-{args.profile}-{args.scheme}"
    index = {"workload": "hpu_frontend_operator_performance", "scope": scope, "producer_commit": pin,
             "nexus_am_commit": output(["git", "-C", args.am_home, "rev-parse", "HEAD"]),
             "nexus_am_worktree_state": "dirty" if output(["git", "-C", args.am_home, "status", "--porcelain"]) else "clean",
             "status": "BUILD_READY_NOT_IT_PASS", "hardware_verified": False, "cases": rows}
    archive = args.output / f"hpu-1019-operator-perf-{scope}.zip"
    if archive.exists() or archive.is_symlink():
        require(not archive.is_symlink(), "archive cannot be a symlink")
        with zipfile.ZipFile(archive) as old:
            previous = json.loads(old.read("index.json"))
        require(previous.get("workload") == index["workload"] and previous.get("scope") == scope and
                previous.get("producer_commit") == pin, "refusing to replace unrelated archive")
    handle, temporary = tempfile.mkstemp(prefix=".operator-perf-", suffix=".zip", dir=args.output)
    os.close(handle)
    temporary = Path(temporary)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1) as zipped:
            zipped.writestr("index.json", json.dumps(index, indent=2) + "\n")
            table = io.StringIO()
            writer = csv.DictWriter(table, fieldnames=list(specs[0]), delimiter="\t", lineterminator="\n")
            writer.writeheader(); writer.writerows(specs)
            zipped.writestr("performance-cases.tsv", table.getvalue())
            zipped.write(ROOT / "scripts/parse_performance.py", "tools/parse_performance.py")
            zipped.write(ROOT / "producer.json", "producer.json")
            zipped.write(ROOT / "PERFORMANCE.md", "PERFORMANCE.md")
            zipped.write(ROOT / "performance-baseline.json", "performance-baseline.json")
            for spec in specs:
                zipped.write(ROOT / spec["source"], "sources/" + spec["case_id"] + ".c")
            for row in rows:
                for key in ("elf", "bin", "disassembly"):
                    zipped.write(args.work / row[key], row[key])
            for spec, source, data, meta, fixture in deliveries:
                prefix = f"delivery/{spec['case_id']}/{spec['variant']}"
                for path, relative in tree_entries(source):
                    zipped.write(path, prefix + "/upstream/" + relative.as_posix())
                for path, relative in tree_entries(data):
                    zipped.write(path, prefix + "/target/" + relative.as_posix())
                zipped.write(source.parent / "PERF_FIXTURE.json", prefix + "/PERF_FIXTURE.json")
                zipped.write(source.parent / "RESOURCE_REPORT.json", prefix + "/RESOURCE_REPORT.json")
        if archive.exists():
            previous = archive.with_name(archive.stem + ".previous-" + uuid.uuid4().hex[:10] + ".zip")
            archive.rename(previous)
            print(f"Previous experimental archive preserved: {previous}")
        temporary.replace(archive)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise
    print(f"Experimental performance package: {archive}; {len(rows)} ELF variants; VCS NOT RUN")
    return archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("am-home", "producer", "output"):
        parser.add_argument("--" + name, required=True, type=lambda value: Path(value).resolve())
    parser.add_argument("--degree", required=True, type=int, choices=(1024, 2048, 4096, 8192))
    parser.add_argument("--profile", required=True, choices=("baseline",))
    parser.add_argument("--scheme", required=True, choices=("ckks", "bfv", "bgv"))
    parser.add_argument("--mode", default="both", choices=("both", "minimal", "silent"))
    parser.add_argument("--arch", default="riscv64-xs", choices=("riscv64-xs",))
    parser.add_argument("--cross", default="riscv64-linux-gnu-")
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--wait-cycles", type=int, default=25000000)
    parser.add_argument("--case-id")
    parser.add_argument("--producer-build", type=lambda value: Path(value).resolve(),
                        help="本地复用已验证的native目录；省略则按producer commit冷构建")
    args = parser.parse_args()
    require(args.jobs > 0 and 0 < args.wait_cycles < 1 << 63, "invalid jobs/cycle budget")
    baseline = args.am_home / "tests/hputest"
    require(not args.output.is_relative_to(baseline) and args.output != args.am_home and
            not args.output.is_relative_to(args.producer), "output overlaps baseline/producer")
    pin = read_json(ROOT / "producer.json")["commit"]
    specs = select_specs(args.degree, args.profile, args.scheme, args.case_id)
    scope = f"n{args.degree}-{args.profile}-{args.scheme}"
    args.work = args.output / pin / scope
    request = {"producer_commit": pin, "scope": scope,
               "generator_sources": {path.relative_to(ROOT).as_posix(): path.read_text()
                                     for path in sorted((ROOT / "tools/operator_perf").rglob("*"))
                                     if path.is_file() and path.suffix in (".cpp", ".hpp", ".h", ".txt")}}
    request["shared_fixture_source"] = (ROOT.parent / "hputest/tools/hpu-scheme-cases/fixture.hpp").read_text()
    cache_request(args.work / "BUILD_REQUEST.json", request)
    generator, validator = prepare_producer(args, pin)
    deliveries = [delivery for spec in specs for delivery in prepare_case(args, spec, pin, generator, validator, request)]
    modes = ("minimal", "silent") if args.mode == "both" else (args.mode,)
    rows = [build_case(args, spec, data, meta, mode)
            for spec, source, data, meta, fixture in deliveries for mode in modes]
    publish(args, deliveries, rows, pin, specs)


if __name__ == "__main__":
    main()
