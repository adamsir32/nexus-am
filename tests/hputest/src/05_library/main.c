#include <workload.h>

/* SEAL算法库级用例只执行一个清单条目，结果与独立golden逐字比较。 */
int main(void) {
    return native_case_run();
}
