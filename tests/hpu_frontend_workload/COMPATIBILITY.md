# Inline-asm更新与原用例兼容性

本轮跟进`feature/operator-resource-management`，从`9686076`升级至`3ab94da16abce89b7e9b74f4e7fcd93604dea495`。上游main并未合入这些实验改动，本次不切换到main，也不修改RTL。

两项上游变化：`9a587c2`统一SSA资源管理、减少应用IO；`3ab94da`加入在线PMUL因子模板。公共ApplicationBuilder/Evaluator接口未破坏，保留已有测试目标和图，优先直接使用上游生成方法，不在AM重写同态算法。

## 哪些旧用例可以继续用

| 范围 | 结论与必要动作 |
|---|---|
| 00～03，44项 | 普通对象/立即数运算、DMA、单stage K8合同不变；C用例沿用，使用新编码器重新生成。普通指令机器字清单与旧版逐字相同。 |
| 04，9项 | 复用整体NTT/INTT/BConv及KeySwitch测试；原语metadata升级v3，使用上游在线PMUL和新ResolvedDma绑定结构。 |
| 05，37项 | 复用三算法库图和特殊参数回归；HMUL的tensor等内部值可留在片上，所有标记输出仍完整自检。 |
| 06，8项 | 继续直接运行上游8个现成应用；原多节点图不再强制逐节点写回DDR。 |
| 07，72项 | 保留N1024/2048/4096/8192、原level和编号；重新生成全部程序与数据，计时端点不变。 |

旧用例源码可复用不等于旧生成包可混用。04～07的机器码、内存镜像、DMA清单和golden必须来自同一新提交。默认仍是00～07单个`hpu.zip`，只含ELF和BIN，不增加包数或重复版本。

## 已适配的接口差异

- NTT参数ABI由v2升级v3，stage和pre/post参数均为两行。普通完整向量PMUL仍合法，但不能把新的两行因子模板当成N项向量使用。
- 对象PMUL新增mode=1；立即数分支仍使用完整imm8，不能把64、192、255的立即数字段误判成online mode。
- post模板已经包含N⁻¹，不另加一次归一化。参数对象不得与数据/目的对象重合。
- operation graph的每个节点必须显式声明布尔`exported`。接收器核对mark_output、final_output、golden标识与完整输出limb集合；只允许不导出内部值，不允许漏检任何声明输出。
- 性能适配器精确接受上游online PMUL长度检查，将其留在preflight；固定单asm及机器字保持原文。计时仍为开始发令→CPU观察完成，包含DMA和轮询，不包含参数检查、数据准备、golden比较及UART。

## 同输入对照：07_39 CKKS HMUL+Reline，N4096/Q4/P1

Q/P、seed和输入Fixture相同，8个最终结果limb逐字节一致：

| 项目 | 旧9686076 | 新3ab94da |
|---|---:|---:|
| HPU指令 | 2701 | 1829 |
| DMA笔数 | 921 | 511 |
| DLOAD字节 | 4600064 | 1685760 |
| DSTORE字节 | 950272 | 131072 |
| DDR golden limb | 20（含tensor） | 8（最终输出） |

tensor仍由host生成器与独立Fixture严格对拍，只是不再为了目标端诊断导出。以上是实际指令/传输统计，不是硬件cycle或加速比结论。

## 验证与硬件边界

本轮验证包含：新编码器、NTT/在线因子物理模型、指令执行模型和fixed executable的官方核心测试；真实含50条在线PMUL的07_39包通过RV32/RV64×O0/O2×固定入口/寄存器压力共8项交叉编译检查；完整170项按统一构建器重新生成、模型校验和RV64编译，07还校验实际ELF计时边界。每次交付的最终状态以对应构建日志为准。

另对保留的6项手动Evaluator示例（CKKS/BFV/BGV×N128/N4096）完成native生成、严格模型、接收与真实ELF/BIN编译，未增加到默认包；HMUL的optimized/noopt两种手动路径也均通过新接收合同，最终导出各为8个limb。

依赖的ISA名称仍是`hpu-objects64-v1.2`，不能只凭该名字认定RTL支持在线PMUL。新版变换序列必须匹配已实现对象PMUL mode=1的RTL。本轮没有运行RTL/FPGA，也没有覆盖该新增模式的全部硬件非法输入边界；00_01的hold和00_11的预期失败性质不变。未迁移的LegacyAuto、特定TB故障注入和boot等项目继续不进入默认包。
