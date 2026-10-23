#!/usr/bin/env python3
"""审计自有HPU清单、案例参数与本地引用；不遍历submodule或运行硬件。"""
import argparse
import ast
import collections
import csv
from pathlib import Path
import posixpath
import re
import subprocess


OWNED_ROOTS = ("tests/hputest/", "tests/hpu_frontend_workload/")
EXCLUDED_PARTS = {"third_party", "vendor", "external", "experiments"}
CASE_ID = re.compile(r"(0[0-7])_(\d{2,3})_([a-z][a-z0-9_]*)\Z")
CASE_SOURCE = re.compile(r"(?:0[0-7]_\d{2,3}_|HPU_IT_)", re.I)
SOURCE_SUFFIXES = {".c", ".cpp", ".h", ".hpp", ".S", ".sv", ".py", ".sh", ".mk"}
TEXT_SUFFIXES = SOURCE_SUFFIXES | {".md", ".tsv", ".json", ".txt", ".yml"}
LEGACY_MODULES = {"case_catalog", "program_adaptation", "program_encoding",
                  "immutable_staging", "hpu_opcode_mapping", "subtest_support"}
REDUCTIONS = {"modswitch", "mod_switch", "rescale", "mod_switch_to_next", "rescale_to_next"}


def owned(path):
    return path.startswith(OWNED_ROOTS) and not (set(Path(path).parts) & EXCLUDED_PARTS)


def tracked_files(repo):
    # 只检查索引中的自有文件；gitlink没有被展开，软件库的规模支持不属于IT案例。
    output = subprocess.check_output(["git", "-C", str(repo), "ls-files", "-z"], text=True)
    return {name for name in output.split("\0") if name and owned(name)
            and (repo / name).is_file() and not (repo / name).is_symlink()}


def integer(row, names, default=0):
    for name in names:
        value = row.get(name, "")
        if value not in (None, ""):
            return int(value)
    return default


def source_path(repo, root, raw):
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts or "\\" in raw:
        raise ValueError("source不是安全的项目相对路径")
    return path if raw.startswith("tests/") else root / path


def validate_catalogs(repo, root, catalogs, files):
    errors, rows, sources = [], [], collections.defaultdict(list)
    seen_ids, seen_semantics = set(), {}
    numbers, ordering = collections.defaultdict(list), {}
    for catalog in catalogs:
        with (repo / catalog).open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            if not {"case_id", "source"}.issubset(reader.fieldnames or ()):
                errors.append(f"{catalog}: 缺少case_id/source列")
                continue
            for line, row in enumerate(reader, 2):
                where = f"{catalog}:{line}"
                case_id = row["case_id"]
                match = CASE_ID.fullmatch(case_id)
                if not match:
                    errors.append(f"{where}: 非法case_id {case_id}")
                    continue
                group, number = match[1], int(match[2])
                if row.get("group", group) != group:
                    errors.append(f"{where}: group与case_id不一致")
                if case_id in seen_ids:
                    errors.append(f"{where}: 重复case_id {case_id}")
                seen_ids.add(case_id)
                numbers[group].append(number)
                try:
                    degree, level = integer(row, ("degree", "N")), integer(row, ("level", "L"))
                    if not 0 <= degree <= 8192 or not 0 <= level <= 4:
                        raise ValueError("N>8192或L>4，或参数为负")
                    if group in ("03", "04", "05"):
                        if degree not in (128, 1024, 2048, 4096, 8192) or not 1 <= level <= 4:
                            raise ValueError("03～05必须明确填写有效N和L")
                        key = (group, row.get("profile", ""))
                        current = (degree, level)
                        if key in ordering and current < ordering[key]:
                            errors.append(f"{where}: 同profile内N/L未按从小到大排序")
                        ordering[key] = current
                        if row.get("operation") in REDUCTIONS and level == 1:
                            errors.append(f"{where}: L1不能执行下一level降级操作")
                    source = source_path(repo, root, row["source"]).as_posix()
                except (ValueError, TypeError) as error:
                    errors.append(f"{where}: {error}")
                    continue
                if not owned(source) or source not in files:
                    errors.append(f"{where}: source不存在、未纳入索引或非自有源码 {source}")
                sources[source].append(case_id)
                # 多个参数用例允许共享同一薄wrapper；不能仅用source去重。
                semantic = (group, source, row.get("program_stem", ""), degree, level,
                            row.get("scheme", ""), row.get("operation", ""),
                            row.get("profile", ""), row.get("subcase", ""),
                            row.get("stage", ""), row.get("component", ""))
                if semantic in seen_semantics:
                    errors.append(f"{where}: 实际参数/程序重复 {seen_semantics[semantic]} 与 {case_id}")
                seen_semantics[semantic] = case_id
                rows.append(row)
    for group, sequence in numbers.items():
        if sorted(sequence) != list(range(1, len(sequence) + 1)):
            errors.append(f"{group}: 组内编号必须从01连续排列，不能缺号或重复")
        if sequence != sorted(sequence):
            errors.append(f"{group}: 清单编号未按数值升序排列")
    for name in files:
        path = Path(name)
        if path.suffix not in (".c", ".cpp", ".S") or not CASE_SOURCE.match(path.name):
            continue
        if name not in sources:
            errors.append(f"{name}: 留有未被canonical清单引用的案例源码")
        # 仅解释案例文件名的参数标签，不扫描普通架构/数学常数。
        for key, cap in (("n", 8192), ("l(?:evel)?", 4)):
            for match in re.finditer(r"(?:^|_)" + key + r"(\d+)(?=_|\.|$)", path.name, re.I):
                if int(match[1]) > cap:
                    errors.append(f"{name}: 案例文件名参数超过当前规模限制")
    return rows, sources, errors


def references(repo, files):
    """提取可证实的本地引用；不把动态输出文件或第三方include误判成丢失源码。"""
    edges, errors = collections.defaultdict(set), []
    by_name = collections.defaultdict(set)
    for name in files:
        by_name[Path(name).name].add(name)
    for name in files:
        path = Path(name)
        if path.suffix not in TEXT_SUFFIXES and not path.name.startswith("Makefile"):
            continue
        text = (repo / name).read_text(encoding="utf-8")
        tokens = re.findall(r"[A-Za-z0-9_./+-]+\.(?:py|sh|cpp|c|hpp|h|S|sv|tsv|json|md|mk|txt)", text)
        imports = []
        if path.suffix == ".py":
            try:
                tree = ast.parse(text)
            except SyntaxError as error:
                errors.append(f"{name}:{error.lineno}: Python语法错误")
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module.split(".")[0])
            for module in imports:
                local = (path.parent / (module + ".py")).as_posix()
                if local in files:
                    edges[name].add(local)
                elif module in LEGACY_MODULES:
                    errors.append(f"{name}: 引用已删除的旧本地模块 {module}")
        for token in tokens:
            token = token.rstrip(".")
            candidates = {posixpath.normpath(token),
                          posixpath.normpath((path.parent / token).as_posix())}
            if token.startswith("scripts/") or token.startswith("src/") or token.startswith("tools/"):
                candidates.update(prefix + token for prefix in OWNED_ROOTS)
            found = candidates & files
            if not found and len(by_name[Path(token).name]) == 1:
                found = by_name[Path(token).name]
            edges[name].update(found)
            # 只检查生产源码中明确的项目源码路径；测试的故意无效路径不作为真实引用。
            is_test = path.name.startswith(("test_", "test-")) or "test" in path.parts
            if owned(token) and Path(token).suffix in SOURCE_SUFFIXES and not is_test and token not in files:
                errors.append(f"{name}: 悬空项目源码引用 {token}")
    return edges, errors


def inventory(repo, root, files, catalogs, sources, edges):
    roots = {name for name in files if name in {str(root / "Makefile"), str(root / "Makefile.case"),
             str(root / "Makefile.native.case"), str(root / "scripts/build-runtime.py"),
             str(root / "producer.json"), *(str(path) for path in catalogs)}}
    roots.update(name for name in files if Path(name).name.startswith(("test_", "test-")))
    roots.update(sources)
    proofs = {name: name for name in roots}
    queue = collections.deque(sorted(roots))
    while queue:
        caller = queue.popleft()
        for target in sorted(edges[caller]):
            if target not in proofs:
                proofs[target] = proofs[caller] + " → " + target
                queue.append(target)
    rows = []
    for name in sorted(files):
        path = Path(name)
        if name in sources:
            purpose = "案例源码：" + ",".join(sources[name])
        elif path.name.startswith(("test_", "test-")):
            purpose = "独立主机验证入口；是否默认运行由CI/Makefile决定"
        elif path.suffix == ".md":
            purpose = "说明文档"
        elif path.suffix in (".tsv", ".json"):
            purpose = "清单/生产者元数据"
        elif path.name.startswith("Makefile") or path.name == "CMakeLists.txt":
            purpose = "构建入口/配置"
        else:
            purpose = "构建、接收、运行时或验证辅助源码"
        rows.append({"path": name, "purpose": purpose,
                     "reachable_from": proofs.get(name, "未由静态引用证明；需人工审核，不自动删除"),
                     "direct_references": ",".join(sorted(edges[name]))})
    return rows


def audit(repo, root, catalogs):
    files = tracked_files(repo)
    cases, sources, errors = validate_catalogs(repo, root, catalogs, files)
    edges, reference_errors = references(repo, files)
    report = inventory(repo, root, files, catalogs, sources, edges)
    return {"cases": cases, "files": report, "errors": errors + reference_errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--root", type=Path, default=Path("tests/hputest"))
    parser.add_argument("--catalog", type=Path, action="append")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = audit(args.repo.resolve(), args.root, args.catalog or [args.root / "cases.tsv"])
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=("path", "purpose", "reachable_from", "direct_references"),
                                    delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(result["files"])
    for error in result["errors"]:
        print(error)
    print(f"自有文件{len(result['files'])}项，案例{len(result['cases'])}项，问题{len(result['errors'])}项；不表示硬件通过。")
    return bool(result["errors"])


if __name__ == "__main__":
    raise SystemExit(main())
