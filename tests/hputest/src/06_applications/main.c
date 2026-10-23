#include <workload.h>

/* 应用链保留上游程序，复用相同的配置、完成同步和内存保护检查。 */
int main(void) {
    return native_case_run();
}
