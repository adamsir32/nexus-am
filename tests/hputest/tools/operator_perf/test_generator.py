#!/usr/bin/env python3
"""薄生成器host验收：共享Fixture、双调度变体、原生包和严格失败记录。"""
import argparse
import csv
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


class OperatorGenerator(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='frontend-operator-host-',dir=ARGS.scratch)
        self.addCleanup(self.temporary.cleanup)
        self.directory=Path(self.temporary.name)/'case'

    def run_generator(self,scheme='ckks',operation='hadd',profile='baseline',extra=(),degree=1024):
        return subprocess.run([str(ARGS.generator),scheme,operation,str(degree),profile,str(self.directory),*extra],
                              text=True,capture_output=True,check=False)

    def read_variants(self,native_package):
        sidecars=[]
        for variant in ('optimized','noopt'):
            folder=self.directory/variant
            metadata=json.loads((folder/'PERF_FIXTURE.json').read_text())
            resources=json.loads((folder/'RESOURCE_REPORT.json').read_text())
            self.assertIsInstance(resources,dict)
            self.assertEqual(metadata['variant'],variant)
            self.assertEqual(metadata['optimize_resources'],variant=='optimized')
            for field in ('verified','instruction_verified','fixture_words_equal','fixture_metadata_equal',
                          'same_seal_source'):
                self.assertIs(metadata[field],True)
            self.assertEqual(metadata['same_fixture_recipe'],metadata['scheme']!='bgv')
            self.assertEqual(metadata['baseline_parameters_equal'],metadata['scheme']!='bgv')
            self.assertEqual(metadata['baseline_input_level'],3 if metadata['scheme']=='bgv' else 4)
            self.assertIs(metadata['hardware_verified'],False)
            self.assertIs(metadata['hardware_contract_verified'],False)
            self.assertEqual(metadata['native_package_written'],native_package)
            self.assertEqual(metadata['producer_commit'],'4e26659cc0c9c3887c60491e8455ff5fd6028025')
            self.assertIs(metadata['profile_execution'],True)
            self.assertEqual(metadata['baseline_inline_asm_commit'],'03a32c168404f3ad64e6a4d7ad82a081f910314b')
            self.assertEqual(metadata['baseline_modified_seal_tree'],'036be909da472f4343b6bac6add0dcb3be5bd057')
            self.assertIn(metadata['producer_worktree_state'],('clean-at-configure','dirty-at-configure'))
            self.assertEqual(metadata['ntt_table_abi']['version'],4)
            self.assertEqual(metadata['ntt_table_abi']['coefficient_order'],'bit_reversed')
            self.assertEqual(metadata['ntt_table_abi']['external_coefficient_order'],'natural')
            self.assertEqual(metadata['ntt_table_abi']['pre_twist_order'],'bit_reversed')
            self.assertEqual(metadata['ntt_table_abi']['post_factor_order'],'bit_reversed')
            self.assertEqual(metadata['ntt_table_abi']['online_pmul_format'],'hpu-pmul-online-k8-v1')
            self.assertEqual(metadata['ntt_table_abi']['online_pmul_parameter_lines'],2)
            self.assertEqual(metadata['ntt_table_abi']['stage_twiddle_format'],'hpu-twiddle-k8-v1')
            self.assertEqual(metadata['ntt_table_abi']['twiddle_chains'],8)
            self.assertEqual(metadata['ntt_table_abi']['stage_parameter_lines'],2)
            self.assertEqual(metadata['seed'],['0x485055534348454d',1024,1,2,3,4,5,6])
            self.assertEqual((folder/'upstream').exists(),native_package)
            if native_package:
                package=json.loads((folder/'upstream/package.json').read_text())
                self.assertEqual(package['case_name'],metadata['program_stem'])
                self.check_execution_profile(folder/'upstream',package)
                parameters=json.loads((folder/'upstream'/package['parameters']).read_text())
                self.assertEqual(parameters['ntt_table_abi'],metadata['ntt_table_abi'])
                self.assertEqual(parameters['levels'][0]['moduli'],metadata['Q'])
                self.assertEqual(parameters['key_moduli'],metadata['Q']+metadata['P'])
                graph=json.loads((folder/'upstream'/package['operation_graph']).read_text())
                self.assertEqual([operation['kind'] for operation in graph['operations']],metadata['node_operations'])
                provenance=json.loads((folder/'upstream/provenance/build.json').read_text())
                self.assertEqual(provenance['commit'],metadata['producer_commit'])
                self.assertEqual(provenance['worktree_state'],metadata['producer_worktree_state'])
                if ARGS.validator:
                    subprocess.run([str(ARGS.validator),str(folder/'upstream')],check=True,capture_output=True,text=True)
            sidecars.append(metadata)
        excluded={'variant','optimize_resources'}
        self.assertEqual({k:v for k,v in sidecars[0].items() if k not in excluded},
                         {k:v for k,v in sidecars[1].items() if k not in excluded})
        self.assertFalse((self.directory/'GENERATION_ERROR.json').exists())
        return sidecars[0]

    def check_execution_profile(self,root,package):
        self.assertEqual(package.get('execution_profile_manifest'),'profiling/execution_window.csv')
        with (root/package['execution_profile_manifest']).open(newline='') as stream:
            windows=list(csv.DictReader(stream))
        self.assertEqual(len(windows),1)
        window=windows[0]
        self.assertEqual(list(window),['begin_instruction','end_instruction',
                                      'arithmetic_instruction_count','dload_count','dstore_count'])
        words=[int(word,2) for word in (root/package['program_inst32']).read_text().splitlines()]
        begin,end=int(window['begin_instruction']),int(window['end_instruction'])
        self.assertTrue(0<begin<end<len(words))
        self.assertEqual((words[begin-1],words[end]),(0x7000005b,0x7000005b))
        arithmetic=[index for index,word in enumerate(words) if word&127==0x5b and word>>28<=5]
        self.assertTrue(arithmetic)
        self.assertTrue(all(begin<=index<end for index in arithmetic))
        self.assertEqual(len(arithmetic),int(window['arithmetic_instruction_count']))
        with (root/package['dma_relocation_manifest']).open(newline='') as stream:
            dma=list(csv.DictReader(stream))
        report=json.loads((root/package['oracle_report']).read_text())
        timing=report['execution_profile']
        self.assertIs(timing['enabled'],True)
        self.assertEqual(timing['window_count'],1)
        self.assertIs(timing['timing_measured'],False)
        self.assertIs(timing['includes_residual_dma'],True)
        counts=dict(prefix_dload_count=0,window_dload_count=0,window_dstore_count=0,suffix_dstore_count=0)
        for row in dma:
            index=int(row['instruction_index'])
            self.assertEqual(int(row['word_hex'],16),words[index])
            direction=row['direction']
            if index<begin:
                self.assertEqual(direction,'dload')
                counts['prefix_dload_count']+=1
            elif index<end:
                counts['window_'+direction+'_count']+=1
            else:
                self.assertEqual(direction,'dstore')
                counts['suffix_dstore_count']+=1
        for name,count in counts.items():
            self.assertEqual(timing[name],count)
        self.assertEqual(int(window['dload_count']),counts['window_dload_count'])
        self.assertEqual(int(window['dstore_count']),counts['window_dstore_count'])
        self.assertLessEqual(len(dma),timing['unprofiled_dma_count'])
        self.assertLessEqual(sum(int(row['line_count'])*256 for row in dma),timing['unprofiled_dma_bytes'])
        code=(root/package['program_source']).read_text()
        self.assertEqual([int(word,16) for word in re.findall(r'\.word (0x[0-9A-Fa-f]+)',code)],words)
        self.assertEqual(code.count('hooks->read_cycles(hooks->user)'),2)
        self.assertEqual(code.count('hooks->wait_complete(hooks->user,'),words.count(0x7000005b))
        self.assertEqual(code.count('return -5;'),2)
        self.assertIn('hpu_run_'+package['case_name']+'_profiled(',code)
        self.assertIn('sample->valid = 1;',code)

    def test_native_packages_keep_shared_baseline_fixture(self):
        result=self.run_generator()
        self.assertEqual(result.returncode,0,result.stderr)
        metadata=self.read_variants(native_package=True)
        self.assertEqual(metadata['program_stem'],'frontend_ckks_hadd_l4_n1024')
        self.assertEqual(metadata['Q'],[134072321,134111233,134176769,134203393])
        self.assertEqual(metadata['P'],[134215681])
        self.assertEqual(metadata['input_scale'],2**30)
        self.assertEqual(metadata['node_operations'],['add'])
        # 生成器不得覆盖此前已验证的包。
        second=self.run_generator()
        self.assertNotEqual(second.returncode,0)
        self.assertIn('refusing to overwrite',second.stderr)
        self.assertFalse((self.directory/'GENERATION_ERROR.json').exists())

    def test_bgv_l4_has_four_actual_q_limbs_and_new_golden(self):
        result=self.run_generator(scheme='bgv')
        self.assertEqual(result.returncode,0,result.stderr)
        metadata=self.read_variants(native_package=True)
        self.assertEqual(metadata['program_stem'],'frontend_bgv_hadd_l4_n1024')
        self.assertEqual(metadata['level'],4)
        self.assertEqual(metadata['input_Q_rns_count'],4)
        self.assertEqual(metadata['output_Q_rns_count'],4)
        self.assertEqual(metadata['Q'][:3],[2013265921,1811939329,469762049])
        self.assertEqual(len(set(metadata['Q'])),4)
        self.assertEqual(metadata['Q'][3].bit_length(),31)
        self.assertEqual(metadata['Q'][3]%(2*metadata['N']),1)
        self.assertNotIn(metadata['Q'][3],metadata['P'])
        self.assertEqual(metadata['P'],[1224736769])
        self.assertEqual(metadata['plain_modulus'],65537)
        self.assertEqual(metadata['input_correction_factor'],1)
        self.assertEqual(metadata['right_correction_factor'],1)
        self.assertEqual(metadata['node_count'],1)
        self.assertIs(metadata['same_fixture_recipe'],False)
        self.assertIs(metadata['baseline_parameters_equal'],False)
        self.assertIn('previous level-3',metadata['parameter_change'])

    def test_removed_degrees_are_rejected_before_generation(self):
        for degree in (2048,4096):
            with self.subTest(degree=degree):
                result=self.run_generator(degree=degree)
                self.assertEqual(result.returncode,1)
                self.assertIn('N1024/N8192',result.stderr)
                self.assertFalse(self.directory.exists())

    def test_legacy_contract_probe_never_exports_unverified_success(self):
        result=self.run_generator(operation='modswitch',extra=('--verify-only','--ntt-contract=legacy-raw-stage'))
        if result.returncode==0:
            metadata=self.read_variants(native_package=False)
            self.assertEqual(metadata['ntt_contract'],'legacy_raw_stage')
        else:
            self.assertEqual(result.returncode,1,result.stderr)
            failure=json.loads((self.directory/'GENERATION_ERROR.json').read_text())
            self.assertEqual(failure['status'],'FAIL')
            self.assertTrue(failure['stage'].startswith('compile.'))
            self.assertIs(failure['require_instruction_verification'],True)
            self.assertEqual(failure['ntt_contract'],'legacy_raw_stage')
            self.assertEqual(failure['native_packages_written'],0)
            self.assertTrue(failure['error'])
            self.assertFalse((self.directory/'optimized').exists())
            self.assertFalse((self.directory/'noopt').exists())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generator',type=Path,required=True)
    parser.add_argument('--validator',type=Path)
    parser.add_argument('--scratch',type=Path,required=True,help='任务专用磁盘缓存目录，不使用/tmp')
    ARGS,remaining=parser.parse_known_args()
    ARGS.scratch.mkdir(parents=True,exist_ok=True)
    unittest.main(argv=[__file__,*remaining])
