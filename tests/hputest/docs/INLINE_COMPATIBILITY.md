# Inline-asm兼容性

固定依赖仍为`feature/operator-resource-management@3ab94da16abce89b7e9b74f4e7fcd93604dea495`，不是自动跟踪main；本轮不改SDK或RTL。

当前默认交付109项，具体范围以`cases.tsv`为准。03～05为N1024/level4；07为N1024/N8192、三算法全level4；00～02与06保持原配置。独立C与旁侧ASM相互对应，不可混用不同批次机器码、DMA、内存镜像和golden。

## 仍需匹配的接口

- 64对象ISA，计算/控制物理opcode为0x5B，DMA为0x2B。
- NTT ABI v3：stage及pre/post模板均为两行；post已包含N⁻¹。
- 对象PMUL mode=1为online模式；立即数64/192/255不能误判为该模式。
- 完整导出结果必须全部检查；SSA留在片上的内部值不能被误当成漏检最终结果。
- 07参数检查在计时前，固定发令路径和x11复用保持，计时包含DMA与完成轮询。

BGV性能从Q3改为Q4，原L3周期数不能直接继承或作为同参数加速比较。其metadata会标记与旧基线参数不相等；CKKS/BFV仍使用原L4配方。所有方案仍要求独立golden和软件模型精确通过，不降低检查标准。

之前大矩阵、N4096指令定向和特殊回归的源码已按当前范围删除，历史可从Git查。软件验证不表示上述模式已在当前RTL/FPGA通过，必须记录并使用匹配的实际硬件版本。
