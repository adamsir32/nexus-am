#include <workload.h>
#include <pir_unified_runtime.h>
#include <hpu/log.h>

volatile struct workload_progress workload_trace;
/* Only the 96 CPU-produced inputs are retained (1.5 MiB), not the DDR image. */
static uint32_t stage1_input_snapshot[PIR_CPU_INPUT_LIMBS][PIR_CPU_DEGREE];
static unsigned stage1_input_snapshot_ready;

void phase_mark(unsigned phase) {
    workload_trace.phase = phase;
    LOG_DEBUG("[PIR][CPU] phase=%u\n", phase);
}

void clean_lines(unsigned lines) {
    const uintptr_t end = MEM_BASE + (uintptr_t)lines * LINE_BYTES;
    for (uintptr_t address = MEM_BASE; address < end; address += 64U) {
#ifdef PIR_UNIFIED_HOST_TEST
        (void)address;
#else
        __asm__ volatile(".insn i 0x0f, 2, x0, %0, 2" : : "r"(address) : "memory");
#endif
    }
    mem_fence();
}

void invalidate_lines(unsigned lines) {
    const uintptr_t end = MEM_BASE + (uintptr_t)lines * LINE_BYTES;
    for (uintptr_t address = MEM_BASE; address < end; address += 64U) {
#ifdef PIR_UNIFIED_HOST_TEST
        (void)address;
#else
        __asm__ volatile(".insn i 0x0f, 2, x0, %0, 0" : : "r"(address) : "memory");
#endif
    }
    mem_fence();
}

static void copy_image(const uint32_t *image, unsigned lines) {
    volatile uint32_t *ddr = line_ptr(0U);
    for (unsigned index = 0U; index < lines * LINE_WORDS; ++index)
        ddr[index] = image[index];
    clean_lines(lines);
}

void pir_prepare_stage0(void) { copy_image(stage0_initial_image, STAGE0_IMAGE_LINES); }
void pir_prepare_stage1(void) {
    stage1_input_snapshot_ready = 0U;
    copy_image(stage1_initial_image, STAGE1_IMAGE_LINES);
}

static int verify_stage(const struct output_span *outputs, unsigned output_count,
                        const uint32_t *golden, const uint32_t *initial,
                        const uint8_t *writable, unsigned image_lines,
                        const char *name) {
    unsigned mismatches = 0U;
    invalidate_lines(image_lines);
    for (unsigned index = 0U; index < output_count; ++index) {
        const struct output_span *span = &outputs[index];
        volatile const uint32_t *actual = line_ptr(span->line);
        for (unsigned word = 0U; word < span->words; ++word) {
            const uint32_t value = actual[word];
            const uint32_t expected = golden[span->golden_word + word];
            if (value == expected && value < span->modulus) continue;
            if (mismatches == 0U) {
                workload_trace.first_line = span->line + word / LINE_WORDS;
                workload_trace.first_word = word % LINE_WORDS;
                workload_trace.actual = value;
                workload_trace.expected = expected;
                LOG_ERROR("[PIR][%s][GOLDEN] line=%u word=%u got=%u expected=%u\n",
                          name, workload_trace.first_line, workload_trace.first_word,
                          value, expected);
            }
            ++mismatches;
        }
    }
    workload_trace.errors += mismatches;
    if (mismatches != 0U) return 1;
    for (unsigned line = 0U; line < image_lines; ++line) {
        if (writable[line]) continue;
        volatile const uint32_t *actual = line_ptr(line);
        for (unsigned word = 0U; word < LINE_WORDS; ++word) {
            const uint32_t expected = initial[line * LINE_WORDS + word];
            if (actual[word] == expected) continue;
            workload_trace.first_line = line;
            workload_trace.first_word = word;
            workload_trace.actual = actual[word];
            workload_trace.expected = expected;
            ++workload_trace.errors;
            LOG_ERROR("[PIR][%s][GUARD] line=%u word=%u got=%u expected=%u\n",
                      name, line, word, actual[word], expected);
            return 1;
        }
    }
    return 0;
}

int pir_check_stage0(void) {
    return verify_stage(stage0_outputs, STAGE0_OUTPUT_COUNT, stage0_golden_words,
                        stage0_initial_image, stage0_writable_lines,
                        STAGE0_IMAGE_LINES, "stage0");
}

int pir_check_stage1(void) {
    if (stage1_input_snapshot_ready == 0U) {
        LOG_ERROR("[PIR][stage1][GUARD] CPU input snapshot missing\n");
        return 1;
    }
    /* The union bitmap excludes CPU inputs from the initial-image comparison.
     * Check them against their actual pre-issue values instead. */
    if (verify_stage(stage1_outputs, STAGE1_OUTPUT_COUNT, stage1_golden_words,
                     stage1_initial_image, stage1_cpu_writable_lines,
                     STAGE1_IMAGE_LINES, "stage1") != 0) return 1;
    for (unsigned index = 0U; index < PIR_CPU_INPUT_LIMBS; ++index) {
        const struct pir_cpu_input_limb *limb = &stage1_cpu_limbs[index];
        volatile const uint32_t *actual = line_ptr(limb->line);
        for (unsigned word = 0U; word < PIR_CPU_DEGREE; ++word) {
            const uint32_t expected = stage1_input_snapshot[index][word];
            if (actual[word] == expected) continue;
            workload_trace.first_line = limb->line + word / LINE_WORDS;
            workload_trace.first_word = word % LINE_WORDS;
            workload_trace.actual = actual[word];
            workload_trace.expected = expected;
            ++workload_trace.errors;
            LOG_ERROR("[PIR][stage1][CPU_INPUT_GUARD] line=%u word=%u got=%u expected=%u\n",
                      workload_trace.first_line, workload_trace.first_word,
                      workload_trace.actual, workload_trace.expected);
            return 1;
        }
    }
    return 0;
}

int pir_check_stage1_fixed_before_issue(void) {
    volatile const uint32_t *ddr = line_ptr(0U);
    stage1_input_snapshot_ready = 0U;
    for (unsigned line = 0U; line < STAGE1_IMAGE_LINES; ++line) {
        if (stage1_cpu_writable_lines[line] && !stage1_writable_lines[line]) continue;
        for (unsigned word = 0U; word < LINE_WORDS; ++word) {
            const unsigned index = line * LINE_WORDS + word;
            if (ddr[index] != stage1_initial_image[index]) {
                LOG_ERROR("[PIR][stage1][FIXED] line=%u word=%u\n", line, word);
                return 1;
            }
        }
    }
    for (unsigned index = 0U; index < PIR_CPU_INPUT_LIMBS; ++index) {
        const struct pir_cpu_input_limb *limb = &stage1_cpu_limbs[index];
        if (limb->words != PIR_CPU_DEGREE || limb->line > STAGE1_IMAGE_LINES ||
            PIR_CPU_DEGREE / LINE_WORDS > STAGE1_IMAGE_LINES - limb->line) {
            LOG_ERROR("[PIR][stage1][CPU_INPUT_GUARD] invalid input span=%u\n", index);
            return 1;
        }
        const volatile uint32_t *source = line_ptr(limb->line);
        for (unsigned word = 0U; word < PIR_CPU_DEGREE; ++word)
            stage1_input_snapshot[index][word] = source[word];
    }
    stage1_input_snapshot_ready = 1U;
    return 0;
}

int case_fail_at(const char *source, unsigned line) {
    const unsigned previous = workload_trace.phase;
    workload_trace.status = csr_read(CSR_STATUS);
    workload_trace.irq = csr_read(CSR_IRQ);
    workload_trace.fault = csr_read(CSR_FAULT);
    workload_trace.source_line = line;
    workload_trace.phase = PHASE_FAIL;
    LOG_ERROR("[PIR][FAIL] source=%s line=%u phase=%u status=0x%x irq=0x%x fault=0x%x\n",
              source, line, previous, workload_trace.status, workload_trace.irq,
              workload_trace.fault);
    return 1;
}

int case_fail(unsigned line) { return case_fail_at("<legacy>", line); }

int case_pass(void) {
    phase_mark(PHASE_DONE);
    LOG_EVENT("[PIR][PASS] two HPU stages, CPU decomposition and encoding\n");
    return 0;
}
