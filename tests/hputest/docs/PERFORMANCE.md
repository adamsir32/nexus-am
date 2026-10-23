# 07组性能口径

07是算法库/KeySwitch代表性性能测试，不替代03～05的N/level功能覆盖。N1024、2048、4096、8192各18项，共72项；每个N包含三方案的KeySwitch、HADD、HMUL+Reline、Reline、Rescale/ModSwitch、Rotate。原参数保持：CKKS/BFV输入Q4，BGV输入Q3，特殊P均不计入输入level。

所有参数来自唯一`../cases.tsv`，源码只有`../src/07_performance/main.c`一份，每个ELF仍固定一个N/level和一个算子程序。不同测试在用例外并行，不在单个ELF串行重复多个参数。

## cycle记录

1. 计时前：准备并clean镜像、参数preflight、配置MMIO、COMMIT并等配置生效。
2. `cycle_start=perf_cycle_read()`。
3. 执行上游固定发令入口，包括DLOAD、HPU计算、DSTORE及末尾唯一PSYNC。
4. 轮询IRQ/VALID/BUSY并检查fault，CPU观察到完成后读`cycle_end`。
5. 计时后清完成电平，核对全部声明导出的golden、只读区和guard，成功才输出`verified=1`。

底层是`fence rw,rw; rdcycle`，不是循环次数。`mcounteren`开放cycle访问权限，不是打开timer中断。区间包含CPU发令、DMA、计算及完成轮询，不是纯HPU内核cycle，也不包含数据准备、preflight、golden比较或UART。`workload_trace.wait_cycles`只反映等待部分，不能混当完整`cycles=end-start`。

上游固定单asm原样保留，x11只在DMA长度变化时重载。在线PMUL长度检查留在计时前，不在发令路径插桩；真实ELF门禁检查所有成功路径的调用及两次rdcycle顺序。stage和pre/post参数均使用NTT ABI v3的两行模板，必须匹配新版RTL。

## 构建和统计

```sh
make -C tests/hputest performance OUTPUT_ROOT=/disk/hpu/perf
make -C tests/hputest performance N=8192 SCHEME=ckks OUTPUT_ROOT=/disk/hpu/perf-8192-ckks
make -C tests/hputest performance VARIANT=noopt OUTPUT_ROOT=/disk/hpu/perf-noopt

python3 tests/hputest/scripts/parse_performance.py run1.log run2.log \
  --output /disk/hpu/results \
  --revision 'AM=<本批commit>; inline-asm=3ab94da; RTL=<实际commit>'
```

默认optimized，noopt只影响07调度且单独显式构建；不默认打四份包。关闭UART可用`LOG_LEVEL=0`，cycle端点仍写入`workload_trace`，但解析器不会将不存在的UART性能行伪造成样本。

解析器仅接受当前清单中N/level完全匹配、端点差一致且`verified=1`的实际记录；输出逐轮样本和平均、最小、最大、波动。不同AM/RTL版本不得混合平均。`noopt_over_optimized`是同参数调度比较，不是CPU/HPU加速比。

CPU对比必须使用相同Q/P、输入、scale、correction factor、旋转步长和结果；按实际测量的`Cycle_CPU/Cycle_HPU`计算。不得将host模型耗时或指令/DMA条数当作硬件cycle。本轮仅验证构建/模型，真实RTL/FPGA性能待运行记录。
