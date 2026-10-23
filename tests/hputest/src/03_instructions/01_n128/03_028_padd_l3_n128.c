#include <workload.h>
#include <program.h>
#include <hpu/log.h>

/*
 * 用例：03_028_padd_l3_n128
 * 目的：模加、别名和依赖；N=128，实际处理3个不同模数分量
 * 参数：N=128（多项式长度），输入level=3（Q基RNS分量数，不含P）。
 * 参考：独立uint64模运算/C单stage参考；固定版本inline-asm编码与指令模型。
 * 发令：具体HPU指令、对象和DMA参数见同目录03_028_padd_l3_n128.asm。
 * 顺序：准备数据 -> 提交窗口 -> 发令（原程序末尾唯一PSYNC）-> 同步 -> 自检。
 * 此处不插入额外PSYNC，不改变上游算术、对象分配或DMA布局。
 */
int main(void) {
    _Static_assert(DEGREE == 128U, "case degree differs from generated layout");
    _Static_assert(LEVEL == 3U, "case level differs from generated layout");

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

    /* 3. 只调用本例的具体程序；完整指令序列在同名.asm。 */
    phase_mark(PHASE_ISSUE);
    const int program_rc = hpu_run_instruction_padd_l3_n128();
    if (program_rc != 0) {
        LOG_ERROR("[HPU][PROGRAM] %s rc=%d\n", CASE_ID, program_rc);
        return case_fail_at(__FILE__, __LINE__);
    }

    /* 4. 等待末尾PSYNC真正完成，再单独检查完成状态清除。 */
    phase_mark(PHASE_WAIT);
    if (wait_program() != 0)
        return case_fail_at(__FILE__, __LINE__);
    if (clear_completion() != 0)
        return case_fail_at(__FILE__, __LINE__);

    /* 5. 两项检查都执行，分别定位计算结果与只读区/guard破坏。 */
    phase_mark(PHASE_COMPARE);
    const int data_rc = check_results();
    const int memory_rc = check_memory();
    if (data_rc != 0)
        return case_fail_at(__FILE__, __LINE__);
    if (memory_rc != 0)
        return case_fail_at(__FILE__, __LINE__);
    return case_pass();
}
