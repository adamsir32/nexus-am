"""07构建和实际ELF计时门禁；清单与单包发布由build-runtime统一负责。"""
import csv
from pathlib import Path
import re
import struct
import subprocess

from import_package import NTT_ABI, expected_operations, package_profile, read_json, require

ROOT = Path(__file__).resolve().parents[1]
OPS = ("keyswitch", "hadd", "hmul", "reline", "modswitch", "rotate")


def run(command, **kwargs):
    subprocess.run([str(value) for value in command], check=True, **kwargs)


def output(command):
    return subprocess.check_output([str(value) for value in command], text=True).strip()


def select_specs(degree, profile, scheme, case_id=None):
    """07也只读取统一cases.tsv；筛选不引入独立构建或发布流水线。"""
    require(degree in (1024, 2048, 4096, 8192) and profile == "baseline",
            "07 requires N<=8192 and level<=4")
    with (ROOT / "cases.tsv").open(newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    result = []
    for source in rows:
        if source["kind"] != "performance":
            continue
        row = dict(source)
        for key in ("degree", "level", "minimum_ram_bytes"):
            row[key] = int(row[key])
        relative = Path(row["source"])
        require(relative == Path("src/07_performance/main.c") and (ROOT / relative).is_file(),
                "invalid case source")
        package_profile({**row, "variant": "optimized"})
        require(row["metric"] == "issue_to_done_v2", "unknown measurement contract")
        if row["degree"] == degree and row["scheme"] == scheme and (
                case_id is None or row["case_id"] == case_id):
            result.append(row)
    require(result and (not case_id or len(result) == 1), "scope/case selects no unique performance case")
    if not case_id:
        require({row["operation"] for row in result} == set(OPS), "incomplete operator scope")
    return result


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
    run(["make", "-s", "-C", ROOT, "-f", "Makefile.native.case", "image",
         f"AM_HOME={args.am_home}", f"ARCH={args.arch}", f"CROSS_COMPILE={args.cross}",
         f"CASE_ID={spec['case_id']}", f"CASE_SOURCE={ROOT / spec['source']}", f"DATA_DIR={data}",
         f"PROGRAM_STEM={spec['program_stem']}", "PERFORMANCE=1", f"CASE_MEM_BASE={spec['memory_base']}",
         f"CASE_DEGREE={spec['degree']}", f"CASE_LEVEL={spec['level']}",
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
