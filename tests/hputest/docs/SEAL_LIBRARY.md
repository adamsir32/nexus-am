# 05组：inline-asm/modified-SEAL算法库验证

参考库来自`producer.json`与gitlink固定的inline-asm提交`3ab94da16abce89b7e9b74f4e7fcd93604dea495`，分支为`feature/operator-resource-management`。使用它自带的`third_party/modified-SEAL`和HPU顶层接口，不使用系统SEAL，也不调用Poseidon。不能把此实验分支写成main。

## 04与05的边界

04检查整体NTT/INTT、BConv和KeySwitch核心。05以完整密文库操作为验收边界；KeySwitch隔离切换分量，而Reline保留并合并完整密文，不能因共享底层指令而视为同一用例。

| 操作 | CKKS参考API | BFV/BGV参考API |
|---|---|---|
| HADD | `Evaluator::add` | `Evaluator::add` |
| HMUL+RELINE | `multiply`后`relinearize` | `multiply`后`relinearize` |
| RELINE | `relinearize` | `relinearize` |
| 降level | `rescale_to_next` | `mod_switch_to_next` |
| ROTATE | `rotate_vector` | `rotate_rows` |

05默认287项：280个有效N/level/算法/操作组合，另7项特殊参数回归。每项在`src/05_library/<N目录>/<case_id>.c`有独立完整main，特殊回归在`06_parameter_regression`；同名`.asm`保存完整发令序列并在构建时核对。每场景独立生成ELF，不把多个N/level串成一轮。唯一清单仍为`cases.tsv`，不另维护第二份参数清单。

N取128、1024、2048、4096、8192；level是输入Q基的RNS分量数1～4，既不是SEAL chain_index，也不包含KeySwitch特殊P。降层算子的L1没有下一层；上游BFV HMUL也明确要求至少两个活动Q。这20个组合写在`docs/unsupported-parameters.tsv`，不产生伪可运行用例。

规范profile保留CF1/1、N/4旋转及固定输入种子；不同level实际生成相应子基，CKKS scale受当前Q容量约束。7项特殊回归保留BGV CF3/5、CF15、CF3及三方案step1旋转，不当成重复项删除。精确模数、scale、密钥和物理布局从生成包metadata读取。

## 参考与目标检查

上游HPU软件执行器必须逐原始物理word匹配modified-SEAL；AM接收器检查完整输出集合、程序/DMA/布局一致性，并保留只读区和guard自检。BFV也不允许以“解密明文相同”放行原始word不匹配。

rounded-P等算术沿用上游实现，不在AM另加取整指令或half-P数据。SSA可将内部tensor留在片上，但所有显式导出结果必须完整检查，不以减少导出诊断值为由漏检最终结果。

每段完整程序DSTORE后只有一次PSYNC，通过MMIO观察完成且BUSY清零，不启用PLIC/timer。软件模型、包验证与编译通过不等于IT/VCS或FPGA通过；这些demo参数不作为安全部署承诺。

## 构建与实验

```bash
git submodule update --init --recursive tests/hputest/third_party/inline-asm
make -C tests/hputest group GROUP=05 N=8192 LEVEL=4 \
  OUTPUT_ROOT=/disk/hpu-library
```

默认Actions仅发布00～07的单一ELF+BIN集合。生成包、golden和中间模型报告留在构建目录，不混进下载包。

Poseidon源码和桥接试验单独放在`tests/hpu-experiments/poseidon`，不由默认CMake/Makefile/Actions构建，也没有因本轮整理而宣称验证通过。旧用例编号映射见`docs/case-id-migration.tsv`，旧源码从Git历史查。
