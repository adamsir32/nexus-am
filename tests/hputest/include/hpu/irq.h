#ifndef HPU_IRQ_H
#define HPU_IRQ_H

#include <stdint.h>

/*
 * HPU 完成中断固定接到 PLIC source 257、S-mode context 1。
 * 用例在发 PSYNC 前调用 irq_open()，再用 irq_wait() 等待处理函数。
 */
int irq_open(void);
/* 纯软件观测：0=尚无ISR完成，1=source257已清除并complete，-1=ISR错误。
 * 不读HPU/PLIC MMIO，不打印；计时区间可反复调用，超时由调用者按cycle预算判定。 */
int irq_poll(void);
/* 累计计数跨close/open/rearm保留；event只计成功source257完成，handler计全部入口。 */
uint32_t irq_event_count(void);
uint32_t irq_handler_count(void);
uint32_t irq_cte_init_count(void);
/* 仅closed状态可显式清除事件/诊断计数；永不重置一次性CTE初始化状态。 */
int irq_reset_events(void);
/* 仅输出缓存的ISR现场，不额外读取/claim硬件；由调用者在计时结束后调用。 */
void irq_diagnose(const char *phase, unsigned polls);
/* W1C清除HPU IRQ，并轮询确认电平已经真正撤销。 */
int irq_clear_and_verify(void);
int irq_wait(void);
/* 等待处理函数清除并complete上一轮中断后，重置完成标志供下一阶段使用。 */
int irq_rearm(void);
void irq_close(void);

#endif
