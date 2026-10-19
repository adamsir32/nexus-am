#!/usr/bin/env python3
"""汇总新API的真实UART性能记录；noopt/optimized比值只写在optimized汇总行。"""

import argparse
from collections import defaultdict
import csv
from pathlib import Path
import re
import statistics


METRIC = "issue_to_done_v2"
MARKER = "[HPU][NEWAPI-PERF]"
PATTERN = re.compile(
    r"\[HPU\]\[NEWAPI-PERF\] case=([A-Za-z0-9_]+) variant=(optimized|noopt) "
    r"N=(4096|8192) level=(\d+) metric=issue_to_done_v2 "
    r"start=(\d+) end=(\d+) cycles=(\d+) verified=1$")
SAMPLE_FIELDS = ["case_id", "variant", "degree", "level", "metric", "start", "end",
                 "cycles", "log", "line", "revision"]
SUMMARY_FIELDS = ["case_id", "variant", "degree", "level", "metric", "rounds",
                  "average_cycles", "minimum_cycles", "maximum_cycles", "spread_cycles",
                  "noopt_over_optimized", "revision"]


def find_catalog(script=__file__):
    directory = Path(script).resolve().parent
    for path in (directory / "performance-cases.tsv", directory.parent / "performance-cases.tsv",
                 directory.parent / "provenance/testplan/performance-cases.tsv"):
        if path.is_file():
            return path
    raise ValueError("performance-cases.tsv not found beside the script or in the workload/package root")


def load_catalog(path):
    with Path(path).open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if not {"case_id", "degree", "level", "metric"}.issubset(reader.fieldnames or []):
            raise ValueError("performance catalog lacks case_id/degree/level/metric")
        result = {}
        for row in reader:
            name = row["case_id"]
            if not name or name in result or row["metric"] != METRIC:
                raise ValueError(f"duplicate or invalid performance catalog entry: {name}")
            degree, level = int(row["degree"]), int(row["level"])
            if degree not in (4096, 8192) or level <= 0 or not name.endswith(f"_l{level}_n{degree}"):
                raise ValueError(f"inconsistent performance catalog parameters: {name}")
            result[name] = dict(degree=degree, level=level)
    if not result:
        raise ValueError("empty performance catalog")
    return result


def parse(logs, catalog, revision):
    if not revision.strip():
        raise ValueError("revision must describe this batch's actual AM/RTL versions")
    samples = []
    for path in map(Path, logs):
        with path.open(encoding="utf-8", errors="replace") as stream:
            for line_number, line in enumerate(stream, 1):
                if MARKER + " " not in line:
                    continue
                match = PATTERN.search(line.strip())
                if match is None:
                    raise ValueError(f"{path}:{line_number}: invalid, unverified or incomplete NEWAPI-PERF record")
                name, variant, degree, level, start, end, cycles = match.groups()
                degree, level, start, end, cycles = map(int, (degree, level, start, end, cycles))
                if name not in catalog or catalog[name] != dict(degree=degree, level=level):
                    raise ValueError(f"{path}:{line_number}: case/N/level differs from performance-cases.tsv")
                if any(value >= 1 << 64 for value in (start, end, cycles)) or cycles == 0 or \
                        ((end - start) & ((1 << 64) - 1)) != cycles:
                    raise ValueError(f"{path}:{line_number}: inconsistent unsigned 64-bit cycle endpoints")
                samples.append(dict(case_id=name, variant=variant, degree=degree, level=level,
                                    metric=METRIC, start=start, end=end, cycles=cycles,
                                    log=str(path), line=line_number, revision=revision))
    if not samples:
        raise ValueError("no verified NEWAPI-PERF samples")
    return samples


def summarize(samples):
    groups = defaultdict(list)
    for row in samples:
        groups[(row["case_id"], row["variant"])].append(row)
    result = []
    for name in sorted({key[0] for key in groups}):
        for variant in ("optimized", "noopt"):
            group = groups.get((name, variant))
            if not group:
                continue
            metadata = {(r["degree"], r["level"], r["metric"], r["revision"]) for r in group}
            if len(metadata) != 1:
                raise ValueError(f"mixed parameters or revisions in one sample group: {name}/{variant}")
            values = [row["cycles"] for row in group]
            ratio = None
            other = groups.get((name, "noopt"))
            if variant == "optimized" and other:
                other_metadata = {(r["degree"], r["level"], r["metric"], r["revision"]) for r in other}
                if other_metadata != metadata:
                    raise ValueError(f"optimized/noopt comparison has different parameters or revisions: {name}")
                ratio = statistics.mean(row["cycles"] for row in other) / statistics.mean(values)
            result.append(dict(case_id=name, variant=variant, degree=group[0]["degree"],
                               level=group[0]["level"], metric=METRIC, rounds=len(values),
                               average_cycles=statistics.mean(values), minimum_cycles=min(values),
                               maximum_cycles=max(values), spread_cycles=max(values) - min(values),
                               noopt_over_optimized=ratio, revision=group[0]["revision"]))
    return result


def write_csv(path, rows, fields):
    with path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path, help="保存samples.csv和summary.csv的新结果目录")
    parser.add_argument("--revision", required=True, help="本批实际AM/RTL版本；不同版本分别运行，不混合平均")
    args = parser.parse_args()
    try:
        samples = parse(args.logs, load_catalog(find_catalog()), args.revision)
        summary = summarize(samples)
        args.output.mkdir(parents=True, exist_ok=True)
        targets = [args.output / "samples.csv", args.output / "summary.csv"]
        if any(path.exists() for path in targets):
            raise ValueError("output already contains performance results; choose a new output directory")
        write_csv(targets[0], samples, SAMPLE_FIELDS)
        write_csv(targets[1], summary, SUMMARY_FIELDS)
    except (ValueError, OSError, csv.Error) as error:
        parser.exit(2, f"new API performance parse failed: {error}\n")
    pairs = sum(row["noopt_over_optimized"] is not None for row in summary)
    print(f"{len(samples)} verified samples, {len(summary)} case/variant groups, {pairs} paired comparisons")


if __name__ == "__main__":
    main()
