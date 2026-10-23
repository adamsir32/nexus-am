#!/usr/bin/env python3
"""使用固定新版编码器准备00～03组，无旧FHE依赖或旧ISA缓存。"""

import argparse
import ctypes
import json
import os
from pathlib import Path
import shlex
import struct
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def run(arguments):
    subprocess.run([str(value) for value in arguments], check=True)


def output(arguments):
    return subprocess.check_output([str(value) for value in arguments], text=True).strip()


def read_words(path):
    data = path.read_bytes()
    return struct.unpack(f"<{len(data) // 4}I", data)


def verify_reference(generated, library):
    # 实际目标端C参考与上游物理模型逐字对拍，不将主机通过冒充RTL通过。
    model = ctypes.CDLL(str(library)).stage_golden
    ptr = ctypes.POINTER(ctypes.c_uint32)
    model.argtypes = [ptr, ptr, ptr, ctypes.c_uint, ctypes.c_uint32, ctypes.c_uint, ctypes.c_uint]
    model.restype = ctypes.c_int
    data_type = ctypes.c_uint32 * 4096
    full_type = ctypes.c_uint32 * 2048
    inputs = [read_words(generated / "inline-asm/mm/test_data/hardware/images/input_a.u32.bin"),
              read_words(generated / "stage-model/edge_a.u32.bin")]
    for inverse, direction in enumerate(("ntt", "intt")):
        for stage in (0, 1, 11):
            stem = f"{direction}_stage_{stage:02d}"
            full = full_type(*read_words(generated / "instruction-data" / f"{stem}_full.u32.bin"))
            for profile, values in enumerate(inputs):
                actual = data_type()
                if model(data_type(*values), full, actual, 4096, 50061313, stage, inverse) != 0:
                    raise RuntimeError(f"独立C参考拒绝{stem}/profile{profile}")
                expected = read_words(generated / "stage-model" / f"{stem}_profile{profile}.u32.bin")
                if tuple(actual) != expected:
                    raise RuntimeError(f"独立C参考与上游模型不一致：{stem}/profile{profile}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("producer", "output", "native-build"):
        parser.add_argument("--" + name, required=True, type=lambda value: Path(value).resolve())
    args = parser.parse_args()
    expected = json.loads((ROOT.parent / "hpu_frontend_workload/producer.json").read_text())["commit"]
    commit = output(["git", "-C", args.producer, "rev-parse", "HEAD"])
    if commit != expected:
        raise RuntimeError("低层producer必须与当前新版gitlink固定提交一致")
    if output(["git", "-C", args.producer, "status", "--porcelain", "--untracked-files=no"]):
        raise RuntimeError("低层producer有未提交修改")
    args.native_build.mkdir(parents=True, exist_ok=True)
    args.output.mkdir(parents=True, exist_ok=True)
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    executable = args.native_build / "generate-lowlevel"
    sources = [ROOT / "scripts/generate-lowlevel.cpp"] + [args.producer / "encode/src" / (stem + ".cpp")
               for stem in ("assembler", "encoder", "instruction", "parser", "executable")]
    sources.append(args.producer / "src/hpu/model/hardware_ntt.cpp")
    run([*compiler, "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror",
         "-I" + str(args.producer / "encode/include"), "-I" + str(args.producer / "include"),
         *sources, "-o", executable])
    run([executable, args.output, commit])
    library = args.native_build / "lowlevel-stage-reference.so"
    run([*shlex.split(os.environ.get("CC", "cc")), "-shared", "-fPIC", "-O2", "-Wall", "-Wextra", "-Werror",
         "-I" + str(ROOT / "include"), ROOT / "runtime/it_stage_reference.c", "-o", library])
    verify_reference(args.output, library)
    metadata = {"producer_commit": commit, "isa": "64-object-v1.2", "twiddle": "hpu-twiddle-k8-v1",
                "fixture": "AM确定性输入；MM逐项模乘；单stage独立C与上游物理模型对拍",
                "single_stage_rounds_verified": 12, "status": "BUILD_READY_NOT_IT_PASS"}
    (args.output / "lowlevel.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
    print("00～03组数据已生成：现代ISA，12个单stage参考轮次通过；未运行RTL。")


if __name__ == "__main__":
    main()
