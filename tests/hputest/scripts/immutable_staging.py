#!/usr/bin/env python3
"""可选共享已验证、后续不再原地修改的发布文件；不用于generated或构建对象。

HPU_HARDLINK_STAGING=1时，artifact/release中至少1MiB的普通文件尝试硬链接，
跨文件系统则复制。调用方必须使用全新的目标目录，后续重建需轮换整个artifact。
"""

import argparse
import errno
import os
from pathlib import Path
import shutil
import stat
import tempfile


LARGE_FILE_BYTES = 1024 * 1024


def hardlink_staging_enabled():
    value = os.environ.get("HPU_HARDLINK_STAGING", "0") or "0"
    if value not in ("0", "1"):
        raise ValueError("HPU_HARDLINK_STAGING must be 0 or 1")
    return value == "1"


def link_or_copy_immutable(source, destination):
    """只写全新目标；绝不覆盖可能与历史交付共享的inode。"""
    source, destination = Path(source), Path(destination)
    info = source.lstat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError(f"expected a plain immutable file: {source}")
    if os.path.lexists(destination):
        raise FileExistsError(f"refusing to overwrite staged file: {destination}")
    if info.st_size >= LARGE_FILE_BYTES:
        try:
            os.link(source, destination, follow_symlinks=False)
            return str(destination)
        except OSError as error:
            if error.errno != errno.EXDEV:
                raise
    return shutil.copy2(source, destination)


def immutable_copy_function():
    return link_or_copy_immutable if hardlink_staging_enabled() else shutil.copy2


def prepare_artifact_directory(value):
    """移动上一轮完整artifact并新建目录，保留全部旧文件及其已发布硬链接。"""
    artifact = Path(value).absolute()
    if artifact.name != "artifact" or artifact.is_symlink():
        raise ValueError("expected a plain directory named artifact")
    if artifact.exists() and not artifact.is_dir():
        raise ValueError(f"artifact is not a directory: {artifact}")
    artifact.parent.mkdir(parents=True, exist_ok=True)
    previous = None
    if artifact.exists():
        holder = Path(tempfile.mkdtemp(prefix=".artifact-previous-", dir=artifact.parent))
        previous = holder / "artifact"
        artifact.rename(previous)
    artifact.mkdir()
    return previous


def discard_fixture_object(object_directory, test_root, elf, binary):
    """链接完成后，只释放本case可由原始bin重建的单个数据对象。"""
    object_directory = Path(object_directory).absolute()
    test_root = Path(test_root).absolute()
    elf, binary = Path(elf).absolute(), Path(binary).absolute()
    if (elf.suffix != ".elf" or binary != elf.with_suffix(".bin") or
            object_directory.name != elf.stem):
        raise ValueError("fixture cleanup requires matching case object directory and ELF/BIN")
    for product in (elf, binary):
        if product.is_symlink() or not product.is_file() or product.stat().st_size == 0:
            raise ValueError(f"fixture cleanup requires a nonempty plain product: {product}")
    if object_directory.is_symlink() or not object_directory.is_dir():
        raise ValueError("fixture cleanup requires a plain case object directory")
    # Makefile.compile将绝对源码路径接在DST_DIR后，不能用Path直接拼绝对路径。
    relative = Path(*test_root.parts[1:]) / "src/common/it_application_fixture.o"
    candidate = object_directory
    for part in relative.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise ValueError(f"fixture cleanup refuses a symlink: {candidate}")
    if not candidate.exists():
        return None
    if (not candidate.resolve().is_relative_to(object_directory.resolve()) or
            not stat.S_ISREG(candidate.stat().st_mode)):
        raise ValueError(f"fixture cleanup target is not a plain case object: {candidate}")
    size = candidate.stat().st_size
    candidate.unlink()  # 一次只处理这一条明确路径；原始bin、ELF和其它对象均保留。
    return candidate, size


def reuse_provenance(source_artifact, target_artifact, revision, log_level):
    """静默构建复用本轮已验证普通artifact；最终ELF仍必须通过validate-build。"""
    if not hardlink_staging_enabled() or log_level != 0:
        raise ValueError("provenance reuse requires hardlink staging and log_level=0")
    source, target = Path(source_artifact).absolute(), Path(target_artifact).absolute()
    for artifact in (source, target):
        if artifact.name != "artifact" or artifact.is_symlink() or not artifact.is_dir():
            raise ValueError(f"expected a plain artifact directory: {artifact}")
    source, target = source.resolve(), target.resolve()
    if source == target or source.is_relative_to(target) or target.is_relative_to(source):
        raise ValueError("source and target artifact directories must not overlap")
    for path in (source / "CASE_MANIFEST.tsv", target / "CASE_MANIFEST.tsv", source / "MANIFEST.txt"):
        if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"missing plain artifact manifest: {path}")
    if (source / "CASE_MANIFEST.tsv").read_bytes() != (target / "CASE_MANIFEST.tsv").read_bytes():
        raise ValueError("normal and silent CASE_MANIFEST.tsv differ")
    metadata = {}
    for line in (source / "MANIFEST.txt").read_text().splitlines():
        key, separator, value = line.partition("=")
        if not separator or not key or key in metadata:
            raise ValueError("invalid normal artifact manifest")
        metadata[key] = value
    if metadata.get("log_level") != "1" or metadata.get("revision") != revision:
        raise ValueError("provenance source must be normal log_level=1 at current revision")
    provenance, destination = source / "provenance", target / "provenance"
    if provenance.is_symlink() or not provenance.is_dir():
        raise ValueError("provenance must be a plain directory")
    if os.path.lexists(destination):
        raise FileExistsError("refusing to overwrite target provenance")
    for directory, names, files in os.walk(provenance, followlinks=False):
        for name in names + files:
            path = Path(directory, name)
            mode = path.lstat().st_mode
            if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise ValueError(f"provenance contains a symlink or special file: {path}")
    shutil.copytree(provenance, destination, copy_function=immutable_copy_function())
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--fresh-artifact", type=Path)
    action.add_argument("--discard-fixture-object", type=Path)
    action.add_argument("--reuse-provenance", type=Path)
    parser.add_argument("--test-root", type=Path)
    parser.add_argument("--elf", type=Path)
    parser.add_argument("--bin", type=Path)
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--revision")
    parser.add_argument("--log-level", type=int, choices=(0, 1, 2))
    args = parser.parse_args()
    if not hardlink_staging_enabled():
        parser.error("staging maintenance requires HPU_HARDLINK_STAGING=1")
    if args.fresh_artifact is not None:
        previous = prepare_artifact_directory(args.fresh_artifact)
        if previous is not None:
            print(f"[hputest] previous artifact preserved: {previous}")
    elif args.discard_fixture_object is not None:
        if None in (args.test_root, args.elf, args.bin):
            parser.error("fixture cleanup requires --test-root, --elf and --bin")
        discarded = discard_fixture_object(args.discard_fixture_object, args.test_root,
                                           args.elf, args.bin)
        if discarded is not None:
            path, size = discarded
            print(f"[hputest] released rebuildable fixture object ({size} bytes): {path}")
    else:
        if None in (args.artifact, args.revision, args.log_level):
            parser.error("provenance reuse requires --artifact, --revision and --log-level")
        destination = reuse_provenance(args.reuse_provenance, args.artifact, args.revision, args.log_level)
        print(f"[hputest] reused validated normal provenance: {destination}")


if __name__ == "__main__":
    main()
