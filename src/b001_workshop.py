"""Local synthetic workshop slice. No network, real enrollment or provider calls."""
import re
import sqlite3
from contextlib import closing
from pathlib import Path


def _token(value):
    if not isinstance(value, str) or not re.fullmatch(r'SYN-[A-Z0-9-]{1,40}', value):
        raise ValueError('synthetic token required')
    return value


def enrollment_status(capacity, enrolled, applicant):
    if type(capacity) is not int or capacity < 0 or not isinstance(enrolled, (list, tuple)):
        return 'INVALID'
    try:
        _token(applicant)
        for person in enrolled:
            _token(person)
    except ValueError:
        return 'INVALID'
    if applicant in enrolled:
        return 'ALREADY'
    return 'ACCEPT' if len(set(enrolled)) < capacity else 'WAITLIST'


class Workshop:
    def __init__(self, path, capacity):
        if type(capacity) is not int or capacity < 0:
            raise ValueError('invalid capacity')
        self.path = path
        with closing(self._connect()) as db, db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY CHECK(id=1), capacity INTEGER NOT NULL CHECK(capacity>=0))')
            db.execute('CREATE TABLE IF NOT EXISTS enrollment (seq INTEGER PRIMARY KEY, applicant TEXT UNIQUE NOT NULL, status TEXT NOT NULL CHECK(status IN (\'ACCEPT\',\'WAITLIST\')))')
            db.execute('CREATE TABLE IF NOT EXISTS request (token TEXT PRIMARY KEY, applicant TEXT NOT NULL, result TEXT NOT NULL)')
            db.execute('INSERT OR IGNORE INTO config VALUES (1,?)', (capacity,))
            if db.execute('SELECT capacity FROM config').fetchone()[0] != capacity:
                raise ValueError('capacity change requires explicit migration')

    def _connect(self):
        return sqlite3.connect(self.path, timeout=5)

    def _read_connect(self):
        return sqlite3.connect(Path(self.path).resolve().as_uri() + "?mode=ro", uri=True, timeout=5)

    def register(self, applicant, request_id, *, fault=None):
        _token(applicant)
        _token(request_id)
        if fault not in (None, 'before_commit', 'after_commit'):
            raise ValueError('invalid fault')
        with closing(self._connect()) as db, db:
            db.execute('BEGIN IMMEDIATE')
            prior = db.execute('SELECT applicant,result FROM request WHERE token=?', (request_id,)).fetchone()
            if prior:
                if prior[0] != applicant:
                    raise ValueError('request ID conflict')
                return prior[1]
            existing = db.execute('SELECT status FROM enrollment WHERE applicant=?', (applicant,)).fetchone()
            if existing:
                result = 'ALREADY'
            else:
                capacity = db.execute('SELECT capacity FROM config').fetchone()[0]
                enrolled = [r[0] for r in db.execute("SELECT applicant FROM enrollment WHERE status='ACCEPT'")]
                result = enrollment_status(capacity, enrolled, applicant)
                db.execute('INSERT INTO enrollment(applicant,status) VALUES (?,?)', (applicant, result))
            db.execute('INSERT INTO request VALUES (?,?,?)', (request_id, applicant, result))
            if fault == 'before_commit':
                raise RuntimeError('synthetic failure before commit')
            db.commit()
            if fault == 'after_commit':
                raise RuntimeError('synthetic response lost after commit')
            return result

    def reconcile(self, request_id):
        _token(request_id)
        with closing(self._read_connect()) as db:
            db.execute('PRAGMA query_only=ON')
            row = db.execute('SELECT applicant,result FROM request WHERE token=?', (request_id,)).fetchone()
        return {'classification': 'COMMITTED' if row else 'NOT_FOUND_REVIEW',
                'result': row[1] if row else None, 'retry_allowed': False}

    def snapshot(self):
        with closing(self._read_connect()) as db:
            db.execute('PRAGMA query_only=ON')
            return db.execute('SELECT applicant,status FROM enrollment ORDER BY seq').fetchall()
