# HPU运行用例（00～07单包交付）

默认主分支是`master`。快速导出只生成一个短名`hpu.zip`，解压后为`00/`～`07/`各组；每条用例只保留一份正常日志模式的ELF和BIN，不带源码、golden、指令文本、反汇编、资源报告或四份重复版本。完整case_id保留在文件名中。00～03复用`tests/hputest`的可读C用例；04～06通过`src/group.c`执行上游生成程序，保留原用例职责和编号；新07位于本目录。历史源码仍可回查，`hputest`路径恢复为同一运行包构建器的兼容入口，不再默认启动旧大矩阵流水线。

迁移前主线完整备份在`backup/master-before-1019-20261023@9016ef9c`。旧源码、历史编号和历史打包方式可从Git回查，不需要为了运行当前00～06切换旧主线。

依赖固定为`feature/operator-resource-management@3ab94da`，不是旧workload的main/legacy-main。完整commit见[producer.json](producer.json)。API和应用图直接采用该分支的`examples/*_evaluator_application.cpp`，不是用AM重新实现一套算法。

本轮从`9686076`跟进SSA/内存IO重构与在线PMUL：原00～07编号、测试职责和顶层图继续使用，但指令、布局和golden必须重新生成。接收器升级NTT ABI v3，stage与pre/post参数均为两行；只核对图中显式导出的结果，不强制把tensor等中间对象写回DDR。所有声明的输出仍逐RNS原始word严格比较，不能用容差或跳过最终结果来通过。新生成的变换序列需要支持PMUL在线模式的新版RTL。详见[兼容性检查](COMPATIBILITY.md)。

2026-10-21跟进NTT ABI v2：每stage使用在线K=8的512字节/2line参数，数据镜像及DMA spans全部由新版库重新生成，不能混用旧完整twiddle表。上游fixed发令入口的单asm和x11长度复用原样保留；接收器分别核对dynamic/fixed两套原生字码，实际ELF检查fixed入口。07专用适配器只提取计时前预检查，不重新生成发令序列。自动跟进机制本次未启用。

2026-10-23继续同步上游64对象ISA、DMA的MOD/REL/CP字段及twiddle-only LLC分配提示。交付数据和指令须由同一固定版本重新生成；CP是DMA指令字段，不是trace开关，不能为关闭打印而删除DMA。

[07组单算子](PERFORMANCE.md)包含N1024、N2048、N4096、N8192，每个N为CKKS/BFV/BGV各6项，共72项。按N升序编号为`07_01`～`07_72`；旧N4096/N8192编号对应关系见[performance-id-map.tsv](performance-id-map.tsv)，不能只凭序号对照旧日志。CKKS/BFV输入level4、BGV输入level3。默认只交付`optimized/minimal`；noopt和silent保留手动实验能力，不自动加入下载包。超过上限的大N或level16不进入当前交付，历史源码仍可回查。

## 保留的六项API样例（非默认独立下载包）

| 独立ELF | 应用 |
| --- | --- |
| CKKS_N128、CKKS_N4096 | `x × (RotateLeft(x,1) + Conjugate(x)) + 1`，显式reline/rescale |
| BFV_N128、BFV_N4096 | `x × (RotateRows(x,1) + RotateColumns(x)) + 7`，显式reline/modswitch |
| BGV_N128、BGV_N4096 | 同上，保留BGV的correction factor和模上下文 |

每个ELF只跑一个scheme、一个N、一张7节点应用图，不串行跑多个规模或重复轮次。图中的算子依赖仍必须按顺序执行。6个ELF可在用例外部分别并行仿真；不能把同一图的依赖节点任意分拆。

可读的main放在`src/`，CSR操作直接可见；共享数据搬运、同步、自检分别放在`runtime/image.c`、`wait.c`、`check.c`。大型producer生成C和数据仅位于忽略的构建目录，不提交进Git，也不进入默认运行包。

## 构建与下载

```sh
git submodule update --init tests/hpu_frontend_workload/third_party/inline-asm
make -C tests/hpu_frontend_workload all

# 同一构建器，也可显式选择磁盘输出目录。
python3 tests/hpu_frontend_workload/scripts/build-runtime.py \
  --am-home "$PWD" \
  --producer "$PWD/tests/hpu_frontend_workload/third_party/inline-asm" \
  --output "$PWD/build/hpu" --jobs 4
```

用例路径通过 `CASE_OBJ_DIR`、`CASE_BINARY` 传入，仅在 `Makefile.case` 本层映射为输出目录；不把公共 `DST_DIR`、`BINARY` 作为命令行变量传给递归 AM/klib 构建。`make test` 会执行变量隔离回归，验证实际构建命令不会污染递归构建的默认路径。

`make all`在`OUTPUT_ROOT/hpu.zip`生成本地运行包；上面显式命令生成仓库下的`build/hpu/hpu.zip`。GitHubActions的`build HPU`工作流只提供一个`hpu`下载项，下载文件名为`hpu.zip`，一次解压直接得到各组目录，不再按N、算法或UART模式拆包。原两个工作流仅保留手动兼容入口，并委托同一单包工作流。CPU测试的工作流不变。

默认压缩包仅有`NN/case_id.elf`和`NN/case_id.bin`，没有`minimal/`、`silent/`或`noopt/`重复目录。清单中的每项必须同时有非空ELF和BIN；缺文件、重复case_id或超出活动07上限会停止打包。Actions直接上传运行目录前，额外检查该目录恰好等于显式清单，旧构建残留不能混入。

输入、密钥、twiddle、节点golden、DMA清单和资源报告留在构建工作目录供开发核查，不作为下载附件。程序需要的初始镜像和自检数据仍嵌入ELF/BIN；删除外置报告不等于取消用例自检。数据、指令和DMA spans必须来自同一次producer交付，不混用旧镜像。

上述六项API样例使用镜像基址`0x87000000`；新07使用`0x90000000`，目标内存至少512MiB，其他组按各自用例配置。运行时按真实window行数配置MMIO，再执行producer程序。末尾仅一次PSYNC；CPU轮询`IRQ=1 && VALID=1 && BUSY=0`，清完成电平，然后对每个声明导出结果逐RNS原始word比较golden，同时检查只读数据及窗外guard。无需PLIC或定时器中断。默认完成等待预算2500万模拟cycle，可通过`WAIT_CYCLES=...`调整；IT模拟器自身的cycle limit也必须足够。发令阶段若受RTL反压阻塞，不能靠完成轮询的预算解除阻塞。

`make minimal`与`make all`采用同一单包默认。`scripts/build.py`保留六项API样例的手动构建能力，`scripts/build_performance.py`保留A/B和静默实验能力，均不自动上传其开发资料包。大构建请把`OUTPUT_ROOT`设到磁盘目录，不放`/tmp`。改变接收器或producer版本时使用新的输出目录，已有交付不会被覆盖。

## 特殊用例与结果判断

`00_01_dload_hold`是保留现场供波形观察的hold用例，不能要求它像普通用例一样返回PASS。`00_11_return_1`是验证失败退出路径的预期fail探针，返回失败是其预期行为；`00_10_return_0`验证正常退出。不得将它们与普通自检用例按同一“必须全部成功退出”规则汇总。说明保留在仓库，不额外塞入运行包。

## 验收边界

算法用例的构建门禁按其类型检查软件模型raw golden、native包、DMA范围、输出覆盖、ELF真实指令字和加载段；手动A/B或silent实验另检查对应等价或静默路径。打包通过只证明显式清单内运行文件齐全，不代表所有功能或实际硬件已经通过。00～03已有44项真实RV64编译检查记录；04～06适配和完整单包验收的结果应以当次构建记录为准，不能用此前36项07或六样例的历史结果替代。

**下载包状态是`BUILD_READY_NOT_IT_PASS`，不是硬件通过。**该分支的host默认采用`natural_coefficient_boundaries`：在首PNTT之前和末PINTT之后做软件模型的bit-reversal边界转换，而不额外发出重排指令；其`hardware_contract_verified=false`。本workload原样保留新的`ntt_table_abi`，不偷偷改数据来适配旧RTL。必须用支持此合同的实际RTL跑VCS并比对，才能宣布IT通过。

CKKS的解密误差/容差记录在producer的`semantic/decoded.json`；目标端按同一交付的原始RNS word严格比较，不能用近似容差掩盖指令、布局或取整错误。这里没有在裸机上解密，也没有把host通过冒充VCS结果。N128是诊断参数；参数安全级别以交付metadata为准，不用于声称密码学安全性。
