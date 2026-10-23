# 兼容旧命令；所有源码、依赖、清单和实际构建只有hputest一份。
.DEFAULT_GOAL := all
.PHONY: all minimal silent group one performance api frontend-six list test audit help
all minimal silent group one performance api list test audit help:
	$(MAKE) --no-print-directory -C ../hputest $(if $(filter minimal,$@),all,$@)
frontend-six:
	$(MAKE) --no-print-directory -C ../hputest api
