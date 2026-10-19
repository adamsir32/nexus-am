#!/usr/bin/env python3
"""核验多规模07绑定、计时边界和真实计时日志协议。"""
import argparse
import csv
import importlib.util
import json
import re
import os
import subprocess
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
def rows(name):
    with (ROOT/name).open() as stream: return list(csv.DictReader(stream,delimiter='\t'))
spec=importlib.util.spec_from_file_location('perf_parser',Path(__file__).with_name('parse-perf-results.py'))
parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)


class LargeCases(unittest.TestCase):
    def test_actual_timing_endpoints_when_supplied(self):
        if ARGS.elf_root is None: self.skipTest('no prebuilt ELF directory supplied')
        for mode in ('normal','silent'):
            for row in rows('perf-cases.tsv'):
                text=(ARGS.elf_root/mode/'07_performance'/(row['case_id']+'.txt')).read_text()
                self.assertEqual(len(re.findall(r'jal\s+[^\n]*<perf_cycle_read>',text)),2)
                self.assertIn('rdcycle',text)

    def test_matrix_and_single_program_timing(self):
        cases={r['case_id']:r for r in rows('cases.tsv')}
        perf=rows('perf-cases.tsv');large=rows('large-cases.tsv')
        self.assertEqual(len(perf),88);self.assertEqual(len(large),13)
        self.assertEqual({degree: sum(r['degree']==degree for r in perf) for degree in ('8192','16384','32768','65536')},
                         {degree: 22 for degree in ('8192','16384','32768','65536')})
        for row in perf:
            self.assertEqual(row['metric'],'issue_to_done_v2')
            if row['degree']=='65536':
                self.assertTrue(row['functional_case_id'].startswith(('04_','05_')))
            else:
                self.assertEqual(row['functional_case_id'],'')
            self.assertEqual(cases[row['case_id']]['source'],row['source'])
            code=(ROOT/row['source']).read_text()
            validate=code.index('rc = hpu_validate_'+row['program_stem']+'();')
            start=code.index('cycle_start = perf_cycle_read();')
            issue=code.index('rc = hpu_run_'+row['program_stem']+'();')
            wait=code.index('rc = application_wait();')
            end=code.index('cycle_end = perf_cycle_read();')
            check=code.index('application_check_results()')
            print_result=code.index('LOG_EVENT("[HPU][PERF]')
            self.assertTrue(validate<start<issue<wait<end<check<print_result)
            self.assertEqual(code.count('perf_cycle_read()'),2)
            self.assertNotIn('for (',code)
            self.assertNotIn('phase_mark',code[start:end])
        self.assertEqual({r['functional_case_id'] for r in perf if r['functional_case_id']},
            {c for c in cases if c.startswith(('04_','05_')) and c.endswith('_n65536')})

    def test_data_geometry_model_evidence_and_guard(self):
        programs={r['program_stem']: r for r in rows('large-cases.tsv')}
        programs.update({r['program_stem']:r for r in rows('perf-cases.tsv') if r['delivery']=='large-data'})
        self.assertEqual(len(programs),25)
        for row in programs.values():
            directory=ARGS.generated/'large-data'/row['program_stem']
            p=json.loads((directory/'PARAMETERS.json').read_text())
            self.assertEqual(p['degree'],int(row.get('degree',65536)))
            self.assertIs(p['model_verified'],True);self.assertIs(p['rtl_verified'],False)
            self.assertIn('mismatched_limbs=0',(directory/'PROGRAM_MODEL.log').read_text())
            words=[int(word,2) for word in (directory/(row['program_stem']+'.inst32')).read_text().split()]
            self.assertEqual(words[-1],0x7000005b);self.assertEqual(words.count(0x7000005b),1)
            image=directory/'application_window.u32.bin'
            self.assertEqual(image.stat().st_size,(p['used_lines']+64)*256)
            self.assertLessEqual(0x90000000+image.stat().st_size,0xa0000000)
            mask=(directory/'application_writable.u8.bin').read_bytes()
            self.assertEqual(len(mask),p['used_lines']+64)
            self.assertEqual(mask[-64:],bytes(64))
        auto=json.loads((ARGS.generated/'large-data/auto_n65536/PARAMETERS.json').read_text())
        self.assertIs(auto['auto_layout']['host_preprocess'],False)

    def test_all_performance_packages_preserve_native_program_and_oracle(self):
        for row in rows('perf-cases.tsv'):
            stem=row['program_stem']; directory=ARGS.generated/row['delivery']/stem
            report=json.loads((directory/'PERF_ADAPTATION.json').read_text())
            self.assertEqual(report['metric'],'issue_to_done_v2')
            self.assertIs(report['timed_parameter_checks'],False)
            self.assertIs(report['timed_trace_writes'],False)
            self.assertIs(report['preflight_emits_hpu'],False)
            code=(directory/(stem+'_perf.c')).read_text()
            words=[int(w,16) for w in re.findall(r'\.word (0x[0-9A-Fa-f]+)',code)]
            self.assertEqual(words,[int(w,2) for w in (directory/(stem+'.inst32')).read_text().split()])
            if stem.startswith('seal_'):
                oracle=json.loads((directory/'SEAL_ORACLE.json').read_text())
                self.assertEqual(oracle['degree'],int(row['degree']))
                self.assertEqual(oracle['raw_word_mismatches'],0)
                self.assertEqual(oracle['status'],'PASS')
            self.assertIn('mismatched_limbs=0',(directory/'PROGRAM_MODEL.log').read_text())

    def test_actual_preflight_accepts_every_bound_package(self):
        with tempfile.TemporaryDirectory(prefix='hpu-perf-valid-') as temporary:
            folder=Path(temporary)
            for row in rows('perf-cases.tsv'):
                stem=row['program_stem']; directory=ARGS.generated/row['delivery']/stem
                harness=folder/'check.c'; executable=folder/'check'
                harness.write_text(f'#include "{stem}_perf.h"\nint main(void) {{ return hpu_validate_{stem}(); }}\n')
                subprocess.run([os.environ.get('CC','cc'),'-std=c11','-O1','-Wall','-Wextra','-Werror',
                                '-I',str(directory),str(directory/(stem+'_perf.c')),str(harness),'-o',str(executable)],check=True)
                subprocess.run([str(executable)],check=True)

    def test_verified_cycle_records_and_rejection(self):
        case=rows('perf-cases.tsv')[0]['case_id']
        with tempfile.TemporaryDirectory(prefix='perf-record-') as temporary:
            path=Path(temporary)/'synthetic-unit-test.log'
            valid=f'[HPU][PERF] case={case} N=65536 metric=issue_to_done_v2 start=100 end=350 cycles=250 verified=1'
            path.write_text(valid+'\n')
            self.assertEqual(parser.parse([path],{case})[0]['cycles'],250)
            for invalid in (valid.replace('cycles=250','cycles=249'),valid.replace('verified=1','verified=0'),valid[:-5],valid.replace(case,'unknown'),valid.replace('N=65536','N=8192'),valid.replace('issue_to_done_v2','issue_to_done')):
                path.write_text(invalid+'\n')
                with self.assertRaises(ValueError): parser.parse([path],{case})
            for row in rows('perf-cases.tsv'):
                path.write_text(f"[HPU][PERF] case={row['case_id']} N={row['degree']} metric=issue_to_done_v2 start=100 end=350 cycles=250 verified=1\n")
                self.assertEqual(parser.parse([path],{row['case_id']:row['degree']})[0]['degree'],int(row['degree']))


if __name__=='__main__':
    options=argparse.ArgumentParser();options.add_argument('--generated',type=Path,required=True)
    options.add_argument('--elf-root',type=Path)
    ARGS,extra=options.parse_known_args();unittest.main(argv=[__file__,*extra])
