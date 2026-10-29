#ifndef PIR_UNIFIED_RUNTIME_H
#define PIR_UNIFIED_RUNTIME_H

void pir_prepare_stage0(void);
void pir_prepare_stage1(void);
int pir_check_stage0(void);
int pir_check_stage1(void);
int pir_check_stage1_fixed_before_issue(void);

#endif
