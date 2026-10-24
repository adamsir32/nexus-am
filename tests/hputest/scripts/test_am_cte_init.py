#!/usr/bin/env python3
"""验证真实AM初始化代码的顺序/幂等性，并交叉编译机器trap入口。

主机桩仅替换RISC-V内联汇编；不声称模拟特权级、PLIC或RTL时序。
"""
from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest

AM_ROOT = Path(__file__).resolve().parents[3]
CTE = AM_ROOT / "am/src/nemu/isa/riscv/cte.c"
CTE64 = CTE.with_name("cte64.c")
MTIME = CTE.with_name("mtime.S")
CLINT = AM_ROOT / "am/src/xs/isa/riscv/clint.c"

AM_STUB = r"""
#ifndef MOCK_AM_H
#define MOCK_AM_H
#include <stdint.h>
#include <stdbool.h>
typedef struct { uintptr_t gpr[32], scause, sepc, sstatus; void *pdir; } _Context;
typedef struct { int event; } _Event;
typedef struct { void *start, *end; } _Area;
enum { _EVENT_ERROR, _EVENT_IRQ_SOFT, _EVENT_IRQ_TIMER, _EVENT_IRQ_IODEV,
       _EVENT_YIELD, _EVENT_SYSCALL };
#define GPR1 gpr[17]
#define GPR2 gpr[10]
void _halt(int);
#endif
"""

HARNESS = r"""
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
unsigned char fake_clint[0xc000 + 8] __attribute__((aligned(16)));
static unsigned asm_count, machine_count, pmp_count, plic_count, rearm_count;
static unsigned scratch_at, mtvec_at, machine_enable_at, machine_cycle_at;
static int machine_started;
static void record_asm(const char *text);
@PRODUCTION@
char _here;
void __am_asm_trap(void) {}
void __am_timervec(void) {}
void __am_get_cur_as(_Context *context) { (void)context; }
void __am_switch(_Context *context) { (void)context; }
void _halt(int value) { (void)value; abort(); }
void __am_irq_rearm(void) { ++rearm_count; }
void init_pmp(void) { ++machine_count; }
void enable_pmp(uintptr_t a, uintptr_t b, uintptr_t c, uint8_t d, uint8_t e) {
    (void)a; (void)b; (void)c; (void)d; (void)e; ++pmp_count;
}
void enable_pmp_TOR(uintptr_t a, uintptr_t b, uintptr_t c, bool d, uint8_t e) {
    (void)a; (void)b; (void)c; (void)d; (void)e; ++pmp_count;
}
void plic_init(uint32_t sources, uint32_t contexts) {
    assert(sources == 257 && contexts == 2);
    assert(scratch_at && mtvec_at && scratch_at < mtvec_at);
    ++plic_count;
}
static void record_asm(const char *text) {
    ++asm_count;
    if (strstr(text, "csrc mstatus")) {
        machine_started = 1;
        /* 默认注册表在允许任何机器trap之前就已完整准备。 */
        assert(interrupt_handler[SCAUSE_SEIP] == __am_irq_SEIP_handler);
        assert(exception_handler[SCAUSE_SECALL] == __am_irq_SECALL_handler);
        assert(exception_handler[2] == __am_irq_default_handler);
    }
    if (strstr(text, "csrw mscratch")) {
        assert(machine_started);
        assert(strstr(text, "&machine_trap_context"));
        assert((uintptr_t)&machine_trap_context != 0);
        assert(((uintptr_t)&machine_trap_context & 15) == 0);
        scratch_at = asm_count;
    }
    if (strstr(text, "csrw mtvec")) {
        assert(scratch_at);
        mtvec_at = asm_count;
    }
    if (strstr(text, "csrs mcounteren")) machine_cycle_at = asm_count;
    if (strstr(text, "csrs mstatus")) {
        assert(mtvec_at && plic_count == EXPECT_HPU);
        machine_enable_at = asm_count;
    }
}
static _Context *custom(_Event event, _Context *context) {
    assert(event.event == _EVENT_IRQ_IODEV);
    return context;
}
static _Context *direct(_Event *event, _Context *context) {
    (void)event; return context;
}
int main(int argc, char **argv) {
    assert(argc == 2);
    int timer_enabled = atoi(argv[1]);
    g_config_disable_timer = !timer_enabled;
    assert(_cte_init(NULL) == 0);
    assert(machine_count == 1 && machine_enable_at > mtvec_at);
    assert((machine_cycle_at != 0) == EXPECT_HPU);
    assert(pmp_count == (EXPECT_HPU ? 0U : 5U));
    if (timer_enabled) {
        assert(machine_trap_context.compare_address == (uintptr_t)(fake_clint + 0x4000));
        assert(machine_trap_context.interval == 0x800);
        assert(*(uint64_t *)(fake_clint + 0x4000) == 0x800);
        set_timer_inc(4096);
        assert(machine_trap_context.interval == 4096);
    } else {
        assert(machine_trap_context.compare_address == 0);
        assert(machine_trap_context.interval == 0);
    }
    seip_handler_reg(custom);
    irq_handler_reg(3, direct);
    unsigned saved_asm_count = asm_count;
    /* 真实代码第二次运行于S态，主机桩要求它完全不再执行CSR汇编。 */
    assert(_cte_init(NULL) == 0);
    assert(asm_count == saved_asm_count && machine_count == 1);
    assert(custom_external_handler == custom && exception_handler[3] == direct);
    _Context context = {0};
    _Event event = {0};
    __am_irq_SEIP_handler(&event, &context);
    assert(event.event == _EVENT_IRQ_IODEV && rearm_count == 1);
    return 0;
}
"""


def mock_assembly(source):
    """保留实际C控制流和汇编操作数说明，只替换完整asm语句。"""
    pattern = re.compile(r"\basm\s+volatile\s*\(")
    result, last = [], 0
    for match in pattern.finditer(source):
        if match.start() < last:
            continue
        tokens = re.compile(r'"(?:\\.|[^"\\])*"|/\*.*?\*/|//[^\n]*|[()]', re.S)
        depth, finish = 1, None
        for token in tokens.finditer(source, match.end()):
            if token[0] == "(":
                depth += 1
            elif token[0] == ")":
                depth -= 1
                if depth == 0:
                    finish = token.end()
                    break
        if finish is None:
            raise ValueError("unbalanced inline assembly")
        result.extend([source[last:match.start()],
                       "record_asm(" + json.dumps(source[match.start():finish]) + ")"])
        last = finish
    return "".join(result) + source[last:]


class TrapInstructionModel:
    """执行mtime.S中本次涉及的RV64整数/CSR指令；不是RTL或完整ISA模拟器。"""
    MASK = (1 << 64) - 1

    def __init__(self, cause, pc=0x80000800, status=0x800, configured=False):
        self.instructions, self.labels = [], {}
        for line in MTIME.read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if not line or line.startswith("."):
                continue
            if line.endswith(":"):
                self.labels[line[:-1]] = len(self.instructions)
            else:
                self.instructions.append(line)
        self.registers = {"zero": 0, "a0": 0x1234, "a1": 0x2345,
                          "a2": 0x3456, "a3": 0x4567}
        self.original = dict(self.registers)
        self.csrs = {"mscratch": 0x80001000, "mcause": cause,
                     "mepc": pc, "mtval": 0xbad, "mstatus": status,
                     "mie": 0, "mip": 0x220}
        self.memory = {0x80001000: 0x80003000 if configured else 0,
                       0x80001008: 2048 if configured else 0,
                       0x80003000: 4096}
        self.addresses = {"__am_irq_rearm_request": 0x80000400,
                          "__am_machine_trap_fault": 0x80002000}
        self.memory[0x80000400] = 0x30402073
        self.result = None

    def run(self):
        cursor = self.labels["__am_timervec"]
        for _ in range(100):
            operation, *arguments = self.instructions[cursor].replace(",", " ").split()
            cursor += 1
            reg, csr, mem = self.registers, self.csrs, self.memory
            if operation == "csrrw":
                destination, name, source = arguments
                old = csr[name]
                csr[name] = reg[source]
                reg[destination] = old
            elif operation == "csrr":
                reg[arguments[0]] = csr[arguments[1]]
            elif operation in ("csrw", "csrs", "csrc"):
                name, source = arguments
                value = reg[source]
                csr[name] = (value if operation == "csrw" else
                             csr[name] | value if operation == "csrs" else
                             csr[name] & ~value)
            elif operation == "li":
                reg[arguments[0]] = int(arguments[1], 0) & self.MASK
            elif operation == "la":
                reg[arguments[0]] = self.addresses[arguments[1]]
            elif operation in ("add", "addi", "and", "slli"):
                destination, left, right = arguments
                value = reg[right] if operation in ("add", "and") else int(right, 0)
                reg[destination] = ((reg[left] & value) if operation == "and" else
                                    (reg[left] << value) if operation == "slli" else
                                    reg[left] + value) & self.MASK
            elif operation in ("sd", "ld", "lwu"):
                register, address = arguments
                offset, base = re.fullmatch(r"(-?\d+)\((\w+)\)", address).groups()
                address = reg[base] + int(offset)
                if operation == "sd":
                    assert 0x80001000 <= address < 0x80001028 or 0x80002000 <= address < 0x80002018 or address == 0x80003000
                    mem[address] = reg[register]
                else:
                    reg[register] = mem[address]
                    if operation == "lwu":
                        reg[register] &= 0xffffffff
            elif operation in ("beq", "bne"):
                left, right, label = arguments
                if (reg[left] == reg[right]) == (operation == "beq"):
                    cursor = self.labels[label]
            elif operation == "beqz":
                if reg[arguments[0]] == 0:
                    cursor = self.labels[arguments[1]]
            elif operation == "j":
                cursor = self.labels[arguments[0]]
            elif operation == "mret":
                self.result = "returned"
                return self
            elif operation == "tail" and arguments == ["_halt"]:
                self.result = reg["a0"]
                return self
            else:
                raise AssertionError("unsupported trap instruction: " + operation)
        raise AssertionError("machine trap did not terminate")


class CteInitTests(unittest.TestCase):
    def test_timer_off_on_and_repeated_supervisor_initialization(self):
        with tempfile.TemporaryDirectory(prefix="am-cte-test-") as temporary:
            directory = Path(temporary)
            (directory / "am.h").write_text(AM_STUB)
            (directory / "klib.h").write_text("#include <assert.h>\n#include <stdio.h>\n")
            (directory / "nemu.h").write_text('#include <am.h>\n#include <riscv.h>\n')
            (directory / "csr.h").write_text("#define PMP_R 1\n#define PMP_W 2\n")
            (directory / "xs.h").write_text(
                '#include <nemu.h>\nextern unsigned char fake_clint[];\n'
                '#define RTC_ADDR ((uintptr_t)(fake_clint + 0xbff8))\n'
                '#define PLIC_NUM_SOURCES 257U\n#define PLIC_NUM_CONTEXTS 2U\n'
                'void plic_init(uint32_t, uint32_t);\n')
            production = "\n".join(mock_assembly(path.read_text()) for path in (CTE, CTE64, CLINT))
            harness = directory / "harness.c"
            harness.write_text(HARNESS.replace("@PRODUCTION@", production))
            for hpu in (0, 1):
                binary = directory / f"test-{hpu}"
                command = [os.environ.get("CC", "cc"), "-std=gnu11", "-Wall", "-Wextra",
                           "-Wno-format", "-Wno-sign-compare", "-Wno-unused-variable",
                           "-Werror", "-D__riscv_xlen=64",
                           "-D__ARCH_RISCV64_XS", f"-DEXPECT_HPU={hpu}",
                           f"-I{directory}", f"-I{AM_ROOT / 'am/include'}"]
                if hpu:
                    command.append("-DLINKNAN_HPU_IT=1")
                subprocess.run(command + [str(harness), "-o", str(binary)], check=True)
                for timer in (0, 1):
                    subprocess.run([str(binary), str(timer)], check=True)

    def test_controlled_rearm_and_unexpected_trap_failure(self):
        code = MTIME.read_text()
        illegal = code.split("is_illegal:", 1)[1].split("end_of_intr:", 1)[0]
        self.assertIn("__am_irq_rearm_request", illegal)
        self.assertIn("0x30402073", illegal)
        self.assertIn("csrr a1, mstatus", illegal)
        self.assertGreaterEqual(illegal.count("unexpected_machine_trap"), 3)
        fault = code.split("unexpected_machine_trap:", 1)[1].split(".globl __am_irq_rearm", 1)[0]
        for csr in ("mepc", "mcause", "mtval"):
            self.assertIn(f"csrr a2, {csr}", fault)
        self.assertIn("li a0, 2", fault)
        self.assertIn("tail _halt", fault)
        self.assertNotIn("addi a3, a3, 4", fault)

    def test_machine_trap_instruction_paths(self):
        for cause in (2, 0, 5, (1 << 63) | 3):
            trap = TrapInstructionModel(cause).run()
            self.assertEqual(trap.result, 2)
            self.assertEqual([trap.memory[0x80002000 + 8 * item] for item in range(3)],
                             [0x80000800, cause, 0xbad])
            self.assertEqual(trap.csrs["mepc"], 0x80000800)
            self.assertEqual(trap.csrs["mscratch"], 0x80001000)
        # 正确helper地址仍不能从M态冒充S态请求。
        self.assertEqual(TrapInstructionModel(2, pc=0x80000400, status=0x1800).run().result, 2)
        trap = TrapInstructionModel(2, pc=0x80000400).run()
        self.assertEqual(trap.result, "returned")
        self.assertEqual(trap.csrs["mepc"], 0x80000404)
        self.assertEqual(trap.csrs["mie"] & 0x800, 0x800)
        self.assertEqual(trap.csrs["mip"] & 0x220, 0)
        self.assertEqual(trap.registers, trap.original)
        # 地址正确但指令字不匹配，也必须停止而不是跳过。
        trap = TrapInstructionModel(2, pc=0x80000400)
        trap.memory[0x80000400] = 0xffffffff
        self.assertEqual(trap.run().result, 2)
        trap = TrapInstructionModel((1 << 63) | 11).run()
        self.assertEqual(trap.result, "returned")
        self.assertEqual(trap.csrs["mip"] & 0x200, 0x200)
        self.assertEqual(trap.csrs["mie"] & 0x800, 0)
        self.assertEqual(trap.registers, trap.original)
        trap = TrapInstructionModel((1 << 63) | 7, configured=True).run()
        self.assertEqual(trap.result, "returned")
        self.assertEqual(trap.memory[0x80003000], 6144)
        self.assertEqual(trap.csrs["mip"], 32)
        self.assertEqual(trap.registers, trap.original)
        # 禁timer的保存区仍安全，但不能处理未配置的timer调度。
        self.assertEqual(TrapInstructionModel((1 << 63) | 7).run().result, 2)

    def test_rv64_cross_compile_and_flash_port_symbols(self):
        compiler = shutil.which("riscv64-linux-gnu-gcc")
        if compiler is None:
            self.skipTest("no RV64 cross compiler")
        with tempfile.TemporaryDirectory(prefix="am-cte-rv64-") as temporary:
            directory = Path(temporary)
            flags = [compiler, "-std=gnu11", "-Wall", "-Werror", "-Wno-format",
                     "-march=rv64gc", "-mabi=lp64d", "-mcmodel=medany", "-fno-pic",
                     "-ffreestanding", "-fno-builtin", "-O2", '-DARCH_H="arch/riscv64-xs.h"',
                     '-DISA_H="riscv.h"',
                     "-I" + str(AM_ROOT / "am"), "-I" + str(AM_ROOT / "am/include"),
                     "-I" + str(AM_ROOT / "libs/klib/include"),
                     "-I" + str(AM_ROOT / "am/src/nemu/include"),
                     "-I" + str(AM_ROOT / "am/src/xs/include")]
            for hpu in (0, 1):
                mode = flags + ["-D__ARCH_RISCV64_XS"]
                if hpu:
                    mode.append("-DLINKNAN_HPU_IT=1")
                objects = []
                for path in (CTE, CTE64, CLINT, MTIME):
                    target = directory / f"{path.stem}-{hpu}.o"
                    subprocess.run(mode + ["-c", str(path), "-o", str(target)], check=True)
                    objects.append(str(target))
                merged = directory / f"combined-{hpu}.o"
                subprocess.run(["riscv64-linux-gnu-ld", "-r", *objects, "-o", str(merged)], check=True)
                undefined = subprocess.check_output(["riscv64-linux-gnu-nm", "-u", str(merged)], text=True)
                self.assertNotRegex(undefined, r"__am_(?:irq_rearm|machine_timer|machine_trap)")
                disassembly = subprocess.check_output(
                    ["riscv64-linux-gnu-objdump", "-d", str(merged)], text=True)
                self.assertIn("30402073", disassembly)
                self.assertIn("mscratch", disassembly)
                self.assertIn("mret", disassembly)
            flash = directory / "clint-flash.o"
            subprocess.run(flags + ["-D__ARCH_RISCV64_XS_FLASH", "-c", str(CLINT),
                                    "-o", str(flash)], check=True)
            undefined = subprocess.check_output(["riscv64-linux-gnu-nm", "-u", str(flash)], text=True)
            self.assertNotIn("__am_machine_timer", undefined)


if __name__ == "__main__":
    unittest.main()
