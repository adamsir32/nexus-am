# HPU用例分组与命名

本次只迁移目录、名称和构建/发布索引，不改变指令序列、输入、golden、等待判据或依赖版本。
迁移前默认分支为`master@5a8ea073`，已备份到
[`backup/master-before-hputest-reorg-20261014-5a8ea073`](https://github.com/cuihu2/nexus-am/tree/backup/master-before-hputest-reorg-20261014-5a8ea073)。
仓库默认分支叫`master`，不是`main`。

## 分组边界

| 组 | 目标 | 目录 | 清单项/具备软件自检/未接入 |
|---|---|---|---|
| 00 | 冒烟、波形观察与结束通道探针 | `src/00_bringup` | 11/8/0，另含1项hold和2项返回值探针 |
| 01 | 正常配置/提交/状态、命令接收/参数配对、DDR回环与计算写回 | `src/01_configuration_and_data_paths` | 8/8/0 |
| 02 | 配置/地址/对象边界、命令压力与条件时序、RISC-V交叉、故障与看门狗 | `src/02_boundaries_and_cpu_interaction` | 22/19/3 |
| 03 | 单条指令和单stage变换 | `src/03_compute_instructions` | 9/9/0，默认交付拆成37个独立子项 |
| 04 | BConv、整体NTT/INTT、KeySwitch、Auto与指令链编排 | `src/04_composite_instruction_sequences` | 11/10/1 |
| 05 | modified-SEAL算法库接口和独立参数回归 | `src/05_algorithm_library` | 39/37/2 |
| 06 | 完整应用指令图 | `src/06_full_application` | 9/8/1 |
| 07 | 功能检查通过后的CPU/HPU性能对比 | `src/07_performance` | 6/2/4 |

按照主要验收目标归类，而不是看到CSR初始化就放01、看到边界系数就移02。
例如03的PADD回绕是指令语义；02的窗口末端/越界是连接边界。05的HMUL内部调用KeySwitch，不等于04/05重复验收。

原02不再独立：普通命令/参数配对、回环、计算写回归01；条件时序与对象/DDR隔离归02。
原08中正常通道回环归01；队列8+1、条件时序、CPU交叉、异常/特权、连续命令和看门狗归02。
原07应用改为06；原06性能改为07，排在最后。

`01_dma_busy_transition`保留“实际观察BUSY再等待结束”的判据，`01_dma_loopback`保留数据回环判据，不能仅因刺激相似就删除其中一项。
`02_cmd_queue_8_plus_1`是配置命令与队列monitor入口，`02_cmd_burst_9`是九条连续算术命令，二者也不等价。

## 命名规则

格式为`<两位组号>_<行为>[_必要参数]`，全小写，以单下划线分隔。不再重复`HPU_IT_DIR`、`CFG`、`CMB`、`LIB_SEAL`或组内流水号。

| 层级 | 示例 | 参数含义 |
|---|---|---|
| 冒烟 | `00_loopback_mmio.c`、`00_compute_irq.c` | MMIO与CPU中断是不同同步判据 |
| 正常连接 | `01_cmd_handshake.c`、`01_dma_arg_pair.c` | 命令接收与x10/x11参数配对 |
| 边界/交叉 | `02_cmd_burst_8.c`、`02_cpu_hpu_alu_mix.c`、`02_watchdog_failstop.c` | `8`为算术命令条数，不是多项式规模 |
| 指令子项 | `03_pmul_imm255.elf`、`03_pntt_stage0_boundary.elf` | 子项号在清单的`subcase`列，不重复写进文件名 |
| 算子 | `04_ckks_keyswitch_n4096.c` | 算法和规模确实影响输入/语义时才标注 |
| 算法库 | `05_bgv_hadd_cf3_cf5_n4096.c` | 区别于默认CF1/1的数据，不能合并 |
| 应用 | `06_bfv_mul_chain_n128.c` | 完整应用图，不是单个库接口 |
| 性能 | `07_ntt_n4096.c` | 与04功能用例共享算子，但验收cycle统计 |

源码文件名、`case_id`和交付文件stem一致。普通版使用原名，静默版仅加`_silent`；二者不是两个覆盖点。
文件和ELF/BIN/TXT名称允许数字开头，C函数/变量/宏仍须是合法标识符。上游`program_stem`、`hpu_run_*`及数据目录是producer接口，不随测试编号重命名。

03子项复用父源码并通过固化的`mainargs=subcase=N`只选一项，不复制运算实现。
例如`03_pmul_imm255.elf`对应`03_pmul.c`中的一个子项；所有兄弟子项均通过才代表该父用例覆盖完整。

## 清单和兼容对照

- [`cases.tsv`](../cases.tsv)：115个父用例，包含资格和源码；`group=core/transform/fhe`是构建数据依赖分类，不是00～07章节号。
- [`subtests/cases.tsv`](../subtests/cases.tsv)：37个独立子项、9个父用例、40段程序。
- [`case-migration.tsv`](../case-migration.tsv)：本次152个入口的原名/原路径→新名/新路径，历史列不再重写。
- [`case-aliases.tsv`](../case-aliases.tsv)：更早的CMB/APP/Poseidon名称及本次旧名直接对应当前名称，无多跳别名。
- [`scheme-cases.tsv`](../scheme-cases.tsv)：保持上游程序、算法、规模与角色绑定。
- [`blocked.tsv`](../blocked.tsv)：11项未接入原因；下载包中只发布索引，不发布占位ELF。
- [`layer-migration.tsv`](../layer-migration.tsv)：之前04/05去重的历史证据，仍保留原始列。

统一包仍是132个测试身份×普通/静默两版，共264套ELF/BIN/TXT，另有11条未接入索引。
本次不新增覆盖，也不把此前未接入的测试改称已实现。下载包的`provenance/testplan`携带迁移对照。

## 构建与验收

```sh
make -C tests/hputest all
make -C tests/hputest one CASE=01_configuration_and_data_paths/04_data_path/01_dma_loopback
make -C tests/hputest subtests
make -C tests/hputest silent
make -C tests/hputest silent-subtests
make -C tests/hputest unified
```

统一包还需要先按工作流调用`package-chapters.py ... --all/--silent`生成两个workload输入；完整顺序见主README和CI。
旧名称用于对照，`make one CASE=`使用迁移后的源码路径；未承诺旧路径仍可编译。

软件`return 0`不替代ready反压、CDC、队列满载、提交/错误路径副作用等monitor证据。
原STING项仍只提供确定性激励；外部随机驱动、seed/replay和覆盖率未接入前不计随机覆盖。
看门狗三例要求匹配RTL、每例独立复位，预期故障不能套用普通成功中断流程。
默认精简日志和静默模式保持不变，不为整理名称恢复逐系数UART输出。
实验性新前端workload、Poseidon目录及RTL不参与本次迁移。
