import itertools
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from src import team_workbench as wb, workbench_learning as learn, workbench_tasks as tasks
from src.b003_shifts import assess, assess_sorted, has_overlap


class ShiftTests(unittest.TestCase):
    def test_endpoints_and_overlap(self):
        for proposed, expected in [((0,10),'CLEAR'),((20,30),'CLEAR'),((9,11),'CONFLICT'),((19,21),'CONFLICT'),((10,20),'CONFLICT'),((12,13),'CONFLICT'),((0,30),'CONFLICT')]:
            self.assertEqual(assess([(10,20)],proposed),expected)
            self.assertEqual(has_overlap([(10,20)],proposed),expected!='CLEAR')
        self.assertEqual(assess([], (0,1)), 'CLEAR')

    def test_invalid_fail_closed(self):
        for proposed in ((1,1),(2,1),(True,5),(0,1.5),('0',1),None,(1,),{}):
            self.assertEqual(assess([],proposed),'INVALID')
            self.assertTrue(has_overlap([],proposed))
        self.assertEqual(assess([(0,9),(3,3)],(1,2)),'INVALID')
        self.assertEqual(assess(None,(1,2)),'INVALID')

    def test_tech_poc_compare_to_discrete_oracle(self):
        intervals = list(itertools.combinations(range(7),2))
        for a,b,p in itertools.product(intervals,repeat=3):
            expected = 'CONFLICT' if (set(range(*a))|set(range(*b))) & set(range(*p)) else 'CLEAR'
            self.assertEqual(assess([a,b],p),expected)
            self.assertEqual(assess_sorted([a,b],p),expected)


class PoolTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)
        self.p=wb.initialize(self.root/'work','synthetic shift project')
        learn.setup(self.p)
        tasks.setup(self.p)
        tasks.question(self.p,'D1','What should invalid input display?')
        tasks.add(self.p,'spec','Document unresolved policy',0,[],[],['R3'])
        tasks.add(self.p,'core','Implement half-open interval prototype',1,['spec'],[],['R1','R2','R4'])
        tasks.add(self.p,'ui','Final user-facing error behavior',2,['core'],['D1'],['UI'])

    def test_dag_and_unresolved_gate(self):
        self.assertEqual(tasks.review(self.p)['next_ready'],['spec'])
        with self.assertRaises(ValueError): tasks.start(self.p,'core','s1')
        with self.assertRaises(ValueError): tasks.add(self.p,'cycle','cycle',0,['cycle'],[],['R'])
        with self.assertRaises(ValueError): tasks.add(self.p,'unknown','unknown',0,['missing'],[],['R'])
        tasks.start(self.p,'spec','s1')
        tasks.finish(self.p,'spec','s1',{'R3':'PASS'},'documented open D1')
        tasks.start(self.p,'core','s1')
        tasks.finish(self.p,'core','s1',{'R1':'PASS','R2':'PASS','R4':'PASS'},'test suite')
        self.assertEqual(tasks.review(self.p)['next_ready'],[])
        with self.assertRaises(ValueError): tasks.start(self.p,'ui','s1')
        with self.assertRaises(ValueError): tasks.resolve_decision(self.p,'D1','reject','fixture')
        tasks.resolve_decision(self.p,'D1','reject','synthetic explicit approval',True)
        self.assertEqual(tasks.review(self.p)['next_ready'],['ui'])
        decision=tasks.review(self.p)['decisions'][0]
        self.assertEqual((decision['answer'],decision['source']),('reject','synthetic explicit approval'))
        with self.assertRaises(ValueError): tasks.resolve_decision(self.p,'D1','different','fixture',True)

    def test_failed_acceptance_retry_and_session_guard(self):
        tasks.start(self.p,'spec','s1')
        with self.assertRaises(ValueError): tasks.finish(self.p,'spec','s2',{'R3':'PASS'},'wrong session')
        with self.assertRaises(ValueError): tasks.finish(self.p,'spec','s1',{},'missing check')
        tasks.finish(self.p,'spec','s1',{'R3':'FAIL'},'synthetic defect')
        self.assertEqual(tasks.review(self.p)['next_ready'],['spec'])
        tasks.start(self.p,'spec','s2')
        tasks.finish(self.p,'spec','s2',{'R3':'PASS'},'retested')
        r=tasks.review(self.p)
        self.assertEqual((r['attempts'],r['failed_attempts'],r['completed']),(2,1,1))
        self.assertEqual(r['next_ready'],['core'])

    def test_fresh_process_resume_and_readonly(self):
        tasks.start(self.p,'spec','s1')
        tasks.finish(self.p,'spec','s1',{'R3':'PASS'},'documented open D1')
        tasks.start(self.p,'core','s2')
        file=self.p/'workbench.sqlite3'
        before=file.read_bytes()
        out=subprocess.run([sys.executable,'-m','src.workbench_tasks','review','--workspace',str(self.p)],check=True,capture_output=True,text=True)
        r=json.loads(out.stdout)
        self.assertEqual(r['running_review'],['core'])
        self.assertEqual(r['open_decisions'][0]['id'],'D1')
        self.assertEqual(file.read_bytes(),before)
        tasks.finish(self.p,'core','s2',{'R1':'PASS','R2':'PASS','R4':'PASS'},'validated prototype')
        self.assertEqual(tasks.review(self.p)['completed'],2)

    def test_interrupted_task_explicit_resume(self):
        tasks.start(self.p,'spec','s1')
        with self.assertRaises(ValueError): tasks.resume(self.p,'spec','s1','s2','readback')
        tasks.resume(self.p,'spec','s1','s2','synthetic verified stopped owner',True)
        with self.assertRaises(ValueError): tasks.finish(self.p,'spec','s1',{'R3':'PASS'},'old owner')
        self.assertEqual(tasks.review(self.p)['running_review'],['spec'])
        tasks.finish(self.p,'spec','s2',{'R3':'PASS'},'reviewed open policy')
        self.assertEqual([x['kind'] for x in tasks.review(self.p)['history']],['START','RESUME','PASS'])

    def test_concurrent_start_only_one(self):
        def begin(i):
            try: tasks.start(self.p,'spec',f's{i}'); return True
            except ValueError: return False
        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(sum(pool.map(begin,range(8))),1)
        self.assertEqual(len(tasks.review(self.p)['history']),1)

    def test_existing_memory_and_case_use(self):
        query='SQLite 唯讀 缺庫 recovery reconcile'
        context=learn.task_context(self.p,'debug-and-repair','B003',query)
        case=next(m for m in context['memory'] if m['topic']=='B001-CASE-001')
        file=self.p/'workbench.sqlite3'
        before=file.read_bytes()
        tasks.setup(self.p)
        self.assertEqual(tasks.review(self.p)['next_ready'],['spec'])
        self.assertEqual(file.read_bytes(),before)
        learn.cite(self.p,'debug-and-repair','B003','s1',query,case['id'],'applied','read-only review preserved database bytes')
        self.assertEqual(learn.history(self.p,'B003')['uses'][0]['topic'],'B001-CASE-001')
        file.unlink()
        with self.assertRaises((ValueError,sqlite3.OperationalError)): tasks.review(self.p)
        self.assertFalse(file.exists())

    def test_workspace_isolation(self):
        other=wb.initialize(self.root/'other','other')
        tasks.setup(other)
        self.assertEqual(tasks.review(other)['tasks'],[])
        self.assertEqual(tasks.review(other)['open_decisions'],[])
