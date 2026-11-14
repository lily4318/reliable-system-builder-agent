import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from src.b001_workshop import Workshop, enrollment_status


class WorkshopTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / 'synthetic.sqlite'
        self.w = Workshop(self.path, 1)

    def test_capacity_waitlist_fifo_and_persistence(self):
        self.assertEqual(self.w.register('SYN-A', 'SYN-R1'), 'ACCEPT')
        self.assertEqual(self.w.register('SYN-B', 'SYN-R2'), 'WAITLIST')
        self.assertEqual(self.w.register('SYN-C', 'SYN-R3'), 'WAITLIST')
        self.assertEqual(Workshop(self.path, 1).snapshot(), [('SYN-A','ACCEPT'),('SYN-B','WAITLIST'),('SYN-C','WAITLIST')])

    def test_duplicate_and_request_replay(self):
        self.assertEqual(self.w.register('SYN-A', 'SYN-R1'), 'ACCEPT')
        self.assertEqual(self.w.register('SYN-A', 'SYN-R1'), 'ACCEPT')
        self.assertEqual(self.w.register('SYN-A', 'SYN-R2'), 'ALREADY')
        with self.assertRaises(ValueError):
            self.w.register('SYN-B', 'SYN-R1')
        self.assertEqual(len(self.w.snapshot()), 1)

    def test_waitlisted_duplicate(self):
        self.w.register('SYN-A', 'SYN-R1')
        self.w.register('SYN-B', 'SYN-R2')
        self.assertEqual(self.w.register('SYN-B', 'SYN-R3'), 'ALREADY')
        self.assertEqual(len(self.w.snapshot()), 2)

    def test_unknown_after_commit_read_only(self):
        with self.assertRaises(RuntimeError):
            self.w.register('SYN-A', 'SYN-R1', fault='after_commit')
        before = self.w.snapshot()
        self.assertEqual(self.w.reconcile('SYN-R1'), {'classification':'COMMITTED','result':'ACCEPT','retry_allowed':False})
        self.assertEqual(self.w.snapshot(), before)

    def test_failure_before_commit_rolls_back(self):
        with self.assertRaises(RuntimeError):
            self.w.register('SYN-A', 'SYN-R1', fault='before_commit')
        self.assertEqual(self.w.snapshot(), [])
        self.assertEqual(self.w.reconcile('SYN-R1'), {'classification':'NOT_FOUND_REVIEW','result':None,'retry_allowed':False})
        self.assertEqual(self.w.register('SYN-B','SYN-R2'), 'ACCEPT')

    def test_concurrent_last_seat(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda i:self.w.register(f'SYN-A{i}',f'SYN-R{i}'), range(8)))
        self.assertEqual(results.count('ACCEPT'), 1)
        self.assertEqual(results.count('WAITLIST'), 7)

    def test_concurrent_duplicate(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda i:self.w.register('SYN-A',f'SYN-R{i}'), range(8)))
        self.assertEqual(results.count('ACCEPT'), 1)
        self.assertEqual(results.count('ALREADY'), 7)
        self.assertEqual(len(self.w.snapshot()), 1)

    def test_input_boundaries(self):
        for capacity in (-1, True, 1.5):
            self.assertEqual(enrollment_status(capacity, [], 'SYN-A'), 'INVALID')
        self.assertEqual(enrollment_status(0, [], 'SYN-A'), 'WAITLIST')
        self.assertEqual(enrollment_status(1, [], 'SYN-A'), 'ACCEPT')
        self.assertEqual(enrollment_status(1, ['SYN-B'], 'SYN-A'), 'WAITLIST')
        with self.assertRaises(ValueError):
            self.w.register('not-synthetic','SYN-R1')
        with self.assertRaises(ValueError):
            Workshop(self.path, 2)
        self.assertEqual(self.w.snapshot(), [])

    def test_readonly_reconcile_missing_database_does_not_create_file(self):
        import sqlite3
        self.path.unlink()
        with self.assertRaises(sqlite3.OperationalError):
            self.w.reconcile('SYN-R1')
        self.assertFalse(self.path.exists())
