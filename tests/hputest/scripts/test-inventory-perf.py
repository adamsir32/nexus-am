#!/usr/bin/env python3
"""用实际交付包核验07四种规模的参数和Excel逐轮记录。"""
import argparse
from collections import Counter
import importlib.util
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('inventory',HERE/'export-case-inventory.py')
inventory=importlib.util.module_from_spec(spec);spec.loader.exec_module(inventory)


class PerformanceInventory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary=tempfile.TemporaryDirectory(prefix='hpu-inventory-perf-',dir=ARGS.generated.parent)
        cls.args=SimpleNamespace(generated=ARGS.generated,output=Path(cls.temporary.name),
                                 parameter_tool=ARGS.parameter_tool,
                                 legacy=Path('/unused/legacy'),st_github=False,st_snapshot=None)
        cls.perf=inventory.table(inventory.ROOT/'perf-cases.tsv')
        # 不加载对应功能用例：即使functional_case_id为空，也必须独立读取交付参数。
        read_table=inventory.table
        selected={row['case_id'] for row in cls.perf}
        selected.update(('03_16_pmodld_n65536','05_41_ckks_hmul_reline_n65536'))
        def subset(path,delimiter='\t'):
            rows=read_table(path,delimiter)
            return [row for row in rows if row['case_id'] in selected] if path.name=='cases.tsv' else rows
        with patch.object(inventory,'table',side_effect=subset):
            cls.records,cls.by_id=inventory.collect(cls.args)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_performance_parameters_match_each_delivery(self):
        self.assertEqual(len(self.perf),88)
        self.assertEqual(Counter(int(row['degree']) for row in self.perf),
                         {8192:22,16384:22,32768:22,65536:22})
        self.assertEqual(sum(not row['functional_case_id'] for row in self.perf),66)
        for row in self.perf:
            with self.subTest(case=row['case_id']):
                p=self.by_id[row['case_id']]['parameters']
                self.assertEqual(p['N'],int(row['degree']))
                self.assertEqual(p['program_stem'],row['program_stem'])
                self.assertEqual(p['metric'],'issue_to_done_v2')
                self.assertEqual(p['memory_base'],'0x90000000')
                self.assertEqual(p['minimum_ram_bytes'],536870912)
                self.assertEqual(p['functional_case_id'],row['functional_case_id'] or None)
                directory=ARGS.generated/row['delivery']/row['program_stem']
                if row['delivery']=='large-data':
                    original=inventory.load(directory/'PARAMETERS.json')
                    self.assertEqual(p['Q'],original['q_moduli'])
                    self.assertEqual(p['P'],original['p_moduli'])
                else:
                    upstream=directory/'upstream'
                    package=inventory.load(upstream/'package.json')
                    original=inventory.load(upstream/package['parameters'])
                    self.assertEqual(p['N'],original['poly_modulus_degree'])
                    self.assertEqual(p['Q'],original['levels'][0]['moduli'])
                    self.assertEqual(p['Q']+p['P'],original['key_moduli'])
                self.assertIsNone(self.by_id[row['case_id']]['IT_pass'])
                self.assertIsNone(self.by_id[row['case_id']]['ST_pass'])

    def test_functional_parameters_keep_their_semantics(self):
        pmod=self.by_id['03_16_pmodld_n65536']['parameters']
        self.assertEqual(len(pmod['Q']),1)
        self.assertEqual(pmod['modulus_table'],pmod['q_moduli'])
        functional=self.by_id['05_41_ckks_hmul_reline_n65536']['parameters']
        timed=self.by_id['07_05_ckks_hmul_reline_n65536']['parameters']
        self.assertEqual(functional,{key:value for key,value in timed.items()
                                    if key not in ('functional_case_id','metric')})
        self.assertNotIn('metric',pmod)

    def test_excel_rounds_use_actual_degree_and_leave_measurements_blank(self):
        from openpyxl import load_workbook
        inventory.output(self.args,self.records,self.by_id)
        book=load_workbook(self.args.output/'HPU_IT_ST用例与参数清单.xlsx')
        sheet=book['07性能逐轮记录']
        rows=list(sheet.iter_rows(min_row=2,values_only=True))
        self.assertEqual(len(rows),264)
        by_case={row['case_id']:row for row in self.perf}
        for row in rows:
            source=by_case[row[0]]
            self.assertEqual(row[1],source['functional_case_id'] or None)
            self.assertEqual(row[4],int(source['degree']))
            self.assertIn(row[2],(1,2,3))
            for column in (3,9,10,12,14):
                self.assertIsNone(row[column])
        self.assertEqual(Counter(row[4] for row in rows),
                         {8192:66,16384:66,32768:66,65536:66})


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generated',type=Path,required=True)
    parser.add_argument('--parameter-tool',type=Path,required=True)
    ARGS,extra=parser.parse_known_args()
    unittest.main(argv=[__file__,*extra])
