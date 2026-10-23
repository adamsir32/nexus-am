# 组织与参数规则

唯一权威输入是`../cases.tsv`；没有scheme/large/perf三套重叠清单，也没有另一个目录保存同版用例。

- 00验证可运行的最小闭环和退出路径；01验证配置、连接与数据通路；02验证边界及CPU交叉。
- 03是指令层：普通模运算、单stage、上下文、同步及释放；RNS分量逐一真实切换，raw不等于某个加密方案。
- 04是基本/组合算子：整体变换、跨基转换和KeySwitch核心。
- 05是CKKS/BFV/BGV算法库接口：HADD、HMUL+Reline、Reline、Rescale/ModSwitch、Rotate。
- 06是依赖图完整应用；`suite=api`另外选择顶层Evaluator对照，不进入默认包。
- 07是代表参数的性能记录；不把cycle读取加进03～05来冒充功能测试。

level始终是输入Q分量数，特殊P单列于native参数。原profile的Q/P、seed及最高level输入保持对照；较小level取实际子基并约束CKKS scale，不套用超出Q容量的编码。模数具体值、bit数、scale、密钥和数据以固定版本生成包的metadata为准，不凭N或方案名猜参数。

组内号连续；03～05统一三位，矩阵按N再level递增。03定向和05特殊回归各自单列profile，不能用排序掩盖不同测试目标。每行对应一个参数场景和一个同名C文件，不能复用共享main，也不能把多个N/level串行塞进一个ELF。

每项C完整写出窗口配置、具体发令函数、完成等待、结果与guard检查；每个失败分支调用`case_fail_at(__FILE__, __LINE__)`，让UART和静默trace都能回查具体源码。仅MMIO、镜像/cache、等待及比较等单一职责底层函数保留共用。

同名`.asm`保存完整HPU指令源码，07的noopt另用`.noopt.asm`。构建时核对源码与当前上游原生包，不能悄悄重写源码或拿展示副本替代真实指令；源文件、清单、原生包和ELF必须相互对应。

指令/算法生成、软件golden及目标端同步自检严格分层。算法图沿用inline-asm；03 raw使用独立整数/C stage参考而不伪称SEAL。生成包缺失任何声明输出、出现未知ABI或参数不支持时直接停止，不跳过结果、不补假的成功用例。
