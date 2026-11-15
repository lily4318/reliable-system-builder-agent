"""Same public oracle for a deliberately weakened baseline and improved design."""
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from src.p22_document_review import ReviewStore, Baseline
from src import team_workbench as wb, workbench_learning as learn


def token(n): return format(n,'032x')


class TransferTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)

    def compare(self, cls, name):
        s=cls(self.root/(cls.__name__+'-'+name+'.sqlite'))
        s.initialize()
        def edit(n,rev,body='Synthetic revised text'):
            return s.action('editor',token(n),'edit',rev,body)
        def approve(n,rev): return s.action('reviewer',token(n),'approve',rev)
        def publish(n,rev): return s.action('publisher',token(n),'publish',rev)
        if name=='happy':
            return (edit(1,1),approve(2,2),publish(3,2),s.snapshot()['published'])==('EDITED','APPROVED','PUBLISHED',2)
        if name=='stale_approval':
            approve(1,1); edit(2,1)
            return publish(3,2)=='UNAPPROVED' and s.snapshot()['published'] is None
        if name=='denied_replay':
            first=publish(1,1); approve(2,1)
            return first=='UNAPPROVED' and publish(1,1)=='UNAPPROVED' and s.snapshot()['published'] is None
        if name=='future_revision_replay':
            first=approve(1,2); edit(2,1)
            return first=='STALE' and approve(1,2)=='STALE' and not s.snapshot()['approvals']
        if name=='fault_atomic':
            try: s.action('editor',token(1),'edit',1,'Synthetic fault',fault=True)
            except RuntimeError: pass
            else: raise AssertionError('fault not injected')
            state=s.snapshot()
            return state['head']==1 and len(state['versions'])==1 and s.receipt('editor',token(1)) is None
        if name=='competing_edit':
            with ThreadPoolExecutor(max_workers=6) as pool:
                results=list(pool.map(lambda i:edit(i,1,'Synthetic '+str(i)),range(1,7)))
            return sorted(results)==['EDITED']+['STALE']*5 and len(s.snapshot()['versions'])==2
        if name=='role_guard':
            before=s.path.read_bytes()
            try: s.action('editor',token(1),'publish',1)
            except PermissionError: return s.path.read_bytes()==before
            return False
        if name=='token_conflict':
            edit(1,1)
            try: edit(1,1,'Different text')
            except ValueError: return s.snapshot()['head']==2
            return False
        if name=='readonly_missing':
            missing=cls(self.root/(cls.__name__+'-missing.sqlite'))
            try: missing.receipt('editor',token(1))
            except sqlite3.Error: return not missing.path.exists()
            return False
        if name=='published_history':
            approve(1,1); publish(2,1); edit(3,1)
            state=s.snapshot()
            return state['published']==1 and state['head']==2 and state['versions'][0]==(1,'Synthetic initial text')
        raise AssertionError(name)

    def test_controlled_transfer_same_oracle(self):
        # Expected behaviors originate in requirements, not in either implementation.
        names=['happy','stale_approval','denied_replay','future_revision_replay','fault_atomic',
               'competing_edit','role_guard','token_conflict','readonly_missing','published_history']
        baseline={n:self.compare(Baseline,n) for n in names}
        improved={n:self.compare(ReviewStore,n) for n in names}
        self.assertEqual({n for n,v in baseline.items() if not v},
                         {'stale_approval','denied_replay','future_revision_replay','fault_atomic'})
        self.assertTrue(all(improved.values()),improved)
        print('P22-TRANSFER: '+json.dumps({'baseline':baseline,'improved':improved,
              'baseline_pass':sum(baseline.values()),'improved_pass':sum(improved.values()),
              'total':len(names),'independent_agent':False}),flush=True)

    def test_revision_artifacts_and_real_case_retrieval(self):
        w=wb.initialize(self.root/'work','Synthetic document review')
        learn.setup(w)
        # Real opt-in case library import; default remains just two public cases.
        original=wb.context(w,'resume-project')['memory']
        self.assertEqual(len(original),2)
        imported=learn.setup(w,include_training_cases=True)
        self.assertEqual(len(imported['seeded_case_keys']),7)
        first=wb.context(w,'resume-project')['memory']
        self.assertEqual(len(first),7)
        learn.setup(w,include_training_cases=True)
        self.assertEqual(wb.context(w,'resume-project')['memory'],first)
        with self.assertRaises(ValueError): learn.setup(w,include_training_cases='yes')
        for skill,body in [
            ('project-intake','Synthetic local document editor, reviewer, publisher; no external release.'),
            ('requirements-spec','Immutable versions; exact current revision approval; local publication pointer; durable negative decisions; audit atomic; role guard; read-only receipt.'),
            ('architecture-design','SQLite single transaction state plus receipt; per-actor token; exact revision CAS; immutable version history.'),
            ('task-planning','Compare same public oracle, execute CLI, recover after unknown result; no deployment.')]:
            wb.handoff(w,skill,body,'P22 synthetic fixture')
        query='idempotency negative decisions ledger atomic transaction revision receipt browser origin rollback'
        ctx=learn.task_context(w,'implement-feature','P22-DOC',query,limit=10)
        self.assertEqual(ctx['status'],'READY_TO_REVIEW_INPUTS')
        hits={r['topic']:r for r in ctx['memory']}
        self.assertTrue({'P21-CASE-003','P21-CASE-005','P21-CASE-006'}<=set(hits))
        self.assertTrue(self.compare(ReviewStore,'denied_replay'))
        self.assertTrue(self.compare(ReviewStore,'fault_atomic'))
        for key,decision,evidence in [
            ('P21-CASE-003','applied','denied_replay oracle: same token cannot publish after later approval'),
            ('P21-CASE-005','applied','fault_atomic oracle: state and receipt roll back together'),
            ('P21-CASE-006','not_applicable','CLI-only slice; browser Origin/DOM and migration conditions absent')]:
            learn.cite(w,'implement-feature','P22-DOC','transfer-1',query,hits[key]['id'],decision,evidence,limit=10)
        wb.handoff(w,'implement-feature','src/p22_document_review.py; ReviewStore and explicit Baseline','same-oracle functional tests')
        wb.handoff(w,'test-and-acceptance','Same oracle with preserved baseline failures and improved controls','test_controlled_transfer_same_oracle')
        wb.handoff(w,'security-review','Actor role check; caller labels trusted only; no network or production auth','role_guard, local CLI scope')
        wb.handoff(w,'deployment','Local CLI only; external release prohibited','controlled synthetic exercise')
        learn.feedback(w,'P22-DOC','transfer-1','p22-red','test_failure','document review stale approval','Baseline permits later version under earlier approval and changes state on fault.','same oracle baseline')
        learn.feedback(w,'P22-DOC','transfer-1','p22-green','test_fix','document review durable decision','Exact revision approval, durable negative decisions and atomic state/receipt pass same oracle.','same oracle improved')
        history=learn.history(w,'P22-DOC')
        self.assertEqual(len(history['events']),2)
        self.assertEqual({r['topic']:r['decision'] for r in history['uses']},
                         {'P21-CASE-003':'applied','P21-CASE-005':'applied','P21-CASE-006':'not_applicable'})
        self.assertEqual(wb.context(w,'deployment')['status'],'READY_TO_REVIEW_INPUTS')
        print('P22-LEARNING: 3 prior cases retrieved; 2 applied; 1 not applicable; 2 candidate feedback events',flush=True)

    def test_cli_lost_acknowledgement_and_restart(self):
        path=self.root/'cli.sqlite'; args=[sys.executable,'-m','src.p22_document_review']
        def cli(command,data=None):
            cmd=args+[command,'--database',str(path)]
            if data is not None:
                inp=self.root/'command.json'
                inp.write_text(json.dumps(data),encoding='utf-8')
                cmd+=['--input',str(inp)]
            r=subprocess.run(cmd,capture_output=True,text=True,timeout=20,check=True)
            return json.loads(r.stdout)
        self.assertTrue(cli('init')['initialized'])
        child=subprocess.run([sys.executable,'-c',
            "import os,sys; from src.p22_document_review import ReviewStore; ReviewStore(sys.argv[1]).action('editor','1'*32,'edit',1,'Synthetic child'); os._exit(23)",str(path)],
            capture_output=True,text=True,timeout=20)
        self.assertEqual(child.returncode,23)
        before=path.read_bytes()
        self.assertEqual(cli('receipt',{'actor':'editor','token':'1'*32})['result'],'EDITED')
        self.assertEqual(path.read_bytes(),before)
        self.assertEqual(cli('action',{'actor':'reviewer','token':token(2),'operation':'approve','expected_revision':2}),'APPROVED')
        self.assertEqual(cli('action',{'actor':'publisher','token':token(3),'operation':'publish','expected_revision':2}),'PUBLISHED')
        state=cli('snapshot')
        self.assertEqual((state['head'],state['published'],len(state['versions'])),(2,2,2))
        print('P22-CLI: subprocess lost acknowledgement reconciled read-only; approval and local publication survived restart',flush=True)
