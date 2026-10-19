"""统一列出功能用例及07独立规模用例所需的生产者包。"""
import csv
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def rows(name):
    with (ROOT / name).open() as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def application_specs():
    specs = {row["program_stem"]: row for row in rows("scheme-cases.tsv")}
    for row in rows("perf-cases.tsv"):
        stem = row["program_stem"]
        if row["delivery"] != "application-data" or stem in specs:
            continue
        match = re.fullmatch(r"(?:seal_)?(ckks|bfv|bgv)_(keyswitch|hadd|hmul|reline|modswitch|rotate)_n(\d+)", stem)
        if match is None or match[3] != row["degree"]:
            raise ValueError(f"invalid performance producer: {stem}")
        specs[stem] = dict(case_id=row["case_id"], program_stem=stem,
                           scheme=match[1], degree=match[3], role=match[2], source=row["source"])
    return specs


if __name__ == "__main__":
    writer = csv.DictWriter(sys.stdout, fieldnames=("case_id", "program_stem", "scheme", "degree", "role", "source"), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(application_specs().values())
