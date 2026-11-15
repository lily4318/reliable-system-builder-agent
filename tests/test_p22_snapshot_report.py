"""P2-2c developer-authored fixed oracles for a distinct source/export workflow."""
import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import zipfile
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path

from src import p22_snapshot_report as export, team_workbench as wb, workbench_learning as learn


class SnapshotReportTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root/'synthetic.sqlite'
        self.output = self.root/'report.zip'
        with closing(sqlite3.connect(self.source)) as db, db:
            db.execute('CREATE TABLE metadata (revision INTEGER NOT NULL)')
            db.execute('INSERT INTO metadata VALUES (1)')
            db.execute('CREATE TABLE records (record_id TEXT, category TEXT, state TEXT, quantity INTEGER)')
            db.executemany('INSERT INTO records VALUES (?,?,?,?)', [
                ('SYN-0003','folder','pending',17),('SYN-0001','paper','complete',5),
                ('SYN-0004','paper','rejected',99),('SYN-0002','folder','complete',7)])

    def read_zip(self,path):
        with zipfile.ZipFile(path) as z:
            self.assertEqual(z.namelist(),['report.json','manifest.json'])
            self.assertIsNone(z.testzip())
            return z.read('report.json'),json.loads(z.read('manifest.json'))

    def test_fixed_oracle_and_privacy(self):
        before = self.source.read_bytes()
        self.assertEqual(export.publish(self.source,self.output,1,2),'PUBLISHED')
        raw, manifest = self.read_zip(self.output)
        expected = b'{"completed_quantities":{"folder":7,"paper":5,"pencil":0},"policy_revision":2,"status_counts":{"complete":2,"pending":1,"rejected":1}}\n'
        source_oracle = b'[["SYN-0001","paper","complete",5],["SYN-0002","folder","complete",7],["SYN-0003","folder","pending",17],["SYN-0004","paper","rejected",99]]\n'
        self.assertEqual(raw,expected)
        self.assertEqual(manifest,{'schema_version':1,'source_revision':1,'policy_revision':2,
            'snapshot_sha256':hashlib.sha256(source_oracle).hexdigest(),
            'report_sha256':hashlib.sha256(expected).hexdigest()})
        self.assertNotIn(b'SYN-',raw)
        self.assertNotIn(b'99',raw)
        self.assertEqual(self.source.read_bytes(),before)
        second = self.root/'again.zip'
        export.publish(self.source,second,1,2)
        self.assertEqual(self.output.read_bytes(),second.read_bytes())

    def test_source_and_policy_revision_change(self):
        export.publish(self.source,self.output,1,1)
        prior = self.output.read_bytes()
        old,_ = self.read_zip(self.output)
        self.assertEqual(json.loads(old),{'policy_revision':1,'completed_quantities':{'paper':5,'folder':7,'pencil':0}})
        self.assertEqual(export.reconcile(self.source,self.output,1,2),'CONFLICT')
        with self.assertRaises(FileExistsError):
            export.publish(self.source,self.output,1,2)
        updated=self.root/'r2.zip'
        export.publish(self.source,updated,1,2)
        self.assertEqual(json.loads(self.read_zip(updated)[0])['status_counts'],{'complete':2,'pending':1,'rejected':1})
        with closing(sqlite3.connect(self.source)) as db, db:
            db.execute('UPDATE metadata SET revision=2')
            db.execute("UPDATE records SET quantity=8 WHERE record_id='SYN-0001'")
        with self.assertRaisesRegex(ValueError,'STALE_SOURCE'):
            export.reconcile(self.source,self.output,1,1)
        self.assertEqual(export.reconcile(self.source,updated,2,2),'CONFLICT')
        fresh=self.root/'source2.zip'
        export.publish(self.source,fresh,2,2)
        self.assertEqual(json.loads(self.read_zip(fresh)[0])['completed_quantities']['paper'],8)
        self.assertEqual(self.output.read_bytes(),prior)
        print('P22C-REVISION: R1 output rejected under R2; old source revision blocked; new revision independently checked',flush=True)

    def test_invalid_source_never_creates_output(self):
        missing=self.root/'missing.sqlite'
        for action in (export.publish,export.reconcile):
            with self.assertRaises(ValueError):
                action(missing,self.output,1,2)
            self.assertFalse(missing.exists())
        with self.assertRaises(ValueError):
            export.publish(self.source,self.output,1,3)
        changes = [
            "INSERT INTO records VALUES ('SYN-0001','paper','complete',1)",
            "UPDATE records SET category='unknown'",
            "UPDATE records SET state='unknown'",
            "UPDATE records SET quantity=-1",
            "UPDATE records SET quantity=1.5",
            "UPDATE records SET record_id='invalid'",
            "DELETE FROM records",
            "INSERT INTO metadata VALUES (1)",
        ]
        for idx,stmt in enumerate(changes):
            with self.subTest(stmt=stmt):
                broken=self.root/('bad-%d.sqlite'%idx)
                broken.write_bytes(self.source.read_bytes())
                with closing(sqlite3.connect(broken)) as db, db:
                    db.execute(stmt)
                before=broken.read_bytes()
                with self.assertRaises(ValueError):
                    export.publish(broken,self.output,1,2)
                self.assertFalse(self.output.exists())
                self.assertEqual(broken.read_bytes(),before)

    def test_readonly_reconciliation_and_concurrent_policy_race(self):
        self.assertEqual(export.reconcile(self.source,self.output,1,2),'NOT_OBSERVED')
        def attempt(policy):
            try:
                return export.publish(self.source,self.output,1,policy)
            except FileExistsError:
                return 'EXISTS'
        with ThreadPoolExecutor(max_workers=2) as workers:
            results=list(workers.map(attempt,(1,2)))
        self.assertCountEqual(results,['PUBLISHED','EXISTS'])
        before=self.output.read_bytes()
        statuses=[export.reconcile(self.source,self.output,1,n) for n in (1,2)]
        self.assertEqual(statuses[results.index('PUBLISHED')],'COMMITTED')
        self.assertEqual(statuses[results.index('EXISTS')],'CONFLICT')
        self.assertEqual(self.output.read_bytes(),before)
        self.output.write_bytes(before+b'corruption')
        self.assertEqual(export.reconcile(self.source,self.output,1,2),'CONFLICT')
        self.assertEqual(self.output.read_bytes(),before+b'corruption')
        self.assertFalse(list(self.root.glob('.p22-report-*')))

    def test_cli_recovery_after_lost_ack(self):
        child=subprocess.run([sys.executable,'-c',
            'import os,sys; from src.p22_snapshot_report import publish; publish(sys.argv[1],sys.argv[2],1,2); os._exit(23)',
            str(self.source),str(self.output)],capture_output=True,timeout=20)
        self.assertEqual(child.returncode,23)
        before=self.output.read_bytes()
        result=subprocess.run([sys.executable,'-m','src.p22_snapshot_report','reconcile',
            '--source',str(self.source),'--output',str(self.output),'--source-revision','1','--policy-revision','2'],
            capture_output=True,text=True,timeout=20,check=True)
        self.assertEqual(json.loads(result.stdout),{'status':'COMMITTED'})
        self.assertEqual(self.output.read_bytes(),before)

    def test_actual_case_transfer_and_versioned_handoffs(self):
        work=wb.initialize(self.root/'work','Synthetic revisioned reports')
        learn.setup(work,include_training_cases=True)
        for skill,body in [
            ('project-intake','Synthetic aggregate report from a local read-only database.'),
            ('requirements-spec','R1 completed quantities; R2 adds status counts, aggregates only; expected source revision.'),
            ('architecture-design','SQLite read snapshot; aggregate JSON plus manifest deterministic ZIP; exclusive output.'),
            ('task-planning','Validate exact totals, source and policy revision, negative paths and recovery.')]:
            wb.handoff(work,skill,body,'P22c synthetic fixture')
        query='SQLite mode ro recovery reconcile file bundle hash exclusive publication browser Origin DOM'
        ctx=learn.task_context(work,'implement-feature','P22-REPORT',query,limit=10)
        self.assertEqual(ctx['status'],'READY_TO_REVIEW_INPUTS')
        hits={m['topic']:m for m in ctx['memory']}
        for key,decision,evidence in [
            ('P22-CASE-002','applied','Adapt single bundle from JSON to ZIP report plus manifest; compare exact bytes, reject stale policy and competing output.'),
            ('B001-CASE-001','applied','Read-only existing SQLite source; missing source cannot be recreated.'),
            ('P21-CASE-006','not_applicable','No browser or database migration.')]:
            self.assertIn(key,hits)
            learn.cite(work,'implement-feature','P22-REPORT','transfer-c',query,hits[key]['id'],decision,evidence,limit=10)
        export.publish(self.source,self.output,1,1)
        self.assertEqual(export.reconcile(self.source,self.output,1,2),'CONFLICT')
        new=self.root/'new-policy.zip'
        export.publish(self.source,new,1,2)
        self.assertEqual(json.loads(self.read_zip(new)[0])['status_counts']['pending'],1)
        for skill,body in [
            ('implement-feature','src/p22_snapshot_report.py: bounded source snapshot and ZIP exporter.'),
            ('test-and-acceptance','Exact fixed report and manifest oracle; stale source/policy and process recovery.'),
            ('security-review','Aggregate-only report, no raw IDs; trusted paths, no production or role authentication.'),
            ('deployment','Local synthetic export only; no external release.')]:
            wb.handoff(work,skill,body,'P22c functional tests')
        learn.feedback(work,'P22-REPORT','transfer-c','p22c-revision','requirement_change',
            'report policy revision','Do not overwrite R1 output when R2 requires additional counters.',
            'R1 output conflict and separate R2 exact result; candidate only')
        history=learn.history(work,'P22-REPORT')
        self.assertEqual({r['topic']:r['decision'] for r in history['uses']},
            {'P22-CASE-002':'applied','B001-CASE-001':'applied','P21-CASE-006':'not_applicable'})
        self.assertEqual(len(history['events']),1)
        self.assertEqual(wb.context(work,'deployment')['status'],'READY_TO_REVIEW_INPUTS')
        print('P22C-TRANSFER: P22-CASE-002 and B001-CASE-001 applied; browser case not applicable; R2 result checked',flush=True)

    def test_curated_snapshot_case_opt_in(self):
        from unittest.mock import patch
        work = wb.initialize(self.root/'casework','Synthetic versioned aggregate export')
        query = 'SQLite snapshot revision policy report aggregate ZIP manifest logical hash'
        def retrieve():
            return learn.task_context(work,'debug-and-repair','SYN-EXPORT',query,limit=10)['memory']
        learn.setup(work)
        self.assertEqual(len(wb.context(work,'resume-project')['memory']),2)
        self.assertNotIn('P22-CASE-003',{r['topic'] for r in retrieve()})
        through_c = tuple(c for c in learn.TRAINING_CASES if c[0] in {'P21-CASE-003','P21-CASE-005','P21-CASE-006','P22-CASE-002','P22-CASE-003'})
        corpus = patch.object(learn,'TRAINING_CASES',through_c)
        corpus.start()
        self.addCleanup(corpus.stop)
        historical = tuple(c for c in learn.TRAINING_CASES if c[0]!='P22-CASE-003')
        with patch.object(learn,'TRAINING_CASES',historical):
            learn.setup(work,include_training_cases=True)
        before = {r['topic']:r for r in wb.context(work,'resume-project')['memory']}
        self.assertEqual(len(before),6)
        learn.setup(work,include_training_cases=True)
        after = {r['topic']:r for r in wb.context(work,'resume-project')['memory']}
        self.assertEqual(len(after),7)
        self.assertEqual({k:after[k] for k in before},before)
        hit = next(r for r in retrieve() if r['topic']=='P22-CASE-003')
        self.assertEqual(hit['basis'],'observed')
        self.assertIn('43668235893',hit['evidence'])
        self.assertIn('not live-source CAS',hit['content'])
        learn.setup(work,include_training_cases=True)
        self.assertEqual({r['topic']:r for r in wb.context(work,'resume-project')['memory']},after)
        args = self.root/'query.json'
        args.write_text(json.dumps({'skill':'debug-and-repair','task':'SYN-EXPORT','query':query,'limit':10}),encoding='utf-8')
        child = subprocess.run([sys.executable,'-m','src.workbench_learning','context','--workspace',str(work),'--input',str(args)],
                               capture_output=True,text=True,check=True,timeout=20)
        self.assertEqual(next(r for r in json.loads(child.stdout)['memory'] if r['topic']=='P22-CASE-003')['id'],hit['id'])
        irrelevant = learn.task_context(work,'debug-and-repair','SYN-OTHER','astronomy telescope nebula',limit=10)
        self.assertNotIn('P22-CASE-003',{r['topic'] for r in irrelevant['memory']})
        print('P22C-DISTILL: 6-to-7 migration, preserved old IDs/content, idempotent opt-in and new process retrieval',flush=True)

    def test_wal_snapshot_revision_is_not_live_publication_cas(self):
        from unittest.mock import patch
        real_connect = sqlite3.connect
        with closing(real_connect(self.source)) as db:
            self.assertEqual(db.execute('PRAGMA journal_mode=WAL').fetchone()[0],'wal')
        events = []
        def connect_with_trace(*args, **kwargs):
            reader = real_connect(*args, **kwargs)
            def writer_at_row_query(statement):
                if statement.startswith('SELECT record_id') and not events:
                    try:
                        with closing(real_connect(self.source,timeout=2)) as writer, writer:
                            writer.execute('UPDATE metadata SET revision=2')
                            writer.execute("UPDATE records SET quantity=8 WHERE record_id='SYN-0001'")
                        events.append('writer_committed')
                    except Exception as exc:
                        events.append(repr(exc))
            reader.set_trace_callback(writer_at_row_query)
            return reader
        with patch.object(export.sqlite3,'connect',connect_with_trace):
            self.assertEqual(export.publish(self.source,self.output,1,2),'PUBLISHED')
        self.assertEqual(events,['writer_committed'])
        raw,manifest=self.read_zip(self.output)
        self.assertEqual(manifest['source_revision'],1)
        self.assertEqual(json.loads(raw)['completed_quantities']['paper'],5)
        with self.assertRaisesRegex(ValueError,'STALE_SOURCE'):
            export.reconcile(self.source,self.output,1,2)
        self.assertEqual(export.reconcile(self.source,self.output,2,2),'CONFLICT')
        fresh=self.root/'revision2.zip'
        export.publish(self.source,fresh,2,2)
        self.assertEqual(json.loads(self.read_zip(fresh)[0])['completed_quantities']['paper'],8)
        print('P22C-SNAPSHOT: WAL writer committed R2 during R1 read; coherent R1 report, live R2 not claimed',flush=True)

    def test_invalid_oversized_fields_not_materialized_into_python(self):
        from unittest.mock import patch
        real_connect=sqlite3.connect
        # Actual SQLite TEXT/BLOB; measure values returned to Python, not a
        # synthetic estimate or native SQLite allocation claim.
        for table,column,value in (
            ('metadata','revision','x'*262144),
            ('records','record_id','x'*262144),
            ('records','category','x'*262144),
            ('records','state',b'x'*262144),
            ('records','quantity',b'x'*262144),
            ('records','record_id','SYN-0005'+chr(0)+'x'*262144),
        ):
            with self.subTest(table=table,column=column,kind=type(value).__name__):
                source=self.root/'oversized.sqlite'
                source.write_bytes(self.source.read_bytes())
                with closing(real_connect(source)) as db, db:
                    db.execute('UPDATE '+table+' SET '+column+'=?',(value,))
                before=source.read_bytes()
                self.output.write_bytes(b'prior output')
                seen=[]
                def connect(*args,**kwargs):
                    reader=real_connect(*args,**kwargs)
                    def measure(cursor,row):
                        seen.extend(len(v) for v in row if isinstance(v,(str,bytes)))
                        return row
                    reader.row_factory=measure
                    return reader
                with patch.object(export.sqlite3,'connect',connect):
                    for action in (export.publish,export.reconcile):
                        with self.assertRaises(ValueError):
                            action(source,self.output,1,2)
                self.assertEqual(source.read_bytes(),before)
                self.assertEqual(self.output.read_bytes(),b'prior output')
                self.assertFalse(list(self.root.glob('.p22-report-*')))
                largest=max(seen,default=0)
                print('P22C-FIELD-BOUND:',table,column,type(value).__name__,
                      'largest Python text/blob field',largest,flush=True)
                self.assertLessEqual(largest,16)
                self.output.unlink()

    def test_snapshot_field_bounds_preserve_valid_utf8_utf16_and_row_limit(self):
        rows=[('SYN-%04d'%i,'pencil','complete',999) for i in range(1000)]
        expected={'policy_revision':2,'completed_quantities':{'paper':0,'pencil':999000,'folder':0},
                  'status_counts':{'complete':1000,'pending':0,'rejected':0}}
        outputs=[]
        for encoding in ('UTF-8','UTF-16le','UTF-16be'):
            with self.subTest(encoding=encoding):
                source=self.root/(encoding+'.sqlite')
                with closing(sqlite3.connect(source)) as db, db:
                    db.execute("PRAGMA encoding='"+encoding+"'")
                    self.assertEqual(db.execute('PRAGMA encoding').fetchone()[0],encoding)
                    db.execute('CREATE TABLE metadata(revision INTEGER)')
                    db.execute('INSERT INTO metadata VALUES (1)')
                    db.execute('CREATE TABLE records(record_id TEXT, category TEXT, state TEXT, quantity INTEGER)')
                    db.executemany('INSERT INTO records VALUES (?,?,?,?)',reversed(rows))
                before=source.read_bytes()
                self.assertEqual(export.snapshot(source,1),rows)
                output=self.root/(encoding+'.zip')
                self.assertEqual(export.publish(source,output,1,2),'PUBLISHED')
                raw,manifest=self.read_zip(output)
                self.assertEqual(json.loads(raw),expected)
                independent=json.dumps(rows,sort_keys=True,separators=(',',':')).encode('ascii')+b'\n'
                self.assertEqual(manifest['snapshot_sha256'],hashlib.sha256(independent).hexdigest())
                self.assertEqual(source.read_bytes(),before)
                outputs.append(output.read_bytes())
                self.assertEqual(export.reconcile(source,output,1,2),'COMMITTED')
                with closing(sqlite3.connect(source)) as db, db:
                    db.execute("INSERT INTO records VALUES ('SYN-1000','paper','pending',1)")
                with self.assertRaisesRegex(ValueError,'row count'):
                    export.publish(source,self.root/'overflow.zip',1,2)
                self.assertFalse((self.root/'overflow.zip').exists())
        self.assertEqual(len(set(outputs)),1)
