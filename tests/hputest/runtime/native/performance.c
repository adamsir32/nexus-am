#include <performance.h>
#include <workload.h>

#ifndef WAIT_CYCLES
#define WAIT_CYCLES UINT64_C(25000000)
#endif

int performance_wait(void) {
    const uint64_t start = cycle_now();
    unsigned polls = 0U;
    for (;;) {
        /* IRQ与STATUS独立跨域：先读完成电平，再读较新的忙状态。 */
        const uint32_t irq = csr_read(CSR_IRQ);
        const uint32_t status = csr_read(CSR_STATUS);
        const uint32_t fault = csr_read(CSR_FAULT);
        if ((fault & FAULT_VALID) != 0U || (status & STATUS_FAULT) != 0U) {
            workload_trace.irq = irq;
            workload_trace.status = status;
            workload_trace.fault = fault;
            workload_trace.wait_cycles = cycle_now() - start;
            return 1;
        }
        if ((irq & IRQ_LEVEL) != 0U &&
            (status & (STATUS_VALID | STATUS_BUSY)) == STATUS_VALID) {
            workload_trace.irq = irq;
            workload_trace.status = status;
            workload_trace.fault = fault;
            workload_trace.wait_cycles = cycle_now() - start;
            return 0;
        }
        /* 对齐主线07等待开销：每64轮才采样cycle和写诊断，不逐轮存储。 */
        if ((++polls & 63U) == 0U) {
            const uint64_t elapsed = cycle_now() - start;
            workload_trace.irq = irq;
            workload_trace.status = status;
            workload_trace.fault = fault;
            workload_trace.wait_cycles = elapsed;
            if (elapsed >= WAIT_CYCLES) return 1;
        }
    }
}
