#include <hpu/perf.h>
#include <hpu/application_case.h>
#include <hpu/completion.h>
#include <hpu/log.h>
#include <hpu/progress.h>
#include <hpu/report.h>
#include <hpu/result.h>
#include <hpu/trace.h>
#include <auto_n65536_perf.h>

/*
 * 测试点：07_169_legacy_auto_l4_n65536，N=65536。
 * 目的：性能镜像，与04_18_legacy_auto_n65536使用同一份数据、参数、程序和golden。
 * 数据、模表、twiddle和可执行指令来自固定版本inline-asm；逐word检查golden及guard。
 * 一次ELF只执行一段程序；DSTORE之后只有一次末尾PSYNC。
 * DDR窗口为0x90000000，仿真RAM至少512MiB；普通/静默版检查相同。
 */
int main(void) {
    int rc;
    uint64_t cycle_start, cycle_end;
    perf_cycle_enable();
    case_start(__FILE__);
    (void)result_context(__FILE__, 0U);
    if (progress_begin(__FILE__, 1U) != 0) return case_fail(__FILE__, __LINE__);
    trace_phase(TRACE_PREPARE);
    phase_mark("prepare");
    /* 拷贝本用例的密文、密钥和模表；输出预置毒值，防止漏写误通过。 */
    if (application_prepare() != 0) return case_fail(__FILE__, __LINE__);

    /* 完整复用生产者参数检查；此阶段不发HPU指令，不计入性能cycle。 */
    phase_mark("validate-program");
    rc = hpu_validate_auto_n65536();
    if (rc != 0) {
        LOG_ERROR("[HPU][PERF][PREFLIGHT-FAIL] rc=%d\n", rc);
        return case_fail(__FILE__, __LINE__);
    }

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

    trace_phase(TRACE_ISSUE);
    phase_mark("issue");
    /* 发令沿用已校验的只读参数，不执行参数检查或逐DMA trace写入。 */
    /* 计时只覆盖发令、DMA、计算及等待完成；不含准备、预检查、UART、自检。 */
    cycle_start = perf_cycle_read();
    rc = hpu_run_auto_n65536();
    if (rc != 0) {
        LOG_ERROR("[HPU][SEAL][PROGRAM-FAIL] rc=%d instruction=%u dma=%u\n",
                  rc, application_trace.instruction, application_trace.dma);
        return case_fail(__FILE__, __LINE__);
    }
    /* MMIO等完成电平和空闲同时可见；不启用PLIC或计时器中断。 */
    rc = application_wait();
    cycle_end = perf_cycle_read();
    if (rc != 0 || completion_clear() != 0 || check_status() != 0)
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
    /* 两个端点及差值统一在自检之后输出；静默版仍读取cycle。 */
    LOG_EVENT("[HPU][PERF] case=07_169_legacy_auto_l4_n65536 N=65536 level=4 metric=issue_to_done_v2 "
              "start=%lu end=%lu cycles=%lu verified=1\n",
              (unsigned long)cycle_start, (unsigned long)cycle_end,
              (unsigned long)(cycle_end-cycle_start));
    return case_pass(__FILE__);
}
