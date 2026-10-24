NAME := am
LIBS := klib
SRCS = $(addprefix src/, $(AM_SRCS))

# HPU用例只传递这个模式变量，不把用例的CFLAGS泄漏到AM/klib递归构建。
LINKNAN_HPU_IT ?= 0
ifeq ($(filter $(LINKNAN_HPU_IT),0 1),)
$(error LINKNAN_HPU_IT must be 0 or 1)
endif
ifeq ($(LINKNAN_HPU_IT),1)
CFLAGS += -DLINKNAN_HPU_IT=1
endif

include $(AM_HOME)/Makefile.lib

# 同一ARCH的AM对象不能在CPU-PMP和HPU-DDR策略之间静默复用。
# 内容不变则保持时间戳，连续同模式构建不重复编译。
AM_HPU_MODE_STAMP := $(DST_DIR)/.hpu-mode
.PHONY: am-hpu-mode-force
$(AM_HPU_MODE_STAMP): am-hpu-mode-force
	@mkdir -p "$(dir $@)"
	@printf 'LINKNAN_HPU_IT=%s\n' '$(LINKNAN_HPU_IT)' > "$@.new"
	@if cmp -s "$@.new" "$@"; then rm -f "$@.new"; else mv -f "$@.new" "$@"; fi
$(OBJS) $(ARCHIVE): $(AM_HPU_MODE_STAMP)
