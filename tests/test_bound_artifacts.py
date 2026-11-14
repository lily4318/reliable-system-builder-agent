"""Synthetic cross-stage binding regression."""
import sqlite3
import tempfile
import unittest
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from src import team_workbench as w, workbench_tasks as t


class BoundArtifactsTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.p=w.initialize(Path(tmp.name)/'work','synthetic')
        t.setup(self.p)
        self.mapping={'intake':'requirements','spec':'specification','arch':'architecture',
                      'plan':'plan','impl':'implementation','qa':'qa',
                      'security':'security-review','deploy':'deployment-plan','audit':None}
        deps={'intake':[],'spec':['intake'],'arch':['spec'],'plan':['arch'],
              'impl':['plan'],'qa':['impl'],'security':['arch'],'deploy':['qa','security'],'audit':[]}
        for task,parents in deps.items():
            t.add(self.p,task,task,0,parents,[],['check'])
        self.old=w.handoff(self.p,'project-intake','R1','synthetic')['artifact_id']
        t.start(self.p,'audit','a1',1)
        t.finish(self.p,'audit','a1',{'check':'PASS'},'independent',1)

    def state(self,task):
        return next(r for r in t.review(self.p)['tasks'] if r['id']==task)

    def bind(self,**kw):
        args=dict(bindings=self.mapping,expected_revisions={k:1 for k in self.mapping},
                  expected_requirement_id=self.old,session='bind',evidence='reviewed',confirmed=True)
        args.update(kw)
        return t.bind_artifacts(self.p,**args)

    def latest(self):
        return w.context(self.p,'resume-project')['artifacts']

    def payload(self,task):
        kind=self.mapping[task]
        skills={s['produces']:s for s in w.catalog().values()}
        latest=self.latest()
        a={'expected_artifact_id':latest[kind]['id'] if kind in latest else None,
           'inputs':{k:latest[k]['id'] for k in skills[kind]['requires']}}
        if task!='intake':
            a.update(content='synthetic '+task,source_ref='source '+task)
        return a

    def start(self,task):
        rev=self.state(task)['revision']
        session=task+'-'+str(rev)
        t.start(self.p,task,session,rev)
        return rev,session

    def finish(self,task,rev,session,artifact):
        return t.finish(self.p,task,session,{'check':'PASS'},'synthetic',rev,artifact=artifact)

    def complete(self,task):
        rev,session=self.start(task)
        return self.finish(task,rev,session,self.payload(task))

    def revise(self):
        return t.revise(self.p,'intake',2,'change','R2',True,
            requirement={'expected_artifact_id':self.old,'content':'R2','source_ref':'source'})

    def all_stages(self):
        for task in ('intake','spec','arch','plan','impl','qa','security','deploy'):
            self.complete(task)

    def test_legacy_requirement_bypass_rejected(self):
        with self.assertRaises(ValueError):
            w.handoff(self.p,'project-intake','R2','bypass')
        self.assertEqual(self.latest()['requirements']['id'],self.old)

    def test_binding_cas_graph_and_guards(self):
        before=t.review(self.p)
        for kw in ({'expected_requirement_id':self.old+1},{'expected_revisions':{}},
                   {'confirmed':False},{'bindings':{**self.mapping,'arch':None}}):
            with self.assertRaises(ValueError): self.bind(**kw)
            self.assertEqual(t.review(self.p),before)
        self.bind()
        self.assertEqual(self.state('audit')['state'],'DONE')
        self.assertFalse(self.latest()['requirements']['current'])
        with self.assertRaises(ValueError):
            t.revise(self.p,'intake',2,'bypass','split',True)
        with self.assertRaises(ValueError):
            t.revise(self.p,'spec',2,'bad-graph','split',True,deps=[])

    def test_cross_stage_invalidation_and_revalidation(self):
        self.bind(); self.all_stages()
        stale=self.payload('qa')
        self.assertEqual(t.review(self.p)['completed'],9)
        self.assertEqual(set(self.revise()['affected']),set(self.mapping)-{'audit'})
        self.assertEqual(t.review(self.p)['completed'],1)
        self.assertTrue(t.revision_status(self.p,'change')['still_current'])
        self.assertTrue(all(not v['current'] for v in self.latest().values()))
        with self.assertRaises(ValueError):
            w.handoff(self.p,'requirements-spec','bypass','old')
        for task in ('intake','spec','arch','plan','impl'):
            self.complete(task)
        rev,session=self.start('qa')
        with self.assertRaises(ValueError): self.finish('qa',rev,session,stale)
        with self.assertRaises(ValueError): self.finish('qa',rev,session,None)
        self.finish('qa',rev,session,self.payload('qa'))
        self.complete('security'); self.complete('deploy')
        self.assertEqual(t.review(self.p)['completed'],9)
        self.assertTrue(all(v['current'] for v in self.latest().values()))

    def test_nonroot_revision_propagates(self):
        self.bind(); self.all_stages()
        t.revise(self.p,'arch',2,'arch-change','reviewed',True)
        current=self.latest()
        self.assertTrue(current['requirements']['current'])
        self.assertTrue(current['specification']['current'])
        self.assertTrue(all(not current[k]['current'] for k in ('architecture','plan','implementation','qa','security-review','deployment-plan')))

    def test_event_failure_rollback(self):
        self.bind(); self.complete('intake')
        rev,session=self.start('spec')
        before=t.review(self.p)
        with closing(w.connect(self.p)) as db, db:
            db.execute("""CREATE TRIGGER fail_pass BEFORE INSERT ON task_events
                WHEN NEW.kind='PASS' BEGIN SELECT RAISE(ABORT,'fixture'); END""")
        with self.assertRaises(sqlite3.IntegrityError):
            self.finish('spec',rev,session,self.payload('spec'))
        self.assertEqual(t.review(self.p),before)
        self.assertNotIn('specification',self.latest())

    def test_inflight_stale_worker(self):
        self.bind(); self.complete('intake'); self.complete('spec')
        rev,session=self.start('arch')
        payload=self.payload('arch')
        self.revise()
        self.assertEqual(self.state('arch')['state'],'RECOVERY_REQUIRED')
        with self.assertRaises(ValueError): self.finish('arch',rev,session,payload)
        self.assertNotIn('intake',t.review(self.p)['next_ready'])
        t.recover(self.p,'arch',3,session,'reviewer','stopped',True)
        self.complete('intake')

    def test_competing_finishes_and_cas(self):
        self.bind(); self.complete('intake')
        rev,session=self.start('spec')
        a=self.payload('spec')
        with self.assertRaises(ValueError):
            self.finish('spec',rev,session,{**a,'expected_artifact_id':999})
        def go(_):
            try: self.finish('spec',rev,session,a); return True
            except ValueError: return False
        with ThreadPoolExecutor(max_workers=4) as pool:
            self.assertEqual(sum(pool.map(go,range(4))),1)
        with closing(w.connect(self.p)) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM artifacts WHERE kind='specification'").fetchone()[0],1)
