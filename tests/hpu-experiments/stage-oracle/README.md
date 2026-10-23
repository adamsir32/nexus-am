# 历史单stage RTL dump对照

旧`test-stage-reference.py`中的两项固定CSV对照依赖上游已移除的
`test/fixtures/ntt_hw_ut/rtl_pntt`和`rtl_pintt`数据。本目录仅保留该历史检查，
不属于默认IT，不以跳过测试或新造“RTL结果”代替缺失证据。

如需复查，显式提供原始历史CSV目录：

```sh
python3 test_stage_dumps.py --fixtures /path/to/historical/ntt_hw_ut
```

该脚本只在主机编译当前独立C`stage_golden`并对比旧CSV，不运行RTL，
也不能证明当前ISA/RTL已经通过。本次只隔离入口，没有原始CSV可供重新验证。
默认主机测试保留所有stage/loader、独立DFT/roundtrip和非法参数检查。
