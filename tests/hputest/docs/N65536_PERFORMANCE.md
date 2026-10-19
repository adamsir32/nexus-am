# 大规模功能与多规模性能交付

现有N128/N4096功能用例保留。N65536功能用例和07性能用例的范围如下：

| 分组 | 编号 | 内容 |
|---|---|---|
| 03 | 03_10～03_18 | PADD、PSUB、PMUL、PMAC、PNTT、PINTT、PMODLD、PSYNC、PFREE，N65536 |
| 04 | 04_12～04_18 | BConv、整体NTT、整体INTT、CKKS/BFV/BGV KeySwitch、完整NTT+Auto，N65536 |
| 05 | 05_40～05_54 | CKKS/BFV/BGV各5项：HADD、HMUL+Reline、Reline、Rescale/ModSwitch、Rotate，N65536 |
| 07 | 07_01～07_40 | N4096：原参数22项（01～22），输入level=16的18项（23～40） |
| 07 | 07_41～07_80 | N8192：原参数22项（41～62），输入level=16的18项（63～80） |
| 07 | 07_81～07_120 | N16384：原参数22项（81～102），输入level=16的18项（103～120） |
| 07 | 07_121～07_160 | N32768：原参数22项（121～142），输入level=16的18项（143～160） |
| 07 | 07_161～07_200 | N65536：原参数22项（161～182），输入level=16的18项（183～200） |

07共200项，按N4096/N8192/N16384/N32768/N65536从小到大排列，每个ELF执行一段独立程序。
原有110项按规模重排，另增加90项level=16用例；本版编号已改变，不能按旧编号直接匹配性能记录。
用例号超过99时使用三位。完整名称显式包含输入level与N，例如`07_05_ckks_hmul_reline_l4_n4096`；
`_l1`、`_l3`、`_l4`、`_l16`分别表示输入Q含1、3、4、16个RNS分量，特殊模数P不计入level。
精确映射见[perf-cases.tsv](../perf-cases.tsv)：`functional_case_id`记录对应的现有04/05入口；
仅在07提供的规模或程序变体该列留空，实际规模、level和生成包应按清单及完整用例名匹配。
旧07的6个入口已原样移至
`archive/performance_before_n65536/`，登记在`archived-cases.tsv`；不能把旧N4096通过记录继承给新N65536。

## 05与07的数量和职责

05验证算法库接口及参数组合；07测量选定操作在不同多项式长度下的执行耗时，同时保留结果与内存自检。

| 分组 | 规模与组成 | 总数 |
|---|---|---:|
| 05算法库 | CKKS/BFV/BGV各5项操作×N128/N4096/N65536，加7项特殊参数回归、2项未接入记录 | 54 |
| 原07性能 | 仅N65536：7项基本/组合算子＋15项算法库操作 | 22 |
| 当前07性能 | N4096/N8192/N16384/N32768/N65536，每种规模原参数22项＋level=16的18项 | 200 |

原参数的22项包含7项算子：整体NTT、整体INTT、BConv、三算法KeySwitch及完整NTT+Auto；
以及15项算法库操作：三算法各自的HADD、HMUL+Reline、Reline、Rescale/ModSwitch、Rotate。
其中整体NTT/INTT为单RNS（level=1），BConv/Auto输入Q为level=4，CKKS/BFV标准接口为level=4，BGV为level=3。
每种规模新增的18项level=16用例覆盖三算法KeySwitch及上述15项算法库操作；每项输入Q均有16个RNS分量。
三算法level=16配置均为Q16/P1：Q含16个素数，P含1个特殊素数；CKKS/BFV的各个q为27bit，BGV的各个q为31bit。
降层操作的文件名记录输入level，输出level以各包参数和golden为准，不把输入输出分量数混写。
05额外的7项是BGV的CF参数回归和三算法的Gen3旋转回归；2项未接入为encode、bootstrap。
这些特殊参数和未接入项不计作07性能基准；05的N128规模不在07范围内，标准N4096操作已有独立性能入口。

## CI下载包与按需构建

00～06功能包仍名为`nexus-am-hpu-tests`，CI使用`HPU_BUILD_SCOPE=functional`，保留03独立subtest。
该包包含161个测试身份、322套普通/静默ELF/BIN/TXT，以及7项未接入索引，合计329条`INDEX.tsv`记录。

07独立发布21个性能分片，名称为`nexus-am-hpu-perf-nN-profile`。按N4096、N8192、N16384、N32768、N65536依次选择：

| profile | 适用N | 每片用例数 | 含义 |
|---|---|---:|---|
| `baseline` | 全部五种N | 22 | 原level=1/3/4的基本/组合算子及算法库操作 |
| `l16-ckks` | 全部五种N | 6 | CKKS KeySwitch及5项库操作，输入level=16 |
| `l16-bfv` | N4096～N32768 | 6 | BFV KeySwitch及5项库操作，输入level=16 |
| `l16-bgv` | 全部五种N | 6 | BGV KeySwitch及5项库操作，输入level=16 |
| `l16-bfv-a`、`l16-bfv-b` | 仅N65536 | 各3 | 将该规模的6项BFV交错拆分，限制单job中间数据占用 |

每个用例同时包含normal和silent版本，07合计200项、400套产物；分片之间互斥且覆盖完整07清单。
各CI job只导入、编译和发布所选scope的包，两个日志版本共享同次输入与golden，不在每个job重建全部200项应用数据。
上游RNS参考工具仍会生成同一N的额外临时样例；CI在每组模型导入成功后启用`HPU_COMPRESS_TEMP_RNS=1`，逐文件压缩本次临时bin为可恢复的`.gz`。

```sh
make -C tests/hputest performance-shard \
  HPU_BUILD_SCOPE=performance:8192:l16-ckks JOBS=4
```

默认分片交付位于`tests/hputest/build/performance-release/release/hputest/`，ELF/BIN/TXT按
`normal/07_performance/`和`silent/07_performance/`保存；构建脚本拒绝覆盖非空的`build/performance-release/`，重建时使用新的`OUTPUT_ROOT`。
`INDEX.tsv`列出用例名、N、输入level、内存要求及模式，`PARAMETERS.json`保留同批实际参数和来源；CI另导出参数表，实测时间留空。
溯源目录保留producer文本、指令、参数、布局、oracle及模型证据；原始window/golden/write-mask已嵌入并逐ELF校验，不再重复大bin。

本地`HPU_BUILD_SCOPE=all`仍可构建340项主清单，并合并为722套产物、729条索引记录，但必须预留足够磁盘。
CI通过上述分片控制存储和构建范围，未把这些构建结果声明为硬件通过或性能实测。

## 固定版本与语义

- SEAL、N65536基础指令及五种性能规模的BConv/NTT/INTT：`hpu-applications`锁定的inline-asm main，当前为`03a32c168404f3ad64e6a4d7ad82a081f910314b`。
- 完整NTT+Auto：沿用原04已使用的`inline-asm` legacy-main `69030963e71dbcf32897e8ae08695cfa2e65d79a`。main的旧Auto demo只做CPU预处理后的Galois KeySwitch，不作为完整Auto替代品。
- 两套生产者分别生成自己的编码和STG语义；AM不手写或拼接机器码。新03的PNTT/PINTT采用main的原位STG接口。
- 03新增的是单个N65536刺激，原N4096的37项边界/别名/立即数子测试仍保留；不声称N65536复制了所有旧subcase。
- 04的KeySwitch输入保留c2且c0/c1清零；05的Reline保留原c0/c1并合并。05 HMUL包含乘法及重线性化。
- 05继续逐原始物理word匹配modified-SEAL，不以解密近似误差放宽验收。BFV位序和CKKS只读输入shadow适配沿用既有接收器，不增加自造取整指令。

## 大数据内存要求

07根据输入level使用以下内存配置；新增N65536功能用例继续使用原512MiB配置，旧N128/N4096功能用例窗口仍为`0x87000000`。

| 用例 | HPU窗口基址 | 最小模拟RAM | Difftest/VCS参数 |
|---|---|---|---|
| 07的level=1/3/4，以及03/04/05的N65536功能用例 | `0x90000000` | 512MiB | `+ram_size=536870912` |
| 全部07的level=16用例 | `0xc0000000` | 2GiB | `+ram_size=2147483648` |

实际生成的BFV HMUL、N65536、level=16窗口镜像为707,528,192字节（约674.75MiB），已经超过旧512MiB模拟RAM的总容量。
level=16统一将窗口移到`0xc0000000`，为ELF内嵌数据、运行窗口及guard留出独立空间。

仅修改模拟器RAM大小不等于修改硬件窗口：ELF内的BASE/SIZE仍由用例明确配置。
构建检查同时验证ELF装载末端不覆盖窗口、窗口加guard不越过对应512MiB或2GiB RAM末端。
加载level=16 ELF时需同步切换模拟RAM配置；仅保留旧512MiB参数不能容纳所有新用例。
仿真max-cycle要覆盖镜像初始化、cache操作、计算及自检；不能仅按07打印的被测区间设置总上限。

## cycle口径

每个07 ELF默认只执行一次程序，不内塞多轮串行测试：

1. 镜像准备及cache clean完成后，调用`hpu_validate_<program_stem>()`检查DMA地址、长度、对象容量和程序参数。此入口不发HPU指令，任何检查失败均在计时前返回失败。
2. 完成窗口配置写入/回读、COMMIT及状态检查；`perf_cycle_read()`在调用发令入口前读取SCPU的`cycle`CSR。
3. 执行DLOAD/配置/计算/DSTORE/唯一末尾PSYNC；`application_wait()`轮询到IRQ有效且BUSY清零后，立即读取结束`cycle`。
4. 清除完成电平、检查最终状态，再完成全部golden、只读区域及guard检查，最后统一打印start/end/cycles。

07链接生成的`<program_stem>_perf.c`：计时发令入口使用已经检查过的只读参数，不再执行原程序中的参数检查和逐DMA trace写入。
适配保留producer生成的全部HPU指令字及顺序，并对照原始`.inst32`校验；原始C程序继续用于03/04/05功能入口。
这样移出的只是软件预检查和诊断写入，DLOAD、计算、DSTORE、同步及结果检查仍完整执行。

修正后的指标名为`issue_to_done_v2`，包括CPU发令/反压、DMA、HPU计算和完成轮询，**不是HPU核心纯计算cycle**。
旧`issue_to_done`包含参数检查和逐DMA trace开销；本次需用新ELF重测，不能把旧数据改名后与v2混合求平均。
正常版仅输出摘要，禁止以verbose模式构建07，避免逐DMA日志污染计时。
静默版保留读cycle及同样自检，但不输出UART。

```text
[HPU][PERF] case=07_05_ckks_hmul_reline_l4_n4096 N=4096 level=4 metric=issue_to_done_v2 start=... end=... cycles=... verified=1
```

建议每项独立执行至少3轮，使用`scripts/parse-perf-results.py`汇总真实日志：

```sh
python3 scripts/parse-perf-results.py run1.log run2.log run3.log \
  --revision 'AM=<commit>;RTL=<commit>' --output perf-results
```

解析器只接收当前200项的`issue_to_done_v2`且`verified=1`记录，核对日志中的`N`、`level`与清单后，按完整用例名分别汇总；旧口径或不完整记录会报错。
需要秒数时额外传`--cpu-hz`（目标SCPU实际频率Hz）。不能把VCS宿主机墙钟耗时当作硬件耗时。

## CPU同参数复现

`tools/hpu-scheme-cases/cpu_benchmark.cpp`使用同一Fixture、固定种子及仓库内modified-SEAL。
它测量Evaluator操作的单线程主机墙钟纳秒，准备/密钥生成/加解密及每轮自检在计时之外。
HMUL测multiply+relinearize，不额外包含rescale。运行参数如下：

```sh
cmake -S tools/hpu-scheme-cases -B build/cpu-baseline \
  -DINLINE_ASM_ROOT="$PWD/third_party/hpu-applications" -DCMAKE_BUILD_TYPE=Release
cmake --build build/cpu-baseline --parallel 4 --target hpu_cpu_benchmark
build/cpu-baseline/hpu_cpu_benchmark ckks hmul 65536 3
build/cpu-baseline/hpu_cpu_benchmark ckks hmul 65536 3 16
# scheme: ckks/bfv/bgv；op: hadd/hmul/reline/modswitch/rotate/keyswitch
# 最后一个可选参数为输入Q的RNS分量数；省略时CKKS/BFV为4，BGV为3。
# 本轮07对比N可选4096、8192、16384、32768、65536；原128功能规模也可复现。
# 服务器应记录CPU型号、频率、编译器和编译选项。
```

SEAL配置关闭HEXL；当前`sec_level_type::none`，参数只作demo，不是安全等级声明。
CPU与FPGA对比必须用相同N、输入level、实际Q/P素数、密文分量、dnum、scale/CF、操作边界和输入。
level=16的HPU数据需与显式传入`16`的CPU执行配对。
原始RNS BConv/NTT/INTT/Auto不冒充SEAL算法库基准；这些项的CPU参考实现选择另行记录。

如需独立生成或复核level=16包，下面的工具复用同一Fixture；`library`用于算法库接口，KeySwitch采用kernel参数入口：

```sh
cmake --build build/cpu-baseline --parallel 4 \
  --target hpu_scheme_case_generator hpu_fixture_parameters
HPU_DELIVERY_COMMIT=03a32c168404f3ad64e6a4d7ad82a081f910314b \
  build/cpu-baseline/hpu_scheme_case_generator ckks hmul 4096 \
  build/packages/ckks-hmul-l16-n4096 library 16
build/cpu-baseline/hpu_scheme_case_generator ckks keyswitch 4096 \
  build/packages/ckks-keyswitch-l16-n4096 30 16
build/cpu-baseline/hpu_fixture_parameters ckks hmul 4096 library 16
build/cpu-baseline/hpu_fixture_parameters ckks keyswitch 4096 kernel 16
```

KeySwitch生成命令中的`30`是CKKS scale位数，最后的`16`才是Q的RNS分量数。
参数输出包含实际素数，交接CPU测试时应连同完整用例名、N、level一起保留。

`HPU_time_seconds = Cycle_SCPU / Frequency_SCPU_Hz`

`Speedup = Time_CPU_seconds / HPU_time_seconds`

跨机器不能直接拿188服务器CPU cycle除以SCPU cycle。未实测前不填写10×或通过结论。

## 参数与验收表

`scripts/export-case-inventory.py`从真实包的parameters、operation_graph、line_map和原生SEAL对象生成XLSX/JSON/CSV。
需要Python的openpyxl；无已连接Excel桌面会话时，检查文件结构和验证规则，不声称完成桌面渲染验证。
表格包含Q/P精确模数及乘积、位宽、RNS数量、L、dnum、密文分量、scale、CF、旋转参数、
BFV各层B/m_sk、种子、指令/DMA数量、DDR布局与版本。IT/ST通过格、实测时间和版本初始留空，填“✓”变绿色。
“可自检”“软件模型PASS”“编译通过”均不等于IT/ST实测通过。ST占位项和历史编号单独列出。
