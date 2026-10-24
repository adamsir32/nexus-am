#ifndef FRONTEND_PERFORMANCE_H
#define FRONTEND_PERFORMANCE_H

#include <hpu/perf.h>

/* 等待末尾PSYNC的真实CPU中断及VALID/空闲；不补清IRQ、不打印、不做结果自检。 */
int performance_wait(void);

#endif
