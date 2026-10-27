#include <workload.h>
#include <performance.h>
#include <program.h>
#include <hpu/log.h>
#include <hpu/irq.h>

/*
 * 用例：07_23_ckks_rescale_l4_n8192。
 * 目的：测量CKKS Rescale的单一连续窗口cycle，并比较golden及内存guard。
 * 参数：多项式长度N=8192，输入Q基RNS分量数level=4；P基不计入level。
 * 完整HPU指令序列：本目录下07_23_ckks_rescale_l4_n8192.asm。
 * noopt构建的完整对照序列：本目录下07_23_ckks_rescale_l4_n8192.noopt.asm。
 * 本例只执行一次算子程序；沿用上游资源调度和NTT表，不串行重复轮次。
 * 计时口径execution_window_irq_v1：排除entry准备及原有尾IO；
 * 窗口包含全部算术、必要DMA和真实PLIC完成等待，不表示无DMA纯计算。
 * 不包含数据准备、窗口配置、首次IRQ武装、golden/guard比较和UART打印。
 */
int main(void) {
    performance_profile_state_t state;
    hpu_execution_profile_sample_t sample = {0};
    int rc;
    _Static_assert(DEGREE == 8192U, "wrong performance degree");
    _Static_assert(LEVEL == 4U, "wrong performance input level");
    _Static_assert(MEM_BASE == UINT64_C(0x90000000), "wrong performance DDR base");

    perf_cycle_enable();
    LOG_EVENT("[HPU][NEWAPI-PERF][START] case=%s variant=%s N=%u level=%u inst=%u dma=%u "
              "completion=plic_irq profile=continuous\n",
              CASE_ID, SCHEDULE_PROFILE, DEGREE, LEVEL, INSTRUCTION_COUNT, DMA_COUNT);
    phase_mark(PHASE_PREPARE);
    prepare_image();

    phase_mark(PHASE_CONFIGURE);
    csr_write(CSR_FAULT, FAULT_VALID);
    if (clear_completion() != 0) return case_fail_at(__FILE__, __LINE__);
    csr_write(CSR_BASE_LO, (uint32_t)MEM_BASE);
    csr_write(CSR_BASE_HI, (uint32_t)(MEM_BASE >> 32U));
    csr_write(CSR_SIZE_LO, WINDOW_LINES);
    csr_write(CSR_SIZE_HI, 0U);
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

    /* M态准备已经完成；首次IRQ武装在官方窗口之外，之后每次PSYNC只rearm。 */
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
    if (performance_profile_init(&state, PROFILE_SYNC_COUNT) != 0) {
        irq_close();
        return case_fail_at(__FILE__, __LINE__);
    }

    /* 官方入口执行entry准备/主体/原有尾IO；只由其两次clock hook设置一个连续计时窗口。 */
    phase_mark(PHASE_ISSUE);
    rc = hpu_run_frontend_ckks_modswitch_l4_n8192_profiled(&state.hooks, &sample);
    irq_close();
    workload_trace.cycle_start = sample.start_cycles;
    workload_trace.cycle_end = sample.end_cycles;
    /* sample直到尾部写回和最终PSYNC均成功才valid；无效运行不进入性能统计。 */
    if (performance_profile_finish(&state, &sample, rc) != 0) {
        irq_diagnose("execution-profile", 0U);
        LOG_ERROR("[HPU][NEWAPI-PERF][PROFILE-FAIL] run=%d error=%d sync=%lu clocks=%u valid=%d\n",
                  rc, state.error, (unsigned long)state.next_sync, state.read_count, sample.valid);
        return case_fail_at(__FILE__, __LINE__);
    }

    /* 主程序只读确认ISR已清电平，不补clear、不重置任何SRAM对象。 */
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

    /* 计时窗内允许必要DMA；不与旧端到端或纯计算口径混用。 */
    LOG_EVENT("[HPU][NEWAPI-PERF] case=%s variant=%s N=%u level=%u "
              "metric=execution_window_irq_v1 completion=plic_irq profile=continuous "
              "start=%lu end=%lu cycles=%lu verified=1 "
              "window_dload_count=%u window_dstore_count=%u prefix_dload_count=%u "
              "prefix_dstore_count=%u suffix_dload_count=%u suffix_dstore_count=%u sync_count=%u\n",
              CASE_ID, SCHEDULE_PROFILE, DEGREE, LEVEL,
              (unsigned long)sample.start_cycles, (unsigned long)sample.end_cycles,
              (unsigned long)(sample.end_cycles - sample.start_cycles),
              PROFILE_WINDOW_DLOAD_COUNT, PROFILE_WINDOW_DSTORE_COUNT, PROFILE_PREFIX_DLOAD_COUNT,
              PROFILE_PREFIX_DSTORE_COUNT, PROFILE_SUFFIX_DLOAD_COUNT, PROFILE_SUFFIX_DSTORE_COUNT, PROFILE_SYNC_COUNT);
    return case_pass();
}
