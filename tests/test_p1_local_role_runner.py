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

class SkillCaseFixture(Fixture):
    def __init__(self,wrong_skill=False,wrong_case=False):
        super().__init__()
        self.wrong_skill=wrong_skill
        self.wrong_case=wrong_case

    def __call__(self,method,path,body=None):
        if path!='/api/chat':
            return super().__call__(method,path,body)
        call=json.loads(body)
        self.calls.append(call)
        ctx=json.loads(call['messages'][1]['content'])
        if 'allowed_skills' in ctx:
            answer={'skill':'deployment' if self.wrong_skill else ctx['allowed_skills'][0]['id'],
                    'query':'SQLite snapshot revision policy report ZIP artifact generation stale worker recovery',
                    'reason':'Synthetic routing fixture, not model judgment'}
        else:
            material=ctx['selected_skill_and_retrieved_cases']
            decisions=[{'memory_id':c['id'],'decision':'not_applicable',
                        'reason':'Fixture only; not actual applicability evaluation'} for c in material['cases']]
            if self.wrong_case:
                decisions.append({'memory_id':999999,'decision':'applied','reason':'invalid fixture'})
            answer={'artifact':'Synthetic candidate only','case_decisions':decisions,
                    'limitations':'No independent review or code execution'}
        return runner._json({'model':MODEL,'done':True,'done_reason':'stop',
            'message':{'role':'assistant','content':json.dumps(answer)},'eval_count':5})


class SkillCaseContract(unittest.TestCase):
    def test_curated_vs_default_real_lookup_and_receipts(self):
        from src import workbench_learning as learn
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            observed={}
            for mode in ('default','curated'):
                f=SkillCaseFixture()
                output=root/mode
                result=runner.run('B001',MODEL,D,output,confirm_offline=True,transport=f,case_mode=mode)
                self.assertEqual(len(f.calls),14)
                self.assertEqual(result['role_response_count'],7)
                self.assertTrue(result['role_skill_case_selection_requested'])
                self.assertFalse(result['autonomous_tool_execution_verified'])
                topics=set()
                for i,record in enumerate(result['records'],1):
                    stem='%02d-%s'%(i,record['role'])
                    material=json.loads((output/(stem+'.material.json')).read_bytes())
                    candidate=json.loads((output/(stem+'.candidate.json')).read_bytes())
                    self.assertIn(material['selection']['skill'],[x['id'] for x in runner.selection.menu(record['role'])])
                    self.assertFalse(candidate['semantic_correctness_verified'])
                    self.assertFalse(candidate['authority_granted'])
                    if material['missing_prerequisites']:
                        self.assertEqual(candidate['status'],'CANDIDATE_MISSING_PREREQUISITES')
                    topics.update(c['topic'] for c in material['cases'])
                    self.assertEqual(len(candidate['case_decisions']),len(material['cases']))
                    evidence=record['skill_case_evidence']
                    for suffix,key in [('route.request','route_request_sha256'),('route.response','route_response_sha256'),('material','material_sha256'),('candidate','candidate_sha256')]:
                        self.assertEqual(runner._sha((output/(stem+'.'+suffix+'.json')).read_bytes()),evidence[key])
                history=learn.history(output/'public-case-workbench','B001')
                self.assertTrue(history['uses'])
                self.assertTrue(all(r['decision']=='not_applicable' for r in history['uses']))
                observed[mode]=topics
                qa=json.loads(f.calls[4]['messages'][1]['content'])
                self.assertEqual(set(qa['upstream_untrusted_handoffs']),{'system-lead'})
            self.assertNotIn('P22-CASE-004',observed['default'])
            self.assertIn('P22-CASE-004',observed['curated'])
            print('P12-SKILL-CASE: 14 fixture requests per arm; real case retrieval and citations; default/curated separated; no inference',flush=True)

    def test_outside_role_skill_and_unknown_case_fail_closed(self):
        for field in ('wrong_skill','wrong_case'):
            with tempfile.TemporaryDirectory() as tmp:
                f=SkillCaseFixture(**{field:True})
                output=Path(tmp)/'run'
                with self.assertRaises(ValueError):
                    runner.run('B001',MODEL,D,output,confirm_offline=True,transport=f,case_mode='curated')
                self.assertEqual(len(f.calls),1 if field=='wrong_skill' else 2)
                self.assertFalse((output/'summary.json').exists())
                self.assertFalse((output/'01-system-lead.receipt.json').exists())
