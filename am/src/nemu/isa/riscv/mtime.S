# 机器trap入口：保存区由CTE64无条件初始化，不依赖timer是否启用。

.globl __am_timervec
.align 4
__am_timervec:
        csrrw a0, mscratch, a0
        sd a1, 16(a0)
        sd a2, 24(a0)
        sd a3, 32(a0)

        # read mcause
        csrr a1, mcause
        # 非法指令只接受下方固定的S态重新武装请求。
        li a2, 2
        beq a1, a2, is_illegal
        # test whether it's a timer interrupt
        li a2, 1
        slli a2, a2, 63
        addi a2, a2, 7
        beq a1, a2, is_timer
        li a2, 1
        slli a2, a2, 63
        addi a2, a2, 11
        beq a1, a2, is_ext
        j unexpected_machine_trap

is_timer:
        # schedule the next timer interrupt
        # by adding interval to mtimecmp.
        ld a1, 0(a0) # CLINT_MTIMECMP(hart)
        ld a2, 8(a0) # interval
        beqz a1, unexpected_machine_trap
        beqz a2, unexpected_machine_trap
        ld a3, 0(a1)
        add a3, a3, a2
        sd a3, 0(a1)

        # raise a supervisor timer interrupt.
	li a3, 32
        csrw mip, a3
        j end_of_intr

is_ext:
        # disable machine mode external interrupt (mie.meie)
        li a3, 0x800
        csrc mie, a3
        # raise a supervisor external interrupt
        li a3, 0x200
        csrs mip, a3

        j end_of_intr

is_illegal:
        # 必须来自S态、准确的入口PC和准确的32位CSR读指令；不吞掉其它illegal。
        csrr a1, mstatus
        li a2, 0x1800
        and a1, a1, a2
        li a2, 0x800
        bne a1, a2, unexpected_machine_trap
        csrr a1, mepc
        la a2, __am_irq_rearm_request
        bne a1, a2, unexpected_machine_trap
        lwu a1, 0(a1)
        li a2, 0x30402073
        bne a1, a2, unexpected_machine_trap
        # 先撤销转发的pending，再允许下一次机器外部中断。
        li a3, 0x220
        csrc mip, a3
        li a3, 0x800
        csrs mie, a3
        csrr a3, mepc
        addi a3, a3, 4
        csrw mepc, a3

end_of_intr:
        ld a3, 32(a0)
        ld a2, 24(a0)
        ld a1, 16(a0)
        csrrw a0, mscratch, a0

        mret

unexpected_machine_trap:
        # 原样记录mepc/mcause/mtval后失败退出；绝不随意把mepc加4继续执行。
        la a1, __am_machine_trap_fault
        csrr a2, mepc
        sd a2, 0(a1)
        csrr a2, mcause
        sd a2, 8(a1)
        csrr a2, mtval
        sd a2, 16(a1)
        # _halt的终止指令若在真机上也触发trap，保存区仍必须有效。
        csrw mscratch, a0
        li a0, 2
        tail _halt

.globl __am_irq_rearm
.align 2
__am_irq_rearm:
        # 固定32位指令，不允许调用者通过其它任意illegal越过机器特权检查。
.globl __am_irq_rearm_request
__am_irq_rearm_request:
        .word 0x30402073 # csrrs zero, mie, zero；S态必定进入is_illegal。
        ret
