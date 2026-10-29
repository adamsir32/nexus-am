/* Namespaced immutable fixtures for two sequential programs in one ELF. */
    .section .rodata.pir_stage0_image,"a",@progbits
    .balign 256
    .globl stage0_initial_image
stage0_initial_image:
    .incbin "stage0/image.u32.bin"
    .size stage0_initial_image, . - stage0_initial_image

    .section .rodata.pir_stage1_image,"a",@progbits
    .balign 256
    .globl stage1_initial_image
stage1_initial_image:
    .incbin "stage1/image.u32.bin"
    .size stage1_initial_image, . - stage1_initial_image

    .section .rodata.pir_stage0_golden,"a",@progbits
    .balign 256
    .globl stage0_golden_words
stage0_golden_words:
    .incbin "stage0/golden.u32.bin"
    .size stage0_golden_words, . - stage0_golden_words

    .section .rodata.pir_stage1_golden,"a",@progbits
    .balign 256
    .globl stage1_golden_words
stage1_golden_words:
    .incbin "stage1/golden.u32.bin"
    .size stage1_golden_words, . - stage1_golden_words

    .section .rodata.pir_stage0_writable,"a",@progbits
    .globl stage0_writable_lines
stage0_writable_lines:
    .incbin "stage0/writable.u8.bin"
    .size stage0_writable_lines, . - stage0_writable_lines

    .section .rodata.pir_stage1_writable,"a",@progbits
    .globl stage1_writable_lines
stage1_writable_lines:
    .incbin "stage1/writable.u8.bin"
    .size stage1_writable_lines, . - stage1_writable_lines

    .section .rodata.pir_stage1_cpu_writable,"a",@progbits
    .globl stage1_cpu_writable_lines
stage1_cpu_writable_lines:
    .incbin "stage1/cpu_writable.u8.bin"
    .size stage1_cpu_writable_lines, . - stage1_cpu_writable_lines
    .section .note.GNU-stack,"",@progbits
