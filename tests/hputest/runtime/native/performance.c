#include <performance.h>
#include <workload.h>
#include <hpu/irq.h>

enum {
    PROFILE_BAD_INITIAL_STATE = 1,
    PROFILE_BAD_SYNC_INDEX,
    PROFILE_WAIT_FAILED,
    PROFILE_EVENT_COUNT,
    PROFILE_REARM_FAILED,
    PROFILE_CLOCK_COUNT,
    PROFILE_CLOCK_ORDER,
    PROFILE_INVALID_SAMPLE,
    PROFILE_PROGRAM_FAILED
};

static int profile_error(performance_profile_state_t *state, int error) {
    if (state != NULL && state->error == 0) state->error = error;
    return -1;
}

int performance_wait(void) {
    /* 与功能用例相同的ISR完成判据；此等待绝不打印、补清IRQ或替代中断。 */
    return wait_program();
}

int performance_profile_init(performance_profile_state_t *state, size_t expected_syncs) {
    if (state == NULL) return 1;
    *state = (performance_profile_state_t){0};
    state->expected_syncs = expected_syncs;
    state->hooks = (hpu_execution_profile_hooks_t){state, performance_profile_cycle, performance_profile_wait};
    if (expected_syncs < 2U || expected_syncs > UINT32_MAX ||
        irq_event_count() != 0U || irq_handler_count() != 0U || irq_poll() != 0)
        return profile_error(state, PROFILE_BAD_INITIAL_STATE);
    return 0;
}

uint64_t performance_profile_cycle(void *user) {
    performance_profile_state_t *state = user;
    const uint64_t now = perf_cycle_read();
    if (state == NULL) return now;
    const unsigned index = state->read_count++;
    if (index >= 2U) {
        (void)profile_error(state, PROFILE_CLOCK_COUNT);
        return now;
    }
    state->recorded_cycles[index] = now;
    if (index == 0U) {
        state->start_sync = state->next_sync;
        if (state->next_sync == 0U || state->next_sync >= state->expected_syncs)
            (void)profile_error(state, PROFILE_CLOCK_ORDER);
    } else if (state->next_sync <= state->start_sync || now < state->recorded_cycles[0]) {
        (void)profile_error(state, PROFILE_CLOCK_ORDER);
    }
    return now;
}

int performance_profile_wait(void *user, size_t sync_index) {
    performance_profile_state_t *state = user;
    if (state == NULL) return -1;
    if (state->error != 0) return -1;
    if (sync_index != state->next_sync || sync_index >= state->expected_syncs)
        return profile_error(state, PROFILE_BAD_SYNC_INDEX);
    if (performance_wait() != 0) return profile_error(state, PROFILE_WAIT_FAILED);
    if (irq_event_count() != sync_index + 1U || irq_handler_count() != sync_index + 1U)
        return profile_error(state, PROFILE_EVENT_COUNT);
    ++state->next_sync;
    /* ISR已经claim/清电平/complete，只重新武装下一条PSYNC；保留所有SRAM对象。 */
    if (state->next_sync < state->expected_syncs && irq_rearm() != 0)
        return profile_error(state, PROFILE_REARM_FAILED);
    return 0;
}

int performance_profile_finish(performance_profile_state_t *state,
                               const hpu_execution_profile_sample_t *sample, int program_status) {
    if (state == NULL || sample == NULL) return 1;
    if (program_status != 0) return profile_error(state, PROFILE_PROGRAM_FAILED);
    if (state->error != 0) return 1;
    if (state->read_count != 2U) return profile_error(state, PROFILE_CLOCK_COUNT);
    if (state->next_sync != state->expected_syncs ||
        irq_event_count() != state->expected_syncs || irq_handler_count() != state->expected_syncs ||
        irq_poll() != 1)
        return profile_error(state, PROFILE_EVENT_COUNT);
    if (sample->valid != 1 || sample->start_cycles != state->recorded_cycles[0] ||
        sample->end_cycles != state->recorded_cycles[1] || sample->end_cycles < sample->start_cycles)
        return profile_error(state, PROFILE_INVALID_SAMPLE);
    return 0;
}
