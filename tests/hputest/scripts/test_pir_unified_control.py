#!/usr/bin/env python3
"""Compile the actual target main against host control stubs and inject failures."""

from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "src/08_pir_psi/08_04_pir_unified.c"
PIR = ROOT / "runtime/pir"
HEADER = r'''
#include <stdint.h>
#include <stddef.h>
#include <pir_cpu.h>
#define MEM_BASE UINT64_C(0x87000000)
#define STAGE0_WINDOW_LINES 30701U
#define STAGE1_WINDOW_LINES 45549U
#define STAGE1_IMAGE_LINES 45613U
#define PHASE_PREPARE 1U
#define PHASE_CONFIGURE 2U
#define PHASE_ISSUE 3U
#define PHASE_WAIT 4U
#define PHASE_COMPARE 5U
#define CSR_FAULT 0x18U
#define CSR_IRQ 0x1cU
#define CSR_BASE_LO 0U
#define CSR_BASE_HI 4U
#define CSR_SIZE_LO 8U
#define CSR_SIZE_HI 12U
#define CSR_COMMIT 16U
#define FAULT_VALID 1U
#define IRQ_LEVEL 1U
#define COMMIT 1U
extern const struct pir_cpu_output_limb stage0_cpu_limbs[16];
extern const struct pir_cpu_input_limb stage1_cpu_limbs[96];
extern const struct pir_cpu_parameters pir_parameters;
uint32_t csr_read(uintptr_t address);
void csr_write(uintptr_t address, uint32_t value);
volatile uint32_t *line_ptr(unsigned line);
int expect_csr(uintptr_t address, uint32_t expected);
int clear_completion(void);
int wait_window(void);
int wait_program(void);
void phase_mark(unsigned phase);
void clean_lines(unsigned lines);
int case_fail_at(const char *source, unsigned line);
int case_pass(void);
'''
IRQ = r'''
#include <stdint.h>
int irq_reset_events(void);
int irq_open(void);
int irq_rearm(void);
void irq_close(void);
uint32_t irq_event_count(void);
uint32_t irq_handler_count(void);
void irq_diagnose(const char *phase, unsigned polls);
'''
HARNESS = r'''
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <workload.h>
#include <hpu/irq.h>
int pir_target_main(void);
static volatile uint32_t ddr[64];
static int mode, stage, ready, opened, prepared, decomposed, encoded, closed;
static uint32_t events, handlers;
const struct pir_cpu_output_limb stage0_cpu_limbs[16] = {{0}};
const struct pir_cpu_input_limb stage1_cpu_limbs[96] = {{0}};
const struct pir_cpu_parameters pir_parameters = {0};
uint32_t csr_read(uintptr_t address) { (void)address; return 0U; }
void csr_write(uintptr_t address, uint32_t value) {
  if (address == CSR_SIZE_LO) {
    stage = value == STAGE1_WINDOW_LINES ? 1 : 0;
    if (stage == 1) assert(decomposed && encoded);
  }
}
volatile uint32_t *line_ptr(unsigned line) { assert(line == 0); return ddr; }
int expect_csr(uintptr_t address, uint32_t expected) { (void)address; (void)expected; return 0; }
int clear_completion(void) { return 0; }
int wait_window(void) { return mode == 6 && stage == 1; }
int wait_program(void) {
  if ((mode == 1 || mode == 2) && stage == 0) return 1;
  if (mode == 7 && stage == 1) return 1;
  ++events; ++handlers; ready = 1; return 0;
}
void phase_mark(unsigned phase) { (void)phase; }
void clean_lines(unsigned lines) { assert(lines == STAGE1_IMAGE_LINES); }
int case_fail_at(const char *source, unsigned line) {
  (void)source; (void)line; assert(!opened); return 1;
}
int case_pass(void) { assert(stage == 1 && ready && closed); return 0; }
int irq_reset_events(void) { assert(!opened); events = handlers = 0; return 0; }
int irq_open(void) { assert(!opened && stage == 0); opened = 1; return 0; }
int irq_rearm(void) {
  assert(opened && stage == 1 && events == 1 && handlers == 1);
  if (mode == 8) return 1;
  ready = 0; return 0;
}
void irq_close(void) { opened = 0; closed = 1; }
uint32_t irq_event_count(void) { return events; }
uint32_t irq_handler_count(void) { return handlers; }
void irq_diagnose(const char *phase, unsigned polls) { (void)phase; (void)polls; }
void pir_prepare_stage0(void) { assert(!prepared); prepared = 1; }
void pir_prepare_stage1(void) { assert(ready && decomposed); prepared = 2; }
int pir_check_stage0(void) { assert(stage == 0 && ready); return mode == 3; }
int pir_check_stage1(void) { assert(stage == 1 && ready && !opened); return mode == 9 || mode == 10; }
int pir_check_stage1_fixed_before_issue(void) { return 0; }
int pir_cpu_decompose(const volatile uint32_t *memory, uint32_t lines,
    const struct pir_cpu_output_limb *limbs, size_t count,
    const struct pir_cpu_parameters *parameters, uint32_t *plains, size_t words) {
  assert(memory == ddr && lines == STAGE0_WINDOW_LINES && limbs == stage0_cpu_limbs);
  assert(count == 16 && parameters == &pir_parameters && plains && words == 32U * 4096U);
  if (mode == 4) return -3;
  decomposed = 1; return 0;
}
int pir_cpu_encoder_init(struct pir_cpu_encoder *encoder,
    const struct pir_cpu_parameters *parameters) {
  assert(prepared == 2 && encoder && parameters == &pir_parameters); return 0;
}
int pir_cpu_encode(const uint32_t *plains, size_t words, volatile uint32_t *memory,
    uint32_t lines, const struct pir_cpu_input_limb *limbs, size_t count,
    const struct pir_cpu_parameters *parameters, struct pir_cpu_encoder *encoder) {
  assert(plains && words == 32U * 4096U && memory == ddr && lines == STAGE1_WINDOW_LINES);
  assert(limbs == stage1_cpu_limbs && count == 96 && parameters == &pir_parameters && encoder);
  if (mode == 5) return -4;
  encoded = 1; return 0;
}
int hpu_run_bfv_sealpir_2d_small_stage0_concentrated_000(void) {
  assert(stage == 0 && opened && prepared == 1); return 0;
}
int hpu_run_bfv_sealpir_2d_small_stage1_concentrated_000(void) {
  assert(stage == 1 && opened && prepared == 2 && encoded && !ready); return 0;
}
int main(int argc, char **argv) {
  assert(argc == 2); mode = atoi(argv[1]);
  int rc = pir_target_main();
  assert((mode == 0 ? rc == 0 : rc != 0) && !opened);
  if (mode >= 3 && mode <= 10 && mode != 6) assert(events >= 1);
  return 0;
}
'''


def main():
    with tempfile.TemporaryDirectory(prefix="pir-unified-control-") as temp:
        directory = Path(temp)
        (directory / "hpu").mkdir()
        (directory / "workload.h").write_text(HEADER)
        (directory / "hpu/irq.h").write_text(IRQ)
        (directory / "hpu/log.h").write_text("#define LOG_ERROR(...) ((void)0)\n")
        for stage in ("stage0", "stage1"):
            stem = f"bfv_sealpir_2d_small_{stage}_concentrated_000"
            (directory / (stem + ".h")).write_text(f"int hpu_run_{stem}(void);\n")
        (directory / "harness.c").write_text(HARNESS)
        common = ["gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                  "-I", str(directory), "-I", str(PIR)]
        subprocess.run(common + ["-Dmain=pir_target_main", "-c", str(MAIN),
                                 "-o", str(directory / "target.o")], check=True)
        subprocess.run(common + [str(directory / "harness.c"),
                                 str(directory / "target.o"), "-o", str(directory / "control")],
                       check=True)
        for scenario in range(11):
            subprocess.run([str(directory / "control"), str(scenario)], check=True)
    print("PIR_UNIFIED_CONTROL_PASS scenarios=11 (host stubs; not RTL)")


if __name__ == "__main__":
    main()
