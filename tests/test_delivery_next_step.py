"""TD-007: synthetic transfer to a multi-service, minimal-interruption delivery.

Real SQLite workbench and a separate Python process; no external services,
secrets, actual website, elapsed-time claim, model invocation, or deployment.
This tests a NEW read-only selector over the existing task pool, not the
already verified revision/session algorithms in isolation.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src import delivery_next_step as selector
from src import team_workbench as wb
from src import workbench_tasks as tasks


class DeliveryNextStepTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.p = wb.initialize(Path(temp.name) / 'synthetic-delivery', 'TD007 synthetic services')
        tasks.setup(self.p)

    def add(self, name, order, deps=None, gates=None):
        tasks.add(self.p, name, name, order, deps or [], gates or [], ['accepted'])

    def complete(self, task, session='automation-1', result='PASS'):
        status = {r['id']:r for r in tasks.review(self.p)['tasks']}[task]
        tasks.start(self.p, task, session, expected_revision=status['revision'])
        return tasks.finish(self.p, task, session, {'accepted':result},
                            'synthetic independent fixture evidence', expected_revision=status['revision'])

    def step(self):
        return selector.choose(tasks.review(self.p))

    def test_no_premature_question_and_fresh_session_resume(self):
        # All services are synthetic, and the only human approvals are
        # the line-connection gate and the later launch gate.
        tasks.question(self.p, 'D_LINE', 'Authorize synthetic LINE integration?')
        tasks.question(self.p, 'D_LAUNCH', 'Approve formal launch?')
        self.add('spec', 0)
        self.add('website', 1, ['spec'])
        self.add('sheets', 2, ['spec'])
        self.add('gas', 3, ['sheets'])
        self.add('line', 4, ['website','gas'], ['D_LINE'])
        self.add('qa', 5, ['line'])
        self.add('launch', 6, ['qa'], ['D_LAUNCH'])

        result=self.step()
        self.assertEqual(result['status'],'AUTONOMOUS_CONTINUE_WITHIN_EXISTING_SCOPE')
        self.assertEqual(result['ready_task_ids'],['spec'])
        self.assertEqual(result['ask_decision_ids'],[])
        for name in ('spec','website','sheets','gas'):
            self.assertIn(name,self.step()['ready_task_ids'])
            self.complete(name)
        stage=self.step()
        self.assertEqual(stage['status'],'NEEDS_CURRENT_HUMAN_DECISION')
        self.assertEqual(stage['blocked_task_id'],'line')
        self.assertEqual(stage['ask_decision_ids'],['D_LINE'])
        self.assertNotIn('D_LAUNCH',stage['ask_decision_ids'])
        with self.assertRaises(ValueError):
            tasks.start(self.p,'line','unauthorized')
        before=(self.p/'workbench.sqlite3').read_bytes()
        out=subprocess.run([sys.executable,'-m','src.delivery_next_step','--workspace',str(self.p)],
                           capture_output=True,text=True,check=True)
        from_new_process=json.loads(out.stdout)
        self.assertEqual(from_new_process,stage)
        self.assertEqual((self.p/'workbench.sqlite3').read_bytes(),before)
        with self.assertRaises(ValueError):
            tasks.resolve_decision(self.p,'D_LINE','allow','test source',False)
        tasks.resolve_decision(self.p,'D_LINE','allow','synthetic explicit approval',True)
        self.assertEqual(self.step()['ready_task_ids'],['line'])

        self.complete('line','automation-1','FAIL')
        self.assertEqual(self.step()['ready_task_ids'],['line'])
        self.assertEqual(self.step()['ask_decision_ids'],[])
        self.complete('line','automation-2')
        self.complete('qa')
        gate=self.step()
        self.assertEqual(gate['status'],'NEEDS_CURRENT_HUMAN_DECISION')
        self.assertEqual(gate['ask_decision_ids'],['D_LAUNCH'])
        self.assertFalse(gate['authorization_granted'])
        tasks.resolve_decision(self.p,'D_LAUNCH','approved in fixture',
                               'synthetic approval event only',True)
        self.complete('launch')
        done=self.step()
        self.assertEqual(done['status'],'TASK_POOL_DONE_REQUIRES_INDEPENDENT_REVIEW')
        self.assertFalse(done['deployment_verified'])
        self.assertFalse(done['independent_acceptance_verified'])
        self.assertEqual(tasks.review(self.p)['completed'],7)
        self.assertEqual(tasks.review(self.p)['failed_attempts'],1)

    def test_running_worker_never_restarted_and_unrelated_work_remains_ready(self):
        self.add('existing-worker',0)
        self.add('independent',1)
        tasks.start(self.p,'existing-worker','owner-1',expected_revision=1)
        next_step=self.step()
        self.assertEqual(next_step['status'],'AUTONOMOUS_CONTINUE_WITHIN_EXISTING_SCOPE')
        self.assertEqual(next_step['ready_task_ids'],['independent'])
        self.assertEqual(next_step['protected_inflight_task_ids'],['existing-worker'])
        self.complete('independent')
        blocked=self.step()
        self.assertEqual(blocked['status'],'READ_ONLY_RECONCILE')
        self.assertEqual(blocked['ask_decision_ids'],[])
        self.assertFalse(blocked['authorization_granted'])

    def test_absent_and_invalid_review_fail_closed_without_creating_tasks(self):
        self.assertEqual(self.step()['status'],'NEEDS_EXISTING_PROJECT_SCOPE')
        for malformed in (None, {}, {'tasks':[]}, {'tasks':[],'open_decisions':[{}]},
                          {'tasks':[{'id':'x'}],'open_decisions':[]}):
            with self.subTest(malformed=malformed):
                with self.assertRaises(ValueError):
                    selector.choose(malformed)
        self.assertEqual(tasks.review(self.p)['tasks'], [])


if __name__ == '__main__':
    unittest.main()
