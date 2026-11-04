# PIR/PSI Small acceptance on Nexus-AM

Tested source commits: inline-asm `de9fdfbbdb092933ed4f315da8094a0fb68a2546` and Nexus-AM `688a16b442f051ce9ff00e34a4f21443a9e3aa9b`. The coordinated runner is `tests/hputest/scripts/run-pir-psi-small-acceptance.py`. It requires the exact full commit IDs and clean worktrees, then builds in a new directory and stops on any required failure.

Server evidence: `/home/zhaozhengyi/independent-pir-psi-audit-20261026/small-acceptance-run-de9f-688a/summary.json`; logs and 910-file `checksums.sha256` are beside it. The complete report is in the producer repository at `doc/delivery/PIR_PSI_SMALL_ACCEPTANCE_REPORT.md`.

The fresh run passed 22/22 producer CTest, PIR two-input software replay, four PSI Small scenarios, seven application package validations, all four target ELF/BIN builds, CPU encoded replay, PIR target C host integration and PSI target C host integration. The PSI host test runs the existing `08_01_psi_single.c` and native image/check code against DDR produced by the actual encoded instruction executor. It rejects output corruption, read-only memory corruption and missing completion. Final PSI decryption and intersection recovery run in the producer/client application.

Target-level simulation, RTL and physical HPU execution: **NOT RUN**.
