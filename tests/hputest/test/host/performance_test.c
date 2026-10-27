#include <assert.h>
#include <performance.h>
#include <workload.h>
#include <hpu/irq.h>

/* 仅模拟CSR采样次序和等待开销，不在host上执行HPU指令。 */
volatile struct workload_progress workload_trace;
static unsigned mode, polls, read_slot, cycle_reads, irq_reads;
static uint64_t cycles;
enum { TRACE_MARKER = 0xdead0000U };

uint64_t test_cycle(void) {
    ++cycle_reads;
    cycles += 256U;
    return cycles;
}

/* 本fixture只覆盖通用wait_program；profile hooks由独立host状态机覆盖。 */
uint64_t perf_cycle_read(void) { return test_cycle(); }
uint32_t irq_event_count(void) { return 0U; }
uint32_t irq_handler_count(void) { return 0U; }
int irq_rearm(void) { assert(!"plain wait must not rearm IRQ"); return 1; }

int irq_poll(void) {
    assert(read_slot == 0U || read_slot == 2U);
    assert(irq_reads == 0U); /* 未到出口前，不准逐轮读取MMIO IRQ作为完成事件。 */
    read_slot = 0U;
    ++polls;
    if (mode == 0U) {
        /* 普通轮询不写trace；64/128轮只采样STATUS/FAULT，不额外读IRQ。 */
        if (polls > 1U) {
            const unsigned previous = polls - 1U;
            assert(workload_trace.status == ((previous & 63U) == 0U
                ? STATUS_VALID | STATUS_BUSY : TRACE_MARKER + previous));
            assert(workload_trace.irq == TRACE_MARKER + previous);
            assert(workload_trace.fault == ((previous & 63U) == 0U
                ? 0U : TRACE_MARKER + previous));
        }
        workload_trace.status = TRACE_MARKER + polls;
        workload_trace.irq = TRACE_MARKER + polls;
        workload_trace.fault = TRACE_MARKER + polls;
    }
    if (mode == 6U) return -1;
    if (mode == 2U || mode == 10U) return 0;
    if (mode == 9U && polls < 3U) return 0;
    return 1;
}

uint32_t test_csr_read(uintptr_t address) {
    if (address == CSR_STATUS) {
        assert(read_slot == 0U);
        read_slot = 1U;
        if (mode == 0U && polls < 130U) return STATUS_VALID | STATUS_BUSY;
        if (mode == 1U && polls < 3U) return STATUS_VALID | STATUS_BUSY;
        if (mode == 8U) return STATUS_VALID | STATUS_BUSY;
        if (mode == 11U)
            return STATUS_VALID | STATUS_BUSY | (polls >= 3U ? STATUS_FAULT : 0U);
        if (mode == 12U) return STATUS_VALID | STATUS_BUSY;
        if (mode == 13U && polls < 256U) return STATUS_VALID | STATUS_BUSY;
        if (mode == 3U) return STATUS_VALID | STATUS_FAULT;
        if (mode == 5U) return 0U;
        return STATUS_VALID;
    }
    if (address == CSR_FAULT) {
        assert(read_slot == 1U);
        read_slot = 2U;
        return mode == 4U || (mode == 12U && polls >= 3U) ? FAULT_VALID : 0U;
    }
    assert(address == CSR_IRQ && read_slot == 2U);
    read_slot = 3U;
    ++irq_reads;
    return mode == 2U || mode == 7U ? IRQ_LEVEL : 0U;
}

void test_csr_write(uintptr_t address, uint32_t value) {
    (void)address;
    (void)value;
    assert(!"performance_wait must not clear IRQ or write configuration");
}

volatile uint32_t *test_line(unsigned line) {
    (void)line;
    return 0;
}

static void begin(unsigned next_mode) {
    mode = next_mode;
    polls = read_slot = cycle_reads = irq_reads = 0U;
    cycles = 0U;
    workload_trace = (struct workload_progress){0};
    workload_trace.cycle_start = 42U;
    workload_trace.cycle_end = 43U;
}

int main(void) {
    begin(0U);
    assert(performance_wait() == 0);
    assert(polls == 130U && cycle_reads == 4U); /* 起点、64/128轮、成功出口。 */
    assert(workload_trace.wait_cycles == 768U);
    assert(workload_trace.status == STATUS_VALID && workload_trace.irq == 0U && irq_reads == 1U);
    assert(workload_trace.cycle_start == 42U && workload_trace.cycle_end == 43U);

    begin(1U);
    assert(performance_wait() == 0 && polls == 3U && irq_reads == 1U); /* ISR先到，仍要等BUSY清零。 */
    begin(2U);
    assert(performance_wait() == 1 && polls == 256U); /* MMIO IRQ=1但无ISR仍不能成功。 */
    assert(workload_trace.wait_cycles == 1024U && cycle_reads == 5U && irq_reads == 1U);
    begin(3U);
    assert(performance_wait() == 1 && polls == 1U);
    assert((workload_trace.status & STATUS_FAULT) != 0U);
    begin(4U);
    assert(performance_wait() == 1 && polls == 1U && workload_trace.fault == FAULT_VALID);
    begin(5U);
    assert(performance_wait() == 1 && polls == 256U); /* 配置失效时ISR不能代表成功。 */
    begin(6U);
    assert(performance_wait() == 1 && polls == 1U && irq_reads == 1U); /* ISR错误立即失败。 */
    begin(7U);
    assert(performance_wait() == 1 && polls == 1U && workload_trace.irq == IRQ_LEVEL); /* 不补清ISR遗漏。 */
    begin(8U);
    assert(performance_wait() == 1 && polls == 256U); /* ISR已到，但BUSY永远不清。 */
    begin(9U);
    assert(performance_wait() == 0 && polls == 3U && irq_reads == 1U); /* ISR第三轮才到。 */
    begin(10U);
    assert(performance_wait() == 1 && polls == 256U && workload_trace.irq == 0U); /* idle/IRQ=0仍需事件。 */
    begin(11U);
    assert(performance_wait() == 1 && polls == 3U && (workload_trace.status & STATUS_FAULT));
    begin(12U);
    assert(performance_wait() == 1 && polls == 3U && workload_trace.fault == FAULT_VALID);
    begin(13U);
    assert(performance_wait() == 0 && polls == 256U); /* 最后一轮BUSY清零仍在合法预算内。 */
    assert(workload_trace.wait_cycles == 1024U && cycle_reads == 5U && irq_reads == 1U);
    return 0;
}
