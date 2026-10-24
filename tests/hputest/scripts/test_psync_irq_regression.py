"""实际03_08 main+IRQ公共层的host控制流回归，不执行HPU算术或证明硬件时序。"""
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "src/03_instructions/03_08_psync_l4_n1024.c"

CSR = r"""
#ifndef MOCK_CSR_H
#define MOCK_CSR_H
#include <stdint.h>
#define CSR_BASE_LO 0x08000000U
#define CSR_BASE_HI 0x08000004U
#define CSR_SIZE_LO 0x08000008U
#define CSR_SIZE_HI 0x0800000cU
#define CSR_COMMIT 0x08000010U
#define CSR_STATUS 0x08000014U
#define CSR_FAULT 0x08000018U
#define CSR_IRQ 0x0800001cU
#define STATUS_VALID 1U
#define STATUS_BUSY 2U
#define STATUS_FAULT 4U
#define FAULT_VALID 1U
#define IRQ_LEVEL 1U
#define COMMIT 1U
#define TIMEOUT 64U
uint32_t csr_read(uintptr_t address);
void csr_write(uintptr_t address, uint32_t value);
#endif
"""

WORKLOAD = r"""
#ifndef MOCK_WORKLOAD_H
#define MOCK_WORKLOAD_H
#include <hpu/csr.h>
#define DEGREE 1024U
#define LEVEL 4U
#define LINE_WORDS 64U
#define IMAGE_LINES 129U
#define WINDOW_LINES 128U
#define OUTPUT_COUNT 8U
#define MEM_BASE UINT64_C(0x87000000)
#define CASE_ID "03_08_psync_l4_n1024"
enum { PHASE_PREPARE, PHASE_CONFIGURE, PHASE_ISSUE, PHASE_WAIT, PHASE_COMPARE };
struct output_span { unsigned line, words, golden_word, modulus, step, component, modulus_id; };
struct progress { uint32_t errors, first_line, first_word, actual, expected; };
extern volatile struct progress workload_trace;
extern const struct output_span outputs[OUTPUT_COUNT];
extern const uint32_t initial_image[IMAGE_LINES * LINE_WORDS], golden_words[8U * DEGREE];
void phase_mark(unsigned phase);
void prepare_image(void);
void invalidate_lines(unsigned lines);
volatile uint32_t *line_ptr(unsigned line);
int clear_completion(void);
int expect_csr(uintptr_t address, uint32_t value);
int wait_window(void);
int wait_program(void);
int check_memory(void);
int case_fail_at(const char *source, unsigned line);
int case_pass(void);
#endif
"""

HARNESS = r"""
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <am.h>
#include <workload.h>
struct cell { uintptr_t address; uint32_t value; };
static struct cell plic[8];
static unsigned used, mode, init_calls, registrations, prepares, programs, waits, guards;
static unsigned claims, completes, invalidations;
static uint32_t config[4], level, fault;
static int enabled, in_handler, clearing;
static _Context *(*registered)(_Event, _Context *);
static void fire_completion(void);
int g_config_disable_timer;

static struct cell *cell(uintptr_t address) {
    assert(address == 0x3c000404UL || address == 0x3c0020a0UL ||
           address == 0x3c201000UL || address == 0x3c201004UL);
    for (unsigned index = 0; index < used; ++index)
        if (plic[index].address == address) return &plic[index];
    assert(used < 8U);
    plic[used].address = address;
    return &plic[used++];
}
static uint32_t host_read(uintptr_t address) {
    if (address == 0x3c201004UL) ++claims;
    return cell(address)->value;
}
static void host_write(uintptr_t address, uint32_t value) {
    if (address == 0x3c201004UL) {
        assert(value == 257U);
        if (mode != 4U) assert(level == 0U);
        ++completes;
        cell(address)->value = 0U;
    } else cell(address)->value = value;
}

@IRQ_IMPLEMENTATION@

volatile struct progress workload_trace;
static uint32_t memory[IMAGE_LINES * LINE_WORDS];
const uint32_t initial_image[IMAGE_LINES * LINE_WORDS] = {
    [0 ... IMAGE_LINES * LINE_WORDS - 1] = UINT32_MAX
};
const uint32_t golden_words[8U * DEGREE] = {[0 ... 8U * DEGREE - 1] = 3U};
#ifndef HOST_FIRST_Q
#define HOST_FIRST_Q 17U
#endif
const struct output_span outputs[OUTPUT_COUNT] = {
    {0, DEGREE, 0, HOST_FIRST_Q, 0, 0, 0}, {16, DEGREE, DEGREE, 19, 0, 0, 1},
    {32, DEGREE, 2U * DEGREE, 23, 0, 0, 2}, {48, DEGREE, 3U * DEGREE, 29, 0, 0, 3},
    {64, DEGREE, 4U * DEGREE, 17, 0, 1, 0}, {80, DEGREE, 5U * DEGREE, 19, 0, 1, 1},
    {96, DEGREE, 6U * DEGREE, 23, 0, 1, 2}, {112, DEGREE, 7U * DEGREE, 29, 0, 1, 3}
};

void _intr_write(int value) {
    enabled = value;
    if (value == 1 && mode == 9U && programs == 0U && irq_event_count() == 0U)
        fire_completion(); /* 武装时突然出现的旧事件不能算成本轮程序完成。 */
}
int _cte_init(void *unused) {
    (void)unused;
    assert(g_config_disable_timer == 1);
    assert(++init_calls == 1U); /* 跨三个scenario不得再次进入M态初始化。 */
    return 0;
}
void seip_handler_reg(_Context *(*callback)(_Event, _Context *)) {
    registered = callback;
    ++registrations;
}
uint32_t csr_read(uintptr_t address) {
    if (address >= CSR_BASE_LO && address <= CSR_SIZE_HI)
        return config[(address - CSR_BASE_LO) / 4U];
    if (address == CSR_STATUS) return STATUS_VALID;
    if (address == CSR_FAULT) return fault;
    assert(address == CSR_IRQ);
    if (clearing && !(mode == 4U && in_handler)) level = 0U;
    return level;
}
void csr_write(uintptr_t address, uint32_t value) {
    if (address >= CSR_BASE_LO && address <= CSR_SIZE_HI) {
        config[(address - CSR_BASE_LO) / 4U] = value;
    } else if (address == CSR_FAULT) {
        fault &= ~value;
    } else if (address == CSR_COMMIT) {
        assert(value == COMMIT);
    } else {
        assert(address == CSR_IRQ);
        assert(value == IRQ_LEVEL || value == 0U);
        clearing = value == IRQ_LEVEL;
    }
}
static void fire_completion(void) {
    _Context context = {0};
    assert(enabled && registered != NULL);
    level = mode == 6U ? 0U : IRQ_LEVEL;
    cell(0x3c201004UL)->value = 257U;
    in_handler = 1;
    assert(registered((_Event){_EVENT_IRQ_IODEV}, &context) == &context);
    in_handler = 0;
}
void phase_mark(unsigned phase) { (void)phase; }
void prepare_image(void) {
    ++prepares;
    memcpy(memory, initial_image, sizeof(memory));
    workload_trace = (struct progress){0};
}
void invalidate_lines(unsigned lines) { assert(lines == IMAGE_LINES); ++invalidations; }
volatile uint32_t *line_ptr(unsigned line) { assert(line < IMAGE_LINES); return memory + line * LINE_WORDS; }
int clear_completion(void) { return irq_clear_and_verify(); }
int expect_csr(uintptr_t address, uint32_t expected) { return csr_read(address) != expected; }
int wait_window(void) { return 0; }
int wait_program(void) { ++waits; return irq_poll() != 1; }
int check_memory(void) {
    ++guards;
    for (unsigned index = WINDOW_LINES * LINE_WORDS; index < IMAGE_LINES * LINE_WORDS; ++index)
        if (memory[index] != initial_image[index]) return 1;
    return 0;
}
int case_fail_at(const char *source, unsigned line) { assert(source != NULL && line != 0U); return 1; }
int case_pass(void) { return 0; }

static int native_prefix(unsigned scenario) {
    assert(scenario == programs / 2U); /* 真实case必须按idle×2、DMA×2、compute×2调用三个入口。 */
    ++programs;
    if (mode == 8U) return -4;
    if (scenario != 0U) {
        for (unsigned index = 0U; index < OUTPUT_COUNT; ++index) {
            const struct output_span *out = &outputs[index];
            if (out->component != scenario - 1U) continue;
            memcpy(memory + out->line * LINE_WORDS, golden_words + out->golden_word,
                   out->words * sizeof(uint32_t));
        }
    }
    if (scenario == 1U && mode == 2U) memory[outputs[4].line * LINE_WORDS] = 7U;
    if (scenario == 2U && mode == 3U) memory[outputs[4].line * LINE_WORDS] = 4U;
    if (scenario == 1U && mode == 7U) memory[WINDOW_LINES * LINE_WORDS] = 0U;
    if (mode == 1U) level = IRQ_LEVEL; /* 只有MMIO完成而没有ISR，必须失败。 */
    else fire_completion();
    if (mode == 5U) fire_completion();
    return 0;
}
int hpu_run_instruction_psync_l4_n1024_idle(void) { return native_prefix(0U); }
int hpu_run_instruction_psync_l4_n1024_dma(void) { return native_prefix(1U); }
int hpu_run_instruction_psync_l4_n1024_compute(void) { return native_prefix(2U); }

#define main psync_case_main
#include "@CASE_SOURCE@"
#undef main

int main(int argc, char **argv) {
    assert(argc == 2);
    mode = (unsigned)atoi(argv[1]);
    cell(0x3c0020a0UL)->value = 8U;
    const int result = psync_case_main();
    assert(init_calls == 1U && irq_cte_init_count() == 1U);
    assert(enabled == 0 && cell(0x3c000404UL)->value == 0U);
    assert(cell(0x3c0020a0UL)->value == 8U);
    if (mode == 0U) {
        assert(result == 0 && registrations == 3U && prepares == 6U && programs == 6U);
        assert(waits == 6U && guards == 6U && invalidations == 6U);
        assert(irq_event_count() == 6U && irq_handler_count() == 6U);
        assert(claims == 6U && completes == 6U && level == 0U);
    } else {
        assert(result == 1);
        if (mode == 1U) assert(irq_event_count() == 0U && claims == 0U);
        if (mode == 2U) assert(programs == 3U && workload_trace.expected == UINT32_MAX);
        if (mode == 3U) assert(programs == 5U && workload_trace.expected == 3U);
        if (mode == 4U) assert(level == IRQ_LEVEL && irq_poll() == -1 && completes == 1U);
        if (mode == 5U) assert(irq_event_count() == 1U && irq_handler_count() == 2U);
        if (mode == 6U) assert(irq_poll() == -1 && irq_event_count() == 0U);
        if (mode == 7U) assert(programs == 3U && guards == 3U);
        if (mode == 8U) assert(programs == 1U && waits == 0U);
        if (mode == 9U) assert(programs == 0U && irq_event_count() == 1U);
        if (mode == 10U) assert(programs == 3U && workload_trace.expected == 3U && workload_trace.actual == 3U);
    }
    return 0;
}
"""


class PsyncIrqRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent = ROOT / "build/host-tests"
        parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(prefix="psync-six-rounds-", dir=parent)
        cls.addClassCleanup(cls.temporary.cleanup)
        directory = Path(cls.temporary.name)
        (directory / "hpu").mkdir()
        headers = {
            "am.h": "#ifndef MOCK_AM_H\n#define MOCK_AM_H\ntypedef struct { int unused; } _Context;\n"
                    "typedef struct { int event; } _Event;\nenum { _EVENT_IRQ_IODEV = 1 };\n"
                    "void _intr_write(int); int _cte_init(void *);\n#endif\n",
            "xsextra.h": "#include <am.h>\nvoid seip_handler_reg(_Context *(*)(_Event, _Context *));\n",
            "xs.h": "#define PLIC_BASE_ADDR 0x3c000000UL\n",
            "klib.h": "#include <stdio.h>\n",
            "hpu/csr.h": CSR,
            "hpu/layout.h": "",
            "workload.h": WORKLOAD,
            "program.h": "",
        }
        for prefix in ("idle", "dma", "compute"):
            stem = "instruction_psync_l4_n1024_" + prefix
            headers[stem + ".h"] = f"int hpu_run_{stem}(void);\n"
        for name, contents in headers.items():
            (directory / name).write_text(contents)
        irq = (ROOT / "src/common/hpu_irq.c").read_text()
        irq, reads = re.subn(r"static uint32_t mmio_read32\([^)]*\) \{.*?\n\}",
                            "static uint32_t mmio_read32(uint64_t address) { return host_read(address); }", irq, flags=re.S)
        irq, writes = re.subn(r"static void mmio_write32\([^)]*\) \{.*?\n\}",
                             "static void mmio_write32(uint64_t address, uint32_t data) { host_write(address, data); }", irq, flags=re.S)
        irq, assembly = re.subn(r'__asm__ volatile\([^;]*\);', '(void)0;', irq)
        assert (reads, writes, assembly) == (1, 1, 5), "review IRQ host hardware seam"
        source = directory / "test.c"
        source.write_text(HARNESS.replace("@IRQ_IMPLEMENTATION@", irq).replace("@CASE_SOURCE@", str(CASE)))
        cls.binaries = []
        cls.compiler = shlex.split(os.environ.get("HOST_CC", "cc")) + [
            "-std=gnu11", "-O2", "-Wall", "-Wextra", "-Werror",
            "-I", str(directory), "-I", str(ROOT / "include"), str(source)]
        cls.directory = directory
        for level in (0, 1):
            binary = directory / f"psync-level{level}"
            subprocess.run(cls.compiler + [f"-DHPU_LOG_LEVEL={level}", "-o", str(binary)], check=True)
            cls.binaries.append(binary)

    def test_three_prefixes_two_rounds_each_share_one_cte_initialization(self):
        for binary in self.binaries:
            subprocess.run([str(binary), "0"], check=True, capture_output=True)

    def test_mmio_only_bad_or_duplicate_irq_and_clear_failure_cannot_pass(self):
        for binary in self.binaries:
            for scenario in (1, 4, 5, 6, 9):
                with self.subTest(level=binary.name, scenario=scenario):
                    subprocess.run([str(binary), str(scenario)], check=True, capture_output=True)

    def test_selected_unselected_guard_corruption_and_issue_failure_close_irq(self):
        for binary in self.binaries:
            for scenario in (2, 3, 7, 8):
                with self.subTest(level=binary.name, scenario=scenario):
                    subprocess.run([str(binary), str(scenario)], check=True, capture_output=True)

    def test_selected_equal_golden_must_still_be_canonical_but_unselected_poison_need_not(self):
        binary = self.directory / "psync-noncanonical-golden"
        subprocess.run(self.compiler + ["-DHPU_LOG_LEVEL=1", "-DHOST_FIRST_Q=3U", "-o", str(binary)], check=True)
        # idle两轮的0xffffffff毒值不受q约束；DMA首轮actual==golden==q仍必须失败。
        subprocess.run([str(binary), "10"], check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
