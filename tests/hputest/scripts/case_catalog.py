"""统一列出功能用例及07独立规模用例所需的生产者包。"""
import argparse
import csv
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def rows(name):
    with (ROOT / name).open() as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def select_cases(scope="all"):
    """按完整清单选择构建范围；CI分片不修改任何用例编号。"""
    cases = rows("cases.tsv")
    if scope == "all":
        return cases
    if scope == "functional":
        return [row for row in cases if not row["case_id"].startswith("07_")]
    match = re.fullmatch(r"performance:(4096|8192|16384|32768|65536):(baseline|l16-(ckks|bfv|bgv)(?:-([ab]))?)", scope)
    if match is None:
        raise ValueError(f"invalid build scope: {scope}")
    degree, profile, scheme, partition = match.groups()
    if partition and (degree != "65536" or scheme != "bfv"):
        raise ValueError("only N65536 L16 BFV needs the a/b storage partitions")
    selected = [row for row in rows("perf-cases.tsv") if row["degree"] == degree and
                ((profile == "baseline" and row["level"] != "16") or
                 (row["level"] == "16" and
                  row["program_stem"].removeprefix("seal_").startswith(str(scheme) + "_")))]
    if len(selected) != (22 if profile == "baseline" else 6):
        raise ValueError(f"unexpected performance shard coverage: {scope}")
    if partition:
        selected = selected[0 if partition == "a" else 1::2]
    ids = {row["case_id"] for row in selected}
    result = [row for row in cases if row["case_id"] in ids]
    if len(result) != len(ids):
        raise ValueError(f"performance shard is not in canonical roster: {scope}")
    return result


def performance_specs(scope="all"):
    selected = {row["case_id"] for row in select_cases(scope)}
    return [row for row in rows("perf-cases.tsv") if row["case_id"] in selected]


def large_specs(scope="all"):
    """功能大规模交付及所选性能原语，按program_stem去重。"""
    selected = {row["case_id"] for row in select_cases(scope)}
    specs = {row["program_stem"]: row for row in rows("large-cases.tsv") if row["case_id"] in selected}
    specs.update({row["program_stem"]: dict(case_id=row["case_id"], program_stem=row["program_stem"], source=row["source"])
                  for row in performance_specs(scope) if row["delivery"] == "large-data"})
    return list(specs.values())


def application_specs(scope="all"):
    specs = {row["program_stem"]: row for row in rows("scheme-cases.tsv")}
    for row in rows("perf-cases.tsv"):
        stem = row["program_stem"]
        if row["delivery"] != "application-data" or stem in specs:
            continue
        match = re.fullmatch(r"(?:seal_)?(ckks|bfv|bgv)_(keyswitch|hadd|hmul|reline|modswitch|rotate)(?:_l(16))?_n(\d+)", stem)
        if match is None or match[4] != row["degree"]:
            raise ValueError(f"invalid performance producer: {stem}")
        specs[stem] = dict(case_id=row["case_id"], program_stem=stem,
                           scheme=match[1], degree=match[4], role=match[2], source=row["source"],
                           q_rns_count=int(match[3]) if match[3] else 0)
    if scope == "all":
        return specs
    selected = {row["case_id"] for row in select_cases(scope)}
    stems = {row["program_stem"] for row in rows("scheme-cases.tsv") if row["case_id"] in selected}
    stems.update(row["program_stem"] for row in performance_specs(scope) if row["delivery"] == "application-data")
    return {stem: row for stem, row in specs.items() if stem in stems}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", default=os.environ.get("HPU_BUILD_SCOPE", "all"))
    parser.add_argument("--table", choices=("application", "performance", "cases", "large"), default="application")
    args = parser.parse_args()
    fields = {
        "application": ("case_id", "program_stem", "scheme", "degree", "role", "source"),
        "performance": tuple(rows("perf-cases.tsv")[0]),
        "cases": ("group", "qualifier", "case_id", "source"),
        "large": ("case_id", "program_stem", "source"),
    }
    data = {"application": lambda: application_specs(args.scope).values(),
            "performance": lambda: performance_specs(args.scope),
            "cases": lambda: select_cases(args.scope),
            "large": lambda: large_specs(args.scope)}
    selected_rows = data[args.table]()
    writer = csv.DictWriter(sys.stdout, fieldnames=fields[args.table], delimiter="\t", lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(selected_rows)
