/* One target CPU program runs both existing HPU programs with live DDR handoff. */
#include <workload.h>
#include <pir_cpu.h>
#include <pir_unified_runtime.h>
#include <hpu/irq.h>
#include <hpu/log.h>
#include <bfv_sealpir_2d_small_stage0_concentrated_000.h>
#include <bfv_sealpir_2d_small_stage1_concentrated_000.h>

static uint32_t decomposed_plaintexts[PIR_CPU_PLAINTEXTS * PIR_CPU_DEGREE];
static struct pir_cpu_encoder encoder;

static int configure_window(unsigned lines) {
    phase_mark(PHASE_CONFIGURE);
    csr_write(CSR_FAULT, FAULT_VALID);
    if (clear_completion() != 0) {
        LOG_ERROR("[PIR][WINDOW] stale completion level did not clear\n");
        return 1;
    }
    csr_write(CSR_BASE_LO, (uint32_t)MEM_BASE);
    csr_write(CSR_BASE_HI, (uint32_t)(MEM_BASE >> 32U));
    csr_write(CSR_SIZE_LO, lines);
    csr_write(CSR_SIZE_HI, 0U);
    if (expect_csr(CSR_BASE_LO, (uint32_t)MEM_BASE) ||
        expect_csr(CSR_BASE_HI, (uint32_t)(MEM_BASE >> 32U)) ||
        expect_csr(CSR_SIZE_LO, lines) || expect_csr(CSR_SIZE_HI, 0U)) return 1;
    csr_write(CSR_COMMIT, COMMIT);
    return wait_window();
}

static int run_stage(int (*entry)(void), unsigned expected_events, const char *name) {
    phase_mark(PHASE_ISSUE);
    const int issue = entry();
    if (issue != 0) {
        LOG_ERROR("[PIR][%s][ISSUE] rc=%d\n", name, issue);
        return 1;
    }
    phase_mark(PHASE_WAIT);
    if (wait_program() != 0) {
        irq_diagnose(name, 0U);
        return 1;
    }
    if (irq_event_count() != expected_events ||
        irq_handler_count() != expected_events ||
        (csr_read(CSR_IRQ) & IRQ_LEVEL) != 0U ||
        (csr_read(CSR_FAULT) & FAULT_VALID) != 0U) {
        LOG_ERROR("[PIR][%s][IRQ] events=%u handlers=%u expected=%u\n",
                  name, irq_event_count(), irq_handler_count(), expected_events);
        irq_diagnose(name, 0U);
        return 1;
    }
    return 0;
}

int main(void) {
    int rc = 1;
    phase_mark(PHASE_PREPARE);
    pir_prepare_stage0();
    if (configure_window(STAGE0_WINDOW_LINES) != 0) goto fail;
    if (irq_reset_events() != 0 || irq_open() != 0) goto close_fail;
    if (irq_event_count() != 0U || irq_handler_count() != 0U) goto close_fail;
    if (run_stage(hpu_run_bfv_sealpir_2d_small_stage0_concentrated_000,
                  1U, "stage0") != 0) goto close_fail;

    phase_mark(PHASE_COMPARE);
    if (pir_check_stage0() != 0) goto close_fail;
    /* This reads the actual HPU DDR result. Golden was only an independent check. */
    const int decompose_rc = pir_cpu_decompose(
        line_ptr(0U), STAGE0_WINDOW_LINES, stage0_cpu_limbs, PIR_CPU_OUTPUT_LIMBS,
        &pir_parameters, decomposed_plaintexts, PIR_CPU_PLAINTEXTS * PIR_CPU_DEGREE);
    if (decompose_rc != 0) {
        LOG_ERROR("[PIR][CPU][DECOMPOSE] rc=%d\n", decompose_rc);
        goto close_fail;
    }

    /* Stage1 reuses DDR only after all stage0 output coefficients are retained. */
    phase_mark(PHASE_PREPARE);
    pir_prepare_stage1();
    if (pir_cpu_encoder_init(&encoder, &pir_parameters) != 0) {
        LOG_ERROR("[PIR][CPU][ENCODER_INIT] invalid parameters\n");
        goto close_fail;
    }
    const int encode_rc = pir_cpu_encode(
        decomposed_plaintexts, PIR_CPU_PLAINTEXTS * PIR_CPU_DEGREE,
        line_ptr(0U), STAGE1_WINDOW_LINES, stage1_cpu_limbs, PIR_CPU_INPUT_LIMBS,
        &pir_parameters, &encoder);
    if (encode_rc != 0) {
        LOG_ERROR("[PIR][CPU][ENCODE] rc=%d\n", encode_rc);
        goto close_fail;
    }
    if (pir_check_stage1_fixed_before_issue() != 0) goto close_fail;
    clean_lines(STAGE1_IMAGE_LINES);
    if (configure_window(STAGE1_WINDOW_LINES) != 0) goto close_fail;
    /* The first ISR has cleared/completed source 257; rearm retains cumulative counts. */
    if (irq_rearm() != 0) goto close_fail;
    if (irq_event_count() != 1U || irq_handler_count() != 1U) goto close_fail;
    if (run_stage(hpu_run_bfv_sealpir_2d_small_stage1_concentrated_000,
                  2U, "stage1") != 0) goto close_fail;
    irq_close();
    phase_mark(PHASE_COMPARE);
    if (pir_check_stage1() != 0) goto fail;
    rc = case_pass();
    return rc;

close_fail:
    irq_close();
fail:
    return case_fail_at(__FILE__, __LINE__);
}
