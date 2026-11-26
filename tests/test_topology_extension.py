"""Real SQLite topology extension, negative paths and recovery (synthetic)."""
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from src import team_workbench as w, workbench_tasks as t


class TopologyExtensionTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.p=w.initialize(Path(tmp.name)/'work','synthetic topology')
        t.setup(self.p)
        self.mapping={'root':'requirements','spec':'specification','arch':'architecture',
                      'plan':'plan','impl':'implementation','qa':'qa','security':'security-review',
                      'deploy':'deployment-plan','audit':None}
        deps={'root':[],'spec':['root'],'arch':['spec'],'plan':['arch'],
              'impl':['plan'],'qa':['impl'],'security':['arch'],'deploy':['qa','security'],'audit':[]}
        for k,parents in deps.items():
            t.add(self.p,k,k,0,parents,[],['check'])
        self.root=w.handoff(self.p,'project-intake','R1','synthetic')['artifact_id']
        t.bind_artifacts(self.p,self.mapping,{k:1 for k in self.mapping},self.root,'bind','synthetic',True)
        for k in ('root','spec','arch','plan','impl','qa','security','deploy','audit'):
            self.complete(k)

    def review(self):
        return t.review(self.p)

    def row(self,k):
        return next(r for r in self.review()['tasks'] if r['id']==k)

    def complete(self,k):
        r=self.row(k)
        rev,kind=r['revision'],r['artifact_kind']
        session=k+'-'+str(rev)
        t.start(self.p,k,session,rev)
        payload=None
        if kind:
            heads=self.review()['artifact_heads']
            skill=next(s for s in w.catalog().values() if s['produces']==kind)
            payload={'expected_artifact_id':heads.get(kind),'inputs':{x:heads[x] for x in skill['requires']}}
            if kind!='requirements':
                payload.update(content='synthetic '+k,source_ref='fixture')
        return t.finish(self.p,k,session,{'check':'PASS'},'fixture',rev,artifact=payload)

    def new(self,k='review',kind=None,deps=None):
        return {'task':k,'title':k,'priority':0,'deps':['impl'] if deps is None else deps,
                'gates':[],'checks':['check'],'artifact_kind':kind}

    def args(self,**kw):
        review=self.review()
        data=dict(additions=[self.new()],attach={'qa':['review']},
                  expected_revisions={r['id']:r['revision'] for r in review['tasks']},
                  expected_artifact_heads=review['artifact_heads'],session='extend-1',
                  evidence='reviewed additive topology',confirmed=True)
        data.update(kw)
        return data

    def test_add_gate_before_done_and_propagate(self):
        before=self.review()
        out=t.extend_topology(self.p,**self.args())
        self.assertEqual(out['invalidated'],['deploy','qa'])
        self.assertEqual(self.row('qa')['revision'],3)
        self.assertEqual(self.row('deploy')['revision'],3)
        self.assertEqual(self.row('impl')['state'],'DONE')
        self.assertEqual(self.row('audit')['state'],'DONE')
        self.assertEqual(self.review()['attempts'],before['attempts'])
        self.assertEqual(self.review()['next_ready'],['review'])
        current=w.context(self.p,'deployment')['artifacts']
        self.assertFalse(current['qa']['current'])
        self.assertFalse(current['deployment-plan']['current'])
        self.assertTrue(current['implementation']['current'])
        with self.assertRaises(ValueError): t.start(self.p,'qa','old',2)
        self.complete('review'); self.complete('qa'); self.complete('deploy')
        self.assertEqual(self.review()['completed'],10)

    def test_add_artifact_producer_and_reverse_order_batch(self):
        # New producer and new downstream task may be listed out of order.
        out=t.extend_topology(self.p,**self.args(additions=[
            self.new('after',None,['repair']),self.new('repair','repair',['impl'])],attach={}))
        self.assertEqual(out['invalidated'],[])
        self.assertEqual(self.review()['completed'],9)
        with self.assertRaises(ValueError): w.handoff(self.p,'debug-and-repair','bypass','fixture')
        self.complete('repair'); self.complete('after')
        self.assertTrue(w.context(self.p,'resume-project')['artifacts']['repair']['current'])
        t.revise(self.p,'impl',2,'impl-change','fixture',True)
        self.assertEqual(self.row('repair')['revision'],2)
        self.assertEqual(self.row('after')['state'],'PENDING')

    def test_reject_bad_graph_bindings_gates_confirmation_and_cas(self):
        before=self.review()
        cases=[{'confirmed':'true'},{'expected_revisions':{}},
               {'expected_artifact_heads':{}},{'additions':[self.new('root')]},
               {'additions':[self.new('review','qa')]},
               {'additions':[self.new('review','no-such-kind')]},
               {'additions':[self.new('review',deps=['deploy'])]},
               {'additions':[self.new('review',deps=['missing'])]},
               {'attach':{'root':['review']}},{'attach':{'qa':['impl']}},
               {'additions':[{**self.new(),'gates':['MISSING']}]},
               {'additions':[self.new(),self.new()]}]
        for case in cases:
            with self.subTest(case=case):
                with self.assertRaises(ValueError): t.extend_topology(self.p,**self.args(**case))
                self.assertEqual(self.review(),before)
        with self.assertRaises(ValueError): t.add(self.p,'bypass','bypass',0,[],[],['check'])

    def test_active_worker_blocks_affected_not_unrelated(self):
        t.revise(self.p,'qa',2,'qa-change','fixture',True)
        t.start(self.p,'qa','qa-active',3)
        before=self.review()
        with self.assertRaises(ValueError): t.extend_topology(self.p,**self.args())
        self.assertEqual(self.review(),before)
        t.extend_topology(self.p,**self.args(attach={},additions=[self.new('independent',deps=[])]))
        self.assertEqual(self.row('qa')['session'],'qa-active')
        self.complete('independent')

    def test_atomic_rollback_on_event_failure(self):
        args=self.args()
        before=self.review()
        with closing(w.connect(self.p)) as db, db:
            db.execute("""CREATE TRIGGER fail_extension BEFORE INSERT ON task_events
              WHEN NEW.kind='EXTEND' BEGIN SELECT RAISE(ABORT,'fixture'); END""")
        with self.assertRaises(sqlite3.IntegrityError): t.extend_topology(self.p,**args)
        self.assertEqual(self.review(),before)
        self.assertEqual(t.extension_status(self.p,'extend-1')['status'],'NOT_OBSERVED')

    def test_concurrent_snapshot_and_replay(self):
        args=self.args()
        def go(i):
            try:
                t.extend_topology(self.p,**{**args,'session':'race-'+str(i)})
                return True
            except ValueError: return False
        with ThreadPoolExecutor(max_workers=4) as pool:
            self.assertEqual(sum(pool.map(go,range(4))),1)
        receipts=[t.extension_status(self.p,'race-'+str(i)) for i in range(4)]
        receipt=next(r for r in receipts if r['status']=='COMMITTED')
        self.assertTrue(receipt['revision_scope_current'])
        with self.assertRaises(ValueError): t.extend_topology(self.p,**args)
        t.revise(self.p,'qa',3,'new-qa','fixture',True)
        self.assertFalse(t.extension_status(self.p,receipt['session'])['revision_scope_current'])

    def test_real_process_cut_before_commit_and_lost_ack(self):
        args=self.args()
        data=self.p.parent/'extension.json'
        data.write_text(json.dumps(args),encoding='utf-8')
        prefix=("import json,os,sys; from src import workbench_tasks as t; "
                "p=sys.argv[1]; args=json.load(open(sys.argv[2])); ")
        script=prefix+"""
original=t._event
def cut(*a,**k):
    original(*a,**k)
    if a[3]=='EXTEND':
        os._exit(23)
t._event=cut
t.extend_topology(p,**args)
"""
        before=self.review()
        child=subprocess.run([sys.executable,'-c',script,str(self.p),str(data)],capture_output=True,timeout=20)
        self.assertEqual(child.returncode,23,child.stderr)
        self.assertEqual(self.review(),before)
        self.assertEqual(t.extension_status(self.p,'extend-1')['status'],'NOT_OBSERVED')
        child=subprocess.run([sys.executable,'-c',prefix+"t.extend_topology(p,**args); os._exit(23)",str(self.p),str(data)],capture_output=True,timeout=20)
        self.assertEqual(child.returncode,23,child.stderr)
        raw=(self.p/'workbench.sqlite3').read_bytes()
        result=t.extension_status(self.p,'extend-1')
        self.assertEqual(result['status'],'COMMITTED')
        self.assertEqual(result['invalidated'],['deploy','qa'])
        self.assertEqual((self.p/'workbench.sqlite3').read_bytes(),raw)
        with closing(w.connect(self.p)) as db:
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
