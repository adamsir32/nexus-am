# Inline-asm兼容性

固定依赖为`feature/compute-profiling@4e26659cc0c9c3887c60491e8455ff5fd6028025`。上游main已合入原资源管理与布局修复；本轮选择官方连续计时分支，不修改SDK或RTL。

当前默认交付109项，具体范围以`cases.tsv`为准。03～05为N1024/level4；07为N1024/N8192、三算法全level4；00～02与06保持原配置。独立C与旁侧ASM相互对应，不可混用不同批次机器码、DMA、内存镜像和golden。

## 仍需匹配的接口

- 64对象ISA，计算/控制物理opcode为0x5B，DMA为0x2B。
- NTT ABI v4：系数域每个RNS分量物理下标j保存自然下标BR_N(j)，pre/post在线模板按上游专用U/V/R packer生成，不能沿用自然顺序镜像。stage及pre/post模板仍均为两行；post已包含N⁻¹。
- 对象PMUL mode=1为online模式；立即数64/192/255不能误判为该模式。
- 完整导出结果必须全部检查；SSA留在片上的内部值不能被误当成漏检最终结果。
- 03～06保持末尾PSYNC的CPU外部中断；配置COMMIT及显式MMIO测试仍可轮询。07使用官方profiled回调，预载与主体边界及最终同步均确认新IRQ事件，非最终边界只rearm；不重复CTE初始化，不重置SRAM。

ISA和NTT ABI v4未变；普通程序默认profile_execution=false，03～06仍核对原旁侧ASM。07由官方资源编译器前置安全预加载并插入窗口边界PSYNC，必须同步本批.asm/.noopt.asm与其原生镜像、DMA及golden，不能只换C入口。回调后每个asm块重新建立x10/x11值，不套用旧单asm预检查提取器。新计时口径不能沿用旧端到端样本。03_08的三种前序各两轮回归仍独立保留。

BGV性能从Q3改为Q4，原L3周期数不能直接继承或作为同参数加速比较。其metadata会标记与旧基线参数不相等；CKKS/BFV仍使用原L4配方。所有方案仍要求独立golden和软件模型精确通过，不降低检查标准。

之前大矩阵、N4096指令定向和特殊回归的源码已按当前范围删除，历史可从Git查。软件验证不表示上述模式已在当前RTL/FPGA通过，必须记录并使用匹配的实际硬件版本。
