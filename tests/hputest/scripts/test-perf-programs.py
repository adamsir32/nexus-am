#!/usr/bin/env python3
"""验证07预检查保留错误判据，且计时发令不再带校验或trace。"""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('perf_adapter', HERE / 'prepare-perf-programs.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)

# 固定生产者模板的最小测试夹具；不会在主机执行HPU机器码。
PROGRAM = '''#include "probe.h"
#define HPU_MEM_LINE_COUNT UINT64_C(128)
enum { HPU_SMALL_BANK_LINE_COUNT = 32 };
int hpu_program_probe(const hpu_dma_span_t *spans, size_t span_count) {
    if (span_count != HPU_PROGRAM_PROBE_DMA_COUNT || (span_count != 0 && spans == NULL)) return -1;
    uint32_t hpu_obj_len[8] = {0};
    for (size_t i = 0; i < span_count; ++i) {
        if (spans[i].line_count == 0 ||
            spans[i].line_offset >= HPU_MEM_LINE_COUNT ||
            spans[i].line_count > HPU_MEM_LINE_COUNT - spans[i].line_offset)
            return -2;
    }
    trace_issue(0U, 0U, 0x08B540ABU);
    if (spans[0].line_count > HPU_SMALL_BANK_LINE_COUNT) return -3;
    hpu_obj_len[4] = spans[0].line_count;
#if defined(__riscv)
    __asm__ volatile(".word 0x08B540AB" : : : "memory");
#endif
    trace_issue(1U, 1U, 0x08B550ABU);
    if (hpu_obj_len[4] == 0 || spans[1].line_count != hpu_obj_len[4]) return -5;
#if defined(__riscv)
    __asm__ volatile(".word 0x08B550AB" : : : "memory");
#endif
    hpu_obj_len[4] = 0;
#if defined(__riscv)
    __asm__ volatile(".word 0x7000005B" : : : "memory");
#endif
#if !defined(__riscv)
    return -4;
#else
    return 0;
#endif
}
static const hpu_dma_span_t resolved[] = {{0, 16}, {64, 16}};
int hpu_run_probe(void) {
    return hpu_program_probe(resolved, 2);
}
'''


class PerformancePrograms(unittest.TestCase):
    def test_preflight_runs_all_validation_without_hardware(self):
        code, count = adapter.adapt(PROGRAM, 'probe')
        self.assertEqual(count, 3)
        self.assertEqual(adapter.instruction_words(code), adapter.instruction_words(PROGRAM))
        begin, end = adapter.function_span(code, 'hpu_program_probe')
        self.assertNotIn('trace_issue', code)
        self.assertNotIn('if (', code[begin:end])
        self.assertNotIn('for (', code[begin:end])
        with tempfile.TemporaryDirectory(prefix='hpu-perf-preflight-') as tmp:
            root = Path(tmp)
            (root / 'probe.h').write_text('#include <stdint.h>\n#include <stddef.h>\ntypedef struct { uint32_t line_offset, line_count; } hpu_dma_span_t;\nenum { HPU_PROGRAM_PROBE_DMA_COUNT=2 };\n')
            harness = r'''
#include <assert.h>
int main(void) {
    hpu_dma_span_t spans[2] = {{0,16}, {64,16}};
    assert(hpu_validate_probe() == 0);
    assert(hpu_program_probe_preflight(spans, 2) == 0);
    assert(hpu_program_probe_preflight(NULL, 2) == -1);
    assert(hpu_program_probe_preflight(spans, 1) == -1);
    spans[0].line_count = 0;
    assert(hpu_program_probe_preflight(spans, 2) == -2);
    spans[0].line_count = 16; spans[0].line_offset = 128;
    assert(hpu_program_probe_preflight(spans, 2) == -2);
    spans[0].line_offset = 120;
    assert(hpu_program_probe_preflight(spans, 2) == -2);
    spans[0].line_offset = 0; spans[0].line_count = 33;
    assert(hpu_program_probe_preflight(spans, 2) == -3);
    spans[0].line_count = 16; spans[1].line_count = 15;
    assert(hpu_program_probe_preflight(spans, 2) == -5);
    return 0;
}
'''
            (root / 'probe.c').write_text(code + harness)
            subprocess.run([os.environ.get('CC', 'cc'), '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                            str(root / 'probe.c'), '-o', str(root / 'check')], check=True)
            subprocess.run([str(root / 'check')], check=True)

    def test_unknown_runtime_control_is_rejected(self):
        modified = PROGRAM.replace('    hpu_obj_len[4] = 0;',
                                   '    if (spans[0].line_offset == 7) return -9;\n    hpu_obj_len[4] = 0;')
        with self.assertRaisesRegex(ValueError, 'unexpected control'):
            adapter.adapt(modified, 'probe')

    def test_changed_producer_template_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'span-range loop'):
            adapter.adapt(PROGRAM.replace('spans[i].line_count == 0', 'spans[i].line_count <= 0'), 'probe')


if __name__ == '__main__': unittest.main()
