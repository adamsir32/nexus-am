# 当前入口只调用新版按组运行包，不执行历史340项准备/打包流水线。
HPU_TEST_ROOT := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
AM_HOME ?= $(abspath $(HPU_TEST_ROOT)/../..)
ARCH ?= riscv64-xs
CROSS_COMPILE ?= riscv64-linux-gnu-
OUTPUT_ROOT ?= $(AM_HOME)/tests/hpu_frontend_workload/build-runtime
JOBS ?= 4
INLINE_ASM_ROOT ?= $(AM_HOME)/tests/hpu_frontend_workload/third_party/inline-asm
CASE_ID ?= $(CASE)

RUNTIME_BUILD = python3 "$(AM_HOME)/tests/hpu_frontend_workload/scripts/build-runtime.py" \
  --am-home "$(AM_HOME)" --producer "$(INLINE_ASM_ROOT)" \
  --output "$(OUTPUT_ROOT)" --jobs "$(JOBS)" \
  --cross "$(CROSS_COMPILE)" --arch "$(ARCH)"

.DEFAULT_GOAL := all
.PHONY: all group one

all:
	@$(RUNTIME_BUILD)

group:
	@case "$(GROUP)" in 00|01|02|03|04|05|06|07) ;; \
	  *) echo '用法：make group GROUP=00（范围00～07）' >&2; exit 2 ;; esac
	@$(RUNTIME_BUILD) --group "$(GROUP)"

one:
	@test -n "$(CASE_ID)" || { echo '用法：make one CASE_ID=03_05_pntt' >&2; exit 2; }
	@$(RUNTIME_BUILD) --case "$(CASE_ID)"
