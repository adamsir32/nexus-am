AM_HOME ?= $(abspath ../..)
ARCH ?= riscv64-xs
CROSS_COMPILE ?= riscv64-linux-gnu-
OUTPUT_ROOT ?= $(CURDIR)/build
INLINE_ASM_ROOT ?= $(CURDIR)/third_party/inline-asm
PRODUCER_BUILD ?= $(OUTPUT_ROOT)/producer-build
PACKAGE_ROOT ?= $(OUTPUT_ROOT)/packages
JOBS ?= 4
WAIT_CYCLES ?= 25000000
DEGREE ?= 4096
PROFILE ?= baseline
SCHEME ?= ckks
MODE ?= both

.PHONY: all minimal silent performance test
# 独立workload：不运行旧hputest的数据生成，不更新其任何依赖或清单。
all minimal silent:
	python3 scripts/build.py --mode $(if $(filter all,$@),both,$@) \
	  --am-home "$(AM_HOME)" --arch "$(ARCH)" --cross "$(CROSS_COMPILE)" \
	  --output "$(OUTPUT_ROOT)" --producer "$(INLINE_ASM_ROOT)" \
	  --producer-build "$(PRODUCER_BUILD)" --packages "$(PACKAGE_ROOT)" \
	  --jobs "$(JOBS)" --wait-cycles "$(WAIT_CYCLES)"

# 新07独立构建，单个分片六项算子；不重跑上面的六项应用图。
performance:
	python3 scripts/build_performance.py --am-home "$(AM_HOME)" \
	  --arch "$(ARCH)" --cross "$(CROSS_COMPILE)" \
	  --producer "$(INLINE_ASM_ROOT)" --output "$(OUTPUT_ROOT)" \
	  --degree "$(DEGREE)" --profile "$(PROFILE)" --scheme "$(SCHEME)" \
	  --mode "$(MODE)" --jobs "$(JOBS)" --wait-cycles "$(WAIT_CYCLES)" \
	  $(if $(CASE_ID),--case-id "$(CASE_ID)")

test:
	python3 -m unittest discover -s scripts -p 'test_*.py'
