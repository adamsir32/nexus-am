#!/usr/bin/env python3
"""检查07实际ELF的校验/计时顺序及发令路径，避免只改源码注释。"""
import argparse
from pathlib import Path
import re


def functions(text):
    result, active = {}, None
    for line in text.splitlines():
        if line.startswith('Disassembly of section '):
            active = None
            continue
        symbol = re.match(r'^[0-9a-f]+ <([^>]+)>:$', line)
        if symbol:
            active = symbol[1]; result[active] = []
        elif active:
            result[active].append(line)
    return {name: '\n'.join(lines) for name, lines in result.items()}


def verify(disassembly, stem):
    symbols = functions(disassembly.read_text())
    main = symbols.get('main', '')
    calls = re.findall(r'\b(?:jal|jalr)\s+[^\n<]*<([^>]+)>', main)
    endpoints = [i for i, call in enumerate(calls) if call == 'perf_cycle_read']
    if len(endpoints) != 2 or f'hpu_validate_{stem}' not in calls:
        raise ValueError('missing preflight or two cycle endpoints')
    if not (calls.index(f'hpu_validate_{stem}') < endpoints[0] <
            calls.index(f'hpu_run_{stem}') < calls.index('application_wait') < endpoints[1]):
        raise ValueError('preflight/issue/wait/cycle ordering differs from performance contract')
    timed = {name: body for name, body in symbols.items()
             if (name.startswith(f'hpu_program_{stem}') or name.startswith(f'hpu_run_{stem}'))
             and '_preflight' not in name}
    if not timed: raise ValueError('missing timed instruction entry')
    for name, body in timed.items():
        if re.search(r'\s(?:beq|bne|blt|bltu|bge|bgeu|beqz|bnez|bgtz|blez|bltz|bgez|bgtu|bleu)\s', body):
            raise ValueError(f'conditional validation branch remains in timed entry: {name}')
        if 'application_trace' in body or 'trace_issue' in body or '_preflight' in body or 'hpu_validate_' in body:
            raise ValueError(f'validation/trace leaked into timed entry: {name}')
    for name, body in symbols.items():
        if name.startswith(f'hpu_validate_{stem}') or name.startswith(f'hpu_program_{stem}_preflight'):
            words = re.findall(r'^\s*[0-9a-f]+:\s+([0-9a-f]{8})\s', body, re.M)
            if any(int(word, 16) & 0x7f in (0x0b, 0x2b, 0x5b) for word in words):
                raise ValueError(f'preflight unexpectedly issues HPU instructions: {name}')
    print(f'[hputest] {stem}: ELF preflight before cycle, timed entry has no validation/trace')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--disassembly', type=Path, required=True)
    parser.add_argument('--operator', required=True)
    args = parser.parse_args()
    verify(args.disassembly, args.operator)
