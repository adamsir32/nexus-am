#include <assert.h>
#include <performance.h>
#include <workload.h>

/* 仅模拟CSR采样次序和等待开销，不在host上执行HPU指令。 */
volatile struct workload_progress workload_trace;
static unsigned mode, polls, read_slot, cycle_reads;
static uint64_t cycles;
enum { TRACE_MARKER = 0xdead0000U };

uint64_t test_cycle(void) {
    ++cycle_reads;
    cycles += 256U;
    return cycles;
}

uint32_t test_csr_read(uintptr_t address) {
    const uintptr_t expected[] = {CSR_IRQ, CSR_STATUS, CSR_FAULT};
    assert(address == expected[read_slot]);
    read_slot = (read_slot + 1U) % 3U;
    if (address == CSR_IRQ) {
        ++polls;
        if (mode == 0U) {
            /* 普通轮询不能写trace：上一轮非64的倍数时应保留探针值。 */
            if (polls > 1U) {
                const unsigned previous = polls - 1U;
                assert(workload_trace.status == ((previous & 63U) == 0U
                    ? STATUS_VALID | STATUS_BUSY : TRACE_MARKER + previous));
                assert(workload_trace.irq == ((previous & 63U) == 0U
                    ? IRQ_LEVEL : TRACE_MARKER + previous));
                assert(workload_trace.fault == ((previous & 63U) == 0U
                    ? 0U : TRACE_MARKER + previous));
            }
            workload_trace.status = TRACE_MARKER + polls;
            workload_trace.irq = TRACE_MARKER + polls;
            workload_trace.fault = TRACE_MARKER + polls;
        }
        return mode == 2U ? 0U : IRQ_LEVEL;
    }
    if (address == CSR_STATUS) {
        if (mode == 0U && polls < 130U) return STATUS_VALID | STATUS_BUSY;
        if (mode == 1U && polls < 3U) return STATUS_VALID | STATUS_BUSY;
        if (mode == 3U) return STATUS_VALID | STATUS_FAULT;
        if (mode == 5U) return 0U;
        return STATUS_VALID;
    }
    return mode == 4U ? FAULT_VALID : 0U;
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
    polls = read_slot = cycle_reads = 0U;
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
    assert(workload_trace.status == STATUS_VALID && workload_trace.irq == IRQ_LEVEL);
    assert(workload_trace.cycle_start == 42U && workload_trace.cycle_end == 43U);

    begin(1U);
    assert(performance_wait() == 0 && polls == 3U); /* IRQ先到，仍要等BUSY清零。 */
    begin(2U);
    assert(performance_wait() == 1 && polls == 256U); /* idle但无IRQ不能成功。 */
    assert(workload_trace.wait_cycles == 1024U);
    begin(3U);
    assert(performance_wait() == 1 && polls == 1U);
    assert((workload_trace.status & STATUS_FAULT) != 0U);
    begin(4U);
    assert(performance_wait() == 1 && polls == 1U && workload_trace.fault == FAULT_VALID);
    begin(5U);
    assert(performance_wait() == 1 && polls == 256U); /* 配置失效时IRQ不能代表成功。 */
    return 0;
}
