#include <workload.h>
#include <program.h>
#include <instruction_psync_l4_n1024_idle.h>
#include <instruction_psync_l4_n1024_dma.h>
#include <instruction_psync_l4_n1024_compute.h>
#include <hpu/log.h>
#include <hpu/irq.h>

/*
 * 用例：03_08_psync_l4_n1024
 * 目的：末尾PSYNC完成与数据闭环；N=1024，实际处理4个不同模数分量
 * 参数：N=1024（多项式长度），输入level=4（Q基RNS分量数，不含P）。
 * 参考：独立uint64模乘golden和官方assembler/instruction model；不手写指令字。
 * 原始共享布局/结果来源：03_08_psync_l4_n1024.asm。
 * 三个真实前序程序：同目录03_08_psync_l4_n1024.{idle,dma,compute}.asm。
 * idle只含PSYNC；DMA对4个RNS分量回环；compute对4个RNS分量执行PMUL。
 * 各程序末尾恰有一个PSYNC，执行两轮；每scenario open/close，第二轮rearm。
 * CPU发PSYNC时前序命令是否仍忙由真实IT波形判断，不由软件或host桩宣称。
 */

static int check_scenario_outputs(int component) {
    unsigned selected = 0U;
    /* 选择性检查不能调用全输出check_results；先失效一次，check_memory复用此结果。 */
    invalidate_lines(IMAGE_LINES);
    for (unsigned index = 0U; index < OUTPUT_COUNT; ++index) {
        const struct output_span *out = &outputs[index];
        const int written = component >= 0 && out->component == (unsigned)component;
        volatile const uint32_t *actual = line_ptr(out->line);
        if (written) ++selected;
        for (unsigned word = 0U; word < out->words; ++word) {
            const uint32_t expected = written ? golden_words[out->golden_word + word]
                : initial_image[out->line * LINE_WORDS + word];
            const uint32_t value = actual[word];
            if (value == expected && (!written || value < out->modulus)) continue;
            if (workload_trace.errors == 0U) {
                workload_trace.first_line = out->line + word / LINE_WORDS;
                workload_trace.first_word = word % LINE_WORDS;
                workload_trace.actual = value;
                workload_trace.expected = expected;
            }
            ++workload_trace.errors;
            LOG_ERROR("[HPU][PSYNC][DATA] component=%d output-component=%u mod=%u word=%u "
                      "actual=0x%x expected=0x%x selected=%u\n",
                      component, out->component, out->modulus_id, word, value, expected, written);
            return 1;
        }
    }
    return selected != (component < 0 ? 0U : LEVEL);
}

int main(void) {
    _Static_assert(DEGREE == 1024U, "case degree differs from generated layout");
    _Static_assert(LEVEL == 4U, "case level differs from generated layout");
    LOG_EVENT("[HPU][START] %s N=%u level=%u completion=plic_irq scenarios=3 rounds=2\n",
              CASE_ID, DEGREE, LEVEL);

    /* 只清一次累计事件；后续close/open及rearm都必须保留CTE/事件计数。 */
    if (irq_reset_events() != 0)
        return case_fail_at(__FILE__, __LINE__);
    for (unsigned scenario = 0U; scenario < 3U; ++scenario) {
        for (unsigned round = 0U; round < 2U; ++round) {
            const unsigned before = scenario * 2U + round;
            int program_rc;
            int arm_rc;

            /* 1. 每轮恢复同一原生image、golden和guard，不复用前轮输出。 */
            phase_mark(PHASE_PREPARE);
            prepare_image();
            LOG_DEBUG("[HPU][PSYNC][ROUND] scenario=%u round=%u N=%u level=%u\n",
                      scenario, round, DEGREE, LEVEL);

            /* 2. 配置前清旧状态；完成后的清除只能由ISR执行。 */
            phase_mark(PHASE_CONFIGURE);
            csr_write(CSR_FAULT, FAULT_VALID);
            if (clear_completion() != 0) {
                irq_close();
                return case_fail_at(__FILE__, __LINE__);
            }
            csr_write(CSR_BASE_LO, (uint32_t)MEM_BASE);
            csr_write(CSR_BASE_HI, (uint32_t)(MEM_BASE >> 32U));
            csr_write(CSR_SIZE_LO, WINDOW_LINES);
            csr_write(CSR_SIZE_HI, 0U);
            if (expect_csr(CSR_BASE_LO, (uint32_t)MEM_BASE) != 0) {
                irq_close();
                return case_fail_at(__FILE__, __LINE__);
            }
            if (expect_csr(CSR_BASE_HI, (uint32_t)(MEM_BASE >> 32U)) != 0) {
                irq_close();
                return case_fail_at(__FILE__, __LINE__);
            }
            if (expect_csr(CSR_SIZE_LO, WINDOW_LINES) != 0) {
                irq_close();
                return case_fail_at(__FILE__, __LINE__);
            }
            if (expect_csr(CSR_SIZE_HI, 0U) != 0) {
                irq_close();
                return case_fail_at(__FILE__, __LINE__);
            }
            csr_write(CSR_COMMIT, COMMIT);
            if (wait_window() != 0) {
                irq_close();
                return case_fail_at(__FILE__, __LINE__);
            }

            /* 3. scenario之间close/open，第二轮rearm；不得二次进入M态CTE初始化。 */
            arm_rc = round == 0U ? irq_open() : irq_rearm();
            if (arm_rc != 0) {
                irq_close();
                return case_fail_at(__FILE__, __LINE__);
            }
            if (irq_event_count() != before) {
                irq_close();
                return case_fail_at(__FILE__, __LINE__);
            }
            if (irq_handler_count() != before) {
                irq_close();
                return case_fail_at(__FILE__, __LINE__);
            }
            if (irq_poll() != 0) {
                irq_close();
                return case_fail_at(__FILE__, __LINE__);
            }

            /* 4. 三个独立官方fixed入口，不是重复同一个完整程序冒充三种前序。 */
            phase_mark(PHASE_ISSUE);
            if (scenario == 0U)
                program_rc = hpu_run_instruction_psync_l4_n1024_idle();
            else if (scenario == 1U)
                program_rc = hpu_run_instruction_psync_l4_n1024_dma();
            else
                program_rc = hpu_run_instruction_psync_l4_n1024_compute();
            if (program_rc != 0) {
                irq_close();
                return case_fail_at(__FILE__, __LINE__);
            }

            /* 5. ISR负责claim257、W1C电平清除和complete；再确认终态及恰好一个新事件。 */
            phase_mark(PHASE_WAIT);
            const int wait_rc = wait_program();
            if (wait_rc != 0) {
                irq_close();
                irq_diagnose("psync-prefix-wait", 0U);
                return case_fail_at(__FILE__, __LINE__);
            }
            if (irq_event_count() != before + 1U) {
                irq_close();
                return case_fail_at(__FILE__, __LINE__);
            }
            if (irq_handler_count() != before + 1U) {
                irq_close();
                return case_fail_at(__FILE__, __LINE__);
            }
            if ((csr_read(CSR_IRQ) & IRQ_LEVEL) != 0U) {
                irq_close();
                return case_fail_at(__FILE__, __LINE__);
            }

            /* 6. 已写component对原golden；未写component必须仍是初始毒值；只读/guard全查。 */
            phase_mark(PHASE_COMPARE);
            const int data_rc = check_scenario_outputs(scenario == 0U ? -1 : (int)scenario - 1);
            const int memory_rc = check_memory();
            if (data_rc != 0) {
                irq_close();
                return case_fail_at(__FILE__, __LINE__);
            }
            if (memory_rc != 0) {
                irq_close();
                return case_fail_at(__FILE__, __LINE__);
            }
            LOG_DEBUG("[HPU][PSYNC][ROUND-PASS] scenario=%u round=%u events=%u cte-init=%u\n",
                      scenario, round, irq_event_count(), irq_cte_init_count());
            if (round == 1U) irq_close();
        }
    }
    if (irq_cte_init_count() != 1U)
        return case_fail_at(__FILE__, __LINE__);
    if (irq_event_count() != 6U)
        return case_fail_at(__FILE__, __LINE__);
    if (irq_handler_count() != 6U)
        return case_fail_at(__FILE__, __LINE__);
    return case_pass();
}
