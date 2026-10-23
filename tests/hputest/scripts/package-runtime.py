#!/usr/bin/env python3
"""按显式交付清单生成一个仅含00～07组ELF和BIN的hpu.zip。"""
import argparse
import csv
import os
from pathlib import Path, PurePosixPath
import re
import stat
import struct
import tempfile
import zipfile


FIELDS = ("group", "case_id", "producer", "elf", "bin", "degree", "level")
CASE_ID = re.compile(r"0[0-7]_\d{2}_[A-Za-z0-9_]+\Z")
GROUP = re.compile(r"(0[0-7])(?:_[A-Za-z0-9_]+)?\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def plain_root(value):
    requested = Path(value).absolute()
    require(not requested.is_symlink() and requested.is_dir(),
            f"expected a plain input directory: {requested}")
    return requested.resolve(strict=True)


def runtime_file(root, value, case_id, suffix):
    relative = PurePosixPath(value)
    require(value and not relative.is_absolute() and ".." not in relative.parts and
            "\\" not in value and not any(ord(char) < 32 for char in value),
            f"{case_id}: invalid {suffix} path")
    require(relative.suffix == suffix, f"{case_id}: wrong {suffix} extension")
    current = root
    for part in relative.parts:
        current /= part
        require(not current.is_symlink(), f"{case_id}: symlink is not allowed: {value}")
    require(current.is_file() and stat.S_ISREG(current.stat().st_mode) and current.stat().st_size > 0,
            f"{case_id}: missing or empty {suffix}: {current}")
    require(current.resolve().is_relative_to(root), f"{case_id}: path escapes input root")
    if suffix == ".elf":
        with current.open("rb") as stream:
            header = stream.read(20)
        require(len(header) == 20 and header[:6] == b"\x7fELF\x02\x01" and
                struct.unpack_from("<H", header, 18)[0] == 243,
                f"{case_id}: expected little-endian RV64 ELF")
    return current


def read_catalog(catalog):
    with Path(catalog).open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t", strict=True)
        require(reader.fieldnames is not None and len(reader.fieldnames) == len(set(reader.fieldnames)) and
                set(FIELDS).issubset(reader.fieldnames), "runtime catalog has missing or duplicate columns")
        rows = list(reader)
    require(rows and not any(None in row or any(value is None for value in row.values()) for row in rows),
            "runtime catalog is empty or malformed")
    return rows


def select_files(rows, roots):
    """只消费清单列出的文件；相邻的源码、旧大规模用例和其他版本不可混入。"""
    files, identities, sources = {}, set(), set()
    for row in rows:
        identity, match = row["case_id"], GROUP.fullmatch(row["group"])
        require(CASE_ID.fullmatch(identity) is not None and match is not None and
                identity[:2] == match[1], f"invalid group/case identity: {identity}")
        group = match[1]
        require(identity not in identities, f"duplicate runtime case: {identity}")
        identities.add(identity)
        require(row["producer"] in roots, f"{identity}: unknown producer: {row['producer']}")
        if group in ("03", "04", "05"):
            require(row["degree"] == "1024" and row["level"] == "4",
                    f"{identity}: 03～05 require N1024/L4")
        elif group == "07":
            require(row["degree"].isdigit() and row["level"].isdigit() and
                    int(row["degree"]) in (1024, 8192) and int(row["level"]) == 4,
                    f"{identity}: 07 requires N1024/N8192 and level=4")
        for key, suffix in (("elf", ".elf"), ("bin", ".bin")):
            source = runtime_file(roots[row["producer"]], row[key], identity, suffix)
            require(source not in sources, f"runtime source reused by multiple cases: {source}")
            sources.add(source)
            files[f"{group}/{identity}{suffix}"] = source
    return files


def prepare_files(catalog, roots, check_tree=False):
    roots = {name: plain_root(value) for name, value in roots.items()}
    files = select_files(read_catalog(catalog), roots)
    if check_tree:
        actual = set()
        for root in roots.values():
            for directory, names, leaves in os.walk(root, followlinks=False):
                for name in names + leaves:
                    path = Path(directory) / name
                    require(not path.is_symlink(), f"runtime tree contains symlink: {path}")
                    require(path.is_dir() or stat.S_ISREG(path.stat().st_mode),
                            f"runtime tree contains special file: {path}")
                actual.update(Path(directory) / name for name in leaves)
        require(actual == set(files.values()), "runtime tree differs from explicit catalog")
    return files


def package_runtime(catalog, roots, output, check_tree=False):
    files = prepare_files(catalog, roots, check_tree)
    output = Path(output).absolute()
    require(output.name == "hpu.zip", "runtime archive must be named hpu.zip")
    require(not output.exists() and not output.is_symlink(), f"output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=".hpu-runtime-", suffix=".zip", dir=output.parent)
    os.close(handle)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1,
                             allowZip64=True) as archive:
            for destination, source in sorted(files.items()):
                archive.write(source, destination)
        # link而不是replace，避免并发构建覆盖已经交付的文件。
        os.link(temporary, output)
    finally:
        temporary.unlink()
    return output, len(files) // 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--root", action="append", required=True, metavar="NAME=PATH",
                        help="清单producer列对应的构建根；可多次提供，不扫描根目录")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check-tree", action="store_true",
                        help="输入根内的文件必须恰好等于清单；用于直接上传目录前的门禁")
    parser.add_argument("--check-only", action="store_true", help="只检查，不写ZIP")
    args = parser.parse_args()
    roots = {}
    for value in args.root:
        name, separator, path = value.partition("=")
        require(separator and name and path and name not in roots, "invalid or duplicate --root")
        roots[name] = Path(path)
    if args.check_only:
        files = prepare_files(args.catalog, roots, args.check_tree)
        print(f"Runtime files checked: {len(files) // 2} cases, ELF + BIN only; hardware NOT RUN")
    else:
        require(args.output is not None, "--output is required unless --check-only is used")
        archive, count = package_runtime(args.catalog, roots, args.output, args.check_tree)
        print(f"Runtime package: {archive}; {count} cases, ELF + BIN only; hardware NOT RUN")


if __name__ == "__main__":
    main()
