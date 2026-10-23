# 02 边界、条件时序、RISC-V交叉与故障

本组16项；正常命令接收、参数配对与数据回环归01。
分类和短名规则见[整理说明](../../docs/TEST_ORGANIZATION.md)，旧路径见[迁移表](../../docs/case-id-migration.tsv)。

## 配置、地址、对象和同步边界

| 用例 | 已有软件检查 | 限制/外部证据 |
|---|---|---|
| `02_01_window_bounds` | 首端/末端1line、中间3lines、末端合法64lines，逐字比较 | AXI地址/长度、窗口外副作用需monitor |
| `02_02_window_write_order` | 固定窗口偏移、BASE/SIZE两种写序、shadow读回/提交 | 非随机生成器；原子生效和随机回放未由软件证明 |
| `02_03_object_isolation` | 两对象、四DDR区域、反序写回，结果和guard检查 | 只有两个驻留对象，不是容量上界；随机时序另需环境 |
| `02_04_psync_rearm_mmio` | 两段独立空闲程序，逐轮观察并清MMIO完成电平 | 不替代真实PLIC/CPU中断次数检查 |
| `02_05_dload_window_fault` | 越界DLOAD line512，检查load/p0 fault与W1C，DDR不改写 | 无非法AXI事务仍需monitor；不外推其它非法输入语义 |

CPU混合、连续1/8/9/32/64条算术命令是独立边缘入口，每个ELF仅运行一遍。
三项条件看门狗负向实验已移到`tests/hpu-experiments/watchdog`，不在本组默认清单中；
它们依赖匹配RTL和独立复位，不能用软件超时冒充核侧握手超时故障。

本章把“软件闭环自检”与“结构时序覆盖”分开验收。软件 `return 0` / `[HPU][PASS]` 只表示当前程序检查通过；不能据此认定 ready 反压、CDC、命令缓存满载或提交顺序已经验证。

逻辑计算/控制通道仍称 `custom0` 或 `cmd_kind=0`，实际 RISC-V 主 opcode 已是 `0x5B`；DLOAD/DSTORE 的 `custom1` 仍为 `0x2B`。发令使用当前 inline-asm 交付生成的机器码和 AM 接收层映射，不在用例里手工拼编码。

## 时序压力与交叉执行

| 文件 | 实际程序 | 软件自检 | 仍需 IT 提供的证据 |
| --- | --- | --- | --- |
| `02_06_cmd_timing` | 模表DLOAD→8条PMODLD→释放→PSYNC | DDR不变、完成和状态检查 | 固定激励，不代表外部STING随机/反压已覆盖 |
| `02_07_cmd_queue_8_plus_1` | 模表DLOAD→9条PMODLD→释放→PSYNC | 完成、清电平、无fault、DDR不变 | 8条确实积压、第9条等待、释放后保序，需queue/ready monitor |
| `02_08_channel_timing` | 两轮确定性p0/A、p1/B回环，每轮末尾PSYNC | 结果与非输出区检查 | 真实随机驱动、seed/replay和CDC监视另需平台 |
| `02_09_cpu_hpu_config_mix` | 8次“PMODLD+128步CPU xorshift” | CPU末值`0xba61d264`和DDR不变 | 接收/提交顺序与队列满载不能由末值推断 |

`02_10_cmd_burst_1/8/9/32/64`是连续算术命令快测，`02_15_cpu_hpu_alu_mix`和
`02_16_cpu_hpu_mem_branch_mix`检查普通CPU运算/访存分支与HPU交叉。
条件看门狗实验的实现和RTL限制见独立实验README。

错误路径、异常/特权及随机CPU交叉仍需环境和真实激励；旧占位C已删除，不发布占位ELF。

原STR001正常通道回环已移到01的`01_08_channel_loopback`；其反压/CDC目标仍须monitor，不丢弃原检查要求。

其它分支预测、核内异常、特权进入/返回测试不因上述定向检查通过而自动覆盖；当前可运行入口以唯一`cases.tsv`为准。

## 数据和结束方式

每轮先调用仅处理数据的 `v2_prepare`。profile 0 使用固定 producer A/B；profile 1 使用 AM 明确派生的0、1、q−1等边界输入，不冒充随机数据。用例在 `main` 中逐项写入并读回 BASE/SIZE，再 COMMIT；辅助接口不隐藏 CSR 配置或额外 HPU 指令。

DDR窗口为512 line，每line为256字节。A/B各64 line（4096个32位系数），模表在line192。STR001允许写回line128..191和256..319；STING确定性样例每轮只允许相应的一个输出区。STR002/STR006不允许任何HPU DDR写回。

期望值取自独立CPU影子，不以可能已被HPU污染的现场输入作golden。结束后失效cache再检查所有非输出区域，包括输入、模表和guard。这个检查能发现本窗口的意外改写，不能证明窗口外或额外读取AXI事务不存在；后者仍由monitor验收。

每段程序只在末尾发送一次PSYNC，随后依次调用 `wait_irq()`、`completion_clear()`、`check_status()`。这里的 `wait_irq()` 是读取MMIO完成电平，不是进入CPU中断处理函数；这些等待接口不再发PSYNC。DSTORE释放它写回的对象；只有仍驻留的模表对象再显式PFREE，避免重复释放。

## 队列/反压实验要点

- 先确认本包和simv采用兼容编码，并记录各自提交版本。
- 对被测九条PMODLD单独编号，区分前导DLOAD及后续PFREE/PSYNC。环境应控制队列排空/ready时序，让前八条确实积压，再观察第九条等待；不能仅根据CPU执行了九次函数调用推断队列曾满。
- 挂起期间检查请求payload保持稳定，恢复后检查每条命令恰好接受一次、无串配且保序。分别记录无等待、单拍和多拍反压的波形/覆盖点。
- STR006中的CPU计算会自然改变发令间隔；是否仍处于满载必须看真实占用，而不是由用例名推断。
- RAM trace记录 `PREPARE`、`ISSUE`、`CHECK`，默认串口保留短摘要与错误。发令突发内部没有成功路径printf；失败时打印具体phase/参数和一次失败后MMIO现场，避免串口输出人为排空队列。
- 轮询预算不是VCS总cycle预算。两轮数据准备、cache维护、全窗guard扫描和串口日志都消耗CPU周期；按实际运行日志配置仿真上限，不统一承诺100万cycle足够。

`STING_STR_001`只能作为确定性接入样例，不能以其两轮通过替代随机用例规模、种子重放或约束覆盖报告。任何结构时序验收都应同时保存IT monitor证据。
