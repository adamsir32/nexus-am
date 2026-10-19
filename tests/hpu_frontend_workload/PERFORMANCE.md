# 1019：新API的07组正确性与性能实验

本组位于独立的`hpu_frontend_workload`，不覆盖主线`hputest`或原有00～07用例。AM基点为`9016ef9c`，实验分支为`1019-operator-resource-perf`。

## 版本与接口

- 新版依赖：inline-asm的`feature/operator-resource-management@a19197ea976d492ea9ce8e0ef6f065c922170ff9`。
- 旧版参照：AM `9016ef9c`使用inline-asm `03a32c168404f3ad64e6a4d7ad82a081f910314b`。旧版依赖和用例保持不动。
- 新版直接调用上游`ApplicationBuilder`、`Evaluator`和资源编译器；AM只负责交付接收、配置、发令、同步和检查，不自行实现KeySwitch或取整补丁。
- 输入准备复用旧版`tools/hpu-scheme-cases/fixture.hpp`。两版modified-SEAL源码树相同；`PERF_FIXTURE.json`记录实际Q/P模数、输入/输出RNS数、scale、correction factor、旋转步长和随机种子。

上游顶层API兼容时，后续调整资源实现可不改C用例，只更新固定依赖并重新生成、验证、编译。依赖仍固定到commit，不在构建时无条件追踪远端HEAD；API、参数或交付格式变化时仍需适配。

## 分组和命名

| 新07编号 | N | 输入level | 数量 |
| --- | --- | --- | --- |
| 07_01～07_18 | 4096 | CKKS/BFV为4，BGV为3 | 18 |
| 07_19～07_36 | 4096 | 三种算法均为16 | 18 |
| 07_37～07_54 | 8192 | CKKS/BFV为4，BGV为3 | 18 |
| 07_55～07_72 | 8192 | 三种算法均为16 | 18 |

每个区间按CKKS、BFV、BGV排序；每种算法依次为KeySwitch、HADD、HMUL+Reline、Reline、Rescale/ModSwitch、Rotate。

示例：`07_03_ckks_hmul_reline_l4_n4096`。`level`表示输入Q基的RNS分量数，不含特殊基P；Rescale/ModSwitch后输出level减少1。CKKS/BFV的Q/P为27位模数；BGV原level采用固定模数，16level采用31位模数，具体值以每包参数为准。明文模数BFV/BGV为65537，均为demo参数，不声称达到标准安全级别。

每项分`optimized`和`noopt`两个独立调度变体，仅改变上游`optimize_resources`开关；各有`minimal`与`silent`两种UART版本。因此是72项逻辑测试、144条独立调度程序、288套ELF/BIN/TXT。**每个ELF只跑一个N、一个level、一个算子，不在一个ELF中串行跑全部组合或重复多轮。**

KeySwitch用三分量输入、将c0/c1置零后调用上游relinearize，区别于普通Reline的完整三分量输入。HMUL明确调用multiply和relinearize，是一个乘法算子的两节点实现，不附加rescale。每个节点及最终结果均按原始RNS word检查，不能只看解密误差。

新顶层API没有单独的NTT/INTT/BConv入口，故不把旧07的这些内核伪装成新API用例；原内核测试仍保留。完整映射见[performance-cases.tsv](performance-cases.tsv)的`baseline_case_id`，不能仅凭新旧序号对应。

## 测量边界

统一采用`issue_to_done_v2`：

1. 计时前完成镜像拷贝、cache clean、全部参数预检查、MMIO读回与COMMIT生效检查。
2. 读取cycle起点，运行上游生成的指令程序，轮询MMIO等待完成，再读取cycle终点。
3. 计时后清完成电平，检查状态、全部节点golden、只读区与guard；全部通过才打印性能行。

计时区间没有UART打印或逐轮阶段打印；等待循环每64轮检查一次超时并保存诊断，与主线07等待开销对齐。程序末尾只发一次PSYNC，不启用PLIC或定时器中断。`silent`仍记录`workload_trace.cycle_start/cycle_end`，但不输出UART。

```text
[HPU][NEWAPI-PERF] case=... variant=optimized N=4096 level=4 metric=issue_to_done_v2 start=... end=... cycles=... verified=1
```

`noopt/optimized`周期比才是本组受控的资源优化对照：两者输入、算子图、所有可见输出和验收条件一致。与主线旧包比较只能作为版本参照：新版NTT表ABI不同，且BFV/BGV的HMUL拆为两个可见节点，旧版为单个融合节点，中间结果写回义务可能不同。不能把这些差异全部归因为资源调度加速，也不能在没有测量结果时宣称提升。

资源优化不保证每项指标都下降。例如本次CKKS HMUL、N4096原level的编译报告中，DMA命令从1129降为1075，但分配的DDR行从13570增为14466。这里是编译器的静态报告，不是执行时间；是否加速必须由同配置实测cycle决定。

## 构建与运行

```sh
git switch 1019-operator-resource-perf
git submodule update --init tests/hpu_frontend_workload/third_party/inline-asm

# 一个分片：6项逻辑算子，各有optimized/noopt及两种UART模式。
make -C tests/hpu_frontend_workload performance \
  DEGREE=4096 PROFILE=baseline SCHEME=ckks JOBS=4

# 可选N=8192、PROFILE=l16、SCHEME=bfv/bgv；只构建静默版可加MODE=silent。
# 只构建一项可加CASE_ID=07_03_ckks_hmul_reline_l4_n4096。
```

GitHub Actions工作流`build 1019 experimental HPU operator performance`按2个N×2种level配置×3种算法分为12个独立分片，不重跑旧hputest。每个完整分片24套ELF/BIN/TXT；包内保留原生交付、参数、指令、golden和资源报告。

原level使用DDR基址`0x90000000`，目标内存至少512MiB；16level使用`0xc0000000`，目标内存至少2GiB。模拟器内存配置必须匹配。完成等待预算默认2500万cycle，可用`WAIT_CYCLES`调整；模拟器总cycle限制独立设置。它们均不是实测性能。

将不同variant分别跑VCS/FPGA后，可用`scripts/parse_performance.py`汇总真实UART日志；`--revision`应填写实际AM、inline-asm和RTL版本。缺失数据保留为空，不生成CPU时间或假加速比。多轮测量在用例外独立执行。

```sh
python3 tests/hpu_frontend_workload/scripts/parse_performance.py \
  optimized-uart.log noopt-uart.log --output performance-results \
  --revision 'AM=<commit>; inline-asm=a19197e; RTL=<实际commit>'
```

解压后的包也可用`tools/parse_performance.py`，无需安装额外Python库。不同版本、RTL配置或时钟条件应分批保存结果，不能混合求平均。

## 验收与已知硬件合同限制

生成器严格比较新版顶层API的最终raw word和共享SEAL Fixture，并执行上游严格instruction model；原生包、DMA范围、输出覆盖、真实ELF指令和静默UART路径也需通过构建门禁。优化开关两版均须通过，不在模型失败时放宽golden。

**host通过不等于RTL通过。**上游默认`natural_coefficient_boundaries`在host模型的NTT边界做bit-reversal转换，新NTT表ABI是否与实际RTL匹配尚未确认；交付保持`hardware_contract_verified=false`和`BUILD_READY_NOT_IT_PASS`。本组不偷偷修改表或指令去适配旧RTL。`legacy_raw_stage`只能作严格诊断，失败不输出替代可运行包。硬件只有在当前交付的原始word与guard自检通过后，性能结果才有效。

2026-10-19本地验证记录：

- 72项Fixture各编译optimized/noopt，两版合计144条程序，严格软件instruction model与raw golden均通过；全矩阵采用`--verify-only`，只保存小型参数和资源报告。
- `07_03_ckks_hmul_reline_l4_n4096`、`07_45_bfv_hmul_reline_l4_n8192`、`07_68_bgv_hadd_l16_n8192`各构建4个实际RISC-V ELF，共12个；原生包、嵌入数据、指令字、成功路径计时顺序、静默UART门禁通过。
- CKKS/N4096/Reline的`legacy_raw_stage`严格探针按预期拒绝生成：与oracle的首word不匹配。未据此修改golden或开启跳过校验开关。
- 未执行VCS/FPGA，未填写实测cycle或加速比。全部72项、288个ELF由本分支独立CI分片构建，其运行结果应以对应Actions记录为准。
