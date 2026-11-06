# PIR/PSI Small acceptance on Nexus-AM

Tested source commits: inline-asm `de9fdfbbdb092933ed4f315da8094a0fb68a2546` and Nexus-AM `688a16b442f051ce9ff00e34a4f21443a9e3aa9b`. The coordinated runner is `tests/hputest/scripts/run-pir-psi-small-acceptance.py`. It requires the exact full commit IDs and clean worktrees, then builds in a new directory and stops on any required failure.

Server evidence: `/home/zhaozhengyi/independent-pir-psi-audit-20261026/small-acceptance-run-de9f-688a/summary.json`; logs and 910-file `checksums.sha256` are beside it. The complete report is in the producer repository at `doc/delivery/PIR_PSI_SMALL_ACCEPTANCE_REPORT.md`.

The fresh run passed 22/22 producer CTest, PIR two-input software replay, four PSI Small scenarios, seven application package validations, all four target ELF/BIN builds, CPU encoded replay, PIR target C host integration and PSI target C host integration. The PSI host test runs the existing `08_01_psi_single.c` and native image/check code against DDR produced by the actual encoded instruction executor. It rejects output corruption, read-only memory corruption and missing completion. Final PSI decryption and intersection recovery run in the producer/client application.

Target-level simulation, RTL and physical HPU execution: **NOT RUN**.

## Audit-fixes parameter clarification (2026-11-05)

This historical report records the Small acceptance baseline. The follow-up
`feature/pir-psi-audit-fixes` work uses the same dimensions. PIR has N=4096,
128 real records of 1024 bytes, 9 records per plaintext, 15 populated
plaintexts plus one zero padding plaintext in a 4 x 4 matrix (16 total).
Stage 0 has 17,740 HPU instructions; Stage 1 has 26,700. The 32 CPU
decomposition plaintexts become 96 three-modulus physical inputs.

PSI Small has N=8192, 10 real Sender items and 5 real Receiver items in
each of empty/single/multi/boundary. The real intersections have 0/1/2/2
items respectively. Kuku has 4096 buckets; one HPU package covers a
contiguous 1024-bucket window. The fixed source config sets
`max_items_per_bin=16`; the independent PDF's value of 2 is inconsistent
with the checked source. These counts describe effective sets, not any
synthetic padding or formal-scale dataset. Target multi-window scheduling
(F-04) and generalized PIR CPU parameters (F-05) remain outside Small scope.
