"""Actual cross-stage exercise on synthetic equipment data; no model calls."""
import inspect
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from src import team_workbench as wb, workbench_tasks as tasks, workbench_learning as learn
from src.p21_equipment_site import Store
from src.p21_equipment_report import report_v1, report_v2

CASE = 'P21-REPORT'
QUERY = 'SQLite inventory transaction mode=ro rollback ledger'


class CrossStageTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.work = wb.initialize(self.root/'work', 'Synthetic equipment report')
        tasks.setup(self.work)
        learn.setup(self.work)
        self.store = Store(self.root/'equipment.sqlite')
        self.store.initialize()
        # Deliberately different owners and actors; real SQLite transitions.
        self.store.reserve('member','1'*32,4)
        self.store.reserve('member2','2'*32,3)
        self.store.reserve('member2','3'*32,8)
        self.store.release('member','member','1'*32,'4'*32,'cancel')
        self.store.release('admin','member2','2'*32,'5'*32,'return')
        self.store.reserve('member','6'*32,2)
        self.store.reserve('member2','7'*32,1)
        self.store.release('member','member','8'*32,'9'*32,'cancel')
        self.store.release('admin','member2','a'*32,'b'*32,'return')
        self.store.release('admin','member','c'*32,'d'*32,'return')

    def ready(self):
        return tasks.review(self.work)['next_ready']

    def state(self, task):
        return next(r for r in tasks.review(self.work)['tasks'] if r['id']==task)

    def stage(self, task, skill, revision, content, evidence):
        self.assertIn(task,self.ready())
        session=f'{task}-r{revision}'
        context=wb.context(self.work,skill)
        self.assertEqual(context['status'],'READY_TO_REVIEW_INPUTS')
        self.assertFalse(context['model_or_subagent_invoked'])
        tasks.start(self.work,task,session,expected_revision=revision)
        item=wb.handoff(self.work,skill,content,evidence)
        current=wb.context(self.work,skill)['artifacts'][item['kind']]
        self.assertTrue(current['current'])
        self.assertEqual(current['content'],content.strip())
        self.assertEqual(current['source_ref'],evidence)
        for dep, ident in json.loads(current['dependencies']).items():
            self.assertEqual(context['artifacts'][dep]['id'],ident)
        self.assertEqual(tasks.finish(self.work,task,session,{'check':'PASS'},evidence,expected_revision=revision)['state'],'DONE')
        return item['artifact_id']

    def check_v1(self, fn):
        self.assertEqual(fn(self.store,'member'),{'active_quantity':2})
        self.assertEqual(fn(self.store,'member2'),{'active_quantity':1})
        self.assertEqual(fn(self.store,'admin'),{'active_quantity':3})

    def check_v2(self, fn):
        self.assertEqual(fn(self.store,'member'),{
            'active_quantity':2,'cancelled_quantity':4,'returned_quantity':0,
            'insufficient_quantity':0,'denied_operations':1})
        self.assertEqual(fn(self.store,'member2'),{
            'active_quantity':1,'cancelled_quantity':0,'returned_quantity':3,
            'insufficient_quantity':8,'denied_operations':0})
        self.assertEqual(fn(self.store,'admin'),{
            'active_quantity':3,'cancelled_quantity':4,'returned_quantity':3,
            'insufficient_quantity':8,'denied_operations':2,
            'inventory':{'stock':10,'reserved':3,'available':7}})

    def test_full_revision_handoff_recovery_and_revalidation(self):
        w=self.work
        tasks.question(w,'LIVE','External activation approval (intentionally absent)')
        definitions=[
            ('intake',[],[]),('spec',['intake'],[]),('arch',['spec'],[]),
            ('plan',['spec','arch'],[]),('impl',['spec','arch','plan'],[]),
            ('qa',['impl'],[]),('security',['arch'],[]),
            ('deploy-plan',['impl','qa','security'],[]),
            ('inventory-audit',[],[]),('activate',['deploy-plan'],['LIVE'])]
        for priority,(name,deps,gates) in enumerate(definitions):
            tasks.add(w,name,name,priority,deps,gates,['check'])
        source1='Synthetic fixture P21-REPORT revision 1; not user approval'
        source2='Synthetic fixture P21-REPORT revision 2; not user approval'
        before=self.store.path.read_bytes()
        # An independent verified inventory branch is not subject to report revisions.
        tasks.start(w,'inventory-audit','audit-r1',expected_revision=1)
        self.assertEqual(self.store.view(None)[:2],(10,3))
        tasks.finish(w,'inventory-audit','audit-r1',{'check':'PASS'},'Store.view: stock 10 reserved 3',expected_revision=1)
        self.stage('intake','project-intake',1,'R1: active quantity by authenticated actor.',source1)
        self.stage('spec','requirements-spec',1,'R1: members own active quantities; admin aggregate; read-only.',source1)
        self.stage('arch','architecture-design',1,'Store.view single read snapshot -> filter RESERVED -> sum qty; actor scope.',source1)
        self.stage('plan','task-planning',1,'Implement report_v1 -> QA three actors -> security -> candidate launch plan only.',source1)
        self.check_v1(report_v1)
        old_impl=self.stage('impl','implement-feature',1,inspect.getsource(report_v1),'Executed report_v1: member=2, member2=1, admin=3')
        old_qa=self.stage('qa','test-and-acceptance',1,'Three actor quantities independently compared with fixture expectations.','test_full_revision_handoff: check_v1 passed')
        self.stage('security','security-review',1,'Member scopes differ; no global count returned by member report.','check_v1 three actors')
        # A separate process actually claims the plan and stages an input,
        # then exits before acceptance. No external commands or deployment.
        pending=self.root/'staged-plan.json'
        script=(
            'import json,sys; from pathlib import Path; '
            'from src import workbench_tasks as t,team_workbench as w; '
            'p=sys.argv[1]; t.start(p,"deploy-plan","worker-r1",expected_revision=1); '
            'c=w.context(p,"deployment"); '
            'Path(sys.argv[2]).write_text(json.dumps({"implementation":c["artifacts"]["implementation"]["id"],"qa":c["artifacts"]["qa"]["id"]}),encoding="utf-8")'
        )
        child=subprocess.run([sys.executable,'-c',script,str(w),str(pending)],check=True,capture_output=True,text=True,timeout=20)
        self.assertEqual(child.returncode,0)
        self.assertEqual(json.loads(pending.read_text()),{'implementation':old_impl,'qa':old_qa})
        self.assertEqual(self.state('deploy-plan')['state'],'RUNNING')
        # Synthetic confirmed revision; explicitly update both dependency indexes.
        change=tasks.revise(w,'intake',1,'change-r2',source2,confirmed=True)
        affected={name for name,_,_ in definitions}-{'inventory-audit'}
        self.assertEqual(set(change['affected']),affected)
        new_requirement=wb.handoff(w,'project-intake',
            'R2: add active/cancelled/returned/insufficient quantities, own denied count; admin-only inventory.',source2)
        stale=wb.context(w,'deployment')
        for kind in ('specification','architecture','plan','implementation','qa','security-review'):
            self.assertFalse(stale['artifacts'][kind]['current'],kind)
        self.assertEqual(stale['status'],'NEEDS_PREREQUISITES')
        with self.assertRaises(ValueError):
            wb.handoff(w,'deployment','stale plan',source2)
        self.assertEqual(self.state('deploy-plan')['state'],'RECOVERY_REQUIRED')
        self.assertEqual(self.state('inventory-audit')['revision'],1)
        self.assertEqual(self.state('inventory-audit')['state'],'DONE')
        self.assertNotIn('intake',self.ready())
        with self.assertRaises(ValueError):
            tasks.finish(w,'deploy-plan','worker-r1',{'check':'PASS'},'stale staged plan',expected_revision=1)
        with self.assertRaises(ValueError):
            tasks.resume(w,'deploy-plan','worker-r1','worker-stale','obsolete',True,expected_revision=2)
        # Actual child exit and local staged item readback precede recovery.
        self.assertEqual(json.loads(pending.read_text())['implementation'],old_impl)
        pending.unlink()
        tasks.recover(w,'deploy-plan',2,'worker-r1','recovery-r2',
                      'Child process exit 0; staged local file inspected and removed; no external deployment.',confirmed=True)
        self.assertIn('intake',self.ready())
        # New process reads persisted state, not chat or old approval.
        fresh=subprocess.run([sys.executable,'-m','src.workbench_tasks','review','--workspace',str(w)],
                             check=True,capture_output=True,text=True,timeout=20)
        self.assertEqual(json.loads(fresh.stdout)['next_ready'],self.ready())
        tasks.start(w,'intake','intake-r2',expected_revision=2)
        self.assertEqual(wb.context(w,'requirements-spec')['artifacts']['requirements']['id'],new_requirement['artifact_id'])
        tasks.finish(w,'intake','intake-r2',{'check':'PASS'},source2,expected_revision=2)
        learn.feedback(w,CASE,'intake-r2','report-revision-2','requirement_change','report revision',
                       'Add state quantities and own denial counts; preserve old evidence.',source2)
        self.stage('spec','requirements-spec',2,
                   'R2: own reservation state quantities for members; admin aggregate + inventory; own denied operations for both; no writes.',source2)
        self.stage('arch','architecture-design',2,
                   'Reuse Store.view(snapshot, actor); sum four state buckets; count own NOT_ACTIVE attempts; check admin stock invariant.',source2)
        self.stage('plan','task-planning',2,'Revalidate old implementation, record failure, implement report_v2, QA exact expected dicts; release gate open.',source2)
        # Real RED: run revised acceptance on executable old implementation.
        tasks.start(w,'impl','impl-red-r2',expected_revision=2)
        try:
            self.check_v2(report_v1)
        except AssertionError as error:
            detail=str(error)
        else:
            self.fail('old implementation unexpectedly satisfied revised requirement')
        self.assertIn('cancelled_quantity',detail)
        tasks.finish(w,'impl','impl-red-r2',{'check':'FAIL'},'check_v2(report_v1): '+detail,expected_revision=2)
        learn.feedback(w,CASE,'impl-red-r2','report-red-2','test_failure','report red',
                       'Actual revised acceptance rejected v1.',detail)
        self.assertNotIn('qa',self.ready())
        # GREEN: executable revised implementation on same fixture and oracle.
        context=learn.task_context(w,'implement-feature',CASE,QUERY)
        self.assertEqual(context['status'],'READY_TO_REVIEW_INPUTS')
        case=next(m for m in context['memory'] if m['topic']=='B002-CASE-001')
        self.check_v2(report_v2)
        self.assertEqual(before,self.store.path.read_bytes())
        new_impl=self.stage('impl','implement-feature',2,inspect.getsource(report_v2),
                            'check_v2(report_v2): three exact dictionaries; SQLite bytes unchanged')
        self.assertNotEqual(new_impl,old_impl)
        learn.cite(w,'implement-feature',CASE,'impl-r2',QUERY,case['id'],'applied',
                   'report_v2 uses Store.view read-only snapshot; bytes unchanged, inventory invariant verified')
        learn.feedback(w,CASE,'impl-r2','report-green-2','test_fix','report green',
                       'Revision 2 exact dictionaries, stock invariant and no writes verified.','check_v2(report_v2)')
        # QA re-runs functional acceptance, then negative inputs and missing DB.
        self.check_v2(report_v2)
        with self.assertRaises(PermissionError): report_v2(self.store,'unknown')
        with self.assertRaises(Exception) as missing:
            report_v2(Store(self.root/'missing.sqlite'),'member')
        self.assertIsInstance(missing.exception,__import__('sqlite3').Error)
        self.assertFalse((self.root/'missing.sqlite').exists())
        self.assertEqual(before,self.store.path.read_bytes())
        self.stage('qa','test-and-acceptance',2,
                   'Exact member/member2/admin dictionaries; unknown actor denied; missing DB not created; unchanged DB.',
                   'check_v2 + negative tests passed')
        self.stage('security','security-review',2,
                   'Member has no global inventory; own denied count only; admin aggregate reservation quantities, own denied count.',
                   'check_v2 exact dictionaries passed')
        self.stage('deploy-plan','deployment',2,
                   'Candidate local report only. No external release, no deployment; LIVE approval remains open.',
                   'QA and security artifacts read back; synthetic scope')
        final=tasks.review(w)
        self.assertEqual(final['completed'],9)
        self.assertEqual(final['failed_attempts'],1)
        self.assertEqual(final['next_ready'],[])
        self.assertEqual(final['recovery_review'],[])
        self.assertEqual(final['open_decisions'][0]['id'],'LIVE')
        self.assertEqual(self.state('activate')['state'],'PENDING')
        with self.assertRaises(ValueError):
            tasks.start(w,'activate','not-authorized',expected_revision=2)
        self.assertEqual(wb.context(w,'deployment')['status'],'READY_TO_REVIEW_INPUTS')
        with wb.connect(w) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM artifacts WHERE id IN (?,?)',(old_impl,old_qa)).fetchone()[0],2)
        history=learn.history(w,CASE)
        self.assertEqual(len(history['events']),3)
        self.assertEqual(history['uses'][0]['topic'],'B002-CASE-001')
        self.assertEqual(history['uses'][0]['decision'],'applied')
        self.assertEqual(before,self.store.path.read_bytes())
        print('P21-CROSS-STAGE: v1 accepted; 9 invalidated; stopped worker recovered; v1 rejected on v2; v2 accepted; 9 DONE; LIVE blocked; 3 feedback events; B002 case applied',flush=True)
