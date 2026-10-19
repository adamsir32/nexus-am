#!/usr/bin/env python3
"""复用生产者C代码：预检查单独执行，07计时发令保留完全相同的HPU指令字。"""
import argparse
import json
from pathlib import Path
import re

from case_catalog import rows

RETURN_BLOCK = "#if !defined(__riscv)\n    return -4;\n#else\n    return 0;\n#endif"


def function_span(code, name):
    match = re.search(r"\bint " + re.escape(name) + r"\([^{};]*\) \{", code)
    if match is None:
        raise ValueError(f"missing producer entry: {name}")
    start, depth = match.end() - 1, 0
    # 跳过注释和字符串，避免汇编模板中的字符影响花括号配对。
    tokens = re.compile(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[{}]', re.S)
    for token in tokens.finditer(code, start):
        if token[0] == "{": depth += 1
        elif token[0] == "}":
            depth -= 1
            if depth == 0: return match.start(), token.end()
    raise ValueError(f"unbalanced producer entry: {name}")


def instruction_words(code):
    return [int(word, 16) for word in re.findall(r'\.word (0x[0-9a-fA-F]+)', code)]


def adapt(code, stem):
    program, entry = f"hpu_program_{stem}", f"hpu_run_{stem}"
    begin, end = function_span(code, program)
    original = code[begin:end]
    expected = instruction_words(original)
    if not expected or original.count(RETURN_BLOCK) != 1:
        raise ValueError("unexpected producer instruction/return template")
    clean = re.sub(r"^    trace_issue\([^;\n]*\);\n", "", original, flags=re.M)
    preflight = re.sub(r"^#if defined\(__riscv\)\n.*?^#endif\n", "", clean, flags=re.M | re.S)
    preflight = preflight.replace(RETURN_BLOCK, "    return 0;")
    preflight = preflight.replace("int " + program + "(", "static int " + program + "_preflight(", 1)
    if "__asm__" in preflight or instruction_words(preflight):
        raise ValueError("preflight must not issue any instruction")

    # 只接受固定生产者的校验模板；未知控制流拒绝导入，不能盲删if。
    fast, count = re.subn(r"^    if \(span_count != HPU_PROGRAM_[A-Z0-9_]+_DMA_COUNT \|\| \(span_count != 0 && spans == NULL\)\) return -1;\n", "", clean, flags=re.M)
    if count != 1: raise ValueError("producer span-count check changed")
    span_loop = ("    for (size_t i = 0; i < span_count; ++i) {\n"
                 "        if (spans[i].line_count == 0 ||\n"
                 "            spans[i].line_offset >= HPU_MEM_LINE_COUNT ||\n"
                 "            spans[i].line_count > HPU_MEM_LINE_COUNT - spans[i].line_offset)\n"
                 "            return -2;\n    }\n")
    if fast.count(span_loop) != 1: raise ValueError("producer span-range loop changed")
    fast = fast.replace(span_loop, "")
    fast = re.sub(r"^    if \(spans\[\d+\]\.line_count > HPU_SMALL_BANK_LINE_COUNT\) return -3;\n", "", fast, flags=re.M)
    fast = re.sub(r"^    if \(hpu_obj_len\[(\d+)\] == 0 \|\| spans\[\d+\]\.line_count != hpu_obj_len\[\1\]\) return -5;\n", "", fast, flags=re.M)
    fast = re.sub(r"^    uint32_t hpu_obj_len\[8\] = \{0\};\n|^    hpu_obj_len\[\d+\] = [^;\n]+;\n", "", fast, flags=re.M)
    fast = fast.replace("size_t span_count) {\n", "size_t span_count) {\n    (void)spans;\n    (void)span_count;\n", 1)
    if re.search(r"\b(?:if|for|while)\s*\(", fast) or "hpu_obj_len" in fast or "trace_issue" in fast:
        raise ValueError("unexpected control/diagnostic code remains in timed program")
    if instruction_words(fast) != expected:
        raise ValueError("timed instruction words differ from original producer")

    wrapper_begin, wrapper_end = function_span(code, entry)
    wrapper = code[wrapper_begin:wrapper_end]
    if wrapper.count(f"return {program}(") != 1:
        raise ValueError("producer resolved wrapper changed")
    validator = wrapper.replace("int " + entry + "(", "int hpu_validate_" + stem + "(", 1)
    validator = validator.replace(f"return {program}(", f"return {program}_preflight(", 1)
    result = code[:begin] + preflight + "\n\n" + fast + code[end:] + "\n\n" + validator + "\n"
    result = result.replace('#include <hpu/trace.h>\n', '')
    if instruction_words(result) != expected or "trace_issue(" in result:
        raise ValueError("performance adapter changed program or retained trace writes")
    return result, len(expected)


def prepare(directory, stem):
    original = (directory / f"{stem}.c").read_text()
    code, count = adapt(original, stem)
    expected = [int(word, 2) for word in (directory / f"{stem}.inst32").read_text().split()]
    if instruction_words(code) != expected:
        raise ValueError(f"{stem}: performance program differs from INST32")
    (directory / f"{stem}_perf.c").write_text(code)
    (directory / f"{stem}_perf.h").write_text(
        f'#include "{stem}.h"\n/* 必须在读起始cycle之前调用；只检查参数，不发HPU指令。 */\n'
        f'int hpu_validate_{stem}(void);\n')
    (directory / 'PERF_ADAPTATION.json').write_text(json.dumps(dict(
        schema_version=1, metric="issue_to_done_v2", program_stem=stem,
        instruction_count=count, instruction_words_unchanged=True,
        preflight_emits_hpu=False, timed_parameter_checks=False,
        timed_trace_writes=False), indent=2) + '\n')
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generated', type=Path, required=True)
    parser.add_argument('--only', help='可选的逗号分隔program_stem列表')
    args = parser.parse_args()
    selected = set(args.only.split(',')) if args.only else None
    done = set()
    for row in rows('perf-cases.tsv'):
        stem = row['program_stem']
        if stem in done or selected is not None and stem not in selected: continue
        count = prepare(args.generated / row['delivery'] / stem, stem)
        done.add(stem)
        print(f'{stem}: preflight separated, {count} native instruction words preserved', flush=True)
