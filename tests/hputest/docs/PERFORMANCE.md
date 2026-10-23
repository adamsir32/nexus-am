# 07组性能口径

07保留36项：N1024与N8192各18项；每个N包括CKKS/BFV/BGV的KeySwitch、HADD、HMUL+Reline、Reline、Rescale/ModSwitch、Rotate。所有输入level均为4，不含特殊P。

BGV不再沿用原Q3基线：当前显式生成Q4/P1，重新生成输入、评估数据、程序及SEAL golden。其metadata标明与旧L3基线参数不相等；不能把旧L3性能或通过结论记到新L4用例上。CKKS/BFV保持原L4参数配方。

## 独立源码与计时

源码位于`src/07_performance/01_n1024/<case_id>.c`或`02_n8192/<case_id>.c`；同名`.asm`与`.noopt.asm`分别保存两种调度的实际序列。每项ELF只运行一次，不串行混装多个参数。

1. 计时前准备/clean镜像，做preflight，配置MMIO并等待COMMIT生效。
2. `cycle_start=perf_cycle_read()`。
3. 具体发令入口执行DLOAD、计算、DSTORE及末尾唯一PSYNC。
4. CPU轮询观察IRQ有效、VALID有效、BUSY清零且无fault，随后读`cycle_end`。
5. 停表后清电平，检查所有golden、只读区及guard，通过才输出`verified=1`。

底层为`fence rw,rw; rdcycle`，不是循环次数。`mcounteren`开放cycle访问，不是开启timer中断。指标`issue_to_done_v2`包含CPU发令、DMA、计算和完成轮询，不是纯HPU核心cycle；不包含准备、参数检查、golden/guard比较及UART。

固定单asm、x11复用和NTT ABI v3保持；错误分支在计时窗外带具体C文件/行号。实际ELF门禁核对所有成功路径的两次读cycle及调用顺序。

## 构建与统计

```bash
make -C tests/hputest performance OUTPUT_ROOT=/disk/hpu/perf
make -C tests/hputest performance N=8192 SCHEME=bgv OUTPUT_ROOT=/disk/hpu/bgv-8192
make -C tests/hputest performance VARIANT=noopt OUTPUT_ROOT=/disk/hpu/noopt
python3 tests/hputest/scripts/parse_performance.py run1.log run2.log \
  --output /disk/hpu/results --revision 'AM=<本批commit>; inline-asm=3ab94da; RTL=<实测commit>'
```

默认optimized；noopt单独显式构建，不打重复默认包。静默版本保留RAM中的cycle端点，但不输出UART性能样本。

解析器仅接受当前编号与N/level匹配、端点差一致且`verified=1`的日志。不同AM/RTL/参数不得混合平均；`noopt_over_optimized`是调度对照，不是CPU/HPU加速比。CPU对比须使用相同实际Q/P、输入、scale、CF和旋转参数，并按相应时钟/耗时口径比较；模型耗时不能当作硬件cycle。未实测不填写加速比。
