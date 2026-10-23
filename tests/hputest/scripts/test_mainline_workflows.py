"""主线只自动发布一个运行包；不构建生成器或依赖YAML第三方模块。"""
import csv
import itertools
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT.parents[1] / ".github/workflows"
RUNTIME_WORKFLOW = "build-hpu.yml"
MANUAL_ALIASES = ("build-hpu-operator-perf.yml", "build-hpu-frontend.yml")


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

    def test_only_one_hpu_workflow_has_automatic_triggers_and_one_job(self):
        text = (WORKFLOWS / RUNTIME_WORKFLOW).read_text()
        events = block(text, "on", 0)
        for event in ("push", "pull_request"):
            self.assertEqual(inline_list(block(events, event, 2), "branches"), ["master"])
        self.assertIn("  workflow_dispatch:", events)
        self.assertEqual(re.findall(r"^  ([\w-]+):$", block(text, "jobs", 0), re.M), ["runtime"])
        self.assertNotIn("matrix:", text)
        self.assertIn("scripts/build-runtime.py", text)
        self.assertNotIn("scripts/build_performance.py", text)
        self.assertNotIn("scripts/build.py", text)

    def test_old_duplicate_hpu_workflows_are_removed(self):
        for name in MANUAL_ALIASES:
            self.assertFalse((WORKFLOWS / name).exists())

    def test_runtime_filters_cover_all_group_sources_and_shared_am_code(self):
        events = block((WORKFLOWS / RUNTIME_WORKFLOW).read_text(), "on", 0)
        expected = ["tests/hputest/**", "tests/hpu_frontend_workload/**", "am/**", "libs/klib/**",
                    "Makefile.app", ".github/workflows/" + RUNTIME_WORKFLOW, ".gitmodules"]
        for event in ("push", "pull_request"):
            with self.subTest(event=event):
                paths = block(block(events, event, 2), "paths", 4)
                self.assertEqual(re.findall(r"^      - '([^']+)'$", paths, re.M), expected)

    def test_runtime_upload_is_one_short_non_nested_elf_and_bin_package(self):
        upload_workflows = []
        for path in WORKFLOWS.glob("build-hpu*.yml"):
            text = path.read_text()
            if "upload-artifact" in text:
                upload_workflows.append(path.name)
            for old_package in ("nexus-am-hpu-tests", "nexus-am-hpu-perf-n", "nexus-am-1019-operator-perf",
                                "nexus-am-hpu-frontend-workload"):
                self.assertNotIn(old_package, text)
        self.assertEqual(upload_workflows, [RUNTIME_WORKFLOW])
        text = (WORKFLOWS / RUNTIME_WORKFLOW).read_text()
        self.assertEqual(text.count("uses: actions/upload-artifact@"), 1)
        self.assertIn("          name: hpu\n", text)
        self.assertIn("${{ env.HPU_OUTPUT }}/runtime/**/*.elf", text)
        self.assertIn("${{ env.HPU_OUTPUT }}/runtime/**/*.bin", text)
        self.assertNotIn("${{ env.HPU_OUTPUT }}/hpu.zip", text)
        self.assertIn('--root "runtime=$HPU_OUTPUT/runtime" --check-tree --check-only', text)
        self.assertLess(text.index("--check-tree --check-only"), text.index("uses: actions/upload-artifact@"))

    def test_canonical_performance_and_optional_api_scopes_are_explicit(self):
        with (ROOT / "cases.tsv").open() as stream:
            rows = list(csv.DictReader(stream, delimiter="\t"))
        performance = [row for row in rows if row["kind"] == "performance"]
        self.assertEqual(len(performance), 36)
        self.assertTrue(all(row["level"] == "4" for row in performance))
        for degree, scheme in itertools.product(("1024", "8192"), ("ckks", "bfv", "bgv")):
            selected = [row for row in performance if (row["degree"], row["scheme"]) == (degree, scheme)]
            self.assertEqual(len(selected), 6)
        api = [row for row in rows if row["suite"] == "api"]
        self.assertEqual({(r["scheme"], r["degree"]) for r in api},
                         set(itertools.product(("ckks", "bfv", "bgv"), ("128", "4096"))))
        self.assertTrue(all(row["group"] == "06" and row["kind"] == "native" for row in api))

if __name__ == "__main__":
    unittest.main()
