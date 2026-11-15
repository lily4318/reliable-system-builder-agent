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

GOOD_SOURCE = """def has_overlap(existing, proposed):
    for item in existing:
        if item[0] < proposed[1] and proposed[0] < item[1]:
            return True
    return False
"""
BAD_SOURCE = """def has_overlap(existing, proposed):
    return False
"""


# These are deliberately deficient, trusted public fixtures, never native-executed.
# All old samples have at most three intervals, so unnecessary cubic work was missed.
EXPENSIVE_SOURCE = """def has_overlap(existing, proposed):
    for a in existing:
        for b in existing:
            for c in existing:
                ignored = c
    for item in existing:
        if item[0] < proposed[1] and proposed[0] < item[1]:
            return True
    return False
"""
LOWER_BOUND_SOURCE = GOOD_SOURCE.replace(
    '    for item in existing:', '    if proposed[0] == -10080:\\n        return False\\n    for item in existing:'.replace('\\n','\n'))
UPPER_BOUND_SOURCE = GOOD_SOURCE.replace(
    '    for item in existing:', '    if proposed[1] == 10080:\\n        return False\\n    for item in existing:'.replace('\\n','\n'))

class FunctionalTransport(Transport):
    def __init__(self, first_source=BAD_SOURCE):
        super().__init__(rejections=0)
        self.first_source=first_source

    def __call__(self,method,path,body=None):
        raw=super().__call__(method,path,body)
        if path=='/api/chat':
            ctx=json.loads(json.loads(body)['messages'][1]['content'])
            if ctx.get('task')=='implementation' and 'selected_skill_and_retrieved_cases' in ctx:
                value=json.loads(raw)
                answer=json.loads(value['message']['content'])
                answer['artifact']=self.first_source if len(self.impl)==1 else GOOD_SOURCE
                value['message']['content']=json.dumps(answer)
                return local._json(value)
        return raw


class FunctionalGateContract(unittest.TestCase):
    def test_public_oracle_runs_actual_bounded_semantics(self):
        from src import p1_restricted_functional as f
        good=f.evaluate(GOOD_SOURCE)
        bad=f.evaluate(BAD_SOURCE)
        self.assertEqual(good['status'],'PUBLIC_SLICE_PASS')
        self.assertEqual(len(good['cases']),12)
        self.assertTrue(all(x['pass'] for x in good['cases']))
        self.assertEqual(bad['status'],'PUBLIC_SLICE_FAIL')
        self.assertGreater(len(bad['findings']),0)
        self.assertEqual(good['oracle_sha256'],bad['oracle_sha256'])
        self.assertNotEqual(good['source_sha256'],bad['source_sha256'])
        self.assertFalse(good['candidate_native_code_executed'])
        self.assertFalse(good['independent_human_review'])
        print('P12-FUNCTIONAL: bounded interpreter ran 12 public fixed cases; correct and incorrect sources distinguished',flush=True)

    def test_host_rejects_unsafe_syntax_invalid_data_and_excess_work(self):
        from src import p1_restricted_functional as f
        for src in ('import os\n'+GOOD_SOURCE,
                    'def has_overlap(existing, proposed):\n    if False:\n        return open("x")\n    return False\n',
                    'def has_overlap(existing, proposed):\n    return proposed.__class__\n',
                    'def has_overlap(existing, proposed):\n    while True:\n        return False\n'):
            self.assertEqual(f.evaluate(src)['status'],'BLOCKED_SYNTAX')
            self.assertFalse(f.evaluate(src)['cases'])
        fn=f._parse(GOOD_SOURCE)
        for invalid in ((True,4),(5,2),(1,1),('1',4)):
            with self.assertRaisesRegex(f.Blocked,'INVALID_INPUT_HOST_REJECTED'):
                f._interpret(fn,(),invalid)
        nested=f._parse('def has_overlap(existing, proposed):\n    for a in existing:\n        for b in existing:\n            for c in existing:\n                if c[0] < proposed[0]:\n                    return True\n    return False\n')
        with self.assertRaisesRegex(f.Blocked,'STEP_BUDGET'):
            f._interpret(nested,((10,11),)*32,(0,1))

    def test_host_failure_overrides_model_ready_and_repairs_exact_revision(self):
        from src import p1_restricted_functional as f
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'pilot'
            t=FunctionalTransport()
            result=run.run('B003',MODEL,D,out,confirm_offline=True,transport=t,functional_pilot=True)
            self.assertEqual(result['status'],'CANDIDATES_CAPTURED_INDEPENDENT_REVIEW_REQUIRED')
            self.assertEqual(result['qa_rejections'],1)
            self.assertEqual(result['repair_rounds'],1)
            self.assertEqual(t.verdicts,2)
            self.assertEqual([r['status'] for r in result['functional_runs']],['PUBLIC_SLICE_FAIL','PUBLIC_SLICE_PASS'])
            self.assertEqual([r['revision'] for r in result['functional_runs']],[1,2])
            for r in result['functional_runs']:
                evidence=(out/r['file']).read_bytes()
                self.assertEqual(local._sha(evidence),r['sha256'])
                self.assertEqual(json.loads(evidence)['oracle_sha256'],f.oracle_digest())
            self.assertTrue(any(x.startswith('Host tool: ') for x in t.impl[1]['repair_findings'][0]['findings']))
            self.assertTrue(result['public_slice_pass'])
            self.assertFalse(result['program_correctness_verified'])
            self.assertFalse(result['candidate_code_executed'])
            self.assertFalse(result['general_sandbox_verified'])
            self.assertFalse(result['release_authorized'])
            print('P12-HOST-QA: model REVIEW_READY overridden by actual bounded tool failure; revision 2 passed fixed public slice; no inference',flush=True)

    def test_public_gate_rejects_valid_maximum_workload_budget_bypass(self):
        from src import p1_restricted_functional as f
        report=f.evaluate(EXPENSIVE_SOURCE)
        # Actual restricted semantics on valid input, independent of case list.
        fn=f._parse(EXPENSIVE_SOURCE)
        existing=tuple((i*2,i*2+1) for i in range(32))
        with self.assertRaisesRegex(f.Blocked,'STEP_BUDGET'):
            f._interpret(fn,existing,(80,81))
        self.assertEqual(report['status'],'PUBLIC_SLICE_FAIL',report)
        self.assertTrue(any('STEP_BUDGET' in x for x in report['findings']))
        self.assertEqual(f.evaluate(GOOD_SOURCE)['status'],'PUBLIC_SLICE_PASS')

    def test_public_gate_covers_integer_boundary_counterexamples(self):
        from src import p1_restricted_functional as f
        for candidate,pair in ((LOWER_BOUND_SOURCE,(-10080,-10079)),
                               (UPPER_BOUND_SOURCE,(10079,10080))):
            with self.subTest(pair=pair):
                self.assertFalse(f._interpret(f._parse(candidate),(pair,),pair))
                self.assertTrue(f._interpret(f._parse(GOOD_SOURCE),(pair,),pair))
                self.assertEqual(f.evaluate(candidate)['status'],'PUBLIC_SLICE_FAIL')

    def test_host_qa_rejects_budget_bypass_even_when_model_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'pilot'
            t=FunctionalTransport(first_source=EXPENSIVE_SOURCE)
            result=run.run('B003',MODEL,D,out,confirm_offline=True,transport=t,functional_pilot=True)
            self.assertEqual(result['qa_rejections'],1)
            self.assertEqual(result['repair_rounds'],1)
            self.assertEqual([r['status'] for r in result['functional_runs']],
                             ['PUBLIC_SLICE_FAIL','PUBLIC_SLICE_PASS'])
            first=json.loads((out/result['functional_runs'][0]['file']).read_bytes())
            self.assertTrue(any('STEP_BUDGET' in x for x in first['findings']))
            self.assertTrue(any('STEP_BUDGET' in x for x in t.impl[1]['repair_findings'][0]['findings']))
            self.assertFalse(result['program_correctness_verified'])
            self.assertFalse(result['release_authorized'])
