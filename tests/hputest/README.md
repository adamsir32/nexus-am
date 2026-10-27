# HPU IT用例

活动源码、依赖和构建只保留本目录一份。[cases.tsv](cases.tsv)是唯一清单。默认交付一个`hpu.zip`，按00～07分组，只含ELF和BIN；源码和完整指令直接在GitHub本目录查看。

inline-asm固定在[producer.json](producer.json)：`feature/compute-profiling@4e26659`。main已包含原资源管理与ABI v4实现；当前选择官方连续计时实验分支，不修改SDK或RTL。

## 当前分组

| 组 | 范围 | 默认数量 |
|---|---|---:|
| 00 | 冒烟、波形hold、退出探针 | 11 |
| 01 | 配置、连接与数据通路 | 8 |
| 02 | 边界与RISC-V交叉 | 16 |
| 03 | 九条基础指令，仅N1024/level4 | 9 |
| 04 | BConv、整体NTT/INTT、三算法KeySwitch，仅N1024/level4 | 6 |
| 05 | 三算法×五种库操作，仅N1024/level4 | 15 |
| 06 | 上游完整应用，原参数保持；另有6项可选API诊断 | 8 |
| 07 | 三算法×六种操作×N1024/N8192，全部level4 | 36 |
| 合计 | 不包含6项可选API | 109 |

level始终是输入Q基的RNS分量数，不是SEAL chain_index，也不包含特殊P。降层后的输出可以少一个Q；例如输入level4的Rescale/ModSwitch输出通常为level3。

03～05已删除其它N/level的用例及其C/ASM，不再保留原N4096定向或特殊参数回归。07仅留两个N；BGV从旧level3真实改为level4，重新生成模数、数据、指令与golden，不能沿用旧L3的通过记录或性能数字。00～02保留原测试源码，06保留原参数但与03～07一起恢复CPU中断完成检查。

## 源码与编号

每例一份与case_id同名的C，完整写出配置、具名发令、等待和自检；只有底层接口共用。参数用例旁有同名`.asm`，07另有`.noopt.asm`。构建必须核对这些指令文本与固定生产者的原生包，不能只改文件名或参数标签。

所有组内号从01连续排列，统一两位，例如：

- `03_01_padd_l4_n1024.c`：PADD。
- `05_01_ckks_hadd_l4_n1024.c`：CKKS HADD。
- `07_13_bgv_keyswitch_l4_n1024.c`：BGV KeySwitch性能。

03～05文件直接放在各组目录，不再套多层N/level目录。07按`01_n1024`、`02_n8192`从小到大分目录。旧日志编号见[迁移表](docs/case-id-migration.tsv)，历史被移除源码从Git查看。

失败输出包含用例编号、具体C文件、source-line、阶段及STATUS/IRQ/FAULT；静默版在`workload_trace.source_line`保存失败行号。默认只输出短摘要与错误，不逐系数打印。

## 构建

```bash
git submodule update --init tests/hputest/third_party/inline-asm

make -C tests/hputest list
make -C tests/hputest all OUTPUT_ROOT=/disk/hpu/all
make -C tests/hputest group GROUP=05 OUTPUT_ROOT=/disk/hpu/library
make -C tests/hputest one CASE_ID=03_01_padd_l4_n1024 OUTPUT_ROOT=/disk/hpu/padd
make -C tests/hputest performance N=8192 OUTPUT_ROOT=/disk/hpu/perf-8192

# 另行按需构建，不混入默认下载包
make -C tests/hputest api OUTPUT_ROOT=/disk/hpu/api
make -C tests/hputest silent OUTPUT_ROOT=/disk/hpu/silent
```

每次使用新磁盘目录。失败任务仅在源码、清单、参数相同条件下用`RESUME=1`恢复；不能混用旧缓存。`VARIANT=noopt`只影响07，默认optimized。`WAIT_CYCLES`是软件完成等待预算，不等于仿真器的总cycle上限。

## 验证边界

`make test`运行契约测试，`make audit`核对独立入口、编号、参数范围、重复语义和源码引用。算法库参考仍为inline-asm自带modified-SEAL，原始结果逐word比较，不以近似解密相等掩盖错误。

03～06默认以末尾一次PSYNC触发真实CPU外部中断完成；07的官方profiled入口在预加载、主体和尾部边界使用PSYNC，每次均通过新的CPU外部中断事件确认。仅显式MMIO用例保留纯轮询。03_08仍验证空闲/DMA/计算各两轮，中间rearm和跨close/open后CTE只初始化一次。

07采用`execution_window_irq_v1`、`profile=continuous`：排除安全预加载及原有尾部写回，计入全部算术、主体必要DMA、CPU发令和完成回调/中断开销，不是纯计算cycle。沿用官方`hpu_run_*_profiled(hooks,sample)`和两次clock hook，不自行拆指令或改写原生C，详见[性能口径](docs/PERFORMANCE.md)。旧端到端`issue_to_irq_done_v1`及MMIO口径`issue_to_done_v2`不与新样本混合统计。

构建、软件模型和ELF检查不是RTL/FPGA通过。新版程序仍需匹配64对象、NTT ABI v4及在线PMUL mode=1的RTL。`00_01`故意无限保持，`00_11`故意返回1，不能要求所有ELF都返回0。Poseidon/watchdog条件实验仍在`tests/hpu-experiments`，不进入默认包。
