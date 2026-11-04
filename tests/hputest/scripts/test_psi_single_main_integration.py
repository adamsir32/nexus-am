#!/usr/bin/env python3
"""Run the real PSI target C main with a fresh encoded-instruction DDR image.

The HPU entry stub copies only writable lines from the producer's actual
instruction-model execution. This tests target CPU control and checks, not RTL.
"""

import argparse
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "src/08_pir_psi/08_01_psi_single.c"
NATIVE = ROOT / "runtime/native"

HARNESS = r'''
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <workload.h>
#include <hpu/irq.h>

static uint32_t ddr[IMAGE_LINES * LINE_WORDS];
static const char *executed_path;
static uint32_t registers[8], events, handlers;
static int opened, issued, prepared, mode;
int psi_target_main(void);

volatile uint32_t *test_line(unsigned line) {
    assert(line < IMAGE_LINES);
    return ddr + (size_t)line * LINE_WORDS;
}
uint64_t test_cycle(void) { return 0; }
uint32_t test_csr_read(uintptr_t address) {
    if (address == CSR_STATUS) return STATUS_VALID;
    assert(address >= CSR_BASE && address <= CSR_IRQ && (address - CSR_BASE) % 4U == 0);
    return registers[(address - CSR_BASE) / 4U];
}
void test_csr_write(uintptr_t address, uint32_t value) {
    assert(address >= CSR_BASE && address <= CSR_IRQ && (address - CSR_BASE) % 4U == 0);
    if (address == CSR_FAULT) { registers[(address - CSR_BASE) / 4U] = 0; return; }
    registers[(address - CSR_BASE) / 4U] = value;
}
int expect_csr(uintptr_t address, uint32_t expected) {
    return test_csr_read(address) != expected;
}
int clear_completion(void) { registers[(CSR_IRQ - CSR_BASE) / 4U] = 0; return 0; }
int wait_window(void) {
    return registers[(CSR_COMMIT - CSR_BASE) / 4U] != COMMIT ||
           registers[(CSR_SIZE_LO - CSR_BASE) / 4U] != WINDOW_LINES;
}
int wait_program(void) { return !opened || events != 1U; }
int irq_reset_events(void) { assert(!opened); events = handlers = 0; return 0; }
int irq_open(void) { assert(!opened); opened = 1; return 0; }
void irq_close(void) { opened = 0; }
uint32_t irq_event_count(void) { return events; }
uint32_t irq_handler_count(void) { return handlers; }
void irq_diagnose(const char *phase, unsigned polls) { (void)phase; (void)polls; }

int hpu_run_bfv_apsi_concentrated_application(void) {
    assert(opened && !issued && !events);
    assert(memcmp(ddr, initial_image, sizeof(ddr)) == 0);
    prepared = issued = 1;
    FILE *source = fopen(executed_path, "rb");
    assert(source);
    uint32_t *model = malloc((size_t)WINDOW_LINES * LINE_BYTES);
    assert(model);
    assert(fread(model, 1, (size_t)WINDOW_LINES * LINE_BYTES, source) ==
           (size_t)WINDOW_LINES * LINE_BYTES);
    assert(fgetc(source) == EOF && fclose(source) == 0);
    for (unsigned line = 0; line < WINDOW_LINES; ++line)
        if (writable_lines[line])
            memcpy(ddr + (size_t)line * LINE_WORDS,
                   model + (size_t)line * LINE_WORDS, LINE_BYTES);
    free(model);
    if (mode == 1) ddr[(size_t)outputs[0].line * LINE_WORDS] ^= 1U;
    if (mode == 2) {
        unsigned line = 0;
        while (line < WINDOW_LINES && writable_lines[line]) ++line;
        assert(line < WINDOW_LINES);
        ddr[(size_t)line * LINE_WORDS] ^= 1U;
    }
    if (mode != 3) { ++events; ++handlers; }
    return 0;
}

int main(int argc, char **argv) {
    assert(argc == 3);
    executed_path = argv[1];
    mode = atoi(argv[2]);
    const int result = psi_target_main();
    assert(prepared && issued && !opened);
    if (mode == 0) {
        assert(result == 0 && workload_trace.phase == PHASE_DONE);
        assert(events == 1 && handlers == 1 && workload_trace.errors == 0);
        puts("PSI_SINGLE_MAIN_HOST_PASS real target C + model DDR");
    } else {
        assert(result != 0 && workload_trace.phase == PHASE_FAIL);
        if (mode == 1) assert(workload_trace.first_line == outputs[0].line);
        if (mode == 3) assert(events == 0 && handlers == 0);
        puts("PSI_SINGLE_MAIN_HOST_FAULT_REJECTED");
    }
    return 0;
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--delivery", required=True, type=Path)
    parser.add_argument("--executed-image", required=True, type=Path)
    args = parser.parse_args()
    delivery = args.delivery.resolve(strict=True)
    executed = args.executed_image.resolve(strict=True)
    for name in ("layout.h", "layout.c", "image.u32.bin", "golden.u32.bin",
                 "writable.u8.bin"):
        if not (delivery / name).is_file():
            raise FileNotFoundError(delivery / name)
    with tempfile.TemporaryDirectory(prefix="psi-single-main-host-") as temp:
        directory = Path(temp)
        (directory / "hpu").mkdir()
        (directory / "hpu/log.h").write_text(
            "#include <stdio.h>\n"
            "#define LOG_ERROR(...) ((void)fprintf(stderr, __VA_ARGS__))\n"
            "#define LOG_EVENT(...) ((void)printf(__VA_ARGS__))\n"
            "#define LOG_DEBUG(...) do { if (0) fprintf(stderr, __VA_ARGS__); } while (0)\n",
            encoding="utf-8")
        (directory / "program.h").write_text(
            "int hpu_run_bfv_apsi_concentrated_application(void);\n", encoding="utf-8")
        (directory / "harness.c").write_text(HARNESS, encoding="utf-8")
        common = ["gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                  "-DWORKLOAD_HOST_TEST", "-I", str(directory),
                  "-I", str(delivery), "-I", str(ROOT / "include")]
        subprocess.run(common + ["-Dmain=psi_target_main", "-c", str(MAIN),
                                 "-o", str(directory / "main.o")], check=True)
        binary = directory / "integration"
        subprocess.run(common + [str(directory / "main.o"), str(NATIVE / "image.c"),
                                 str(NATIVE / "check.c"), str(NATIVE / "fixture.S"),
                                 str(delivery / "layout.c"), str(directory / "harness.c"),
                                 "-o", str(binary)], cwd=delivery, check=True)
        for mode in range(4):
            subprocess.run([str(binary), str(executed), str(mode)], check=True)


if __name__ == "__main__":
    main()
