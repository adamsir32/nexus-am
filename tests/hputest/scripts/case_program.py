"""逐用例源码旁的HPU发令文本必须与当前inline-asm原生包完全一致。"""
from pathlib import Path, PurePosixPath

from import_package import read_json, require


ROOT = Path(__file__).resolve().parents[1]


def plain_file(root, relative):
    name = PurePosixPath(relative)
    require(relative and not name.is_absolute() and ".." not in name.parts and
            "\\" not in relative and not any(ord(char) < 32 for char in relative),
            "用例程序路径必须是安全的相对路径")
    current = root
    for part in name.parts:
        current /= part
        require(not current.is_symlink(), f"用例程序不接受软链：{current}")
    require(current.is_file() and current.stat().st_size > 0,
            f"用例程序源码缺失或为空：{current}")
    return current


def case_program_path(spec):
    source = Path(spec["source"])
    require(source.suffix == ".c" and source.stem == spec["case_id"],
            "每个用例必须有与case_id同名的独立C源码")
    variant = spec.get("variant", "optimized")
    require(variant in ("optimized", "noopt"), "未知发令调度版本")
    require(variant == "optimized" or spec["kind"] == "performance",
            "noopt仅适用于07组性能用例")
    return source.with_suffix(".noopt.asm" if variant == "noopt" else ".asm")


def verify_case_program(package, spec):
    """不拼接/替换指令；不一致时停止构建，不能悄悄改写用户审阅的源码。"""
    manifest = read_json(plain_file(package, "package.json"))
    upstream = plain_file(package, manifest.get("program_asm", ""))
    checked_in = plain_file(ROOT, case_program_path(spec).as_posix())
    require(upstream.read_bytes() == checked_in.read_bytes(),
            f"{spec['case_id']}: 当前inline-asm发令序列与{checked_in.name}不同；"
            "请核对并显式更新该用例源码，不允许混用旧指令")
    return checked_in
