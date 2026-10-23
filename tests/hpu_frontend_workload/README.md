# HPU新API工作负载（当前主线交付）

当前默认主分支实际名为`master`，HPU交付采用原`1019-operator-resource-perf`的本目录：36项新07性能测试及六个API应用，N≤8192、输入level≤4。旧`hputest`构建入口及大矩阵已退役，目录中的历史源码和公共支持仍保留，不再生成旧HPU包。

迁移前主线完整备份在`backup/master-before-1019-20261023@9016ef9c`。需要旧00～07基线时切换该备份，不要在新主线上恢复旧构建入口。

依赖固定为`feature/operator-resource-management@9686076`，不是旧workload的main/legacy-main。完整commit见[producer.json](producer.json)。API和应用图直接采用该分支的`examples/*_evaluator_application.cpp`，不是用AM重新实现一套算法。

2026-10-21跟进NTT ABI v2：每stage使用在线K=8的512字节/2line参数，数据镜像及DMA spans全部由新版库重新生成，不能混用旧完整twiddle表。上游fixed发令入口的单asm和x11长度复用原样保留；接收器分别核对dynamic/fixed两套原生字码，实际ELF检查fixed入口。07专用适配器只提取计时前预检查，不重新生成发令序列。自动跟进机制本次未启用。

2026-10-23继续同步上游64对象ISA、DMA的MOD/REL/CP字段及twiddle-only LLC分配提示。交付数据和指令须由同一固定版本重新生成；CP是DMA指令字段，不是trace开关，不能为关闭打印而删除DMA。

本次`1019-operator-resource-perf`分支的[07组单算子性能实验](PERFORMANCE.md)只保留N4096/N8192、输入level≤4的36项活动用例；默认构建N8192，CKKS/BFV使用level4，BGV保留原level3。资源优化开启与关闭分别生成独立ELF。超过上限的36项level16用例保留在[历史归档](archive/20261023-level16/README.md)，不进入活动构建、CI或下载包，原编号不重新排列。下面原有六项应用仍为N128/N4096，不混入这次单算子性能比较，也未新增N8192应用入口。

## 用例

| 独立ELF | 应用 |
| --- | --- |
| CKKS_N128、CKKS_N4096 | `x × (RotateLeft(x,1) + Conjugate(x)) + 1`，显式reline/rescale |
| BFV_N128、BFV_N4096 | `x × (RotateRows(x,1) + RotateColumns(x)) + 7`，显式reline/modswitch |
| BGV_N128、BGV_N4096 | 同上，保留BGV的correction factor和模上下文 |

每个ELF只跑一个scheme、一个N、一张7节点应用图，不串行跑多个规模或重复轮次。图中的算子依赖仍必须按顺序执行。6个ELF可在用例外部分别并行仿真；不能把同一图的依赖节点任意分拆。

可读的main放在`src/`，CSR操作直接可见；共享数据搬运、同步、自检分别放在`runtime/image.c`、`wait.c`、`check.c`。大型producer生成C和数据仅位于忽略的build目录和下载包，不提交进Git。

## 构建与下载

```sh
git submodule update --init tests/hpu_frontend_workload/third_party/inline-asm
make -C tests/hpu_frontend_workload all
```

用例路径通过 `CASE_OBJ_DIR`、`CASE_BINARY` 传入，仅在 `Makefile.case` 本层映射为输出目录；不把公共 `DST_DIR`、`BINARY` 作为命令行变量传给递归 AM/klib 构建。`make test` 会执行变量隔离回归，验证实际构建命令不会污染递归构建的默认路径。

产物是`build/hpu-frontend-workload.zip`；GitHubActions的`build HPU frontend workload`工作流提供`nexus-am-hpu-frontend-workload`下载包，旧`nexus-am-hpu-tests`不再发布。

压缩包的`minimal/`、`silent/`各包含6套ELF/BIN/TXT。正常包只打印阶段、CSR错误、前4个结果错误及错误总数，不全量打印4096项。静默版关闭用例打印、AM启动UART初始化和字符出口，自检与return码不变；可读取`workload_trace`定位阶段和首错。

`delivery/<case>/upstream/`保留输入、密钥、twiddle、全部节点golden、语义解密报告、应用图、DMA清单和资源报告；`target/`保留实际嵌入镜像、输出毒化、只读检查mask及末端guard。数据、指令、x10/x11和DMA spans均来自同一次producer交付，**不手写编码，不套用旧BFV布局/CKKS取整适配**。

AM将镜像搬到`0x87000000`，按真实window行数配置MMIO，再执行producer程序。末尾仅一次PSYNC；CPU轮询`IRQ=1 && VALID=1 && BUSY=0`，清完成电平，然后逐节点、逐RNS原始word比较golden，同时检查只读数据及窗外guard。无需PLIC或定时器中断。默认完成等待预算2500万模拟cycle，可通过`WAIT_CYCLES=...`调整；IT模拟器自身的cycle limit也必须足够。发令阶段若受RTL反压阻塞，不能靠完成轮询的预算解除阻塞。

仅构建一种UART模式可用`make minimal`或`make silent`。大构建请把`OUTPUT_ROOT`设到磁盘目录，不放`/tmp`。改变接收器或producer版本时使用新的输出目录，已有交付不会被接收器覆盖。

## 验收边界

构建门禁包括SEAL/软件模型raw golden、优化等价、严格host instruction model、native包验证、DMA子区间/只读限制、全部输出覆盖、ELF真实指令字比对、加载段与DDR不重叠，以及静默ELF无UART路径检查。任何门禁失败都会停止构建。

**下载包状态是`BUILD_READY_NOT_IT_PASS`，不是硬件通过。**该分支的host默认采用`natural_coefficient_boundaries`：在首PNTT之前和末PINTT之后做软件模型的bit-reversal边界转换，而不额外发出重排指令；其`hardware_contract_verified=false`。本workload原样保留新的`ntt_table_abi`，不偷偷改数据来适配旧RTL。必须用支持此合同的实际RTL跑VCS并比对，才能宣布IT通过。

CKKS的解密误差/容差记录在producer的`semantic/decoded.json`；目标端按同一交付的原始RNS word严格比较，不能用近似容差掩盖指令、布局或取整错误。这里没有在裸机上解密，也没有把host通过冒充VCS结果。N128是诊断参数；参数安全级别以交付metadata为准，不用于声称密码学安全性。
