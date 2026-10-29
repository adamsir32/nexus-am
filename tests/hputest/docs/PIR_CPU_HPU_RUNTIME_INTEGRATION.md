# PIR CPU/HPU runtime integration status

## Software-model handoff update (independent branch)

The `feature/pir-dynamic-stage-handoff` work adds `stage1_patch.py materialize`.
It accepts 96 newly encoded dynamic Q-limb files plus an allocation map,
retains the six fixed plaintext limbs from the package, creates a complete
SHA-256-bound patch manifest, and calls the existing `apply` validator. The
inline-asm software experiment loads the resulting image and executes the
original 26,700 stage1 encoded instructions with their original DMA spans.
For two legal database inputs sharing one encrypted second-dimension query,
all output ciphertext coefficients match a separately calculated SEAL result,
and the decrypted 1,024-byte records are correct. Real stage0 encoded-model
DDR export and CPU readback supply the dynamic plaintexts. The reproducible
test and hashes are documented in the producer branch's
`doc/delivery/PIR_DYNAMIC_STAGE_HANDOFF_REPORT.md`.

The sections below describe the **earlier fixed baseline** and its then-open
software gap; the new result closes that software-model gap. Target RTL and
bare-metal unified CPU orchestration remain untested.

## Current two-stage contract

The small PIR producer emits two independent BFV application packages at N=4096, input Q level 3. Stage0 has a fixed encrypted query and 16 Golden limbs representing every exported first-stage ciphertext component/modulus. Stage1 contains its own fixed decomposed plaintext input, 32 Golden reply limbs, and an independent HPU program. Each package has its own image, DMA relocation manifest, line allocation map, CSR window size and target ELF/BIN. The 08 target cases exercise each stage separately; stage1 PASS in a future RTL run would not by itself prove a dynamic stage0→stage1 handoff.

The intended runtime handoff is: run stage0; read all exported `step_*` component/modulus spans from the **executed** DDR image; convert HPU bit-reversed physical coefficients to the SEAL/Trident representation; perform the recursive ciphertext decomposition on CPU; encode the resulting plaintexts in each stage1 modulus and physical layout; patch only stage1 plaintext allocation spans; run stage1 with the unchanged HPU instruction program; compare the reply to an independently computed reference for that query. The first-stage output spans are located by `golden_manifest.csv` and `layout.c`, never by assumed consecutive addresses.

## What was implemented and tested

`stage1_patch.py` exports all 102 stage1 physical plaintext allocation spans from `line_map.csv` to a versioned manifest and binary files. On apply it requires exact allocation coverage/order, the source package SHA-256, each input file SHA-256, fixed length, canonical residues for the corresponding Q modulus, and no overwrite of the destination. It changes only those bytes in a copy of the initial HPU_MEM image. An identity snapshot/apply preserved the image hash. Changing one canonical input word produced a different image hash while the `.inst32` SHA-256 remained `d541de297369100e44c725468753d6148454b6e74cfa4979e582882056fe60e1`. A malformed coverage manifest was rejected. This demonstrates a stable address and instruction binding for raw physical input replacement; it does **not** establish numerical correctness for the changed input.

The existing producer can import a synthetic stage0 Golden readback, but that is an oracle proxy. Its public HPU software execution interface does not export an independently executed final memory image needed for the dynamic handoff. We did not present that synthetic readback as independent evidence. The CPU decomposition currently uses C++/SEAL and has not been ported to Nexus-AM bare metal; the exact physical encoding for newly decomposed plaintexts needs a reference check. A unified two-stage CPU main and software-model dynamic replay therefore remain **BLOCKED**. The two separate target mains and input patch validation are the completed pieces.

## Answers for the next RTL integration

| Question | Status |
| --- | --- |
| Stage0 independent target program | Built and statically checked; RTL execution NOT RUN |
| Stage1 independent target program | Built and statically checked; RTL execution NOT RUN |
| Same stage1 machine words for changed raw physical input | PASS for image preparation and unchanged `.inst32`; numerical replay NOT RUN |
| Stage0 executed memory readback | BLOCKED on a public final-memory export or actual RTL DDR readback |
| Bare-metal CPU ciphertext decomposition | NOT RUN; C++/SEAL dependency and physical representation need port and comparison |
| Unified CPU program controlling both stages | NOT IMPLEMENTED pending the above handoff and numerical reference |

Replacing correctly encoded stage1 physical input bytes does not intrinsically require recompiling its HPU instructions because the program and DMA spans use fixed addresses. The current high-level producer does recompile when given different decomposed inputs, and no independent dynamic numerical verification exists yet. A runtime API and reference test are required before claiming general no-recompile PIR execution.
