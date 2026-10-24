"""统一原生用例的目标构建与机器字验证；不维护第二套清单或发布入口。"""
from pathlib import Path
import re
import struct
import subprocess

from import_package import require

ROOT = Path(__file__).resolve().parents[1]


def run(arguments, **kwargs):
    subprocess.run([str(arg) for arg in arguments], check=True, **kwargs)


def output(arguments):
    return subprocess.check_output([str(arg) for arg in arguments], text=True).strip()


def verify_elf(path, cross, meta):
    data = path.read_bytes()
    require(data[:6] == b"\x7fELF\x02\x01" and struct.unpack_from("<H", data, 18)[0] == 243,
            "expected little-endian RV64 ELF")
    phoff = struct.unpack_from("<Q", data, 32)[0]
    size, count = struct.unpack_from("<HH", data, 54)
    for index in range(count):
        kind, flags, off, va, pa, filesz, memsz, alignment = struct.unpack_from("<IIQQQQQQ", data, phoff + index * size)
        if kind == 1 and memsz:
            require(pa + memsz <= 0x87000000, "ELF LOAD segment overlaps workload DDR")
    # GCC会把大函数拆成.part.0或.constprop.0；按实际text符号查找，不能假定原名保留。
    symbols = output([cross + "nm", "-S", "--defined-only", path]).splitlines()
    # 新版实际执行fixed hpu_run；旧版wrapper无HPU字时才检查其dynamic callee。
    for entry in ("hpu_run_", "hpu_program_"):
        prefix = entry + meta["program_stem"]
        names = [row.split()[-1] for row in symbols if len(row.split()) == 4 and
                 row.split()[-2] in ("T", "t") and
                 (row.split()[-1] == prefix or row.split()[-1].startswith(prefix + "."))]
        disassembly = "\n".join(output([cross + "objdump", "-d", "--disassemble=" + name, path]) for name in names)
        words = [int(word, 16) for word in re.findall(r"^\s*[0-9a-f]+:\s+([0-9a-f]{8})\s", disassembly, re.M)]
        actual = [word for word in words if word & 0x7f in (0x2b, 0x5b)]
        if actual:
            return actual
    raise ValueError("missing native HPU program text")


def build_case(args, spec, data, meta, mode):
    case_dir = args.output / "artifact" / mode / spec["case_id"]
    case_dir.mkdir(parents=True, exist_ok=True)
    binary = case_dir / spec["case_id"]
    objects = args.output / "objects" / mode / str(args.wait_cycles) / spec["case_id"]
    # AM共享库和mainargs.S不可并行改写，ELF逐个构建；多个ELF在IT外部可并行运行。
    run(["make", "-s", "-C", ROOT, "-f", "Makefile.native.case", "image",
         f"AM_HOME={args.am_home}", f"ARCH={args.arch}", f"CROSS_COMPILE={args.cross}",
         f'CASE_ID={spec["case_id"]}', f'CASE_SOURCE={ROOT / spec["source"]}',
         f"DATA_DIR={data}", f'PROGRAM_STEM={meta["program_stem"]}',
         f"LOG_LEVEL={int(mode != 'silent')}", f"WAIT_CYCLES={args.wait_cycles}",
         f"CASE_OBJ_DIR={objects}", f"CASE_BINARY={binary}"])
    run([args.cross + "strip", "--strip-debug", str(binary) + ".elf"])
    if "psync_prefixes" in meta:
        from psync_prefixes import verify_prefix_elf
        verify_prefix_elf(Path(str(binary) + ".elf"), data, meta["psync_prefixes"], args.cross)
    else:
        actual_words = verify_elf(Path(str(binary) + ".elf"), args.cross, meta)
        expected_words = [int(word, 2) for word in (data / (meta["program_stem"] + ".inst32")).read_text().split()]
        require(actual_words == expected_words, "ELF HPU words differ from native package")
    if mode == "silent":
        run(["python3", args.am_home / "tests/hputest/scripts/verify-silent-elf.py",
             "--elf", str(binary) + ".elf", "--cross-compile", args.cross])
    return {**meta, "mode": mode, "wait_cycle_budget": args.wait_cycles,
            "elf_instruction_words_verified": True,
            "elf": str((case_dir / (spec["case_id"] + ".elf")).relative_to(args.output / "artifact"))}
