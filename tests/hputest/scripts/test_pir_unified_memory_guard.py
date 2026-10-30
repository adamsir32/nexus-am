#!/usr/bin/env python3
"""Exercise the real PIR runtime's DDR checks with a tiny host memory image."""

from pathlib import Path
import os
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime/pir/pir_unified_runtime.c"

WORKLOAD = r'''
#ifndef AUDIT_WORKLOAD_H
#define AUDIT_WORKLOAD_H
#include <stddef.h>
#include <stdint.h>
#define LINE_WORDS 64U
#define LINE_BYTES 256U
#define STAGE0_IMAGE_LINES 1U
#define STAGE1_IMAGE_LINES 3U
#define STAGE0_OUTPUT_COUNT 1U
#define STAGE1_OUTPUT_COUNT 1U
#define PIR_CPU_INPUT_LIMBS 1U
#define PIR_CPU_DEGREE 64U
#define MEM_BASE ((uintptr_t)ddr)
#define CSR_STATUS 1U
#define CSR_IRQ 2U
#define CSR_FAULT 3U
#define PHASE_FAIL 7U
#define PHASE_DONE 6U
struct workload_progress {
  uint32_t phase, status, irq, fault, errors;
  uint32_t first_line, first_word, actual, expected, source_line;
};
struct output_span {
  unsigned line, words, golden_word, modulus, step, component, modulus_id;
};
struct pir_cpu_input_limb {
  uint32_t line, words, plaintext_index, modulus_id, modulus;
};
extern uint32_t ddr[STAGE1_IMAGE_LINES * LINE_WORDS];
extern volatile struct workload_progress workload_trace;
extern const uint32_t stage0_initial_image[STAGE0_IMAGE_LINES * LINE_WORDS];
extern const uint32_t stage1_initial_image[STAGE1_IMAGE_LINES * LINE_WORDS];
extern const uint32_t stage0_golden_words[1];
extern const uint32_t stage1_golden_words[1];
extern const uint8_t stage0_writable_lines[STAGE0_IMAGE_LINES];
extern const uint8_t stage1_writable_lines[STAGE1_IMAGE_LINES];
extern const uint8_t stage1_cpu_writable_lines[STAGE1_IMAGE_LINES];
extern const struct output_span stage0_outputs[STAGE0_OUTPUT_COUNT];
extern const struct output_span stage1_outputs[STAGE1_OUTPUT_COUNT];
extern const struct pir_cpu_input_limb stage1_cpu_limbs[PIR_CPU_INPUT_LIMBS];
volatile uint32_t *line_ptr(unsigned line);
uint32_t csr_read(uintptr_t address);
void mem_fence(void);
#endif
'''

HARNESS = r'''
#include <workload.h>
#include <pir_unified_runtime.h>
uint32_t ddr[STAGE1_IMAGE_LINES * LINE_WORDS];
const uint32_t stage0_initial_image[STAGE0_IMAGE_LINES * LINE_WORDS] = {0};
const uint32_t stage1_initial_image[STAGE1_IMAGE_LINES * LINE_WORDS] = {0};
const uint32_t stage0_golden_words[1] = {0};
const uint32_t stage1_golden_words[1] = {3};
const uint8_t stage0_writable_lines[STAGE0_IMAGE_LINES] = {1};
const uint8_t stage1_writable_lines[STAGE1_IMAGE_LINES] = {0, 0, 1};
const uint8_t stage1_cpu_writable_lines[STAGE1_IMAGE_LINES] = {0, 1, 1};
const struct output_span stage0_outputs[STAGE0_OUTPUT_COUNT] = {{0, 1, 0, 17, 0, 0, 0}};
const struct output_span stage1_outputs[STAGE1_OUTPUT_COUNT] = {{2, 1, 0, 17, 0, 0, 0}};
const struct pir_cpu_input_limb stage1_cpu_limbs[PIR_CPU_INPUT_LIMBS] = {{1, 64, 0, 0, 17}};
volatile uint32_t *line_ptr(unsigned line) { return ddr + line * LINE_WORDS; }
uint32_t csr_read(uintptr_t address) { (void)address; return 0; }
void mem_fence(void) { }

int main(void) {
  pir_prepare_stage1();
  ddr[LINE_WORDS] = 7; /* CPU encoded input, outside the initial image. */
  if (pir_check_stage1_fixed_before_issue() != 0) return 1;
  ddr[2 * LINE_WORDS] = 3; /* Correct HPU output. */
  if (pir_check_stage1() != 0) return 2;
  ddr[LINE_WORDS] ^= 1; /* HPU incorrectly changed a read-only input. */
  if (pir_check_stage1() == 0) return 3;
  ddr[LINE_WORDS] ^= 1;
  ddr[5] = 1; /* Existing fixed-image guard remains active. */
  if (pir_check_stage1() == 0) return 4;
  return 0;
}
'''


def test_memory_guard():
    with tempfile.TemporaryDirectory(prefix="pir-unified-guard-") as temporary:
        directory = Path(temporary)
        (directory / "hpu").mkdir()
        (directory / "workload.h").write_text(WORKLOAD, encoding="utf-8")
        (directory / "hpu/log.h").write_text(
            "#include <stdio.h>\n"
            "#define LOG_DEBUG(...) do { if (0) fprintf(stderr, __VA_ARGS__); } while (0)\n"
            "#define LOG_ERROR(...) do { if (0) fprintf(stderr, __VA_ARGS__); } while (0)\n"
            "#define LOG_EVENT(...) do { if (0) fprintf(stderr, __VA_ARGS__); } while (0)\n",
            encoding="utf-8")
        (directory / "harness.c").write_text(HARNESS, encoding="utf-8")
        binary = directory / ("guard.exe" if os.name == "nt" else "guard")
        compiled = subprocess.run([
            os.environ.get("CC", "gcc"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            "-DPIR_UNIFIED_HOST_TEST", "-I", str(directory),
            "-I", str(ROOT / "runtime/pir"), str(RUNTIME),
            str(directory / "harness.c"), "-o", str(binary),
        ], capture_output=True, text=True, check=False)
        assert compiled.returncode == 0, (
            f"host compiler rc={compiled.returncode}: {compiled.stdout}{compiled.stderr}")
        result = subprocess.run([str(binary)], check=False)
        assert result.returncode == 0, f"DDR guard scenario failed at step {result.returncode}"


if __name__ == "__main__":
    test_memory_guard()
    print("PIR_UNIFIED_MEMORY_GUARD_PASS (host DDR fault injection; not RTL)")
