#!/usr/bin/env python3
"""只配置不编译：确认实验native目标不依赖旧hputest submodule。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

HERE=Path(__file__).resolve().parent


class NativeConfigure(unittest.TestCase):
    def test_configures_without_baseline_submodule(self):
        with tempfile.TemporaryDirectory(prefix='frontend-native-configure-',dir=ARGS.scratch) as temporary:
            root=Path(temporary)
            source=root/'tests/hpu_frontend_workload/tools/operator_perf'
            source.mkdir(parents=True)
            for name in ('CMakeLists.txt','generator.cpp'):
                shutil.copyfile(HERE/name,source/name)
            fixture=root/'tests/hputest/tools/hpu-scheme-cases'
            fixture.mkdir(parents=True)
            shutil.copyfile(HERE.parents[2]/'hputest/tools/hpu-scheme-cases/fixture.hpp',fixture/'fixture.hpp')
            self.assertFalse((root/'tests/hputest/third_party').exists())
            build=root/'native'
            result=subprocess.run(['cmake','-S',str(source),'-B',str(build),
                                   '-DINLINE_ASM_ROOT='+str(ARGS.inline_root),'-DCMAKE_BUILD_TYPE=Release'],
                                  capture_output=True,text=True,check=False)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            cache=(build/'CMakeCache.txt').read_text()
            for option in ('HPU_ENABLE_SEAL_DIFFERENTIAL_ORACLE','HPU_ENABLE_SEAL_BFV_ORACLE',
                           'SEAL_USE_MSGSL','SEAL_USE_ZLIB','SEAL_USE_ZSTD','SEAL_USE_INTEL_HEXL'):
                self.assertIn(option+':BOOL=OFF',cache)
            self.assertFalse((build/'hpu_frontend_operator_generator').exists())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inline-root',type=Path,required=True)
    parser.add_argument('--scratch',type=Path,required=True)
    ARGS,extra=parser.parse_known_args()
    ARGS.inline_root=ARGS.inline_root.resolve()
    ARGS.scratch.mkdir(parents=True,exist_ok=True)
    unittest.main(argv=[__file__,*extra])
