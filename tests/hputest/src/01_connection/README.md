# 01 配置、状态、正常连接与数据通路

本组8项只验收正常工作路径。窗口末端/越界、时序压力、对象隔离和CPU交叉等已迁到02，
不是看到用例写CSR就重复归入01。旧名与新路径见[迁移表](../../docs/case-id-migration.tsv)。

每个测试点保持独立 C 文件，`main` 中直接写 BASE/SIZE、读回并 COMMIT。
默认串口只保留短摘要和失败，阶段保留RAM trace；详细日志可用于定位。失败报告源文件行号、
阶段和 STATUS/FAULT/IRQ/BASE/SIZE 的实际读值；这些寄存器分别采样，不能视为
同一时刻的原子快照，失败诊断也不会读取有 claim 副作用的 PLIC 寄存器。

| 用例 | 本次实际软件检查 | 仍需外部证据 |
| --- | --- | --- |
| `01_01_mmio_rw` | 四个 shadow CSR 写入/读回、COMMIT 后窗口有效、空闲 PSYNC 完成、IRQ W1C 清除 | CSR 访问握手及逐周期状态，`needs-monitor` |
| `01_02_window_commit` | 先提交 A 窗口、再提交 B 窗口，B 相对地址 `0→64` 对应物理 line `256→320` 的一行回环；B canary 为 A 首行逐项 `+1 mod q`，保证读错旧窗口不能通过 | COMMIT 前后原子生效、无 BASE/SIZE 半更新组合，`needs-monitor` |
| `01_03_dma_busy_transition` | DLOAD/DSTORE 程序中实际采样到 BUSY，再观察最终 IRQ 与空闲，比较完整 4096-word 回环 | 更细的逐周期状态迁移，`needs-monitor` |
| `01_04_cmd_handshake` | 模表DLOAD→PMODLD→PFREE→PSYNC；无fault且DDR不变 | 命令只接收一次、等待期间payload稳定 |
| `01_05_dma_arg_pair` | p0/p1分别装载A/B并写回，独立CPU影子逐项比较 | x10/x11与每条DMA命令逐周期配对 |
| `01_06_dma_loopback` | DDR[A]→p0→DDR[OUT]，完整4096-word回环 | DMA方向、AXI地址和长度 |
| `01_07_compute_writeback` | A/B/模表DLOAD→PADD→DSTORE→末尾PSYNC，逐项CPU模加golden | 命令到数据通路的逐周期对应 |
| `01_08_channel_loopback` | 两个profile，p0/A、p1/B分别回环；比较输出和全窗非输出区 | 正常接收/CDC无丢失、重复或串配；若施加反压需额外monitor证据 |

## 数据和通过条件

- 使用 inline-asm producer 的两组 4096 个系数；CPU 独立 shadow 保存输入和期望值。
- `v2_prepare` 先给 512-line 测试区填充地址相关 guard，输出保留 poison，不预装 golden。
- 仅将明确的 DSTORE 目标标记为允许写入，最后检查其余窗口中的输入、模表和 guard。
- 窗口回环、数据检查、完成事件检查均通过才 `return 0`。日志中的
  `SW-CHECK-PASS` 只代表软件检查通过，不意味着 `needs-monitor` 部分已经验收。
- `01_03_dma_busy_transition`有意要求软件观察到BUSY，与只检查回环数据的用例不是同一判据；日志记录最后的STATUS、是否曾见BUSY和
  轮询次数。`TIMEOUT` 是轮询上限，不是 VCS cycle 数，不能据此保证一百万周期足够。

## 与02的衔接

02保留`02_01_window_bounds`、`02_02_window_write_order`、`02_05_dload_window_fault`和`02_04_psync_rearm_mmio`，
以及多对象隔离、队列压力和CPU交叉。详见[02说明](../02_boundary/README.md)。

当前没有把“未提交配置”“零长度”“非法对象/不支持类型”等都当作同一种故障。
这些场景需按明确的接口定义逐项增加预期和激励，不能从仿真现象反推语义。
同值重复 COMMIT、部分 shadow 写入时的原子性、DSTORE 故障方向等也没有被
上表现有软件检查替代。guard 只能验证本测试窗口中的最终内容，不能证明所有
DDR 地址、读事务或瞬时 AXI 副作用不存在。
