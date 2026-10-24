#include <assert.h>
#include <stddef.h>
#include <workload.h>
#include <hpu/irq.h>

/* RV64调试工具既有trace布局不变；源码行号只能追加到末尾。 */
_Static_assert(offsetof(struct workload_progress, phase) == 0U, "phase ABI changed");
_Static_assert(offsetof(struct workload_progress, status) == 4U, "status ABI changed");
_Static_assert(offsetof(struct workload_progress, irq) == 8U, "irq ABI changed");
_Static_assert(offsetof(struct workload_progress, fault) == 12U, "fault ABI changed");
_Static_assert(offsetof(struct workload_progress, errors) == 16U, "errors ABI changed");
_Static_assert(offsetof(struct workload_progress, first_line) == 20U, "first_line ABI changed");
_Static_assert(offsetof(struct workload_progress, first_word) == 24U, "first_word ABI changed");
_Static_assert(offsetof(struct workload_progress, actual) == 28U, "actual ABI changed");
_Static_assert(offsetof(struct workload_progress, expected) == 32U, "expected ABI changed");
_Static_assert(offsetof(struct workload_progress, wait_cycles) == 40U, "wait_cycles ABI changed");
_Static_assert(offsetof(struct workload_progress, cycle_start) == 48U, "cycle_start ABI changed");
_Static_assert(offsetof(struct workload_progress, cycle_end) == 56U, "cycle_end ABI changed");
_Static_assert(offsetof(struct workload_progress, source_line) == 64U, "source_line must be appended");

/* 仅验证AM接收端的内存/同步逻辑，不在host上伪装执行HPU。 */
const uint32_t initial_image[IMAGE_LINES * LINE_WORDS] = {
    [0] = 0x12345678U, [64] = UINT32_MAX, [128] = 0xa5a55a5aU
};
const uint32_t golden_words[GOLDEN_WORDS] = { [0] = 5U, [1] = 10U };
const uint8_t writable_lines[IMAGE_LINES] = { 0, 1, 0 };
const struct output_span outputs[OUTPUT_COUNT] = { {1, 64, 0, 17, 0, 0, 0} };
static uint32_t ram[IMAGE_LINES * LINE_WORDS];
static unsigned mode, status_reads, write_count, irq_polls;
static uint64_t cycles;
static uint32_t irq_level;

volatile uint32_t *test_line(unsigned line) { return ram + line * LINE_WORDS; }
uint64_t test_cycle(void) { cycles += 256U; return cycles; }
int irq_poll(void) {
    ++irq_polls;
    if (mode == 9U) return -1;
    if (mode == 1U || mode == 8U) return 0;
    if (mode == 12U && irq_polls < 3U) return 0;
    return 1;
}
uint32_t test_csr_read(uintptr_t address) {
    if (address == CSR_IRQ) return irq_level;
    if (address == CSR_STATUS) {
        ++status_reads;
        if (mode == 2U) return STATUS_VALID | STATUS_FAULT;
        if (mode == 0U && status_reads < 3U) return STATUS_VALID | STATUS_BUSY;
        if (mode == 5U) return STATUS_VALID | STATUS_BUSY;
        if (mode == 10U) return 0U;
        if (mode == 11U)
            return STATUS_VALID | STATUS_BUSY | (status_reads >= 3U ? STATUS_FAULT : 0U);
        return STATUS_VALID;
    }
    if (address == CSR_FAULT) return mode == 2U || mode == 6U ? FAULT_VALID : 0U;
    return 0U;
}
void test_csr_write(uintptr_t address, uint32_t value) {
    assert(address == CSR_IRQ);
    ++write_count;
    if (mode != 4U && value == IRQ_LEVEL) irq_level = 0U;
}

static void begin_wait(unsigned next_mode, uint32_t level) {
    mode = next_mode;
    status_reads = write_count = irq_polls = 0U;
    cycles = 0U;
    irq_level = level;
    workload_trace.wait_cycles = 0U;
}

int main(void) {
    prepare_image();
    assert(ram[0] == initial_image[0] && ram[64] == UINT32_MAX && ram[128] == 0xa5a55a5aU);
    /* 未执行DSTORE时，毒化输出必须失败，不能把golden预填造成假PASS。 */
    assert(check_results() == 1);
    for (unsigned i = 0U; i < GOLDEN_WORDS; ++i) ram[64U + i] = golden_words[i];
    workload_trace.errors = 0U;
    assert(check_results() == 0 && check_memory() == 0);
    ram[65] = 18U;
    assert(check_results() == 1 && workload_trace.errors == 1U);
    assert(workload_trace.first_line == 1U && workload_trace.first_word == 1U);
    assert(workload_trace.actual == 18U && workload_trace.expected == 10U);
    ram[65] = golden_words[1];
    ram[0] ^= 1U;
    assert(check_memory() == 1); /* 输入/常量不允许被写。 */
    ram[0] = initial_image[0];
    ram[128] ^= 1U;
    assert(check_memory() == 1); /* 窗口末端guard也必须检查。 */
    ram[128] = initial_image[128];

    begin_wait(0U, 0U); /* 真实ISR已清IRQ，BUSY第三轮才清零，仍必须等到第三轮。 */
    assert(wait_program() == 0 && status_reads == 3U && irq_polls == 3U);
    assert(write_count == 0U && workload_trace.irq == 0U);
    irq_level = IRQ_LEVEL;
    assert(clear_completion() == 0 && irq_level == 0U && write_count == 2U);

    begin_wait(1U, IRQ_LEVEL);
    assert(wait_program() == 1 && irq_polls == 128U); /* MMIO完成电平不能代替真实ISR。 */
    assert(write_count == 0U && workload_trace.irq == IRQ_LEVEL && workload_trace.wait_cycles == 512U);
    begin_wait(8U, 0U);
    assert(wait_program() == 1 && irq_polls == 128U); /* idle且电平为0，也不能无事件通过。 */
    begin_wait(2U, 0U);
    assert(wait_program() == 1 && workload_trace.fault == FAULT_VALID);
    assert(irq_polls == 1U && write_count == 0U);
    begin_wait(6U, 0U);
    assert(wait_program() == 1 && workload_trace.fault == FAULT_VALID); /* 独立FAULT亦失败。 */
    begin_wait(5U, 0U);
    assert(wait_program() == 1 && irq_polls == 128U); /* ISR已到但BUSY不清不能成功。 */
    begin_wait(7U, IRQ_LEVEL);
    assert(wait_program() == 1 && irq_polls == 1U && write_count == 0U); /* main不得补清ISR遗漏。 */
    begin_wait(9U, 0U);
    assert(wait_program() == 1 && irq_polls == 1U); /* ISR错误不能被idle掩盖。 */
    begin_wait(10U, 0U);
    assert(wait_program() == 1 && irq_polls == 128U); /* 无有效窗口仍超时。 */
    begin_wait(11U, 0U);
    assert(wait_program() == 1 && irq_polls == 3U); /* 等BUSY时出现fault要立即失败。 */
    begin_wait(12U, 0U);
    assert(wait_program() == 0 && irq_polls == 3U); /* 空闲不能绕过第三轮才到的ISR。 */

    begin_wait(3U, 0U);
    assert(wait_window() == 0); /* COMMIT就绪不需要PSYNC事件。 */
    assert(irq_polls == 0U);
    begin_wait(4U, IRQ_LEVEL);
    assert(clear_completion() == 1); /* 清电平也必须有cycle超时。 */
    mode = 2U;
    workload_trace.phase = PHASE_COMPARE;
    workload_trace.first_line = 7U;
    workload_trace.first_word = 9U;
    workload_trace.actual = 13U;
    workload_trace.expected = 17U;
    workload_trace.cycle_start = 101U;
    workload_trace.cycle_end = 202U;
    assert(case_fail_at("src/host-case.c", 321U) == 1);
    assert(workload_trace.phase == PHASE_FAIL && workload_trace.source_line == 321U);
    assert(workload_trace.status == (STATUS_VALID | STATUS_FAULT));
    assert(workload_trace.irq == IRQ_LEVEL && workload_trace.fault == FAULT_VALID);
    assert(workload_trace.first_line == 7U && workload_trace.first_word == 9U);
    assert(workload_trace.actual == 13U && workload_trace.expected == 17U);
    assert(workload_trace.cycle_start == 101U && workload_trace.cycle_end == 202U);
    return 0;
}
