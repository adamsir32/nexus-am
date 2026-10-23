#include <workload.h>
#include <program.h>
#include <hpu/log.h>

/*
 * 03～06共用的目标端闭环；运算和内存布局由固定版本inline-asm生成。
 * 每例只执行本清单指定的程序，不把多个独立测试串成一轮。
 * 末尾唯一PSYNC通过MMIO同步；结果、只读区域和guard全部自检。
 */
int native_case_run(void) {
    _Static_assert(DEGREE <= 8192U, "unsupported delivery degree");
    LOG_EVENT("[HPU][START] %s N=%u level=%u inst=%u dma=%u lines=%u\n",
              CASE_ID, DEGREE, LEVEL, INSTRUCTION_COUNT, DMA_COUNT, WINDOW_LINES);
    LOG_DEBUG("[HPU][PURPOSE] %s\n", CASE_PURPOSE);
    phase_mark(PHASE_PREPARE);
    prepare_image();
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

    phase_mark(PHASE_ISSUE);
    const int rc = WORKLOAD_RUN();
    if (rc != 0) {
        LOG_ERROR("[HPU][PROGRAM] %s rc=%d\n", CASE_ID, rc);
        return case_fail(__LINE__);
    }
    phase_mark(PHASE_WAIT);
    if (wait_program() != 0 || clear_completion() != 0)
        return case_fail(__LINE__);
    phase_mark(PHASE_COMPARE);
    const int data_rc = check_results();
    const int memory_rc = check_memory();
    if (data_rc != 0 || memory_rc != 0) return case_fail(__LINE__);
    return case_pass();
}
