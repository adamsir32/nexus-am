# Trident PIR/PSI → Nexus-AM optional 08 integration

## Scope and fixed revisions

- Producer: `adamsir32/inline-asm` commit `22c08dcdf08b57fcb6505ff6b7942ffad5f42849`, configured from a clean worktree.
- Nexus-AM base: `631f9970003b27ca82eb13549c830c02bea78215` on independent branch `feature/trident-pir-psi-it`.
- Original inline-asm reference: `cfee951e4056660e521d55a3535d82335a49bb08`.
- No HPU arithmetic, ISA, producer compiler, Golden, or original 109-case default build path was changed. The 08 cases are invoked explicitly; `cases.tsv`, the default Makefile, and the pinned `producer.json` remain unchanged.

## Cases and target flow

| Case | Package | N / input Q level | HPU words | DMA spans | HPU_MEM lines | Golden limbs |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `08_01_psi_single` | `nexus-small-psi/hpu_query` | 8192 / 4 | 2891 | 1161 | 23025 | 8 |
| `08_02_pir_stage0` | `nexus-small-pir/stage0_concentrated_000` | 4096 / 3 | 17740 | 6434 | 30701 | 16 |
| `08_03_pir_stage1` | `nexus-small-pir/stage1_concentrated_000` | 4096 / 3 | 26700 | 9642 | 45549 | 32 |

The producer's `hpu_validate_package` first checks the original package. `import_package.py` then checks its exact producer revision, clean-at-configure provenance, ABI, NTT table contract, full instruction/DMA agreement, allocation boundaries, output order and modulus, and the target memory budget. The 08 identity mapping accepts only these three application stems and parameter sets. The import keeps the original HPU program and initial HPU_MEM data. It poisons write-first Golden output spans and adds 64 guard lines. It produces `layout.h/c`, initial image, Golden and writable masks. The same target build and `verify_elf` routines used by existing native cases create ELF/BIN and compare every embedded HPU machine word with `.inst32` in order.

Each separate C entry in `src/08_pir_psi` uses the Nexus CSR window, source-257 interrupt, HPU program call, Golden comparison, and read-only/guard check. A PASS is possible only after a real completion interrupt and actual DDR readback. None of these target programs was run against HPU RTL or hardware in this phase.

## Reproduce on the server

Run from the Nexus-AM checkout. Substitute absolute paths if the checkout differs:

```sh
PRODUCER=../trident-alignment-20261026
OUTPUT=../nexus-pir-psi-output
VALIDATOR="$PRODUCER/build/hpu_validate_package"
CROSS=/opt/riscv/bin/riscv64-unknown-elf-
python3 tests/hputest/scripts/build-pir-psi.py --case 08_01_psi_single --package "$PRODUCER/nexus-small-psi/hpu_query" --package-validator "$VALIDATOR" --output "$OUTPUT" --am-home . --cross "$CROSS"
python3 tests/hputest/scripts/build-pir-psi.py --case 08_02_pir_stage0 --package "$PRODUCER/nexus-small-pir/stage0_concentrated_000" --package-validator "$VALIDATOR" --output "$OUTPUT" --am-home . --cross "$CROSS"
python3 tests/hputest/scripts/build-pir-psi.py --case 08_03_pir_stage1 --package "$PRODUCER/nexus-small-pir/stage1_concentrated_000" --package-validator "$VALIDATOR" --output "$OUTPUT" --am-home . --cross "$CROSS"
```

Outputs are under `$OUTPUT/artifact/normal/<case>/` and imported data under `$OUTPUT/imported/<case>/`. An existing imported delivery is accepted only with `--verify-existing`, which byte-checks each imported file before building. Receipts record source and artifact SHA-256 values. The build script is optional and has no effect on the existing catalog.

## Capacity and next integration step

The three small images are 5,894,400, 7,859,456, and 11,660,544 bytes. Each imported image also has a 16,384-byte guard. The Nexus native workload budget is strictly below `0x07000000` bytes, and the ELF PT_LOAD segments must end before `0x87000000` to avoid the HPU workload DDR. These are checked during import/build.

The prior 17 formal PSI packages are independent partitions. Their largest single image is 94,580,992 bytes (90.2 MiB); `5,980,417` lines is their **aggregate**, not one package. The largest image fits the 112 MiB nominal 06 workload budget in isolation, but code/data embedding overhead, distinct package identities, scheduler, and RTL capacity remain unverified. Formal PIR stage0/stage1 images are 516,261,120 and 169,575,680 bytes, above this 112 MiB budget. Existing formal packages have `dirty-at-configure` provenance and are audit references only. No formal ELF is claimed here.

For multi-package PSI, the CPU should load one partition, run its HPU program, check its own Golden and guards, decode that partition's matching slots, then union, sort and deduplicate the decoded identifiers. Partitions have independent initial images and output manifests; no cross-partition ciphertext state should be inferred without an explicit manifest. The scheduler must report partition, operation and allocation on failure. This is a design; no multi-package target run was performed.
