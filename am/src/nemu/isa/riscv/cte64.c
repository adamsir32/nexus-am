#include <riscv.h>
#include <nemu.h>
#include <stddef.h>
extern void __am_timervec(void);

#if defined(__ARCH_RISCV64_XS) && defined(LINKNAN_HPU_IT)
#include <xs.h>
#endif

/* 前两项供timer使用，后三项供所有机器trap保存a1/a2/a3。 */
static struct {
  uintptr_t compare_address;
  uintptr_t interval;
  uintptr_t saved[3];
} machine_trap_context __attribute__((aligned(16)));

volatile uintptr_t __am_machine_trap_fault[3];

_Static_assert(sizeof(uintptr_t) == 8, "mtime.S使用RV64保存区布局");
_Static_assert(offsetof(typeof(machine_trap_context), saved) == 16,
               "mtime.S保存寄存器偏移必须为16/24/32");

void __am_machine_timer_config(uintptr_t compare_address, uintptr_t interval) {
  machine_trap_context.compare_address = compare_address;
  machine_trap_context.interval = interval;
}

void __am_machine_timer_interval(uintptr_t interval) {
  machine_trap_context.interval = interval;
}

static void init_machine_exception(void) {
  /* mscratch始终指向真实、对齐的保存区；不能依赖init_timer()的副作用。 */
  asm volatile("csrw mscratch, %0" : : "r"(&machine_trap_context) : "memory");
  asm volatile("csrw mtvec, %0" : : "r"(__am_timervec) : "memory");
}

int g_config_disable_timer = 0; // dirty hack of __am_init_cte64(), to be refactored
extern void init_timer();
extern void enable_timer();
extern void init_pmp(); 
extern void enable_pmp(uintptr_t pmp_reg, uintptr_t pmp_addr, uintptr_t pmp_size, uint8_t lock, uint8_t permission);
extern void enable_pmp_TOR(uintptr_t pmp_reg, uintptr_t pmp_addr, uintptr_t pmp_size, bool lock, uint8_t permission);
#include <csr.h>

static void init_eip() {
  // enable machine external interrupt (mie.meip and mstatus.mie)
  asm volatile("csrs mie, %0" : : "r"(1 << 11));
  asm volatile("csrs mstatus, %0" : : "r"(1 << 3));
}

void __am_init_cte64() {
  /* 注册表已准备好；保存区安装前仍禁止机器中断进入。 */
  asm volatile("csrc mstatus, %0" : : "r"((uintptr_t)(1U << 3)) : "memory");
  asm volatile("csrc mie, %0" : : "r"((uintptr_t)0x8a2U) : "memory");
  init_machine_exception();
  // set delegation (do not deleg illegal instruction exception)
  asm volatile("csrw mideleg, %0" : : "r"(0xffff));
  asm volatile("csrw medeleg, %0" : : "r"(0xfffb));

  // set PMP to access all memory in S-mode
  // asm volatile("csrw pmpaddr8, %0" : : "r"(-1));
  // asm volatile("csrw pmpcfg2, %0" : : "r"(31));
  
  init_pmp();
#if !defined(LINKNAN_HPU_IT)
#if defined(__ARCH_RISCV64_NOOP) || defined(__ARCH_RISCV32_NOOP) || defined(__ARCH_RISCV64_XS)
  // protect 0x90000000 + 0x10000 for test purpose
  enable_pmp(1, 0x90000000, 0x10000, 0, 0); // !rw
  // protect 0xb00000000 + 0x100
  enable_pmp_TOR(3, 0xb0000000, 0x1000, 0, 0); // !rw
  enable_pmp_TOR(5, 0xb0004000, 0x1000, 0, PMP_R); // r,!w
  enable_pmp_TOR(7, 0xb0008000, 0x1000, 0, PMP_W); // !r, w
  enable_pmp_TOR(9, 0xb0010000, 0x1000, 0, 0); // !r, w
#elif defined(__ARCH_RISCV64_XS_SOUTHLAKE) || defined(__ARCH_RISCV64_XS_SOUTHLAKE_FLASH)
  // protect 0x210000000 + 0x10000 for test purpose
  enable_pmp(1, 0x2010000000, 0x10000, 0, 0);
  // protect 0x240000000 + 0x100
  enable_pmp_TOR(4, 0x2040000000, 0x100, 0, 0);
#else
  // invalid arch
#endif
#endif /* CPU PMP定向测试的禁止区不能覆盖HPU的DDR窗口。 */

#if defined(LINKNAN_HPU_IT)
  /* 后续目标程序在S态读取cycle；必须在仍处于M态时开放访问。 */
  asm volatile("csrs mcounteren, %0" : : "r"((uintptr_t)1U) : "memory");
#endif

  if(!g_config_disable_timer){
    init_timer();
    enable_timer();
  }
#if defined(__ARCH_RISCV64_XS) && defined(LINKNAN_HPU_IT)
  /* Initialize the PLIC while still in M-mode and before enabling MEIE. */
  plic_init(PLIC_NUM_SOURCES, PLIC_NUM_CONTEXTS);
#endif
  init_eip();

  // enter S-mode
  uintptr_t status = MSTATUS_SPP(MODE_S);
  extern char _here;
  asm volatile(
    "csrw sstatus, %0;"
    "csrw sepc, %1;"
    "sret;"
    "_here:"
    : : "r"(status), "r"(&_here));
}
