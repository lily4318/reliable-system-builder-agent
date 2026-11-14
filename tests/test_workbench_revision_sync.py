"""Synthetic fault injection for coordinated requirement revisions."""
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from src import team_workbench as wb, workbench_tasks as tasks
from src import workbench_learning as learn


class RevisionSyncTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.w=wb.initialize(Path(tmp.name)/'work','Synthetic revision synchronization')
        tasks.setup(self.w)
        learn.setup(self.w)
        for i,(task,deps) in enumerate([('intake',[]),('spec',['intake']),('arch',['spec']),('audit',[])]):
            tasks.add(self.w,task,task,i,deps,[],['check'])
        self.old=wb.handoff(self.w,'project-intake','R1','synthetic R1')['artifact_id']
        wb.handoff(self.w,'requirements-spec','Spec R1','synthetic R1')
        wb.handoff(self.w,'architecture-design','Arch R1','synthetic R1')
        for task in ('intake','spec','arch','audit'):
            tasks.start(self.w,task,task+'-1',expected_revision=1)
            tasks.finish(self.w,task,task+'-1',{'check':'PASS'},'synthetic acceptance',expected_revision=1)

    def state(self):
        return tasks.review(self.w)

    def artifact(self):
        return wb.context(self.w,'architecture-design')['artifacts']

    def change(self, session='change-2', **kw):
        req={'expected_artifact_id':self.old,'content':'R2','source_ref':'synthetic R2'}
        req.update(kw)
        return tasks.revise(self.w,'intake',1,session,'synthetic confirmed R2',
                            confirmed=True,requirement=req)

    def child(self, body):
        prefix='import os,sys; from src import workbench_tasks as t,team_workbench as w; p=sys.argv[1]; '
        return subprocess.run([sys.executable,'-c',prefix+body,str(self.w)],
                              capture_output=True,text=True,timeout=20)

    def test_legacy_task_first_interruption_reproduced(self):
        # Reproduce the previous documented two-call workflow, then lose process.
        child=self.child("t.revise(p,'intake',1,'legacy-change','synthetic R2',confirmed=True); os._exit(23)")
        self.assertEqual(child.returncode,23,child.stderr)
        self.assertEqual(self.state()['completed'],1)
        self.assertTrue(self.artifact()['specification']['current'])
        self.assertEqual(self.artifact()['requirements']['id'],self.old)
        # The stale artifact can still be used by the old separate API.
        self.assertEqual(wb.context(self.w,'architecture-design')['status'],'READY_TO_REVIEW_INPUTS')
        wb.handoff(self.w,'architecture-design','incorrect stale rebuild','legacy split')
        print('REVISION-SPLIT-RED: task-first interruption leaves stale artifacts usable',flush=True)

    def test_legacy_artifact_first_interruption_reproduced(self):
        child=self.child("w.handoff(p,'project-intake','R2','synthetic R2'); os._exit(23)")
        self.assertEqual(child.returncode,23,child.stderr)
        self.assertFalse(self.artifact()['specification']['current'])
        self.assertEqual(self.state()['completed'],4)
        print('REVISION-SPLIT-RED: artifact-first interruption leaves old task PASS current',flush=True)

    def test_reconcile_preexisting_task_first_split(self):
        tasks.revise(self.w,'intake',1,'legacy-partial','synthetic R2',confirmed=True)
        review=self.state()
        root=next(row for row in review['tasks'] if row['id']=='intake')
        old=self.artifact()['requirements']
        self.assertEqual(root['revision'],2)
        self.assertEqual(old['content'],'R1')
        # Fixture independently provides the authoritative R2; do not infer it
        # from the incremented task revision or the stale artifact.
        result=tasks.revise(self.w,'intake',root['revision'],'reconcile-3',
            'Reviewed both indexes; synthetic R2 source independently confirmed',confirmed=True,
            requirement={'expected_artifact_id':old['id'],'content':'R2','source_ref':'synthetic R2'})
        self.assertEqual(result['revision'],3)
        self.assertEqual(self.artifact()['requirements']['content'],'R2')
        self.assertFalse(self.artifact()['architecture']['current'])
        self.assertEqual(self.state()['completed'],1)
        self.assertEqual(tasks.revision_status(self.w,'reconcile-3')['status'],'COMMITTED')

    def test_reconcile_preexisting_artifact_first_split(self):
        wb.handoff(self.w,'project-intake','R2','synthetic R2')
        self.assertEqual(self.state()['completed'],4)
        root=next(row for row in self.state()['tasks'] if row['id']=='intake')
        current=self.artifact()['requirements']
        result=tasks.revise(self.w,'intake',root['revision'],'reconcile-2',
            'Reviewed both indexes; independently confirmed synthetic R2',confirmed=True,
            requirement={'expected_artifact_id':current['id'],'content':'R2','source_ref':'synthetic R2'})
        self.assertEqual(result['revision'],2)
        self.assertEqual(self.state()['completed'],1)
        self.assertFalse(self.artifact()['architecture']['current'])
        self.assertEqual(self.artifact()['requirements']['content'],'R2')
        self.assertEqual(tasks.revision_status(self.w,'reconcile-2')['status'],'COMMITTED')

    def test_combined_revision_and_readonly_receipt(self):
        out=self.change()
        self.assertEqual(set(out['affected']),{'intake','spec','arch'})
        self.assertEqual(self.state()['completed'],1)
        self.assertFalse(self.artifact()['specification']['current'])
        self.assertFalse(self.artifact()['architecture']['current'])
        self.assertEqual(self.artifact()['requirements']['content'],'R2')
        self.assertEqual(self.state()['next_ready'],['intake'])
        with self.assertRaises(ValueError):
            wb.handoff(self.w,'architecture-design','old output','stale')
        before=(self.w/'workbench.sqlite3').read_bytes()
        receipt=tasks.revision_status(self.w,'change-2')
        self.assertEqual(receipt['requirement_change'],out['requirement_change'])
        self.assertEqual(receipt['status'],'COMMITTED')
        self.assertTrue(receipt['still_current'])
        self.assertEqual((self.w/'workbench.sqlite3').read_bytes(),before)
        with self.assertRaises(ValueError): self.change()
        for task,skill,content in [('intake',None,None),('spec','requirements-spec','Spec R2'),('arch','architecture-design','Arch R2')]:
            tasks.start(self.w,task,task+'-2',expected_revision=2)
            if skill: wb.handoff(self.w,skill,content,'synthetic R2')
            tasks.finish(self.w,task,task+'-2',{'check':'PASS'},'new acceptance',expected_revision=2)
        self.assertEqual(self.state()['completed'],4)
        self.assertTrue(self.artifact()['architecture']['current'])
        print('REVISION-SYNC-GREEN: combined revision, stale guard, receipt, revalidation',flush=True)

    def test_process_exit_before_commit_rolls_back_both(self):
        # Exit immediately after the real artifact INSERT, but before task events
        # and COMMIT. SQLite must roll back the transaction on process death.
        script="""\noriginal=w._handoff_in_transaction
def abrupt(*args,**kw):
    original(*args,**kw)
    os._exit(23)
w._handoff_in_transaction=abrupt
t.revise(p,'intake',1,'crash','synthetic R2',confirmed=True,requirement={'expected_artifact_id':1,'content':'R2','source_ref':'synthetic R2'})
"""
        self.assertEqual(self.old,1)
        child=self.child(script)
        self.assertEqual(child.returncode,23,child.stderr)
        self.assertEqual(self.state()['completed'],4)
        self.assertEqual(self.artifact()['requirements']['id'],self.old)
        self.assertTrue(self.artifact()['architecture']['current'])
        self.assertEqual(tasks.revision_status(self.w,'crash')['status'],'NOT_OBSERVED')
        with closing(wb.connect(self.w)) as db:
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
        self.change('reviewed-new-attempt')
        self.assertEqual(self.state()['completed'],1)

    def test_task_event_failure_rolls_back_artifact_and_revisions(self):
        with closing(wb.connect(self.w)) as db, db:
            db.execute("""CREATE TRIGGER fail_event BEFORE INSERT ON task_events
                WHEN NEW.kind='INVALIDATE' BEGIN SELECT RAISE(ABORT,'injected event failure'); END""")
        old=self.state()
        with self.assertRaises(sqlite3.IntegrityError): self.change()
        self.assertEqual(self.state(),old)
        self.assertEqual(self.artifact()['requirements']['id'],self.old)
        self.assertEqual(tasks.revision_status(self.w,'change-2')['status'],'NOT_OBSERVED')

    def test_after_commit_lost_acknowledgement(self):
        child=self.child("t.revise(p,'intake',1,'lost-ack','synthetic R2',confirmed=True,requirement={'expected_artifact_id':1,'content':'R2','source_ref':'synthetic R2'}); os._exit(23)")
        self.assertEqual(child.returncode,23,child.stderr)
        before=(self.w/'workbench.sqlite3').read_bytes()
        status=tasks.revision_status(self.w,'lost-ack')
        self.assertEqual(status['status'],'COMMITTED')
        self.assertEqual(status['revision'],2)
        self.assertEqual(self.state()['completed'],1)
        self.assertEqual((self.w/'workbench.sqlite3').read_bytes(),before)
        with self.assertRaises(ValueError): self.change('lost-ack')
        self.assertEqual(self.state()['completed'],1)

    def test_conflict_and_competition(self):
        with self.assertRaises(ValueError): self.change(expected_artifact_id=self.old+1)
        with self.assertRaises(ValueError): self.change(content='')
        self.assertEqual(self.state()['completed'],4)
        def attempt(i):
            try:
                self.change('race-'+str(i))
                return True
            except ValueError:
                return False
        with ThreadPoolExecutor(max_workers=4) as pool:
            self.assertEqual(sum(pool.map(attempt,range(4))),1)
        self.assertEqual(self.state()['completed'],1)
        self.assertEqual(sum(tasks.revision_status(self.w,'race-'+str(i))['status']=='COMMITTED' for i in range(4)),1)
        with closing(wb.connect(self.w)) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM artifacts WHERE kind='requirements'").fetchone()[0],2)
