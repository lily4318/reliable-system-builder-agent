"""P2-2b independent expected values, real file publication and recovery."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from src import p22_file_intake as intake, team_workbench as wb, workbench_learning as learn


HEADER = b'record_id,category,quantity\n'
DATA = HEADER + b'R0001,paper,3\nR0002,folder,7\nR0003,paper,2\n'


class FileIntakeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / 'input.csv'
        self.source.write_bytes(DATA)
        self.output = self.root / 'result.json'

    def test_exact_oracle_and_repeatability(self):
        expected_result = {'row_count': 3, 'totals': {'folder': 7, 'paper': 5, 'pencil': 0}}
        expected_result_bytes = b'{"row_count":3,"totals":{"folder":7,"paper":5,"pencil":0}}\n'
        self.assertEqual(intake.publish(self.source, self.output), 'PUBLISHED')
        original = self.output.read_bytes()
        expected = {'schema_version': 1, 'input_sha256': hashlib.sha256(DATA).hexdigest(),
                    'result_sha256': hashlib.sha256(expected_result_bytes).hexdigest(), 'result': expected_result}
        self.assertEqual(json.loads(original), expected)
        other = self.root / 'again.json'
        intake.publish(self.source, other)
        self.assertEqual(other.read_bytes(), original)
        self.assertEqual(self.source.read_bytes(), DATA)
        self.assertEqual(intake.reconcile(self.source, self.output), 'COMMITTED')
        with self.assertRaises(FileExistsError):
            intake.publish(self.source, self.output)
        self.assertEqual(self.output.read_bytes(), original)

    def test_invalid_input_never_publishes(self):
        cases = [b'', HEADER, b'category,record_id,quantity\nR0001,paper,2\n',
                 HEADER+b'R0001,paper,2\nR0001,folder,3\n',
                 HEADER+b'R0001,unknown,2\n', HEADER+b'R0001,paper,-1\n',
                 HEADER+b'R0001,paper,0\n', HEADER+b'R0001,paper,01\n',
                 HEADER+b'R0001,paper,1000\n', HEADER+b'R0001,paper,1,extra\n',
                 HEADER+b'R0001,"paper,2\n', HEADER+b'R0001,paper,\xff\n',
                 HEADER+b'x'*intake.MAX_BYTES,
                 HEADER+b''.join(('R%04d,paper,1\n'%i).encode() for i in range(1001))]
        for data in cases:
            with self.subTest(data=data[:80]):
                self.source.write_bytes(data)
                with self.assertRaises(ValueError):
                    intake.publish(self.source, self.output)
                self.assertFalse(self.output.exists())
                self.assertEqual(self.source.read_bytes(), data)
        self.assertFalse(list(self.root.glob('.p22-intake-*')))

    def test_readonly_conflicts_and_prepublication_fault(self):
        self.assertEqual(intake.reconcile(self.source, self.output), 'NOT_OBSERVED')
        self.assertFalse(self.output.exists())
        with self.assertRaises(RuntimeError):
            intake.publish(self.source, self.output, fault_before_link=True)
        self.assertFalse(self.output.exists())
        self.assertFalse(list(self.root.glob('.p22-intake-*')))
        intake.publish(self.source, self.output)
        old = self.output.read_bytes()
        self.source.write_bytes(DATA.replace(b'paper,3', b'paper,4'))
        self.assertEqual(intake.reconcile(self.source, self.output), 'CONFLICT')
        self.assertEqual(self.output.read_bytes(), old)
        self.source.write_bytes(DATA)
        self.output.write_bytes(old+b'corruption')
        self.assertEqual(intake.reconcile(self.source, self.output), 'CONFLICT')
        self.assertEqual(self.output.read_bytes(), old+b'corruption')

    def test_concurrent_publish_no_overwrite(self):
        def attempt(_):
            try:
                return intake.publish(self.source, self.output)
            except FileExistsError:
                return 'EXISTS'
        with ThreadPoolExecutor(max_workers=8) as pool:
            statuses = list(pool.map(attempt, range(8)))
        self.assertEqual(statuses.count('PUBLISHED'), 1)
        self.assertEqual(statuses.count('EXISTS'), 7)
        self.assertEqual(intake.reconcile(self.source, self.output), 'COMMITTED')
        self.assertFalse(list(self.root.glob('.p22-intake-*')))

    def test_real_process_exit_after_publication(self):
        child = subprocess.run([sys.executable, '-c',
            'import os,sys; from src.p22_file_intake import publish; publish(sys.argv[1],sys.argv[2]); os._exit(23)',
            str(self.source), str(self.output)], capture_output=True, timeout=20)
        self.assertEqual(child.returncode, 23)
        before = self.output.read_bytes()
        result = subprocess.run([sys.executable, '-m', 'src.p22_file_intake', 'reconcile',
            '--input', str(self.source), '--output', str(self.output)],
            capture_output=True, text=True, check=True, timeout=20)
        self.assertEqual(json.loads(result.stdout), {'status': 'COMMITTED'})
        self.assertEqual(self.output.read_bytes(), before)
        print('P22B-FILE-RECOVERY: process exit after publication; exact bundle reconciled read-only', flush=True)

    def test_prior_case_scope_and_handoffs(self):
        workspace = wb.initialize(self.root/'work', 'Synthetic CSV intake')
        learn.setup(workspace, include_training_cases=True)
        for skill, body in [
            ('project-intake', 'Synthetic record IDs and office supply quantities, local CSV only.'),
            ('requirements-spec', 'Strict schema, unique IDs, deterministic totals, no overwrite, read-only reconciliation.'),
            ('architecture-design', 'Bounded UTF-8 CSV -> complete validation -> canonical JSON bundle -> exclusive publication. No SQLite workflow state.'),
            ('task-planning', 'Validate fixed oracle plus malformed data, concurrency and process exit; no external destination.')]:
            wb.handoff(workspace, skill, body, 'P22b synthetic fixture')
        query = 'atomic transaction artifact receipt interruption idempotency negative decisions browser origin CLI migration'
        ctx = learn.task_context(workspace, 'implement-feature', 'P22-FILE', query, limit=10)
        self.assertEqual(ctx['status'], 'READY_TO_REVIEW_INPUTS')
        hits = {row['topic']: row for row in ctx['memory']}
        for key, decision, evidence in [
            ('P21-CASE-005', 'applied', 'Transfer principle only: output and receipt share one immutable bundle; exclusive link and process-exit test, not SQLite transaction.'),
            ('P21-CASE-003', 'not_applicable', 'No actor-scoped mutation or denied decision ledger; invalid input produces no output.'),
            ('P21-CASE-006', 'not_applicable', 'No browser form, Origin or legacy database migration.')]:
            self.assertIn(key, hits)
            learn.cite(workspace, 'implement-feature', 'P22-FILE', 'p22b-1', query,
                       hits[key]['id'], decision, evidence, limit=10)
        self.assertEqual(intake.publish(self.source, self.output), 'PUBLISHED')
        self.assertEqual(intake.reconcile(self.source, self.output), 'COMMITTED')
        wb.handoff(workspace, 'implement-feature', 'src/p22_file_intake.py: bounded parse, canonical bundle, exclusive link', 'P22b implementation')
        wb.handoff(workspace, 'test-and-acceptance', 'Exact external-to-implementation oracle, malformed inputs, concurrency and subprocess exit', 'P22b functional tests')
        wb.handoff(workspace, 'security-review', 'Trusted local directory only; strict inputs; no replacement or remote writes', 'P22b security bounds')
        wb.handoff(workspace, 'deployment', 'Local synthetic CLI; no external deployment', 'P22b scope')
        learn.feedback(workspace, 'P22-FILE', 'p22b-1', 'p22b-bundle', 'test_fix',
                       'file bundle publication', 'One deterministic bundle avoids split output and receipt.',
                       'Exact oracle, exclusive publication and recovery tests; candidate only')
        history = learn.history(workspace, 'P22-FILE')
        self.assertEqual(len(history['events']), 1)
        self.assertEqual({r['topic']:r['decision'] for r in history['uses']},
                         {'P21-CASE-005':'applied', 'P21-CASE-003':'not_applicable', 'P21-CASE-006':'not_applicable'})
        self.assertEqual(wb.context(workspace, 'deployment')['status'], 'READY_TO_REVIEW_INPUTS')
        print('P22B-LEARNING: 3 cases considered; 1 principle transferred; 2 not applicable; feedback candidate', flush=True)
