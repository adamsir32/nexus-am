"""单运行包构建调度与恢复合同；所有生产者、AM编译均使用Mock。"""
import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


SPEC = importlib.util.spec_from_file_location("build_runtime", Path(__file__).with_name("build-runtime.py"))
runtime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime)


class RuntimeBuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hpu-runtime-build-test-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.args = SimpleNamespace(output=self.directory / "output", am_home=runtime.ROOT.parents[1],
                                    producer=self.directory / "producer", native_build=self.directory / "native",
                                    lowlevel_cache=None, arch="riscv64-xs", cross="riscv64-linux-gnu-",
                                    wait_cycles=25000000, jobs=4, group=None, case=None, resume=False)
        (self.args.output / "logs").mkdir(parents=True)

    @staticmethod
    def row(spec):
        identity = spec["case_id"]
        return dict(group=identity[:2], case_id=identity, producer="runtime",
                    elf=f"{identity[:2]}/{identity}.elf", bin=f"{identity[:2]}/{identity}.bin",
                    degree=spec.get("degree", 0), level=spec.get("level", ""),
                    qualifier=spec.get("qualifier", "software-self-check"))

    def invoke_main(self, filters, output):
        low = Mock(side_effect=lambda args, specs: [self.row(spec) for spec in specs])
        functional = Mock(side_effect=lambda args, spec, pin, validator: self.row(spec))
        perf = Mock(side_effect=lambda args, spec, pin, validator: self.row(spec))
        native = Mock(return_value=("pin", self.directory / "validator"))
        command = ["build-runtime.py", "--am-home", str(self.args.am_home),
                   "--producer", str(self.args.producer), "--output", str(output), *filters]
        with patch.object(runtime.sys, "argv", command), patch.object(runtime, "build_lowlevel", low), \
                patch.object(runtime, "build_functional", functional), patch.object(runtime, "build_perf", perf), \
                patch.object(runtime, "prepare_native", native), patch.object(runtime, "run") as run, \
                patch.object(runtime, "target_recipe", return_value={}), \
                contextlib.redirect_stdout(io.StringIO()):
            runtime.main()
        return low, functional, perf, native, run

    def test_default_schedules_canonical_suite_and_only_one_package(self):
        low, functional, perf, native, run = self.invoke_main([], self.directory / "default")
        expected = [row for row in runtime.catalog_specs() if row["suite"] == "default"]
        self.assertEqual(len(expected), 109)
        self.assertEqual(sum(r["kind"] == "lowlevel" for r in expected), 35)
        self.assertEqual(len(low.call_args.args[1]), sum(r["kind"] == "lowlevel" for r in expected))
        self.assertEqual(functional.call_count, sum(r["kind"] in ("native", "instruction") for r in expected))
        self.assertEqual(perf.call_count, sum(r["kind"] == "performance" for r in expected))
        self.assertEqual(native.call_count, 1)
        rows = runtime.read_catalog(self.directory / "default/runtime-cases.tsv")
        self.assertEqual(len(rows), len(expected))
        self.assertEqual(len({row["case_id"] for row in rows}), len(expected))
        self.assertEqual({row["group"] for row in rows}, {f"{number:02}" for number in range(8)})
        self.assertTrue(all(row["elf"].endswith(".elf") and row["bin"].endswith(".bin") for row in rows))
        self.assertEqual(run.call_count, 1)
        self.assertIn("--check-tree", run.call_args.args[0])
        self.assertEqual(Path(run.call_args.args[0][-1]).name, "hpu.zip")

    def test_retired_parameters_and_old_directed_03_are_rejected_even_for_listing(self):
        original = runtime.read_catalog(runtime.ROOT / "cases.tsv")
        for group in ("03", "04", "05", "07"):
            template = next(row for row in original if row["group"] == group)
            retired = ((128, 4), (2048, 4), (4096, 4), (1024, 3)) if group != "07" else ((2048, 4), (4096, 4), (8192, 3))
            for degree, level in retired:
                row = {**template, "degree": str(degree), "level": str(level)}
                with self.subTest(group=group, degree=degree, level=level), \
                        patch.object(runtime, "read_catalog", return_value=[row]), self.assertRaisesRegex(ValueError, "仅接受"):
                    runtime.catalog_specs(validate_sources=False)
        directed = {**next(row for row in original if row["group"] == "03"), "kind": "lowlevel"}
        with patch.object(runtime, "read_catalog", return_value=[directed]), self.assertRaisesRegex(ValueError, "原生用例"):
            runtime.catalog_specs(validate_sources=False)

    def test_group_and_case_filters_never_schedule_other_groups(self):
        scenarios = [(["--group", "00"], 11, 0, 0),
                     (["--group", "04"], 0, sum(r["group"] == "04" for r in runtime.catalog_specs()), 0),
                     (["--case", "07_03_ckks_hmul_reline_l4_n1024"], 0, 0, 1)]
        for number, (filters, low_count, functional_count, perf_count) in enumerate(scenarios):
            with self.subTest(filters=filters):
                low, functional, perf, native, unused_run = self.invoke_main(filters, self.directory / f"filter-{number}")
                self.assertEqual(len(low.call_args.args[1]) if low.called else 0, low_count)
                self.assertEqual(functional.call_count, functional_count)
                self.assertEqual(perf.call_count, perf_count)
                self.assertEqual(native.call_count, int(bool(functional_count or perf_count)))

    def test_conflicting_group_and_case_stop_before_build(self):
        with self.assertRaisesRegex(ValueError, "筛选未命中"):
            self.invoke_main(["--group", "00", "--case", "07_03_ckks_hmul_reline_l4_n1024"],
                             self.directory / "no-match")
        self.assertFalse((self.directory / "no-match/RUNTIME_BUILD_REQUEST.json").exists())

    def test_resume_requires_the_identical_roster_pin_and_target_parameters(self):
        spec = dict(case_id="00_02_probe", degree=0, qualifier="software-self-check")
        runtime.prepare_export(self.args, [spec], [], [])
        self.args.resume = True
        runtime.prepare_export(self.args, [spec], [], [])
        with self.assertRaisesRegex(ValueError, "resume的清单"):
            runtime.prepare_export(self.args, [{**spec, "case_id": "00_03_probe"}], [], [])
        self.args.wait_cycles += 1
        with self.assertRaisesRegex(ValueError, "resume的清单"):
            runtime.prepare_export(self.args, [spec], [], [])
        self.args.wait_cycles -= 1
        original = runtime.read_json
        with patch.object(runtime, "read_json", wraps=original) as read:
            read.side_effect = lambda path: {"commit": "another-pin"} if path.name == "producer.json" else original(path)
            with self.assertRaisesRegex(ValueError, "resume的清单"):
                runtime.prepare_export(self.args, [spec], [], [])

    def test_source_recipes_reject_changed_target_or_generator_without_pin_change(self):
        low = dict(case_id="00_02_probe", degree=0)
        runtime.prepare_export(self.args, [low], [], [])
        self.args.resume = True
        recipe = runtime.target_recipe(self.args, [low], [], [])
        self.assertFalse(any("README" in Path(name).name or "/test/" in name or
                             Path(name).name.startswith(("test_", "test-")) for name in recipe))
        changed = {**recipe, "am/src/xs/common/trm.c": "changed target wrapper"}
        with patch.object(runtime, "target_recipe", return_value=changed):
            with self.assertRaisesRegex(ValueError, "resume的清单"):
                runtime.prepare_export(self.args, [low], [], [])

        group = dict(case_id="04_01_probe", degree=4096, profile="primitive")
        group_recipe = runtime.native_recipe(group)
        self.assertTrue(any(name.endswith("group_cases/generator.cpp") for name in group_recipe))
        self.assertTrue(any(name.endswith("group_cases/composite.cpp") for name in group_recipe))
        perf_recipe = runtime.native_recipe({"case_id": "07_01_probe"})
        self.assertTrue(any(name.endswith("operator_perf/generator.cpp") for name in perf_recipe))
        self.assertFalse(any("group_cases/" in name for name in perf_recipe))
        package = self.args.output / "packages/source-probe"
        with patch.object(runtime, "run", side_effect=lambda *args, **kwargs: package.mkdir()):
            runtime.ensure_package(self.args, group, "same-pin", ["mock-generator", package], package)
        changed_group = {**group_recipe, "tests/hputest/tools/group_cases/generator.cpp": "changed generator"}
        with patch.object(runtime, "native_recipe", return_value=changed_group):
            with self.assertRaisesRegex(ValueError, "现有包不完整或参数不同"):
                runtime.ensure_package(self.args, group, "same-pin", ["mock-generator", package], package)

    def test_resume_rejects_unowned_output_extra_files_and_partial_pairs(self):
        spec = dict(case_id="00_02_probe", degree=0)
        self.args.resume = True
        with self.assertRaisesRegex(ValueError, "resume的清单"):
            runtime.prepare_export(self.args, [spec], [], [])
        self.args.resume = False
        runtime.prepare_export(self.args, [spec], [], [])
        self.args.resume = True
        group = self.args.output / "runtime/00"
        group.mkdir(parents=True)
        (group / "00_02_probe.elf").write_bytes(b"partial")
        with self.assertRaisesRegex(ValueError, r"完整ELF\+BIN"):
            runtime.prepare_export(self.args, [spec], [], [])
        (group / "00_02_probe.bin").write_bytes(b"completed pair")
        (group / "unexpected.c").write_text("must not mix")
        with self.assertRaisesRegex(ValueError, "清单外文件"):
            runtime.prepare_export(self.args, [spec], [], [])

    def test_staging_reuses_only_byte_identical_pairs_without_overwriting(self):
        spec = dict(case_id="00_02_probe", degree=0)
        elf, binary = self.directory / "probe.elf", self.directory / "probe.bin"
        elf.write_bytes(b"verified-elf")
        binary.write_bytes(b"verified-bin")
        row = runtime.stage_runtime(self.args, spec, elf, binary)
        self.args.resume = True
        with patch.object(runtime.shutil, "copyfile") as copy:
            self.assertEqual(runtime.stage_runtime(self.args, spec, elf, binary), row)
            copy.assert_not_called()
        binary.write_bytes(b"different-bin")
        with self.assertRaisesRegex(ValueError, "拒绝覆盖不同"):
            runtime.stage_runtime(self.args, spec, elf, binary)
        self.assertEqual((self.args.output / "runtime" / row["bin"]).read_bytes(), b"verified-bin")

    def test_native_cache_marker_stays_outside_the_strict_package_and_matches_request(self):
        spec = dict(case_id="04_01_probe", degree=4096)
        package = self.args.output / "packages/04_01_probe"
        with patch.object(runtime, "run", side_effect=lambda *args, **kwargs: package.mkdir()) as run:
            runtime.ensure_package(self.args, spec, "pin", ["mock-generator", package], package)
            runtime.ensure_package(self.args, spec, "pin", ["mock-generator", package], package)
            self.assertEqual(run.call_count, 1)
        self.assertEqual(list(package.iterdir()), [])
        self.assertTrue(package.with_name(package.name + ".request.json").is_file())
        with self.assertRaisesRegex(ValueError, "现有包不完整或参数不同"):
            runtime.ensure_package(self.args, {**spec, "degree": 8192}, "pin", ["mock-generator", package], package)

    def test_performance_build_only_uses_optimized_and_minimal_before_staging(self):
        spec = dict(case_id="07_01_probe", scheme="ckks", operation="hadd", degree=1024,
                    level=4, program_stem="probe")
        events = []
        with patch.object(runtime, "ensure_package") as ensure, \
                patch.object(runtime.performance, "validate_fixture", side_effect=lambda *args: events.append("fixture")), \
                patch.object(runtime, "run", side_effect=lambda *args, **kwargs: events.append("validator")), \
                patch.object(runtime, "verify_case_program", side_effect=lambda *args: events.append("program")) as program, \
                patch.object(runtime, "import_package", side_effect=lambda *args, **kwargs: events.append("import") or {}), \
                patch.object(runtime.performance, "perf_adapter"), \
                patch.object(runtime.performance, "build_case", side_effect=lambda *args: (
                    events.append("validated-elf") or {"elf": "probe.elf", "bin": "probe.bin"})) as build, \
                patch.object(runtime, "stage_runtime", side_effect=lambda *args: events.append("stage")):
            runtime.build_perf(self.args, spec, "pin", self.directory / "validator")
        self.assertIn("--optimized-only", ensure.call_args.args[3])
        self.assertEqual(build.call_args.args[1]["variant"], "optimized")
        self.assertEqual(program.call_args.args[1]["variant"], "optimized")
        self.assertEqual(build.call_args.args[-1], "minimal")
        self.assertEqual(events, ["fixture", "validator", "program", "import", "validated-elf", "stage"])

    def test_functional_staging_happens_after_embedded_verification(self):
        spec = dict(case_id="06_01_probe", profile="application", target="example", degree=128)
        events = []
        with patch.object(runtime, "ensure_package"), \
                patch.object(runtime, "run", side_effect=lambda *args, **kwargs: events.append("validator")), \
                patch.object(runtime, "verify_case_program", side_effect=lambda *args: events.append("program")), \
                patch.object(runtime, "import_package", side_effect=lambda *args, **kwargs: events.append("import") or {}), \
                patch.object(runtime.functional, "build_case", side_effect=lambda *args: events.append(args[-1])), \
                patch.object(runtime.performance, "verify_embedded", side_effect=lambda *args: events.append("embedded")), \
                patch.object(runtime, "stage_runtime", side_effect=lambda *args: events.append("stage")):
            runtime.build_functional(self.args, spec, "pin", self.directory / "validator")
        self.assertEqual(events, ["validator", "program", "import", "minimal", "embedded", "stage"])

    def test_asm_mismatch_stops_functional_and_performance_before_import_or_compilation(self):
        functional = dict(case_id="06_01_probe", profile="application", target="example", degree=128)
        perf = dict(case_id="07_01_probe", scheme="ckks", operation="hadd", degree=1024,
                    level=4, program_stem="probe")
        for builder, spec in ((runtime.build_functional, functional), (runtime.build_perf, perf)):
            with self.subTest(builder=builder.__name__), patch.object(runtime, "ensure_package"), \
                    patch.object(runtime, "run"), patch.object(runtime.performance, "validate_fixture"), \
                    patch.object(runtime, "verify_case_program", side_effect=ValueError("program asm differs")), \
                    patch.object(runtime, "import_package") as importer, \
                    patch.object(runtime.functional, "build_case") as functional_build, \
                    patch.object(runtime.performance, "build_case") as perf_build, \
                    patch.object(runtime, "stage_runtime") as stage:
                with self.assertRaisesRegex(ValueError, "program asm differs"):
                    builder(self.args, spec, "pin", self.directory / "validator")
                importer.assert_not_called()
                functional_build.assert_not_called()
                perf_build.assert_not_called()
                stage.assert_not_called()

    def test_case_source_and_variant_asm_are_receiver_inputs_not_native_generator_inputs(self):
        spec = dict(case_id="07_01_probe", source="src/07_performance/01_n1024/07_01_probe.c", kind="performance")
        source = runtime.ROOT / spec["source"]
        for variant, suffix in (("optimized", ".asm"), ("noopt", ".noopt.asm")):
            self.args.variant = variant
            with self.subTest(variant=variant), patch.object(runtime, "source_snapshot", return_value={}) as snapshot:
                runtime.target_recipe(self.args, [], [], [spec])
                paths = set(snapshot.call_args.args[0])
                self.assertIn(source, paths)
                self.assertIn(source.with_suffix(suffix), paths)
                self.assertIn(runtime.ROOT / "scripts/case_program.py", paths)
                self.assertNotIn(runtime.ROOT / "runtime/native_case.c", paths)
        native = runtime.native_sources(spec)
        self.assertNotIn(source, native)
        self.assertFalse(any(path.suffix == ".asm" or path.name == "case_program.py" for path in native))


if __name__ == "__main__":
    unittest.main()
