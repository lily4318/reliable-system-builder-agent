"""Offline runner contract tests. Fake transport only, never inference."""
import json
import tempfile
import unittest
from pathlib import Path
from src import p1_local_role_runner as runner

D='a'*64
MODEL='synthetic:local'


class Fixture:
    def __init__(self,fail_at=None):
        self.calls=[]
        self.fail_at=fail_at
    def __call__(self,method,path,body=None):
        if path=='/api/tags':
            return runner._json({'models':[{'name':MODEL,'digest':D,'size':1}]})
        if path=='/api/version':
            return runner._json({'version':'fixture'})
        self.calls.append(json.loads(body))
        if len(self.calls)==self.fail_at:
            raise OSError('fixture lost response')
        return runner._json({'model':MODEL,'done':True,'done_reason':'stop','message':{'role':'assistant','content':'fixture handoff %d'%len(self.calls)},'eval_count':5})


class RunnerContract(unittest.TestCase):
    def test_no_implicit_execution(self):
        f=Fixture()
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'run'
            with self.assertRaises(ValueError):
                runner.run('B001',MODEL,D,output,transport=f)
            with self.assertRaises(ValueError):
                runner.run('B001','example-cloud',D,output,confirm_offline=True,transport=f)
            with self.assertRaises(ValueError):
                runner.run('B001',MODEL,'b'*64,output,confirm_offline=True,transport=f)
            self.assertFalse(output.exists())
            self.assertEqual(f.calls,[])
            self.assertEqual(runner.probe(f)['actual_model_calls'],0)

    def test_fixed_roles_and_independent_qa_inputs(self):
        f=Fixture()
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'run'
            result=runner.run('B001',MODEL,D,output,confirm_offline=True,transport=f)
            self.assertEqual(len(f.calls),7)
            self.assertEqual(result['role_response_count'],7)
            self.assertFalse(result['autonomous_tool_execution_verified'])
            self.assertFalse(result['candidate_code_executed'])
            self.assertFalse(result['program_correctness_verified'])
            for call,record in zip(f.calls,result['records']):
                self.assertEqual([m['role'] for m in call['messages']],['system','user'])
                self.assertNotIn('tools',call)
                ctx=json.loads(call['messages'][1]['content'])
                self.assertFalse(ctx['public_task']['reference_code_included'])
                self.assertEqual(set(ctx['upstream_untrusted_handoffs']),set(record['upstream_roles']))
            qa=json.loads(f.calls[2]['messages'][1]['content'])
            self.assertEqual(set(qa['upstream_untrusted_handoffs']),{'system-lead'})
            self.assertEqual(len(list(output.glob('*.receipt.json'))),7)
            for i,record in enumerate(result['records'],1):
                stem='%02d-%s'%(i,record['role'])
                self.assertEqual(runner._sha((output/(stem+'.request.json')).read_bytes()),record['request_sha256'])
                self.assertEqual(runner._sha((output/(stem+'.response.json')).read_bytes()),record['response_sha256'])
            with self.assertRaises(ValueError):
                runner.run('B001',MODEL,D,output,confirm_offline=True,transport=f)
            self.assertEqual(len(f.calls),7)

    def test_lost_response_is_retained_without_retry(self):
        f=Fixture(fail_at=2)
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'run'
            with self.assertRaises(OSError):
                runner.run('B001',MODEL,D,output,confirm_offline=True,transport=f)
            self.assertEqual(len(f.calls),2)
            self.assertTrue((output/'01-system-lead.receipt.json').exists())
            self.assertTrue((output/'02-architect.request.json').exists())
            self.assertFalse((output/'02-architect.response.json').exists())
            self.assertFalse((output/'summary.json').exists())
            with self.assertRaises(ValueError):
                runner.run('B001',MODEL,D,output,confirm_offline=True,transport=f)
            self.assertEqual(len(f.calls),2)
