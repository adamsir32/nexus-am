#include <performance.h>
#include <workload.h>

int performance_wait(void) {
    /* 与功能用例相同的ISR完成判据；此等待绝不打印、补清IRQ或替代中断。 */
    return wait_program();
}
