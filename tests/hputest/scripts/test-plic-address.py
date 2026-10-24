#!/usr/bin/env python3
"""编译实际平台/PLIC/HPU中断代码，用主机MMIO桩验证地址及两轮中断。

仅替换MMIO原语和RISC-V内联汇编，不模拟RTL、PLIC硬件或真实中断时序。
"""

from pathlib import Path
import os
import re
import shlex
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
AM = ROOT.parents[1]

AM_HEADER = r"""
#ifndef MOCK_AM_H
#define MOCK_AM_H
#include <stdint.h>
typedef struct { int unused; } _Context;
typedef struct { int event; } _Event;
enum { _EVENT_IRQ_IODEV = 1 };
void _intr_write(int enable);
int _cte_init(void *unused);
#endif
"""
CSR_HEADER = r"""
#include <stdint.h>
#define CSR_STATUS 0x08000014U
#define CSR_FAULT 0x08000018U
#define CSR_IRQ 0x0800001cU
#define STATUS_VALID 1U
#define STATUS_BUSY 2U
#define STATUS_FAULT 4U
#define FAULT_VALID 1U
#define IRQ_LEVEL 1U
#define TIMEOUT 64U
uint32_t csr_read(uintptr_t address);
void csr_write(uintptr_t address, uint32_t value);
"""
HARNESS = r"""
#include <assert.h>
#include <stdlib.h>
#include <stdint.h>
struct cell { uintptr_t address; uint32_t value; };
static struct cell cells[512];
static unsigned used, plic_accesses, claims, completions, init_calls, csr_accesses;
static unsigned irq_reads, clear_after;
static int enabled, bad_readback, clearing, expect_open_clear, cte_failure, allow_stuck_complete;
static uint32_t hpu_level, hpu_status = 1U, hpu_fault;
int g_config_disable_timer;
static struct cell *cell(uintptr_t address) {
    /* 旧0x04窗口会立即触发断言，不可能靠默认读回0蒙混通过。 */
    assert(address >= 0x3c000000UL && address <= 0x3c201004UL);
    for (unsigned i = 0; i < used; ++i) if (cells[i].address == address) return &cells[i];
    assert(used < 512U);
    cells[used].address = address;
    return &cells[used++];
}
static uint32_t host_read(uintptr_t address) {
    ++plic_accesses;
    if (address == 0x3c201004UL) ++claims;
    if (bad_readback && address == 0x3c000404UL) return 0U;
    return cell(address)->value;
}
static void host_write(uintptr_t address, uint32_t value) {
    ++plic_accesses;
    if (address == 0x3c201004UL) {
        assert(value != 0U);
        if (value == 257U && !allow_stuck_complete)
            assert(hpu_level == 0U); /* 正常路径先清HPU电平，再complete PLIC。 */
        ++completions;
    }
    cell(address)->value = value;
}

/* 这里插入实际的 plic.c、hpu_irq.c，仅把MMIO和ISA原语换成上述桩。 */
@PRODUCTION@

static _Context *(*registered)(_Event, _Context *);
void seip_handler_reg(_Context *(*function)(_Event, _Context *)) { registered = function; }
void _intr_write(int value) { enabled = value; }
int _cte_init(void *unused) {
    (void)unused;
    assert(g_config_disable_timer == 1);
    ++init_calls;
    assert(init_calls == 1U); /* 再次调用就重现S态重入M初始化根因。 */
    if (cte_failure) return -1;
    plic_init(257U, 2U);
    for (unsigned source = 1U; source <= 257U; ++source)
        assert(cell(0x3c000000UL + 4U * source)->value == 0U);
    for (unsigned context = 0U; context < 2U; ++context) {
        for (unsigned word = 0U; word < 9U; ++word)
            assert(cell(0x3c002000UL + 0x80U * context + 4U * word)->value == 0U);
        assert(cell(0x3c200000UL + 0x1000U * context)->value == 7U);
    }
    return 0;
}
uint32_t csr_read(uintptr_t address) {
    ++csr_accesses;
    if (address == CSR_STATUS) return hpu_status;
    if (address == CSR_FAULT) return hpu_fault;
    assert(address == CSR_IRQ);
    if (clearing) {
        ++irq_reads;
        if (expect_open_clear) {
            assert(enabled == 0);
            assert(cell(0x3c000404UL)->value == 0U);
            assert((cell(0x3c0020a0UL)->value & 2U) == 0U);
        }
        if (clear_after != 0U && irq_reads >= clear_after) hpu_level = 0U;
    }
    return hpu_level;
}
void csr_write(uintptr_t address, uint32_t value) {
    ++csr_accesses;
    assert(address == CSR_IRQ);
    assert(value == IRQ_LEVEL || value == 0U);
    if (value == IRQ_LEVEL) {
        clearing = 1;
        irq_reads = 0U;
    } else {
        clearing = 0;
    }
}
int main(int argc, char **argv) {
    assert(argc == 2);
    _Static_assert(PLIC_PRIORITY_ADDR == 0x3c000404UL, "priority source257/index256");
    _Static_assert(PLIC_ENABLE_ADDR == 0x3c0020a0UL, "enable source257/context1");
    _Static_assert(PLIC_THRESHOLD_ADDR == 0x3c201000UL, "threshold context1");
    _Static_assert(PLIC_CLAIM_ADDR == 0x3c201004UL, "claim context1");
    clear_after = 1U;
    if (atoi(argv[1]) == 2) {
        bad_readback = 1;
        assert(irq_open() == 1 && enabled == 0);
        assert(claims == 0 && completions == 0);
        return 0;
    }
    if (atoi(argv[1]) == 3) {
        hpu_level = IRQ_LEVEL;
        clear_after = 3U;
        expect_open_clear = 1;
        assert(irq_open() == 0);
        expect_open_clear = 0;
        assert(irq_reads == 3U && hpu_level == 0U && enabled == 1);
        irq_close();
        return 0;
    }
    if (atoi(argv[1]) == 4) {
        hpu_level = IRQ_LEVEL;
        clear_after = 0U;
        expect_open_clear = 1;
        assert(irq_open() == 1);
        expect_open_clear = 0;
        assert(irq_reads == TIMEOUT / 16U);
        assert(hpu_level == IRQ_LEVEL && enabled == 0);
        return 0;
    }
    if (atoi(argv[1]) == 12) {
        cte_failure = 1;
        assert(irq_open() == 1 && enabled == 0);
        assert(irq_open() == 1 && init_calls == 1U);
        assert(irq_cte_init_count() == 1U);
        return 0;
    }
    assert(irq_open() == 0 && enabled == 1 && init_calls == 1U);
    assert(cell(0x3c000404UL)->value == 1U);
    assert(cell(0x3c0020a0UL)->value == 2U);
    assert(cell(0x3c201000UL)->value == 0U);
    cell(0x3c0020a0UL)->value |= 8U; /* close必须保留其它源enable位。 */
    if (atoi(argv[1]) == 13) {
        assert(irq_open() == 0 && init_calls == 1U && enabled == 1);
        assert(irq_poll() == 0 && irq_cte_init_count() == 1U);
    }
    if (atoi(argv[1]) == 5) {
        /* MMIO电平/idle不能代替一次ISR，poll和超时诊断不得访问MMIO/claim。 */
        unsigned before = plic_accesses, csr_before = csr_accesses;
        hpu_level = IRQ_LEVEL;
        assert(irq_reset_events() == 1);
        assert(irq_poll() == 0 && irq_wait() == 1);
        irq_diagnose("host-timeout", TIMEOUT);
        assert(irq_event_count() == 0U && irq_handler_count() == 0U);
        assert(plic_accesses == before && csr_accesses == csr_before);
        assert(claims == 0U && completions == 0U);
        irq_close();
        return 0;
    }
    if (atoi(argv[1]) >= 6 && atoi(argv[1]) <= 11) {
        const unsigned mode = (unsigned)atoi(argv[1]);
        _Context context = {0};
        cell(0x3c201004UL)->value = mode == 7U ? 259U : 257U;
        hpu_level = mode == 8U || mode == 7U ? 0U : IRQ_LEVEL;
        if (mode == 9U) { clear_after = 0U; allow_stuck_complete = 1; }
        if (mode == 10U) hpu_status |= STATUS_FAULT;
        if (mode == 11U) hpu_fault = FAULT_VALID;
        assert(registered((_Event){mode == 6U ? _EVENT_IRQ_IODEV + 1 : _EVENT_IRQ_IODEV}, &context) == &context);
        assert(irq_poll() == -1 && irq_wait() == 1);
        assert(irq_handler_count() == 1U && irq_event_count() == 0U);
        assert(claims == (mode == 6U ? 0U : 1U));
        assert(completions == (mode == 6U ? 0U : 1U));
        if (mode == 9U) assert(irq_clear_polls == TIMEOUT / 16U && hpu_level == IRQ_LEVEL);
        unsigned before = plic_accesses, csr_before = csr_accesses;
        irq_diagnose("host-error", 1U);
        assert(plic_accesses == before && csr_accesses == csr_before);
        irq_close();
        return 0;
    }
    if (atoi(argv[1]) == 14 || atoi(argv[1]) == 15) {
        _Context context = {0};
        if (atoi(argv[1]) == 15) {
            cell(0x3c201004UL)->value = 0U;
            assert(registered((_Event){_EVENT_IRQ_IODEV}, &context) == &context);
            assert(irq_poll() == -1 && claims == 1U && completions == 0U);
            assert(irq_event_count() == 0U && irq_handler_count() == 1U);
        } else {
            cell(0x3c201004UL)->value = 257U;
            hpu_level = IRQ_LEVEL;
            assert(registered((_Event){_EVENT_IRQ_IODEV}, &context) == &context);
            assert(irq_poll() == 1 && irq_event_count() == 1U);
            hpu_level = IRQ_LEVEL;
            assert(registered((_Event){_EVENT_IRQ_IODEV}, &context) == &context);
            assert(irq_poll() == -1 && irq_event_count() == 1U);
            assert(irq_handler_count() == 2U && claims == 2U && completions == 2U);
        }
        irq_close();
        return 0;
    }
    for (unsigned scenario = 0U; scenario < 3U; ++scenario) {
        if (scenario != 0U) assert(irq_open() == 0 && enabled == 1);
        assert(init_calls == 1U && irq_cte_init_count() == 1U);
        assert(irq_reset_events() == 1); /* opened时不允许抹掉ISR计数。 */
        for (unsigned round = 0U; round < 2U; ++round) {
            _Context context = {0};
            unsigned expected = scenario * 2U + round + 1U;
            assert(irq_poll() == 0);
            cell(0x3c201004UL)->value = 257U;
            hpu_level = IRQ_LEVEL;
            assert(registered((_Event){_EVENT_IRQ_IODEV}, &context) == &context);
            assert(irq_poll() == 1 && irq_wait() == 0 && hpu_level == 0U);
            assert(irq_event_count() == expected && irq_handler_count() == expected);
            assert(claims == expected && completions == expected);
            if (round == 0U) {
                unsigned before = plic_accesses;
                assert(irq_rearm() == 0 && enabled == 1);
                assert(plic_accesses == before); /* 不重新claim/初始化。 */
                assert(cell(0x3c000404UL)->value == 1U);
                assert(cell(0x3c0020a0UL)->value == 10U);
            }
        }
        irq_close();
        assert(enabled == 0 && cell(0x3c000404UL)->value == 0U);
        assert(cell(0x3c0020a0UL)->value == 8U);
    }
    assert(init_calls == 1U && irq_event_count() == 6U);
    assert(irq_rearm() == 1 && enabled == 0); /* close后不允许凭旧done重新武装。 */
    assert(irq_reset_events() == 0 && irq_cte_init_count() == 1U);
    assert(irq_event_count() == 0U && irq_handler_count() == 0U && irq_poll() == 0);
    assert(irq_open() == 0 && init_calls == 1U); /* 显式清计数也不能重置CTE。 */
    irq_close();
    return 0;
}
"""


class PlicAddressTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build = ROOT / "build"
        build.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="plic-address-", dir=build)
        cls.addClassCleanup(temporary.cleanup)
        cls.directory = Path(temporary.name)
        (cls.directory / "hpu").mkdir()
        headers = {"am.h": AM_HEADER, "klib.h": "#include <stdio.h>\n",
                   "isa_mock.h": "", "hpu/csr.h": CSR_HEADER,
                   "platform.h": CSR_HEADER.replace("#define TIMEOUT 64U\n", ""),
                   "hpu/layout.h": "",
                   "xsextra.h": '#include <am.h>\nvoid seip_handler_reg(_Context *(*handler)(_Event, _Context *));\n'}
        for name, contents in headers.items():
            (cls.directory / name).write_text(contents, encoding="utf-8")
        cls.compiler = shlex.split(os.environ.get("HOST_CC", "cc")) + [
            "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            "-I", str(cls.directory), "-I", str(AM / "am/src/xs/include"),
            "-I", str(ROOT / "include"), '-DISA_H="isa_mock.h"']
        plic = (AM / "am/src/xs/isa/riscv/plic.c").read_text()
        plic = re.sub(r"^#define READ_WORD\(addr\).*$", "#define READ_WORD(addr) host_read(addr)", plic, flags=re.M)
        plic = re.sub(r"^#define WRITE_WORD\(addr, data\).*$", "#define WRITE_WORD(addr, data) host_write(addr, data)", plic, flags=re.M)
        irq = (ROOT / "src/common/hpu_irq.c").read_text()
        irq, reads = re.subn(r"static uint32_t mmio_read32\([^)]*\) \{.*?\n\}",
                            "static uint32_t mmio_read32(uint64_t address) { return host_read(address); }", irq, flags=re.S)
        irq, writes = re.subn(r"static void mmio_write32\([^)]*\) \{.*?\n\}",
                             "static void mmio_write32(uint64_t address, uint32_t data) { host_write(address, data); }", irq, flags=re.S)
        irq, asm = re.subn(r'__asm__ volatile\([^;]*\);', '(void)0;', irq)
        assert (reads, writes, asm) == (1, 1, 5), "hardware seam changed; review test adapter"
        source = cls.directory / "irq_test.c"
        cls.source = source
        source.write_text(HARNESS.replace("@PRODUCTION@", plic + "\n" + irq), encoding="utf-8")
        cls.binaries = []
        for level in (0, 1, 2):
            binary = cls.directory / f"irq-level{level}"
            subprocess.run(cls.compiler + ["-D__ARCH_RISCV64_XS", "-DLINKNAN_HPU_IT=1",
                                           f"-DHPU_LOG_LEVEL={level}", str(source), "-o", str(binary)], check=True)
            cls.binaries.append(binary)

    def test_init_open_two_interrupts_rearm_and_close_use_platform_base(self):
        for binary in self.binaries:
            subprocess.run([str(binary), "1"], check=True, capture_output=True)

    def test_pending_poll_and_wait_cannot_substitute_mmio_or_timer_for_an_isr(self):
        for binary in self.binaries:
            subprocess.run([str(binary), "5"], check=True, capture_output=True)

    def test_wrong_event_claim_level_clear_and_hpu_fault_cannot_complete_successfully(self):
        for binary in self.binaries:
            for scenario in range(6, 12):
                with self.subTest(level=binary.name, scenario=scenario):
                    subprocess.run([str(binary), str(scenario)], check=True, capture_output=True)

    def test_failed_cte_attempt_is_not_reentered(self):
        for binary in self.binaries:
            subprocess.run([str(binary), "12"], check=True, capture_output=True)

    def test_repeated_open_without_close_does_not_reenter_cte(self):
        for binary in self.binaries:
            subprocess.run([str(binary), "13"], check=True, capture_output=True)

    def test_duplicate_unarmed_event_and_zero_claim_are_not_successes(self):
        for binary in self.binaries:
            for scenario in (14, 15):
                with self.subTest(level=binary.name, scenario=scenario):
                    subprocess.run([str(binary), str(scenario)], check=True, capture_output=True)

    def test_native_irq_uses_platform_header_without_n4096_fixture(self):
        flags = ["-D__ARCH_RISCV64_XS", "-DLINKNAN_HPU_IT=1", "-DHPU_NATIVE_IRQ=1", "-DHPU_LOG_LEVEL=1"]
        binary = self.directory / "irq-native"
        subprocess.run(self.compiler + flags + [str(self.source), "-o", str(binary)], check=True)
        subprocess.run([str(binary), "1"], check=True, capture_output=True)
        dependencies = subprocess.check_output(self.compiler + flags + ["-M", str(self.source)], text=True)
        self.assertIn("platform.h", dependencies)
        self.assertNotIn("hpu/csr.h", dependencies)
        self.assertNotIn("hpu/layout.h", dependencies)
        self.assertNotIn("inline_asm_mm_delivery.h", dependencies)

    def test_priority_readback_failure_does_not_claim_or_enable_interrupts(self):
        for binary in self.binaries:
            subprocess.run([str(binary), "2"], check=True, capture_output=True)

    def test_stale_irq_is_cleared_before_interrupts_are_enabled(self):
        for binary in self.binaries:
            subprocess.run([str(binary), "3"], check=True, capture_output=True)

    def test_stale_irq_timeout_keeps_interrupts_disabled(self):
        for binary in self.binaries:
            subprocess.run([str(binary), "4"], check=True, capture_output=True)

    def test_platform_header_variants(self):
        source = self.directory / "platform.c"
        source.write_text('#include <xs.h>\n_Static_assert(PLIC_BASE_ADDR == EXPECTED_BASE, "base");\n'
                          'int main(void) { return 0; }\n', encoding="utf-8")
        for arch, hpu, expected in (("__ARCH_RISCV64_XS", True, "0x3c000000UL"),
                                    ("__ARCH_RISCV64_XS", False, "0x3c000000UL"),
                                    ("__ARCH_RISCV64_XS_SOUTHLAKE", True, "0x1f1c000000UL")):
            subprocess.run(self.compiler + [f"-D{arch}", f"-DEXPECTED_BASE={expected}"] +
                           (["-DLINKNAN_HPU_IT=1"] if hpu else []) +
                           [str(source), "-o", str(self.directory / "platform")], check=True)


if __name__ == "__main__":
    unittest.main()
