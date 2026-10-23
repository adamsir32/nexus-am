# 旧路径兼容入口

活动源码、唯一清单、依赖及构建已统一到[tests/hputest](../hputest/README.md)。本目录只有Makefile转发，不保留第二套用例或历史归档。

旧`make all/group/one/performance/silent`会进入同一个构建器；新用法及N/level筛选请直接使用`make -C tests/hputest`。默认下载仍只有一个`hpu.zip`，仅含ELF和BIN。
