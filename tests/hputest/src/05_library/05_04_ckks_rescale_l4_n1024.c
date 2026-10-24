#include <workload.h>
#include <program.h>
#include <hpu/log.h>
#include <hpu/irq.h>

/*
 * 用例：05_04_ckks_rescale_l4_n1024
 * 目的：CKKS rescale库接口；N=1024，输入Q分量=4；独立SEAL参考
 * 参数：N=1024（多项式长度），输入level=4（Q基RNS分量数，不含P）。
 * 参考：固定版本inline-asm的SEAL下降程序及原始word golden，沿用导入校验。
 * 发令：具体HPU指令、对象和DMA参数见同目录05_04_ckks_rescale_l4_n1024.asm。
 * 顺序：准备数据 -> 提交窗口 -> PLIC武装 -> 发令（原程序末尾唯一PSYNC）-> ISR同步 -> 自检。
 * 此处不插入额外PSYNC，不改变上游算术、对象分配或DMA布局。
 */
int main(void) {
    _Static_assert(DEGREE == 1024U, "case degree differs from generated layout");
    _Static_assert(LEVEL == 4U, "case level differs from generated layout");

    LOG_EVENT("[HPU][START] %s N=%u level=%u inst=%u dma=%u lines=%u\n",
              CASE_ID, DEGREE, LEVEL, INSTRUCTION_COUNT, DMA_COUNT, WINDOW_LINES);
    LOG_DEBUG("[HPU][PURPOSE] %s\n", CASE_PURPOSE);

    /* 1. 准备本例输入、golden布局和guard，不计作HPU运算。 */
    phase_mark(PHASE_PREPARE);
    prepare_image();

    /* 2. 清旧故障/完成状态，配置并逐项读回DDR窗口。 */
    phase_mark(PHASE_CONFIGURE);
    csr_write(CSR_FAULT, FAULT_VALID);
    if (clear_completion() != 0)
        return case_fail_at(__FILE__, __LINE__);
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
    if (wait_window() != 0)
        return case_fail_at(__FILE__, __LINE__);

    /* 3. 准备完成后才首次进入CTE/武装source257；发令前必须没有旧ISR事件。 */
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

    /* 4. 只调用本例的具体程序；完整指令序列在同名.asm。 */
    phase_mark(PHASE_ISSUE);
    const int program_rc = hpu_run_seal_ckks_modswitch_l4_n1024();
    if (program_rc != 0) {
        irq_close();
        LOG_ERROR("[HPU][PROGRAM] %s rc=%d\n", CASE_ID, program_rc);
        return case_fail_at(__FILE__, __LINE__);
    }

    /* 5. 等source257的ISR清除/complete及HPU空闲；MMIO电平不能冒充ISR。 */
    phase_mark(PHASE_WAIT);
    const int wait_rc = wait_program();
    irq_close();
    if (wait_rc != 0) {
        irq_diagnose("program-wait", 0U);
        return case_fail_at(__FILE__, __LINE__);
    }
    if (irq_event_count() != 1U)
        return case_fail_at(__FILE__, __LINE__);
    if (irq_handler_count() != 1U)
        return case_fail_at(__FILE__, __LINE__);
    if ((csr_read(CSR_IRQ) & IRQ_LEVEL) != 0U)
        return case_fail_at(__FILE__, __LINE__);

    /* 6. 两项检查都执行，分别定位计算结果与只读区/guard破坏。 */
    phase_mark(PHASE_COMPARE);
    const int data_rc = check_results();
    const int memory_rc = check_memory();
    if (data_rc != 0)
        return case_fail_at(__FILE__, __LINE__);
    if (memory_rc != 0)
        return case_fail_at(__FILE__, __LINE__);
    return case_pass();
}
