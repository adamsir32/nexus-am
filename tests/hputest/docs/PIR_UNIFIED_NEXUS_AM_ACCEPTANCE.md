# Unified PIR Nexus-AM acceptance, 2026-10-29

## Fixed versions and evidence root

- Work branches in both repositories: `feature/pir-unified-cpu-hpu-runtime`.
- inline-asm base `f2093a88dcea1d0e12358b3816200990f4a298a9`; code commit
  `95a46c7f8934aa778f47f7b95d5f151e2007482d`.
- Nexus-AM base `ce1d4ffd48f4c14d55aca008c845ac4c6a8a43c3`; code commit
  `533ea4f1adad1df40fea0386fc5b420b24a6ed10`.
- Server evidence root `$A=/home/zhaozhengyi/independent-pir-psi-audit-20261026`;
  producer checkout `$P=$A/trident-alignment-20261026/repo`, build
  `$A/trident-alignment-20261026/build`; Nexus checkout `$N=$A/nexus-am-pir-psi`.
  Fresh two-input fixture is `$A/trident-alignment-20261026/pir-unified-fixture`.
  Generated artifacts and import receipt are in `$A/pir-unified-target-build`.
  No RTL/SoC run has been performed.

## Acceptance matrix

| Requirement | Result | Evidence |
| --- | --- | --- |
| One RV64 ELF/BIN with one CPU main, two HPU entries | **PASS — build/static** | `$A/pir-unified-target-build/artifact/normal/08_04_pir_unified/08_04_pir_unified.{elf,bin}`; `receipt.json` |
| Exact stage0/stage1 HPU words and order | **PASS — static** | 17,740 and 26,700 custom words extracted independently from the ELF and exactly compared with each package `.inst32` |
| DMA and memory binding | **PASS — static** | Package receiver validates 6,434/9,642 DMA rows against each encoded program and line map; maximum active window 45,549 lines; LOAD ends at `0x81496228`, below DDR `0x87000000` |
| Target-compilable CPU decomposition | **PASS — build/host** | Same C module linked in ELF and host test; 32×4096 coefficients per input equal same-run C++/SEAL |
| Target-compilable physical encoder | **PASS — build/host** | Same C module linked in ELF and host test; 96×4096 physical words per input equal compiler output; fixed regions unchanged |
| Live stage0 output to stage1 input data flow | **PASS — software** | C test reads two genuine encoded-instruction stage0 execution images, not Golden; CPU-patched image hashes match previous dynamic replay |
| Second-stage numerical execution | **PASS — software model** | Both C-patched images execute the *same* 26,700 instruction/9,642 DMA program; all 2,915,136 final words per input equal independently SEAL-checked execution image; record oracle passed in handoff acceptance |
| Two distinct HPU calls, CSR configuration, ISR rounds | **PASS — linked source/host control** | One `main()`, `irq_open()` once, `irq_rearm()` between calls, cumulative event/handler counts 1 then 2; 11 host control scenarios passed |
| First/second faults, timeouts, corrupt output, bounds, final mismatch/guard | **PASS — simulated/host checks** | Six CPU invalid-input cases, eight package corruption cases, and 11 host control scenarios; these do not establish hardware fault behavior |
| Real unified ELF execution on RTL/SoC | **NOT RUN** | Compatible HPU RTL/SoC execution environment unavailable |
| Complete default 109-case Nexus-AM target build matrix | **NOT RUN** | Three relevant legacy application builds and selected unit tests were run; this does not stand in for the full matrix |

No requirement above is recorded as hardware PASS. The software result is
about the actual target C algorithm sources and the encoded HPU instruction
model; the target ELF has only been built and statically checked.
The embedded target images and Golden are for the baseline database. The
changed-database test exercises the same CPU C modules and fixed stage1 HPU
instructions in host software; it does not turn this ELF into an arbitrary
database or query loader.

## Reproduction commands and exits

The commands below ran on the server. Paths are given through `$A`, `$P`, and
`$N` above. All listed commands returned **0** unless otherwise stated.

1. From `$P`, generate baseline and changed database fixtures with
   `../build/hpu_bfv_sealpir_2d_concentrated_example --profile small
   --record-index 8 --stage0-executed-image
   ../pir-unified-fixture/stage0-executed.u32.bin --emit-dir
   ../pir-unified-fixture/packages --dynamic-replay-dir
   ../pir-unified-fixture/replay --stage1-patch-script
   ../../nexus-am-pir-psi/tests/hputest/scripts/stage1_patch.py`.
   Log: `$A/trident-alignment-20261026/pir-unified-fixture/run.log`.
   It reports two `AUDIT_STAGE1_REPLAY_PASS` and
   `AUDIT_DYNAMIC_TWO_INPUTS_PASS`.
2. From `$N`, run
   `python3 tests/hputest/scripts/test_pir_cpu_algorithms.py --fixture
   ../trident-alignment-20261026/pir-unified-fixture --output
   ../pir-unified-cpu-replay-final --replay-executable
   ../trident-alignment-20261026/build/pir_cpu_encoded_replay`.
   Log and machine result: `$A/pir-unified-cpu-replay-final.log` and
   `$A/pir-unified-cpu-replay-final/summary.json`. Both model replay logs
   report `PIR_CPU_ENCODED_REPLAY_PASS`.
3. From `$N`, run `python3 tests/hputest/scripts/test_pir_unified_control.py`.
   Log: `$A/pir-unified-control-test.log`;
   `PIR_UNIFIED_CONTROL_PASS scenarios=11 (host stubs; not RTL)`.
4. From `$N`, run `python3 tests/hputest/scripts/build-pir-psi.py --case
   08_04_pir_unified --stage0-package
   ../trident-alignment-20261026/pir-unified-fixture/packages/stage0_concentrated_000
   --stage1-package
   ../trident-alignment-20261026/pir-unified-fixture/packages/stage1_concentrated_000
   --cpu-parameters
   ../trident-alignment-20261026/pir-unified-fixture/replay/cpu-fixture/parameters.json
   --dynamic-input-map
   ../trident-alignment-20261026/pir-unified-fixture/replay/baseline/dynamic/dynamic_inputs.tsv
   --package-validator ../trident-alignment-20261026/build/hpu_validate_package
   --output ../pir-unified-target-build --am-home .
   --cross /opt/riscv/bin/riscv64-unknown-elf- --verify-existing`.
   Log: `$A/pir-unified-target-final.log`; receipt in artifact directory.
   The `--verify-existing` replay byte-checks both prior imported packages.
5. From `$A/trident-alignment-20261026/build`, run
   `ctest --output-on-failure -R
   'hpu_bfv_sealpir_2d_concentrated_small_record_(0|8|9|64|127)$|bfv_sealpir_2d_concentrated_small_delivery_test$|hpu_bfv_sealpir_stage0_readback_adapter$|hpu_bfv_apsi_concentrated_small_(empty|single|multi|boundary)$|bfv_apsi_concentrated_small_delivery_test$|hpu_bfv_apsi_trident_small_(multi|truncation|cross_felt)$|hpu_bfv_apsi_trident_native_cross_felt$|hpu_bfv_apsi_trident_duplicate_input$|hpu_bfv_apsi_senderdb_driver_failures$'`.
   `$A/trident-alignment-20261026/pir-unified-producer-regression.log`:
   **18/18 PASS**.
6. From `$A/trident-alignment-20261026/build`, run
   `python3 ../repo/test/pir_dynamic_stage_handoff_test.py --example
   ./hpu_bfv_sealpir_2d_concentrated_example --stage1-patch-script
   ../../nexus-am-pir-psi/tests/hputest/scripts/stage1_patch.py --output
   ../pir-unified-prior-handoff`.
   `$A/trident-alignment-20261026/pir-unified-prior-handoff.log` and
   `pir-unified-prior-handoff/handoff_summary.json`: **PASS**, two-input
   replay, 16 stage0 output limbs, 96 dynamic limbs, 5,200,636 changed
   nonoutput stage0 bytes.
7. From `$N`, build each of `08_01_psi_single`, `08_02_pir_stage0`, and
   `08_03_pir_stage1` with the existing `build-pir-psi.py --case ...
   --package ... --package-validator ... --output
   ../pir-unified-regression-build --am-home .
   --cross /opt/riscv/bin/riscv64-unknown-elf-` command.
   Logs `$A/pir-unified-regression-08_*.log`: **three RC=0**.
8. From `$N`, run `test_runtime_list.py`, `test_am_cte_init.py`,
   `test_receiver.py`, `test_build_isolation.py`, and
   `test_psync_irq_regression.py` under `tests/hputest/scripts/`.
   Logs `$A/pir-unified-unit-*.log`: **22 tests, 21 PASS, 1 skipped**.
   Also run `test-pir-psi-negative.py` with the prior PSI and PIR stage1
   packages and `hpu_validate_package`; its eight corruption cases all
   rejected (`$A/pir-unified-package-negative.log`). A wrong primitive psi
   root was separately rejected against the package's 128-word pre-twist
   table during layout generation.

## Artifact identity and target memory

| Item | Value |
| --- | --- |
| ELF SHA-256 | `c258d6a88637baed936e4c93c2461885988b227b40558a32135586cc84eb8e90` |
| BIN SHA-256 | `05d7b594790209a3d17b00c3ae31c7d2c5bc923608257717b3fce9689d82c531` |
| ELF/BIN bytes | 21,526,016 / 21,586,472 |
| ELF `.bss` | 852,536 bytes |
| PT_LOAD physical range | `0x80000000..0x81496228` |
| Stage0/1 HPU window | 30,701 / 45,549 lines |
| Guarded maximum | 45,613 lines = 11,676,928 bytes |
| Stage0/1 instructions | 17,740 / 26,700 |
| Stage0/1 DMA entries | 6,434 / 9,642 |

## Remaining RTL handoff

Load the **single** `08_04_pir_unified.elf` or `.bin` into an RV64 Nexus-AM
platform with custom HPU opcodes, CSR base `0x08000000`, DDR base
`0x87000000`, cache maintenance, and PLIC source 257 in S-mode context 1.
Trace both window commits, DMA access, two W1C-cleared PSYNC interrupts,
event/handler counters, CPU dynamic writes, and final Golden/guard checks.
Until that run is observed, target execution and real interrupt/fault behavior
remain **NOT RUN**.
