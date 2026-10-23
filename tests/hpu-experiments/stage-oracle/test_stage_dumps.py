#!/usr/bin/env python3
"""显式使用历史RTL CSV核对独立C单stage参考；不运行或证明当前RTL。"""

import argparse
import csv
import ctypes
from pathlib import Path
import subprocess
import tempfile
import unittest


HPU_ROOT = Path(__file__).resolve().parents[2] / "hputest"


def column(path, name):
    with path.open(newline="", encoding="utf-8") as stream:
        return [int(row[name], 0) for row in csv.DictReader(stream)]


class HistoricalStageDumpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build = Path(__file__).resolve().parent / "build"
        build.mkdir(exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(prefix="stage-dump-host-", dir=build)
        cls.addClassCleanup(cls.temporary.cleanup)
        library = Path(cls.temporary.name) / "stage.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        "-I", str(HPU_ROOT / "include"), str(HPU_ROOT / "runtime/it_stage_reference.c"),
                        "-o", str(library)], check=True)
        cls.library = ctypes.CDLL(str(library))
        cls.reference = cls.library.stage_golden
        pointer = ctypes.POINTER(ctypes.c_uint32)
        cls.reference.argtypes = [pointer, pointer, pointer] + [ctypes.c_uint] * 4
        cls.reference.restype = ctypes.c_int

    def run_c(self, data, twiddle, stage, inverse):
        source = (ctypes.c_uint32 * len(data))(*data)
        table = (ctypes.c_uint32 * len(twiddle))(*twiddle)
        output = (ctypes.c_uint32 * len(data))()
        self.assertEqual(self.reference(source, table, output, len(data), 0xFFFFFFFE, stage, inverse), 0)
        return list(output)

    def test_fixed_pntt_rtl_stage0(self):
        fixture = FIXTURES / "rtl_pntt"
        data = column(fixture / "obj0_poly.csv", "value")
        table = column(fixture / "obj1_twiddle.csv", "value")[:len(data) // 2]
        expected = column(fixture / "obj2_output_exp_vs_rtl.csv", "rtl_act")
        self.assertEqual(self.run_c(data, table, 0, 0), expected)

    def test_fixed_pintt_rtl_stage0_and_stage1(self):
        fixture = FIXTURES / "rtl_pintt"
        for stage, input_file, output_file in (
                (0, "obj0_polyA.csv", "obj2_stage0_output_exp_vs_rtl.csv"),
                (1, "obj1_polyB.csv", "obj3_stage1_output_exp_vs_rtl.csv")):
            with self.subTest(stage=stage):
                data = column(fixture / input_file, "value")
                table = ([1] * (len(data) // 2) if stage == 0 else
                         column(fixture / "obj4_twiddle.csv", "value")[:len(data) // 2])
                expected = column(fixture / output_file, "rtl_act")
                self.assertEqual(self.run_c(data, table, stage, 1), expected)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", required=True, type=Path,
                        help="explicit historical ntt_hw_ut directory containing original RTL CSV files")
    args, remaining = parser.parse_known_args()
    FIXTURES = args.fixtures.resolve()
    for direction in ("rtl_pntt", "rtl_pintt"):
        if not (FIXTURES / direction).is_dir():
            parser.error("missing historical fixture directory: " + direction)
    unittest.main(argv=[__file__, *remaining])
