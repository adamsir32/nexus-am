/* Shared Nexus-AM control path for three separately packaged applications. */
#include <workload.h>
#include <program.h>
#include <hpu/log.h>
#include <hpu/irq.h>

#ifndef APPLICATION_ENTRY
#error APPLICATION_ENTRY must name the a generated HPU entry
#endif

int main(void) {
    LOG_EVENT("[HPU][START] %s N=%u level=%u inst=%u dma=%u lines=%u\n",
              CASE_ID, DEGREE, LEVEL, INSTRUCTION_COUNT, DMA_COUNT, WINDOW_LINES);
    phase_mark(PHASE_PREPARE);
    prepare_image();

    phase_mark(PHASE_CONFIGURE);
    csr_write(CSR_FAULT, FAULT_VALID);
    if (clear_completion() != 0) return case_fail_at(__FILE__, __LINE__);
    csr_write(CSR_BASE_LO, (uint32_t)MEM_BASE);
    csr_write(CSR_BASE_HI, (uint32_t)(MEM_BASE >> 32U));
    csr_write(CSR_SIZE_LO, WINDOW_LINES);
    csr_write(CSR_SIZE_HI, 0U);
    if (expect_csr(CSR_BASE_LO, (uint32_t)MEM_BASE) != 0 ||
        expect_csr(CSR_BASE_HI, (uint32_t)(MEM_BASE >> 32U)) != 0 ||
        expect_csr(CSR_SIZE_LO, WINDOW_LINES) != 0 ||
        expect_csr(CSR_SIZE_HI, 0U) != 0)
        return case_fail_at(__FILE__, __LINE__);
    csr_write(CSR_COMMIT, COMMIT);
    if (wait_window() != 0) return case_fail_at(__FILE__, __LINE__);

    if (irq_reset_events() != 0) return case_fail_at(__FILE__, __LINE__);
    if (irq_open() != 0) {
        irq_close();
        return case_fail_at(__FILE__, __LINE__);
    }
    if (irq_event_count() != 0U || irq_handler_count() != 0U) {
        irq_close();
        return case_fail_at(__FILE__, __LINE__);
    }

    phase_mark(PHASE_ISSUE);
    const int program_rc = APPLICATION_ENTRY();
    if (program_rc != 0) {
        irq_close();
        LOG_ERROR("[HPU][PROGRAM] %s rc=%d\n", CASE_ID, program_rc);
        return case_fail_at(__FILE__, __LINE__);
    }
    phase_mark(PHASE_WAIT);
    const int wait_rc = wait_program();
    irq_close();
    if (wait_rc != 0) {
        irq_diagnose("program-wait", 0U);
        return case_fail_at(__FILE__, __LINE__);
    }
    if (irq_event_count() != 1U || irq_handler_count() != 1U ||
        (csr_read(CSR_IRQ) & IRQ_LEVEL) != 0U)
        return case_fail_at(__FILE__, __LINE__);

    phase_mark(PHASE_COMPARE);
    const int data_rc = check_results();
    const int memory_rc = check_memory();
    if (data_rc != 0 || memory_rc != 0)
        return case_fail_at(__FILE__, __LINE__);
    return case_pass();
}
