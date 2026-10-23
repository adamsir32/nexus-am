"""主线只发布1019现有HPU交付；不运行生成器或依赖YAML第三方模块。"""
import csv
import itertools
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT.parents[1] / ".github/workflows"
HPU_WORKFLOWS = ("build-hpu-operator-perf.yml", "build-hpu-frontend.yml")


def block(text, key, indent):
    """从本项目结构固定的工作流中读取一段映射配置。"""
    lines = text.splitlines()
    marker = " " * indent + key + ":"
    start = lines.index(marker) + 1
    end = next((index for index in range(start, len(lines))
                if lines[index].strip() and
                len(lines[index]) - len(lines[index].lstrip()) <= indent), len(lines))
    return "\n".join(lines[start:end])


def inline_list(text, key):
    match = re.search(r"^\s*" + re.escape(key) + r": \[([^\]]*)\]\s*$", text, re.M)
    if match is None:
        raise AssertionError("missing inline list: " + key)
    return [item.strip() for item in match.group(1).split(",")]


class MainlineWorkflowTests(unittest.TestCase):
    def test_cpu_workflow_keeps_cpu_build_and_no_legacy_hpu_jobs(self):
        text = (WORKFLOWS / "build.yml").read_text()
        jobs = block(text, "jobs", 0)
        self.assertEqual(re.findall(r"^  ([\w-]+):$", jobs, re.M), ["build"])
        for target in ("tests/cputest", "tests/softprefetchtest", "tests/dualcoretest",
                       "tests/cacheoptest/dcache", "tests/cacheoptest/icache",
                       "tests/cacheoptest/llc", "tests/aliastest", "tests/countertest",
                       "apps/microbench", "apps/coremark", "apps/loader", "tests/amtest"):
            self.assertIn(target, jobs)
        self.assertIn("name: nexus-am-workloads", jobs)

    def test_no_active_workflow_calls_or_uploads_legacy_hpu_delivery(self):
        for path in WORKFLOWS.glob("*.yml"):
            with self.subTest(workflow=path.name):
                text = path.read_text()
                self.assertNotIn("tests/hputest", text)
                self.assertNotIn("nexus-am-hpu-tests", text)
                self.assertNotIn("nexus-am-hpu-perf-n", text)

    def test_hpu_triggers_include_mainline_and_1019_but_not_backups(self):
        for name in HPU_WORKFLOWS:
            with self.subTest(workflow=name):
                events = block((WORKFLOWS / name).read_text(), "on", 0)
                self.assertEqual(inline_list(block(events, "push", 2), "branches"),
                                 ["master", "1019-operator-resource-perf"])
                self.assertEqual(inline_list(block(events, "pull_request", 2), "branches"),
                                 ["master"])
                self.assertIn("  workflow_dispatch:", events)

    def test_hpu_path_filters_cover_only_current_delivery_and_dependencies(self):
        for name in HPU_WORKFLOWS:
            events = block((WORKFLOWS / name).read_text(), "on", 0)
            for event in ("push", "pull_request"):
                with self.subTest(workflow=name, event=event):
                    paths = block(block(events, event, 2), "paths", 4)
                    self.assertEqual(re.findall(r"^      - '([^']+)'$", paths, re.M),
                                     ["tests/hpu_frontend_workload/**",
                                      ".github/workflows/" + name, ".gitmodules"])

    def test_six_operator_shards_cover_exactly_the_current_36_cases(self):
        text = (WORKFLOWS / HPU_WORKFLOWS[0]).read_text()
        matrix = block(text, "matrix", 6)
        self.assertEqual(inline_list(matrix, "degree"), ["4096", "8192"])
        self.assertEqual(inline_list(matrix, "profile"), ["baseline"])
        self.assertEqual(inline_list(matrix, "scheme"), ["ckks", "bfv", "bgv"])
        self.assertNotIn("include:", matrix)
        self.assertNotIn("exclude:", matrix)
        with (ROOT / "performance-cases.tsv").open() as stream:
            cases = list(csv.DictReader(stream, delimiter="\t"))
        scopes = list(itertools.product(inline_list(matrix, "degree"),
                                        inline_list(matrix, "scheme")))
        self.assertEqual(len(scopes), 6)
        self.assertEqual(len(cases), 36)
        self.assertEqual(len({row["case_id"] for row in cases}), 36)
        for degree, scheme in scopes:
            selected = [row for row in cases if (row["degree"], row["scheme"]) == (degree, scheme)]
            self.assertEqual(len(selected), 6)
        self.assertTrue(all(int(row["degree"]) <= 8192 and int(row["level"]) <= 4 for row in cases))
        self.assertIn('--scheme "${{ matrix.scheme }}" --mode both --jobs 2', text)
        self.assertIn("name: nexus-am-1019-operator-perf-n${{ matrix.degree }}-${{ matrix.profile }}-${{ matrix.scheme }}", text)

    def test_frontend_keeps_the_existing_six_api_cases_and_package(self):
        text = (WORKFLOWS / HPU_WORKFLOWS[1]).read_text()
        jobs = block(text, "jobs", 0)
        self.assertEqual(re.findall(r"^  ([\w-]+):$", jobs, re.M), ["build-frontend"])
        self.assertIn("make -C tests/hpu_frontend_workload all JOBS=4", jobs)
        self.assertIn("name: nexus-am-hpu-frontend-workload", jobs)
        with (ROOT / "cases.tsv").open() as stream:
            cases = list(csv.DictReader(stream, delimiter="\t"))
        self.assertEqual(len(cases), 6)
        self.assertEqual({(row["scheme"], row["degree"]) for row in cases},
                         set(itertools.product(("ckks", "bfv", "bgv"), ("128", "4096"))))


if __name__ == "__main__":
    unittest.main()
