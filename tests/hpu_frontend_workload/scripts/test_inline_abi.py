"""在线twiddle ABI和fixed C适配的focused门禁；不宣称执行FHE或硬件。"""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from import_package import ISA_ABI, NTT_ABI, validate_isa_contract, validate_ntt_contract
from performance_adapter import (RETURN_BLOCK, adapt, function_span, instruction_words,
                                 prepare, validate_source)


STEM = "frontend_probe"
WORDS = [0x00b5202b, 0x02b5202b, 0x04b5202b, 0x7000005b]
SPANS = [(4, 2), (8, 2), (12, 64)]


def source_fixture():
    # 缩小的上游C模板夹具；只验证接收/适配，不是算法/真实native包证据。
    dynamic = f'''int hpu_program_{STEM}(const hpu_dma_span_t *spans, size_t span_count) {{
    if (span_count != HPU_PROGRAM_{STEM.upper()}_DMA_COUNT || (span_count != 0 && spans == NULL)) return -1;
    volatile uint32_t hpu_obj_len[64];
    for (size_t i = 0; i < 64; ++i) hpu_obj_len[i] = 0;
    for (size_t i = 0; i < span_count; ++i) {{
        if (spans[i].line_count == 0 ||
            spans[i].line_offset >= HPU_MEM_LINE_COUNT ||
            spans[i].line_count > HPU_MEM_LINE_COUNT - spans[i].line_offset)
            return -2;
    }}
'''
    for index, word in enumerate(WORDS):
        if index < len(SPANS):
            dynamic += f"    hpu_obj_len[{index}] = spans[{index}].line_count;\n"
        dynamic += (f"    /* {index}: producer instruction */\n#if defined(__riscv)\n"
                    f'    __asm__ volatile(".word 0x{word:08X}" : : : "memory");\n#endif\n')
    dynamic += RETURN_BLOCK + "\n}\n"
    spans = f"static const hpu_dma_span_t hpu_program_{STEM}_resolved_spans[] = {{\n"
    spans += "".join(f"    {{ UINT32_C({first}), UINT32_C({count}) }},\n" for first, count in SPANS) + "};\n"
    fixed = f'''int hpu_run_{STEM}(void) {{
    (void)hpu_program_{STEM}_resolved_spans;
#if defined(__riscv)
    __asm__ volatile(
        "li x10, 4\\n\\t"
        "li x11, 2\\n\\t"
        ".word 0x00B5202B\\n\\t"
        "li x10, 8\\n\\t"
        ".word 0x02B5202B\\n\\t"
        "li x10, 12\\n\\t"
        "li x11, 64\\n\\t"
        ".word 0x04B5202B\\n\\t"
        ".word 0x7000005B\\n\\t"
        : : : "x10", "x11", "memory");
    return 0;
#else
    return -4;
#endif
}}
'''
    return f'#include "{STEM}.h"\n' + dynamic + spans + fixed


class OnlineNttAbiTests(unittest.TestCase):
    def setUp(self):
        self.parameters = {"ntt_table_abi": copy.deepcopy(NTT_ABI)}
        self.memory_abi = dict(NTT_ABI)
        self.rows = [{"allocation_id": "q0/intt/stage0", "kind": "twiddle", "read_only": "true",
                      "payload_words": "128", "padded_words": "128", "line_count": "2"},
                     {"allocation_id": "q0/ntt/pre_twist", "kind": "twiddle", "read_only": "true",
                      "payload_words": "128", "padded_words": "128", "line_count": "2"},
                     {"allocation_id": "q0/intt/post_untwist_scale", "kind": "twiddle", "read_only": "true",
                      "payload_words": "128", "padded_words": "128", "line_count": "2"}]

    def validate(self):
        validate_ntt_contract(self.parameters, self.memory_abi, self.rows, 4096)

    def test_stage_and_pre_post_are_explicit_online_parameter_contracts(self):
        self.validate()

    def test_small_n128_still_requires_two_parameter_lines(self):
        rows = copy.deepcopy(self.rows)
        rows[1]["payload_words"] = rows[2]["payload_words"] = "128"
        validate_ntt_contract(self.parameters, self.memory_abi, rows, 128)
        rows[0].update(payload_words="64", padded_words="64", line_count="1")
        with self.assertRaisesRegex(ValueError, "two-line"):
            validate_ntt_contract(self.parameters, self.memory_abi, rows, 128)

    def test_old_v1_contract_cannot_silently_load_on_new_producer(self):
        self.parameters["ntt_table_abi"]["version"] = 1
        with self.assertRaisesRegex(ValueError, "ABI v3"):
            self.validate()

    def test_unknown_chain_count_and_memory_sidecar_mismatch_are_rejected(self):
        self.memory_abi["twiddle_chains"] = 4
        with self.assertRaisesRegex(ValueError, "ABI mismatch"):
            self.validate()

    def test_old_full_table_or_single_line_stage_is_rejected(self):
        for count, payload in ((32, 2048), (1, 64)):
            with self.subTest(count=count):
                self.rows[0].update(line_count=str(count), payload_words=str(payload), padded_words=str(payload))
                with self.assertRaisesRegex(ValueError, "two-line"):
                    self.validate()

    def test_old_full_pre_twist_is_not_an_online_pmul_parameter_template(self):
        self.rows[1].update(payload_words="4096", padded_words="4096", line_count="64")
        with self.assertRaisesRegex(ValueError, "two-line"):
            self.validate()


class Objects64AbiTests(unittest.TestCase):
    def test_current_contract_is_accepted(self):
        validate_isa_contract(dict(ISA_ABI))

    def test_old_isa_missing_cp_or_wrong_object_width_is_rejected(self):
        for field, value in (("instruction_isa", "hpu-objects64-v1.1"), ("object_slots", 8),
                             ("dma_format", "type_release"), ("dma_cache_policy", "preserve")):
            with self.subTest(field=field):
                abi = dict(ISA_ABI)
                abi[field] = value
                with self.assertRaisesRegex(ValueError, "v1.2"):
                    validate_isa_contract(abi)


class FixedEntryTests(unittest.TestCase):
    def test_double_word_copy_is_accepted_only_in_matching_dynamic_and_fixed_entries(self):
        validate_source(source_fixture(), STEM, WORDS, SPANS)
        with self.assertRaisesRegex(ValueError, "dynamic/fixed"):
            validate_source(source_fixture().replace("0x00B5202B", "0x00B5205B", 1), STEM, WORDS, SPANS)

    def test_changed_immediate_cached_length_and_clobber_are_rejected(self):
        for old, new in (("li x10, 8", "li x10, 9"), ("li x11, 64", "li x11, 2"),
                         ('"x10", "x11", "memory"', '"x10", "memory"')):
            with self.subTest(change=old):
                with self.assertRaisesRegex(ValueError, "single-asm"):
                    validate_source(source_fixture().replace(old, new), STEM, WORDS, SPANS)

    def test_adapter_keeps_fixed_single_asm_identical_and_extracts_preflight(self):
        original = source_fixture()
        adapted, count = adapt(original, STEM)
        self.assertEqual(count, len(WORDS))
        self.assertEqual(instruction_words(adapted), WORDS)
        begin, end = function_span(original, "hpu_run_" + STEM)
        actual_begin, actual_end = function_span(adapted, "hpu_run_" + STEM)
        self.assertEqual(adapted[actual_begin:actual_end], original[begin:end])
        start, stop = function_span(adapted, "hpu_program_" + STEM + "_preflight")
        self.assertNotIn("__asm__", adapted[start:stop])
        self.assertIn("return -2", adapted[start:stop])
        self.assertIn("hpu_validate_" + STEM, adapted)
        self.assertEqual(adapted.count('"li x11,'), 2)

    def test_unknown_dynamic_control_is_not_moved_out_of_timing(self):
        original = source_fixture().replace("    volatile uint32_t hpu_obj_len", "    unexpected();\n    volatile uint32_t hpu_obj_len")
        with self.assertRaisesRegex(ValueError, "unexpected producer control"):
            adapt(original, STEM)

    def test_prepare_checks_inst32_and_records_native_fixed_entry(self):
        with tempfile.TemporaryDirectory(prefix="frontend-online-adapter-test-") as temporary:
            root = Path(temporary)
            (root / f"{STEM}.c").write_text(source_fixture())
            (root / f"{STEM}.inst32").write_text("\n".join(f"{word:032b}" for word in WORDS))
            self.assertEqual(prepare(root, STEM), len(WORDS))
            report = json.loads((root / "PERF_ADAPTATION.json").read_text())
            self.assertTrue(report["native_fixed_entry_unchanged"])
            self.assertFalse(report["preflight_emits_hpu"])
            self.assertEqual((root / f"{STEM}.c").read_text(), source_fixture())


if __name__ == "__main__":
    unittest.main()
