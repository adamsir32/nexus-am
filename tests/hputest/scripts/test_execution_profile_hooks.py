"""实际profiling hooks的host状态机；不执行HPU字码，也不报告目标周期。"""
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest

from test_performance_cases import PROFILE_ABI_HEADER


ROOT = Path(__file__).resolve().parents[1]
HARNESS = r"""
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <performance.h>
#include <hpu/irq.h>

static uint32_t events, handlers, level;
static int completed, fail_rearm;
static unsigned waits, rearms, clocks;
static uint64_t ticks;
static const uint32_t resident_expected[4] = {9U, 19U, 29U, 39U};
static uint32_t resident[4];

uint32_t irq_event_count(void) { return events; }
uint32_t irq_handler_count(void) { return handlers; }
int irq_poll(void) { return completed; }
int irq_rearm(void) {
    assert(completed == 1 && level == 0U);
    assert(memcmp(resident, resident_expected, sizeof(resident)) == 0);
    ++rearms;
    ticks += 5U;
    if (fail_rearm) return 1;
    completed = 0;
    return 0;
}
/* CTE、设备reset、补clear或在callback内打印都不是profiling运行时的权限。 */
int irq_open(void) { assert(!"hooks must not reopen CTE/IRQ"); return 1; }
void irq_close(void) { assert(!"main owns IRQ close"); }
int irq_reset_events(void) { assert(!"hooks must preserve accumulated ISR events"); return 1; }
int irq_clear_and_verify(void) { assert(!"ISR owns completion clear"); return 1; }
void irq_diagnose(const char *phase, unsigned polls) { (void)phase; (void)polls; assert(!"main diagnoses after return"); }
void perf_cycle_enable(void) { assert(!"main enables counters before S-mode"); }
uint64_t perf_cycle_read(void) { ++clocks; ticks += 17U; return ticks; }
int wait_program(void) {
    ++waits;
    ticks += 100U;
    assert(memcmp(resident, resident_expected, sizeof(resident)) == 0);
    return completed != 1 || level != 0U;
}

static void reset_host(void) {
    events = handlers = level = 0U;
    completed = fail_rearm = 0;
    waits = rearms = clocks = 0U;
    ticks = 0U;
    memcpy(resident, resident_expected, sizeof(resident));
}
static void signal_irq(void) { ++events; ++handlers; completed = 1; level = 0U; }
static int ack(performance_profile_state_t *state, size_t sync) {
    return state->hooks.wait_complete(state->hooks.user, sync);
}
static uint64_t clock_read(performance_profile_state_t *state) {
    return state->hooks.read_cycles(state->hooks.user);
}
static int run_host_profile(performance_profile_state_t *state,
                            hpu_execution_profile_sample_t *sample, unsigned options) {
    /* 模拟官方ABI调用次序：预载、窗口内既有中途sync、窗口结束、尾写回sync。
     * 下列ticks只是探针值，用来证明窗口连续且不包含prefix/suffix，不是硬件测量。 */
    ticks += 500U;
    for (size_t sync = 0U; sync < 4U; ++sync) {
        if (sync == 1U) ticks += 200U;
        if (sync == 2U) ticks += 300U;
        if (sync == 3U) ticks += 400U;
        signal_irq();
        if ((options & 1U) && sync == 3U) completed = -1;
        const int status = ack(state, sync);
        if (status != 0) return status;
        if (sync == 0U) sample->start_cycles = clock_read(state);
        if (sync == 2U && !(options & 2U)) sample->end_cycles = clock_read(state);
    }
    sample->valid = 1;
    return 0;
}
static void rejected(performance_profile_state_t *state,
                     const hpu_execution_profile_sample_t *sample, int status) {
    assert(performance_profile_finish(state, sample, status) != 0);
    assert(state->error != 0);
}

int main(int argc, char **argv) {
    assert(argc == 2);
    const unsigned mode = (unsigned)atoi(argv[1]);
    performance_profile_state_t state;
    hpu_execution_profile_sample_t sample = {0};
    reset_host();
    if (mode == 18U) {
        assert(performance_profile_init(NULL, 4U) != 0);
        assert(performance_profile_init(&state, 0U) != 0);
        assert(performance_profile_init(&state, 1U) != 0);
#if SIZE_MAX > UINT32_MAX
        assert(performance_profile_init(&state, (size_t)UINT32_MAX + 1U) != 0);
#endif
        events = 1U;
        assert(performance_profile_init(&state, 4U) != 0);
        events = 0U; handlers = 1U;
        assert(performance_profile_init(&state, 4U) != 0);
        handlers = 0U; completed = 1;
        assert(performance_profile_init(&state, 4U) != 0);
        assert(waits == 0U && rearms == 0U && clocks == 0U);
        return 0;
    }
    assert(performance_profile_init(&state, 4U) == 0);
    assert(state.hooks.user == &state && state.hooks.read_cycles == performance_profile_cycle);
    assert(state.hooks.wait_complete == performance_profile_wait);
    switch (mode) {
    case 0:
        assert(run_host_profile(&state, &sample, 0U) == 0);
        assert(performance_profile_finish(&state, &sample, 0) == 0);
        assert(events == 4U && handlers == 4U && waits == 4U && rearms == 3U);
        assert(state.next_sync == 4U && state.read_count == 2U && clocks == 2U);
        assert(sample.valid == 1 && sample.start_cycles == 622U && sample.end_cycles == 1349U);
        assert(sample.end_cycles - sample.start_cycles == 727U && ticks == 1849U);
        break;
    case 1: /* sync_index必须从0开始，不能跳过预加载等待。 */
        assert(ack(&state, 1U) != 0 && waits == 0U && rearms == 0U);
        rejected(&state, &sample, 0);
        break;
    case 2: /* 同一序号不能重放旧ISR。 */
    case 3: /* 也不能跳过中途序号。 */
        signal_irq(); assert(ack(&state, 0U) == 0);
        assert(ack(&state, mode == 2U ? 0U : 2U) != 0 && waits == 1U);
        rejected(&state, &sample, 0);
        break;
    case 4: /* MMIO电平而没有真实ISR不能完成PSYNC。 */
        level = 1U;
        assert(ack(&state, 0U) != 0 && events == 0U && rearms == 0U);
        rejected(&state, &sample, 0);
        break;
    case 5: /* ISR错误不能冒充完成。 */
        completed = -1; handlers = 1U;
        assert(ack(&state, 0U) != 0 && rearms == 0U);
        rejected(&state, &sample, 0);
        break;
    case 6: /* 即使done为真，多一次handler也要拒绝。 */
        signal_irq(); ++handlers;
        assert(ack(&state, 0U) != 0 && rearms == 0U);
        rejected(&state, &sample, 0);
        break;
    case 7:
        signal_irq(); fail_rearm = 1;
        assert(ack(&state, 0U) != 0 && rearms == 1U);
        rejected(&state, &sample, 0);
        break;
    case 8: /* 已有end timestamp也不能掩盖窗口外尾部写回失败。 */
        assert(run_host_profile(&state, &sample, 1U) != 0);
        assert(sample.start_cycles == 622U && sample.end_cycles == 1349U && sample.valid == 0);
        assert(state.next_sync == 3U && rearms == 3U);
        rejected(&state, &sample, -1);
        break;
    case 9: /* 首个PSYNC完成前不能记start。 */
        (void)clock_read(&state);
        assert(state.error != 0 && ack(&state, 0U) != 0);
        rejected(&state, &sample, 0);
        break;
    case 10: /* 两次端点必须跨越不同PSYNC。 */
        signal_irq(); assert(ack(&state, 0U) == 0);
        (void)clock_read(&state); (void)clock_read(&state);
        assert(state.error != 0);
        rejected(&state, &sample, 0);
        break;
    case 11:
        assert(run_host_profile(&state, &sample, 0U) == 0);
        (void)clock_read(&state);
        assert(state.read_count == 3U);
        rejected(&state, &sample, 0);
        break;
    case 12: /* 时钟倒退使整个sample失效。 */
        signal_irq(); assert(ack(&state, 0U) == 0);
        ticks = 1000U; (void)clock_read(&state);
        signal_irq(); assert(ack(&state, 1U) == 0);
        ticks = 0U; (void)clock_read(&state);
        assert(state.error != 0);
        rejected(&state, &sample, 0);
        break;
    case 13:
        assert(run_host_profile(&state, &sample, 2U) == 0 && state.read_count == 1U);
        rejected(&state, &sample, 0);
        break;
    case 14:
    case 21:
        assert(run_host_profile(&state, &sample, 0U) == 0);
        if (mode == 14U) ++sample.end_cycles;
        else ++sample.start_cycles;
        rejected(&state, &sample, 0);
        break;
    case 15:
        assert(run_host_profile(&state, &sample, 0U) == 0);
        sample.valid = 0;
        rejected(&state, &sample, 0);
        break;
    case 16:
        assert(run_host_profile(&state, &sample, 0U) == 0);
        rejected(&state, &sample, -4);
        break;
    case 17:
        assert(run_host_profile(&state, &sample, 0U) == 0);
        ++events; ++handlers;
        rejected(&state, &sample, 0);
        break;
    case 19:
        signal_irq(); level = 1U;
        assert(ack(&state, 0U) != 0 && rearms == 0U);
        rejected(&state, &sample, 0);
        break;
    case 20:
        assert(run_host_profile(&state, &sample, 0U) == 0);
        completed = 0;
        rejected(&state, &sample, 0);
        break;
    default: abort();
    }
    assert(memcmp(resident, resident_expected, sizeof(resident)) == 0);
    return 0;
}
"""


class ExecutionProfileHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent = ROOT / "build/host-tests"
        parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(prefix="continuous-profile-hooks-", dir=parent)
        cls.addClassCleanup(cls.temporary.cleanup)
        directory = Path(cls.temporary.name)
        (directory / "program.h").write_text(PROFILE_ABI_HEADER)
        source = directory / "hooks.c"
        source.write_text(HARNESS)
        cls.binary = directory / "hooks"
        subprocess.run(shlex.split(os.environ.get("HOST_CC", "cc")) + [
            "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-DWORKLOAD_HOST_TEST",
            "-I", str(directory), "-I", str(ROOT / "test/host/include"), "-I", str(ROOT / "include"),
            str(source), str(ROOT / "runtime/native/performance.c"), "-o", str(cls.binary)], check=True)

    def run_scenarios(self, scenarios):
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                result = subprocess.run([str(self.binary), str(scenario)], check=True, capture_output=True)
                self.assertEqual(result.stdout, b"", "callbacks不能在测量过程中打印")

    def test_single_continuous_window_excludes_prefix_and_suffix_but_waits_for_both(self):
        self.run_scenarios((0,))

    def test_sync_freshness_wait_errors_exact_events_and_rearm_are_required(self):
        self.run_scenarios((1, 2, 3, 4, 5, 6, 7, 8, 17, 18, 19, 20))

    def test_clock_count_order_sample_validity_and_final_status_are_required(self):
        self.run_scenarios((*range(9, 17), 21))


if __name__ == "__main__":
    unittest.main()
