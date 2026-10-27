"""接收官方连续计时窗口；仅核对原生源码，不重排DMA或改写发令入口。"""
import csv
import json
from pathlib import Path
import re

METRIC = "execution_window_irq_v1"
COMPLETION = "plic_irq"
PROFILE = "continuous"
WINDOW_FIELDS = ("begin_instruction", "end_instruction", "arithmetic_instruction_count",
                 "dload_count", "dstore_count")
REPORT_COUNTS = ("prefix_dload_count", "window_dload_count", "window_dstore_count",
                 "suffix_dstore_count", "unprofiled_dma_bytes", "unprofiled_dma_count")
ARITHMETIC = {"padd", "psub", "pmul", "pmac", "pntt", "pintt"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def expected_header(stem, dma_count):
    """encode/executable.cpp的公开ABI文本；用于拒绝未审阅的头文件变更。"""
    guard = "HPU_PROGRAM_" + stem.upper() + "_H"
    return f'''#ifndef {guard}
#define {guard}

#include <stddef.h>
#include <stdint.h>

#ifndef HPU_DMA_SPAN_T_DEFINED
#define HPU_DMA_SPAN_T_DEFINED
typedef struct hpu_dma_span {{
    uint32_t line_offset;
    uint32_t line_count;
}} hpu_dma_span_t;
#endif

#ifdef __cplusplus
extern "C" {{
#endif

enum {{ HPU_PROGRAM_{stem.upper()}_DMA_COUNT = {dma_count} }};
int hpu_program_{stem}(const hpu_dma_span_t *spans, size_t span_count);

#ifndef HPU_EXECUTION_PROFILE_TYPES_DEFINED
#define HPU_EXECUTION_PROFILE_TYPES_DEFINED
typedef struct hpu_execution_profile_hooks {{
    void *user;
    uint64_t (*read_cycles)(void *user);
    /* Wait for this zero-based PSYNC, acknowledge its completion and check
       faults without resetting resident objects. Nonzero aborts execution. */
    int (*wait_complete)(void *user, size_t sync_index);
}} hpu_execution_profile_hooks_t;
typedef struct hpu_execution_profile_sample {{
    uint64_t start_cycles;
    uint64_t end_cycles;
    int valid;
}} hpu_execution_profile_sample_t;
#endif

/* Ordinary entries return -5. The single timer includes necessary body DMA.
   -1: missing hooks/sample; -4: non-RISC-V host; otherwise zero or the
   completion hook error. valid is set only after the complete program
   succeeds, including output stores outside the timed window. */
int hpu_run_{stem}(void);
int hpu_run_{stem}_profiled(const hpu_execution_profile_hooks_t *hooks,
    hpu_execution_profile_sample_t *sample);

#ifdef __cplusplus
}}
#endif

#endif
'''


def expected_source(stem, words, spans, window):
    """逐字验证官方分块模板，跨回调必须重新设置x10/x11。此结果不写入交付。"""
    result = f'''/* Generated single-window profile; residual body DMA remains timed. */
#include "{stem}.h"

int hpu_program_{stem}(const hpu_dma_span_t *spans, size_t span_count) {{
    (void)spans; (void)span_count; return -5;
}}

int hpu_run_{stem}(void) {{ return -5; }}

int hpu_run_{stem}_profiled(const hpu_execution_profile_hooks_t *hooks,
    hpu_execution_profile_sample_t *sample) {{
    if (sample != NULL) {{
        sample->start_cycles = 0; sample->end_cycles = 0; sample->valid = 0;
    }}
    if (hooks == NULL || hooks->read_cycles == NULL ||
        hooks->wait_complete == NULL || sample == NULL) return -1;
#if defined(__riscv)
'''
    begin, dma_index, sync_index = 0, 0, 0
    for end, word in enumerate(words):
        if word != 0x7000005b:
            continue
        result += f"    /* Instructions [{begin}, {end + 1}), including completion PSYNC. */\n"
        result += "    __asm__ volatile(\n"
        previous_count = 0
        for value in words[begin:end + 1]:
            if value & 127 == 0x2b:
                first, count = spans[dma_index]
                dma_index += 1
                result += f'        "li x10, {first}\\n\\t"\n'
                if count != previous_count:
                    result += f'        "li x11, {count}\\n\\t"\n'
                    previous_count = count
            result += f'        ".word 0x{value:08X}\\n\\t"\n'
        result += ('        : : : "x10", "x11", "memory");\n'
                   '    {\n'
                   f'        const int status = hooks->wait_complete(hooks->user, {sync_index});\n'
                   '        if (status != 0) return status;\n'
                   '    }\n')
        if end + 1 == window["begin_instruction"]:
            result += '    sample->start_cycles = hooks->read_cycles(hooks->user);\n'
        if end == window["end_instruction"]:
            result += '    sample->end_cycles = hooks->read_cycles(hooks->user);\n'
        begin, sync_index = end + 1, sync_index + 1
    require(begin == len(words) and dma_index == len(spans), "profile source DMA/PSYNC coverage differs")
    return result + '    sample->valid = 1;\n    return 0;\n#else\n    return -4;\n#endif\n}\n'


def validate_source(code, header, stem, words, spans, window):
    require(re.fullmatch(r"[a-z][a-z0-9_]+", stem) is not None, "unsafe profile program stem")
    require(code == expected_source(stem, words, spans, window),
            "profile source differs from official callbacks/words/DMA/x11/timestamp template")
    require(header == expected_header(stem, len(spans)), "profile header/hook/sample ABI differs")


def validate_window(words, assembly, dma, rows, report):
    require(len(rows) == 1 and tuple(rows[0]) == WINDOW_FIELDS,
            "execution profile requires exactly one complete window manifest row")
    require(all(type(value) is str and re.fullmatch(r"[0-9]+", value) for value in rows[0].values()),
            "profile window fields must be unsigned decimal integers")
    window = {key: int(value) for key, value in rows[0].items()}
    begin, end = window["begin_instruction"], window["end_instruction"]
    require(words and words[-1] == 0x7000005b and all(value & 127 in (0x2b, 0x5b) for value in words),
            "profile instruction opcode/final PSYNC differs")
    require(0 < begin < end < len(words) and words[begin - 1] == words[end] == 0x7000005b,
            "profile window is out of range or missing its PSYNC boundaries")
    mnemonics = [line.split()[0].lower() for line in assembly.splitlines() if line.strip()]
    require(len(mnemonics) == len(words) and all(name in ARITHMETIC | {"dload", "dstore", "pmodld", "pfree", "psync"}
            for name in mnemonics), "profile assembly instruction count/mnemonic differs")
    syncs = [index for index, value in enumerate(words) if value == 0x7000005b]
    require(syncs == [index for index, name in enumerate(mnemonics) if name == "psync"],
            "profile ASM/INST32 PSYNC order differs")
    arithmetic = [index for index, name in enumerate(mnemonics) if name in ARITHMETIC]
    require(arithmetic and arithmetic[0] == begin and arithmetic[-1] + 1 == end and
            window["arithmetic_instruction_count"] == len(arithmetic),
            "continuous profile must cover all arithmetic, not a selected sub-operation")
    require([int(row["instruction_index"]) for row in dma] ==
            [index for index, value in enumerate(words) if value & 127 == 0x2b], "profile DMA ordering differs")
    counts = dict(prefix_dload_count=0, prefix_dstore_count=0, window_dload_count=0,
                  window_dstore_count=0, suffix_dload_count=0, suffix_dstore_count=0)
    for row in dma:
        index = int(row["instruction_index"])
        direction = row["direction"]
        require(direction in ("dload", "dstore") and mnemonics[index] == direction,
                "profile DMA/assembly direction differs")
        if index < begin:
            # BFV noopt的原有workspace复制可位于首条算术前；如实统计，不改官方边界。
            key = "prefix_" + direction + "_count"
        elif index >= end:
            key = "suffix_" + direction + "_count"
        else:
            key = "window_" + direction + "_count"
        counts[key] += 1
    require(window["dload_count"] == counts["window_dload_count"] and
            window["dstore_count"] == counts["window_dstore_count"], "profile window DMA counts differ")
    require(type(report) is dict and report.get("enabled") is True and
            type(report.get("window_count")) is int and report["window_count"] == 1 and
            report.get("timing_measured") is False and report.get("includes_residual_dma") is True,
            "profile oracle must declare one continuous, unmeasured window including residual DMA")
    require(all(type(report.get(key)) is int and report[key] >= 0 for key in REPORT_COUNTS) and
            all(report.get(key) == counts[key] for key in REPORT_COUNTS if key in counts) and
            all(key not in report or type(report[key]) is int and report[key] == value
                for key, value in counts.items()), "profile oracle DMA statistics differ")
    require(len(dma) <= report["unprofiled_dma_count"] and
            sum(int(row["line_count"]) * 256 for row in dma) <= report["unprofiled_dma_bytes"],
            "entry preloading added DMA/spill/reload relative to the unprofiled schedule")
    return {**report, **counts, **window, "sync_count": len(syncs), "sync_instruction_indices": syncs,
            "start_sync_index": syncs.index(begin - 1), "end_sync_index": syncs.index(end)}


def constants(profile):
    return {"PROFILE_SYNC_COUNT": profile["sync_count"],
            "PROFILE_BEGIN_INSTRUCTION": profile["begin_instruction"],
            "PROFILE_END_INSTRUCTION": profile["end_instruction"],
            "PROFILE_ARITHMETIC_COUNT": profile["arithmetic_instruction_count"],
            "PROFILE_WINDOW_DLOAD_COUNT": profile["dload_count"],
            "PROFILE_WINDOW_DSTORE_COUNT": profile["dstore_count"],
            "PROFILE_PREFIX_DLOAD_COUNT": profile["prefix_dload_count"],
            "PROFILE_PREFIX_DSTORE_COUNT": profile["prefix_dstore_count"],
            "PROFILE_SUFFIX_DLOAD_COUNT": profile["suffix_dload_count"],
            "PROFILE_SUFFIX_DSTORE_COUNT": profile["suffix_dstore_count"]}


def prepare(directory, stem):
    """保持上游C/H原字节；只核对已接收的窗口、DMA和公开模板并写验证记录。"""
    directory = Path(directory)
    meta = json.loads((directory / 'delivery.json').read_text())
    profile = meta.get('execution_profile')
    require(meta.get('program_stem') == stem and type(profile) is dict,
            "missing received execution profile metadata")
    raw = (directory / (stem + '.inst32')).read_text().splitlines()
    require(raw and all(re.fullmatch(r'[01]{32}', value) for value in raw), "profile INST32 format differs")
    words = [int(value, 2) for value in raw]
    with (directory / 'execution_window.csv').open(newline='') as stream:
        windows = list(csv.DictReader(stream))
    with (directory / 'profile_dma.csv').open(newline='') as stream:
        dma = list(csv.DictReader(stream))
    actual = validate_window(words, (directory / 'profile.asm').read_text(), dma, windows, profile)
    require(actual == profile, "received profile metadata changed after validation")
    validate_source((directory / (stem + '.c')).read_text(), (directory / (stem + '.h')).read_text(),
                    stem, words, [(int(row['line_offset']), int(row['line_count'])) for row in dma], profile)
    receipt = dict(schema_version=1, metric=METRIC, completion=COMPLETION, profile=PROFILE,
                   source_adaptation='none', native_profiled_entry_unchanged=True,
                   instruction_count=len(words), execution_profile=profile)
    target = directory / 'EXECUTION_PROFILE.json'
    content = (json.dumps(receipt, indent=2) + '\n').encode()
    require(not target.is_symlink(), "profile receipt must not be a symlink")
    if target.exists():
        require(target.is_file() and target.read_bytes() == content, "profile receipt differs")
    else:
        with target.open('xb') as stream:
            stream.write(content)
    return len(words)
