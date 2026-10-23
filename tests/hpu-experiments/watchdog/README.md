# Watchdog条件实验，不属于默认IT

本目录保留核侧HPU命令握手超时和缺依赖阻塞的历史诊断；不在
`tests/hputest/cases.tsv`、默认Actions或`hpu.zip`中。
本次只移动文件并修正显式路径/参数，未编译AM、未运行TB、未修改CPU或RTL。

## 适用条件

历史C源码中的假设来自IT-SCPU-RTL的特定版本：入口连续反压500000个CPU周期后
fail-stop、故障码1、后续HPU指令停发，以及特定controller依赖阻塞行为。
头文件仍保留这些原始判据，不代表当前最新RTL已经支持同样接口。
旧诊断脚本曾以`0cfd995302af926aa22767e145aade9fc9d21ca2`为基线，
现在必须显式指定`--ref`，先核对所选RTL文件、故障CSR、时钟和ISA。

没有DLOAD就计算、未COMMIT就发令等刺激不是通用的“合法卡住HPU”接口。
只有选定设计明确规定阻塞/故障语义时才可启用；不得从某次仿真现象反推接口。

## 保存的内容

- `src/02_17_watchdog_failstop.c`：未提交窗口制造入口反压的条件负向测试；
- `src/02_18_watchdog_compute_before_dload.c`：计算先于数据装载的依赖阻塞实验；
- `src/02_19_watchdog_pmodld_before_dload.c`：PMODLD先于模表装载的依赖阻塞实验；
- `include/hpu/watchdog.h`、`watchdog_data.h`：仅供这三个历史实验使用；
- `scripts/test-watchdog-rtl.py`及`watchdog_merge_tb.sv`：独立入口看门狗TB；
- `scripts/test-watchdog-dependencies-rtl.py`及`watchdog_dependencies_tb.sv`：独立依赖阻塞TB。

原02编号只是历史称呼，不占用当前默认02组编号。

## 手动诊断入口

先准备匹配RTL仓库和本轮真实编码器生成的低层头，再显式运行：

```sh
python3 scripts/test-watchdog-rtl.py --rtl-repository /path/to/rtl --ref MATCHED_COMMIT
python3 scripts/test-watchdog-dependencies-rtl.py --rtl-repository /path/to/rtl --ref MATCHED_COMMIT --generated-root /path/to/generated
```

脚本只从指定Git版本读取RTL，在本目录`build`下写诊断产物，不修改RTL仓库。
TB通过也不等于CPU/DMAC/NoC整机IT已通过。

三个AM实验尚无当前统一构建入口。手动接入时，应把本目录`include`放在
`tests/hputest/include`之前，引用匹配的生成头和fixture，并独立复位每个ELF；
不得将它们重新塞进默认低层44项或当作普通正常完成用例。
