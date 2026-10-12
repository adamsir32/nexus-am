# inline-asm主线03a32c1接入

本次稳定算子/应用依赖升级为`03a32c168404f3ad64e6a4d7ad82a081f910314b`，对应上游`fix: restore rounded single-P CKKS KeySwitch`。重构API仍在独立实验workload中，不把未合入main的API/NTT合同混到原算子回归。

## 升级前基线

[INLINE_BASELINE.json](INLINE_BASELINE.json)记录升级前AM及全部依赖的精确commit：算子/应用采用`c11dfe2`，旧固定参数指令/fixture采用`legacy-main@6903096`。用户报告算子层级已跑通，但没有提供那次硬件运行的AM、RTL、下载包revision，因此这里不伪称当前HEAD就是该次实测版本。

需要回退时，在干净工作区从`63e8aac32b4aac376dc729d51ab39601f23b2e66`新建回归分支，再按该提交初始化submodule并重新生成独立下载包。不重置或删除现有工作区，也不混用升级前后的随机密钥、镜像和golden。

## 取整来源

上游`CkksApplicationImageBuilder::add_keyswitch_constants()`生成每个Q/P上下文的`hardware/half/mod<ID>`常量；`operation_relocation.cpp`为两个accumulator分量分别绑定load-half、PADD和写回。Relinearize、Rotate/Conjugate以及融合Multiply在合法SEAL单P布局下调用上游rounded-single-P核心。

AM不再插入PADD取整链、不生成half-P数据、不调用编码器重编码这批指令。ASM、INST32、CMD26和头文件取自同一份上游交付，golden仍是modified-SEAL；接收记录的`ckks_rounded_p_instructions_added`必须为0。

保留两项目标端接收职责：BFV系数域的目标物理排列，以及CKKS对只读输入/逐节点output的workspace重定位。上游已声明为可写的workspace可按其原指令原地使用，不额外复制；重定位只调整DMA span和window上界，不改变数学指令或word数。全部交付仍须逐指令模型回放通过，并检查只读区/guard。

## 编号

04组目录由`01_composite_operators`、`03_instruction_sequence_orchestration`改为连续的`01`、`02`。原`HPU_IT_*`测试点ID保持不变，避免把目录序号与历史测试点编号混淆。清单和下载路径同步更新，新增目录连续性回归。

本次构建/host模型通过不等于VCS硬件通过；上游升级后的IT仍需使用新下载包回归。
