# 日志与静默构建

统一构建器默认`LOG_LEVEL=1`：短开始/结束摘要、失败阶段/状态/首错，不打印每个成功系数。03保留定向用例额外报告子项身份；正常阶段保留RAM trace。07每个ELF只有一轮，正确性检查通过后统一打印cycle起止及差值，计时区间内不打印。

`LOG_LEVEL=0`关闭目标程序UART输出，保留相同发令、同步、golden、guard、计时和退出行为。静默07仍保存`workload_trace.cycle_start/cycle_end`，但没有可解析的UART性能数值；需要收集数值时用默认版本。普通00～06不因阶段日志额外采样cycle。关闭日志不求值实参，测试步骤不放入日志宏。

## 下载与本地构建

Actions只交付一个`hpu`运行集合，按00～07目录放ELF+BIN。默认不混装silent、全量诊断或重复版本，也不把源码和golden放进下载包。

```bash
# 默认短日志；输出目录必须是新目录
make -C tests/hputest all OUTPUT_ROOT=/disk/hpu-minimal

# 按需单独生成无UART包，不与默认交付混装
make -C tests/hputest silent OUTPUT_ROOT=/disk/hpu-silent

# 也可筛选同一参数/单例
make -C tests/hputest one CASE_ID=03_010_padd_l1_n128 LOG_LEVEL=0 \
  OUTPUT_ROOT=/disk/hpu-one-silent
```

内部低层日志头还支持按需详细诊断宏，但统一交付入口只接受0/1；旧`diagnostic/subtests/unified`构建和多包拼装入口已删除，不再作为当前用法。

## 结果判定

静默只影响ELF中的UART，不关闭仿真器自己的日志。构建器检查无输出空桩及最终ELF停止指令，不修改公共AM/klib或RTL。有限用例仍通过`main()`返回0/非0上报结果；无日志、进程exit0或耗尽cycle预算都不能单独算PASS。

`00_01`发令后无限保持、`00_11`故意返回1的探针仍维持特殊验收方式。日志减量不意味着这些探针会正常PASS，也不意味着运行过RTL/FPGA。若静默仍超时，应区分计算、等待和硬件故障，不删自检或无限加预算。
