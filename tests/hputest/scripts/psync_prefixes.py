"""03_08可选PSYNC sidecar接收与逐入口ELF核对；不改变标准原生包。"""
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

from import_package import instruction_contract, read_rows, require, validate_dma
from performance_adapter import (instruction_words, resolved_spans,
                                 validate_fixed_entry)

ROOT = Path(__file__).resolve().parents[1]
CASE = "03_08_psync_l4_n1024"
STEM = "instruction_psync_l4_n1024"
NAMES = ("idle", "dma", "compute")
FLAGS = ("verified", "model_verified", "read_only_guard_verified")
MANIFEST_FIELDS = {"schema", "schema_version", "producer_commit", "base_program_stem",
                   "degree", "level", "source_format", "initial_output_poison",
                   *FLAGS, "hardware_verified", "prefixes"}
PREFIX_FIELDS = {"name", "entry", "asm_file", "source_file", "header_file", "words_file",
                 "expected_components", "instruction_count", "compared_output_words",
                 "unchanged_words", *FLAGS, "dma_spans"}


def is_psync_case(spec):
    return spec.get("case_id") == CASE and spec.get("kind") == "instruction" and spec.get("operation") == "psync"


def plain_file(root, relative):
    require(type(relative) is str and relative and "\\" not in relative and
            not any(ord(char) < 32 for char in relative), "unsafe PSYNC file path")
    name = PurePosixPath(relative)
    require(not name.is_absolute() and ".." not in name.parts and str(name) == relative,
            "unsafe PSYNC file path")
    current = root
    require(current.is_dir() and not current.is_symlink(), "PSYNC root must be a plain directory")
    for part in name.parts:
        current /= part
        require(not current.is_symlink(), "PSYNC files must not use symlinks")
    require(current.is_file(), "missing PSYNC file: " + relative)
    return current


def read_json(root, relative):
    return json.loads(plain_file(root, relative).read_text())


def csv_int(row, key):
    value = row[key]
    require(type(value) is str and re.fullmatch(r"[0-9]+", value) is not None, "invalid PSYNC CSV integer")
    return int(value)


def binary_words(path):
    lines = path.read_text().splitlines()
    require(bool(lines) and all(re.fullmatch(r"[01]{32}", line) is not None for line in lines),
            "PSYNC words_file must contain only 32-bit binary lines")
    words = [int(line, 2) for line in lines]
    require(words[-1] == 0x7000005b and words.count(0x7000005b) == 1 and
            all(word & 127 in (0x2b, 0x5b) for word in words), "PSYNC prefix must end in its unique PSYNC")
    return words


def prefix_header(stem, count):
    guard = "HPU_PROGRAM_" + stem.upper() + "_H"
    return (f"#ifndef {guard}\n#define {guard}\n\n#include <stddef.h>\n#include <stdint.h>\n\n"
            "#ifndef HPU_DMA_SPAN_T_DEFINED\n#define HPU_DMA_SPAN_T_DEFINED\n"
            "typedef struct hpu_dma_span {\n    uint32_t line_offset;\n    uint32_t line_count;\n"
            "} hpu_dma_span_t;\n#endif\n\n#ifdef __cplusplus\nextern \"C\" {\n#endif\n\n"
            f"enum {{ HPU_PROGRAM_{stem.upper()}_DMA_COUNT = {count} }};\n"
            f"int hpu_run_{stem}(void);\n\n#ifdef __cplusplus\n}}\n#endif\n\n#endif\n")


def validate_program(root, row, words):
    stem = STEM + "_" + row["name"]
    spans = [(item["line_offset"], item["line_count"]) for item in row["dma_spans"]]
    code = plain_file(root, row["source_file"]).read_text()
    require(instruction_words(code) == words and resolved_spans(code) == spans,
            "PSYNC fixed C/words/resolved spans differ")
    begin, end = validate_fixed_entry(code, stem, words, spans)
    expected = f'#include "{stem}.h"\n'
    if spans:
        expected += f"\nstatic const hpu_dma_span_t hpu_program_{stem}_resolved_spans[] = {{\n"
        expected += "".join(f"    {{ UINT32_C({first}), UINT32_C({count}) }},\n" for first, count in spans)
        expected += "};\n"
    expected += "\n/* Fixed spans validated at generation; x11 changes only with DMA length. */\n"
    require(code == expected + code[begin:end] + "\n", "unexpected code outside PSYNC fixed entry")
    require(plain_file(root, row["header_file"]).read_text() == prefix_header(stem, len(spans)),
            "PSYNC prefix header differs from its fixed-only declaration")
    snapshot = ROOT / "src/03_instructions" / (CASE + "." + row["name"] + ".asm")
    require(snapshot.is_file() and not snapshot.is_symlink() and
            plain_file(root, row["asm_file"]).read_bytes() == snapshot.read_bytes(),
            "PSYNC prefix ASM differs from its checked-in snapshot")


def base_contract(source, spec, pin):
    descriptor = read_json(source, "package.json")
    require(descriptor.get("schema") == "hpu-application-package" and descriptor.get("schema_version") == 1 and
            descriptor.get("case_name") == STEM and descriptor.get("scheme") == "ckks", "PSYNC base package identity differs")
    provenance = read_json(source, "provenance/build.json")
    require(provenance.get("commit") == pin and provenance.get("worktree_state") == "clean-at-configure",
            "PSYNC base producer revision/cleanliness differs")
    parameters = read_json(source, descriptor["parameters"])
    graph = read_json(source, descriptor["operation_graph"])
    moduli, _ = instruction_contract(spec, parameters, graph, read_json(source, descriptor["oracle_report"]))
    require(parameters.get("poly_modulus_degree") == 1024 and graph.get("component_count") == 2,
            "PSYNC base shape differs")
    allocations = read_rows(plain_file(source, descriptor["line_map"]))
    memory = read_rows(plain_file(source, descriptor["memory_manifest"]))
    fields = ("allocation_id", "kind", "read_only", "line_offset", "line_count", "payload_words", "padded_words", "initialization")
    require([{key: row[key] for key in fields} for row in allocations] ==
            [{key: row[key] for key in fields} for row in memory], "PSYNC base memory manifests differ")
    config = read_json(source, descriptor["memory_config"])
    used = config["used_lines"]
    require(type(used) is int and 0 < used == config["capacity_lines"] < 1 << 32, "invalid PSYNC base image capacity")
    words = binary_words(plain_file(source, descriptor["program_inst32"]))
    dma = read_rows(plain_file(source, descriptor["dma_relocation_manifest"]))
    validate_dma(words, dma, allocations, graph["operations"], used)
    require(len(words) == 39 and len(dma) == 21, "PSYNC base program must contain both four-RNS scenarios")
    golden = read_rows(plain_file(source, descriptor["golden_manifest"]))
    scenarios = graph["scenario_outputs"]
    require(len(golden) == len(scenarios) == 8, "PSYNC base output coverage differs")
    outputs = []
    removed = set()
    by_span = {(csv_int(row, "line_offset"), csv_int(row, "line_count")): row for row in allocations}
    dma_by_instruction = {csv_int(row, "instruction_index"): row for row in dma}
    for index, (scenario, row) in enumerate(zip(scenarios, golden)):
        component, modulus_id = index % 2, index // 2
        require(scenario.get("component") == component and scenario.get("modulus_id") == modulus_id and
                scenario.get("scenario") == ("psync/dma-prefix" if component == 0 else "psync/compute-prefix"),
                "PSYNC base scenario order differs")
        for key in ("component", "modulus_id", "modulus", "line_offset", "line_count"):
            require(type(scenario.get(key)) is int and scenario[key] == csv_int(row, key),
                    "PSYNC base scenario/golden fields differ")
        require(row["object_id"] == "step_0" and row["domain"] == "coefficient" and
                csv_int(row, "modulus") == moduli[modulus_id] and
                scenario.get("words") == csv_int(row, "payload_words") == csv_int(row, "padded_words") == 1024 and
                scenario["line_count"] == 16, "PSYNC base scenario/golden shape differs")
        allocation = by_span.get((scenario["line_offset"], scenario["line_count"]))
        require(allocation is not None and allocation["kind"] == "output" and allocation["read_only"] == "false",
                "PSYNC selected output must be a base output allocation")
        output = {**scenario, "output_index": index, "allocation_id": allocation["allocation_id"]}
        outputs.append(output)
        stores = [item for item in dma if item["allocation_id"] == allocation["allocation_id"] and
                  item["direction"] == "dstore" and csv_int(item, "line_offset") == scenario["line_offset"] and
                  csv_int(item, "line_count") == scenario["line_count"]]
        require(len(stores) == 1, "PSYNC base output has no unique DSTORE binding")
        if component == 0:
            store = csv_int(stores[0], "instruction_index")
            load = dma_by_instruction.get(store - 1)
            require(load is not None and load["direction"] == "dload" and load["object_slot"] == "0" and
                    stores[0]["object_slot"] == "0" and stores[0]["type_or_release"] == "1" and
                    load["line_count"] == stores[0]["line_count"], "PSYNC DMA pair must be adjacent load/store-release")
            removed.update((store - 1, store))
    require(len(removed) == 8, "PSYNC DMA prefix coverage differs")
    kept = {"idle": [len(words) - 1], "dma": sorted(removed) + [len(words) - 1],
            "compute": [index for index in range(len(words)) if index not in removed]}
    return used, words, dma_by_instruction, outputs, kept


def prepare_prefixes(source, dest_data, spec, pin, verify_existing=False):
    source, dest_data = Path(source), Path(dest_data)
    require(is_psync_case(spec) and spec.get("profile") == "instruction" and spec.get("scheme") == "raw" and
            type(spec.get("degree")) is int and spec["degree"] == 1024 and
            type(spec.get("level")) is int and spec["level"] == 4 and spec.get("program_stem") == STEM,
            "PSYNC prefixes only support 03_08 N1024/L4 instruction case")
    used, base_words, base_dma, outputs, kept = base_contract(source, spec, pin)
    sidecar = source.with_name(source.name + ".psync-prefixes")
    manifest = read_json(sidecar, "manifest.json")
    require(set(manifest) == MANIFEST_FIELDS and manifest.get("schema") == "hpu-psync-prefixes" and
            type(manifest.get("schema_version")) is int and manifest["schema_version"] == 1 and
            manifest.get("producer_commit") == pin and manifest.get("base_program_stem") == STEM and
            type(manifest.get("degree")) is int and manifest["degree"] == 1024 and
            type(manifest.get("level")) is int and manifest["level"] == 4 and
            type(manifest.get("initial_output_poison")) is int and manifest["initial_output_poison"] == 0xffffffff and
            manifest.get("source_format") == "upstream_fixed_entry_only" and
            all(manifest.get(key) is True for key in FLAGS) and manifest.get("hardware_verified") is False,
            "PSYNC sidecar schema/pin/shape/model contract differs")
    prefixes = manifest["prefixes"]
    require(type(prefixes) is list and len(prefixes) == 3 and
            [row.get("name") for row in prefixes] == list(NAMES), "PSYNC sidecar requires exactly idle/dma/compute")
    copies, result = {}, []
    for row in prefixes:
        name = row["name"]
        stem = STEM + "_" + name
        components = {"idle": [], "dma": [0], "compute": [1]}[name]
        require(set(row) == PREFIX_FIELDS and row.get("entry") == "hpu_run_" + stem and
                row.get("expected_components") == components and
                all(type(value) is int for value in row["expected_components"]) and
                all(row.get(key) is True for key in FLAGS),
                "PSYNC prefix identity/components/model contract differs")
        for key, extension in (("source_file", ".c"), ("header_file", ".h"),
                               ("asm_file", ".asm"), ("words_file", ".inst32")):
            require(row.get(key) == stem + extension, "PSYNC prefix filename differs")
            copies[row[key]] = plain_file(sidecar, row[key]).read_bytes()
        words = binary_words(plain_file(sidecar, row["words_file"]))
        require(words == [base_words[index] for index in kept[name]], "PSYNC prefix words differ from selected base instructions")
        require(type(row.get("instruction_count")) is int and row["instruction_count"] == len(words) and
                type(row.get("compared_output_words")) is int and row["compared_output_words"] == 4096 * len(components) and
                type(row.get("unchanged_words")) is int and row["unchanged_words"] == used * 64 - row["compared_output_words"],
                "PSYNC prefix model comparison coverage differs")
        spans = row["dma_spans"]
        expected_spans = []
        for new_index, old_index in enumerate(kept[name]):
            original = base_dma.get(old_index)
            if original:
                expected_spans.append(dict(instruction_index=new_index, allocation_id=original["allocation_id"],
                                           line_offset=csv_int(original, "line_offset"), line_count=csv_int(original, "line_count")))
        require(type(spans) is list and all(type(item) is dict and set(item) ==
                {"instruction_index", "allocation_id", "line_offset", "line_count"} and
                all(type(item[key]) is int for key in ("instruction_index", "line_offset", "line_count")) for item in spans) and
                spans == expected_spans, "PSYNC prefix DMA bindings differ from selected base allocations")
        validate_program(sidecar, row, words)
        selected = [output for output in outputs if output["component"] in components]
        result.append({**row, "program_stem": stem, "words": words, "dma_count": len(spans),
                       "selected_outputs": selected, "output_indices": [output["output_index"] for output in selected]})
    require({path.name for path in sidecar.iterdir()} == {"manifest.json", *copies} and
            all(path.is_file() and not path.is_symlink() for path in sidecar.iterdir()),
            "PSYNC sidecar file whitelist/symlink violation")
    meta = {**manifest, "schema": "hpu-psync-prefixes-received", "program_stem": STEM, "prefixes": result,
            "source_files": [row["source_file"] for row in result],
            "header_files": [row["header_file"] for row in result], "asm_snapshots_verified": True}
    copies["PSYNC_PREFIXES.json"] = (json.dumps(meta, indent=2) + "\n").encode()
    require(not dest_data.is_symlink() and (not dest_data.exists() or dest_data.is_dir()), "PSYNC data must be a plain directory")
    for name, data in copies.items():
        target = dest_data / name
        require(not verify_existing or target.is_file(), "cached PSYNC data missing: " + name)
        require(not target.is_symlink() and (not target.exists() or target.is_file() and target.read_bytes() == data),
                "refusing to overwrite different PSYNC data: " + name)
    if not verify_existing:
        dest_data.mkdir(parents=True, exist_ok=True)
        for name, data in copies.items():
            target = dest_data / name
            if not target.exists():
                with target.open("xb") as stream:
                    stream.write(data)
    return meta


def verify_prefix_elf(elf, data, meta, cross):
    elf, data = Path(elf), Path(data)
    saved = read_json(data, "PSYNC_PREFIXES.json")
    require(set(saved) == MANIFEST_FIELDS | {"program_stem", "source_files", "header_files", "asm_snapshots_verified"} and
            saved.get("schema") == "hpu-psync-prefixes-received" and
            type(saved.get("schema_version")) is int and saved["schema_version"] == 1 and
            saved.get("program_stem") == saved.get("base_program_stem") == meta.get("program_stem") == STEM and
            saved.get("producer_commit") == meta.get("producer_commit") and saved.get("degree") == 1024 and
            saved.get("level") == 4 and all(saved.get(key) is True for key in FLAGS) and
            saved.get("asm_snapshots_verified") is True and saved.get("hardware_verified") is False,
            "PSYNC received metadata identity differs")
    if "prefixes" in meta:
        require(all(meta.get(key) == value for key, value in saved.items()),
                "PSYNC received metadata changed after preparation")
    require([row.get("name") for row in saved["prefixes"]] == list(NAMES), "PSYNC received prefix inventory differs")
    # 延迟导入，避免builder接入本helper时形成循环依赖；复用RV64与RAM段界限门禁。
    from build import verify_elf
    listing = subprocess.check_output([cross + "nm", "-S", "--defined-only", str(elf)], text=True)
    for row in saved["prefixes"]:
        stem = STEM + "_" + row["name"]
        require(row["entry"] == "hpu_run_" + stem, "PSYNC received entry name differs")
        words = binary_words(plain_file(data, row["words_file"]))
        require(words == row["words"], "PSYNC received words changed after preparation")
        validate_program(data, row, words)
        names = [fields[3] for line in listing.splitlines() if len(fields := line.split()) == 4 and
                 fields[2] in ("T", "t") and (fields[3] == row["entry"] or fields[3].startswith(row["entry"] + "."))]
        require(bool(names), "missing PSYNC fixed ELF entry: " + row["entry"])
        actual = verify_elf(elf, cross, {"program_stem": stem})
        require(actual == words and actual[-1] == 0x7000005b and actual.count(0x7000005b) == 1,
                "PSYNC fixed ELF words/tail differ: " + row["entry"])
