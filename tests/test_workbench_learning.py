import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from src import team_workbench as wb
from src import workbench_learning as learn


class LearningTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.p = wb.initialize(self.root/'private','synthetic lab')
        learn.setup(self.p)
        self.query = 'SQLite 唯讀 缺庫 transaction inventory concurrency'

    def ctx(self, query=None, **kw):
        return learn.task_context(self.p,'debug-and-repair','SYN-LAB-3',query or self.query,**kw)

    def test_additive_setup_idempotent(self):
        before = self.ctx()['memory']
        learn.setup(self.p)
        self.assertEqual(self.ctx()['memory'],before)
        self.assertEqual(len(wb.context(self.p,'resume-project')['memory']),2)

    def test_new_task_retrieval_and_irrelevant_exclusion(self):
        wb.remember(self.p,'case','css','color contrast for typography','fixture','observed')
        hits = self.ctx()['memory']
        self.assertEqual([m['topic'] for m in hits], ['B002-CASE-001','B001-CASE-001'])
        self.assertTrue(all(m['matched_terms'] for m in hits))
        self.assertTrue(all('Scope:' in m['content'] for m in hits))
        self.assertEqual([m['topic'] for m in self.ctx('typography')['memory']],['css'])
        self.assertEqual(self.ctx('astronomy telescope')['memory'],[])

    def test_context_payload_budget_and_stale(self):
        wb.handoff(self.p,'project-intake','x'*1000,'fixture')
        wb.handoff(self.p,'requirements-spec','old spec','fixture')
        small = learn.task_context(self.p,'requirements-spec','SYN-LAB-3',self.query,budget=256)
        self.assertEqual(small['status'],'NEEDS_FULL_READ')
        self.assertEqual(small['requires_full_read'],['requirements'])
        wb.handoff(self.p,'project-intake','revised','fixture')
        stale = learn.task_context(self.p,'architecture-design','SYN-LAB-3',self.query)
        self.assertEqual(stale['missing'],['specification'])
        self.assertFalse(stale['artifact_index']['specification']['current'])
        self.assertNotIn('specification',stale['artifact_content'])
        full = self.ctx(budget=800)
        self.assertLessEqual(full['payload_chars'],800)
        self.assertEqual(full['artifact_content'],{})
        self.assertNotIn('old spec',json.dumps(full))

    def test_feedback_candidate_and_dedup(self):
        args = (self.p,'SYN-LAB-3','session-1','event-1','test_failure','SQLite inventory','synthetic rollback failed','local test')
        first = learn.feedback(*args)
        self.assertTrue(first['review_required'])
        self.assertEqual(learn.feedback(*args)['memory_id'],first['memory_id'])
        with self.assertRaises(ValueError):
            learn.feedback(*args[:-1],'different evidence')
        ctx = self.ctx()
        self.assertNotIn(first['memory_id'],[m['id'] for m in ctx['memory']])
        self.assertIn(first['memory_id'],[m['id'] for m in ctx['review_candidates']])
        self.assertEqual(len(learn.history(self.p,'SYN-LAB-3')['events']),1)

    def test_candidate_preference_never_applied(self):
        result = learn.feedback(self.p,'SYN-LAB-3','s1','evt-2','preference','SQLite','use SQLite everywhere','fixture statement')
        self.assertEqual(result['basis'],'candidate')
        self.assertIn(result['memory_id'],[m['id'] for m in self.ctx()['review_candidates']])
        self.assertNotIn(result['memory_id'],[m['id'] for m in self.ctx()['memory']])

    def test_case_citation_persists_in_new_process(self):
        mid = self.ctx()['memory'][0]['id']
        result = learn.cite(self.p,'debug-and-repair','SYN-LAB-3','session-1',self.query,mid,'applied','synthetic repair test')
        self.assertTrue(result['operator_declared_not_independently_verified'])
        inp = self.root/'input.json'
        inp.write_text(json.dumps({'task':'SYN-LAB-3'}),encoding='utf-8')
        response = subprocess.run([sys.executable,'-m','src.workbench_learning','history','--workspace',str(self.p),'--input',str(inp)],capture_output=True,text=True,check=True)
        use = json.loads(response.stdout)['uses'][0]
        self.assertEqual(use['session'],'session-1')
        self.assertEqual(use['topic'],'B002-CASE-001')
        inp.write_text(json.dumps({'skill':'debug-and-repair','task':'SYN-LAB-3','query':self.query}),encoding='utf-8')
        response = subprocess.run([sys.executable,'-m','src.workbench_learning','context','--workspace',str(self.p),'--input',str(inp)],capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(response.stdout)['memory'][0]['id'],mid)
        learn.cite(self.p,'debug-and-repair','SYN-LAB-3','session-2',self.query,mid,'not_applicable','future multi-node test needs different architecture')
        self.assertEqual(len(learn.history(self.p,'SYN-LAB-3')['uses']),2)
        self.assertEqual(learn.history(self.p,'OTHER')['uses'],[])

    def test_irrelevant_or_retired_case_cannot_be_cited(self):
        mid = self.ctx()['memory'][0]['id']
        with self.assertRaises(ValueError):
            learn.cite(self.p,'debug-and-repair','SYN-LAB-3','s1','astronomy',mid,'applied','fixture')
        replacement = wb.remember(self.p,'case','B002-CASE-001','SQLite inventory revised','fixture','observed')['memory_id']
        self.assertNotIn(mid,[m['id'] for m in self.ctx()['memory']])
        wb.resolve(self.p,mid,replacement,'synthetic review')
        learn.setup(self.p)
        self.assertNotIn(mid,[m['id'] for m in self.ctx()['memory']])
        with self.assertRaises(ValueError):
            learn.cite(self.p,'debug-and-repair','SYN-LAB-3','s1',self.query,mid,'applied','fixture')

    def test_readonly_retrieval_and_missing_database(self):
        db = self.p/'workbench.sqlite3'
        before = db.read_bytes()
        self.ctx()
        learn.history(self.p,'SYN-LAB-3')
        self.assertEqual(db.read_bytes(),before)
        db.unlink()
        with self.assertRaises((ValueError,sqlite3.OperationalError)):
            self.ctx()
        self.assertFalse(db.exists())

    def test_project_isolation(self):
        other = wb.initialize(self.root/'other','synthetic other')
        learn.setup(other)
        private = wb.remember(self.p,'case','SQLite secret fixture','isolated notes','fixture','observed')['memory_id']
        self.assertIn(private,[m['id'] for m in self.ctx()['memory']])
        self.assertNotIn('isolated notes',json.dumps(learn.task_context(other,'debug-and-repair','SYN-LAB-3',self.query)))
        self.assertEqual(learn.history(other,'SYN-LAB-3')['uses'],[])

    def test_bounds_and_missing_setup(self):
        for kw in ({'budget':0},{'limit':21},{'limit':True}):
            with self.assertRaises(ValueError):
                self.ctx(**kw)
        other = wb.initialize(self.root/'new','synthetic other')
        before = (other/'workbench.sqlite3').read_bytes()
        with self.assertRaises(sqlite3.OperationalError):
            learn.task_context(other,'debug-and-repair','T',self.query)
        self.assertEqual((other/'workbench.sqlite3').read_bytes(),before)

    def test_new_lab_report_recovery_applies_case(self):
        # New task: report exporter must not recreate a missing source database.
        query = 'SQLite 唯讀 缺庫 report recovery reconcile'
        ctx = learn.task_context(self.p,'debug-and-repair','SYN-REPORT',query)
        case = next(m for m in ctx['memory'] if m['topic']=='B001-CASE-001')
        source = self.root/'missing-report.sqlite'
        with self.assertRaises(sqlite3.OperationalError):
            sqlite3.connect(source.as_uri()+'?mode=ro',uri=True)
        self.assertFalse(source.exists())
        learn.cite(self.p,'debug-and-repair','SYN-REPORT','report-session',query,case['id'],'applied','test_new_lab_report_recovery_applies_case: read-only absent source raises and no file is created')
        observed = learn.feedback(self.p,'SYN-REPORT','report-session','report-fix','test_fix','SQLite report','Missing source refused without new file','test_new_lab_report_recovery_applies_case')
        self.assertEqual(observed['basis'],'candidate')
        self.assertEqual(learn.history(self.p,'SYN-REPORT')['uses'][0]['topic'],'B001-CASE-001')
