"""Synthetic Developer/QA lab; no network, real data or deployment."""
import csv, hashlib, io, json, os, re, sqlite3, tempfile, unittest
from contextlib import closing
from pathlib import Path

class Store:
    def __init__(self, path, strict=True):
        self.path, self.strict = path, strict
        with closing(sqlite3.connect(path)) as db, db:
            db.executescript('CREATE TABLE meta(version TEXT, revision INTEGER); INSERT INTO meta VALUES (\'v1\',0); CREATE TABLE records(id TEXT PRIMARY KEY, score INTEGER, note TEXT NOT NULL); CREATE TABLE events(revision INTEGER PRIMARY KEY, count INTEGER);')

    def apply(self, version, revision, rows):
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            if self.strict and (type(revision) is not int or (version, revision) != db.execute('SELECT * FROM meta').fetchone()):
                raise ValueError('stale contract')
            if not 1 <= len(rows) <= 100:
                raise ValueError('batch bounds')
            seen = set()
            for row in rows:
                if set(row) != {'id', 'score', 'note'}:
                    raise ValueError('fields')
                key, score, note = row['id'], row['score'], row['note']
                if not isinstance(key, str) or not re.fullmatch(r'P[0-9]{3}', key):
                    raise ValueError('id')
                if self.strict and key in seen:
                    raise ValueError('duplicate')
                seen.add(key)
                if score is not None and (not isinstance(score, int) or not 0 <= score <= 100 or (self.strict and type(score) is not int)):
                    raise ValueError('score')
                if not isinstance(note, str) or len(note) > 200 or '\x00' in note:
                    raise ValueError('note')
                note.encode('utf-8')
                db.execute('INSERT INTO records VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET score=excluded.score,note=excluded.note', (key, score, note))
                if not self.strict:
                    db.commit()  # intentionally unsafe training comparator
            db.execute('UPDATE meta SET revision=revision+1')
            rev = db.execute('SELECT revision FROM meta').fetchone()[0]
            db.execute('INSERT INTO events VALUES(?,?)', (rev, len(rows)))
            return rev

    def export(self, hook=lambda: None):
        with closing(sqlite3.connect(self.path)) as db, db:
            if self.strict:
                db.execute('BEGIN')
            version, rev = db.execute('SELECT * FROM meta').fetchone()
            hook()
            rows = db.execute('SELECT * FROM records ORDER BY id').fetchall()
        out = io.StringIO(newline='')
        w = csv.writer(out, lineterminator='\r\n')
        w.writerow(['dictionary_version', 'revision', 'id', 'score_status', 'score', 'note_encoded'])
        for key, score, note in rows:
            w.writerow([version, rev, key, 'missing' if self.strict and score is None else 'observed', score if self.strict else score or 0, 'text:' + json.dumps(note, ensure_ascii=False) if self.strict else note])
        return out.getvalue().encode('utf-8')

class ResearchData(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / 'lab.sqlite'
        self.store = Store(self.path, os.environ.get('LAB_MODE') != 'unsafe')
        with closing(sqlite3.connect(self.path)) as db:
            db.execute('PRAGMA journal_mode=WAL')
    def row(self, key='P001', score=0, note=''):
        return dict(id=key, score=score, note=note)
    def state(self):
        with closing(sqlite3.connect(self.path)) as db:
            return tuple(db.execute('SELECT * FROM '+table+' ORDER BY 1').fetchall() for table in ('meta','records','events'))
    def reject(self, rows, version='v1', revision=0):
        before = self.state()
        with self.assertRaises(ValueError): self.store.apply(version, revision, rows)
        self.assertEqual(before, self.state())
    def parse(self, raw):
        return list(csv.DictReader(io.StringIO(raw.decode('utf-8'), newline=''), strict=True))
    def test_atomic_late_failure(self):
        self.reject([self.row(), self.row('P002', 101)])
    def test_exact_type(self):
        for value in (True, False, 1.5, '1', -1):
            with self.subTest(value=value): self.reject([self.row(score=value)])
    def test_duplicate_batch(self):
        self.reject([self.row(), self.row(score=9)])
    def test_schema_and_stale_revision(self):
        self.reject([self.row()], version='v2')
        self.store.apply('v1', 0, [self.row()])
        self.reject([self.row(score=9)])
    def test_missing_zero_and_text_roundtrip(self):
        note = '=1+1, "中文"\r\n下一行'
        self.store.apply('v1', 0, [self.row('P002', None, note), self.row()])
        a,b = self.parse(self.store.export())
        self.assertEqual((a['id'],a['score_status'],a['score']), ('P001','observed','0'))
        self.assertEqual((b['id'],b['score_status'],b['score']), ('P002','missing',''))
        self.assertEqual(json.loads(b['note_encoded'].removeprefix('text:')), note)
        self.assertEqual(json.loads(a['note_encoded'].removeprefix('text:')), '')
    def test_formula_prefixes(self):
        for i, note in enumerate(('=1+1','+1','-1','@x','\t=x','\r=x','\n=x','＝x','  =x','text:x')):
            self.store.apply('v1', i, [self.row(note=note)])
            field = self.parse(self.store.export())[0]['note_encoded']
            self.assertTrue(field.startswith('text:'))
            self.assertEqual(json.loads(field[5:]), note)
    def test_reproducible_and_revision(self):
        self.store.apply('v1', 0, [self.row('P002',100),self.row()])
        raw = self.store.export()
        self.assertEqual(hashlib.sha256(raw).digest(),hashlib.sha256(self.store.export()).digest())
        self.assertEqual([(r['id'],r['revision'],r['dictionary_version']) for r in self.parse(raw)], [('P001','1','v1'),('P002','1','v1')])
        self.assertEqual(self.state()[2],[(1,2)])
    def test_actual_interleaved_snapshot(self):
        self.store.apply('v1', 0, [self.row(score=10)])
        raw = self.store.export(lambda: self.store.apply('v1', 1, [self.row(score=20)]))
        self.assertEqual((self.parse(raw)[0]['revision'],self.parse(raw)[0]['score']), ('1','10'))
        self.assertEqual((self.parse(self.store.export())[0]['revision'],self.parse(self.store.export())[0]['score']), ('2','20'))
    def test_invalid_fields_and_bounds(self):
        for rows in ([], [self.row('bad')], [self.row(note='x'*201)], [dict(self.row(),extra=1)], [self.row()]*101):
            with self.subTest(rows=len(rows)): self.reject(rows)
    def test_update_replaces_not_duplicates(self):
        self.store.apply('v1',0,[self.row(score=1)])
        self.store.apply('v1',1,[self.row(score=2)])
        self.assertEqual(self.state(),([('v1',2)],[('P001',2,'')],[(1,1),(2,1)]))

if __name__ == '__main__': unittest.main(verbosity=2)
