#!/usr/bin/env python3
"""汇总07的真实UART端点；未通过自检的轮次不进入性能结果。"""
import argparse
import csv
from collections import defaultdict
from pathlib import Path
import re
import statistics

PATTERN = re.compile(r"\[HPU\]\[PERF\] case=(\w+) N=(8192|16384|32768|65536) metric=issue_to_done_v2 start=(\d+) end=(\d+) cycles=(\d+) verified=1$")


def parse(logs, allowed):
    samples=[]
    for path in logs:
        for line_number,line in enumerate(path.read_text(errors='replace').splitlines(),1):
            if '[HPU][PERF] case=' not in line: continue
            match=PATTERN.search(line.strip())
            if not match: raise ValueError(f'{path}:{line_number}: invalid/incomplete performance record')
            name,degree,start,end,cycles=match.groups();start,end,cycles=map(int,(start,end,cycles))
            if name not in allowed or not name.endswith('_n'+degree) or \
                    isinstance(allowed, dict) and str(allowed[name]) != degree or \
                    any(value<0 or value>=1<<64 for value in (start,end,cycles)) or not cycles or ((end-start)&((1<<64)-1))!=cycles:
                raise ValueError(f'{path}:{line_number}: unknown case or inconsistent cycle endpoints')
            samples.append(dict(case_id=name,degree=int(degree),metric='issue_to_done_v2',start=start,end=end,cycles=cycles,log=str(path),line=line_number))
    if not samples: raise ValueError('no verified 07 performance records')
    return samples


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('logs',nargs='+',type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--revision',required=True,help='本批实际AM/RTL版本，不能混合不同版本后平均')
    parser.add_argument('--cpu-hz',type=int,help='目标SCPU频率，不是188服务器频率')
    args=parser.parse_args()
    if args.cpu_hz is not None and args.cpu_hz<=0: parser.error('--cpu-hz must be positive')
    root=Path(__file__).resolve().parents[1]
    catalog=root/'perf-cases.tsv'
    if not catalog.exists(): catalog=root/'provenance/testplan/perf-cases.tsv'
    with catalog.open() as stream:
        allowed={r['case_id']: r['degree'] for r in csv.DictReader(stream,delimiter='\t')}
    samples=parse(args.logs,allowed);groups=defaultdict(list)
    for row in samples: groups[row['case_id']].append(row['cycles'])
    args.output.mkdir(parents=True,exist_ok=True)
    with (args.output/'samples.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(samples[0])+['revision'])
        writer.writeheader();writer.writerows(dict(row,revision=args.revision) for row in samples)
    with (args.output/'summary.csv').open('w',newline='') as stream:
        writer=csv.writer(stream)
        writer.writerow(['case_id','degree','metric','rounds','average_cycles','minimum_cycles','maximum_cycles','spread_cycles','SCPU_Hz','average_seconds','revision'])
        for name,values in sorted(groups.items()):
            average=statistics.mean(values)
            writer.writerow([name,allowed[name],'issue_to_done_v2',len(values),average,min(values),max(values),max(values)-min(values),
                             args.cpu_hz,average/args.cpu_hz if args.cpu_hz else None,args.revision])
    print(f'{len(samples)} verified samples, {len(groups)} cases; no CPU speedup is inferred')


if __name__=='__main__': main()
