#!/usr/bin/env python3
"""Run the real unified C main with real CPU code and model-produced DDR images.

The HPU entry stubs load prerecorded instruction-model memory. This checks the
combined CPU/control/runtime data flow; it is not RTL or target execution.
"""

import argparse
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
PIR = ROOT / "runtime/pir"
MAIN = ROOT / "src/08_pir_psi/08_04_pir_unified.c"

WORKLOAD = r'''
#ifndef PIR_HOST_WORKLOAD_H
#define PIR_HOST_WORKLOAD_H
#include <stdint.h>
#include <stddef.h>
#include <layout.h>
#define LINE_WORDS 64U
#define LINE_BYTES 256U
extern uint32_t ddr[STAGE1_IMAGE_LINES * LINE_WORDS];
#define MEM_BASE ((uintptr_t)ddr)
#define PHASE_PREPARE 1U
#define PHASE_CONFIGURE 2U
#define PHASE_ISSUE 3U
#define PHASE_WAIT 4U
#define PHASE_COMPARE 5U
#define PHASE_DONE 6U
#define PHASE_FAIL 7U
#define CSR_BASE_LO 0U
#define CSR_BASE_HI 4U
#define CSR_SIZE_LO 8U
#define CSR_SIZE_HI 12U
#define CSR_COMMIT 16U
#define CSR_STATUS 20U
#define CSR_FAULT 24U
#define CSR_IRQ 28U
#define STATUS_VALID 1U
#define STATUS_BUSY 2U
#define STATUS_FAULT 4U
#define FAULT_VALID 1U
#define IRQ_LEVEL 1U
#define COMMIT 1U
struct workload_progress {
  uint32_t phase, status, irq, fault, errors;
  uint32_t first_line, first_word, actual, expected;
  uint64_t wait_cycles, cycle_start, cycle_end;
  uint32_t source_line;
};
extern volatile struct workload_progress workload_trace;
volatile uint32_t *line_ptr(unsigned line);
void mem_fence(void);
uint32_t csr_read(uintptr_t address);
void csr_write(uintptr_t address, uint32_t value);
int expect_csr(uintptr_t address, uint32_t expected);
int clear_completion(void);
int wait_window(void);
int wait_program(void);
void clean_lines(unsigned lines);
void invalidate_lines(unsigned lines);
void phase_mark(unsigned phase);
int case_fail_at(const char *source, unsigned line);
int case_pass(void);
#endif
'''

HARNESS = r'''
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <workload.h>
#include <hpu/irq.h>
#include <pir_unified_runtime.h>

uint32_t ddr[STAGE1_IMAGE_LINES * LINE_WORDS];
static const char *stage0_file, *stage1_patched, *stage1_executed;
static uint32_t csr[8], events, handlers;
static int opened, stage, input_checked, fault_mode;
int pir_target_main(void);

volatile uint32_t *line_ptr(unsigned line) {
  assert(line < STAGE1_IMAGE_LINES);
  return ddr + (size_t)line * LINE_WORDS;
}
void mem_fence(void) { }
uint32_t csr_read(uintptr_t address) {
  if (address == CSR_STATUS) return STATUS_VALID;
  assert(address <= CSR_IRQ && address % 4U == 0U);
  return csr[address / 4U];
}
void csr_write(uintptr_t address, uint32_t value) {
  assert(address <= CSR_IRQ && address % 4U == 0U);
  if (address == CSR_FAULT) { csr[address / 4U] = 0U; return; }
  csr[address / 4U] = value;
  if (address == CSR_SIZE_LO) stage = value == STAGE1_WINDOW_LINES ? 1 : 0;
}
int expect_csr(uintptr_t address, uint32_t expected) {
  return csr_read(address) != expected;
}
int clear_completion(void) { csr[CSR_IRQ / 4U] = 0U; return 0; }
int wait_window(void) { return csr[CSR_COMMIT / 4U] != COMMIT; }
int irq_reset_events(void) { assert(!opened); events = handlers = 0; return 0; }
int irq_open(void) { assert(!opened && stage == 0); opened = 1; return 0; }
int irq_rearm(void) { return !(opened && stage == 1 && events == 1 && handlers == 1); }
void irq_close(void) { opened = 0; }
uint32_t irq_event_count(void) { return events; }
uint32_t irq_handler_count(void) { return handlers; }
void irq_diagnose(const char *name, unsigned polls) { (void)name; (void)polls; }
int wait_program(void) { return !opened || events != (unsigned)(stage + 1); }

static void load_exact(const char *path, void *target, size_t bytes) {
  FILE *stream = fopen(path, "rb");
  assert(stream);
  assert(fread(target, 1, bytes, stream) == bytes);
  assert(fgetc(stream) == EOF);
  assert(fclose(stream) == 0);
}
static void load_model_writes(const char *path, unsigned lines,
                              const uint8_t *writable) {
  const size_t bytes = (size_t)lines * LINE_BYTES;
  uint32_t *executed = malloc(bytes);
  assert(executed);
  load_exact(path, executed, bytes);
  for (unsigned line = 0; line < lines; ++line)
    if (writable[line])
      memcpy(ddr + (size_t)line * LINE_WORDS,
             executed + (size_t)line * LINE_WORDS, LINE_BYTES);
  free(executed);
}
int hpu_run_bfv_sealpir_2d_small_stage0_concentrated_000(void) {
  assert(opened && stage == 0 && events == 0);
  load_model_writes(stage0_file, STAGE0_WINDOW_LINES, stage0_writable_lines);
  ++events; ++handlers;
  return 0;
}
int hpu_run_bfv_sealpir_2d_small_stage1_concentrated_000(void) {
  const size_t bytes = (size_t)STAGE1_WINDOW_LINES * LINE_BYTES;
  assert(opened && stage == 1 && events == 1);
  void *expected = malloc(bytes);
  assert(expected);
  load_exact(stage1_patched, expected, bytes);
  for (unsigned limb = 0; limb < PIR_CPU_INPUT_LIMBS; ++limb) {
    const unsigned first = stage1_cpu_limbs[limb].line * LINE_WORDS;
    const uint32_t *reference = expected;
    for (unsigned word = 0; word < PIR_CPU_DEGREE; ++word)
      if (ddr[first + word] != reference[first + word]) {
        fprintf(stderr, "CPU stage1 input differs from model at limb=%u word=%u "
                "actual=%u expected=%u\n", limb, word,
                ddr[first + word], reference[first + word]);
        free(expected);
        return 1;
      }
  }
  free(expected);
  input_checked = 1;
  load_model_writes(stage1_executed, STAGE1_WINDOW_LINES, stage1_writable_lines);
  if (fault_mode == 1) ddr[(size_t)stage1_cpu_limbs[0].line * LINE_WORDS] ^= 1U;
  if (fault_mode == 2) ddr[(size_t)stage1_outputs[0].line * LINE_WORDS] ^= 1U;
  ++events; ++handlers;
  return 0;
}

int main(int argc, char **argv) {
  assert(argc == 5);
  stage0_file = argv[1]; stage1_patched = argv[2]; stage1_executed = argv[3];
  fault_mode = atoi(argv[4]);
  const int result = pir_target_main();
  assert(!opened && input_checked && events == 2 && handlers == 2);
  if (!fault_mode) {
    assert(result == 0 && workload_trace.phase == PHASE_DONE);
    puts("PIR_UNIFIED_MAIN_HOST_PASS real CPU + runtime + prerecorded HPU model DDR");
  } else if (fault_mode == 1) {
    assert(result != 0 && workload_trace.phase == PHASE_FAIL);
    assert(workload_trace.first_line == stage1_cpu_limbs[0].line);
    puts("PIR_UNIFIED_MAIN_HOST_FAULT_REJECTED dynamic input write");
  } else {
    assert(result != 0 && workload_trace.phase == PHASE_FAIL);
    assert(workload_trace.first_line == stage1_outputs[0].line);
    puts("PIR_UNIFIED_MAIN_HOST_FAULT_REJECTED output corruption");
  }
  return 0;
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--delivery", required=True, type=Path)
    parser.add_argument("--fixture", required=True, type=Path)
    args = parser.parse_args()
    delivery = args.delivery.resolve()
    fixture = args.fixture.resolve()
    for path in (delivery / "layout.h", delivery / "layout.c",
                 fixture / "stage0-executed.u32.bin",
                 fixture / "replay/baseline/stage1-patched.u32.bin",
                 fixture / "replay/baseline/stage1-executed.u32.bin"):
        if not path.is_file():
            raise FileNotFoundError(path)
    with tempfile.TemporaryDirectory(prefix="pir-unified-main-host-") as temporary:
        directory = Path(temporary)
        (directory / "hpu").mkdir()
        (directory / "workload.h").write_text(WORKLOAD, encoding="utf-8")
        (directory / "hpu/log.h").write_text(
            "#include <stdio.h>\n"
            "#define LOG_ERROR(...) ((void)fprintf(stderr, __VA_ARGS__))\n"
            "#define LOG_EVENT(...) ((void)printf(__VA_ARGS__))\n"
            "#define LOG_DEBUG(...) do { if (0) fprintf(stderr, __VA_ARGS__); } while (0)\n",
            encoding="utf-8")
        (directory / "harness.c").write_text(HARNESS, encoding="utf-8")
        common = ["gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                  "-DPIR_UNIFIED_HOST_TEST", "-I", str(directory),
                  "-I", str(delivery), "-I", str(delivery / "stage0"),
                  "-I", str(delivery / "stage1"), "-I", str(PIR),
                  "-I", str(ROOT / "include")]
        subprocess.run(common + ["-Dmain=pir_target_main", "-c", str(MAIN),
                                 "-o", str(directory / "main.o")], check=True)
        binary = directory / "integration"
        subprocess.run(common + [str(directory / "main.o"),
                                 str(PIR / "pir_unified_runtime.c"),
                                 str(PIR / "pir_cpu_decompose.c"),
                                 str(PIR / "pir_cpu_encode.c"),
                                 str(delivery / "layout.c"),
                                 str(PIR / "fixture.S"),
                                 str(directory / "harness.c"), "-o", str(binary)],
                       cwd=delivery, check=True)
        paths = [str(binary), str(fixture / "stage0-executed.u32.bin"),
                 str(fixture / "replay/baseline/stage1-patched.u32.bin"),
                 str(fixture / "replay/baseline/stage1-executed.u32.bin")]
        for mode in (0, 1, 2):
            subprocess.run(paths + [str(mode)], check=True)


if __name__ == "__main__":
    main()
