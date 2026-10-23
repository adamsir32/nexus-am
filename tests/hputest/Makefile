.DEFAULT_GOAL := all
AM_HOME ?= $(abspath ../..)
ARCH ?= riscv64-xs
CROSS_COMPILE ?= riscv64-linux-gnu-
INLINE_ASM_ROOT ?= $(CURDIR)/third_party/inline-asm
OUTPUT_ROOT ?= $(CURDIR)/build/runtime
JOBS ?= 4
WAIT_CYCLES ?= 25000000
LOG_LEVEL ?= 1
VARIANT ?= optimized
SUITE ?= default
CASE_ID ?= $(CASE)

FILTERS = $(if $(GROUP),--group "$(GROUP)") $(if $(CASE_ID),--case "$(CASE_ID)") \
          $(if $(N),--degree "$(N)") $(if $(LEVEL),--level "$(LEVEL)") \
          $(if $(SCHEME),--scheme "$(SCHEME)")
BUILD = python3 scripts/build-runtime.py --am-home "$(AM_HOME)" --arch "$(ARCH)" \
        --cross "$(CROSS_COMPILE)" --producer "$(INLINE_ASM_ROOT)" --output "$(OUTPUT_ROOT)" \
        --jobs "$(JOBS)" --wait-cycles "$(WAIT_CYCLES)" --suite "$(SUITE)" \
        --variant "$(VARIANT)" --log-level "$(LOG_LEVEL)" $(FILTERS)

.PHONY: all group one performance silent api list audit test help
all:
	$(BUILD) $(if $(filter 1,$(RESUME)),--resume)

group:
	@test -n "$(GROUP)" || { echo '需要GROUP=00～07'; exit 2; }
	$(BUILD) $(if $(filter 1,$(RESUME)),--resume)

one:
	@test -n "$(CASE_ID)" || { echo '需要CASE_ID=用例编号'; exit 2; }
	$(BUILD) $(if $(filter 1,$(RESUME)),--resume)

performance:
	$(MAKE) --no-print-directory group GROUP=07

silent:
	$(MAKE) --no-print-directory all LOG_LEVEL=0

api:
	$(MAKE) --no-print-directory all SUITE=api

list:
	@$(BUILD) --list

audit:
	python3 scripts/audit_sources.py --repo "$(AM_HOME)" --report "$(OUTPUT_ROOT)/source-audit.tsv"

test:
	python3 -m unittest discover -s scripts -p 'test_*.py'

help:
	@printf '%s\n' 'all：711项默认用例，导出一个hpu.zip（ELF+BIN）' \
	  'group GROUP=03 N=8192 LEVEL=4：筛选功能参数' \
	  'one CASE_ID=03_010_padd_l1_n128：只编一项' \
	  'list：只读清单，不生成文件；可按GROUP/N/LEVEL/SCHEME筛选' \
	  'performance：07组最高层性能；api：6项可选顶层API诊断' \
	  'silent：关闭UART；test/audit：契约单测与源码/清单检查' \
	  'OUTPUT_ROOT使用新目录；失败后RESUME=1恢复同一源码和参数'
