"""在线PMUL只增加已知参数检查；固定发令与字码必须保持原样。"""
import unittest
from unittest.mock import patch

import test_inline_abi as fixture
from performance_adapter import adapt, function_span, instruction_words


GUARD = ("    if (hpu_obj_len[2] == 0 || hpu_obj_len[2] < 2 || "
         "hpu_obj_len[2] > 1024 || (hpu_obj_len[2] & (hpu_obj_len[2] - 1)) != 0 || "
         "hpu_obj_len[1] != 2) return -6;\n")
ONLINE_WORD = 0x2082415B


def online_fixture():
    # 这是精简的上游源码模板，不替代真实包、指令模型或硬件执行。
    words = fixture.WORDS[:-1] + [ONLINE_WORD, fixture.WORDS[-1]]
    with patch.object(fixture, "WORDS", words):
        source = fixture.source_fixture()
    fixed_sync = '        ".word 0x7000005B\\n\\t"\n'
    source = source.replace(fixed_sync, f'        ".word 0x{ONLINE_WORD:08X}\\n\\t"\n' + fixed_sync)
    return source.replace("    /* 3: producer instruction */", GUARD +
                          "    hpu_obj_len[2] = hpu_obj_len[2];\n" +
                          "    /* 3: producer instruction */"), words


class OnlinePmulAdapterTests(unittest.TestCase):
    def test_native_online_guard_is_preserved_outside_fixed_entry(self):
        source, words = online_fixture()
        adapted, count = adapt(source, fixture.STEM)
        self.assertEqual((count, instruction_words(adapted)), (len(words), words))
        begin, end = function_span(source, "hpu_run_" + fixture.STEM)
        fixed_begin, fixed_end = function_span(adapted, "hpu_run_" + fixture.STEM)
        self.assertEqual(source[begin:end], adapted[fixed_begin:fixed_end])
        begin, end = function_span(adapted, "hpu_program_" + fixture.STEM + "_preflight")
        self.assertIn(GUARD, adapted[begin:end])
        self.assertNotIn("__asm__", adapted[begin:end])
        self.assertNotIn(".word", adapted[begin:end])
        self.assertNotIn("hpu_obj_len", adapted[fixed_begin:fixed_end])

    def test_unknown_or_inconsistent_guard_is_rejected(self):
        source, _ = online_fixture()
        for original, changed in (
            ("hpu_obj_len[2] < 2", "hpu_obj_len[3] < 2"),
            ("hpu_obj_len[2] > 1024", "hpu_obj_len[2] > 2048"),
            ("hpu_obj_len[1] != 2", "hpu_obj_len[1] != 4"),
            ("(hpu_obj_len[2] & (hpu_obj_len[2] - 1)) != 0", "0 != 0"),
            ("return -6;", "return diagnose();"),
        ):
            with self.subTest(change=changed):
                with self.assertRaisesRegex(ValueError, "unexpected producer control"):
                    adapt(source.replace(original, changed), fixture.STEM)

    def test_unknown_additional_control_is_not_silently_moved(self):
        source, _ = online_fixture()
        with self.assertRaisesRegex(ValueError, "unexpected producer control"):
            adapt(source.replace(GUARD, GUARD + "    if (unknown()) return -6;\n"), fixture.STEM)


if __name__ == "__main__":
    unittest.main()
