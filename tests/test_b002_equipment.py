import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
from src.b002_equipment import Equipment, can_checkout


class EquipmentTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / 'equipment.sqlite'
        self.e = Equipment.create(self.path, 10, 3)

    def test_available_exact_boundary_and_persistence(self):
        self.assertEqual(self.e.snapshot(), {'stock':10,'reserved':3,'available':7})
        self.assertEqual(self.e.reserve('SYN-R1', 7), 'RESERVED')
        self.assertEqual(self.e.reserve('SYN-R2', 1), 'INSUFFICIENT')
        self.assertEqual(Equipment(self.path).snapshot(), {'stock':10,'reserved':10,'available':0})

    def test_invalid_quantities_no_mutation(self):
        for q in (-1, 0, True, 1.5, '1', None, 2**63):
            self.assertFalse(can_checkout(10, 3, q))
            with self.assertRaises(ValueError):
                self.e.reserve('SYN-R1', q)
        self.assertFalse(can_checkout(2, 3, 1))
        self.assertFalse(can_checkout(-1, 0, 1))
        self.assertEqual(self.e.snapshot()['reserved'], 3)
        self.assertEqual(self.e.reconcile('SYN-R1')['classification'], 'NOT_FOUND_REVIEW')

    def test_duplicate_token_and_payload_conflict(self):
        self.assertEqual(self.e.reserve('SYN-R1', 2), 'RESERVED')
        self.assertEqual(self.e.reserve('SYN-R1', 2), 'RESERVED')
        with self.assertRaises(ValueError):
            self.e.reserve('SYN-R1', 3)
        self.assertEqual(self.e.snapshot()['reserved'], 5)

    def test_rejected_request_is_recorded_not_reserved(self):
        self.assertEqual(self.e.reserve('SYN-R1', 8), 'INSUFFICIENT')
        self.assertEqual(self.e.reconcile('SYN-R1'), {'classification':'COMMITTED','quantity':8,'result':'INSUFFICIENT','retry_allowed':False})
        self.assertEqual(self.e.snapshot()['reserved'], 3)

    def test_concurrent_variable_quantity(self):
        quantities = [3, 2, 1, 4, 2, 1, 3, 2]
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda x:self.e.reserve(f'SYN-R{x[0]}', x[1]), enumerate(quantities)))
        taken = sum(q for q, r in zip(quantities, results) if r == 'RESERVED')
        self.assertLessEqual(taken, 7)
        self.assertEqual(self.e.snapshot()['reserved'], 3+taken)
        self.assertIn('INSUFFICIENT', results)
        self.assertEqual(sum(self.e.reconcile(f'SYN-R{i}')['result']=='RESERVED' for i in range(8)), results.count('RESERVED'))

    def test_concurrent_same_token(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _:self.e.reserve('SYN-R1', 2), range(8)))
        self.assertEqual(results, ['RESERVED']*8)
        self.assertEqual(self.e.snapshot()['reserved'], 5)

    def test_rollback_after_inventory_before_ledger(self):
        with self.assertRaises(RuntimeError):
            self.e.reserve('SYN-R1', 4, fault='after_inventory')
        self.assertEqual(self.e.snapshot()['reserved'], 3)
        self.assertEqual(self.e.reconcile('SYN-R1')['classification'], 'NOT_FOUND_REVIEW')
        self.assertEqual(self.e.reserve('SYN-R2', 7), 'RESERVED')

    def test_rollback_after_ledger_before_commit(self):
        with self.assertRaises(RuntimeError):
            self.e.reserve('SYN-R1', 4, fault='before_commit')
        self.assertEqual(self.e.snapshot()['reserved'], 3)
        self.assertFalse(self.e.reconcile('SYN-R1')['retry_allowed'])
        self.assertEqual(self.e.reconcile('SYN-R1')['classification'], 'NOT_FOUND_REVIEW')

    def test_unknown_after_commit_readback(self):
        with self.assertRaises(RuntimeError):
            self.e.reserve('SYN-R1', 4, fault='after_commit')
        before = self.path.read_bytes()
        self.assertEqual(self.e.reconcile('SYN-R1'), {'classification':'COMMITTED','quantity':4,'result':'RESERVED','retry_allowed':False})
        self.assertEqual(self.e.snapshot()['reserved'], 7)
        self.assertEqual(self.path.read_bytes(), before)

    def test_missing_database_never_created_by_read_or_reserve(self):
        self.path.unlink()
        for operation in (self.e.snapshot, lambda:self.e.reconcile('SYN-R1'), lambda:self.e.reserve('SYN-R1',1)):
            with self.assertRaises(sqlite3.OperationalError):
                operation()
            self.assertFalse(self.path.exists())

    def test_initialization_is_exclusive(self):
        with self.assertRaises(FileExistsError):
            Equipment.create(self.path, 30)
        self.assertEqual(self.e.snapshot()['stock'], 10)
        with self.assertRaises(ValueError):
            Equipment.create(self.path.parent/'invalid.sqlite', 2, 3)
        self.assertFalse((self.path.parent/'invalid.sqlite').exists())

    def test_read_connection_rejects_mutation(self):
        with self.e._connect('ro') as db:
            with self.assertRaises(sqlite3.OperationalError):
                db.execute('UPDATE inventory SET reserved=0')
        db.close()
        self.assertEqual(self.e.snapshot()['reserved'], 3)

    def test_reproduce_old_readonly_pattern_then_compare(self):
        # Controlled legacy comparator, not a blind test or pre-training model.
        def legacy_connect(mode):
            return sqlite3.connect(self.path)
        self.path.unlink()
        with patch.object(self.e, '_connect', legacy_connect):
            with self.assertRaises(sqlite3.OperationalError):
                self.e.reconcile('SYN-R1')
        self.assertTrue(self.path.exists())
        self.path.unlink()
        with self.assertRaises(sqlite3.OperationalError):
            self.e.reconcile('SYN-R1')
        self.assertFalse(self.path.exists())
