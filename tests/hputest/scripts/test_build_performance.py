"""验证07官方continuous profiling的主控制流、hooks和实际ELF；夹具不是硬件结果。"""
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import build_performance as build

STEM = "probe"
PSYNC = 0x7000005b
WORDS = [0x00b5002b, PSYNC, 0x0400405b, PSYNC, 0x00b5102b, PSYNC]
PROFILE = {"begin_instruction": 2, "end_instruction": 3, "sync_count": 3}


def assembly(name, base, operations):
    labels = {}
    cursor = base
    for operation in operations:
        if operation.endswith(":"):
            labels[operation[:-1]] = cursor
        else:
            cursor += 4
    output = [f"{base:08x} <{name}>:"]
    cursor = base
    for operation in operations:
        if operation.endswith(":"):
            continue
        for label, address in labels.items():
            operation = operation.replace("@" + label, f"{address:x} <{name}+0x{address-base:x}>")
        # 固定字码仅供CFG单测，不执行这些合成指令。
        word = operation.split()[0] if operation.startswith(("00b", "700", "040")) else "00000013"
        if word != "00000013":
            operation = ".word 0x" + word
        output.append(f"    {cursor:x}: {word} {operation}")
        cursor += 4
    return "\n".join(output) + "\n"


def main_operations():
    return [
        "jal 2000 <irq_reset_events>", "bnez a0,@fail",
        "jal 2100 <irq_open>", "bnez a0,@cleanup",
        "jal 2200 <irq_event_count>", "bnez a0,@cleanup",
        "jal 2300 <irq_handler_count>", "bnez a0,@cleanup",
        "jal 2400 <performance_profile_init>", "bnez a0,@cleanup", "jal 3000 <hpu_run_probe_profiled>",
        "jal 2500 <irq_close>", "jal 2600 <performance_profile_finish>", "bnez a0,@fail",
        "lui s1,0x8000", "lwu a5,28(s1)", "lwu a5,20(s1)", "lwu a5,24(s1)",
        "jal 2700 <check_results>", "jal 2800 <check_memory>", "j 2900 <case_pass>",
        "cleanup:", "jal 2500 <irq_close>", "fail:", "j 2a00 <case_fail>"]


def profile_operations(words=WORDS, profile=PROFILE):
    result = ["mv s0,a0", "mv s1,a1", "sd zero,0(s1)", "sd zero,8(s1)", "sw zero,16(s1)"]
    begin = 0
    for index, end in enumerate(position for position, word in enumerate(words) if word == PSYNC):
        segment = words[begin:end+1]
        result += [f"{word:08x}" for word in segment]
        result += ["ld a5,16(s0)", "ld a0,0(s0)", f"li a1,{index}", "jalr a5", "bnez a0,@error"]
        if end + 1 == profile["begin_instruction"] or end == profile["end_instruction"]:
            offset = 0 if end + 1 == profile["begin_instruction"] else 8
            result += ["ld a5,8(s0)", "ld a0,0(s0)", "jalr a5", f"sd a0,{offset}(s1)"]
        begin = end + 1
    return result + ["li a5,1", "sw a5,16(s1)", "li a0,0", "ret", "error:", "ret"]


def fixture(main=None, native=None):
    return (assembly("main", 0x1000, main_operations() if main is None else main) +
            assembly("hpu_run_probe_profiled", 0x3000, profile_operations() if native is None else native) +
            assembly("performance_profile_init", 0x4000,
                     ["auipc a5,0 # 4100 <performance_profile_cycle>",
                      "auipc a4,0 # 4200 <performance_profile_wait>", "ret"]) +
            assembly("performance_profile_cycle", 0x4100, ["jal 5000 <perf_cycle_read>", "ret"]) +
            assembly("performance_profile_wait", 0x4200, ["jal 5100 <wait_program>", "ret"]) +
            assembly("wait_program", 0x5100, ["jal 5200 <irq_poll>", "ret"]) +
            assembly("performance_profile_finish", 0x4300,
                     ["jal 2200 <irq_event_count>", "jal 2300 <irq_handler_count>", "ret"]))


def verify(text):
    build.verify_timing(text, STEM, WORDS, PROFILE)


class TimingTests(unittest.TestCase):
    def test_official_continuous_hooks_and_failed_arm_cleanup_are_accepted(self):
        verify(fixture())

    def test_gcc13_sext_counter_sources_are_preserved(self):
        operations = main_operations()
        operations.insert(5, "sext.w a0,a0")
        index = operations.index("jal 2300 <irq_handler_count>")
        operations[index+1:index+1] = ["sext.w a5,a0"]
        operations[index+2] = "bnez a5,@cleanup"
        verify(fixture(main=operations))

    def test_unknown_or_truncated_gcc13_counter_sources_are_rejected(self):
        for instruction in ("sext.w a0,t0", "andi a0,a0,255"):
            operations = main_operations()
            operations.insert(5, instruction)
            with self.subTest(instruction=instruction), self.assertRaisesRegex(ValueError, "ordering differs"):
                verify(fixture(main=operations))

    def test_missing_arm_finish_or_result_checks_are_rejected(self):
        for operation in ("jal 2100 <irq_open>", "bnez a0,@cleanup",
                          "jal 2400 <performance_profile_init>", "jal 2600 <performance_profile_finish>",
                          "lwu a5,20(s1)", "jal 2700 <check_results>", "jal 2800 <check_memory>"):
            operations = main_operations()
            operations[operations.index(operation)] = "nop"
            with self.subTest(operation=operation), self.assertRaisesRegex(ValueError, "ordering differs"):
                verify(fixture(main=operations))

    def test_old_unprofiled_entry_or_main_cycle_reads_are_rejected(self):
        for replacement in ("jal 3000 <hpu_run_probe>", "jal 5000 <perf_cycle_read>"):
            operations = main_operations()
            operations[operations.index("jal 3000 <hpu_run_probe_profiled>")] = replacement
            with self.subTest(replacement=replacement), self.assertRaisesRegex(ValueError, "ordering differs"):
                verify(fixture(main=operations))

    def test_every_psync_must_wait_and_check_callback_status(self):
        for index in (0, 1, 2):
            operations = profile_operations()
            location = operations.index(f"li a1,{index}")
            for offset in (1, 2):
                broken = list(operations)
                broken[location+offset] = "nop"
                with self.subTest(index=index, offset=offset), self.assertRaises(ValueError):
                    verify(fixture(native=broken))

    def test_callback_offsets_user_and_sync_index_cannot_be_changed(self):
        for original, replacement in (("ld a5,16(s0)", "ld a5,8(s0)"),
                                      ("ld a5,8(s0)", "ld a5,0(s0)"),
                                      ("ld a0,0(s0)", "li a0,0"),
                                      ("li a1,1", "li a1,0")):
            operations = profile_operations()
            operations[operations.index(original)] = replacement
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                verify(fixture(native=operations))

    def test_timestamp_stores_and_suffix_completion_are_required(self):
        for original, replacement in (("sd a0,0(s1)", "nop"), ("sd a0,8(s1)", "nop"),
                                      ("sw a5,16(s1)", "nop"), ("li a5,1", "li a5,2")):
            operations = profile_operations()
            operations[operations.index(original)] = replacement
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                verify(fixture(native=operations))
        operations = profile_operations()
        operations.remove("sw a5,16(s1)")
        operations.insert(operations.index("li a1,2"), "sw a5,16(s1)")
        with self.assertRaises(ValueError):
            verify(fixture(native=operations))

    def test_read_hook_before_preload_completion_is_rejected(self):
        operations = profile_operations()
        operations[operations.index("ld a5,16(s0)")] = "ld a5,8(s0)"
        with self.assertRaisesRegex(ValueError, "read hook"):
            verify(fixture(native=operations))

    def test_profile_wait_must_observe_real_isr(self):
        with self.assertRaisesRegex(ValueError, "real ISR"):
            verify(fixture().replace("<irq_poll>", "<read_status_only>"))

    def test_existing_internal_psync_stays_in_one_continuous_window(self):
        words = WORDS[:3] + [PSYNC, 0x0400405b] + WORDS[3:]
        profile = {"begin_instruction": 2, "end_instruction": 5, "sync_count": 4}
        body = assembly("hpu_run_probe_profiled", 0x3000, profile_operations(words, profile))
        build.verify_profile_entry(body, words, profile)

    def test_extra_timestamp_and_runtime_logging_are_rejected(self):
        operations = profile_operations()
        location = operations.index("sd a0,8(s1)")
        operations[location+1:location+1] = ["ld a5,8(s0)", "ld a0,0(s0)", "jalr a5"]
        with self.assertRaisesRegex(ValueError, "read hook"):
            verify(fixture(native=operations))
        with self.assertRaisesRegex(ValueError, "logging"):
            verify(fixture().replace("jal 5000 <perf_cycle_read>",
                                     "jal 5000 <perf_cycle_read>\n    4102: 000000ef jal 5300 <printf_>"))

    def test_actual_main_and_callback_abi_cross_compilation(self):
        """真实07 main/runtime+小型链接夹具；只验证编译/CFG，不执行HPU或构建AM。"""
        compiler = shutil.which("riscv64-linux-gnu-gcc")
        if compiler is None:
            self.skipTest("no RV64 cross compiler")
        with tempfile.TemporaryDirectory(prefix="profile-main-cfg-") as temporary:
            directory = Path(temporary)
            stem = "frontend_ckks_hadd_l4_n1024"
            (directory / "layout.h").write_text(
                '#define CASE_ID "07_02_ckks_hadd_l4_n1024"\n#define SCHEDULE_PROFILE "optimized"\n'
                '#define DEGREE 1024U\n#define LEVEL 4U\n#define WINDOW_LINES 128U\n'
                '#define IMAGE_LINES 128U\n#define GOLDEN_WORDS 64U\n'
                '#define INSTRUCTION_COUNT 6U\n#define DMA_COUNT 2U\n'
                '#define PROFILE_SYNC_COUNT 3U\n#define PROFILE_WINDOW_DLOAD_COUNT 0U\n'
                '#define PROFILE_WINDOW_DSTORE_COUNT 0U\n#define PROFILE_PREFIX_DLOAD_COUNT 1U\n'
                '#define PROFILE_SUFFIX_DSTORE_COUNT 1U\n#define PROFILE_PREFIX_DSTORE_COUNT 0U\n'
                '#define PROFILE_SUFFIX_DLOAD_COUNT 0U\n')
            (directory / "program.h").write_text(
                '#ifndef UNIT_PROFILE_H\n#define UNIT_PROFILE_H\n#include <stdint.h>\n#include <stddef.h>\n'
                'typedef struct {void *user; uint64_t (*read_cycles)(void *); '
                'int (*wait_complete)(void *, size_t);} hpu_execution_profile_hooks_t;\n'
                'typedef struct {uint64_t start_cycles, end_cycles; int valid;} hpu_execution_profile_sample_t;\n'
                f'int hpu_run_{stem}_profiled(const hpu_execution_profile_hooks_t *, hpu_execution_profile_sample_t *);\n#endif\n')
            native = ['#include "program.h"',
                      f'int hpu_run_{stem}_profiled(const hpu_execution_profile_hooks_t *hooks, hpu_execution_profile_sample_t *sample) {{',
                      'if (sample) {sample->start_cycles=0; sample->end_cycles=0; sample->valid=0;}',
                      'if (!hooks || !sample || !hooks->read_cycles || !hooks->wait_complete) return -1;']
            for index, segment in enumerate((WORDS[:2], WORDS[2:4], WORDS[4:])):
                native.append('__asm__ volatile(' + ''.join(f'".word 0x{word:08x}\\n\\t"' for word in segment) + ':::"x10","x11","memory");')
                native.append(f'{{int status=hooks->wait_complete(hooks->user,{index}); if(status) return status;}}')
                if index < 2:
                    native.append(f'sample->{"start" if index == 0 else "end"}_cycles=hooks->read_cycles(hooks->user);')
            native.append('sample->valid=1; return 0;}')
            (directory / "program.c").write_text('\n'.join(native))
            (directory / "stubs.c").write_text(
                '#include <workload.h>\n#include <performance.h>\n#include <hpu/irq.h>\n'
                'volatile struct workload_progress workload_trace; volatile int stub_irq_flag;\n'
                'void perf_cycle_enable(void) {}\nuint64_t perf_cycle_read(void) {return 0;}\n'
                'void phase_mark(unsigned p) {(void)p;}\nvoid prepare_image(void) {}\n'
                'int clear_completion(void) {return 0;}\n'
                'int expect_csr(uintptr_t a,uint32_t b) {(void)a;(void)b;return 0;}\n'
                'int wait_window(void) {return 0;}\nint irq_reset_events(void) {return 0;}\n'
                'int irq_open(void) {return 0;}\nvoid irq_close(void) {}\nint irq_rearm(void) {return 0;}\n'
                'uint32_t irq_event_count(void) {return stub_irq_flag;}\n'
                'uint32_t irq_handler_count(void) {return stub_irq_flag;}\n'
                'void irq_diagnose(const char *p,unsigned n) {(void)p;(void)n;}\n'
                '__attribute__((noinline)) int irq_poll(void) {return stub_irq_flag;}\n'
                'int wait_program(void) {return irq_poll();}\nint check_results(void) {return 0;}\n'
                'int check_memory(void) {return 0;}\nint case_pass(void) {return 0;}\n'
                'int case_fail_at(const char *p,unsigned n) {(void)p;(void)n;return 1;}\n')
            am = build.ROOT.parents[1]
            elf = directory / "main.elf"
            flags = [compiler, "-O2", "-std=gnu11", "-Wall", "-Wextra", "-Werror",
                     "-march=rv64gc", "-mabi=lp64d", "-mcmodel=medany", "-fno-pic",
                     "-no-pie", "-nostdlib", "-static", "-fno-builtin", "-DHPU_LOG_LEVEL=0",
                     "-DMEM_BASE=0x90000000ULL", '-DARCH_H="arch/riscv64-xs.h"',
                     f"-I{directory}", f"-I{build.ROOT / 'include'}", f"-I{am / 'am'}",
                     f"-I{am / 'am/include'}", f"-I{am / 'libs/klib/include'}",
                     "-Wl,-Ttext=0x80000000", "-Wl,-e,main"]
            subprocess.run(flags + [str(build.ROOT / "src/07_performance/01_n1024/07_02_ckks_hadd_l4_n1024.c"),
                                    str(build.ROOT / "runtime/native/performance.c"), str(directory / "program.c"),
                                    str(directory / "stubs.c"), "-o", str(elf)], check=True)
            text = subprocess.check_output(["riscv64-linux-gnu-objdump", "-d", str(elf)], text=True)
            build.verify_timing(text, stem, WORDS, PROFILE)


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
