/* 每表独立节：005 只保留正向表，006 只保留逆向表。 */
    .section .rodata.ntt_twiddle_0,"a",@progbits
    .balign 256
    .globl ntt_twiddle_0
    .type ntt_twiddle_0, @object
ntt_twiddle_0:
    .incbin "ntt_stage_00.u32.bin"
    .size ntt_twiddle_0, . - ntt_twiddle_0

    .section .rodata.ntt_twiddle_1,"a",@progbits
    .balign 256
    .globl ntt_twiddle_1
    .type ntt_twiddle_1, @object
ntt_twiddle_1:
    .incbin "ntt_stage_01.u32.bin"
    .size ntt_twiddle_1, . - ntt_twiddle_1

    .section .rodata.ntt_twiddle_11,"a",@progbits
    .balign 256
    .globl ntt_twiddle_11
    .type ntt_twiddle_11, @object
ntt_twiddle_11:
    .incbin "ntt_stage_11.u32.bin"
    .size ntt_twiddle_11, . - ntt_twiddle_11

    .section .rodata.intt_twiddle_0,"a",@progbits
    .balign 256
    .globl intt_twiddle_0
    .type intt_twiddle_0, @object
intt_twiddle_0:
    .incbin "intt_stage_00.u32.bin"
    .size intt_twiddle_0, . - intt_twiddle_0

    .section .rodata.intt_twiddle_1,"a",@progbits
    .balign 256
    .globl intt_twiddle_1
    .type intt_twiddle_1, @object
intt_twiddle_1:
    .incbin "intt_stage_01.u32.bin"
    .size intt_twiddle_1, . - intt_twiddle_1

    .section .rodata.intt_twiddle_11,"a",@progbits
    .balign 256
    .globl intt_twiddle_11
    .type intt_twiddle_11, @object
intt_twiddle_11:
    .incbin "intt_stage_11.u32.bin"
    .size intt_twiddle_11, . - intt_twiddle_11

/* 完整表仅供CPU独立蝶形参考，HPU只装入前述128字种子。 */
    .section .rodata.ntt_full_0,"a",@progbits
    .balign 256
    .globl ntt_full_0
ntt_full_0:
    .incbin "ntt_stage_00_full.u32.bin"
    .section .rodata.ntt_full_1,"a",@progbits
    .balign 256
    .globl ntt_full_1
ntt_full_1:
    .incbin "ntt_stage_01_full.u32.bin"
    .section .rodata.ntt_full_11,"a",@progbits
    .balign 256
    .globl ntt_full_11
ntt_full_11:
    .incbin "ntt_stage_11_full.u32.bin"
    .section .rodata.intt_full_0,"a",@progbits
    .balign 256
    .globl intt_full_0
intt_full_0:
    .incbin "intt_stage_00_full.u32.bin"
    .section .rodata.intt_full_1,"a",@progbits
    .balign 256
    .globl intt_full_1
intt_full_1:
    .incbin "intt_stage_01_full.u32.bin"
    .section .rodata.intt_full_11,"a",@progbits
    .balign 256
    .globl intt_full_11
intt_full_11:
    .incbin "intt_stage_11_full.u32.bin"

    .section .note.GNU-stack,"",@progbits
