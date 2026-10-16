#!/usr/bin/env python3
"""核验N65536扩展的绑定、计时边界和真实计时日志协议。"""
import argparse
import csv
import importlib.util
import json
import re
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
        self.assertEqual(len(perf),22);self.assertEqual(len(large),13)
        self.assertEqual(len({r['functional_case_id'] for r in perf}),22)
        for row in perf:
            self.assertEqual(row['degree'],'65536')
            self.assertTrue(row['functional_case_id'].startswith(('04_','05_')))
            self.assertEqual(cases[row['case_id']]['source'],row['source'])
            code=(ROOT/row['source']).read_text()
            start=code.index('cycle_start = perf_cycle_read();')
            issue=code.index('rc = hpu_run_'+row['program_stem']+'();')
            wait=code.index('rc = application_wait();')
            end=code.index('cycle_end = perf_cycle_read();')
            check=code.index('application_check_results()')
            print_result=code.index('LOG_EVENT("[HPU][PERF]')
            self.assertTrue(start<issue<wait<end<check<print_result)
            self.assertEqual(code.count('perf_cycle_read()'),2)
            self.assertNotIn('for (',code)
            self.assertNotIn('phase_mark',code[start:end])
        self.assertEqual({r['functional_case_id'] for r in perf},
            {c for c in cases if c.startswith(('04_','05_')) and c.endswith('_n65536')})

    def test_data_geometry_model_evidence_and_guard(self):
        for row in rows('large-cases.tsv'):
            directory=ARGS.generated/'large-data'/row['program_stem']
            p=json.loads((directory/'PARAMETERS.json').read_text())
            self.assertEqual(p['degree'],65536)
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

    def test_verified_cycle_records_and_rejection(self):
        case=rows('perf-cases.tsv')[0]['case_id']
        with tempfile.TemporaryDirectory(prefix='perf-record-') as temporary:
            path=Path(temporary)/'synthetic-unit-test.log'
            valid=f'[HPU][PERF] case={case} N=65536 metric=issue_to_done start=100 end=350 cycles=250 verified=1'
            path.write_text(valid+'\n')
            self.assertEqual(parser.parse([path],{case})[0]['cycles'],250)
            for invalid in (valid.replace('cycles=250','cycles=249'),valid.replace('verified=1','verified=0'),valid[:-5],valid.replace(case,'unknown')):
                path.write_text(invalid+'\n')
                with self.assertRaises(ValueError): parser.parse([path],{case})


if __name__=='__main__':
    options=argparse.ArgumentParser();options.add_argument('--generated',type=Path,required=True)
    options.add_argument('--elf-root',type=Path)
    ARGS,extra=options.parse_known_args();unittest.main(argv=[__file__,*extra])
