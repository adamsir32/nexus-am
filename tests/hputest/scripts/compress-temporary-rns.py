#!/usr/bin/env python3
"""逐文件压缩本次large.*树内已完成的原生RNS临时数据，可用gzip恢复。

调用方必须等reference及prepare-large-data成功结束，确认没有读写者再调用。
只接受一个明确.bin路径；不处理delivery、应用包或ELF，不生成校验清单。
"""

import argparse
import gzip
import os
from pathlib import Path
import re
import shutil
import stat


MINIMUM_BYTES = 1024 * 1024


def signature(info):
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def compress_one(value, generation_root):
    root, source = Path(generation_root).absolute(), Path(value).absolute()
    if (root.is_symlink() or not root.is_dir() or
            re.fullmatch(r"large\.[A-Za-z0-9_-]+", root.name) is None):
        raise ValueError("generation root must be this run's plain large.* directory")
    try:
        relative = source.relative_to(root)
    except ValueError as error:
        raise ValueError("input is outside generation root") from error
    if (".." in relative.parts or len(relative.parts) < 3 or
            re.fullmatch(r"(?:legacy-)?n(?:4096|8192|16384|32768|65536)", relative.parts[0]) is None or
            relative.parts[1] != "outputs" or source.suffix != ".bin"):
        raise ValueError("input must be a .bin below nN/outputs or legacy-nN/outputs")
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"symlink is not allowed: {current}")
    before = source.stat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError("input must be a regular file")
    if (before.st_size == 0 or before.st_size % 4 != 0 or
            source.stem.lower().endswith((".tmp", ".part", ".partial", ".incomplete"))):
        raise ValueError("input is empty, incomplete or not whole RNS words")
    destination = source.with_name(source.name + ".gz")
    if os.path.lexists(destination):
        raise FileExistsError(f"compressed file already exists: {destination}")
    if before.st_size <= MINIMUM_BYTES:
        return None

    created = None
    try:
        with source.open("rb") as raw:
            if signature(os.fstat(raw.fileno())) != signature(before):
                raise ValueError("input changed before compression")
            with destination.open("xb") as compressed:
                created = os.fstat(compressed.fileno())
                with gzip.GzipFile(filename=source.name, mode="wb", fileobj=compressed,
                                   compresslevel=1, mtime=int(before.st_mtime)) as stream:
                    shutil.copyfileobj(raw, stream, length=MINIMUM_BYTES)
                compressed.flush()
                os.fsync(compressed.fileno())
            if (raw.tell() != before.st_size or
                    signature(os.fstat(raw.fileno())) != signature(before) or
                    signature(source.lstat()) != signature(before)):
                raise ValueError("input changed during compression; original file retained")
        compressed_bytes = destination.stat().st_size
        source.unlink()  # 仅此明确路径；完整.gz已关闭并落盘，可恢复原始字节。
        return destination, before.st_size, compressed_bytes
    except Exception:
        # 只回收本次独占创建的失败输出；已有.gz、原文件和其它目录均不动。
        if created is not None and destination.exists():
            current = destination.lstat()
            if (current.st_dev, current.st_ino) == (created.st_dev, created.st_ino):
                destination.unlink()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="一个明确的已完成原生.bin文件")
    parser.add_argument("--generation-root", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = compress_one(args.file, args.generation_root)
    except (OSError, ValueError) as error:
        parser.exit(2, f"temporary RNS compression: {error}\n")
    if result is not None:
        destination, original, compressed = result
        print(f"[hputest] temporary RNS compressed: {destination} ({original} -> {compressed} bytes)")


if __name__ == "__main__":
    main()
