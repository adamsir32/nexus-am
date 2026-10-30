"""验证07的统一清单、目标构建和实际ELF门禁；夹具不是硬件执行结果。"""
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import build_performance as build


STEM = "probe"
CFG = """00001000 <main>:
    1000: 000000ef jal 2000 <hpu_validate_probe>
    1004: 00000063 bnez a0,1090 <main+0x90>
    1008: 000000ef jal 2600 <irq_reset_events>
    100c: 00000063 bnez a0,1090 <main+0x90>
    1010: 000000ef jal 2700 <irq_open>
    1014: 00000063 bnez a0,1080 <main+0x80>
    1018: 000000ef jal 2800 <irq_event_count>
    101c: 00000063 bnez a0,1080 <main+0x80>
    1020: 000000ef jal 2900 <irq_handler_count>
    1024: 00000063 bnez a0,1080 <main+0x80>
    1028: 000000ef jal 2100 <perf_cycle_read>
    102c: 000000ef jal 2200 <hpu_run_probe>
    1030: 00000063 beqz a0,1040 <main+0x40>
    1034: 000000ef jal 2100 <perf_cycle_read>
    1038: 000000ef jal 2a00 <irq_close>
    103c: 0000006f j 3000 <case_fail>
    1040: 000000ef jal 2300 <performance_wait>
    1044: 000000ef jal 2100 <perf_cycle_read>
    1048: 000000ef jal 2a00 <irq_close>
    104c: 000000ef jal 2800 <irq_event_count>
    1050: 00000413 li s0,1
    1054: 00000063 bne a0,s0,1090 <main+0x90>
    1058: 000000ef jal 2900 <irq_handler_count>
    105c: 00000063 bne a0,s0,1090 <main+0x90>
    1060: 080004b7 lui s1,0x8000
    1064: 00000003 lwu a5,28(s1)
    1068: 00000003 lwu a5,20(s1)
    106c: 00000003 lwu a5,24(s1)
    1070: 000000ef jal 2400 <check_results>
    1074: 000000ef jal 2500 <check_memory>
    1078: 0000006f j 3100 <case_pass>
    1080: 000000ef jal 2a00 <irq_close>
    1084: 0000006f j 3000 <case_fail>
    1090: 0000006f j 3000 <case_fail>
00002000 <hpu_validate_probe>:
    2000: 00008067 ret
00002200 <hpu_run_probe>:
    2200: 7000005b .word 0x7000005b
    2204: 00008067 ret
00002300 <performance_wait>:
    2300: 000000ef jal 2b00 <irq_poll>
    2304: 00008067 ret
"""


def gcc13_counter_cfg():
    """复刻Ubuntu24.04/GCC13.3实际生成的计数sext.w及保存/比较形式。"""
    main, helpers = CFG.split("00002000 <hpu_validate_probe>:", 1)
    # 留出真实的4字节指令槽；保留原CFG所有成功/失败分支。
    def address(match):
        return f"{0x1000 + (int(match[1], 16) - 0x1000) * 2:04x}"
    main = re.sub(r"\b([0-9a-f]+)(?=:)", address, main)
    main = re.sub(r"\b([0-9a-f]+)(?= <main\+)", address, main)
    main = main.replace("1030: 000000ef jal 2800 <irq_event_count>",
                        "1030: 000000ef jal 2800 <irq_event_count>\n"
                        "    1034: 2501 sext.w a0,a0")
    main = main.replace("1040: 000000ef jal 2900 <irq_handler_count>",
                        "1040: 000000ef jal 2900 <irq_handler_count>\n"
                        "    1044: 0005079b sext.w a5,a0").replace(
                            "1048: 00000063 bnez a0", "1048: 00000063 bnez a5")
    main = main.replace("1098: 000000ef jal 2800 <irq_event_count>",
                        "1098: 000000ef jal 2800 <irq_event_count>\n"
                        "    109c: 0005041b sext.w s0,a0")
    main = main.replace("10a0: 00000413 li s0,1", "10a0: 00000793 li a5,1")
    main = main.replace("10a8: 00000063 bne a0,s0,1120 <main+0x90>",
                        "10a8: 00000063 beq s0,a5,10b0 <main+0xb0>\n"
                        "    10ac: 0000006f j 3000 <case_fail>")
    main = main.replace("10b0: 000000ef jal 2900 <irq_handler_count>",
                        "10b0: 000000ef jal 2900 <irq_handler_count>\n"
                        "    10b4: 0005079b sext.w a5,a0").replace(
                            "10b8: 00000063 bne a0,s0", "10b8: 00000063 bne a5,s0")
    return main + "00002000 <hpu_validate_probe>:" + helpers


class TimingTests(unittest.TestCase):
    def test_checked_event_count_saved_on_stack_still_proves_handler_count(self):
        stacked = CFG.replace(
            "1058: 000000ef jal 2900 <irq_handler_count>",
            "1057: 00000023 sd a0,0(sp)\n"
            "    1058: 000000ef jal 2900 <irq_handler_count>").replace(
                "105c: 00000063 bne a0,s0,1090 <main+0x90>",
                "105a: 00003403 ld s0,0(sp)\n"
                "    105c: 00000063 bne a0,s0,1090 <main+0x90>")
        build.verify_timing(stacked, STEM)
        for broken in (stacked.replace("sd a0,0(sp)", "sd zero,0(sp)"),
                       stacked.replace("105a: 00003403 ld s0,0(sp)",
                                       "105a: 00000413 li s0,0")):
            with self.subTest(broken=broken), self.assertRaisesRegex(
                    ValueError, "ordering differs"):
                build.verify_timing(broken, STEM)

    def test_gcc13_counter_normalization_preserves_exact_zero_and_one_checks(self):
        build.verify_timing(gcc13_counter_cfg(), STEM)

    def test_gcc13_normalization_cannot_hide_wrong_or_missing_counter_checks(self):
        cfg = gcc13_counter_cfg()
        broken = [cfg.replace("1044: 0005079b sext.w a5,a0", "1044: 0002879b sext.w a5,t0"),
                  cfg.replace("1034: 2501 sext.w a0,a0", "1034: 0ff57513 andi a0,a0,255"),
                  cfg.replace("10a0: 00000793 li a5,1", "10a0: 00000793 li a5,2"),
                  cfg.replace("10b8: 00000063 bne a5,s0,1120 <main+0x90>", "10b8: 00000013 nop")]
        for text in broken:
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "ordering differs"):
                build.verify_timing(text, STEM)

    def test_explicit_source_failure_entry_keeps_the_same_success_timing_contract(self):
        build.verify_timing(CFG.replace("<case_fail>", "<case_fail_at>"), STEM)

    def test_gcc_copied_failure_stop_does_not_add_a_success_sample(self):
        build.verify_timing(CFG, STEM)

    def test_pass_path_cannot_skip_wait(self):
        broken = CFG.replace("1030: 00000063 beqz a0,1040", "1030: 00000063 beqz a0,1044")
        with self.assertRaisesRegex(ValueError, "ordering differs"):
            build.verify_timing(broken, STEM)

    def test_a_second_pass_path_cannot_bypass_the_measurement(self):
        broken = CFG.replace("1004: 00000063 bnez a0,1090", "1004: 00000063 bnez a0,1078")
        with self.assertRaisesRegex(ValueError, "ordering differs"):
            build.verify_timing(broken, STEM)

    def test_logging_between_issue_and_stop_is_rejected(self):
        broken = CFG.replace("1040: 000000ef jal 2300 <performance_wait>",
                             "1040: 000000ef jal 2300 <performance_wait>\n"
                             "1042: 000000ef jal 3200 <printf_>")
        with self.assertRaisesRegex(ValueError, "ordering differs"):
            build.verify_timing(broken, STEM)

    def test_extra_cycle_on_success_is_rejected(self):
        broken = CFG.replace("1070: 000000ef jal 2400 <check_results>",
                             "106e: 000000ef jal 2100 <perf_cycle_read>\n"
                             "1070: 000000ef jal 2400 <check_results>")
        with self.assertRaisesRegex(ValueError, "ordering differs"):
            build.verify_timing(broken, STEM)

    def test_preflight_must_not_issue_hpu(self):
        broken = CFG.replace("2000: 00008067 ret", "2000: 7000005b .word 0x7000005b")
        with self.assertRaisesRegex(ValueError, "preflight issues"):
            build.verify_timing(broken, STEM)

    def test_missing_or_unchecked_irq_arm_is_rejected(self):
        for broken in (CFG.replace("1010: 000000ef jal 2700 <irq_open>", "1010: 00000013 nop"),
                       CFG.replace("1014: 00000063 bnez a0,1080 <main+0x80>", "1014: 00000013 nop")):
            with self.subTest(broken=broken), self.assertRaisesRegex(ValueError, "ordering differs"):
                build.verify_timing(broken, STEM)

    def test_irq_arm_inside_timing_window_is_rejected(self):
        broken = CFG.replace("1010: 000000ef jal 2700 <irq_open>",
                             "1010: 000000ef jal 2100 <perf_cycle_read>").replace(
                                 "1028: 000000ef jal 2100 <perf_cycle_read>",
                                 "1028: 000000ef jal 2700 <irq_open>")
        with self.assertRaisesRegex(ValueError, "ordering differs"):
            build.verify_timing(broken, STEM)

    def test_close_before_stop_and_missing_isr_terminal_checks_are_rejected(self):
        cases = [CFG.replace("1040: 000000ef jal 2300 <performance_wait>",
                             "1040: 000000ef jal 2a00 <irq_close>"),
                 CFG.replace("1058: 000000ef jal 2900 <irq_handler_count>", "1058: 00000013 nop"),
                 CFG.replace("1068: 00000003 lwu a5,20(s1)", "1068: 00000013 nop"),
                 CFG.replace("1064: 00000003 lwu a5,28(s1)", "1064: 00000023 sw a5,28(s1)")]
        for broken in cases:
            with self.subTest(broken=broken), self.assertRaisesRegex(ValueError, "ordering differs"):
                build.verify_timing(broken, STEM)

    def test_failure_arm_cleanup_is_not_mistaken_for_timed_close(self):
        # CFG中1080是arm/旧计数检查失败的close，不经过start，也不能到PASS。
        build.verify_timing(CFG, STEM)

    def test_wait_must_observe_isr_and_cannot_clear_or_print(self):
        for replacement in ("2300: 00000013 nop",
                            "2300: 000000ef jal 2b00 <clear_completion>",
                            "2300: 000000ef jal 2b00 <irq_diagnose>"):
            broken = CFG.replace("2300: 000000ef jal 2b00 <irq_poll>", replacement)
            with self.subTest(replacement=replacement), self.assertRaisesRegex(ValueError, "wait path"):
                build.verify_timing(broken, STEM)

    def test_unique_shared_wait_delegate_preserves_the_isr_gate(self):
        delegated = CFG.replace("2300: 000000ef jal 2b00 <irq_poll>\n    2304: 00008067 ret",
                                "2300: 0000006f j 2c00 <wait_program>\n"
                                "00002c00 <wait_program>:\n"
                                "    2c00: 000000ef jal 2b00 <irq_poll>\n"
                                "    2c04: 00008067 ret")
        build.verify_timing(delegated, STEM)
        for broken in (delegated.replace("2c00: 000000ef jal 2b00 <irq_poll>",
                                         "2c00: 000000ef jal 2b00 <clear_completion>"),
                       delegated.replace("2300: 0000006f j 2c00 <wait_program>",
                                         "2300: 000000ef jal 2d00 <untracked_work>\n"
                                         "    2304: 0000006f j 2c00 <wait_program>")):
            with self.subTest(broken=broken), self.assertRaisesRegex(ValueError, "wait path"):
                build.verify_timing(broken, STEM)

    def test_actual_main_cross_compilation_keeps_irq_timing_contract(self):
        """只交叉编译真实main+最小链接桩，核查GCC控制流，不构建AM或声称硬件通过。"""
        compiler = shutil.which("riscv64-linux-gnu-gcc")
        if compiler is None:
            self.skipTest("no RV64 cross compiler")
        with tempfile.TemporaryDirectory(prefix="perf-main-cfg-") as temporary:
            directory = Path(temporary)
            (directory / "layout.h").write_text(
                '#define CASE_ID "07_02_ckks_hadd_l4_n1024"\n'
                '#define SCHEDULE_PROFILE "optimized"\n'
                '#define DEGREE 1024U\n#define LEVEL 4U\n#define WINDOW_LINES 128U\n'
                '#define IMAGE_LINES 128U\n#define GOLDEN_WORDS 64U\n'
                '#define INSTRUCTION_COUNT 1U\n#define DMA_COUNT 0U\n')
            stem = "frontend_ckks_hadd_l4_n1024"
            (directory / "program.h").write_text(
                f'int hpu_validate_{stem}(void);\nint hpu_run_{stem}(void);\n')
            (directory / "stubs.c").write_text(
                '#include <workload.h>\n#include <performance.h>\n#include <hpu/irq.h>\n'
                'volatile struct workload_progress workload_trace;\n'
                'void perf_cycle_enable(void) {}\nuint64_t perf_cycle_read(void) { return 0; }\n'
                'void phase_mark(unsigned p) {(void)p;}\nvoid prepare_image(void) {}\n'
                'int clear_completion(void) {return 0;}\n'
                'int expect_csr(uintptr_t a, uint32_t b) {(void)a; (void)b; return 0;}\n'
                'int wait_window(void) {return 0;}\nint irq_reset_events(void) {return 0;}\n'
                'int irq_open(void) {return 0;}\nvoid irq_close(void) {}\n'
                'uint32_t irq_event_count(void) {return 0;}\n'
                'uint32_t irq_handler_count(void) {return 0;}\n'
                'void irq_diagnose(const char *p, unsigned n) {(void)p; (void)n;}\n'
                'int performance_wait(void) {return irq_poll();}\nint check_results(void) {return 0;}\n'
                'volatile int stub_irq_flag;\n'
                '__attribute__((noinline)) int irq_poll(void) {return stub_irq_flag;}\n'
                'int check_memory(void) {return 0;}\nint case_pass(void) {return 0;}\n'
                'int case_fail_at(const char *p, unsigned n) {(void)p; (void)n; return 1;}\n'
                f'int hpu_validate_{stem}(void) {{return 0;}}\n'
                f'int hpu_run_{stem}(void) {{return 0;}}\n')
            am = build.ROOT.parents[1]
            source = build.ROOT / "src/07_performance/01_n1024/07_02_ckks_hadd_l4_n1024.c"
            elf = directory / "main.elf"
            subprocess.run([compiler, "-O2", "-std=gnu11", "-Wall", "-Wextra", "-Werror",
                            "-march=rv64gc", "-mabi=lp64d", "-mcmodel=medany", "-fno-pic",
                            "-no-pie", "-nostdlib", "-static", "-fno-builtin", "-DHPU_LOG_LEVEL=0",
                            "-DMEM_BASE=0x90000000ULL", '-DARCH_H="arch/riscv64-xs.h"',
                            f"-I{directory}", f"-I{build.ROOT / 'include'}",
                            f"-I{am / 'am'}", f"-I{am / 'am/include'}",
                            f"-I{am / 'libs/klib/include'}", "-Wl,-Ttext=0x80000000", "-Wl,-e,main",
                            str(source), str(directory / "stubs.c"), "-o", str(elf)], check=True)
            text = subprocess.check_output(["riscv64-linux-gnu-objdump", "-d", str(elf)], text=True)
            build.verify_timing(text, stem)


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="frontend-perf-build-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_six_scopes_cover_36_cases_without_overlap(self):
        rows = [row for degree in (1024, 8192) for profile in ("baseline",)
                for scheme in ("ckks", "bfv", "bgv") for row in build.select_specs(degree, profile, scheme)]
        self.assertEqual(len(rows), 36)
        self.assertEqual(len({row["case_id"] for row in rows}), 36)

    def test_retired_profiles_and_larger_degrees_are_rejected(self):
        for degree, profile in ((2048, "baseline"), (4096, "baseline"), (8192, "l16"), (16384, "baseline")):
            with self.subTest(degree=degree, profile=profile):
                with self.assertRaisesRegex(ValueError, "N1024/N8192 and level=4"):
                    build.select_specs(degree, profile, "ckks")

    def test_case_paths_do_not_leak_to_recursive_am_make(self):
        args = SimpleNamespace(work=self.root, am_home=build.ROOT.parents[1], arch="riscv64-xs",
                               cross="riscv64-linux-gnu-", wait_cycles=999)
        spec = {**build.select_specs(1024, "baseline", "ckks")[0], "variant": "optimized"}
        recorded = []
        def stop(command, **kwargs):
            recorded.extend(command)
            raise RuntimeError("captured")
        with patch.object(build, "run", side_effect=stop):
            with self.assertRaisesRegex(RuntimeError, "captured"):
                build.build_case(args, spec, self.root / "data", {}, "minimal")
        self.assertTrue(any(str(value).startswith("CASE_OBJ_DIR=") for value in recorded))
        self.assertTrue(any(str(value).startswith("CASE_BINARY=") for value in recorded))
        self.assertIn(f"CASE_DEGREE={spec['degree']}", recorded)
        self.assertIn(f"CASE_LEVEL={spec['level']}", recorded)
        self.assertFalse(any(str(value).startswith(("DST_DIR=", "BINARY=")) for value in recorded))

class EmbeddedDataTests(unittest.TestCase):
    def test_readonly_embedded_payload_is_compared_byte_for_byte(self):
        with tempfile.TemporaryDirectory(prefix="frontend-perf-elf-test-") as temporary:
            root = Path(temporary)
            contents = (("initial_image", "image.u32.bin", b"IMG0"),
                        ("golden_words", "golden.u32.bin", b"GLD0"),
                        ("writable_lines", "writable.u8.bin", b"\x01"))
            blob = bytearray(0x209)
            blob[:6] = b"\x7fELF\x02\x01"
            struct.pack_into("<H", blob, 18, 243)
            struct.pack_into("<QQ", blob, 32, 64, 120)
            struct.pack_into("<HHHH", blob, 54, 56, 1, 64, 2)
            struct.pack_into("<IIQQQQQQ", blob, 64, 1, 4, 0, 0x80000000, 0x80000000, len(blob), len(blob), 256)
            struct.pack_into("<IIQQQQIIQQ", blob, 184, 0, 1, 2, 0x80000100, 0x200, 9, 0, 0, 256, 0)
            listing, offset = [], 0
            for symbol, filename, payload in contents:
                (root / filename).write_bytes(payload)
                blob[0x200 + offset:0x200 + offset + len(payload)] = payload
                listing.append(f"{0x80000100 + offset:016x} {len(payload):016x} R {symbol}")
                offset += len(payload)
            elf = root / "probe.elf"
            elf.write_bytes(blob)
            meta = {"memory_base": "0x90000000", "minimum_ram_bytes": 536870912}
            with patch.object(build, "output", return_value="\n".join(listing)):
                build.verify_embedded(elf, root, meta, "unused-")
                (root / "golden.u32.bin").write_bytes(b"bad!")
                with self.assertRaisesRegex(ValueError, "embedded data differs"):
                    build.verify_embedded(elf, root, meta, "unused-")


if __name__ == "__main__":
    unittest.main()
