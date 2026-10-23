#include <workload.h>

/* 原生组合算子的计算来自固定版本inline-asm，不在目标端重写算法。 */
int main(void) {
    return native_case_run();
}
