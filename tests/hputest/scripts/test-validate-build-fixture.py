#!/usr/bin/env python3
"""执行validate-build的真实fixture分支，防止把可空功能映射误当成catalog成员身份。"""

import csv
import os
from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = (ROOT / "scripts/validate-build.sh").read_text()
DISPATCH = re.search(r'^  case "\$elf" in\n.*?^  esac\n', VALIDATOR, re.M | re.S).group(0)
RNS_CHECK = re.search(r'^require_rns_fixture\(\) \{\n.*?^\}', VALIDATOR, re.M | re.S).group(0)
BUILD = (ROOT / "scripts/build.sh").read_text()
BUILD_SELECTION = BUILD[BUILD.index('scope_roster=$(python3 '):
                        BUILD.index('if [[ ${#case_sources[@]} -eq 0 ]]')]
VALIDATE_SELECTION = VALIDATOR[VALIDATOR.index('declare -A selected_ids=()'):
                                VALIDATOR.index('expected_cases=${#selected_case_ids[@]}')]


def read_catalog(name):
    with (ROOT / name).open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


CASES = {row["case_id"]: row for row in read_catalog("cases.tsv")}


def run_policy(rows, real_elf=None):
    check = RNS_CHECK if real_elf else 'require_rns_fixture() { printf "%s\\n" "$name"; }'
    shell = ('set -euo pipefail\ntest_root=$1\ncross_compile=$2\n' + check + '\n'
             'require_watchdog_mod_fixture() { :; }\nreject_mm_only_fixture() { :; }\n'
             'while IFS=$\'\\t\' read -r name qualifier elf; do\n' + DISPATCH + '\ndone\n')
    inputs = ''.join(f"{row['case_id']}\t{row['qualifier']}\t"
                     f"{real_elf or '/artifact/' + row['source'].removeprefix('src/').removesuffix('.c') + '.elf'}\n"
                     for row in rows)
    return subprocess.run(["bash", "-c", shell, "fixture-policy", str(ROOT),
                           os.environ.get("CROSS_COMPILE", "riscv64-linux-gnu-")],
                          input=inputs, capture_output=True, text=True)


class FixturePolicyTests(unittest.TestCase):
    def test_builder_and_validator_use_the_same_functional_roster(self):
        setup = '''set -euo pipefail
test_root=$1
script_dir=$test_root/scripts
build_scope=$2
case_group=all
case_filter=
manifest_selection=$build_scope
roster_ids=()
declare -A roster_group=() roster_qualifier=() roster_source=() roster_path_ids=()
while IFS=$'\t' read -r group qualifier case_id source; do
  [[ $case_id == case_id ]] && continue
  roster_ids+=("$case_id")
  roster_group[$case_id]=$group
  roster_qualifier[$case_id]=$qualifier
  roster_source[$case_id]=$source
  roster_path_ids[$source]=$case_id
done < "$test_root/cases.tsv"
'''
        for scope, count in (('all', 340), ('functional', 140)):
            with self.subTest(scope=scope):
                expected = {name for name, row in CASES.items()
                            if scope == 'all' or not row['source'].startswith('src/07_performance/')}
                built = subprocess.run(['bash', '-c', setup + BUILD_SELECTION +
                                        '\nprintf "%s\\n" "${case_sources[@]}"\n',
                                        'build-scope', str(ROOT), scope], capture_output=True, text=True)
                self.assertEqual(built.returncode, 0, built.stderr)
                self.assertEqual({Path(path).stem for path in built.stdout.splitlines()}, expected)
                validated = subprocess.run(['bash', '-c', setup + VALIDATE_SELECTION +
                                            '\nprintf "%s\\n" "${selected_case_ids[@]}"\n',
                                            'validate-scope', str(ROOT), scope], capture_output=True, text=True)
                self.assertEqual(validated.returncode, 0, validated.stderr)
                self.assertEqual(set(validated.stdout.splitlines()), expected)
                self.assertEqual(len(expected), count)

    def test_all_performance_catalog_members_use_their_own_images(self):
        perf = read_catalog("perf-cases.tsv")
        self.assertTrue(any(not row['functional_case_id'] for row in perf))
        self.assertTrue(any(row['level'] == '16' for row in perf))
        self.assertTrue(any(row['degree'] != '65536' for row in perf))
        result = run_policy([CASES[row['case_id']] for row in perf])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "", "catalog成员不应要求通用RNS fixture")

    def test_scheme_and_large_catalog_members_keep_their_exemption(self):
        rows = read_catalog('scheme-cases.tsv') + read_catalog('large-cases.tsv')
        result = run_policy([CASES[row['case_id']] for row in rows])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_ordinary_cases_still_require_generic_fixture(self):
        names = ['01_01_mmio_rw', '03_01_padd', '03_04_pmac']
        result = run_policy([CASES[name] for name in names])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), names)

    def test_similar_name_cannot_bypass_membership(self):
        row = dict(CASES[read_catalog('perf-cases.tsv')[0]['case_id']])
        row['case_id'] += '_not_in_catalog'
        result = run_policy([row])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [row['case_id']])

    @unittest.skipUnless(os.environ.get('HPU_FIXTURE_ELF_ROOT'),
                         '设置HPU_FIXTURE_ELF_ROOT以只读核对已构建ELF')
    def test_built_baseline_and_level16_images_do_not_need_rns_arrays(self):
        elf_root = Path(os.environ['HPU_FIXTURE_ELF_ROOT'])
        prefix = os.environ.get('CROSS_COMPILE', 'riscv64-linux-gnu-')
        for name in ('07_04_ckks_keyswitch_l4_n4096', '07_23_ckks_keyswitch_l16_n4096'):
            with self.subTest(case=name):
                elf = elf_root / '07_performance' / (name + '.elf')
                self.assertTrue(elf.is_file(), str(elf))
                nm = subprocess.run([prefix + 'nm', '-S', '--defined-only', str(elf)],
                                    capture_output=True, text=True, check=True)
                symbols = {line.split()[-1] for line in nm.stdout.splitlines() if line.split()}
                self.assertNotIn('RNS_A', symbols)
                self.assertNotIn('RNS_B', symbols)
                result = run_policy([CASES[name]], real_elf=elf)
                self.assertEqual(result.returncode, 0, result.stderr)
                # 同一个缺少RNS数据的ELF若冒充普通PADD，真实nm检查仍须拒绝。
                invalid = run_policy([CASES['03_01_padd']], real_elf=elf)
                self.assertEqual(invalid.returncode, 2, invalid.stderr)
                self.assertIn('does not embed 16384-byte RNS_A', invalid.stderr)


if __name__ == '__main__':
    unittest.main()
