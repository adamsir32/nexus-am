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

/* PZL1 stores 256-byte DDR lines as zero runs or verbatim runs. Validate the
 * complete stream before writing DDR, so a truncated fixture fails clearly. */
static uint32_t image_u32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8U) |
           ((uint32_t)p[2] << 16U) | ((uint32_t)p[3] << 24U);
}

enum image_mode { IMAGE_VALIDATE, IMAGE_LOAD, IMAGE_POSTCHECK, IMAGE_PRECHECK };

static int walk_image(const uint8_t *image, unsigned bytes, unsigned lines,
                      enum image_mode mode, const uint8_t *writable,
                      const uint8_t *hpu_writable, const char *name) {
    if (bytes < 8U || image[0] != 'P' || image[1] != 'Z' ||
        image[2] != 'L' || image[3] != '1' || image_u32(image + 4U) != lines) {
        LOG_ERROR("[PIR][%s][IMAGE] bad header or line count\n", name);
        return 1;
    }
    unsigned offset = 8U, line = 0U;
    while (line < lines) {
        if (bytes - offset < 4U) goto malformed;
        const uint32_t token = image_u32(image + offset);
        offset += 4U;
        const unsigned count = token & UINT32_C(0x7fffffff);
        const int zero = (token & UINT32_C(0x80000000)) != 0U;
        if (count == 0U || count > lines - line ||
            (!zero && (uint64_t)count * LINE_BYTES > bytes - offset))
            goto malformed;
        for (unsigned span = 0U; span < count; ++span) {
            volatile uint32_t *actual = line_ptr(line + span);
            if (mode == IMAGE_VALIDATE) continue;
            if (mode == IMAGE_POSTCHECK && writable[line + span]) continue;
            if (mode == IMAGE_PRECHECK && writable[line + span] &&
                !hpu_writable[line + span]) continue;
            for (unsigned word = 0U; word < LINE_WORDS; ++word) {
                const uint32_t expected = zero ? 0U :
                    image_u32(image + offset + span * LINE_BYTES + word * 4U);
                if (mode == IMAGE_LOAD) {
                    actual[word] = expected;
                } else if (actual[word] != expected) {
                    workload_trace.first_line = line + span;
                    workload_trace.first_word = word;
                    workload_trace.actual = actual[word];
                    workload_trace.expected = expected;
                    ++workload_trace.errors;
                    LOG_ERROR("[PIR][%s][GUARD] line=%u word=%u got=%u expected=%u\n",
                              name, line + span, word, actual[word], expected);
                    return 1;
                }
            }
        }
        if (!zero) offset += count * LINE_BYTES;
        line += count;
    }
    if (offset == bytes) return 0;
malformed:
    LOG_ERROR("[PIR][%s][IMAGE] malformed run stream at line=%u byte=%u\n",
              name, line, offset);
    return 1;
}

static int unpack_image(const uint8_t *image, unsigned bytes, unsigned lines,
                         const char *name) {
    if (walk_image(image, bytes, lines, IMAGE_VALIDATE, 0, 0, name) != 0 ||
        walk_image(image, bytes, lines, IMAGE_LOAD, 0, 0, name) != 0) return 1;
    clean_lines(lines);
    return 0;
}

int pir_prepare_stage0(void) {
    return unpack_image(stage0_compressed_image, STAGE0_COMPRESSED_BYTES,
                         STAGE0_IMAGE_LINES, "stage0");
}
int pir_prepare_stage1(void) {
    stage1_input_snapshot_ready = 0U;
    return unpack_image(stage1_compressed_image, STAGE1_COMPRESSED_BYTES,
                         STAGE1_IMAGE_LINES, "stage1");
}

static int verify_stage(const struct output_span *outputs, unsigned output_count,
                        const uint32_t *golden, const uint8_t *image,
                        unsigned image_bytes, const uint8_t *writable, unsigned image_lines,
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
    return walk_image(image, image_bytes, image_lines, IMAGE_POSTCHECK,
                      writable, 0, name);
}

int pir_check_stage0(void) {
    return verify_stage(stage0_outputs, STAGE0_OUTPUT_COUNT, stage0_golden_words,
                        stage0_compressed_image, STAGE0_COMPRESSED_BYTES, stage0_writable_lines,
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
                     stage1_compressed_image, STAGE1_COMPRESSED_BYTES, stage1_cpu_writable_lines,
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
    stage1_input_snapshot_ready = 0U;
    if (walk_image(stage1_compressed_image, STAGE1_COMPRESSED_BYTES,
                   STAGE1_IMAGE_LINES, IMAGE_PRECHECK,
                   stage1_cpu_writable_lines, stage1_writable_lines,
                   "stage1") != 0) return 1;
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
