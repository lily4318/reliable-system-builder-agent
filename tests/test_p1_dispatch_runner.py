"""Dispatch contracts with scripted transport; no model invocation."""
import json
import tempfile
import unittest
from pathlib import Path
from src import p1_dispatch_runner as run, p1_local_role_runner as local

MODEL='synthetic:local'
D='b'*64

class Transport:
    def __init__(self,rejections=1,bad=False,stop=False,fail=None):
        self.rejections=rejections
        self.bad=bad
        self.stop=stop
        self.fail=fail
        self.calls=[]
        self.chosen=[]
        self.impl=[]
        self.oracles=[]
        self.verdicts=0

    def __call__(self,method,path,body=None):
        if path=='/api/tags':
            return local._json({'models':[{'name':MODEL,'digest':D,'size':1}]})
        if path=='/api/version':
            return local._json({'version':'fixture'})
        payload=json.loads(body)
        ctx=json.loads(payload['messages'][1]['content'])
        self.calls.append(ctx)
        if len(self.calls)==self.fail:
            raise OSError('fixture lost reply')
        if 'ready_tasks' in ctx:
            ready=ctx['ready_tasks']
            key='security' if self.bad else 'STOP' if self.stop else 'qa-oracle' if 'qa-oracle' in ready else next(iter(ready))
            self.chosen.append(key)
            answer={'task':key,'reason':'Scripted dispatch, not model judgment'}
        elif 'allowed_skills' in ctx:
            answer={'skill':ctx['allowed_skills'][0]['id'],'query':'SQLite transaction recovery artifact generation stale worker',
                    'reason':'Scripted skill choice'}
        elif 'review_candidate' in ctx:
            self.verdicts+=1
            answer={'verdict':'REJECT' if self.verdicts<=self.rejections else 'REVIEW_READY',
                    'findings':['Missing negative decision evidence'] if self.verdicts<=self.rejections else []}
        else:
            if ctx['task']=='implementation':
                self.impl.append(ctx)
            if ctx['task']=='qa-oracle':
                self.oracles.append(ctx)
            material=ctx['selected_skill_and_retrieved_cases']
            answer={'artifact':'Candidate '+ctx['task']+' '+str(len(self.calls)),
                    'case_decisions':[{'memory_id':c['id'],'decision':'not_applicable','reason':'Fixture only'} for c in material['cases']],
                    'limitations':'No code execution or semantic verification'}
        return local._json({'model':MODEL,'done':True,'done_reason':'stop',
            'message':{'role':'assistant','content':json.dumps(answer)},'eval_count':5})


class DispatchContract(unittest.TestCase):
    def test_model_choice_and_qa_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'pilot'
            t=Transport()
            result=run.run('B001',MODEL,D,out,confirm_offline=True,transport=t)
            self.assertEqual(result['status'],'CANDIDATES_CAPTURED_INDEPENDENT_REVIEW_REQUIRED')
            self.assertEqual(t.chosen[:3],['intake','qa-oracle','architecture'])
            self.assertEqual(t.chosen.count('implementation'),2)
            self.assertEqual(t.chosen.count('qa-review'),2)
            self.assertEqual(len(t.oracles),1)
            self.assertEqual(set(t.oracles[0]['upstream_candidates']),{'intake'})
            self.assertEqual(t.impl[0]['repair_findings'],[])
            self.assertEqual(t.impl[1]['repair_findings'][0]['findings'],['Missing negative decision evidence'])
            self.assertEqual(result['repair_rounds'],1)
            self.assertEqual(result['task_capture_status']['failed_attempts'],1)
            self.assertEqual(result['current_candidate_refs']['implementation']['revision'],2)
            self.assertEqual(result['current_candidate_refs']['qa-oracle']['revision'],1)
            self.assertEqual(len(list(out.glob('*-implementation-r*.candidate.json'))),2)
            for key in ('program_correctness_verified','independent_qa_verified','candidate_code_executed','release_authorized','holdout_used'):
                self.assertFalse(result[key])
            self.assertEqual(len(t.calls),32)
            print('P12-DISPATCH: ready-choice ordering, recorded QA rejection, new implementation revision, original oracle and old candidate retained; fixture only',flush=True)

    def test_repair_budget_and_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            t=Transport(rejections=20)
            result=run.run('B001',MODEL,D,root/'reject',confirm_offline=True,transport=t)
            self.assertEqual(result['status'],'QA_REPAIR_BUDGET_EXHAUSTED')
            self.assertEqual(result['repair_rounds'],2)
            self.assertEqual(result['qa_rejections'],3)
            self.assertNotIn('security',t.chosen)
            self.assertNotIn('qa-review',result['current_candidate_refs'])
            self.assertLessEqual(result['dispatches'],run.MAX_DISPATCH)
            result=run.run('B001',MODEL,D,root/'stop',confirm_offline=True,transport=Transport(stop=True))
            self.assertEqual(result['status'],'MODEL_STOPPED_REVIEW_REQUIRED')
            self.assertEqual(result['task_capture_status']['completed'],0)

    def test_invalid_dispatch_and_lost_reply_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name,t in [('bad',Transport(bad=True)),('lost',Transport(fail=2))]:
                out=root/name
                with self.assertRaises((ValueError,OSError)):
                    run.run('B001',MODEL,D,out,confirm_offline=True,transport=t)
                self.assertFalse((out/'summary.json').exists())
                count=len(t.calls)
                self.assertEqual(count,1 if name=='bad' else 2)
                with self.assertRaises(ValueError):
                    run.run('B001',MODEL,D,out,confirm_offline=True,transport=t)
                self.assertEqual(len(t.calls),count)
