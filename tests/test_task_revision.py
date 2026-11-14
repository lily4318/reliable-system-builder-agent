import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from src import team_workbench as wb, workbench_tasks as t, workbench_learning as learn


class RevisionTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.p = wb.initialize(Path(tmp.name)/'work', 'synthetic revisions')
        learn.setup(self.p)
        t.setup(self.p)
        for name, deps in [('spec',[]),('design',['spec']),('build',['design']),('qa',['build']),('other',[])]:
            t.add(self.p, name, name, 0, deps, [], ['R'])

    def row(self, name):
        return next(r for r in t.review(self.p)['tasks'] if r['id']==name)

    def complete(self, name, session):
        rev = self.row(name)['revision']
        t.start(self.p,name,session,expected_revision=rev)
        t.finish(self.p,name,session,{'R':'PASS'},'synthetic test',expected_revision=rev)

    def change(self, name='spec', revision=1, **kw):
        return t.revise(self.p,name,revision,'reviewer','synthetic confirmed revision',confirmed=True,**kw)

    def test_legacy_session_reuse_is_rejected(self):
        t.start(self.p,'spec','old')
        t.finish(self.p,'spec','old',{'R':'FAIL'},'synthetic failure')
        with self.assertRaises(ValueError): t.start(self.p,'spec','old')

    def test_cascade_reopen_and_history(self):
        for name in ['spec','design','build','qa','other']: self.complete(name,'s1')
        self.assertEqual(set(self.change()['affected']),{'spec','design','build','qa'})
        self.assertEqual(t.review(self.p)['next_ready'],['spec'])
        for name in ['spec','design','build','qa']:
            self.assertEqual((self.row(name)['state'],self.row(name)['revision']),('PENDING',2))
        self.assertEqual((self.row('other')['state'],self.row('other')['revision']),('DONE',1))
        self.assertEqual(t.review(self.p)['completed'],1)
        self.assertEqual(t.review(self.p)['attempts'],5)
        self.complete('spec','s2')
        self.assertEqual(t.review(self.p)['next_ready'],['design'])
        self.assertEqual(t.review(self.p)['completed'],2)

    def test_inflight_invalidated_requires_recovery(self):
        self.complete('spec','s1'); self.complete('design','s1')
        t.start(self.p,'build','running')
        self.change()
        self.assertEqual(self.row('build')['state'],'RECOVERY_REQUIRED')
        self.assertIn('build',t.review(self.p)['recovery_review'])
        self.assertEqual(self.row('spec')['recovery_blockers'],['build'])
        self.assertEqual(t.review(self.p)['next_ready'],['other'])
        with self.assertRaises(ValueError): t.start(self.p,'spec','s2',expected_revision=2)
        with self.assertRaises(ValueError): t.finish(self.p,'build','running',{'R':'PASS'},'old result')
        with self.assertRaises(ValueError): t.resume(self.p,'build','running','new','old stopped',True,expected_revision=2)
        with self.assertRaises(ValueError): t.recover(self.p,'build',2,'wrong','reviewer','stopped',True)
        with self.assertRaises(ValueError): t.recover(self.p,'build',2,'running','reviewer','stopped',False)
        t.recover(self.p,'build',2,'running','reviewer','synthetic prior writer stopped',True)
        self.assertEqual(self.row('build')['state'],'PENDING')
        self.assertIn('design',self.row('build')['blocked_by'])
        self.complete('spec','s2'); self.complete('design','s2'); self.complete('build','s2')
        self.assertEqual(t.review(self.p)['next_ready'],['other','qa'])

    def test_stale_revision_and_session_aba(self):
        self.complete('spec','s1'); self.change()
        for kwargs in ({},{'expected_revision':1},{'expected_revision':True}):
            with self.assertRaises(ValueError): t.start(self.p,'spec','s2',**kwargs)
        with self.assertRaises(ValueError): t.start(self.p,'spec','s1',expected_revision=2)
        t.start(self.p,'spec','s2',expected_revision=2)
        with self.assertRaises(ValueError): t.finish(self.p,'spec','s1',{'R':'PASS'},'stale',expected_revision=2)
        with self.assertRaises(ValueError): t.finish(self.p,'spec','s2',{'R':'PASS'},'stale',expected_revision=1)
        t.finish(self.p,'spec','s2',{'R':'PASS'},'new',expected_revision=2)
        with self.assertRaises(ValueError): self.change(revision=1)

    def test_cycle_unknown_gate_and_unconfirmed_atomic_reject(self):
        self.complete('spec','s1')
        before=t.review(self.p)
        for kw in ({'deps':['qa']},{'deps':['absent']},{'gates':['missing']},{'checks':[]}):
            with self.assertRaises(ValueError): self.change(**kw)
        with self.assertRaises(ValueError): t.revise(self.p,'spec',1,'reviewer','unconfirmed')
        self.assertEqual(t.review(self.p),before)
        t.question(self.p,'D2','new policy')
        self.change(gates=['D2'],checks=['NEW'])
        self.assertNotIn('spec',t.review(self.p)['next_ready'])
        t.resolve_decision(self.p,'D2','synthetic policy','fixture',True)
        t.start(self.p,'spec','s2',expected_revision=2)
        with self.assertRaises(ValueError): t.finish(self.p,'spec','s2',{'R':'PASS'},'old checks',expected_revision=2)
        t.finish(self.p,'spec','s2',{'NEW':'PASS'},'new checks',expected_revision=2)

    def test_two_concurrent_revisions_only_one(self):
        def go(i):
            try: self.change(title='variant '+str(i)); return True
            except ValueError: return False
        with ThreadPoolExecutor(max_workers=8) as ex:
            self.assertEqual(sum(ex.map(go,range(8))),1)
        self.assertEqual(self.row('qa')['revision'],2)

    def test_finish_races_change_never_stale_done(self):
        t.start(self.p,'spec','s1')
        def finish():
            try: t.finish(self.p,'spec','s1',{'R':'PASS'},'old'); return True
            except ValueError: return False
        with ThreadPoolExecutor(max_workers=2) as ex:
            f=ex.submit(finish); c=ex.submit(self.change); c.result(); f.result()
        self.assertIn(self.row('spec')['state'],('PENDING','RECOVERY_REQUIRED'))
        self.assertEqual(self.row('spec')['revision'],2)
        self.assertNotIn('design',t.review(self.p)['next_ready'])

    def test_concurrent_resume_and_old_session_rejected(self):
        t.start(self.p,'spec','s1')
        def go(i):
            try: t.resume(self.p,'spec','s1',f's{i+2}','synthetic reviewed stop',True); return True
            except ValueError: return False
        with ThreadPoolExecutor(max_workers=8) as ex:
            self.assertEqual(sum(ex.map(go,range(8))),1)
        owner=self.row('spec')['session']
        with self.assertRaises(ValueError): t.resume(self.p,'spec',owner,'s1','stopped',True)
        with self.assertRaises(ValueError): t.finish(self.p,'spec','s1',{'R':'PASS'},'old')
        t.finish(self.p,'spec',owner,{'R':'PASS'},'current')

    def test_fresh_process_review_and_recovery(self):
        t.start(self.p,'spec','s1'); self.change()
        before=(self.p/'workbench.sqlite3').read_bytes()
        out=subprocess.run([sys.executable,'-m','src.workbench_tasks','review','--workspace',str(self.p)],check=True,capture_output=True,text=True)
        r=json.loads(out.stdout)
        self.assertEqual(r['recovery_review'],['spec'])
        self.assertEqual((self.p/'workbench.sqlite3').read_bytes(),before)
        t.recover(self.p,'spec',2,'s1','s2','reviewed stopped worker',True)
        self.complete('spec','s3')

    def test_migrate_legacy_running_without_losing_history(self):
        t.start(self.p,'spec','s1')
        with closing(wb.connect(self.p)) as db, db:
            db.execute('ALTER TABLE task_pool DROP COLUMN revision')
        t.setup(self.p)
        r=self.row('spec')
        self.assertEqual((r['state'],r['revision']),('RECOVERY_REQUIRED',2))
        self.assertEqual([e['kind'] for e in t.review(self.p)['history']],['START','MIGRATION_FENCE'])
        before=t.review(self.p); t.setup(self.p); self.assertEqual(t.review(self.p),before)
        t.recover(self.p,'spec',2,'s1','reviewer','legacy worker stopped',True)
        self.complete('spec','s2')

    def test_actual_cross_process_competing_revise(self):
        root=self.p.parent
        command=[sys.executable,'-m','src.workbench_tasks','revise','--workspace',str(self.p),'--input']
        files=[]
        for i in range(3):
            file=root/f'change-{i}.json'
            file.write_text(json.dumps({'task':'spec','expected_revision':1,'session':f's{i}','evidence':'confirmed fixture','confirmed':True,'title':f'v{i}'}))
            files.append(file)
        workers=[subprocess.Popen(command+[str(f)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for f in files]
        for worker in workers: worker.communicate(timeout=10)
        self.assertEqual(sorted(w.returncode for w in workers),[0,2,2])
        self.assertEqual(self.row('qa')['revision'],2)

    def test_repeat_revision_does_not_release_quarantined_worker(self):
        t.start(self.p,'spec','s1'); self.change(); self.change(revision=2)
        self.assertEqual((self.row('spec')['state'],self.row('spec')['revision'],self.row('spec')['session']),('RECOVERY_REQUIRED',3,'s1'))
        with self.assertRaises(ValueError): t.recover(self.p,'spec',2,'s1','s2','stopped',True)
        t.recover(self.p,'spec',3,'s1','s2','stopped',True)
        self.complete('spec','s3')
        self.assertEqual(self.row('spec')['state'],'DONE')

    def test_atomic_cascade_rollback_on_database_failure(self):
        self.complete('spec','s1'); self.complete('design','s1')
        with closing(wb.connect(self.p)) as db, db:
            db.execute("CREATE TRIGGER synthetic_fail BEFORE UPDATE OF revision ON task_pool WHEN OLD.id='qa' BEGIN SELECT RAISE(ABORT,'synthetic write failure'); END")
        before=t.review(self.p)
        with self.assertRaises(sqlite3.IntegrityError): self.change(title='new spec')
        self.assertEqual(t.review(self.p),before)
        with closing(wb.connect(self.p)) as db, db: db.execute('DROP TRIGGER synthetic_fail')
        self.change(title='new spec')
        self.assertEqual(self.row('spec')['title'],'new spec')

    def test_exited_worker_resume_and_stale_process_finish(self):
        root=self.p.parent
        def call(action,args):
            file=root/(action+'.json')
            file.write_text(json.dumps(args),encoding='utf-8')
            return subprocess.run([sys.executable,'-m','src.workbench_tasks',action,'--workspace',str(self.p),'--input',str(file)],capture_output=True,text=True,timeout=10)
        self.assertEqual(call('start',{'task':'spec','session':'exited-worker','expected_revision':1}).returncode,0)
        self.assertEqual(self.row('spec')['state'],'RUNNING')
        self.assertEqual(call('resume',{'task':'spec','previous_session':'exited-worker','session':'new-worker','evidence':'start subprocess exited and readback confirmed owner','confirmed':True,'expected_revision':1}).returncode,0)
        args={'task':'spec','session':'exited-worker','results':{'R':'PASS'},'evidence':'synthetic stale completion','expected_revision':1}
        self.assertEqual(call('finish',args).returncode,2)
        args.update(session='new-worker',evidence='synthetic current completion')
        self.assertEqual(call('finish',args).returncode,0)
        self.assertEqual(self.row('spec')['state'],'DONE')
