"""--list与实际构建共用筛选，且不得准备native、打开producer或创建输出。"""
import contextlib
import csv
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location("runtime_list_probe", Path(__file__).with_name("build-runtime.py"))
runtime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime)


class RuntimeListTests(unittest.TestCase):
    def test_readonly_list_filters_group_n_level_scheme_and_suite(self):
        with tempfile.TemporaryDirectory(prefix="hpu-list-probe-") as temporary:
            directory = Path(temporary)
            output = directory / "must-not-be-created"
            command = ["build-runtime.py", "--am-home", str(runtime.ROOT.parents[1]),
                       "--producer", str(directory / "missing-producer"), "--output", str(output),
                       "--list", "--group", "05", "--degree", "1024", "--level", "4", "--scheme", "ckks"]
            stream = io.StringIO()
            with patch.object(runtime.sys, "argv", command), contextlib.redirect_stdout(stream), \
                    patch.object(runtime, "prepare_native", side_effect=AssertionError("native must not be touched")), \
                    patch.object(runtime, "read_json", side_effect=AssertionError("producer pin must not be opened")), \
                    patch.object(runtime, "load_module", side_effect=AssertionError("lowlevel must not be prepared")), \
                    patch.object(runtime, "run", side_effect=AssertionError("no build command")):
                runtime.main()
            self.assertFalse(output.exists())
            rows = list(csv.DictReader(io.StringIO(stream.getvalue()), delimiter="\t"))
            expected = [row for row in runtime.catalog_specs() if row["suite"] == "default" and
                        row["group"] == "05" and row["degree"] == 1024 and row["level"] == 4 and row["scheme"] == "ckks"]
            self.assertEqual([r["case_id"] for r in rows], [r["case_id"] for r in expected])
            self.assertTrue(all(row["purpose"] and row["N"] == "1024" and row["level"] == "4" for row in rows))

    def test_list_and_build_use_the_same_filter_and_api_selection(self):
        from types import SimpleNamespace
        args = SimpleNamespace(group="06", case=None, suite="api", degree=128, level=None,
                               scheme="bgv", list=True)
        listed = runtime.filtered_specs(args)
        args.list = False
        self.assertEqual(listed, runtime.filtered_specs(args))
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0]["suite"], "api")

    def test_application_degree_filters_keep_n128_n4096_and_n8192(self):
        from types import SimpleNamespace
        for degree in (128, 4096, 8192):
            args = SimpleNamespace(group="06", case=None, suite="all", degree=degree, level=None,
                                   scheme=None, list=True)
            with self.subTest(degree=degree):
                rows = runtime.filtered_specs(args)
                self.assertTrue(rows)
                self.assertTrue(all(row["degree"] == degree for row in rows))


if __name__ == "__main__":
    unittest.main()
