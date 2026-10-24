"""PSYNC sidecar格式负向单测；合成夹具不代表原生模型或硬件执行。"""
import copy
import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import psync_prefixes as receiver


PIN = "test-pin"
QS = [2013265921, 1811939329, 469762049, 998244353]


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def fixed_source(stem, words, spans):
    source = f'#include "{stem}.h"\n'
    if spans:
        source += f"\nstatic const hpu_dma_span_t hpu_program_{stem}_resolved_spans[] = {{\n"
        source += "".join(f"    {{ UINT32_C({row['line_offset']}), UINT32_C({row['line_count']}) }},\n" for row in spans)
        source += "};\n"
    source += "\n/* Fixed spans validated at generation; x11 changes only with DMA length. */\n"
    source += f"int hpu_run_{stem}(void) {{\n"
    if spans:
        source += f"    (void)hpu_program_{stem}_resolved_spans;\n"
    source += "#if defined(__riscv)\n    __asm__ volatile(\n"
    dma, previous = 0, None
    for word in words:
        if word & 127 == 0x2b:
            row = spans[dma]
            dma += 1
            source += f'        "li x10, {row["line_offset"]}\\n\\t"\n'
            if row["line_count"] != previous:
                source += f'        "li x11, {row["line_count"]}\\n\\t"\n'
                previous = row["line_count"]
        source += f'        ".word 0x{word:08X}\\n\\t"\n'
    return source + '        : : : "x10", "x11", "memory");\n    return 0;\n#else\n    return -4;\n#endif\n}\n'


def fixture(root):
    source = root / "package"
    source.mkdir()
    spec = dict(case_id=receiver.CASE, kind="instruction", operation="psync", profile="instruction",
                scheme="raw", degree=1024, level=4, program_stem=receiver.STEM)
    descriptor = dict(schema="hpu-application-package", schema_version=1, case_name=receiver.STEM, scheme="ckks",
                      parameters="parameters.json", operation_graph="graph.json", oracle_report="report.json",
                      line_map="line_map.csv", memory_manifest="memory.csv", memory_config="config.json",
                      program_inst32="base.inst32", dma_relocation_manifest="dma.csv", golden_manifest="golden.csv")
    write_json(source / "package.json", descriptor)
    write_json(source / "provenance/build.json", dict(commit=PIN, worktree_state="clean-at-configure"))
    write_json(source / "parameters.json", dict(scheme="ckks", test_layer="instruction", encrypted=False,
        poly_modulus_degree=1024, plain_modulus=0, input_rns_components=4, context_moduli=QS,
        key_moduli=QS, levels=[dict(moduli=QS)]))
    allocations, words, dma, scenarios, golden = [], [], [], [], []
    used = 0

    def allocation(name, kind, count, readonly=True):
        nonlocal used
        row = dict(allocation_id=name, kind=kind, read_only="true" if readonly else "false", line_offset=str(used),
                   line_count=str(count), payload_words=str(count * 64), padded_words=str(count * 64), initialization="provided")
        used += count
        allocations.append(row)
        return row

    def transfer(obj, row, store=False, modulus=False):
        # 仅格式夹具的DMA字段；不会作为算法或真实SDK编码的通过证据。
        mask = 32 if modulus else 0
        word = (obj << 26) | (11 << 20) | (10 << 15) | (int(store) << 12) | (int(store or modulus) << 14) | ((mask >> 5) << 25) | 0x2b
        index = len(words)
        words.append(word)
        dma.append(dict(instruction_index=str(index), dma_index=str(len(dma)), operation_index="0", operation_id="tested",
                        operation_dma_index=str(len(dma)), direction="dstore" if store else "dload", object_slot=str(obj),
                        type_or_release=str(int(store or modulus)), flag=str(mask), allocation_id=row["allocation_id"],
                        line_offset=row["line_offset"], line_count=row["line_count"], word_hex=hex(word), normalized_asm="fixture", cp="0"))

    def output(component, limb):
        row = allocation(f"output/{len(golden)}", "output", 16, False)
        scenario = dict(component=component, modulus_id=limb, modulus=QS[limb], line_offset=int(row["line_offset"]),
                        line_count=16, words=1024, scenario="psync/dma-prefix" if component == 0 else "psync/compute-prefix")
        scenarios.append(scenario)
        golden.append(dict(object_id="step_0", component=str(component), modulus_id=str(limb), modulus=str(QS[limb]),
                           domain="coefficient", line_offset=row["line_offset"], line_count="16", payload_words="1024", padded_words="1024"))
        return row

    transfer(63, allocation("constants/modulus_table", "modulus_table", 1), modulus=True)
    for limb in range(4):
        words.append(0x6000005b | limb << 8)
        transfer(0, allocation(f"input/{limb * 3}/dma-a", "constant", 16))
        transfer(0, output(0, limb), store=True)
        allocation(f"guard/{limb * 2}", "constant", 1)
        transfer(0, allocation(f"input/{limb * 3 + 1}/compute-a", "constant", 16))
        transfer(1, allocation(f"input/{limb * 3 + 2}/compute-b", "constant", 16))
        words.append(0x2000005b)
        transfer(2, output(1, limb), store=True)
        allocation(f"guard/{limb * 2 + 1}", "constant", 1)
        words.extend((0x8000005b, 0x8000015b))
    words.extend((0x80003f5b, 0x7000005b))
    graph = dict(test_layer="instruction", component_semantics="scenario_not_ciphertext", component_count=2,
                 terminal_psync_count=1, timing_verified=False, irq_rearm_verified=False, scenario_outputs=scenarios,
                 operations=[dict(id="tested", kind="psync")])
    write_json(source / "graph.json", graph)
    report = {key: True for key in ("oracle_verified", "golden_matches_oracle", "model_verified", "raw_physical_words_equal",
              "readonly_and_guard_verified", "host_instruction_model_verified")}
    report.update(test_layer="instruction", overall_status="pass", oracle="independent_u64_modular_and_C_stage_golden",
                  host_instruction_model=dict(required=True, verified=True, status="pass", ntt_contract="legacy_raw_stage",
                      hardware_contract_verified=False, compared_words=8192),
                  instruction_execution_verified=False, rtl_verified=False, hardware_verified=False)
    write_json(source / "report.json", report)
    write_json(source / "config.json", dict(used_lines=used, capacity_lines=used))
    for filename, rows in (("line_map.csv", allocations), ("memory.csv", allocations), ("dma.csv", dma), ("golden.csv", golden)):
        write_csv(source / filename, rows)
    (source / "base.inst32").write_text("".join(f"{word:032b}\n" for word in words))
    sidecar = source.with_name(source.name + ".psync-prefixes")
    sidecar.mkdir()
    removed = {2 + 9 * limb + offset for limb in range(4) for offset in (0, 1)}
    kept = dict(idle=[38], dma=sorted(removed) + [38], compute=[index for index in range(39) if index not in removed])
    base_dma = {int(row["instruction_index"]): row for row in dma}
    prefixes = []
    for name in receiver.NAMES:
        stem = receiver.STEM + "_" + name
        selected = [words[index] for index in kept[name]]
        spans = [dict(instruction_index=new, allocation_id=base_dma[old]["allocation_id"],
                      line_offset=int(base_dma[old]["line_offset"]), line_count=int(base_dma[old]["line_count"]))
                 for new, old in enumerate(kept[name]) if old in base_dma]
        components = {"idle": [], "dma": [0], "compute": [1]}[name]
        row = dict(name=name, entry="hpu_run_" + stem, source_file=stem + ".c", header_file=stem + ".h",
                   asm_file=stem + ".asm", words_file=stem + ".inst32", expected_components=components,
                   instruction_count=len(selected), compared_output_words=4096 * len(components),
                   unchanged_words=used * 64 - 4096 * len(components), verified=True, model_verified=True,
                   read_only_guard_verified=True, dma_spans=spans)
        (sidecar / row["source_file"]).write_text(fixed_source(stem, selected, spans))
        (sidecar / row["header_file"]).write_text(receiver.prefix_header(stem, len(spans)))
        (sidecar / row["asm_file"]).write_bytes((receiver.ROOT / "src/03_instructions" / (receiver.CASE + "." + name + ".asm")).read_bytes())
        (sidecar / row["words_file"]).write_text("".join(f"{word:032b}\n" for word in selected))
        prefixes.append(row)
    manifest = dict(schema="hpu-psync-prefixes", schema_version=1, producer_commit=PIN, base_program_stem=receiver.STEM,
                    degree=1024, level=4, source_format="upstream_fixed_entry_only", initial_output_poison=0xffffffff,
                    verified=True, model_verified=True, read_only_guard_verified=True, hardware_verified=False, prefixes=prefixes)
    write_json(sidecar / "manifest.json", manifest)
    return source, sidecar, spec, manifest


class PsyncPrefixTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="psync-prefix-unit-"))
        self.addCleanup(self.clean)
        self.source, self.sidecar, self.spec, self.manifest = fixture(self.root)
        self.data = self.root / "data"

    def clean(self):
        # 只处理本测试创建的已关闭夹具，每次删除一个明确路径，不递归清除共享目录。
        for path in sorted(self.root.rglob("*"), key=lambda path: len(path.parts), reverse=True):
            if path.is_symlink() or path.is_file():
                path.unlink()
            else:
                path.rmdir()
        self.root.rmdir()

    def prepare(self, **kwargs):
        return receiver.prepare_prefixes(self.source, self.data, self.spec, PIN, **kwargs)

    def test_inventory_selected_outputs_and_identical_readonly_reuse(self):
        meta = self.prepare()
        self.assertEqual([row["output_indices"] for row in meta["prefixes"]], [[], [0, 2, 4, 6], [1, 3, 5, 7]])
        self.assertEqual([len(row["words"]) for row in meta["prefixes"]], [1, 9, 31])
        self.assertEqual(len(meta["source_files"]), 3)
        before = {path.name: (path.read_bytes(), path.stat().st_mtime_ns) for path in self.data.iterdir()}
        self.assertEqual(self.prepare(verify_existing=True), meta)
        self.assertEqual(self.prepare(), meta)
        self.assertEqual(before, {path.name: (path.read_bytes(), path.stat().st_mtime_ns) for path in self.data.iterdir()})

    def test_missing_or_different_cached_files_are_not_overwritten(self):
        meta = self.prepare()
        target = self.data / meta["source_files"][0]
        target.write_text("different")
        for readonly in (False, True):
            with self.subTest(readonly=readonly), self.assertRaisesRegex(ValueError, "overwrite different"):
                self.prepare(verify_existing=readonly)
        self.assertEqual(target.read_text(), "different")
        target.unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            self.prepare(verify_existing=True)
        self.assertFalse(target.exists())

    def test_readonly_missing_directory_and_wrong_case_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing"):
            self.prepare(verify_existing=True)
        self.assertFalse(self.data.exists())
        self.spec["level"] = 3
        with self.assertRaisesRegex(ValueError, "N1024/L4"):
            self.prepare()

    def test_schema_pin_shape_poison_and_verification_flags_are_strict(self):
        for key, value in (("producer_commit", "other"), ("schema_version", True), ("degree", 8192),
                           ("level", 3), ("initial_output_poison", 0), ("model_verified", False),
                           ("hardware_verified", True), ("unknown", 1)):
            with self.subTest(key=key):
                write_json(self.sidecar / "manifest.json", {**self.manifest, key: value})
                with self.assertRaisesRegex(ValueError, "schema/pin/shape"):
                    self.prepare()
                self.assertFalse(self.data.exists())

    def test_names_components_paths_and_valid_but_wrong_allocations_are_rejected(self):
        for mutation in ("names", "components", "path", "allocation"):
            with self.subTest(mutation=mutation):
                manifest = copy.deepcopy(self.manifest)
                row = manifest["prefixes"][1]
                if mutation == "names":
                    row["name"] = "compute"
                elif mutation == "components":
                    row["expected_components"] = [False]
                elif mutation == "path":
                    row["source_file"] = "../outside.c"
                else:
                    original = manifest["prefixes"][2]["dma_spans"][1]
                    row["dma_spans"][0].update({key: original[key] for key in ("allocation_id", "line_offset", "line_count")})
                write_json(self.sidecar / "manifest.json", manifest)
                with self.assertRaises(ValueError):
                    self.prepare()
                self.assertFalse(self.data.exists())

    def test_unknown_files_symlinks_and_asm_drift_are_rejected(self):
        extra = self.sidecar / "unknown.txt"
        extra.write_text("not allowed")
        with self.assertRaisesRegex(ValueError, "whitelist"):
            self.prepare()
        extra.unlink()
        target = self.sidecar / self.manifest["prefixes"][0]["source_file"]
        original = target.read_text()
        target.unlink()
        target.symlink_to(self.sidecar / self.manifest["prefixes"][0]["header_file"])
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.prepare()
        target.unlink()
        target.write_text(original)
        asm = self.sidecar / self.manifest["prefixes"][0]["asm_file"]
        asm.write_text("psync\npsync\n")
        with self.assertRaisesRegex(ValueError, "ASM differs"):
            self.prepare()

    def test_binary_width_fixed_clobber_and_duplicate_psync_are_rejected(self):
        row = self.manifest["prefixes"][1]
        words_file = self.sidecar / row["words_file"]
        original_words = words_file.read_text()
        words_file.write_text("1\n")
        with self.assertRaisesRegex(ValueError, "32-bit binary"):
            self.prepare()
        words_file.write_text(original_words + f"{0x7000005b:032b}\n")
        with self.assertRaisesRegex(ValueError, "unique PSYNC"):
            self.prepare()
        words_file.write_text(original_words)
        code = self.sidecar / row["source_file"]
        code.write_text(code.read_text().replace('"x10", "x11", "memory"', '"x10", "memory"'))
        with self.assertRaisesRegex(ValueError, "single-asm"):
            self.prepare()

    def test_base_scenario_golden_disagreement_is_rejected(self):
        graph = json.loads((self.source / "graph.json").read_text())
        graph["scenario_outputs"][0]["line_offset"] += 1
        write_json(self.source / "graph.json", graph)
        with self.assertRaisesRegex(ValueError, "scenario/golden"):
            self.prepare()

    def elf_listing(self, meta, missing=False):
        return "\n".join(f"00010000 00000010 T {row['entry']}.part.0" for row in meta["prefixes"][:2 if missing else 3])

    def test_elf_checks_each_fixed_part_without_requiring_base_entry(self):
        meta = self.prepare()
        by_stem = {row["program_stem"]: row["words"] for row in meta["prefixes"]}
        with patch("psync_prefixes.subprocess.check_output", return_value=self.elf_listing(meta)), \
             patch("build.verify_elf", side_effect=lambda elf, cross, row: by_stem[row["program_stem"]]) as check:
            receiver.verify_prefix_elf(self.root / "fixture.elf", self.data, meta, "cross-")
        self.assertEqual([call.args[2]["program_stem"] for call in check.call_args_list], list(by_stem))

    def test_elf_missing_entry_wrong_words_and_ram_bound_failure_are_rejected(self):
        meta = self.prepare()
        with patch("psync_prefixes.subprocess.check_output", return_value=self.elf_listing(meta, missing=True)), \
             patch("build.verify_elf", side_effect=[row["words"] for row in meta["prefixes"]]):
            with self.assertRaisesRegex(ValueError, "missing PSYNC fixed ELF entry"):
                receiver.verify_prefix_elf(self.root / "fixture.elf", self.data, meta, "cross-")
        with patch("psync_prefixes.subprocess.check_output", return_value=self.elf_listing(meta)), \
             patch("build.verify_elf", return_value=[0x7000005b, 0x7000005b]):
            with self.assertRaisesRegex(ValueError, "ELF words/tail"):
                receiver.verify_prefix_elf(self.root / "fixture.elf", self.data, meta, "cross-")
        with patch("psync_prefixes.subprocess.check_output", return_value=self.elf_listing(meta)), \
             patch("build.verify_elf", side_effect=ValueError("ELF LOAD segment overlaps workload DDR")):
            with self.assertRaisesRegex(ValueError, "overlaps workload DDR"):
                receiver.verify_prefix_elf(self.root / "fixture.elf", self.data, meta, "cross-")


if __name__ == "__main__":
    unittest.main()
