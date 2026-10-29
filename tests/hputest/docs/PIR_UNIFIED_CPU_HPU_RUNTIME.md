# Single-ELF PIR CPU/HPU runtime

## Components and linkage

`08_04_pir_unified.c` is the only CPU `main()`. It links the two original
generated `hpu_run_bfv_sealpir_2d_small_{stage0,stage1}_concentrated_000()`
functions, target C decomposition and encoding, `runtime/native/wait.c`, the
existing source-257 interrupt driver, and a namespaced two-stage fixture.
The HPU programs remain separate; no target compiler or graph rebuild runs.
`build-pir-psi.py --case 08_04_pir_unified` invokes the established package
validator and `import_package()` separately for both packages. The generated
`layout.h/c` supplies read-only stage-specific output, input, and parameter
tables. `fixture.S` embeds both poisoned initial images, both Golden arrays,
and both writable masks under distinct symbols. This avoids the generic
single-package `initial_image`/`outputs` name collision.

## Exact control sequence

1. Copy stage0 initial image to DDR `0x87000000`; clean its cache lines.
2. Clear HPU fault/completion, configure base and 30,701-line window, read
   back CSR values, commit, and wait until the window becomes valid.
3. Reset interrupt counters, initialize and open PLIC source 257 once, then
   issue the existing 17,740 stage0 HPU instructions.
4. Wait for the actual ISR completion and idle status; require one successful
   event, one handler invocation, cleared IRQ level, and no fault. The ISR
   clears HPU completion and completes the PLIC claim.
5. Invalidate stage0 DDR cache lines. Compare all 16 output limbs with Golden,
   and compare all nonwritable lines, gaps, and 64 outer guard lines with the
   initial image. Decompose **the actual DDR output pointers** to the static
   32×4096 plaintext buffer. Golden is used only for independent validation.
6. Copy the stage1 initial image into the same DDR base after decomposition.
   Initialize the static NTT encoder and overwrite exactly 96 dynamic input
   limbs. Check that every other stage1 byte remains at its initial value;
   clean all stage1 cache lines.
7. Clear fault/completion, configure and commit the 45,549-line stage1
   window. `irq_rearm()` checks the first ISR's completion, cleared level,
   idle status, valid window, and no fault, then arms the second round without
   rerunning one-time CTE initialization. Require cumulative counters still
   at one before issuing the original 26,700 stage1 HPU instructions.
8. Wait for a second ISR completion and idle status; require two events and
   two handler calls. Close interrupts. Invalidate DDR and check 32 final
   output limbs plus all nonwritable/non-dynamic lines and guards against
   independent Golden and initial data. Report PASS only after these checks.

The target's `wait_program()` rejects a fault or timeout and cannot treat an
MMIO level alone as a completed interrupt. Failures close the interrupt
channel, preserve phase/CSR/line diagnostics, and return a nonzero status.
This sequence is linked and statically checked; actual target execution
awaits RTL/SoC support for the custom HPU instructions and interrupt path.

## Memory and capacity

The two HPU programs reuse one DDR window. The maximum active HPU window is
45,549×256 = 11,660,544 bytes, plus 64×256 = 16,384 guard bytes (45,613
lines total). It is **not** the sum of the two windows. Both stage images and
Golden arrays are present in the CPU ELF; the final ELF is 21,526,016 bytes,
the raw BIN is 21,586,472 bytes, and `.bss` is 852,536 bytes. `.bss` includes
the 524,288-byte plaintext buffer and encoder tables/scratch. The sole LOAD
segment occupies `0x80000000..0x81496228`, below DDR `0x87000000`; the
build verifies every PT_LOAD against that boundary. The package receiver
checks the 256 MiB memory contract. No large stack allocation or heap
allocation is made by the new CPU algorithms.

The generated stage0 and stage1 HPU code uses its own package DMA addresses
relative to the configured DDR base. `verify_elf()` independently extracts
each function's custom instruction words from the linked ELF and requires
exact equality and order against its validated `.inst32`; package import
validates each DMA relocation manifest against those words and the package
line map. The final counts are stage0 17,740 instructions/6,434 DMA and
stage1 26,700 instructions/9,642 DMA.

This ELF embeds the baseline database image and its stage-specific Golden.
The changed-database seed is validated in the separate host software handoff
test using the same CPU C modules and fixed stage1 HPU instructions. The
target ELF is not a general database-loading or arbitrary-query service.

## Hardware handoff conditions

The target ELF/BIN has not run on RTL. Hardware integration needs a platform
that implements the custom1/custom2 HPU instructions, CSR base
`0x08000000`, DDR base `0x87000000` with at least 45,613 accessible lines,
cache clean/invalidate operations, PLIC source 257 in S-mode context 1, and
two independent PSYNC completion interrupts with W1C clearing. An RTL run
must confirm the two window commits, DMA behavior, IRQ rearm, and final
Golden/guard checks using this **single** target executable.
