"""Synthetic local equipment reservations; no remote or production operations."""
import re
import sqlite3
from contextlib import closing
from pathlib import Path

MAX_INTEGER = 2**63 - 1


def _count(value):
    return type(value) is int and 0 <= value <= MAX_INTEGER


def can_checkout(stock, reserved, quantity):
    return (all(_count(v) for v in (stock, reserved, quantity))
            and reserved <= stock and 0 < quantity <= stock - reserved)


def _token(value):
    if not isinstance(value, str) or not re.fullmatch(r'SYN-[A-Z0-9-]{1,40}', value):
        raise ValueError('synthetic token required')
    return value


class Equipment:
    def __init__(self, path):
        self.path = Path(path).resolve()

    @classmethod
    def create(cls, path, stock, reserved=0):
        if not _count(stock) or not _count(reserved) or reserved > stock:
            raise ValueError('invalid initial inventory')
        obj = cls(path)
        # Exclusive creation: never silently initialize an existing inventory.
        with obj.path.open('xb'):
            pass
        try:
            with closing(obj._connect('rw')) as db, db:
                db.execute('BEGIN IMMEDIATE')
                db.execute('CREATE TABLE inventory (id INTEGER PRIMARY KEY CHECK(id=1), stock INTEGER NOT NULL CHECK(stock>=0), reserved INTEGER NOT NULL CHECK(reserved>=0 AND reserved<=stock))')
                db.execute('CREATE TABLE requests (token TEXT PRIMARY KEY, quantity INTEGER NOT NULL CHECK(quantity>0), result TEXT NOT NULL CHECK(result IN (\'RESERVED\',\'INSUFFICIENT\')))')
                db.execute('INSERT INTO inventory VALUES (1,?,?)', (stock, reserved))
        except Exception:
            # Keep failed creation for manual inspection; do not blindly delete.
            raise
        return obj

    def _connect(self, mode):
        return sqlite3.connect(self.path.as_uri() + '?mode=' + mode, uri=True, timeout=5)

    def snapshot(self):
        with closing(self._connect('ro')) as db:
            db.execute('PRAGMA query_only=ON')
            stock, reserved = db.execute('SELECT stock,reserved FROM inventory WHERE id=1').fetchone()
            return {'stock':stock, 'reserved':reserved, 'available':stock-reserved}

    def reserve(self, request_id, quantity, *, fault=None):
        _token(request_id)
        if not _count(quantity) or quantity == 0:
            raise ValueError('invalid quantity')
        if fault not in (None, 'after_inventory', 'before_commit', 'after_commit'):
            raise ValueError('invalid fault')
        with closing(self._connect('rw')) as db, db:
            db.execute('BEGIN IMMEDIATE')
            prior = db.execute('SELECT quantity,result FROM requests WHERE token=?', (request_id,)).fetchone()
            if prior:
                if prior[0] != quantity:
                    raise ValueError('request ID conflict')
                return prior[1]
            stock, reserved = db.execute('SELECT stock,reserved FROM inventory WHERE id=1').fetchone()
            result = 'INSUFFICIENT'
            if can_checkout(stock, reserved, quantity):
                changed = db.execute('UPDATE inventory SET reserved=reserved+? WHERE id=1 AND stock-reserved>=?', (quantity, quantity)).rowcount
                if changed != 1:
                    raise RuntimeError('inventory invariant changed')
                result = 'RESERVED'
            if fault == 'after_inventory':
                raise RuntimeError('synthetic failure after inventory update')
            db.execute('INSERT INTO requests VALUES (?,?,?)', (request_id, quantity, result))
            if fault == 'before_commit':
                raise RuntimeError('synthetic failure before commit')
            db.commit()
            if fault == 'after_commit':
                raise RuntimeError('synthetic response lost after commit')
            return result

    def reconcile(self, request_id):
        _token(request_id)
        with closing(self._connect('ro')) as db:
            db.execute('PRAGMA query_only=ON')
            row = db.execute('SELECT quantity,result FROM requests WHERE token=?', (request_id,)).fetchone()
        return {'classification':'COMMITTED' if row else 'NOT_FOUND_REVIEW',
                'quantity':row[0] if row else None, 'result':row[1] if row else None,
                'retry_allowed':False}
