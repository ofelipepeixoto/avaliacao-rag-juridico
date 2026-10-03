import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

from avaliar import carregar, recuperar

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('radar_promptfoo_verify', ROOT/'promptfoo/verify.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


def fixture_report():
    rows = []
    for split in ('desenvolvimento', 'reserva'):
        for case in carregar(split+'.json'):
            for mode in ('literal', 'equivalencias'):
                actual = recuperar(case['pergunta'], mode == 'equivalencias') or 'SEM_TRECHO'
                expected = case['esperado'] or 'SEM_TRECHO'
                rows.append({'provider': {'label': mode},
                             'testCase': {'vars': {'question': case['pergunta']},
                                          'metadata': {'split': split},
                                          'assert': [{'type': 'equals', 'value': expected}]},
                             'response': {'output': actual}, 'success': actual == expected,
                             'failureReason': 0 if actual == expected else 1})
    return {'results': {'results': rows}}


class OfflineIntegrationTests(unittest.TestCase):
    def test_quality_failures_remain_visible(self):
        summary = verifier.verify_report(fixture_report())
        self.assertEqual(sum(x['falhou'] for x in summary.values()), 8)

    def test_duplicate_rows_cannot_replace_missing_case(self):
        report = fixture_report()
        report['results']['results'][-1] = copy.deepcopy(report['results']['results'][0])
        with self.assertRaises(AssertionError):
            verifier.verify_report(report)

    def test_modified_expectation_and_provider_failure_rejected(self):
        for key, value in (('failureReason', 2), ('success', False)):
            report = fixture_report()
            report['results']['results'][0][key] = value
            with self.assertRaises(AssertionError):
                verifier.verify_report(report)
        report = fixture_report()
        report['results']['results'][0]['testCase']['assert'][0]['value'] = 'falso'
        with self.assertRaises(AssertionError):
            verifier.verify_report(report)

    @unittest.skipUnless(sys.platform.startswith('linux'), 'seccomp só existe no Linux')
    def test_network_guard_denial_is_inherited_by_python_and_node(self):
        code = """
import errno, socket, subprocess
from promptfoo.run_seccomp import deny_network
deny_network()
for family in (socket.AF_INET, socket.AF_INET6):
    try: socket.socket(family)
    except OSError as error: assert error.errno == errno.EPERM
    else: raise AssertionError('socket permitido')
a,b=socket.socketpair()
b.close()
with a as local:
    try: local.connect('/tmp/radar-offline-nonexistent')
    except OSError as error: assert error.errno == errno.EPERM
    else: raise AssertionError('connect Unix permitido')
subprocess.run(['node', '-e', "const net=require('node:net'); const s=net.createServer(); s.on('error',e=>{if(e.code!=='EPERM')process.exit(2)}); s.listen(0,'127.0.0.1',()=>process.exit(3));"], check=True, timeout=10)
"""
        subprocess.run([sys.executable, '-c', code], cwd=ROOT, check=True, timeout=20)

    def test_network_guard_preflight_refuses_faked_marker(self):
        result = subprocess.run([sys.executable, str(ROOT/'promptfoo/network_check.py')],
                                env={'RADAR_OFFLINE_GUARD': 'linux_seccomp_socket_denial'},
                                text=True, capture_output=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('criação de socket permitida', result.stderr)


if __name__ == '__main__':
    unittest.main()
