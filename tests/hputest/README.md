# HPU IT用例

活动源码、依赖和构建只保留本目录一份。[cases.tsv](cases.tsv)是唯一用例清单，负责编号、参数、用途、入口及构建选择。旧`hpu_frontend_workload`只转发命令，不再保存另一套源码。

默认导出一个`hpu.zip`，按00～07分组，仅含ELF和BIN；不夹带源码、独立golden、反汇编或重复版本。inline-asm固定在[producer.json](producer.json)，目前是`feature/operator-resource-management@3ab94da`。

## 分组

| 组 | 范围 | 默认数量 |
|---|---|---:|
| 00 | 冒烟、波形hold、退出探针 | 11 |
| 01 | 配置、连接与数据通路 | 8 |
| 02 | 边界与RISC-V交叉 | 16 |
| 03 | 9项定向指令测试＋180项多N/RNS指令矩阵 | 189 |
| 04 | BConv、整体NTT/INTT、三算法KeySwitch | 120 |
| 05 | 三算法库操作参数矩阵＋7项特殊参数回归 | 287 |
| 06 | 上游完整应用；另有6项可选API回归 | 8 |
| 07 | 既定代表参数下的算法库/KeySwitch性能测试 | 72 |
| 合计 | 不包括可选API与独立实验 | 711 |

03～05覆盖N=128、1024、2048、4096、8192及输入level=1～4。N是多项式长度，level是实际输入Q的RNS分量数量，不是SEAL的内部链编号，也不包括特殊模数P。03会真实加载和切换不同模上下文；不是只改参数标签。N128及低level属于诊断/边界参数，不构成精度、安全性或性能达标证明。

L1不生成Rescale/ModSwitch，BFV HMUL也需要至少两个active Q；20个不支持组合明确列于[参数限制](docs/unsupported-parameters.tsv)，不以空程序或伪PASS补数。其他支持的L1操作正常覆盖。

07用于端到端cycle测量，不代替03～05功能参数覆盖。为保留既有性能对照，其CKKS/BFV输入L4、BGV输入L3；包含N1024/2048/4096/8192，不在本轮改变这些代表参数。

## 命名和源码位置

用例名为`组号_组内号_行为[_lL_nN]`。00/01/02/06/07使用两位组内号；03/04/05超过99项，统一三位号，例如`03_010_padd_l1_n128`、`05_001_ckks_hadd_l1_n128`。矩阵按N升序、再按level升序；03定向场景、05特殊参数回归分别作为独立profile。历史编号对照只用于查旧日志，见[编号迁移](docs/case-id-migration.tsv)，不会参与构建。

```text
src/00_smoke/、01_connection/、02_boundary/  定向C场景
src/03_instructions/directed/              原9项指令定向场景
src/03_instructions/、04_operators/、05_library/、06_applications/
                                          各组薄入口，共用native_case_run
src/07_performance/main.c                  共用计时入口
runtime/native/                           图像准备、MMIO同步、自检
tools/instruction_cases/                   指令矩阵与独立数学/C oracle
tools/group_cases/                         算子/库图，直接复用上游API
tools/common/fixture.hpp                   三算法共享输入、Q/P和golden参数
scripts/build-runtime.py                   唯一调度器
third_party/inline-asm/                    唯一活动生产依赖
```

一个ELF只处理一个N/level场景，不串行跑不同参数。03内部的别名、立即数、stage及生命周期子场景属于该条指令的必要检查；CPU端不重算大型FHE golden。03～07不再复制数百份仅参数不同的main。

## 使用

```sh
git submodule update --init tests/hputest/third_party/inline-asm

# 查看清单，不生成文件。支持GROUP/N/LEVEL/SCHEME筛选。
make -C tests/hputest list GROUP=05 N=8192 LEVEL=4

# 每次使用新的磁盘输出目录；一次得到一个hpu.zip。
make -C tests/hputest all OUTPUT_ROOT=/disk/hpu/all
make -C tests/hputest group GROUP=05 N=8192 LEVEL=4 OUTPUT_ROOT=/disk/hpu/05-n8192-l4
make -C tests/hputest one CASE_ID=03_010_padd_l1_n128 OUTPUT_ROOT=/disk/hpu/03-010

# 可选顶层API诊断，不混入默认711项；关闭UART仍保留全部检查。
make -C tests/hputest api OUTPUT_ROOT=/disk/hpu/api
make -C tests/hputest silent OUTPUT_ROOT=/disk/hpu/silent
```

`VARIANT=noopt`只影响07调度；正常交付默认optimized。可用`WAIT_CYCLES`设置完成等待预算，仿真器自己的cycle上限也须足够。失败任务可在同一源码、清单、参数下使用`RESUME=1`继续；已有成功包不覆盖，旧缓存不能冒充当前版本。

默认只打印简短开始/结束和错误，阶段继续写入RAM中的trace，失败时输出出错阶段及状态。长用途说明通过`make list`查看，不逐系数刷UART。07计时区间无UART、数据准备或golden比较，口径见[性能说明](docs/PERFORMANCE.md)。

## 检查与交付边界

`make test`运行契约单测；`make audit`检查自有源码引用、连续编号、N/level顺序和范围、重复参数与孤立案例，报告写到输出目录。源码整理结果见[审阅记录](docs/SOURCE_REVIEW.md)。

上游CPU/FHE模型、原生包、实际ELF机器字、guard和计时门禁属于构建验证，不是RTL/FPGA实测。新生成程序需要支持在线PMUL mode=1与NTT ABI v3的RTL；更新背景见[兼容性说明](docs/INLINE_COMPATIBILITY.md)。

`00_01_dload_hold`故意保持运行，`00_11_return_1`是预期失败退出探针，不能按“所有ELF必须返回0”汇总。boot占位、未迁移LegacyAuto、外部RTL注入不伪装成默认已实现用例。Poseidon和条件watchdog已独立放到`tests/hpu-experiments/`，不参与当前IT构建或通过统计。

历史源码从Git回查，不在当前树再留archive副本。此前依赖快照及硬件通过版本缺失项保留在[历史基线](docs/HISTORICAL_BASELINE.json)，不把用户报告的通过范围自动扩充成已确认的RTL版本。
