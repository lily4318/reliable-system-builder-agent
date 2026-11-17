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

class MissingValueLesson(unittest.TestCase):
    def test_missing_and_zero_must_not_be_conflated(self):
        with sqlite3.connect(':memory:') as db:
            db.execute('CREATE TABLE trial (id TEXT PRIMARY KEY NOT NULL, score INTEGER DEFAULT 0)')
            db.executemany('INSERT INTO trial(id,score) VALUES (?,?)', [('observed-zero',0),('unobserved',None),('observed-positive',12)])
            self.assertEqual(db.execute('SELECT id FROM trial WHERE score IS NULL').fetchall(), [('unobserved',)])
            self.assertEqual(db.execute('SELECT id FROM trial WHERE score = NULL').fetchall(), [])
            self.assertEqual(db.execute('SELECT id FROM trial WHERE score = 0').fetchall(), [('observed-zero',)])
            self.assertEqual(db.execute('SELECT COUNT(*), COUNT(score), AVG(score), AVG(COALESCE(score,0)) FROM trial').fetchone(), (3,2,6.0,4.0))
            self.assertEqual(db.execute('SELECT 10+20+NULL, NULLIF(0,0), COALESCE(NULL,0)').fetchone(), (None,None,0))
            db.execute("INSERT INTO trial(id) VALUES ('omitted')")
            self.assertEqual(db.execute("SELECT score FROM trial WHERE id='omitted'").fetchone(), (0,))
            self.assertEqual(db.execute("SELECT score FROM trial WHERE id='unobserved'").fetchone(), (None,))
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute('INSERT INTO trial(id,score) VALUES (NULL, 0)')
        # Transfer: missing vs zero for an unrelated operational count, not research data.
        with sqlite3.connect(':memory:') as db:
            db.execute('CREATE TABLE capacity (id TEXT PRIMARY KEY, slots INTEGER)')
            db.executemany('INSERT INTO capacity VALUES (?,?)', [('unknown',None),('full',0),('open',4)])
            self.assertEqual(db.execute('SELECT id FROM capacity WHERE slots=0').fetchall(), [('full',)])
            self.assertEqual(db.execute('SELECT id FROM capacity WHERE slots IS NULL').fetchall(), [('unknown',)])
            self.assertEqual(db.execute('SELECT COUNT(slots), SUM(slots) FROM capacity').fetchone(), (2,4))
            self.assertEqual(db.execute('SELECT COUNT(slots), SUM(slots) FROM capacity WHERE slots IS NULL').fetchone(), (0,None))

class IdentityAndTypeLesson(unittest.TestCase):
    def test_cross_database_identity_and_semantic_relation(self):
        source = sqlite3.connect(':memory:')
        target = sqlite3.connect(':memory:')
        for db in (source, target):
            db.execute('PRAGMA foreign_keys=ON')
            db.executescript('''CREATE TABLE item (local_id INTEGER PRIMARY KEY, stable_id TEXT NOT NULL UNIQUE, code TEXT NOT NULL UNIQUE);
                CREATE TABLE detail (id INTEGER PRIMARY KEY, item_id INTEGER NOT NULL REFERENCES item(local_id));''')
        source.execute('INSERT INTO item VALUES (1,?,?)', ('source-A','001'))
        source.execute('INSERT INTO detail VALUES (7,1)')
        target.execute('INSERT INTO item VALUES (1,?,?)', ('other-B','002'))
        target.execute('INSERT INTO item VALUES (2,?,?)', ('source-A','001'))
        # Deliberately unsafe transfer: an existing number satisfies FK but refers to the wrong item.
        target.execute('INSERT INTO detail VALUES (7,1)')
        self.assertEqual(target.execute('PRAGMA foreign_key_check').fetchall(), [])
        self.assertEqual(target.execute('SELECT stable_id FROM detail JOIN item ON item_id=local_id').fetchone(), ('other-B',))
        expected = source.execute('SELECT stable_id FROM detail JOIN item ON item_id=local_id WHERE detail.id=7').fetchone()
        self.assertNotEqual(expected, ('other-B',))
        # Correctly translate the source identity to the destination local key.
        target.execute('UPDATE detail SET item_id=(SELECT local_id FROM item WHERE stable_id=?) WHERE id=7', expected)
        self.assertEqual(target.execute('SELECT stable_id FROM detail JOIN item ON item_id=local_id').fetchone(), ('source-A',))
        target.execute('UPDATE item SET code=? WHERE stable_id=?', ('003','source-A'))
        self.assertEqual(target.execute('SELECT code FROM detail JOIN item ON item_id=local_id').fetchone(), ('003',))
        target.commit()
        before = target.execute('SELECT * FROM item ORDER BY local_id').fetchall()
        for row in ((3,'source-A','004'),(3,'new-C','003')):
            with self.subTest(duplicate=row), self.assertRaises(sqlite3.IntegrityError), target:
                target.execute('INSERT INTO item VALUES (?,?,?)', row)
        self.assertEqual(target.execute('SELECT * FROM item ORDER BY local_id').fetchall(), before)
        with self.assertRaises(sqlite3.IntegrityError), target:
            target.execute('INSERT INTO detail VALUES (8,999)')
        self.assertEqual(target.execute('PRAGMA foreign_key_check').fetchall(), [])
        source.close()
        target.close()

    def test_identifiers_exact_amounts_and_half_open_time_window(self):
        with sqlite3.connect(':memory:') as db:
            db.executescript('''CREATE TABLE legacy (code INTEGER, amount REAL);
              CREATE TABLE observation (code TEXT PRIMARY KEY NOT NULL,
                amount_minor INTEGER NOT NULL CHECK(amount_minor BETWEEN 0 AND 999999),
                occurred_utc TEXT NOT NULL) STRICT;''')
            db.executemany('INSERT INTO legacy VALUES (?,?)', [('001',0.1),('1',0.2)])
            self.assertEqual(db.execute('SELECT COUNT(DISTINCT code) FROM legacy').fetchone(), (1,))
            self.assertNotEqual(db.execute('SELECT SUM(amount) FROM legacy').fetchone()[0], 0.3)
            db.executemany('INSERT INTO observation VALUES (?,?,?)', [
                ('001',10,'2026-01-01T00:00:00.000Z'),
                ('1',20,'2026-01-01T23:59:59.999Z'),
                ('002',40,'2026-01-02T00:00:00.000Z')])
            self.assertEqual(db.execute('SELECT COUNT(DISTINCT code) FROM observation').fetchone(), (3,))
            start, end = '2026-01-01T00:00:00.000Z','2026-01-02T00:00:00.000Z'
            self.assertEqual(db.execute('SELECT SUM(amount_minor) FROM observation WHERE occurred_utc BETWEEN ? AND ?', (start,end)).fetchone(), (70,))
            self.assertEqual(db.execute('SELECT code,amount_minor FROM observation WHERE occurred_utc>=? AND occurred_utc<? ORDER BY occurred_utc',(start,end)).fetchall(), [('001',10),('1',20)])
            self.assertEqual(db.execute('SELECT SUM(amount_minor) FROM observation WHERE occurred_utc>=? AND occurred_utc<?',(start,end)).fetchone(), (30,))
            db.commit()
            before = db.execute('SELECT * FROM observation ORDER BY code').fetchall()
            for amount in (-1,1000000,10.5,None):
                with self.subTest(amount=amount), self.assertRaises(sqlite3.IntegrityError), db:
                    db.execute('INSERT INTO observation VALUES (?,?,?)', ('bad',amount,start))
            self.assertEqual(db.execute('SELECT * FROM observation ORDER BY code').fetchall(), before)

if __name__ == '__main__': unittest.main(verbosity=2)
