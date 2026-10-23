# HPU运行用例

当前只交付一个短名`hpu.zip`，按`00/`～`07/`分目录，每个用例保留`.elf`和`.bin`。压缩包不夹带源码、独立golden、反汇编、构建日志或重复的静默/子项版本。

本目录`make`已恢复为新版统一构建入口，转交[新版运行包构建器](../hpu_frontend_workload/scripts/build-runtime.py)，不会调用历史340项流水线。默认依赖是`tests/hpu_frontend_workload/third_party/inline-asm`，固定提交`3ab94da`；旧缓存不能混入当前包。原用例的复用范围与新增硬件要求见[兼容性检查](../hpu_frontend_workload/COMPATIBILITY.md)。

## 分组与状态

| 组 | 内容 | 当前范围 |
|---|---|---|
| 00 | 冒烟、波形hold与终止探针 | 11项 |
| 01 | 配置、连接与数据通路 | 8项 |
| 02 | 边界与CPU交互 | 16项 |
| 03 | 基本指令与单stage变换 | 9项；NTT/INTT使用新版原地更新及两行K8参数 |
| 04 | 基本与组合算子 | 9项：BConv、整体NTT/INTT、三算法KeySwitch |
| 05 | 算法库 | 37项：三算法库操作和correction factor/旋转参数回归 |
| 06 | 完整应用 | 8项：复用上游应用；x²+1为N8192，其余保留N128 |
| 07 | 性能用例 | N1024、N2048、N4096、N8192各18项，共72项；输入level≤4 |

当前默认170项。00～03组44项完成现代ISA构建及机器字核对，单stage的12轮独立C参考与上游物理模型一致；04～06组54项完成严格模型、原生包及ELF/BIN构建检查。07组72项还核对实际ELF计时区间。上述均不是硬件或RTL通过证明；交付状态为`BUILD_READY_NOT_IT_PASS`。

00组保留原资格：`00_01_dload_hold`故意持续运行，`00_10_return_0`与`00_11_return_1`分别测试返回0和返回1；不能把全部用例都当作应返回0的自检。02组旧watchdog依赖用例及未实现用例不进入默认包。

`04_10_legacy_auto_n4096`依赖旧专用Auto/twiddle合同，尚未迁移到本次64对象/K8版本，不用普通Rotate冒充，源码仍保留。boot等未实现项、依赖外部TB的故障注入和超过参数上限的历史用例也不进入运行清单。

## 构建

```sh
# 默认全部组，输出单个hpu.zip。
make -C tests/hputest

# 只导出一个组或一个原case_id。
make -C tests/hputest group GROUP=07
make -C tests/hputest one CASE_ID=03_05_pntt
```

可覆盖`OUTPUT_ROOT`、`AM_HOME`、`ARCH`、`CROSS_COMPILE`、`JOBS`和`INLINE_ASM_ROOT`。默认输出目录为`tests/hpu_frontend_workload/build-runtime`；默认平台`riscv64-xs`、工具链前缀`riscv64-linux-gnu-`。`one CASE=03_05_pntt`仅作为`CASE_ID`的兼容写法，不再接受历史源码路径形式。

源码和CPU测试仍保留在仓库。旧主线可从`backup/master-before-1019-20261023`（`9016ef9c`）回查；旧入口与完整旧说明另存于[历史归档](archive/20261023-runtime-delivery/README.legacy.md)，不作为当前构建指南。
