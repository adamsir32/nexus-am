#include <hpu/irq.h>
#include <hpu/application_case.h>
#include <hpu/completion.h>
#include <hpu/log.h>
#include <hpu/progress.h>
#include <hpu/report.h>
#include <hpu/result.h>
#include <hpu/trace.h>
#include <psync_n65536.h>

/*
 * 测试点：03_17_psync_n65536，N=65536。
 * 目的：65536系数DMA回环后，确认PSYNC完成中断及数据结果。
 * 数据、模表、twiddle和可执行指令来自固定版本inline-asm；逐word检查golden及guard。
 * 一次ELF只执行一段程序；DSTORE之后只有一次末尾PSYNC。
 * 大数据窗口为0x90000000，仿真RAM至少512MiB；正常/静默版检查完全相同。
 */
int main(void) {
    int rc;
    case_start(__FILE__);
    (void)result_context(__FILE__, 0U);
    if (progress_begin(__FILE__, 1U) != 0) return case_fail(__FILE__, __LINE__);
    trace_phase(TRACE_PREPARE);
    phase_mark("prepare");
    /* 拷贝本用例的密文、密钥和模表；输出预置毒值，防止漏写误通过。 */
    if (application_prepare() != 0) return case_fail(__FILE__, __LINE__);

    trace_phase(TRACE_CONFIGURE);
    phase_mark("configure");
    /* 写shadow配置并回读，再COMMIT；寄存器级步骤保留在用例中。 */
    csr_write(CSR_FAULT, FAULT_VALID);
    csr_write(CSR_IRQ, IRQ_LEVEL);
    csr_write(CSR_IRQ, 0U);
    csr_write(CSR_BASE_LO, (uint32_t)MEM_BASE);
    csr_write(CSR_BASE_HI, (uint32_t)(MEM_BASE >> 32U));
    csr_write(CSR_SIZE_LO, HPU_APPLICATION_CAPACITY_LINES);
    csr_write(CSR_SIZE_HI, 0U);
    if (expect_csr(CSR_BASE_LO, (uint32_t)MEM_BASE, UINT32_MAX) != 0 ||
        expect_csr(CSR_BASE_HI, (uint32_t)(MEM_BASE >> 32U), UINT32_MAX) != 0 ||
        expect_csr(CSR_SIZE_LO, HPU_APPLICATION_CAPACITY_LINES, UINT32_MAX) != 0 ||
        expect_csr(CSR_SIZE_HI, 0U, UINT32_MAX) != 0)
        return case_fail(__FILE__, __LINE__);
    csr_write(CSR_COMMIT, COMMIT);
    if (wait_window(1) != 0 || check_status() != 0) return case_fail(__FILE__, __LINE__);

    /* 只开启HPU外部中断，不启用计时器。 */
    if (irq_open() != 0) return case_fail(__FILE__, __LINE__);
    trace_phase(TRACE_ISSUE);
    phase_mark("issue");
    /* 指令发射及DMA位置可从application_trace定位，不逐系数打印。 */
    rc = hpu_run_psync_n65536();
    if (rc != 0) {
        LOG_ERROR("[HPU][SEAL][PROGRAM-FAIL] rc=%d instruction=%u dma=%u\n",
                  rc, application_trace.instruction, application_trace.dma);
        return case_fail(__FILE__, __LINE__);
    }
    trace_phase(TRACE_WAIT);
    phase_mark("wait-completion");
    /* ISR完成claim/清电平/complete后，再确认HPU已经空闲。 */
    rc = irq_wait();
    irq_close();
    if (rc != 0) return case_fail(__FILE__, __LINE__);
    /* IRQ和BUSY独立同步；ISR已清IRQ，不能再等IRQ电平，也不能把一次BUSY=1判失败。 */
    unsigned timeout;
    for (timeout = 0U; timeout < TIMEOUT; ++timeout) {
        const uint32_t status = csr_read(CSR_STATUS);
        const uint32_t fault = csr_read(CSR_FAULT);
        if ((status & STATUS_FAULT) != 0U || (fault & FAULT_VALID) != 0U ||
            (status & STATUS_VALID) == 0U)
            return case_fail(__FILE__, __LINE__);
        if ((status & STATUS_BUSY) == 0U) break;
    }
    if (timeout == TIMEOUT || (csr_read(CSR_IRQ) & IRQ_LEVEL) != 0U || check_status() != 0)
        return case_fail(__FILE__, __LINE__);

    trace_phase(TRACE_COMPARE);
    phase_mark("compare-results");
    const int data_rc = application_check_results();
    trace_phase(TRACE_GUARD);
    phase_mark("check-guard");
    const int guard_rc = application_check_memory();
    if (data_rc != 0 || guard_rc != 0) return case_fail(__FILE__, __LINE__);
    trace_phase(TRACE_DONE);
    phase_mark("case-done");
    return case_pass(__FILE__);
}
