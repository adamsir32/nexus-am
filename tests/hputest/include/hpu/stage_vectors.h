#ifndef HPU_STAGE_VECTORS_H
#define HPU_STAGE_VECTORS_H

#include <stdint.h>

/* 两行K8种子来自当前上游模型；完整oracle表只供独立C参考，不发往HPU。 */
enum { STAGE_WORDS = 128, STAGE_LINES = 2, STAGE_FULL_WORDS = 2048,
       STAGE_MODULUS = 50061313 };

extern const uint32_t ntt_twiddle_0[STAGE_WORDS];
extern const uint32_t ntt_twiddle_1[STAGE_WORDS];
extern const uint32_t ntt_twiddle_11[STAGE_WORDS];
extern const uint32_t intt_twiddle_0[STAGE_WORDS];
extern const uint32_t intt_twiddle_1[STAGE_WORDS];
extern const uint32_t intt_twiddle_11[STAGE_WORDS];
extern const uint32_t ntt_full_0[STAGE_FULL_WORDS];
extern const uint32_t ntt_full_1[STAGE_FULL_WORDS];
extern const uint32_t ntt_full_11[STAGE_FULL_WORDS];
extern const uint32_t intt_full_0[STAGE_FULL_WORDS];
extern const uint32_t intt_full_1[STAGE_FULL_WORDS];
extern const uint32_t intt_full_11[STAGE_FULL_WORDS];

/* 输入twiddle为完整oracle表；不发指令，不执行完整变换的前后因子。 */
int stage_golden(const uint32_t *input, const uint32_t *twiddle,
                 uint32_t *output, unsigned words, uint32_t q,
                 unsigned stage, unsigned inverse);

#endif
