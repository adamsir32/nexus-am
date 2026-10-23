"""组件复用仅接受同合同的native，低层必须重编；小夹具不表示真实ELF通过。"""
import contextlib
import copy
import csv
import importlib.util
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


SPEC = importlib.util.spec_from_file_location("native_reuse_probe", Path(__file__).with_name("build-runtime.py"))
runtime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime)


class NativeReuseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hpu-native-reuse-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "completed"
        self.source.mkdir()
        self.args = SimpleNamespace(am_home=runtime.ROOT.parents[1], producer=self.root / "producer",
            native_build=self.root / "native", output=self.root / "fresh", arch="riscv64-xs",
            cross="riscv64-linux-gnu-", wait_cycles=25000000, suite="default", variant="optimized",
            log_level=1, reuse_native_from=self.source, resume=False)
        self.spec = dict(case_id="05_001_ckks_hadd_l1_n128", group="05", kind="native", profile="library",
                         scheme="ckks", operation="hadd", degree=128, level=1, program_stem="seal_ckks_hadd_l1_n128",
                         source="src/05_library/main.c", qualifier="software-self-check",
                         memory_base="0x87000000", minimum_ram_bytes=268435456)
        self.recipe = {"tests/hputest/runtime/native_case.c": "native unchanged"}
        with patch.object(runtime, "target_recipe", return_value=self.recipe):
            request = runtime.build_request(self.args, [], [self.spec], [])
        request["source_recipe"]["tests/hputest/runtime/it_progress.c"] = "old lowlevel source"
        (self.source / "RUNTIME_BUILD_REQUEST.json").write_text(json.dumps(request))
        (self.source / "hpu.zip").write_bytes(b"completed bundle fixture")
        identity = self.spec["case_id"]
        self.row = dict(group="05", case_id=identity, producer="runtime", elf=f"05/{identity}.elf",
                        bin=f"05/{identity}.bin", degree="128", level="1", qualifier="software-self-check")
        with (self.source / "runtime-cases.tsv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=runtime.FIELDS, delimiter="\t")
            writer.writeheader()
            writer.writerow(self.row)

    def plan(self):
        # 当前native组件不含变化的低层it_progress.c；不能直接放宽整个source_recipe。
        recipe = {key: value for key, value in self.recipe.items() if "it_progress" not in key}
        pin = runtime.read_json(runtime.ROOT / "producer.json")["commit"]
        with patch.object(runtime, "target_recipe", return_value=recipe), \
                patch.object(runtime.functional, "output", side_effect=[pin, ""]):
            return runtime.prepare_native_reuse(self.args, [self.spec], [])

    def test_unchanged_native_accepts_lowlevel_only_delta_without_editing_receipt(self):
        path = self.source / "RUNTIME_BUILD_REQUEST.json"
        original = path.read_bytes()
        self.assertEqual(self.plan()["source"], self.source)
        self.assertEqual(path.read_bytes(), original)
        self.assertFalse(self.args.output.exists())

    def test_pin_parameters_source_and_case_changes_are_rejected(self):
        path = self.source / "RUNTIME_BUILD_REQUEST.json"
        original = json.loads(path.read_text())
        for field, value in (("producer_commit", "other-pin"), ("wait_cycles", 17), ("variant", "noopt")):
            changed = copy.deepcopy(original)
            changed[field] = value
            path.write_text(json.dumps(changed))
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "构建参数不同"):
                self.plan()
        changed = copy.deepcopy(original)
        changed["source_recipe"]["tests/hputest/runtime/native_case.c"] = "modified native"
        path.write_text(json.dumps(changed))
        with self.assertRaisesRegex(ValueError, "native组件源码不同"):
            self.plan()
        changed = copy.deepcopy(original)
        changed["cases"][0]["level"] = 2
        path.write_text(json.dumps(changed))
        with self.assertRaisesRegex(ValueError, "用例参数不同"):
            self.plan()

    def test_lowlevel_reuse_incomplete_bundle_and_symlink_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "不能复用低层"):
            runtime.prepare_native_reuse(self.args, [], [])
        with self.assertRaisesRegex(ValueError, "禁止复用低层"):
            runtime.reuse_native_case(self.args, {"kind": "lowlevel"}, {})
        (self.source / "hpu.zip").unlink()
        with self.assertRaisesRegex(ValueError, "缺失或为空"):
            self.plan()
        (self.source / "hpu.zip").symlink_to(self.source / "RUNTIME_BUILD_REQUEST.json")
        with self.assertRaisesRegex(ValueError, "软链"):
            self.plan()

    def test_current_checkout_must_match_pin_and_remain_clean(self):
        pin = runtime.read_json(runtime.ROOT / "producer.json")["commit"]
        recipe = {"tests/hputest/runtime/native_case.c": "native unchanged"}
        for head, status in (("different checkout", ""), (pin, " M encode/src/encoder.cpp")):
            with self.subTest(head=head, status=status), \
                    patch.object(runtime, "target_recipe", return_value=recipe), \
                    patch.object(runtime.functional, "output", side_effect=[head, status]), \
                    self.assertRaisesRegex(ValueError, "固定提交且工作树干净"):
                runtime.prepare_native_reuse(self.args, [self.spec], [])

    def test_deleted_shared_header_cannot_disappear_from_the_component_contract(self):
        path = self.source / "RUNTIME_BUILD_REQUEST.json"
        request = json.loads(path.read_text())
        request["source_recipe"]["tests/hputest/include/hpu/deleted.h"] = "previously compiled header"
        path.write_text(json.dumps(request))
        with self.assertRaisesRegex(ValueError, "依赖集合不同"):
            self.plan()

    def test_reuse_compares_original_runtime_bytes_before_staging(self):
        identity = self.spec["case_id"]
        paths = {"packages/functional/" + identity + "/package.json": b"{}",
                 "generated/functional/" + identity + "/delivery.json": b"{}",
                 "generated/functional/" + identity + "/" + self.spec["program_stem"] + ".inst32": b"01110000000000000000000001011011\n"}
        artifact = "functional-build/artifact/minimal/" + identity + "/" + identity
        for suffix, contents in ((".elf", b"not-real-elf-fixture"), (".bin", b"binary-fixture")):
            paths[artifact + suffix] = contents
            paths["runtime/05/" + identity + suffix] = contents
        for relative, contents in paths.items():
            path = self.source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)
        plan = self.plan()
        with patch.object(runtime, "import_package", return_value={}), \
                patch.object(runtime.functional, "verify_elf", return_value=[0x7000005b]) as verify, \
                patch.object(runtime.performance, "verify_embedded") as embedded, \
                patch.object(runtime, "stage_runtime", return_value=self.row) as stage:
            self.assertEqual(runtime.reuse_native_case(self.args, self.spec, plan), self.row)
            verify.assert_called_once()
            embedded.assert_called_once()
            stage.assert_called_once()
            (self.source / "runtime/05" / (identity + ".bin")).write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "与已验证原产物不同"):
                runtime.reuse_native_case(self.args, self.spec, plan)
            self.assertEqual(stage.call_count, 1)

    def test_main_rebuilds_lowlevel_and_never_invokes_native_compilers_in_reuse_mode(self):
        def result(spec):
            name = spec["case_id"]
            return dict(group=spec["group"], case_id=name, producer="runtime", elf=f"{name[:2]}/{name}.elf",
                        bin=f"{name[:2]}/{name}.bin", degree=spec["degree"], level=spec["level"],
                        qualifier=spec["qualifier"])
        command = ["build-runtime.py", "--am-home", str(self.args.am_home), "--producer", str(self.args.producer),
                   "--output", str(self.args.output), "--native-build", str(self.args.native_build),
                   "--reuse-native-from", str(self.source)]
        low = Mock(side_effect=lambda args, specs: [result(row) for row in specs])
        reused = Mock(side_effect=lambda args, spec, plan: result(spec))
        with patch.object(runtime.sys, "argv", command), contextlib.redirect_stdout(io.StringIO()), \
                patch.object(runtime, "prepare_native_reuse", return_value={"source": self.source}), \
                patch.object(runtime, "prepare_export"), patch.object(runtime, "build_lowlevel", low), \
                patch.object(runtime, "reuse_native_case", reused), patch.object(runtime, "prepare_native") as native, \
                patch.object(runtime, "build_functional") as functional, patch.object(runtime, "build_perf") as perf, \
                patch.object(runtime, "run") as run:
            runtime.main()
        rows = [row for row in runtime.catalog_specs() if row["suite"] == "default"]
        self.assertEqual(len(low.call_args.args[1]), sum(row["kind"] == "lowlevel" for row in rows))
        self.assertEqual(reused.call_count, sum(row["kind"] != "lowlevel" for row in rows))
        native.assert_not_called()
        functional.assert_not_called()
        perf.assert_not_called()
        self.assertEqual(run.call_count, 1, "最终仍然只调用一次单包导出")

    def test_performance_rechecks_actual_disassembly_bytes_before_the_timing_gate(self):
        spec = {**self.spec, "kind": "performance", "case_id": "07_01_ckks_keyswitch_l4_n1024",
                "group": "07", "degree": 1024, "level": 4, "operation": "keyswitch"}
        identity = spec["case_id"]
        artifact = f"performance-build/artifact/optimized/minimal/{identity}/{identity}"
        contents = {f"packages/performance/{identity}/optimized/PERF_FIXTURE.json": b"{}",
                    f"packages/performance/{identity}/optimized/upstream/package.json": b"{}",
                    f"generated/performance/{identity}/delivery.json": b"{}",
                    artifact + ".elf": b"fake ELF fixture", artifact + ".bin": b"fake BIN fixture",
                    artifact + ".txt": b"\nactual disassembly\n"}
        for suffix in (".elf", ".bin"):
            contents[f"runtime/07/{identity}{suffix}"] = contents[artifact + suffix]
        for relative, data in contents.items():
            path = self.source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        with patch.object(runtime.performance, "validate_fixture"), \
                patch.object(runtime, "import_package", return_value={}), \
                patch.object(runtime.subprocess, "check_output", return_value=b"\nactual disassembly\n") as disassemble, \
                patch.object(runtime.performance, "verify_elf") as timing, \
                patch.object(runtime, "stage_runtime") as stage:
            plan = {"source": self.source, "producer_commit": "pin"}
            runtime.reuse_native_case(self.args, spec, plan)
            timing.assert_called_once()
            stage.assert_called_once()
            disassemble.return_value = b"different actual ELF disassembly"
            with self.assertRaisesRegex(ValueError, "反汇编与实际ELF不同"):
                runtime.reuse_native_case(self.args, spec, plan)
            self.assertEqual(timing.call_count, 1)
            self.assertEqual(stage.call_count, 1)


if __name__ == "__main__":
    unittest.main()
