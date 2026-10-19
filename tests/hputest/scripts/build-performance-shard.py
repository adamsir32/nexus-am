#!/usr/bin/env python3
"""编译并校验一个07性能分片；普通/静默共用本次已校验的producer数据。"""

import argparse
import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import case_catalog
from immutable_staging import discard_fixture_object


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[1]
INDEX_FIELDS = (
    "case_id", "variant", "degree", "level", "metric", "memory_base",
    "minimum_ram_bytes", "program_stem", "source", "elf", "bin",
    "disassembly", "build_status",
)
TEXT_EXTENSIONS = {".c", ".h", ".S", ".asm", ".inst32", ".cmd26", ".json",
                   ".csv", ".tsv", ".log", ".txt", ".md", ".conf"}
EMBEDDED_FILES = ("application_window.u32.bin", "application_golden.u32.bin",
                  "application_writable.u8.bin")


def run(command, **kwargs):
    return subprocess.run(command, check=True, **kwargs)


def selection(scope):
    if not scope.startswith("performance:"):
        raise ValueError("a performance:N:baseline|l16-SCHEME scope is required")
    selected = case_catalog.select_cases(scope)
    catalog = {row["case_id"]: row for row in case_catalog.rows("perf-cases.tsv")}
    result = []
    for case in selected:
        identity = case["case_id"]
        if identity not in catalog or case["qualifier"] != "software-self-check":
            raise ValueError(f"non-performance/unqualified case in shard: {identity}")
        row = dict(catalog[identity])
        if case["source"] != row["source"] or not (ROOT / row["source"]).is_file():
            raise ValueError(f"source/catalog mismatch: {identity}")
        result.append(row)
    if not result or len({row["case_id"] for row in result}) != len(result):
        raise ValueError("empty or duplicate performance selection")
    return result


def prepare_output(output, generated):
    """只接受新的专用目录；失败产物保留供定位，不能覆盖之前的交付。"""
    output = Path(output).absolute()
    if output.is_symlink():
        raise ValueError("output root cannot be a symlink")
    output = output.resolve()
    generated = Path(generated).resolve()
    if output in (ROOT, REPOSITORY, Path.home(), Path("/")) or \
            output in ROOT.parents or output == generated or \
            output in generated.parents or generated in output.parents:
        raise ValueError("output must be a dedicated directory separate from source/generated data")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError(f"refusing nonempty/non-directory output: {output}")
    output.mkdir(parents=True, exist_ok=True)
    return output


def pinned_revisions():
    revisions = {}
    for name in ("inline-asm", "hpu-applications"):
        relative = f"tests/hputest/third_party/{name}"
        commit = subprocess.check_output(
            ["git", "-C", str(REPOSITORY / relative), "rev-parse", "HEAD"], text=True).strip()
        record = subprocess.check_output(
            ["git", "-C", str(REPOSITORY), "ls-files", "-s", "--", relative], text=True).split()
        if len(record) < 2 or record[:2] != ["160000", commit]:
            raise ValueError(f"{name} checkout differs from the AM gitlink")
        revisions[name] = commit
    revisions["nexus-am"] = subprocess.check_output(
        ["git", "-C", str(REPOSITORY), "rev-parse", "HEAD"], text=True).strip()
    return revisions


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def delivery_parameters(directory, row):
    if row["delivery"] == "large-data":
        relative = "PARAMETERS.json"
    elif (directory / "FIXTURE_PARAMETERS.json").is_file():
        relative = "FIXTURE_PARAMETERS.json"
    else:
        relative = "upstream/metadata/parameters.json"
    parameters = read_json(directory / relative)
    if parameters.get("degree", parameters.get("poly_modulus_degree")) != int(row["degree"]):
        raise ValueError(f"parameter degree differs from catalog: {row['case_id']}")
    if row["delivery"] == "application-data":
        count = parameters.get("Q_rns_count")
        if count is None:
            count = len(parameters.get("levels", [{}])[0].get("moduli", []))
        if count != int(row["level"]):
            raise ValueError(f"parameter input level differs from catalog: {row['case_id']}")
    return dict(parameters, evidence_file=relative)


def validate_delivery(generated, row, revisions):
    stem = row["program_stem"]
    directory = generated / row["delivery"] / stem
    expected = revisions["inline-asm" if stem.startswith("auto_") else "hpu-applications"]
    required = [f"{stem}.{suffix}" for suffix in ("c", "h", "asm", "inst32", "cmd26")]
    required += [f"{stem}_perf.c", f"{stem}_perf.h", "application_layout.h",
                 "dma_relocation_manifest.csv", "PROGRAM_MODEL.log", "PERF_ADAPTATION.json"]
    required += list(EMBEDDED_FILES)
    for name in required:
        path = directory / name
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"missing performance delivery: {path}")
    adaptation = read_json(directory / "PERF_ADAPTATION.json")
    if any(adaptation.get(key) != value for key, value in {
            "schema_version": 1, "metric": "issue_to_done_v2", "program_stem": stem,
            "instruction_words_unchanged": True, "preflight_emits_hpu": False,
            "timed_parameter_checks": False, "timed_trace_writes": False}.items()):
        raise ValueError(f"invalid performance adaptation: {stem}")
    if row["delivery"] == "application-data":
        if (directory / "producer_commit.txt").read_text().strip() != expected:
            raise ValueError(f"stale producer delivery: {stem}")
        model = read_json(directory / "AM_ADAPTATION.json")
        if model.get("producer_commit") != expected or model.get("program_model_matches_seal") is not True:
            raise ValueError(f"application model evidence missing: {stem}")
        parameters = delivery_parameters(directory, row)
        if stem.startswith("seal_"):
            oracle = read_json(directory / "SEAL_ORACLE.json")
            if oracle.get("status") != "PASS" or oracle.get("producer_commit") != expected or \
                    oracle.get("raw_word_mismatches") != 0 or \
                    oracle.get("comparison") != "all raw physical words":
                raise ValueError(f"SEAL oracle evidence invalid: {stem}")
    else:
        parameters = delivery_parameters(directory, row)
        if parameters.get("legacy_commit") != expected or parameters.get("model_verified") is not True:
            raise ValueError(f"operator model evidence missing: {stem}")
    return directory, parameters


def copy_evidence(directory, destination):
    """仅复制本分片的文本证据；原始镜像已嵌入并逐ELF对拍，不再随目录复制。"""
    copied = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_EXTENSIONS:
            continue
        relative = path.relative_to(directory)
        # 上游的原始文件校验清单不作为新的交付校验流程发布。
        if relative.as_posix() == "upstream/provenance/files.csv":
            continue
        if path.is_symlink():
            raise ValueError(f"unexpected evidence symlink: {path}")
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        copied.append(relative.as_posix())
    return copied


def build_variant(row, variant, directory, generated, package, output, arch, cross, jobs, elf_only, scope):
    identity = row["case_id"]
    quiet = variant == "silent"
    relative = Path(variant) / Path(row["source"]).relative_to("src").with_suffix("")
    if quiet:
        relative = relative.with_name(relative.name + "_silent")
    binary = package / relative
    elf, image, disassembly = (binary.with_suffix(ext) for ext in (".elf", ".bin", ".txt"))
    objects = output / "obj" / variant / binary.name
    binary.parent.mkdir(parents=True, exist_ok=True)
    objects.mkdir(parents=True)
    logs = package / "build-logs" / variant
    logs.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ, AM_HOME=str(REPOSITORY), CROSS_COMPILE=cross,
                       HPU_GENERATED_ROOT=str(generated), HPU_BUILD_SCOPE=scope)
    command = ["make", "-C", str(ROOT), "-f", "Makefile.case", f"-j{jobs}",
               f"ARCH={arch}", f"CROSS_COMPILE={cross}", "LINUX_GNU_TOOLCHAIN=1",
               f"CASE_SOURCE={ROOT / row['source']}", f"CASE_ID={identity}",
               f"HPU_DST_DIR={objects}/", f"BINARY={binary}", f"HPU_GENERATED_ROOT={generated}",
               "HPU_DUMP_RESULTS=0", f"HPU_LOG_LEVEL={0 if quiet else 1}", "mainargs=all"]
    print(f"[hputest][perf-shard][{variant}] {identity}", flush=True)
    with (logs / f"{identity}.log").open("w", encoding="utf-8") as log:
        run(command, env=environment, stdout=log, stderr=subprocess.STDOUT)
        run([cross + "strip", "--strip-debug", str(elf)], stdout=log, stderr=subprocess.STDOUT)
        run([cross + "objcopy", "-O", "binary", str(elf), str(image)],
            stdout=log, stderr=subprocess.STDOUT)
        # ELF/BIN已经固化镜像，只释放这个case的可重建大数据.o。
        discard_fixture_object(objects, ROOT, elf, image)
        with disassembly.open("w", encoding="utf-8") as stream:
            run([cross + "objdump", "-d", elf.name], cwd=elf.parent,
                stdout=stream, stderr=log)
        run([sys.executable, str(ROOT / "scripts/verify-operator-elf.py"),
             "--delivery", str(directory), "--elf", str(elf),
             "--disassembly", str(disassembly), "--operator", row["program_stem"]],
            env=environment, stdout=log, stderr=subprocess.STDOUT)
        run([sys.executable, str(ROOT / "scripts/verify-perf-elf.py"),
             "--disassembly", str(disassembly), "--operator", row["program_stem"]],
            env=environment, stdout=log, stderr=subprocess.STDOUT)
        if quiet:
            run([sys.executable, str(ROOT / "scripts/verify-silent-elf.py"),
                 "--elf", str(elf), "--cross-compile", cross],
                env=environment, stdout=log, stderr=subprocess.STDOUT)
    if elf_only:
        image.unlink()  # 本次新建且已用于释放fixture对象的确定路径。
    return dict({key: row[key] for key in INDEX_FIELDS if key in row},
                variant=variant, elf=relative.with_suffix(".elf").as_posix(),
                bin="" if elf_only else relative.with_suffix(".bin").as_posix(),
                disassembly=relative.with_suffix(".txt").as_posix(),
                build_status="BUILD_READY_NOT_IT_PASS")


def write_rows(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build(generated, output, scope, jobs=4, arch="riscv64-xs", cross="riscv64-linux-gnu-", elf_only=False):
    if jobs < 1 or arch != "riscv64-xs":
        raise ValueError("positive jobs and riscv64-xs architecture are required")
    cases = selection(scope)
    generated = Path(generated).resolve(strict=True)
    revisions = pinned_revisions()
    header = (generated / "include/hpu/inline_asm_mm_delivery.h").read_text()
    if f'#define HPU_INLINE_ASM_SOURCE_COMMIT "{revisions["inline-asm"]}"' not in header:
        raise ValueError("stale generated MM header")
    deliveries = {row["case_id"]: validate_delivery(generated, row, revisions) for row in cases}
    for tool in ("make", cross + "gcc", cross + "strip", cross + "objcopy", cross + "objdump", cross + "nm"):
        if shutil.which(tool) is None:
            raise ValueError(f"missing build tool: {tool}")
    output = prepare_output(output, generated)
    staging = Path(tempfile.mkdtemp(prefix=".release-staging-", dir=output))
    package = staging / "hputest"
    package.mkdir()
    indexes, parameters = [], []
    try:
        for row in cases:
            directory, fixture_parameters = deliveries[row["case_id"]]
            for variant in ("normal", "silent"):
                indexes.append(build_variant(row, variant, directory, generated, package, output,
                                             arch, cross, jobs, elf_only, scope))
            evidence = Path("provenance") / row["delivery"] / row["program_stem"]
            copy_evidence(directory, package / evidence)
            parameters.append(dict(row, fixture_parameters=fixture_parameters,
                                   evidence=evidence.as_posix(),
                                   embedded_bytes={name: (directory / name).stat().st_size
                                                   for name in EMBEDDED_FILES}))
        write_rows(package / "INDEX.tsv", indexes, INDEX_FIELDS)
        write_rows(package / "PERFORMANCE.tsv", cases, list(cases[0]))
        testplan = package / "provenance/testplan"
        testplan.mkdir(parents=True, exist_ok=True)
        write_rows(testplan / "perf-cases.tsv", cases, list(cases[0]))
        shutil.copy2(ROOT / "perf-migration.tsv", testplan / "perf-migration.tsv")
        (package / "PARAMETERS.json").write_text(json.dumps(parameters, ensure_ascii=False, indent=2) + "\n")
        tools = package / "tools"
        tools.mkdir()
        shutil.copy2(ROOT / "scripts/parse-perf-results.py", tools / "parse-perf-results.py")
        shutil.copy2(ROOT / "docs/N65536_PERFORMANCE.md", package / "PERFORMANCE.md")
        metadata = {
            "format": "hpu-performance-shard-v1", "scope": scope, "revision": revisions["nexus-am"],
            "inline_asm_commit": revisions["inline-asm"], "hpu_applications_commit": revisions["hpu-applications"],
            "arch": arch, "metric": "issue_to_done_v2", "case_count": len(cases),
            "variant_count": len(indexes), "variants": "normal,silent", "bin_included": int(not elf_only),
            "qualification": "BUILD_READY_NOT_IT_PASS", "golden_backend": "inline-asm/modified-SEAL",
            "raw_provenance_bins": "omitted-embedded-and-verified-in-each-elf",
        }
        (package / "MANIFEST.txt").write_text("".join(f"{key}={value}\n" for key, value in metadata.items()))
        (package / "README.md").write_text(
            f"# HPU性能分片\n\n本包范围：`{scope}`，{len(cases)}个用例，各有normal/silent两个版本。\n\n"
            "`INDEX.tsv`列出完整用例名、N、输入level、内存要求和实际文件路径；"
            "`PARAMETERS.json`保留同批Fixture的实际Q/P及其它参数。\n\n"
            "normal保留精简UART及cycle输出，silent关闭UART并保留全部指令和自检。"
            "每项已检查实际ELF中的HPU指令、输入/golden/guard镜像及计时边界；静默版另检查UART路径。"
            "构建校验不代表IT/VCS/FPGA运行通过。\n\n"
            "level=16使用窗口0xc0000000且模拟RAM至少2GiB；其余07使用0x90000000且至少512MiB。"
            "计时口径为issue_to_done_v2，参数预检查在计时外；不同N/level/版本分别统计。\n\n"
            "provenance保留此分片的producer源码、指令、参数、布局、oracle及软件模型证据。"
            "为控制下载体积，不再重复原始大bin；window、golden和write-mask已经嵌入ELF并逐字节核对。"
            "保留的upstream元数据用于追溯，不是可以重新运行包验证器的完整上游目录。\n\n"
            + ("本地elf-only构建：保留ELF和反汇编，未发布BIN。\n" if elf_only else "每项提供ELF、BIN和反汇编TXT。\n"),
            encoding="utf-8")
        staging.rename(output / "release")
    except Exception:
        print(f"Incomplete performance shard preserved for diagnosis: {staging}", file=sys.stderr)
        raise
    print(f"[hputest] performance shard validated: {len(cases)} cases x 2 variants; {output / 'release'}", flush=True)
    return output / "release"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated", type=Path, default=Path(os.environ.get("HPU_GENERATED_ROOT", ROOT / "build/generated")))
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--scope", default=os.environ.get("HPU_BUILD_SCOPE", ""))
    parser.add_argument("--jobs", type=int, default=int(os.environ.get("JOBS", "4")))
    parser.add_argument("--arch", default=os.environ.get("ARCH", "riscv64-xs"), choices=("riscv64-xs",))
    parser.add_argument("--cross-compile", default=os.environ.get("CROSS_COMPILE", "riscv64-linux-gnu-"))
    parser.add_argument("--elf-only", action="store_true", help="仅供本地减少产物占用；CI交付仍须包含BIN")
    args = parser.parse_args()
    try:
        build(args.generated, args.output_root, args.scope, args.jobs, args.arch, args.cross_compile, args.elf_only)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"performance shard failed: {error}\n")


if __name__ == "__main__":
    main()
