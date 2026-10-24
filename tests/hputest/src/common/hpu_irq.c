#include <hpu/log.h>
#include <am.h>
#ifdef HPU_NATIVE_IRQ
#include <platform.h>
#else
#include <hpu/csr.h>
#include <hpu/layout.h>
#endif
#include <hpu/irq.h>
#include <klib.h>
#include <xsextra.h>
#include <xs.h>

#include <stddef.h>
#include <stdint.h>

#ifndef TIMEOUT
#define TIMEOUT 20000000U
#endif

#define PLIC_SOURCE         257U
#define PLIC_PRIORITY_INDEX (PLIC_SOURCE - 1U)
#define PLIC_CONTEXT_S      1U
#define SIE_SEIE            (UINT64_C(1) << 9U)

/* 与 AM 的 plic_init() 共用平台地址，不在用例层另设 PLIC 基址。 */

#define PLIC_PRIORITY_ADDR \
    (PLIC_BASE_ADDR + UINT64_C(0x4) + \
     (uint64_t)PLIC_PRIORITY_INDEX * sizeof(uint32_t))
#define PLIC_ENABLE_ADDR \
    (PLIC_BASE_ADDR + UINT64_C(0x2000) + \
     (uint64_t)PLIC_CONTEXT_S * UINT64_C(0x80) + \
     (uint64_t)(PLIC_SOURCE / 32U) * sizeof(uint32_t))
#define PLIC_THRESHOLD_ADDR \
    (PLIC_BASE_ADDR + UINT64_C(0x200000) + \
     (uint64_t)PLIC_CONTEXT_S * UINT64_C(0x1000))
#define PLIC_CLAIM_ADDR \
    (PLIC_BASE_ADDR + UINT64_C(0x200004) + \
     (uint64_t)PLIC_CONTEXT_S * UINT64_C(0x1000))

extern int g_config_disable_timer;

static uint32_t mmio_read32(uint64_t address) {
    return *(volatile uint32_t *)(uintptr_t)address;
}

static void mmio_write32(uint64_t address, uint32_t data) {
    *(volatile uint32_t *)(uintptr_t)address = data;
}

static uint32_t hpu_plic_claim(void) {
    return mmio_read32(PLIC_CLAIM_ADDR);
}

static void hpu_plic_complete(uint32_t claim) {
    mmio_write32(PLIC_CLAIM_ADDR, claim);
}

static void hpu_plic_enable(void) {
    uint32_t enable = mmio_read32(PLIC_ENABLE_ADDR);

    mmio_write32(PLIC_ENABLE_ADDR,
                 enable | (1U << (PLIC_SOURCE % 32U)));
}

static void hpu_plic_disable(void) {
    uint32_t enable = mmio_read32(PLIC_ENABLE_ADDR);

    mmio_write32(PLIC_ENABLE_ADDR,
                 enable & ~(1U << (PLIC_SOURCE % 32U)));
}

/* 初始化/重新准备后由中断处理函数写，主程序仅轮询完成标志。 */
static volatile uint32_t irq_done;
static volatile uint32_t irq_error;
static uint32_t irq_cte_attempted;
static uint32_t irq_cte_ready;
static volatile uint32_t irq_opened;
static volatile uint32_t irq_events;
static volatile uint32_t irq_handlers;

enum {
    IRQ_BAD_EVENT = 1U,
    IRQ_BAD_CLAIM,
    IRQ_MISSING_LEVEL,
    IRQ_CLEAR_TIMEOUT,
    IRQ_HPU_FAULT,
    IRQ_UNARMED_EVENT
};

/* ISR 内不调用 printf；只保存已经读到的现场，由 irq_wait() 在失败后输出。 */
static volatile uint32_t irq_handler_seen;
static volatile int irq_last_event;
static volatile uint32_t irq_last_claim;
static volatile uint32_t irq_last_level;
static volatile uint32_t irq_last_status;
static volatile uint32_t irq_last_fault;
static volatile uint32_t irq_clear_last;
static volatile uint32_t irq_clear_polls;

static void irq_reset_round(void) {
    irq_done = 0U;
    irq_error = 0U;
    irq_handler_seen = 0U;
    irq_last_event = 0;
    irq_last_claim = 0U;
    irq_last_level = 0U;
    irq_last_status = 0U;
    irq_last_fault = 0U;
    irq_clear_last = 0U;
    irq_clear_polls = 0U;
}

int irq_poll(void) {
    /* done先读、error后读：ISR若插在两次读取之间，也不会把新错误误报成成功。 */
    uint32_t done = irq_done;
    uint32_t error = irq_error;
    if (error != 0U) return -1;
    return done == 1U ? 1 : 0;
}

uint32_t irq_event_count(void) { return irq_events; }
uint32_t irq_handler_count(void) { return irq_handlers; }
uint32_t irq_cte_init_count(void) { return irq_cte_attempted; }

int irq_reset_events(void) {
    if (irq_opened != 0U) return 1;
    irq_events = 0U;
    irq_handlers = 0U;
    irq_reset_round();
    return 0;
}

int irq_clear_and_verify(void) {
    unsigned timeout;
    uint32_t level = 0U;

    csr_write(CSR_IRQ, IRQ_LEVEL);
    for (timeout = 0U; timeout < TIMEOUT / 16U; ++timeout) {
        level = csr_read(CSR_IRQ);
        if ((level & IRQ_LEVEL) == 0U) break;
    }
    csr_write(CSR_IRQ, 0U);
    irq_clear_last = level;
    irq_clear_polls = timeout == TIMEOUT / 16U ? timeout : timeout + 1U;
    return timeout == TIMEOUT / 16U ? 1 : 0;
}

static _Context *handler(_Event event, _Context *context) {
    uint32_t claim;

    ++irq_handlers;
    irq_handler_seen = 1U;
    irq_last_event = event.event;
    if (event.event != _EVENT_IRQ_IODEV) {
        irq_error = IRQ_BAD_EVENT;
        irq_done = 1U;
        return context;
    }

    claim = hpu_plic_claim();
    irq_last_claim = claim;
    if (claim != PLIC_SOURCE) {
        irq_error = IRQ_BAD_CLAIM;
        if (claim != 0U) hpu_plic_complete(claim);
        irq_done = 1U;
        return context;
    }

    irq_last_level = csr_read(CSR_IRQ);
    irq_last_status = csr_read(CSR_STATUS);
    irq_last_fault = csr_read(CSR_FAULT);
    if (irq_opened == 0U || irq_done != 0U) irq_error = IRQ_UNARMED_EVENT;
    if ((irq_last_status & STATUS_FAULT) != 0U ||
        (irq_last_fault & FAULT_VALID) != 0U) irq_error = IRQ_HPU_FAULT;
    if ((irq_last_level & IRQ_LEVEL) == 0U) {
        irq_error = IRQ_MISSING_LEVEL;
    } else if (irq_clear_and_verify() != 0) {
        irq_error = IRQ_CLEAR_TIMEOUT;
    }
    hpu_plic_complete(claim);
    if (irq_error == 0U) ++irq_events;
    irq_done = 1U;
    return context;
}

int irq_open(void) {
    int rc;

    _intr_write(0);
    /* HPU中断用例只观察外部中断，禁止CTE同时打开定时器中断。 */
    g_config_disable_timer = 1;
    /* 首次CTE会从M降到S；close不升回M，任何后续open都不能重走M态CSR初始化。
     * 即使首次CTE返回失败，也不重试可能已部分降权的一次性路径。 */
    if (irq_cte_attempted == 0U) {
        irq_cte_attempted = 1U;
        rc = _cte_init(NULL);
        if (rc != 0) {
            LOG_ERROR("[HPU][IRQ][FAIL] phase=open reason=cte-init rc=%d\n", rc);
            return 1;
        }
        irq_cte_ready = 1U;
    }
    if (irq_cte_ready == 0U) return 1;
    _intr_write(0);
    irq_opened = 0U;
    hpu_plic_disable();
    mmio_write32(PLIC_PRIORITY_ADDR, 0U);
    irq_reset_round();

    /* 先确认旧完成电平已撤销，再武装PLIC，避免把旧事件当成本轮结果。 */
    if (irq_clear_and_verify() != 0) {
        LOG_ERROR("[HPU][IRQ][FAIL] phase=open reason=stale-level-clear-timeout "
               "clear-last=0x%x clear-polls=%u\n",
               irq_clear_last, irq_clear_polls);
        return 1;
    }

    seip_handler_reg(handler);
    mmio_write32(PLIC_PRIORITY_ADDR, 1U);
    mmio_write32(PLIC_THRESHOLD_ADDR, 0U);
    hpu_plic_enable();
    __asm__ volatile("fence iorw, iorw" : : : "memory");

    /* 配置地址错误时在这里失败，不再等到irq_wait()超时。 */
    {
        uint32_t priority = mmio_read32(PLIC_PRIORITY_ADDR);
        uint32_t enable = mmio_read32(PLIC_ENABLE_ADDR);
        uint32_t threshold = mmio_read32(PLIC_THRESHOLD_ADDR);

        LOG_DEBUG("[HPU][IRQ] plic=0x%lx priority=0x%x enable=0x%x "
               "threshold=0x%x\n",
               (unsigned long)PLIC_BASE_ADDR, priority, enable, threshold);
        if (priority != 1U) {
            LOG_ERROR("[HPU][IRQ][FAIL] phase=open reason=plic-priority actual=0x%x expected=1 source=%u\n",
                   priority, PLIC_SOURCE);
            return 1;
        }
        if ((enable & (1U << (PLIC_SOURCE % 32U))) == 0U) {
            LOG_ERROR("[HPU][IRQ][FAIL] phase=open reason=plic-enable actual=0x%x required-mask=0x%x\n",
                   enable, 1U << (PLIC_SOURCE % 32U));
            return 1;
        }
        if (threshold != 0U) {
            LOG_ERROR("[HPU][IRQ][FAIL] phase=open reason=plic-threshold actual=0x%x expected=0\n",
                   threshold);
            return 1;
        }
    }
    __asm__ volatile("csrs sie, %0" : : "r"(SIE_SEIE) : "memory");
    irq_opened = 1U;
    _intr_write(1);
    return 0;
}

void irq_diagnose(const char *phase, unsigned polls) {
    uint32_t error = irq_error;
    const char *reason;
    switch (error) {
    case 0U: reason = "timeout"; break;
    case IRQ_BAD_EVENT: reason = "unexpected-event"; break;
    case IRQ_BAD_CLAIM: reason = "unexpected-claim"; break;
    case IRQ_MISSING_LEVEL: reason = "hpu-level-missing"; break;
    case IRQ_CLEAR_TIMEOUT: reason = "clear-level-timeout"; break;
    case IRQ_HPU_FAULT: reason = "hpu-fault"; break;
    case IRQ_UNARMED_EVENT: reason = "unarmed-event"; break;
    default: reason = "unknown-handler-error"; break;
    }
    /* 只打印缓存现场，不为诊断额外 claim PLIC 或读取 HPU MMIO。 */
    LOG_ERROR("[HPU][IRQ][FAIL] phase=%s reason=%s polls=%u handler-seen=%u "
           "done=%u error=%u event=%d claim=%u expected-claim=%u irq=0x%x "
           "status=0x%x fault=0x%x clear-last=0x%x clear-polls=%u "
           "events=%u handlers=%u cte-init=%u\n",
           phase, reason, polls, irq_handler_seen, irq_done, error, irq_last_event,
           irq_last_claim, PLIC_SOURCE, irq_last_level, irq_last_status, irq_last_fault,
           irq_clear_last, irq_clear_polls, irq_events, irq_handlers, irq_cte_attempted);
}

int irq_wait(void) {
    unsigned timeout;
    for (timeout = 0U; timeout < TIMEOUT; ++timeout) {
        int state = irq_poll();
        if (state < 0) {
            irq_diagnose("wait", timeout);
            return 1;
        }
        if (state > 0) return 0;
    }
    irq_diagnose("wait", timeout);
    return 1;
}

int irq_rearm(void) {
    _intr_write(0);
    __asm__ volatile("fence iorw, iorw" : : : "memory");
    uint32_t status = csr_read(CSR_STATUS);
    uint32_t value = irq_done;
    if (irq_opened == 0U) {
        LOG_ERROR("[HPU][IRQ][FAIL] phase=rearm reason=not-open status=0x%x\n", status);
        return 1;
    }
    /* 保持原先短路判断及 MMIO 读取顺序；每条失败日志只用已读到的值。 */
    if (value != 1U) {
        LOG_ERROR("[HPU][IRQ][FAIL] phase=rearm reason=not-done done=%u status=0x%x\n",
               value, status);
        return 1;
    }
    value = irq_error;
    if (value != 0U) {
        LOG_ERROR("[HPU][IRQ][FAIL] phase=rearm reason=handler-error error=%u status=0x%x\n",
               value, status);
        return 1;
    }
    value = csr_read(CSR_IRQ);
    if ((value & IRQ_LEVEL) != 0U) {
        LOG_ERROR("[HPU][IRQ][FAIL] phase=rearm reason=level-not-cleared irq=0x%x status=0x%x\n",
               value, status);
        return 1;
    }
    value = csr_read(CSR_FAULT);
    if ((value & FAULT_VALID) != 0U) {
        LOG_ERROR("[HPU][IRQ][FAIL] phase=rearm reason=fault-valid fault=0x%x status=0x%x\n",
               value, status);
        return 1;
    }
    if ((status & STATUS_VALID) == 0U) {
        LOG_ERROR("[HPU][IRQ][FAIL] phase=rearm reason=window-invalid status=0x%x\n", status);
        return 1;
    }
    if ((status & STATUS_BUSY) != 0U) {
        LOG_ERROR("[HPU][IRQ][FAIL] phase=rearm reason=busy status=0x%x\n", status);
        return 1;
    }
    if ((status & STATUS_FAULT) != 0U) {
        LOG_ERROR("[HPU][IRQ][FAIL] phase=rearm reason=status-fault status=0x%x\n", status);
        return 1;
    }
    irq_reset_round();
    __asm__ volatile("fence iorw, iorw" : : : "memory");
    _intr_write(1);
    return 0;
}

void irq_close(void) {
    _intr_write(0);
    irq_opened = 0U;
    __asm__ volatile("csrc sie, %0" : : "r"(SIE_SEIE) : "memory");
    hpu_plic_disable();
    mmio_write32(PLIC_PRIORITY_ADDR, 0U);
}
