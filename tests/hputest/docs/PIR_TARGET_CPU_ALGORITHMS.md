# PIR target CPU decomposition and physical input encoding

## Source contract

The target implementation is `runtime/pir/pir_cpu_decompose.c` and
`runtime/pir/pir_cpu_encode.c`. Both are C11, use fixed caller-owned storage,
and build for the Nexus-AM RV64 target. They implement the small fixed-query
package only: polynomial degree 4096, 20-bit decomposition chunks, two stage0
output Q limbs, and three stage1 input Q limbs. They do not link SEAL or run a
compiler on the target.

The C++ oracle is `examples/bfv_sealpir_2d_application.cpp`:
`import_stage0_readback()`, `decompose_to_plaintexts()`, and the call to
`bfv_multiply_plaintext_to_hpu()`. The application exports same-run plaintext
coefficients and NTT parameters under `replay/cpu-fixture/`; this is a test
fixture, not a target runtime input. The target consumes its stage0 DDR
window and generated package layout table.

## Stage0 output to 32 plaintexts

The receiver validates all 16 physical output limbs and their Golden files.
Each limb is 4096 little-endian u32 words; each word must be below its declared
Q modulus. The target indexes the table by reply (0–3), ciphertext component
(0–1), and Q limb (0–1), with no duplicate or missing tuple. Physical word
index `p` corresponds to natural coefficient `bit_reverse_12(p)`. A natural
coefficient `v` produces chunks `v & ((1<<20)-1)` and `v >> 20`, in
reply → component → Q limb → chunk order. Hence 4×2×2×2 = 32 plaintexts,
each of 4096 coefficients. The full 32×4096 u32 buffer is static BSS; no
Golden or exported reference plaintext is read by `pir_cpu_decompose()`.

## Stage1 physical encoding

The 102 package plaintext limbs comprise 6 fixed limbs (two plaintexts ×
three Q moduli) and 96 dynamic limbs (32 plaintexts × three Q moduli).
`pir_unified_layout.py` resolves every dynamic allocation ID, physical line,
Q limb, and plaintext index from the validated line map. It rejects changed
counts, modulus chains, duplicate/missing coverage, overlap with HPU writable
lines, and out-of-window spans. The CPU encoder validates all inputs and
spans before changing DDR and writes only the 96 dynamic physical regions.

For each coefficient `v` in `[0,t)`, the target applies BFV signed plaintext
lift using `upper_half=(t+1)/2`: `v` below that threshold maps to `v` in Q,
and values at or above it map to `q-(t-v)`. It multiplies coefficient `i` by
`psi^i mod q`, bit-reverses the twisted input for a forward decimation-in-time
NTT, then applies the 12 stage, 128-lane twiddle/butterfly/permutation schedule
of `HardwareNttModel`. The per-Q roots from the same-run producer fixture are
validated against the package moduli and `psi^4096=-1 mod q`; they are embedded
in the unified ELF's read-only layout table. All multiplication uses u64
intermediates. The resulting physical words match the compiler's native
little-endian NTT layout, including its per-stage lane rotation.

The concrete moduli in this fixed package are `t=2056193`, stage0 output
Q=`[2147205121,2147295233]`, stage1 input
Q=`[2147205121,2147295233,2147352577]`, and stage1 psi
`[425927,872006,1689795]`.

## Independent host results

On the development server, `test_pir_cpu_algorithms.py` compiled these *same*
C sources with GCC `-std=c11 -O2 -Wall -Wextra -Werror`, then tested the
baseline and changed database seeds from fresh encoded-instruction stage0
executions. For **each** input, all 131,072 decomposed coefficients matched
the same-run C++/SEAL export, and all 393,216 encoded physical words matched
the compiler export. The complete patched image matched the original patch
path byte for byte; no fixed region changed. SHA-256 of the two patched images:

| Seed | Patched stage1 image SHA-256 |
| --- | --- |
| Baseline | `d7ce4d4fb9af69726f03a5f04d9edeb0061e2de6d55d97e90b413a9169d81caa` |
| Changed | `a7f0012090a0e9d0c7d7354fb2511effbfc96daebb422b55315ff70f9a7a4675` |

Both **C-generated** images were fed directly to `pir_cpu_encoded_replay`,
which ran the unmodified 26,700 encoded stage1 instructions with 9,642 DMA
spans. Each replay completed and compared all 2,915,136 final image words to
the same-run SEAL-checked execution image. The earlier dynamic handoff run
also independently checked recovered record bytes for both database seeds.

Negative tests rejected duplicate/missing stage0 limb coverage, short output
window, noncanonical stage0 coefficient, noncanonical plaintext coefficient,
duplicate stage1 limb, and out-of-window stage1 limb. Encoder validation
failures left DDR unchanged. These are host software tests of target C, not
RTL fault injection.
