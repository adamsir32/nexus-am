# 07组：新API单算子运行用例与手动性能实验

本组位于`hpu_frontend_workload`，随默认主线`master`的00～07运行用例一起交付到唯一的`hpu.zip`。当前07覆盖N1024/N2048/N4096/N8192共72项，每项只交付`optimized/minimal`的ELF和BIN；不再自动上传N/算法分片、A/B重复版本或开发资料。00～06仍保留在`hputest`，其兼容入口转发到同一运行包构建器。迁移前主线备份为`backup/master-before-1019-20261023@9016ef9c`。

## 版本与接口

- 新版依赖：inline-asm的`feature/operator-resource-management@3ab94da16abce89b7e9b74f4e7fcd93604dea495`；此前1019交付的`a19197e`、`7306d1c`、`9686076`保留在Git历史中。
- 旧版参照：备份中的AM `9016ef9c`使用inline-asm `03a32c168404f3ad64e6a4d7ad82a081f910314b`。旧依赖和历史用例可回查；当前默认构建使用新固定依赖，不启动旧依赖的准备或多包发布流程。
- 新版直接调用上游`ApplicationBuilder`、`Evaluator`和资源编译器；AM只负责交付接收、配置、发令、同步和检查，不自行实现KeySwitch或取整补丁。
- 输入准备复用旧版`tools/hpu-scheme-cases/fixture.hpp`。两版modified-SEAL源码树相同；`PERF_FIXTURE.json`记录实际Q/P模数、输入/输出RNS数、scale、correction factor、旋转步长和随机种子。

上游顶层API兼容时，后续调整资源实现可不改C用例，只更新固定依赖并重新生成、验证、编译。依赖仍固定到commit，不在构建时无条件追踪远端HEAD；API、参数或交付格式变化时仍需适配。

NTT ABI v3要求stage以及pre/post在线PMUL参数均为128个u32、512字节、2line，N128也不例外；在线PMUL模式为1，参数放入Bank5，post模板已含归一化。接收器同时核对参数与memory ABI，拒绝旧表或错误K/长度。新版库直接生成fixed单asm入口，x11只在DMA长度变化时重载；性能适配器原样保留该入口，只从dynamic入口提取无HPU指令的预检查，不退回旧动态发令代码。SSA仅将声明的输出落DDR，未标记中间值不再为了AM检查额外写回；最终结果、guard和只读区检查不变。详见[兼容性检查](COMPATIBILITY.md)。

2026-10-23同步64对象ISA、DMA的MOD/REL/CP字段及twiddle-only LLC分配提示，数据和指令由当前固定版本重新生成。CP是实际DMA指令字段，不能当作trace开关，也不能为静默输出删掉真实DMA。本次不部署自动更新机制。

## 分组和命名

| 新07编号 | N | 输入level | 数量 |
| --- | --- | --- | --- |
| 07_01～07_18 | 1024 | CKKS/BFV为4，BGV为3 | 18 |
| 07_19～07_36 | 2048 | CKKS/BFV为4，BGV为3 | 18 |
| 07_37～07_54 | 4096 | CKKS/BFV为4，BGV为3 | 18 |
| 07_55～07_72 | 8192 | CKKS/BFV为4，BGV为3 | 18 |

每个区间按CKKS、BFV、BGV排序；每种算法依次为KeySwitch、HADD、HMUL+Reline、Reline、Rescale/ModSwitch、Rotate。

活动清单只接受上述四个N、输入level≤4；默认运行包构建全部72项，不只构建N8192。旧level16源码及清单保留在[历史归档](archive/20261023-level16/README.md)，更大的N也不进入当前交付。加入N1024/N2048后按N升序重新连续编号，旧N4096/N8192的36项编号映射保存在[performance-id-map.tsv](performance-id-map.tsv)。归档和旧日志中的同一序号不一定代表当前用例，必须按完整case_id或映射回查。

示例：`07_03_ckks_hmul_reline_l4_n1024`和`07_39_ckks_hmul_reline_l4_n4096`。`level`表示输入Q基的RNS分量数，不含特殊基P；Rescale/ModSwitch后输出level减少1。CKKS/BFV的Q/P为27位模数；BGV保留原level3及固定模数，未为统一到level4而改变密码参数，具体值以构建目录中的参数记录为准。明文模数BFV/BGV为65537，均为demo参数，不声称达到标准安全级别。

默认交付为72项逻辑测试、72套ELF/BIN，均采用`optimized/minimal`。手动实验仍可分别构建`optimized`和`noopt`（仅改变上游`optimize_resources`开关），以及`minimal`和`silent`两种UART模式；这些额外版本不自动进入运行包。每个ELF只跑一个N、一个level、一个算子，不在一个ELF中串行跑全部组合或重复多轮。

KeySwitch用三分量输入、将c0/c1置零后调用上游relinearize，区别于普通Reline的完整三分量输入。HMUL明确调用multiply和relinearize，是一个乘法算子的两节点实现，不附加rescale。每个节点及最终结果均按原始RNS word检查，不能只看解密误差。

新顶层API没有单独的NTT/INTT/BConv入口，故不把旧07的这些内核伪装成新API用例；00～06的指令/算法测试和旧07历史源码仍保留。旧主线性能参照见[performance-cases.tsv](performance-cases.tsv)的`baseline_case_id`；新增N1024/N2048没有旧主线对应项，该列留空，不编造映射。

## 测量边界

统一采用`issue_to_done_v2`：

1. 计时前完成镜像拷贝、cache clean、全部参数预检查、MMIO读回与COMMIT生效检查。
2. 读取cycle起点，运行上游生成的指令程序，轮询MMIO等待完成，再读取cycle终点。
3. 计时后清完成电平，检查状态、全部声明导出结果的golden、只读区与guard；全部通过才打印性能行。

计时区间没有UART打印或逐轮阶段打印；等待循环每64轮检查一次超时并保存诊断，与主线07等待开销对齐。程序末尾只发一次PSYNC，不启用PLIC或定时器中断。`silent`仍记录`workload_trace.cycle_start/cycle_end`，但不输出UART。

```text
[HPU][NEWAPI-PERF] case=... variant=optimized N=4096 level=4 metric=issue_to_done_v2 start=... end=... cycles=... verified=1
```

`noopt/optimized`周期比才是本组受控的资源优化对照：两者输入、算子图、所有可见输出和验收条件一致。与主线旧包比较只能作为版本参照：新版NTT表ABI不同，且BFV/BGV的HMUL拆为两个可见节点，旧版为单个融合节点，中间结果写回义务可能不同。不能把这些差异全部归因为资源调度加速，也不能在没有测量结果时宣称提升。

资源优化不保证每项指标都下降。例如2026-10-19的`a19197e`基线中，CKKS HMUL、N4096原level的DMA命令从1129降为1075，但分配的DDR行从13570增为14466。这里是旧版编译器的静态报告，不是新版执行时间；是否加速必须由同配置实测cycle决定。

## 构建与运行

默认与00～06一起导出一个运行包：

```sh
git submodule update --init tests/hpu_frontend_workload/third_party/inline-asm
make -C tests/hpu_frontend_workload all
```

GitHubActions的`build HPU`只有一个顺序构建job，复用native producer后上传一个短名`hpu`。下载`hpu.zip`后直接得到`00/`～`07/`；07目录仅有72项的ELF和BIN。源码、golden、inst32、反汇编、参数及资源报告留在仓库或构建工作目录，不塞入ZIP，也不上传中间分片。

需要资源优化A/B或静默对照时才显式运行以下手动实验：

```sh
# 一个分片：6项逻辑算子，各有optimized/noopt及两种UART模式。
make -C tests/hpu_frontend_workload performance \
  DEGREE=8192 PROFILE=baseline SCHEME=ckks JOBS=4

# 可选DEGREE=1024/2048/4096、SCHEME=bfv/bgv；PROFILE仅保留baseline。
# 只构建静默版可加MODE=silent。
# 只构建一项可加CASE_ID=07_57_ckks_hmul_reline_l4_n8192。
```

手动实验脚本仍可产生带开发资料的分片包，供本地排查；它不是默认交付，也没有独立自动上传任务。原`build-hpu-operator-perf.yml`和`build-hpu-frontend.yml`仅保留手动兼容入口，统一委托`build-hpu.yml`。

当前活动用例使用DDR基址`0x90000000`，目标内存至少512MiB。模拟器内存配置必须匹配。完成等待预算默认2500万cycle，可用`WAIT_CYCLES`调整；模拟器总cycle限制独立设置。它们均不是实测性能。

将不同variant分别跑VCS/FPGA后，可用`scripts/parse_performance.py`汇总真实UART日志；`--revision`应填写实际AM、inline-asm和RTL版本。缺失数据保留为空，不生成CPU时间或假加速比。多轮测量在用例外独立执行。

```sh
python3 tests/hpu_frontend_workload/scripts/parse_performance.py \
  optimized-uart.log noopt-uart.log --output performance-results \
  --revision 'AM=<commit>; inline-asm=3ab94da; RTL=<实际commit>'
```

日志解析工具保留在仓库，不复制到运行包；无需安装额外Python库。不同版本、RTL配置或时钟条件应分批保存结果，不能混合求平均。

## 验收与已知硬件合同限制

生成器严格比较新版顶层API的最终raw word和共享SEAL Fixture，并执行上游严格instruction model；原生包、DMA范围、输出覆盖和真实ELF指令也需通过构建门禁。手动A/B的两版均须通过，silent版本另检查静默UART路径；不在模型失败时放宽golden。打包器只证明清单列出的ELF+BIN齐全，不把打包成功当作算子或硬件通过。

**host通过不等于RTL通过。**上游默认`natural_coefficient_boundaries`在host模型的NTT边界做bit-reversal转换，新NTT表ABI是否与实际RTL匹配尚未确认；交付保持`hardware_contract_verified=false`和`BUILD_READY_NOT_IT_PASS`。本组不偷偷修改表或指令去适配旧RTL。`legacy_raw_stage`只能作严格诊断，失败不输出替代可运行包。硬件只有在当前交付的原始word与guard自检通过后，性能结果才有效。

新版上游迁移说明还保留HpuCmdMerge在反压时可能使PNTT越过较早参数DLOAD的风险说明。仅更新在线twiddle格式不能据此证明已消除该风险；需以实际RTL版本验证。本次不加每stage软件等待，也不修改RTL掩盖此问题。

## 当前单包验收与历史记录

2026-10-23的当前单包改造已完成00～03共44项RV64编译检查，04～06仍在适配，新增N1024/N2048和完整单包的最终验收结果以当次构建记录为准。下列记录属于改造前的矩阵/编号，不证明当前00～07全部通过；历史报告中的case_id应通过映射回查。尚未运行真实RTL/VCS/FPGA，不填写硬件周期或加速比。

2026-10-23版本`9686076`、改造前36项07交付的历史记录：

- 接续中断前的构建任务，其生成器验收和6个活动性能分片均成功；36项算子、optimized/noopt合计72条原生程序通过严格模型/golden/包验证，144个真实RISC-V ELF通过指令、嵌入数据、计时位置及静默输出门禁。
- 六个API应用（CKKS/BFV/BGV各N128/N4096）重新生成，输入level均为3，12个精简/静默ELF构建及校验通过。
- 构建结果逐项检查均为0返回码；原有59项Python验收通过，另对默认N8192入口增加1项定向检查。归档36份源码与迁移前版本直接比较一致，不进入当前6个性能下载包。
- 下载包保持`BUILD_READY_NOT_IT_PASS`；未运行真实RTL/VCS/FPGA，不填写硬件周期或加速比。新包要求64对象ISA v1.2及在线K=8合同匹配，不能与旧8对象RTL或旧镜像混用。

2026-10-19历史基线`a19197e`验证记录（非本次新版结果）：

- 72项Fixture各编译optimized/noopt，两版合计144条程序，严格软件instruction model与raw golden均通过；全矩阵采用`--verify-only`，只保存小型参数和资源报告。
- `07_03_ckks_hmul_reline_l4_n4096`、`07_45_bfv_hmul_reline_l4_n8192`、`07_68_bgv_hadd_l16_n8192`各构建4个实际RISC-V ELF，共12个；原生包、嵌入数据、指令字、成功路径计时顺序、静默UART门禁通过。
- CKKS/N4096/Reline的`legacy_raw_stage`严格探针按预期拒绝生成：与oracle的首word不匹配。未据此修改golden或开启跳过校验开关。
- 未执行VCS/FPGA，未填写实测cycle或加速比。该历史版本完整矩阵为72项、288个ELF，CI运行结果应以当时对应Actions记录为准，不作为当前活动矩阵数量。

2026-10-21历史版本`7306d1c`的验证记录（非本次新版结果）：

- 72项Fixture、optimized/noopt合计144条程序，严格instruction model与共享SEAL raw golden均通过。旧输入、golden及计时边界没有为迁移而放宽。
- 六个API应用（CKKS/BFV/BGV各N128/N4096）全部重新生成并通过host/native包检查；两种UART模式合计12个真实ELF构建、指令字和静默检查通过。
- 07代表性CKKS/N4096乘法、BFV/N8192乘法、BGV/N8192/16level加法，各四种变体，共12个真实ELF的嵌入数据、字码、计时及静默门禁通过。
- K=8 NTT、固定DMA入口、指令执行器三项上游原生测试通过；RV32/RV64、O0/O2、寄存器压力组合的8项目标代码生成验证通过。Debian交叉工具检查使用任务专属工具入口，未修改上游或本机配置。
- 接收器/适配器/构建路径等52项Python测试通过，生成器三项验收通过。
- 未执行真实RTL/VCS/FPGA回归；软件/构建通过不记为IT或ST通过，不填写实测cycle。自动依赖更新按用户要求延期，现有固定pin和手动回退能力保留。
