# 2026-10-23归档：level16用例

为将`1019-operator-resource-perf`活动用例限制在N≤8192、输入level≤4，本目录保留移出的36项level16历史源码及清单：

| 原编号 | N | 输入level | 数量 |
| --- | --- | --- | --- |
| 07_19～07_36 | 4096 | 16 | 18 |
| 07_55～07_72 | 8192 | 16 | 18 |

归档内容不参与活动构建、CI或下载包；当前构建和生成器入口拒绝已停用的`l16`配置。保留源码供历史追溯，不删除旧实验记录，也不重新编号活动用例。

当前活动清单见[performance-cases.tsv](../../performance-cases.tsv)，说明见[PERFORMANCE.md](../../PERFORMANCE.md)：共36项，N4096/N8192，CKKS/BFV为level4，BGV保留原level3。旧版level16验证记录不代表当前inline-asm版本或RTL/硬件已经通过。
