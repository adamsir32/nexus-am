# 05组：SEAL算法库验证

当前15项，仅N1024、输入level4：CKKS/BFV/BGV各五种操作。

| 操作 | CKKS参考API | BFV/BGV参考API |
|---|---|---|
| HADD | add | add |
| HMUL+Reline | multiply后relinearize | multiply后relinearize |
| Reline | relinearize | relinearize |
| 降level | rescale_to_next | mod_switch_to_next |
| Rotate | rotate_vector | rotate_rows |

每项源码在`src/05_library/<case_id>.c`，同名ASM为完整发令序列。参考仍来自固定inline-asm的modified-SEAL，不使用系统SEAL/Poseidon；逐原始物理word和metadata严格比较，不能以解密近似相等放行。

level指输入Q分量数4，不含P，也不是chain_index。降层操作输出可以为Q3，不能因此把输入参数标成level3。精确模数、scale、密钥、CF、旋转步长及布局取自本次原生包。

04只验证基本算子与KeySwitch核心；05验收完整密文库操作，不能因共享指令链混为一组。原N128/N2048/N4096/N8192及不同level、特殊CF/step1回归已按要求删除源码，不保留占位。

算法/rounded-P沿用固定上游实现。末尾一次PSYNC→CPU外部中断，ISR清电平并完成PLIC claim；主程序确认一次真实事件、VALID/非BUSY/无fault，再检查全部输出及只读区/guard。不能只读MMIO完成电平替代中断检查。软件模型和构建通过不代表RTL/FPGA通过。

```bash
make -C tests/hputest group GROUP=05 OUTPUT_ROOT=/disk/hpu/library
```

Poseidon仍独立在`tests/hpu-experiments/poseidon`，不进入默认IT。历史源码和旧编号分别从Git与`docs/case-id-migration.tsv`查。
