#include <workload.h>
#include <performance.h>
#include <frontend_bgv_rotate_l3_n4096_perf.h>
#include <hpu/log.h>

/* 历史编号留档；默认构建仅使用performance-cases.tsv中的新编号。
 * 07_18_bgv_rotate_l3_n4096：BGV，N=4096，输入level=3（不含特殊P）。
 * 目的：按原07的N/4步长验证密文旋转；只执行1个旋转节点。
 * 对照原用例07_22_bgv_rotate_l3_n4096，复用相同Fixture参数、输入和golden。
 * optimized/noopt由本次layout指定；每个ELF只运行一个算子程序，不串行重复轮次。
 * 资源调度及NTT表沿用实验分支；host验证与真实HPU执行结果分别记录。
 */
int main(void) {
    int rc;
    int wait_rc = 1;
    uint64_t cycle_start, cycle_end;
    _Static_assert(DEGREE == 4096U, "wrong performance degree");
    _Static_assert(LEVEL == 3U, "wrong performance input level");
    _Static_assert(MEM_BASE == UINT64_C(0x90000000), "wrong performance DDR base");

    perf_cycle_enable();
    LOG_EVENT("[HPU][NEWAPI-PERF][START] case=%s variant=%s N=%u level=%u inst=%u dma=%u\n",
              CASE_ID, SCHEDULE_PROFILE, DEGREE, LEVEL, INSTRUCTION_COUNT, DMA_COUNT);
    phase_mark(PHASE_PREPARE);
    prepare_image();
    /* 参数检查只在计时前执行，不发HPU指令。 */
    rc = hpu_validate_frontend_bgv_rotate_l3_n4096();
    if (rc != 0) {
        LOG_ERROR("[HPU][NEWAPI-PERF][PREFLIGHT-FAIL] rc=%d\n", rc);
        return case_fail(__LINE__);
    }

    phase_mark(PHASE_CONFIGURE);
    csr_write(CSR_FAULT, FAULT_VALID);
    if (clear_completion() != 0) return case_fail(__LINE__);
    csr_write(CSR_BASE_LO, (uint32_t)MEM_BASE);
    csr_write(CSR_BASE_HI, (uint32_t)(MEM_BASE >> 32U));
    csr_write(CSR_SIZE_LO, WINDOW_LINES);
    csr_write(CSR_SIZE_HI, 0U);
    if (expect_csr(CSR_BASE_LO, (uint32_t)MEM_BASE) != 0 ||
        expect_csr(CSR_BASE_HI, (uint32_t)(MEM_BASE >> 32U)) != 0 ||
        expect_csr(CSR_SIZE_LO, WINDOW_LINES) != 0 ||
        expect_csr(CSR_SIZE_HI, 0U) != 0)
        return case_fail(__LINE__);
    csr_write(CSR_COMMIT, COMMIT);
    if (wait_window() != 0) return case_fail(__LINE__);

    /* 只计CPU发令、DMA、HPU计算及完成轮询；此区间不打印或重复参数检查。 */
    phase_mark(PHASE_ISSUE);
    cycle_start = perf_cycle_read();
    rc = hpu_run_frontend_bgv_rotate_l3_n4096();
    if (rc == 0) wait_rc = performance_wait();
    cycle_end = perf_cycle_read();
    /* 停表后才保存端点，静默版也能从workload_trace读取。 */
    workload_trace.cycle_start = cycle_start;
    workload_trace.cycle_end = cycle_end;
    if (rc != 0 || wait_rc != 0) {
        LOG_ERROR("[HPU][NEWAPI-PERF][EXECUTION-FAIL] run=%d wait=%d cycles=%lu\n",
                  rc, wait_rc, (unsigned long)(cycle_end - cycle_start));
        return case_fail(__LINE__);
    }

    if (clear_completion() != 0) return case_fail(__LINE__);
    const uint32_t status = csr_read(CSR_STATUS);
    if ((status & (STATUS_VALID | STATUS_BUSY | STATUS_FAULT)) != STATUS_VALID ||
        (csr_read(CSR_FAULT) & FAULT_VALID) != 0U)
        return case_fail(__LINE__);
    phase_mark(PHASE_COMPARE);
    const int data_rc = check_results();
    const int memory_rc = check_memory();
    if (data_rc != 0 || memory_rc != 0) return case_fail(__LINE__);

    /* 全部golden和guard通过后统一输出；静默版保留端点但不输出UART。 */
    LOG_EVENT("[HPU][NEWAPI-PERF] case=%s variant=%s N=%u level=%u "
              "metric=issue_to_done_v2 start=%lu end=%lu cycles=%lu verified=1\n",
              CASE_ID, SCHEDULE_PROFILE, DEGREE, LEVEL,
              (unsigned long)cycle_start, (unsigned long)cycle_end,
              (unsigned long)(cycle_end - cycle_start));
    return case_pass();
}
