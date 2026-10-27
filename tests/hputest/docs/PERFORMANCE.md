# 07组性能口径

07保留36项：N1024与N8192各18项；每个N包括CKKS/BFV/BGV的KeySwitch、HADD、HMUL+Reline、Reline、Rescale/ModSwitch、Rotate。所有输入level均为4，不含特殊P。

BGV不再沿用原Q3基线：当前显式生成Q4/P1，重新生成输入、评估数据、程序及SEAL golden。其metadata标明与旧L3基线参数不相等；不能把旧L3性能或通过结论记到新L4用例上。CKKS/BFV保持原L4参数配方。

## 官方连续窗口与独立源码

源码位于`src/07_performance/01_n1024/<case_id>.c`或`02_n8192/<case_id>.c`；同名`.asm`与`.noopt.asm`分别保存两种调度的实际序列。每项ELF只运行一次，不串行混装多个参数。

1. main准备/clean镜像，配置MMIO并等COMMIT生效；武装CPU/PLIC外部中断，确认旧事件数为0，绑定官方hooks。
2. 具体`hpu_run_<stem>_profiled(&state.hooks,&sample)`执行上游安全前置的输入、密钥、常量和twiddle预加载及原有entry准备IO，PSYNC完成后通过clock hook读取start。
3. 同一连续窗口执行全部算术、必要DLOAD/DSTORE、spill/reload及保留的中途同步；主体末PSYNC完成后通过clock hook读取end。
4. 继续执行原来已在最后算术之后的尾部写回、释放与最终同步。只有完整程序成功，官方入口才设置`sample.valid=1`。
5. main关闭IRQ，验收sample、两次clock及全部PSYNC累计事件数，核对终态并比较全部golden/只读区/guard；通过后才打印`verified=1`。

底层为`fence rw,rw; rdcycle`，不是循环次数。`mcounteren`开放cycle访问，不开启timer中断。新指标为`execution_window_irq_v1`、`completion=plic_irq`、`profile=continuous`，包含主体发令、全部算术、残余DMA、clock hook及完成回调/ISR/rearm开销，不是无DMA纯计算。数据准备、首次IRQ配置、前置预加载及原有尾部写回、golden/guard比较和成功UART输出不在窗口内。失败回调可能打印诊断，该样本无效，不能进入统计。

只采用上游`CompileOptions.profile_execution=true`，不自行提前DMA或延迟中间输出。官方C按PSYNC分asm块，回调后重新设置x10/x11，不跨调用错误复用长度寄存器。每次wait严格匹配从0递增的sync_index，ISR仍claim source257、W1C清电平并complete，非最终边界只rearm，不重新CTE初始化或清空SRAM。仅MMIO电平不能冒充完成。

窗口以官方`profiling/execution_window.csv`为准。接收器核对全部算术都在窗口内、窗口DMA计数、与原调度相比未增加DMA、每PSYNC回调及两端时间戳，直接编译原生C/H而不提取或复制计算片段。ELF门禁再检查实际机器字、回调绑定、两次读clock、尾部完成后valid及最终自检路径。NTT数据ABI仍为v4，指令编码未变；07顺序及新增边界PSYNC必须使用本批旁侧ASM。

## 构建与统计

```bash
make -C tests/hputest performance OUTPUT_ROOT=/disk/hpu/perf
make -C tests/hputest performance N=8192 SCHEME=bgv OUTPUT_ROOT=/disk/hpu/bgv-8192
make -C tests/hputest performance VARIANT=noopt OUTPUT_ROOT=/disk/hpu/noopt
python3 tests/hputest/scripts/parse_performance.py run1.log run2.log \
  --output /disk/hpu/results --revision 'AM=<本批commit>; inline-asm=4e26659; RTL=<实测commit>'
```

默认optimized；noopt单独显式构建，不打重复默认包。静默版本保留RAM中的cycle端点，但不输出UART性能样本。

日志另打印`window_dload_count`、`window_dstore_count`、`prefix_dload_count`、`prefix_dstore_count`、`suffix_dload_count`、`suffix_dstore_count`及`sync_count`，直接取实际交付窗口，不把残余DMA隐藏成0。BFV noopt KeySwitch/Reline的原调度在首条算术前已有一次workspace DSTORE，官方窗口仍排除这项准备写；接收器保留并单列统计，不把它误当新增输出写、改动计时边界或静默记0。解析器只接受新metric/profile、当前编号与N/level匹配、端点差一致且`verified=1`的日志；旧`issue_to_irq_done_v1`和`issue_to_done_v2`会被拒绝，不能混算。

不同AM/RTL/参数不得混合平均；`noopt_over_optimized`是调度对照，不是CPU/HPU加速比。CPU对比须使用相同实际Q/P、输入、scale、CF、旋转参数及计时范围。预加载和边界同步可能改变IO/计算重叠，不能用新旧窗口耗时相减推算独立DMA时间。模型耗时不能当硬件cycle，未实测不填写加速比。
