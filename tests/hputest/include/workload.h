#ifndef FRONTEND_WORKLOAD_H
#define FRONTEND_WORKLOAD_H

#include <platform.h>
#include <layout.h>

enum { PHASE_PREPARE = 1U, PHASE_CONFIGURE, PHASE_ISSUE, PHASE_WAIT,
       PHASE_COMPARE, PHASE_DONE, PHASE_FAIL };

/* 静默版保留这些符号，可从ELF符号/内存读出阶段、CSR和首错。 */
struct workload_progress {
    uint32_t phase, status, irq, fault, errors;
    uint32_t first_line, first_word, actual, expected;
    uint64_t wait_cycles;
    uint64_t cycle_start, cycle_end;
    /* 尾部追加，保留已有phase/MMIO/首错/cycle字段的RAM偏移。 */
    uint32_t source_line;
};
extern volatile struct workload_progress workload_trace;
extern const uint32_t initial_image[IMAGE_LINES * LINE_WORDS];
extern const uint32_t golden_words[GOLDEN_WORDS];
extern const uint8_t writable_lines[IMAGE_LINES];

void phase_mark(unsigned phase);
void prepare_image(void);
int check_results(void);
int check_memory(void);
int case_fail_at(const char *source, unsigned line);
/* 仅供旧接收端调用兼容；独立main应传入自己的__FILE__和__LINE__。 */
int case_fail(unsigned line);
int case_pass(void);

#endif
