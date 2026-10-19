# 大规模功能与多规模性能交付

现有N128/N4096功能用例保留。N65536功能用例和07性能用例的范围如下：

| 分组 | 编号 | 内容 |
|---|---|---|
| 03 | 03_10～03_18 | PADD、PSUB、PMUL、PMAC、PNTT、PINTT、PMODLD、PSYNC、PFREE，N65536 |
| 04 | 04_12～04_18 | BConv、整体NTT、整体INTT、CKKS/BFV/BGV KeySwitch、完整NTT+Auto，N65536 |
| 05 | 05_40～05_54 | CKKS/BFV/BGV各5项：HADD、HMUL+Reline、Reline、Rescale/ModSwitch、Rotate，N65536 |
| 07 | 07_01～07_22 | N65536，上述04/05的22个计时镜像，使用相同生成包、输入、HPU指令及golden |
| 07 | 07_23～07_44 | N8192，相同22种操作，按本规模重新生成输入、程序及golden |
| 07 | 07_45～07_66 | N16384，相同22种操作，按本规模重新生成输入、程序及golden |
| 07 | 07_67～07_88 | N32768，相同22种操作，按本规模重新生成输入、程序及golden |

07共88项，每个ELF执行一段独立程序；本次新增三个规模，不把多个规模串在同一ELF里。
精确映射见[perf-cases.tsv](../perf-cases.tsv)：N65536行的`functional_case_id`对应现有04/05入口；
新增规模仅在07提供入口，故该列留空，实际规模和生成包由`degree`、`program_stem`标明。
旧07的6个入口已原样移至
`archive/performance_before_n65536/`，登记在`archived-cases.tsv`；不能把旧N4096通过记录继承给新N65536。

## 05与07的数量和职责

05验证算法库接口及参数组合；07测量选定操作在不同多项式长度下的执行耗时，同时保留结果与内存自检。

| 分组 | 规模与组成 | 总数 |
|---|---|---:|
| 05算法库 | CKKS/BFV/BGV各5项操作×N128/N4096/N65536，加7项特殊参数回归、2项未接入记录 | 54 |
| 原07性能 | 仅N65536：7项基本/组合算子＋15项算法库操作 | 22 |
| 当前07性能 | N8192/N16384/N32768/N65536，每种规模22项 | 88 |

每种规模的7项算子是整体NTT、整体INTT、BConv、三算法KeySwitch及完整NTT+Auto。
15项算法库操作是三算法各自的HADD、HMUL+Reline、Reline、Rescale/ModSwitch、Rotate。
05额外的7项是BGV的CF参数回归和三算法的Gen3旋转回归；2项未接入为encode、bootstrap。
这些特殊参数和未接入项不计作07性能基准；05的N128/N4096规模也未在07重复。

## 固定版本与语义

- SEAL、N65536基础指令及四种性能规模的BConv/NTT/INTT：`hpu-applications`锁定的inline-asm main，当前为`03a32c168404f3ad64e6a4d7ad82a081f910314b`。
- 完整NTT+Auto：沿用原04已使用的`inline-asm` legacy-main `69030963e71dbcf32897e8ae08695cfa2e65d79a`。main的旧Auto demo只做CPU预处理后的Galois KeySwitch，不作为完整Auto替代品。
- 两套生产者分别生成自己的编码和STG语义；AM不手写或拼接机器码。新03的PNTT/PINTT采用main的原位STG接口。
- 03新增的是单个N65536刺激，原N4096的37项边界/别名/立即数子测试仍保留；不声称N65536复制了所有旧subcase。
- 04的KeySwitch输入保留c2且c0/c1清零；05的Reline保留原c0/c1并合并。05 HMUL包含乘法及重线性化。
- 05继续逐原始物理word匹配modified-SEAL，不以解密近似误差放宽验收。BFV位序和CKKS只读输入shadow适配沿用既有接收器，不增加自造取整指令。

## 大数据内存要求

新增N65536功能用例和全部07性能用例的HPU窗口为`0x90000000`，旧N128/N4096功能用例仍为`0x87000000`。
必须给模拟RAM至少512MiB，例如本项目Difftest/VCS入口支持：

```text
+ram_size=536870912
```

仅修改模拟器RAM大小不等于修改硬件窗口：ELF内的BASE/SIZE仍由用例明确配置。
构建检查同时验证ELF装载末端不覆盖窗口、窗口加guard不越过512MiB RAM末端。
BFV HMUL的大镜像超过旧窗口前的可用空间，不能把新ELF装进仍按256MiB配置的环境。
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
[HPU][PERF] case=07_05_ckks_hmul_reline_n65536 N=65536 metric=issue_to_done_v2 start=... end=... cycles=... verified=1
```

建议每项独立执行至少3轮，使用`scripts/parse-perf-results.py`汇总真实日志：

```sh
python3 scripts/parse-perf-results.py run1.log run2.log run3.log \
  --revision 'AM=<commit>;RTL=<commit>' --output perf-results
```

解析器只接收当前88项的`issue_to_done_v2`且`verified=1`记录，按用例和规模分别汇总；旧口径或不完整记录会报错。
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
# scheme: ckks/bfv/bgv；op: hadd/hmul/reline/modswitch/rotate/keyswitch
# 本轮07对比N可选8192、16384、32768、65536；原128/4096功能规模也可复现。
# 服务器应记录CPU型号、频率、编译器和编译选项。
```

SEAL配置关闭HEXL；当前`sec_level_type::none`，参数只作demo，不是安全等级声明。
CPU对比必须用相同N、Q/P、密文分量、dnum、scale/CF、操作边界和输入。
原始RNS BConv/NTT/INTT/Auto不冒充SEAL算法库基准；这些项的CPU参考实现选择另行记录。

`HPU_time_seconds = Cycle_SCPU / Frequency_SCPU_Hz`

`Speedup = Time_CPU_seconds / HPU_time_seconds`

跨机器不能直接拿188服务器CPU cycle除以SCPU cycle。未实测前不填写10×或通过结论。

## 参数与验收表

`scripts/export-case-inventory.py`从真实包的parameters、operation_graph、line_map和原生SEAL对象生成XLSX/JSON/CSV。
需要Python的openpyxl；无已连接Excel桌面会话时，检查文件结构和验证规则，不声称完成桌面渲染验证。
表格包含Q/P精确模数及乘积、位宽、RNS数量、L、dnum、密文分量、scale、CF、旋转参数、
BFV各层B/m_sk、种子、指令/DMA数量、DDR布局与版本。IT/ST通过格、实测时间和版本初始留空，填“✓”变绿色。
“可自检”“软件模型PASS”“编译通过”均不等于IT/ST实测通过。ST占位项和历史编号单独列出。
