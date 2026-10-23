#include <workload.h>

/* 指令矩阵的参数和指令由当前用例清单选择，共享闭环负责同步与自检。 */
int main(void) {
    return native_case_run();
}
