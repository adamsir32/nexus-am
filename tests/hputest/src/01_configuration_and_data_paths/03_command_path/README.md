# 01 命令与DDR通路检查细则

本说明随原02有效测试点归到01。条件时序和对象隔离入口已经归到02，不再保留独立数据通路组。

每个测试点独立成 C 文件。初始化 CSR 和命令顺序保留在 `main`，只复用单条
指令接口、完成电平清除及数据比对。完整程序在最后执行一次 PSYNC；模表 DLOAD、
PMODLD 和计算之间不插入 PSYNC，也不把这些测试混同于 00-06 的纯 MMIO 同步用例。

命名中的内部 `cmd_kind=0` 对应当前物理 opcode `0x5B`；DMA 的 `cmd_kind=1`
仍使用 `0x2B`。机器码来自已固定的 inline-asm 编码器及 AM opcode 接收映射。

| 用例 | 实际激励与软件检查 | 仍需外部证据 |
| --- | --- | --- |
| `01_04_cmd_handshake` | 模表 DLOAD、PMODLD(0)、PFREE(p4)、最终 PSYNC；检查无 fault 和 DDR 无改写 | 每条命令单次接收、无等待/单拍/多拍反压时的 payload，`needs-monitor` |
| `01_05_dma_arg_pair` | p0/p1 两组 DLOAD/DSTORE，输出 A/B 分别与独立影子比较，各 4096 words | 每笔命令与 x10/x11 参数的周期级配对、无丢失/重复，`needs-monitor` |
| `01_06_dma_loopback` | DDR[A]→p0→DDR[OUT] 完整 4096-word 回环 | DMA/AXI 事务及方向，`needs-monitor` |
| `01_07_compute_writeback` | 模表、A/B DLOAD→PADD(p2,p0,p1)→DSTORE→释放剩余输入/模表→PSYNC；逐项与 CPU 模加 golden 比较 | 命令到数据通路的逐周期对应关系，`needs-monitor` |

## 日志和 guard

发令前打印对象、相对 line、line count、模数/上下文和预计的完整命令链。
失败打印阶段、源文件行号以及只读 CSR 状态。CSR 诊断为独立采样，不会读取
PLIC claim，也不把几次 MMIO 读取声称为原子快照。

所有输入、模表、未使用区域的原值保存于 CPU shadow。只允许各用例明确列出的
DSTORE 区域改变；其余 512-line 窗口逐字检查。比较输出时不从可能被 HPU 污染的
现场 DDR 重新计算 golden，首错日志给出地址、系数索引、实际值和期望值。

`return 0` 仅表示软件数据/状态检查通过。未绑定 STING/monitor 时，不能把
`seed_tag` 日志、正常完成或 guard 通过视为反压、队列满、CDC、AXI 零副作用、
对象容量上界等测试目标全部达成。逻辑 p0..p7 是对象编号，不是八个大容量物理 bank。
