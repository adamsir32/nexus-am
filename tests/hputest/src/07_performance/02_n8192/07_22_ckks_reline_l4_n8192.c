#include <workload.h>
#include <performance.h>
#include <program.h>
#include <hpu/log.h>
#include <hpu/irq.h>

/*
 * 用例：07_22_ckks_reline_l4_n8192。
 * 目的：测量CKKS 重线性化Reline的端到端cycle，并比较golden及内存guard。
 * 参数：多项式长度N=8192，输入Q基RNS分量数level=4；P基不计入level。
 * 完整HPU指令序列：本目录下07_22_ckks_reline_l4_n8192.asm。
 * noopt构建的完整对照序列：本目录下07_22_ckks_reline_l4_n8192.noopt.asm。
 * 本例只执行一次算子程序；沿用上游资源调度和NTT表，不串行重复轮次。
 * 计时口径issue_to_irq_done_v1：包含CPU发令、DMA、HPU计算和PLIC中断处理/完成观察；
 * 不包含数据准备、参数检查、窗口配置、IRQ武装、golden/guard比较和UART打印。
 */
int main(void) {
    int rc;
    int wait_rc = 1;
    uint64_t cycle_start, cycle_end;
    _Static_assert(DEGREE == 8192U, "wrong performance degree");
    _Static_assert(LEVEL == 4U, "wrong performance input level");
    _Static_assert(MEM_BASE == UINT64_C(0x90000000), "wrong performance DDR base");

    perf_cycle_enable();
    LOG_EVENT("[HPU][NEWAPI-PERF][START] case=%s variant=%s N=%u level=%u inst=%u dma=%u completion=plic_irq\n",
              CASE_ID, SCHEDULE_PROFILE, DEGREE, LEVEL, INSTRUCTION_COUNT, DMA_COUNT);
    phase_mark(PHASE_PREPARE);
    prepare_image();
    /* 只做参数检查，不发HPU指令；必须在起始cycle之前完成。 */
    rc = hpu_validate_frontend_ckks_reline_l4_n8192();
    if (rc != 0) {
        LOG_ERROR("[HPU][NEWAPI-PERF][PREFLIGHT-FAIL] rc=%d\n", rc);
        return case_fail_at(__FILE__, __LINE__);
    }

    phase_mark(PHASE_CONFIGURE);
    csr_write(CSR_FAULT, FAULT_VALID);
    if (clear_completion() != 0) return case_fail_at(__FILE__, __LINE__);
    csr_write(CSR_BASE_LO, (uint32_t)MEM_BASE);
    csr_write(CSR_BASE_HI, (uint32_t)(MEM_BASE >> 32U));
    csr_write(CSR_SIZE_LO, WINDOW_LINES);
    csr_write(CSR_SIZE_HI, 0U);
    /* 分开检查，失败时可由源码文件和行号定位具体寄存器。 */
    if (expect_csr(CSR_BASE_LO, (uint32_t)MEM_BASE) != 0)
        return case_fail_at(__FILE__, __LINE__);
    if (expect_csr(CSR_BASE_HI, (uint32_t)(MEM_BASE >> 32U)) != 0)
        return case_fail_at(__FILE__, __LINE__);
    if (expect_csr(CSR_SIZE_LO, WINDOW_LINES) != 0)
        return case_fail_at(__FILE__, __LINE__);
    if (expect_csr(CSR_SIZE_HI, 0U) != 0)
        return case_fail_at(__FILE__, __LINE__);
    csr_write(CSR_COMMIT, COMMIT);
    if (wait_window() != 0) return case_fail_at(__FILE__, __LINE__);

    /* M态准备/预检查已完成；PLIC武装不计入cycle，旧事件不能冒充本轮完成。 */
    if (irq_reset_events() != 0)
        return case_fail_at(__FILE__, __LINE__);
    if (irq_open() != 0) {
        irq_close();
        return case_fail_at(__FILE__, __LINE__);
    }
    if (irq_event_count() != 0U) {
        irq_close();
        return case_fail_at(__FILE__, __LINE__);
    }
    if (irq_handler_count() != 0U) {
        irq_close();
        return case_fail_at(__FILE__, __LINE__);
    }

    /* 此窗口内不打印、不准备数据、不重复参数检查；指令含最终PSYNC。 */
    phase_mark(PHASE_ISSUE);
    cycle_start = perf_cycle_read();
    rc = hpu_run_frontend_ckks_reline_l4_n8192();
    if (rc == 0) wait_rc = performance_wait();
    cycle_end = perf_cycle_read();
    irq_close();
    /* 停表后才保存端点，静默版也能从workload_trace读取。 */
    workload_trace.cycle_start = cycle_start;
    workload_trace.cycle_end = cycle_end;
    if (rc != 0) {
        LOG_ERROR("[HPU][NEWAPI-PERF][EXECUTION-FAIL] run=%d cycles=%lu\n",
                  rc, (unsigned long)(cycle_end - cycle_start));
        return case_fail_at(__FILE__, __LINE__);
    }
    if (wait_rc != 0) {
        irq_diagnose("performance-wait", 0U);
        LOG_ERROR("[HPU][NEWAPI-PERF][WAIT-FAIL] wait=%d cycles=%lu\n",
                  wait_rc, (unsigned long)(cycle_end - cycle_start));
        return case_fail_at(__FILE__, __LINE__);
    }

    /* 完成必须来自一次真实ISR；main只读确认电平，不能代替ISR清除。 */
    if (irq_event_count() != 1U) return case_fail_at(__FILE__, __LINE__);
    if (irq_handler_count() != 1U) return case_fail_at(__FILE__, __LINE__);
    if ((csr_read(CSR_IRQ) & IRQ_LEVEL) != 0U)
        return case_fail_at(__FILE__, __LINE__);
    const uint32_t status = csr_read(CSR_STATUS);
    if ((status & STATUS_VALID) == 0U) return case_fail_at(__FILE__, __LINE__);
    if ((status & STATUS_BUSY) != 0U) return case_fail_at(__FILE__, __LINE__);
    if ((status & STATUS_FAULT) != 0U) return case_fail_at(__FILE__, __LINE__);
    if ((csr_read(CSR_FAULT) & FAULT_VALID) != 0U)
        return case_fail_at(__FILE__, __LINE__);
    phase_mark(PHASE_COMPARE);
    const int data_rc = check_results();
    const int memory_rc = check_memory();
    if (data_rc != 0) return case_fail_at(__FILE__, __LINE__);
    if (memory_rc != 0) return case_fail_at(__FILE__, __LINE__);

    /* golden和guard全部通过后统一输出；静默版保留端点但不输出UART。 */
    LOG_EVENT("[HPU][NEWAPI-PERF] case=%s variant=%s N=%u level=%u "
              "metric=issue_to_irq_done_v1 completion=plic_irq start=%lu end=%lu cycles=%lu verified=1\n",
              CASE_ID, SCHEDULE_PROFILE, DEGREE, LEVEL,
              (unsigned long)cycle_start, (unsigned long)cycle_end,
              (unsigned long)(cycle_end - cycle_start));
    return case_pass();
}
