# HPU用例分组与命名

在`master@ec3baa4a`的分组基础上增加固定组内编号；不改变指令序列、输入、golden、等待判据或依赖版本。
03独立子项只增加一条身份日志，默认仍不逐系数打印，静默版仍不输出UART。
初次目录整理前的主分支为`master@5a8ea073`，已备份到
[`backup/master-before-hputest-reorg-20261014-5a8ea073`](https://github.com/cuihu2/nexus-am/tree/backup/master-before-hputest-reorg-20261014-5a8ea073)。
仓库默认分支叫`master`，不是`main`。

## 分组边界

| 组 | 目标 | 目录 | 清单项/具备软件自检/未接入 |
|---|---|---|---|
| 00 | 冒烟、波形观察与结束通道探针 | `src/00_bringup` | 11/8/0，另含1项hold和2项返回值探针 |
| 01 | 正常配置/提交/状态、命令接收/参数配对、DDR回环与计算写回 | `src/01_configuration_and_data_paths` | 8/8/0 |
| 02 | 配置/地址/对象边界、命令压力与条件时序、RISC-V交叉、故障与看门狗 | `src/02_boundaries_and_cpu_interaction` | 22/19/3 |
| 03 | 单条指令和单stage变换 | `src/03_compute_instructions` | 18/18/0，原9项拆成37个独立子项，另有9项N65536 |
| 04 | BConv、整体NTT/INTT、KeySwitch、Auto与指令链编排 | `src/04_composite_instruction_sequences` | 18/17/1 |
| 05 | modified-SEAL算法库接口和独立参数回归 | `src/05_algorithm_library` | 54/52/2 |
| 06 | 完整应用指令图 | `src/06_full_application` | 9/8/1 |
| 07 | N65536算子/算法库的cycle测量及自检 | `src/07_performance` | 22/22/0 |

按照主要验收目标归类，而不是看到CSR初始化就放01、看到边界系数就移02。
例如03的PADD回绕是指令语义；02的窗口末端/越界是连接边界。05的HMUL内部调用KeySwitch，不等于04/05重复验收。

原02不再独立：普通命令/参数配对、回环、计算写回归01；条件时序与对象/DDR隔离归02。
原08中正常通道回环归01；队列8+1、条件时序、CPU交叉、异常/特权、连续命令和看门狗归02。
原07应用改为06；原06性能改为07，排在最后。

`01_03_dma_busy_transition`保留“实际观察BUSY再等待结束”的判据，`01_06_dma_loopback`保留数据回环判据，不能仅因刺激相似就删除其中一项。
`02_07_cmd_queue_8_plus_1`是配置命令与队列monitor入口，`02_12_cmd_burst_9`是九条连续算术命令，二者也不等价。

## 命名规则

父用例格式为`<两位组号>_<两位用例号>_<行为>[_必要参数]`；03独立子项为
`<组号>_<父用例号>_<两位子项号>_<行为>[_必要参数]`，描述部分全小写。
不再重复`HPU_IT_DIR`、`CFG`、`CMB`、`LIB_SEAL`等类别前缀。

每组跨子目录连续编号；编号一旦确定，不因名称或文件字母排序变化重算，新用例追加编号。
人际交流可直接称“00组06用例”或“03组01用例的02子项”。以下范围包含未接入记录，
未接入项只在清单占号，不发布占位ELF；不能根据下载目录缺少某个ELF推断漏写源码。

| 组 | 主清单编号 | 独立子项 |
|---|---|---|
| 00 | `00_01～00_11` | 无 |
| 01 | `01_01～01_08` | 无 |
| 02 | `02_01～02_22` | 无 |
| 03 | `03_01～03_18` | 前9项的37个子项，父用例内从01连续编号 |
| 04 | `04_01～04_18` | 无 |
| 05 | `05_01～05_54` | 无 |
| 06 | `06_01～06_09` | 无 |
| 07 | `07_01～07_22` | 无 |

| 层级 | 示例 | 参数含义 |
|---|---|---|
| 冒烟 | `00_06_loopback_mmio.c`、`00_08_compute_irq.c` | MMIO与CPU中断是不同同步判据 |
| 正常连接 | `01_04_cmd_handshake.c`、`01_05_dma_arg_pair.c` | 命令接收与x10/x11参数配对 |
| 边界/交叉 | `02_11_cmd_burst_8.c`、`02_15_cpu_hpu_alu_mix.c`、`02_17_watchdog_failstop.c` | `8`为算术命令条数，不是多项式规模 |
| 指令子项 | `03_03_06_pmul_imm255.elf`、`03_05_04_pntt_stage0_boundary.elf` | 对外子项号从01开始；内部`subcase`仍从0开始 |
| 算子 | `04_05_ckks_keyswitch_n4096.c` | 算法和规模确实影响输入/语义时才标注 |
| 算法库 | `05_31_bgv_hadd_cf3_cf5_n4096.c` | 区别于默认CF1/1的数据，不能合并 |
| 应用 | `06_03_bfv_mul_chain_n128.c` | 完整应用图，不是单个库接口 |
| 性能 | `07_01_ntt_n65536.c` | 与04_13共享输入/指令/golden，增加首尾cycle采样 |

父用例源码文件名与`case_id`一致；普通ELF/BIN/TXT使用用例名，静默版仅加`_silent`，二者不是两个覆盖点。
文件和ELF/BIN/TXT名称允许数字开头，C函数/变量/宏仍须是合法标识符。上游`program_stem`、`hpu_run_*`及数据目录是producer接口，不随测试编号重命名。

03子项复用父源码并通过固化的`mainargs=subcase=N`只选一项，不复制运算实现。
例如`03_03_06_pmul_imm255.elf`对应`03_03_pmul.c`中的一个子项；所有兄弟子项均通过才代表该父用例覆盖完整。
`03_01_01_padd_dst_p2.elf`固化`subcase=0`，`03_01_02_padd_alias_p0.elf`固化`subcase=1`。
普通/详细日志显示`[HPU][SUBTEST] id=03_01_01 subcase=0`这一身份记录；父源码路径也包含`03_01`。

## 清单和兼容对照

- [`cases.tsv`](../cases.tsv)：162个父用例，包含资格和源码；`group=core/transform/fhe`是构建数据依赖分类，不是00～07章节号。
- [`subtests/cases.tsv`](../subtests/cases.tsv)：37个独立子项、9个父用例、40段程序。
- [`case-migration.tsv`](../case-migration.tsv)：本次152个入口的原名/原路径→新名/新路径，历史列不再重写。
- [`case-numbering.tsv`](../case-numbering.tsv)：补编号前的152个短名/路径→带固定编号的名称/路径；完整编号分配以此表为准。
- [`case-aliases.tsv`](../case-aliases.tsv)：更早的CMB/APP/Poseidon名称及本次旧名直接对应当前名称，无多跳别名。
- [`scheme-cases.tsv`](../scheme-cases.tsv)：保持上游程序、算法、规模与角色绑定。
- [`blocked.tsv`](../blocked.tsv)：7项未接入原因；下载包中只发布索引，不发布占位ELF。
- [`archived-cases.tsv`](../archived-cases.tsv)：旧07的6项原样归档；历史记录仍指向归档源码，不映射成新规模通过结果。
- [`perf-cases.tsv`](../perf-cases.tsv)：07与04/05的22项精确镜像绑定。
- [`layer-migration.tsv`](../layer-migration.tsv)：之前04/05去重的历史证据，仍保留原始列。

统一包是183个测试身份×普通/静默两版，共366套ELF/BIN/TXT，另有7条未接入索引。
N65536扩展和计时定义见[N65536_PERFORMANCE.md](N65536_PERFORMANCE.md)。下载包的`provenance/testplan`携带迁移对照。

## 构建与验收

```sh
make -C tests/hputest all
make -C tests/hputest one CASE=01_configuration_and_data_paths/04_data_path/01_06_dma_loopback
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
