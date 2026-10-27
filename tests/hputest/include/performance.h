#ifndef FRONTEND_PERFORMANCE_H
#define FRONTEND_PERFORMANCE_H

#include <program.h>
#include <hpu/perf.h>

/* 等待末尾PSYNC的真实CPU中断及VALID/空闲；不补清IRQ、不打印、不做结果自检。 */
int performance_wait(void);

/* 沿用官方program.h的hooks/sample ABI；只跟踪本次连续窗口的IRQ及clock合同。 */
typedef struct performance_profile_state {
    hpu_execution_profile_hooks_t hooks;
    size_t expected_syncs, next_sync;
    unsigned read_count;
    int error;
    uint64_t recorded_cycles[2];
    size_t start_sync;
} performance_profile_state_t;

/* main完成M态配置后显式reset/open IRQ；本函数不初始化CTE、不重置设备。 */
int performance_profile_init(performance_profile_state_t *state, size_t expected_syncs);
uint64_t performance_profile_cycle(void *user);
int performance_profile_wait(void *user, size_t sync_index);
/* main在profiled入口返回后close IRQ，再验证尾部写回、全部PSYNC及sample均成功。 */
int performance_profile_finish(performance_profile_state_t *state,
                               const hpu_execution_profile_sample_t *sample, int program_status);

#endif
