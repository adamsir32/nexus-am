#!/usr/bin/env python3
"""按唯一清单顺序构建低层定向用例，仅导出ELF/BIN。"""

import argparse
import csv
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("group", "case_id", "producer", "elf", "bin", "degree", "level", "qualifier")


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def selected_cases(root):
    # kind明确区分定向C用例和新的03指令矩阵，不凭旧编号范围猜测归属。
    with (root / "cases.tsv").open(newline="", encoding="utf-8") as stream:
        cases = [row for row in csv.DictReader(stream, delimiter="\t") if row["kind"] == "lowlevel"]
    require(cases and len({row["case_id"] for row in cases}) == len(cases),
            "低层清单为空或case_id重复")
    return cases


def prepare(args):
    expected = json.loads((ROOT / "producer.json").read_text())["commit"]
    actual_commit = subprocess.check_output(
        ["git", "-C", args.producer, "rev-parse", "HEAD"], text=True).strip()
    require(actual_commit == expected, "低层producer路径不是当前固定新版提交")
    metadata = args.generated / "lowlevel.json"
    if not metadata.is_file():
        subprocess.run([sys.executable, ROOT / "scripts/prepare-lowlevel.py",
                        "--producer", args.producer, "--output", args.generated,
                        "--native-build", args.output / "native-lowlevel"], check=True)
    actual = json.loads(metadata.read_text())
    require(actual.get("producer_commit") == expected and actual.get("isa") == "64-object-v1.2"
            and actual.get("twiddle") == "hpu-twiddle-k8-v1", "现有低层生成目录不是当前新版交付")
    with (args.generated / "lowlevel-encodings.tsv").open(newline="", encoding="utf-8") as stream:
        return {int(row["word_hex"], 16) for row in csv.DictReader(stream, delimiter="\t")}


def verify_elf(path, cross, allowed):
    data = path.read_bytes()
    require(data[:6] == b"\x7fELF\x02\x01" and struct.unpack_from("<H", data, 18)[0] == 243,
            f"不是little-endian RV64 ELF：{path}")
    # ELF的可加载区不得覆盖运行时HPU DDR窗口。
    offset = struct.unpack_from("<Q", data, 32)[0]
    size, count = struct.unpack_from("<HH", data, 54)
    for index in range(count):
        kind, flags, file_offset, virtual, physical, file_size, memory_size, alignment = struct.unpack_from(
            "<IIQQQQQQ", data, offset + index * size)
        if kind == 1 and memory_size:
            require(physical + memory_size <= 0x87000000, f"ELF与HPU DDR窗口重叠：{path}")
    disassembly = subprocess.check_output([cross + "objdump", "-d", path], text=True)
    words = [int(word, 16) for word in re.findall(r"^\s*[0-9a-f]+:\s+([0-9a-f]{8})\s", disassembly, re.M)]
    hpu = [word for word in words if word & 0x7f in (0x0b, 0x2b, 0x5b)]
    require(all(word in allowed for word in hpu), f"ELF包含非当前编码器机器字：{path}")
    # MMIO与终止探针允许不含HPU机器字，不能因此伪造发指令次数。
    return len(hpu)


def degree(row):
    return int(row.get("degree") or 0)


def build_case(args, row, allowed):
    case_id = row["case_id"]
    objects = args.output / "objects-lowlevel" / case_id
    objects.mkdir(parents=True, exist_ok=True)
    binary = objects / case_id
    log = args.output / "logs" / (case_id + ".log")
    source = args.am_home / "tests/hputest" / row["source"]
    command = ["make", "-s", "-j", str(args.jobs), "-C", args.am_home / "tests/hputest",
               "-f", "Makefile.case", "image", f"AM_HOME={args.am_home}", f"ARCH={args.arch}",
               f"CROSS_COMPILE={args.cross}", "LINUX_GNU_TOOLCHAIN=1", f"CASE_ID={case_id}",
               f"CASE_SOURCE={source}", f"HPU_DST_DIR={objects}",
               f"HPU_GENERATED_ROOT={args.generated}", f"CASE_BINARY={binary}",
               f"HPU_LOG_LEVEL={getattr(args, 'log_level', 1)}"]
    with log.open("w", encoding="utf-8") as stream:
        result = subprocess.run([str(value) for value in command], stdout=stream, stderr=subprocess.STDOUT)
        require(result.returncode == 0, f"{case_id}构建失败，详见{log}")
        subprocess.run([args.cross + "strip", "--strip-debug", str(binary) + ".elf"],
                       check=True, stdout=stream, stderr=subprocess.STDOUT)
    count = verify_elf(Path(str(binary) + ".elf"), args.cross, allowed)
    if getattr(args, "log_level", 1) == 0:
        subprocess.run([sys.executable, ROOT / "scripts/verify-silent-elf.py", "--elf", str(binary) + ".elf",
                        "--cross-compile", args.cross], check=True)
    destination = args.output / "runtime" / row["group"]
    destination.mkdir(parents=True, exist_ok=True)
    for extension in ("elf", "bin"):
        shutil.copyfile(str(binary) + "." + extension, destination / (case_id + "." + extension))
    return {"group": row["group"], "case_id": case_id, "producer": "runtime",
            "elf": f'{row["group"]}/{case_id}.elf', "bin": f'{row["group"]}/{case_id}.bin',
            "degree": degree(row), "level": int(row.get("level") or 0), "qualifier": row["qualifier"]}, count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("am-home", "producer", "output", "generated"):
        parser.add_argument("--" + name, required=name != "generated", type=lambda value: Path(value).resolve())
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--cross", default=os.environ.get("CROSS_COMPILE", "riscv64-linux-gnu-"))
    parser.add_argument("--arch", default="riscv64-xs", choices=["riscv64-xs"])
    parser.add_argument("--log-level", type=int, choices=(0, 1), default=1)
    args = parser.parse_args()
    require(args.jobs > 0, "jobs必须为正整数")
    args.generated = args.generated or args.output / "generated"
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "logs").mkdir(exist_ok=True)
    cases = selected_cases(args.am_home / "tests/hputest")
    allowed = prepare(args)
    rows = []
    for index, case in enumerate(cases, 1):
        row, count = build_case(args, case, allowed)
        rows.append(row)
        print(f"[{index}/{len(cases)}] {row['case_id']} ELF/BIN通过，原生HPU机器字{count}条", flush=True)
    with (args.output / "lowlevel-cases.tsv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(cases)}项低层用例构建及机器字验证完成；未运行RTL。")


if __name__ == "__main__":
    main()
