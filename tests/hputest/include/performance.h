#ifndef FRONTEND_PERFORMANCE_H
#define FRONTEND_PERFORMANCE_H

#include <hpu/perf.h>

/* 仅等待本段程序的末尾PSYNC；不清IRQ、不打印、不执行结果自检。 */
int performance_wait(void);

#endif
