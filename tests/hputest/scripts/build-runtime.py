#!/usr/bin/env python3
"""构建一个00～07分组运行包；默认仅optimized/minimal ELF与BIN。"""
import argparse
import csv
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from types import SimpleNamespace

import build as functional
import build_performance as performance
from import_package import import_package, read_json, require

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("group", "case_id", "producer", "elf", "bin", "degree", "level", "qualifier")


def run(command, **kwargs):
    subprocess.run([str(value) for value in command], check=True, **kwargs)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_catalog(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def selected(args, case_id):
    return (args.group is None or case_id[:2] == args.group) and \
        (args.case is None or case_id == args.case)


def source_snapshot(paths, base):
    return {path.relative_to(base).as_posix(): path.read_text(encoding="utf-8")
            for path in sorted(set(paths))}


def native_sources(spec):
    paths = [ROOT / "tools/operator_perf/CMakeLists.txt"]
    if spec.get("kind") == "instruction":
        paths.append(ROOT / "tools/instruction_cases/generator.cpp")
        paths.append(ROOT / "runtime/it_stage_reference.c")
    else:
        paths.append(ROOT / "tools/common/fixture.hpp")
        if spec["case_id"].startswith("07_"):
            paths.append(ROOT / "tools/operator_perf/generator.cpp")
        elif spec.get("profile") != "application":
            paths.extend(ROOT / "tools/group_cases" / name for name in ("generator.cpp", "composite.cpp"))
    return paths

def native_recipe(spec):
    return source_snapshot(native_sources(spec), ROOT.parents[1])


def target_recipe(args, low_specs, groups, perf):
    """只记录参与本次生成/接收/目标程序的源码，不把README或测试纳入缓存合同。"""
    baseline = args.am_home / "tests/hputest"
    paths = [args.am_home / name for name in ("Makefile.app", "Makefile.lib", "am/Makefile",
             "am/arch/riscv64-xs.mk", "am/arch/isa/riscv64.mk", "libs/klib/Makefile")]
    for directory in (args.am_home / "am/src/xs", args.am_home / "libs/klib/src"):
        paths.extend(path for path in directory.rglob("*")
                     if path.is_file() and path.suffix in (".c", ".h", ".S", ".ld"))
    paths.extend((args.am_home / "am/include").glob("*.h"))
    paths.append(args.am_home / "am/include/arch/riscv64-xs.h")
    paths.extend((args.am_home / "libs/klib/include").glob("*.h"))
    paths.extend((baseline / "include").rglob("*.h"))
    if low_specs:
        paths.extend(baseline / row["source"] for row in low_specs if row.get("source"))
        paths.extend(baseline / name for name in ("Makefile.case", "scripts/build-lowlevel.py",
                     "scripts/prepare-lowlevel.py", "src/common/hpu_rns_fixture.S",
                     "src/common/hpu_mm_fixture.S", "src/common/hpu_irq.c", "src/common/it_stage_twiddle.S"))
        paths.extend((baseline / "runtime").glob("*.c"))
    if groups or perf:
        paths.extend(ROOT / name for name in ("Makefile.native.case", "scripts/import_package.py", "scripts/performance_adapter.py", "runtime/native_case.c",
                     "runtime/native/fixture.S", "runtime/native/image.c", "runtime/native/wait.c", "runtime/native/check.c"))
        paths.extend((ROOT / "include").glob("*.h"))
        for row in groups + perf:
            paths.append(ROOT / row["source"])
            paths.extend(native_sources(row))
    if groups:
        paths.append(ROOT / "scripts/build.py")
    if perf:
        paths.extend(ROOT / name for name in ("scripts/build_performance.py", "scripts/performance_adapter.py",
                                             "runtime/native/performance.c"))
        paths.append(baseline / "runtime/it_perf.c")
    return source_snapshot(paths, args.am_home)


def build_request(args, low_specs, groups, perf):
    return {"schema_version": 1, "producer_commit": read_json(ROOT / "producer.json")["commit"],
            "am_home": str(args.am_home), "producer": str(args.producer),
            "native_build": str(args.native_build),
            "arch": args.arch, "cross": args.cross, "wait_cycles": args.wait_cycles,
            "suite": getattr(args, "suite", "default"), "variant": getattr(args, "variant", "optimized"),
            "log_level": getattr(args, "log_level", 1),
            "reuse_native_from": str(args.reuse_native_from) if getattr(args, "reuse_native_from", None) else None,
            "source_recipe": target_recipe(args, low_specs, groups, perf),
            "cases": [{"kind": "lowlevel", **row} for row in low_specs] +
                     [dict(row) for row in groups] +
                     [{"kind": "performance", **row} for row in perf]}


def prepare_export(args, low_specs, groups, perf):
    """恢复只接受同一清单和构建合同；既有运行文件仍须在本轮重新验证。"""
    require(not (args.output / "hpu.zip").exists() and not (args.output / "hpu.zip").is_symlink(),
            "运行包已存在，请使用新的运行导出目录")
    request = build_request(args, low_specs, groups, perf)
    marker = args.output / "RUNTIME_BUILD_REQUEST.json"
    if args.resume:
        require(marker.is_file() and not marker.is_symlink() and read_json(marker) == request,
                "resume的清单、producer或构建参数不同，请使用新的运行导出目录")
    else:
        require(not marker.exists() and not marker.is_symlink() and
                not (args.output / "runtime").exists() and not (args.output / "runtime").is_symlink() and
                not (args.output / "runtime-cases.tsv").exists(),
                "请使用新的运行导出目录，或显式使用--resume恢复同一任务")
        with marker.open("x") as stream:
            json.dump(request, stream, indent=2)
            stream.write("\n")
    runtime = args.output / "runtime"
    expected = {runtime / row["case_id"][:2] / (row["case_id"] + extension)
                for row in low_specs + groups + perf for extension in (".elf", ".bin")}
    if runtime.exists() or runtime.is_symlink():
        require(runtime.is_dir() and not runtime.is_symlink(), "runtime必须是普通目录")
        for path in runtime.rglob("*"):
            require(not path.is_symlink() and (path.is_dir() or path.is_file()),
                    f"runtime含软链或特殊文件：{path}")
            require(path.is_dir() or path in expected, f"runtime含清单外文件：{path}")
        for row in low_specs + groups + perf:
            stem = runtime / row["case_id"][:2] / row["case_id"]
            require(Path(str(stem) + ".elf").exists() == Path(str(stem) + ".bin").exists(),
                    f"resume需要完整ELF+BIN，不能复用半成品：{stem}")


def same_bytes(left, right):
    if left.stat().st_size != right.stat().st_size:
        return False
    with left.open("rb") as first, right.open("rb") as second:
        while True:
            block = first.read(1024 * 1024)
            if block != second.read(1024 * 1024):
                return False
            if not block:
                return True


def reuse_file(root, relative):
    """复用入口只读已完成交付的明确文件，拒绝软链、越界和空产物。"""
    path = Path(relative)
    require(not path.is_absolute() and ".." not in path.parts, "复用文件越出源交付")
    current = root
    for part in path.parts:
        current /= part
        require(not current.is_symlink(), f"复用路径包含软链：{current}")
    require(current.is_file() and current.stat().st_size > 0, f"复用文件缺失或为空：{current}")
    return current


def prepare_native_reuse(args, groups, perf):
    """只复用目标源码和参数完全相同的native组件；低层变更仍必须重新构建。"""
    source = getattr(args, "reuse_native_from", None)
    if source is None:
        return None
    require(groups or perf, "--reuse-native-from不能复用低层用例")
    require(source.is_dir() and not source.is_symlink() and source != args.output and
            not args.output.is_relative_to(source) and not source.is_relative_to(args.output),
            "复用源和新输出必须是互不重叠的独立目录")
    old = read_json(reuse_file(source, "RUNTIME_BUILD_REQUEST.json"))
    reuse_file(source, "hpu.zip")
    current = build_request(args, [], groups, perf)
    fields = ("schema_version", "producer_commit", "am_home", "producer", "native_build", "arch", "cross",
              "wait_cycles", "suite", "variant", "log_level")
    require(all(old.get(key) == current[key] for key in fields),
            "native复用的producer或构建参数不同")
    require(functional.output(["git", "-C", args.producer, "rev-parse", "HEAD"]) == current["producer_commit"] and
            not functional.output(["git", "-C", args.producer, "status", "--porcelain"]),
            "native复用要求当前producer固定提交且工作树干净")
    old_recipe = old.get("source_recipe", {})
    # 这些目录由target_recipe动态枚举；旧版存在、当前已删除的公共头/源也必须使复用失效。
    shared = ("am/src/xs/", "libs/klib/src/", "am/include/", "libs/klib/include/", "tests/hputest/include/")
    old_component = {name: content for name, content in old_recipe.items()
                     if name in current["source_recipe"] or name.startswith(shared)}
    require(set(old_component) == set(current["source_recipe"]), "native组件依赖集合不同，存在新增或删除的共享源码")
    for name, content in current["source_recipe"].items():
        require(old_recipe.get(name) == content, f"native组件源码不同：{name}")
    old_cases = old.get("cases", [])
    require(isinstance(old_cases, list) and len({row["case_id"] for row in old_cases}) == len(old_cases),
            "复用源请求清单重复或无效")
    by_id = {row["case_id"]: row for row in old_cases}
    catalog = read_catalog(reuse_file(source, "runtime-cases.tsv"))
    require(len(catalog) == len(by_id) and {row["case_id"] for row in catalog} == set(by_id) and
            all(set(row) == set(FIELDS) for row in catalog), "复用源不是完整交付清单")
    catalog = {row["case_id"]: row for row in catalog}
    for spec in groups + perf:
        case_id = spec["case_id"]
        require(spec["kind"] in ("instruction", "native", "performance") and
                re.fullmatch(r"0[3-7]_\d{2,3}_[a-z0-9_]+", case_id) is not None and
                by_id.get(case_id) == spec, f"native复用的用例参数不同：{case_id}")
        expected = dict(group=case_id[:2], case_id=case_id, producer="runtime",
                        elf=f"{case_id[:2]}/{case_id}.elf", bin=f"{case_id[:2]}/{case_id}.bin",
                        degree=str(spec["degree"]), level=str(spec["level"]),
                        qualifier=spec.get("qualifier", "software-self-check"))
        require(catalog[case_id] == expected, f"native复用的运行清单参数不同：{case_id}")
    return {"source": source, "producer_commit": current["producer_commit"]}


def reuse_native_case(args, spec, plan):
    """重验原生包、实际ELF与嵌入数据，逐字一致后仅复制ELF/BIN，不重新编译。"""
    require(spec["kind"] in ("instruction", "native", "performance"), "禁止复用低层ELF")
    source, case_id = plan["source"], spec["case_id"]
    is_perf = spec["kind"] == "performance"
    variant = getattr(args, "variant", "optimized")
    mode = "silent" if getattr(args, "log_level", 1) == 0 else "minimal"
    category = "performance" if is_perf else "functional"
    selected_spec = {**spec, "variant": variant} if is_perf else spec
    package = source / "packages" / category / case_id
    if is_perf:
        performance.validate_fixture(reuse_file(source, f"packages/performance/{case_id}/{variant}/PERF_FIXTURE.json"),
                                     selected_spec, plan["producer_commit"])
        package /= variant + "/upstream"
    reuse_file(source, (package.relative_to(source) / "package.json").as_posix())
    data = source / "generated" / category / case_id
    reuse_file(source, (data.relative_to(source) / "delivery.json").as_posix())
    # verify_existing只比较既有文件，不改写源交付中的数据、golden或receipt。
    meta = import_package(package, data, selected_spec, plan["producer_commit"], verify_existing=True)
    artifact = (Path("performance-build/artifact") / variant / mode if is_perf else
                Path("functional-build/artifact") / mode) / case_id / case_id
    elf, binary = (reuse_file(source, str(artifact) + suffix) for suffix in (".elf", ".bin"))
    for suffix, original in ((".elf", elf), (".bin", binary)):
        published = reuse_file(source, f"runtime/{case_id[:2]}/{case_id}{suffix}")
        require(same_bytes(published, original), f"复用运行文件与已验证原产物不同：{case_id}{suffix}")
    if is_perf:
        disassembly = reuse_file(source, str(artifact) + ".txt")
        require(disassembly.read_bytes() == subprocess.check_output([args.cross + "objdump", "-d", elf]),
                f"复用反汇编与实际ELF不同：{case_id}")
        performance.verify_elf(elf, disassembly, data, meta, args.cross)
    else:
        actual = functional.verify_elf(elf, args.cross, meta)
        expected = [int(word, 2) for word in (data / (spec["program_stem"] + ".inst32")).read_text().split()]
        require(actual == expected, f"复用ELF机器字不同：{case_id}")
        performance.verify_embedded(elf, data, spec, args.cross)
    if mode == "silent":
        run([sys.executable, ROOT / "scripts/verify-silent-elf.py", "--elf", elf, "--cross-compile", args.cross])
    return stage_runtime(args, spec, elf, binary)


def catalog_specs(validate_sources=True):
    rows = read_catalog(ROOT / "cases.tsv")
    require(rows and len({row["case_id"] for row in rows}) == len(rows), "canonical清单为空或case_id重复")
    for row in rows:
        for key in ("degree", "level", "minimum_ram_bytes"):
            row[key] = int(row[key] or 0)
        require(row["kind"] in ("lowlevel", "instruction", "native", "performance") and
                row["suite"] in ("default", "api"), "清单kind/suite无效")
        source = Path(row["source"])
        require(not source.is_absolute() and ".." not in source.parts and
                (not validate_sources or (ROOT / source).is_file()),
                "清单source缺失或越出项目")
        require(0 <= row["degree"] <= 8192 and 0 <= row["level"] <= 4,
                "清单N/L超过当前交付范围")
    return rows


def filtered_specs(args):
    """列表与构建共用全部筛选条件，不维护第二份用例目录。"""
    return [row for row in catalog_specs(validate_sources=not getattr(args, "list", False))
            if selected(args, row["case_id"]) and
            (args.suite == "all" or row["suite"] == args.suite) and
            (getattr(args, "degree", None) is None or row["degree"] == args.degree) and
            (getattr(args, "level", None) is None or row["level"] == args.level) and
            (getattr(args, "scheme", None) is None or row["scheme"] == args.scheme)]


def group_specs():
    return [row for row in catalog_specs() if row["kind"] in ("instruction", "native")]


def perf_specs():
    return [row for row in catalog_specs() if row["kind"] == "performance"]

def prepare_native(args, groups, need_perf):
    pin = read_json(ROOT / "producer.json")["commit"]
    require(functional.output(["git", "-C", args.producer, "rev-parse", "HEAD"]) == pin,
            "producer不是当前固定提交")
    require(not functional.output(["git", "-C", args.producer, "status", "--porcelain"]),
            "producer必须干净，禁止混入本地编码修改")
    targets = {"hpu_validate_package"}
    for spec in groups:
        targets.add(spec["target"])
    if need_perf:
        targets.add("hpu_frontend_operator_generator")
    run(["cmake", "-S", ROOT / "tools/operator_perf", "-B", args.native_build,
         "-DINLINE_ASM_ROOT=" + str(args.producer), "-DCMAKE_BUILD_TYPE=Release"])
    run(["cmake", "--build", args.native_build, "--parallel", args.jobs, "--target", *sorted(targets)])
    return pin, args.native_build / "inline-asm/hpu_validate_package"


def ensure_package(args, spec, pin, command, directory):
    # 原生包有严格文件白名单，构建缓存标记只能放在包目录外。
    marker = directory.parent / (directory.name + ".request.json")
    request = {"producer_commit": pin, "case": spec, "generator_command": [str(v) for v in command],
               "source_recipe": native_recipe(spec)}
    if directory.exists():
        require(marker.is_file() and read_json(marker) == request,
                f"现有包不完整或参数不同，请换输出目录：{directory}")
        return
    directory.parent.mkdir(parents=True, exist_ok=True)
    with (args.output / "logs" / (spec["case_id"] + "-producer.log")).open("w") as log:
        run(command, stdout=log, stderr=subprocess.STDOUT)
    with marker.open("x") as stream:
        json.dump(request, stream, indent=2)
        stream.write("\n")


def stage_runtime(args, spec, elf, binfile):
    group, case_id = spec["case_id"][:2], spec["case_id"]
    destination = args.output / "runtime" / group
    destination.mkdir(parents=True, exist_ok=True)
    sources = (elf, binfile)
    targets = tuple(destination / (case_id + extension) for extension in (".elf", ".bin"))
    for path in sources:
        require(path.is_file() and not path.is_symlink() and path.stat().st_size > 0,
                f"已验证的运行文件缺失或为空：{path}")
    require(not any(path.is_symlink() for path in targets), "拒绝覆盖运行文件软链")
    if any(path.exists() for path in targets):
        require(args.resume and all(path.is_file() for path in targets) and
                all(same_bytes(source, target) for source, target in zip(sources, targets)),
                f"拒绝覆盖不同的运行文件或半成品：{case_id}")
    else:
        for source, target in zip(sources, targets):
            shutil.copyfile(source, target)
    return dict(group=group, case_id=case_id, producer="runtime", elf=f"{group}/{case_id}.elf",
                bin=f"{group}/{case_id}.bin", degree=spec["degree"], level=spec.get("level", ""),
                qualifier=spec.get("qualifier", "software-self-check"))


def build_functional(args, spec, pin, validator):
    source = args.output / "packages/functional" / spec["case_id"]
    if spec["profile"] == "application":
        command = [args.native_build / "inline-asm" / spec["target"],
                   "--degree", spec["degree"], "--emit-dir", source]
    elif spec["kind"] == "instruction":
        command = [args.native_build / spec["target"], spec["operation"], spec["degree"], spec["level"], source]
    else:
        command = [args.native_build / spec["target"], "ckks" if spec["scheme"] == "raw" else spec["scheme"], spec["operation"],
                   spec["degree"], spec["level"], spec["profile"], source]
    ensure_package(args, spec, pin, command, source)
    run([validator, source], stdout=subprocess.DEVNULL)
    data = args.output / "generated/functional" / spec["case_id"]
    meta = import_package(source, data, spec, pin, verify_existing=True)
    context = SimpleNamespace(**vars(args))
    context.output = args.output / "functional-build"
    context.packages = args.output / "packages/functional"
    log = args.output / "logs" / (spec["case_id"] + "-build.log")
    original_run = functional.run
    with log.open("w") as stream:
        functional.run = lambda cmd, **kwargs: run(cmd, stdout=stream, stderr=subprocess.STDOUT, **kwargs)
        try:
            functional.build_case(context, spec, data, meta, "silent" if getattr(args, "log_level", 1) == 0 else "minimal")
        finally:
            functional.run = original_run
    mode = "silent" if getattr(args, "log_level", 1) == 0 else "minimal"
    binary = context.output / "artifact" / mode / spec["case_id"] / spec["case_id"]
    # 功能包与性能包使用相同的只读嵌入镜像检查，日志不进入下载包。
    performance.verify_embedded(Path(str(binary) + ".elf"), data,
                                {"memory_base": "0x87000000", "minimum_ram_bytes": 268435456}, args.cross)
    return stage_runtime(args, spec, Path(str(binary) + ".elf"), Path(str(binary) + ".bin"))


def build_perf(args, spec, pin, validator):
    container = args.output / "packages/performance" / spec["case_id"]
    command = [args.native_build / "hpu_frontend_operator_generator", spec["scheme"], spec["operation"],
               spec["degree"], "baseline", container, *(["--optimized-only"] if getattr(args, "variant", "optimized") == "optimized" else [])]
    ensure_package(args, spec, pin, command, container)
    selected_spec = {**spec, "variant": getattr(args, "variant", "optimized")}
    source = container / selected_spec["variant"] / "upstream"
    performance.validate_fixture(container / selected_spec["variant"] / "PERF_FIXTURE.json", selected_spec, pin)
    run([validator, source], stdout=subprocess.DEVNULL)
    data = args.output / "generated/performance" / spec["case_id"]
    meta = import_package(source, data, selected_spec, pin, verify_existing=True)
    performance.perf_adapter().prepare(data, spec["program_stem"])
    context = SimpleNamespace(**vars(args))
    context.work = args.output / "performance-build"
    log = args.output / "logs" / (spec["case_id"] + "-build.log")
    original_run = performance.run
    with log.open("w") as stream:
        def logged_run(cmd, **kwargs):
            kwargs.setdefault("stdout", stream)
            kwargs.setdefault("stderr", subprocess.STDOUT)
            run(cmd, **kwargs)
        performance.run = logged_run
        try:
            result = performance.build_case(context, selected_spec, data, meta, "silent" if getattr(args, "log_level", 1) == 0 else "minimal")
        finally:
            performance.run = original_run
    return stage_runtime(args, spec, context.work / result["elf"], context.work / result["bin"])


def build_lowlevel(args, specs):
    low = load_module("build_lowlevel", args.am_home / "tests/hputest/scripts/build-lowlevel.py")
    # 低层构建器会写自己的runtime目录；先在独立工作区完成字码校验，
    # 再由stage_runtime比较或交付，不能在resume时提前覆盖已交付文件。
    context = SimpleNamespace(**vars(args))
    context.output = args.output / "lowlevel-build"
    context.generated = args.output / "lowlevel/generated"
    (context.output / "logs").mkdir(parents=True, exist_ok=True)
    allowed = low.prepare(context)
    rows = []
    for spec in specs:
        row, unused_count = low.build_case(context, spec, allowed)
        rows.append(stage_runtime(args, row, context.output / "runtime" / row["elf"],
                                  context.output / "runtime" / row["bin"]))
        print(f"[RUNTIME] {row['case_id']} ELF/BIN ready (RTL not run)", flush=True)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("am-home", "producer", "output", "native-build", "reuse-native-from"):
        parser.add_argument("--" + name, required=name in ("am-home", "producer", "output"),
                            type=lambda value: Path(value).resolve())
    parser.add_argument("--group", choices=[f"{n:02}" for n in range(8)])
    parser.add_argument("--case")
    parser.add_argument("--degree", choices=(128, 1024, 2048, 4096, 8192), type=int)
    parser.add_argument("--level", choices=(1, 2, 3, 4), type=int)
    parser.add_argument("--scheme", choices=("raw", "ckks", "bfv", "bgv"))
    parser.add_argument("--list", action="store_true", help="只读清单并显示筛选结果，不准备数据或创建输出")
    parser.add_argument("--suite", choices=("default", "api", "all"), default="default")
    parser.add_argument("--variant", choices=("optimized", "noopt"), default="optimized", help="只影响07资源调度")
    parser.add_argument("--log-level", choices=(0, 1), type=int, default=1)
    parser.add_argument("--resume", action="store_true",
                        help="仅恢复同一清单/pin/参数；本轮重新验证后只复用逐字相同的ELF+BIN")
    parser.add_argument("--jobs", default=4, type=int)
    parser.add_argument("--arch", default="riscv64-xs", choices=["riscv64-xs"])
    parser.add_argument("--cross", default="riscv64-linux-gnu-")
    parser.add_argument("--wait-cycles", default=25000000, type=int)
    args = parser.parse_args()
    require(args.jobs > 0 and 0 < args.wait_cycles < 1 << 63, "jobs/cycle budget不合法")
    roster = filtered_specs(args)
    require(roster, "筛选未命中已实现用例")
    if args.list:
        writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
        writer.writerow(("case_id", "N", "level", "scheme", "purpose"))
        writer.writerows((row["case_id"], row["degree"], row["level"], row["scheme"], row["purpose"])
                         for row in roster)
        return
    require(args.output != args.am_home and not args.output.is_relative_to(args.producer),
            "输出目录不能覆盖源码或producer")
    args.native_build = args.native_build or args.output / "native-build"
    low_specs = [row for row in roster if row["kind"] == "lowlevel"]
    groups = [row for row in roster if row["kind"] in ("instruction", "native")]
    perf = [row for row in roster if row["kind"] == "performance"]
    reuse = prepare_native_reuse(args, groups, perf)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "logs").mkdir(exist_ok=True)
    require(low_specs or groups or perf, "筛选未命中已实现用例")
    prepare_export(args, low_specs, groups, perf)
    rows = build_lowlevel(args, low_specs) if low_specs else []
    if reuse is not None:
        for spec in groups + perf:
            rows.append(reuse_native_case(args, spec, reuse))
            print(f"[RUNTIME][REUSE] {spec['case_id']} native包/ELF/嵌入数据/字节重验通过 (RTL not run)", flush=True)
    elif groups or perf:
        pin, validator = prepare_native(args, groups, bool(perf))
        for spec in groups:
            rows.append(build_functional(args, spec, pin, validator))
            print(f"[RUNTIME] {spec['case_id']} model/ELF/BIN ready (RTL not run)", flush=True)
        for spec in perf:
            rows.append(build_perf(args, spec, pin, validator))
            print(f"[RUNTIME] {spec['case_id']} model/ELF/BIN/cycle-boundary ready (RTL not run)", flush=True)
    rows.sort(key=lambda row: (row["group"], int(row["case_id"].split("_")[1])))
    catalog = args.output / "runtime-cases.tsv"
    if catalog.exists() or catalog.is_symlink():
        expected_rows = [{key: str(row.get(key, "")) for key in FIELDS} for row in rows]
        require(args.resume and not catalog.is_symlink() and read_catalog(catalog) == expected_rows,
                "已存在的运行清单与本轮验证结果不一致")
    else:
        with catalog.open("x", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t", lineterminator="\n", extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
    run([sys.executable, ROOT / "scripts/package-runtime.py", "--catalog", catalog,
         "--root", "runtime=" + str(args.output / "runtime"), "--check-tree", "--output", args.output / "hpu.zip"])
    print(f"{args.output / 'hpu.zip'}: {len(rows)} cases, ELF+BIN only; hardware not verified")


if __name__ == "__main__":
    main()
