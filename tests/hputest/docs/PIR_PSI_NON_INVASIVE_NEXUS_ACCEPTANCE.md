# Non-invasive PIR/PSI Nexus-AM acceptance

Branch `feature/pir-psi-non-invasive-refactor` starts at the prior audited Nexus-AM commit `13c1c4583fbaf5d10f975332d77db87596faaf7e`. This branch changes only this report. The corresponding producer source is `adamsir32/inline-asm` code commit `b78e1395a5a6da8d429492de1e3c9a5a5230367d`; its first acceptance report commit is `880a23785d2d3313cdd6428551ae2675e8c6c022`.

All builds and tests below ran on `zhaozhengyi@10.102.104.22:9322` in `/home/zhaozhengyi/independent-pir-psi-audit-20261026`, with a fresh target output directory `non-invasive-targets-b78`. Evidence is under `non-invasive-evidence/` and the producer report `doc/delivery/PIR_PSI_NON_INVASIVE_ACCEPTANCE.md`.

| Check | Result | Evidence |
|---|---|---|
| `08_01_psi_single` ELF/BIN and static checks | PASS | `08_01_psi_single-build.log` |
| `08_02_pir_stage0` ELF/BIN and static checks | PASS | `08_02_pir_stage0-build.log` |
| `08_03_pir_stage1` ELF/BIN and static checks | PASS | `08_03_pir_stage1-build.log` |
| `08_04_pir_unified` ELF/BIN and static checks | PASS | `08_04_pir_unified-build.log` |
| Unified target C host integration: real CPU decomposition/encoding, two HPU stages, dynamic-input and output fault rejection | PASS | `main-host-b78.log` |
| CPU encoded replay: 32 x 4096 decomposed coefficients, 96 x 4096 encoded values, two input cases | PASS | `cpu-clean-b78.log` and `cpu-clean-b78/summary.json` |
| Unified control negative tests | PASS 11 cases | `unified-control.log` |
| Python unit tests | PASS 181, skipped 2 | `nexus-unittests.log` |
| Default runtime static build | PASS 109 ELF/BIN cases | `default-109.log`, `non-invasive-default-109/hpu.zip` |
| RTL simulation and physical HPU execution | NOT RUN | Hardware is not available in this software acceptance |

Target ELF/BIN SHA-256 values are in `non-invasive-evidence/target-hashes.md` and the producer acceptance report. No original Nexus-AM source or script was modified in this round. Existing-file modifications inherited from the prior audit are inventoried in the producer `PIR_PSI_NON_INVASIVE_DIFF_AUDIT.md`.
