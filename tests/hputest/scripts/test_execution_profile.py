"""连续窗口接收器的小型合成契约测试；不宣称执行原生FHE或RTL。"""
import copy
import csv
import json
from pathlib import Path
import re
import tempfile
import unittest

import execution_profile as profile


STEM = "frontend_profile_probe"
SYNC = 0x7000005b
WORDS = [0x12b5402b, 0x6000005b, 0x00b5002b, 0x04b5002b, SYNC,
         0x2080005b, 0x08b5102b, 0x8000005b, 0x00b5002b, SYNC,
         0x0080005b, SYNC, 0x8000005b, 0x8000015b, 0x08b5502b, 0x8000045b, SYNC]
ASSEMBLY = "\n".join(("dload x10, x11, p4, 1, 0, 32", "pmodld 0", "dload x10, x11, p0, 0, 0, 0",
    "dload x10, x11, p1, 0, 0, 0", "psync", "pmul p2, p0, p1", "dstore x10, x11, p2, 0, 0",
    "pfree p0", "dload x10, x11, p0, 0, 0, 0", "psync", "padd p2, p2, p0", "psync", "pfree p0",
    "pfree p1", "dstore x10, x11, p2, 1, 0", "pfree p4", "psync")) + "\n"
SPANS = [(0, 1), (2, 2), (4, 2), (6, 2), (8, 2), (10, 2)]
DMA = [dict(instruction_index=str(index), direction=direction, line_offset=str(first), line_count=str(count))
       for index, direction, (first, count) in zip((0, 2, 3, 6, 8, 14),
           ("dload", "dload", "dload", "dstore", "dload", "dstore"), SPANS)]
WINDOW = dict(zip(profile.WINDOW_FIELDS, (5, 11, 2, 1, 1)))
ROWS = [{key: str(value) for key, value in WINDOW.items()}]
REPORT = dict(enabled=True, window_count=1, timing_measured=False, includes_residual_dma=True,
              prefix_dload_count=3, window_dload_count=1, window_dstore_count=1, suffix_dstore_count=1,
              unprofiled_dma_count=6, unprofiled_dma_bytes=2816)
RECEIVED = {**REPORT, **WINDOW, "sync_count": 4, "sync_instruction_indices": [4, 9, 11, 16],
            "start_sync_index": 0, "end_sync_index": 2, "prefix_dstore_count": 0, "suffix_dload_count": 0}


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


class ExecutionWindowTests(unittest.TestCase):
    def check_window(self, words=None, assembly=ASSEMBLY, dma=None, rows=None, report=None):
        return profile.validate_window(WORDS if words is None else words, assembly,
            DMA if dma is None else dma, ROWS if rows is None else rows, REPORT if report is None else report)

    def test_one_continuous_window_includes_residual_dma_and_an_existing_inner_sync(self):
        self.assertEqual(self.check_window(), RECEIVED)
        self.assertEqual(profile.constants(RECEIVED), dict(PROFILE_SYNC_COUNT=4, PROFILE_BEGIN_INSTRUCTION=5,
            PROFILE_END_INSTRUCTION=11, PROFILE_ARITHMETIC_COUNT=2, PROFILE_WINDOW_DLOAD_COUNT=1,
            PROFILE_WINDOW_DSTORE_COUNT=1, PROFILE_PREFIX_DLOAD_COUNT=3, PROFILE_SUFFIX_DSTORE_COUNT=1,
            PROFILE_PREFIX_DSTORE_COUNT=0, PROFILE_SUFFIX_DLOAD_COUNT=0))

    def test_multiple_windows_partial_arithmetic_and_bad_boundaries_are_rejected(self):
        for rows in (ROWS + copy.deepcopy(ROWS), [],
                     [{**ROWS[0], "begin_instruction": "10", "arithmetic_instruction_count": "1"}],
                     [{**ROWS[0], "end_instruction": "9", "arithmetic_instruction_count": "1"}],
                     [{**ROWS[0], "begin_instruction": "0"}], [{**ROWS[0], "end_instruction": "17"}]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                self.check_window(rows=rows)

    def test_window_header_numeric_fields_and_declared_counts_must_match(self):
        for rows in ([{**ROWS[0], "unknown": "1"}], [dict(reversed(list(ROWS[0].items())))],
                     [{**ROWS[0], "begin_instruction": "-5"}], [{**ROWS[0], "end_instruction": 11}],
                     [{**ROWS[0], "arithmetic_instruction_count": "3"}], [{**ROWS[0], "dstore_count": "0"}]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                self.check_window(rows=rows)

    def test_oracle_flags_counts_and_added_dma_are_rejected(self):
        for key, value in (("enabled", False), ("window_count", True), ("window_count", 2),
                           ("timing_measured", True), ("includes_residual_dma", False),
                           ("prefix_dload_count", 2), ("window_dload_count", -1),
                           ("window_dstore_count", True), ("suffix_dstore_count", 2),
                           ("unprofiled_dma_count", 5), ("unprofiled_dma_bytes", 2815)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.check_window(report={**REPORT, key: value})

    def test_dma_order_assembly_syncs_and_io_direction_are_checked(self):
        changed_dma = copy.deepcopy(DMA)
        changed_dma[0]["instruction_index"] = "1"
        with self.assertRaisesRegex(ValueError, "DMA ordering"):
            self.check_window(dma=changed_dma)
        with self.assertRaisesRegex(ValueError, "PSYNC order"):
            self.check_window(assembly=ASSEMBLY.replace("psync\n", "pfree p0\n", 1))
        for position, direction, label in ((0, "dstore", "prefix"), (5, "dload", "suffix")):
            changed_dma = copy.deepcopy(DMA)
            changed_dma[position]["direction"] = direction
            with self.subTest(label=label), self.assertRaisesRegex(ValueError, "direction differs"):
                self.check_window(dma=changed_dma)

    def test_existing_prefix_store_and_suffix_load_are_explicitly_counted(self):
        for inserted, word, assembly, direction, field in (
            (4, 0x00b5102b, "dstore x10, x11, p0, 0, 0", "dstore", "prefix_dstore_count"),
            (14, 0x00b5002b, "dload x10, x11, p0, 0, 0, 0", "dload", "suffix_dload_count")):
            with self.subTest(field=field):
                words = WORDS[:inserted] + [word] + WORDS[inserted:]
                lines = ASSEMBLY.splitlines()
                lines.insert(inserted, assembly)
                dma = copy.deepcopy(DMA)
                for row in dma:
                    row["instruction_index"] = str(int(row["instruction_index"]) +
                        int(int(row["instruction_index"]) >= inserted))
                dma.append(dict(instruction_index=str(inserted), direction=direction, line_offset="12", line_count="2"))
                dma.sort(key=lambda row: int(row["instruction_index"]))
                window = {key: value + int(key in ("begin_instruction", "end_instruction") and value >= inserted)
                          for key, value in WINDOW.items()}
                rows = [{key: str(value) for key, value in window.items()}]
                report = {**REPORT, "unprofiled_dma_count": 7, "unprofiled_dma_bytes": 3328}
                actual = self.check_window(words=words, assembly="\n".join(lines) + "\n", dma=dma, rows=rows, report=report)
                self.assertEqual(actual[field], 1)
                self.assertEqual(actual["arithmetic_instruction_count"], 2)
                self.assertEqual(actual["dload_count"], 1)
                self.assertEqual(actual["dstore_count"], 1)
                # 未声明的额外方向可由实指令推导；若上游声明了，必须逐项一致。
                self.assertEqual(self.check_window(words=words, assembly="\n".join(lines) + "\n", dma=dma,
                    rows=rows, report={**report, field: 1})[field], 1)
                with self.assertRaises(ValueError):
                    self.check_window(words=words, assembly="\n".join(lines) + "\n", dma=dma,
                        rows=rows, report={**report, field: 0})
                with self.assertRaisesRegex(ValueError, "added DMA"):
                    self.check_window(words=words, assembly="\n".join(lines) + "\n", dma=dma,
                        rows=rows, report={**report, "unprofiled_dma_count": 6})


class ProfileSourceTests(unittest.TestCase):
    def setUp(self):
        self.code = profile.expected_source(STEM, WORDS, SPANS, WINDOW)
        self.header = profile.expected_header(STEM, len(SPANS))

    def validate(self, code=None, header=None):
        profile.validate_source(self.code if code is None else code,
            self.header if header is None else header, STEM, WORDS, SPANS, WINDOW)

    def test_all_words_waits_fresh_x11_and_the_single_timestamp_pair_are_explicit(self):
        self.validate()
        self.assertEqual([int(word, 16) for word in re.findall(r"\.word (0x[0-9A-F]+)", self.code)], WORDS)
        self.assertEqual(self.code.count("__asm__ volatile("), 4)
        self.assertEqual(self.code.count("li x10,"), 6)
        # 同块可重用2-line长度；经历wait回调后同长度也必须重新设置。
        self.assertEqual(self.code.count("li x11,"), 4)
        self.assertEqual(re.findall(r"wait_complete\(hooks->user, (\d+)\)", self.code), ["0", "1", "2", "3"])
        self.assertEqual(self.code.count("hooks->read_cycles(hooks->user)"), 2)
        order = ("hooks->wait_complete(hooks->user, 0)", "sample->start_cycles = hooks->read_cycles",
                 "hooks->wait_complete(hooks->user, 1)", "hooks->wait_complete(hooks->user, 2)",
                 "sample->end_cycles = hooks->read_cycles", "hooks->wait_complete(hooks->user, 3)",
                 "sample->valid = 1;")
        positions = [self.code.index(token) for token in order]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(self.code.count("return -5;"), 2)
        self.assertIn("if (status != 0) return status;", self.code)

    def test_missing_redundant_or_wrong_register_setup_and_wait_index_are_rejected(self):
        second = self.code.index("/* Instructions [5, 10)")
        fresh = self.code.index('        "li x11, 2\\n\\t"\n', second)
        no_fresh = self.code[:fresh] + self.code[fresh:].replace('        "li x11, 2\\n\\t"\n', "", 1)
        for code in (no_fresh, self.code.replace("li x10, 8", "li x10, 9"),
                     self.code.replace('"x10", "x11", "memory"', '"x10", "memory"'),
                     self.code.replace("wait_complete(hooks->user, 1)", "wait_complete(hooks->user, 0)")):
            with self.subTest(code=code[-150:]), self.assertRaisesRegex(ValueError, "official callbacks"):
                self.validate(code=code)

    def test_extra_timestamp_early_valid_and_old_fixed_source_are_rejected(self):
        for code in (self.code.replace("    sample->valid = 1;", "    sample->end_cycles = hooks->read_cycles(hooks->user);\n    sample->valid = 1;"),
                     self.code.replace("    sample->valid = 1;", "").replace("    /* Instructions [12, 17)",
                         "    sample->valid = 1;\n    /* Instructions [12, 17)"),
                     'int hpu_run_' + STEM + '(void) { return hpu_program_' + STEM + '(0, 0); }\n'):
            with self.subTest(code=code[-150:]), self.assertRaisesRegex(ValueError, "official callbacks"):
                self.validate(code=code)

    def test_hook_sample_and_ordinary_entry_header_abi_must_match_exactly(self):
        for old, new in (("uint64_t (*read_cycles)", "uint32_t (*read_cycles)"),
                         ("size_t sync_index", "unsigned sync_index"), ("    int valid;", "    unsigned valid;"),
                         ("_profiled(const", "_profiled_wrong(const"),
                         ("HPU_EXECUTION_PROFILE_TYPES_DEFINED", "HPU_PROFILE_OLD_TYPES")):
            with self.subTest(old=old), self.assertRaisesRegex(ValueError, "header/hook/sample ABI"):
                self.validate(header=self.header.replace(old, new))


class ProfilePreparationTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="execution-profile-unit-"))
        self.addCleanup(self.clean)
        (self.root / (STEM + ".c")).write_text(profile.expected_source(STEM, WORDS, SPANS, WINDOW))
        (self.root / (STEM + ".h")).write_text(profile.expected_header(STEM, len(SPANS)))
        (self.root / (STEM + ".inst32")).write_text("".join(f"{word:032b}\n" for word in WORDS))
        (self.root / "profile.asm").write_text(ASSEMBLY)
        write_csv(self.root / "execution_window.csv", ROWS)
        write_csv(self.root / "profile_dma.csv", DMA)
        self.write_meta(dict(program_stem=STEM, execution_profile=RECEIVED))

    def clean(self):
        for path in self.root.iterdir():
            path.unlink()
        self.root.rmdir()

    def write_meta(self, meta):
        (self.root / "delivery.json").write_text(json.dumps(meta) + "\n")

    def test_prepare_keeps_official_c_header_unchanged_and_reuses_identical_receipt(self):
        originals = {suffix: (self.root / (STEM + suffix)).read_bytes() for suffix in (".c", ".h")}
        self.assertEqual(profile.prepare(self.root, STEM), len(WORDS))
        target = self.root / "EXECUTION_PROFILE.json"
        receipt = json.loads(target.read_text())
        self.assertEqual((receipt["metric"], receipt["completion"], receipt["profile"]),
                         ("execution_window_irq_v1", "plic_irq", "continuous"))
        self.assertEqual(receipt["source_adaptation"], "none")
        self.assertIs(receipt["native_profiled_entry_unchanged"], True)
        self.assertEqual(receipt["execution_profile"], RECEIVED)
        before = (target.read_bytes(), target.stat().st_mtime_ns)
        self.assertEqual(profile.prepare(self.root, STEM), len(WORDS))
        self.assertEqual((target.read_bytes(), target.stat().st_mtime_ns), before)
        self.assertEqual({suffix: (self.root / (STEM + suffix)).read_bytes() for suffix in originals}, originals)

    def test_receipt_with_different_content_or_symlink_is_never_overwritten(self):
        target = self.root / "EXECUTION_PROFILE.json"
        target.write_bytes(b"different")
        with self.assertRaisesRegex(ValueError, "receipt differs"):
            profile.prepare(self.root, STEM)
        self.assertEqual(target.read_bytes(), b"different")
        target.unlink()
        target.symlink_to(self.root / (STEM + ".h"))
        with self.assertRaisesRegex(ValueError, "symlink"):
            profile.prepare(self.root, STEM)

    def test_missing_stale_metadata_and_non_binary_inst32_are_rejected_before_receipt(self):
        for meta in (dict(program_stem="other", execution_profile=RECEIVED), dict(program_stem=STEM),
                     dict(program_stem=STEM, execution_profile={**RECEIVED, "start_sync_index": 1})):
            with self.subTest(meta=meta), self.assertRaises(ValueError):
                self.write_meta(meta)
                profile.prepare(self.root, STEM)
        self.write_meta(dict(program_stem=STEM, execution_profile=RECEIVED))
        (self.root / (STEM + ".inst32")).write_text("111\n")
        with self.assertRaisesRegex(ValueError, "INST32 format"):
            profile.prepare(self.root, STEM)
        self.assertFalse((self.root / "EXECUTION_PROFILE.json").exists())


if __name__ == "__main__":
    unittest.main()
