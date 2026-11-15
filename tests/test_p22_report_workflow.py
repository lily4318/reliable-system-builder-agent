"""P2-2d real report bytes, bound task generations, stale workers and recovery."""
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch
from src import p22_report_workflow as flow, p22_snapshot_report as report
from src import team_workbench as wb, workbench_tasks as tasks, workbench_learning as learn

R1={'policy_revision':1,'completed_quantities':{'paper':5,'folder':7,'pencil':0}}
R2={'policy_revision':2,'completed_quantities':{'paper':5,'folder':7,'pencil':0},
    'status_counts':{'complete':2,'pending':1,'rejected':1}}
R3={**R2,'completed_quantities':{'paper':8,'folder':7,'pencil':0}}


class ReportWorkflowTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        self.work=self.root/'work'
        self.source=self.root/'source.sqlite'
        with closing(sqlite3.connect(self.source)) as db, db:
            db.execute('CREATE TABLE metadata (revision INTEGER NOT NULL)')
            db.execute('INSERT INTO metadata VALUES (1)')
            db.execute('CREATE TABLE records (record_id TEXT, category TEXT, state TEXT, quantity INTEGER)')
            db.executemany('INSERT INTO records VALUES (?,?,?,?)',[
                ('SYN-0001','paper','complete',5),('SYN-0002','folder','complete',7),
                ('SYN-0003','folder','pending',17),('SYN-0004','paper','rejected',99)])
        self.ident=flow.initialize(self.work,self.source,1,1)['root_id']
        self.serial=0

    def state(self,name):
        return next(r for r in tasks.review(self.work)['tasks'] if r['id']==name)

    def artifacts(self):
        return wb.context(self.work,'resume-project')['artifacts']

    def start(self,name):
        self.serial+=1
        rev=self.state(name)['revision']
        session='stage-%d'%self.serial
        tasks.start(self.work,name,session,rev)
        return rev,session

    def stage(self,name,oracle=None,reconcile_existing=False):
        rev,session=self.start(name)
        return flow.complete_stage(self.work,self.source,name,session,rev,self.ident,oracle,reconcile_existing)

    def complete(self,oracle):
        for name in flow.STAGES:
            self.assertEqual(self.stage(name,oracle if name=='qa' else None)['state'],'DONE')
        self.assertEqual(flow.verify(self.work,self.source,self.ident),'COMMITTED')
        self.assertNotIn('activate',tasks.review(self.work)['next_ready'])
        self.assertTrue(all(a['current'] for a in self.artifacts().values()))

    def change(self,source_revision,policy,session):
        old=self.ident
        rev=self.state('intake')['revision']
        result=flow.revise(self.work,self.source,source_revision,policy,old,rev,session,'Synthetic confirmed change',True)
        self.ident=result['requirement_change']['artifact_id']
        self.assertEqual(set(result['affected']),set(flow.STAGES)|{'activate'})
        receipt=tasks.revision_status(self.work,session)
        self.assertEqual(receipt['status'],'COMMITTED')
        self.assertTrue(receipt['still_current'])
        self.assertTrue(all(not a['current'] for a in self.artifacts().values()))
        return old,rev

    def test_policy_then_source_change_rebuilds_actual_artifacts(self):
        rev,session=self.start('audit')
        tasks.finish(self.work,'audit',session,{'check':'PASS'},'Independent fixture audit',rev)
        self.complete(R1)
        old=self.ident
        original=flow._path(self.work,old).read_bytes()
        old_ids={k:a['id'] for k,a in self.artifacts().items()}
        self.change(1,2,'policy-r2')
        with self.assertRaises(ValueError):
            flow.verify(self.work,self.source,old)
        self.assertEqual(self.state('audit')['state'],'DONE')
        self.complete(R2)
        second=self.ident
        second_bytes=flow._path(self.work,second).read_bytes()
        self.assertNotEqual(second_bytes,original)
        self.assertEqual(flow._path(self.work,old).read_bytes(),original)
        self.assertTrue(all(a['id']!=old_ids[k] for k,a in self.artifacts().items()))
        with closing(sqlite3.connect(self.source)) as db, db:
            db.execute('UPDATE metadata SET revision=2')
            db.execute("UPDATE records SET quantity=8 WHERE record_id='SYN-0001'")
        with self.assertRaisesRegex(ValueError,'STALE_SOURCE'):
            flow.verify(self.work,self.source,second)
        self.change(2,2,'source-r2')
        self.complete(R3)
        self.assertEqual(flow._path(self.work,second).read_bytes(),second_bytes)
        self.assertEqual(flow._path(self.work,old).read_bytes(),original)
        self.assertEqual(self.state('audit')['revision'],1)
        self.assertEqual(tasks.review(self.work)['completed'],9)
        self.assertEqual(len(list(self.work.glob('report-root-*.zip'))),3)
        with closing(wb.connect(self.work)) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM artifacts WHERE kind='qa'").fetchone()[0],3)
        print('P22D-REBUILD: policy then source change; 3 exact ZIP generations; all 8 dependent stages reaccepted; independent audit retained; LIVE blocked',flush=True)

    def test_stale_worker_after_file_publication_cannot_accept(self):
        for name in ('intake','spec','arch','plan'):
            self.stage(name)
        rev,session=self.start('impl')
        old=self.ident
        publish=report._publish_bundle
        def publish_then_revise(data,path):
            result=publish(data,path)
            self.change(1,2,'during-publication')
            return result
        with patch.object(report,'_publish_bundle',publish_then_revise):
            with self.assertRaises(ValueError):
                flow.complete_stage(self.work,self.source,'impl',session,rev,old)
        orphan=flow._path(self.work,old)
        before=orphan.read_bytes()
        self.assertEqual(self.state('impl')['state'],'RECOVERY_REQUIRED')
        self.assertNotIn('intake',tasks.review(self.work)['next_ready'])
        self.assertNotIn('implementation',self.artifacts())
        self.assertFalse(flow._path(self.work,self.ident).exists())
        tasks.recover(self.work,'impl',rev+1,session,'review-old-worker',
            'Fixture call stopped; historical ZIP inspected; no remote write',True)
        self.complete(R2)
        self.assertEqual(orphan.read_bytes(),before)
        self.assertNotEqual(self.artifacts()['implementation']['content'],before.decode('latin1'))
        print('P22D-STALE: file committed before root revise; old worker PASS rejected; explicit recovery and new output accepted',flush=True)

    def test_unknown_output_requires_explicit_reconciliation_and_qa_failure(self):
        for name in ('intake','spec','arch','plan'):
            self.stage(name)
        rev,session=self.start('impl')
        path=flow._path(self.work,self.ident)
        report.publish(self.source,path,1,1)
        prior=path.read_bytes()
        with self.assertRaises(FileExistsError):
            flow.complete_stage(self.work,self.source,'impl',session,rev,self.ident)
        self.assertEqual(self.state('impl')['state'],'RUNNING')
        result=flow.complete_stage(self.work,self.source,'impl',session,rev,self.ident,reconcile_existing=True)
        self.assertEqual(result['state'],'DONE')
        self.assertEqual(path.read_bytes(),prior)
        self.assertEqual(self.stage('qa',R2)['state'],'PENDING')
        self.assertEqual(tasks.review(self.work)['failed_attempts'],1)
        self.assertNotIn('deploy-plan',tasks.review(self.work)['next_ready'])
        self.assertEqual(self.stage('qa',R1)['state'],'DONE')
        self.stage('security')
        self.stage('deploy-plan')
        self.assertNotIn('activate',tasks.review(self.work)['next_ready'])
        print('P22D-RECOVER: exact existing file reconciled only by explicit choice; wrong QA oracle retained FAIL; correct oracle PASS',flush=True)

    def test_same_revision_changed_snapshot_rejected_and_case_retrieved(self):
        self.stage('intake')
        rev,session=self.start('spec')
        with closing(sqlite3.connect(self.source)) as db, db:
            db.execute("UPDATE records SET quantity=8 WHERE record_id='SYN-0001'")
        with self.assertRaisesRegex(ValueError,'snapshot differs'):
            flow.complete_stage(self.work,self.source,'spec',session,rev,self.ident)
        before=tasks.review(self.work)
        with self.assertRaisesRegex(ValueError,'new revision'):
            flow.revise(self.work,self.source,1,2,self.ident,self.state('intake')['revision'],'wrong-change','fixture',True)
        self.assertEqual(tasks.review(self.work),before)
        with closing(sqlite3.connect(self.source)) as db, db:
            db.execute('UPDATE metadata SET revision=2')
        self.change(2,2,'new-source')
        tasks.recover(self.work,'spec',rev+1,session,'review-spec','Fixture stopped without write',True)
        self.complete(R3)
        query='SQLite snapshot revision policy report aggregate ZIP manifest logical hash'
        ctx=learn.task_context(self.work,'debug-and-repair','P22D',query,limit=10)
        hit=next(r for r in ctx['memory'] if r['topic']=='P22-CASE-003')
        learn.cite(self.work,'debug-and-repair','P22D','transfer-d',query,hit['id'],'applied',
            'Pinned snapshot hash and source/policy revisions; stale worker and exact new output tests',limit=10)
        self.assertEqual(learn.history(self.work,'P22D')['uses'][0]['topic'],'P22-CASE-003')
        print('P22D-TRANSFER: P22-CASE-003 retrieved and cited; same-revision content drift rejected',flush=True)
