# HPU 测试点、甘特图与冒烟用例对齐

本文固定 Nexus-AM HPU 测试源码、测试点文档和项目甘特图之间的命名关系。
唯一机器清单是[`cases.tsv`](../cases.tsv)，不再另维护旧编号子项清单。
计划表每行填写清单中的短名`case_id`和源码路径；命名及旧名追溯见[整理说明](TEST_ORGANIZATION.md)。

## 1. 测试类别

| 甘特图类别 | 源码目录 | 测试点数 | 测试点 ID |
|---|---|---:|---|
| 配置、正常连接与数据通路 | `src/01_connection` | 8 | `01_01_mmio_rw`、`01_06_dma_loopback`等 |
| 边界、RISC-V交叉与故障 | `src/02_boundary` | 16 | `02_01_window_bounds`、`02_11_cmd_burst_8`等；watchdog条件实验独立存放 |
| 指令测试 | `src/03_instructions` | 9 | 仅N1024/level4；`03_01`至`03_09` |
| 基本/组合算子 | `src/04_operators` | 6 | N1024/level4的NTT/INTT/BConv与三算法KeySwitch |
| 算法库接口 | `src/05_library` | 15 | N1024/level4，三算法各五种操作 |
| 应用测试 | `src/06_applications` | 8 | 直接使用上游完整应用；另6项API诊断按需构建 |
| 性能测试 | `src/07_performance` | 36 | N1024/N8192、三算法、输入level4，单ELF一轮计时 |

以上共98项，加`src/00_smoke`的9个冒烟和2个返回值探针，默认109项。
用例数量不等于结构覆盖数量；是否需要monitor、负向预期或特殊结束方式，仍须查看清单`qualifier`。
未实现/未接入项不发布占位二进制，不能因列入计划而标为完成。

## 2. 冒烟用例的当前名称

下表列出完整编号；源码、日志和产物使用相同编号，内部指令、同步和自检不变。
本页下文单独出现的01～09均指00组内用例，不是01～09组。

当前 HPU 配置和状态寄存器只有地址 `0x08000000..0x0800001c` 的 MMIO
访问方式。没有已定义的 HPU architectural CSR 编号，因此不提供 `csrr HPU_STATUS`
版本，也不能拿 `sip`、`mip` 等标准中断 CSR 冒充 HPU STATUS。

| 编号 | 文件 | 唯一目的 |
|---:|---|---|
| `00_01` | `00_01_dload_hold.c` | DLOAD后永久等待，给波形观察留下时间 |
| `00_02` | `00_02_mmio_rw.c` | 逐地址写读BASE/SIZE，COMMIT后检查MMIO STATUS |
| `00_03` | `00_03_dload_mmio.c` | DLOAD，轮询MMIO STATUS的busy由0→1→0 |
| `00_04` | `00_04_psync_irq.c` | 空闲PSYNC，以PLIC source257中断完成 |
| `00_05` | `00_05_dload_irq.c` | DLOAD+PSYNC，以PLIC中断和volatile flag完成 |
| `00_06` | `00_06_loopback_mmio.c` | 分别等待DLOAD、DSTORE的BUSY 1→0，逐4096系数比较；无PSYNC |
| `00_07` | `00_07_loopback_irq.c` | 连续DLOAD+DSTORE+PSYNC，CPU中断完成，逐4096系数比较 |
| `00_08` | `00_08_compute_irq.c` | producer PMUL程序，PSYNC中断完成，golden/C oracle精确比较 |
| `00_09` | `00_09_compute_mmio.c` | 同一PMUL程序，MMIO完成电平轮询，golden/C oracle精确比较 |
| `00_10` | `00_10_return_0.c` | 故意返回0，仅验证结束通道，不验证HPU功能 |
| `00_11` | `00_11_return_1.c` | 故意返回1的预期失败探针，不计为功能失败 |

当前编号只保留 MMIO 状态访问方式：

- 03 只验证 DLOAD 的 MMIO busy 轮询；
- 04 单独隔离空闲 PSYNC 的中断路径；
- 05 在 DLOAD 后验证 PSYNC 中断；
- 06 分别轮询 DLOAD、DSTORE 的 MMIO STATUS；不发 PSYNC、不访问 `CSR_IRQ`、不调用 PLIC 中断路径；
- 07 连续提交 DLOAD、DSTORE，再以 PSYNC 中断完成；与 06 比较相同回环数据，但命令序列和等待位置不同；
- 08 增加 producer 生成的 PMUL 计算闭环。
- 09 与 08 使用同一计算闭环，只把CPU完成等待从PLIC中断改为MMIO轮询。

中断用例公共层使用 `csrs/csrc sie`，只是在 S-mode 打开/关闭标准外部中断，
不是第二种 HPU 状态寄存器访问方式。

06 必须在 DLOAD 完成后才提交 DSTORE，并为每次 DMA 重新清零 `saw_busy`，
各自观察忙状态由 1→0。MMIO 的 BUSY 来自 DMA busy，不能把 DLOAD 结束后的
空闲间隔作为整个回环完成的证据，也不能在命令刚提交时第一次读到 BUSY=0
就通过。如果某一阶段的 BUSY=1 未被 CPU 采到，保守地等待至超时报失败；
该结果不单独证明 RTL 错误，需要结合对应阶段波形复验。

当前 07/08 使用程序末尾的 PSYNC/CPU 中断，09 使用末尾 PSYNC 后 MMIO
轮询。按当前编程手册，08/09 的模表加载和算子内部不插入 PSYNC，完整计算
程序只产生一次完成通知；06 保持无 PSYNC 的分步状态轮询。旧 06 的 IRQ/BUSY
竞态修复记录保留在 [`MMIO_COMPLETION_RACE.md`](MMIO_COMPLETION_RACE.md)，
不能再把其中的 PSYNC+MMIO 流程当成当前 06 的要求。

## 3. IT 回传失败记录的解释边界

以下内容来自 IT/VCS 人工回传的日志和波形，不是 GitHub Actions 或本仓库本地
执行出的 VCS 结果；测试源码不得为了绕过这些现象而放宽判据。

- 06 在旧 RTL 上报告 DSTORE 倒数 burst 附近等待不到 `dma_ack`，随后 DMA
  timeout。该结果应保留为 RTL/版本复验项；增加 C 侧等待次数不能修复 RTL 内部
  ACK 超时。
- 05 卡住时，应先确认 DLOAD 是否完成、PSYNC 是否入队、HPU IRQ 电平是否置位、
  PLIC source 257 是否被 claim。UART用于定位阶段，完成判据仍是claim、状态和
  `main()`返回值，不能只凭打印文本判PASS。
- 07 的 SRAM 警告中 `X` 表示 unknown，`Z` 表示 high impedance；这是 Verilog
  四态数据，不是 RISC-V 的 `Z*` 指令集扩展。应在同一拍区分
  `wr_dma_valid/wr_dma_data` 与计算写回 `wr0_valid/wr0_data`、
  `wr1_valid/wr1_data`，再看最终选择信号和 bank write-enable。
- C self-check 可以在 X/Z 污染落入 DDR 结果后通过 `return 1` 报错，但 C 的
  二态整数本身不能替代波形对 X/Z 来源的定位。

重新运行时必须记录实际 RTL commit。若使用的是聊天中确认的旧 RTL，05/06/07
结果只能作为旧版本失败记录，不能据此修改 Nexus-AM 测试去“适配”错误实现。
