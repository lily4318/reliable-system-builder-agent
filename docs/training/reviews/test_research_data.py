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

class NormalizationRelationLesson(unittest.TestCase):
    def test_normalize_independent_entities_and_temporal_facts(self):
        with sqlite3.connect(':memory:') as db:
            db.execute('PRAGMA foreign_keys=ON')
            db.executescript('''CREATE TABLE flat (person TEXT NOT NULL, protocol TEXT NOT NULL,
              label TEXT NOT NULL, unit TEXT NOT NULL, amount INTEGER NOT NULL,
              PRIMARY KEY(person,protocol));
              INSERT INTO flat VALUES ('P1','R1','Initial','lab-A',100),('P2','R1','Initial','lab-A',120);''')
            db.execute("UPDATE flat SET label='Revised' WHERE person='P1'")
            self.assertEqual(db.execute('SELECT COUNT(DISTINCT label) FROM flat').fetchone(), (2,))
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("INSERT INTO flat VALUES (NULL,'R2','New','lab-A',0)")
            db.execute("DELETE FROM flat WHERE protocol='R1'")
            self.assertEqual(db.execute('SELECT COUNT(*) FROM flat').fetchone(), (0,))
            db.executescript('''CREATE TABLE unit (id TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL);
              CREATE TABLE protocol (id TEXT PRIMARY KEY NOT NULL, label TEXT NOT NULL, unit_id TEXT NOT NULL REFERENCES unit(id));
              CREATE TABLE person (id TEXT PRIMARY KEY NOT NULL);
              CREATE TABLE participation (person_id TEXT NOT NULL REFERENCES person(id), protocol_id TEXT NOT NULL REFERENCES protocol(id),
                amount_at_event INTEGER NOT NULL, PRIMARY KEY(person_id,protocol_id));
              INSERT INTO unit VALUES ('U1','lab-A');
              INSERT INTO protocol VALUES ('R1','Initial','U1'),('R2','New','U1');
              INSERT INTO person VALUES ('P1'),('P2');
              INSERT INTO participation VALUES ('P1','R1',100),('P2','R1',120);''')
            sql='SELECT person_id,protocol_id,label,name,amount_at_event FROM participation JOIN protocol ON protocol_id=protocol.id JOIN unit ON unit_id=unit.id ORDER BY person_id'
            self.assertEqual(db.execute(sql).fetchall(), [('P1','R1','Initial','lab-A',100),('P2','R1','Initial','lab-A',120)])
            db.execute("UPDATE protocol SET label='Revised' WHERE id='R1'")
            db.execute("UPDATE unit SET name='lab-B' WHERE id='U1'")
            self.assertEqual(db.execute(sql).fetchall(), [('P1','R1','Revised','lab-B',100),('P2','R1','Revised','lab-B',120)])
            self.assertEqual(db.execute("SELECT count(*) FROM protocol WHERE id='R2'").fetchone(), (1,))
            db.execute("DELETE FROM participation WHERE protocol_id='R1'")
            self.assertEqual(db.execute('SELECT id FROM protocol ORDER BY id').fetchall(), [('R1',),('R2',)])

    def test_bcnf_lossless_does_not_preserve_every_dependency(self):
        with sqlite3.connect(':memory:') as db:
            db.execute('PRAGMA foreign_keys=ON')
            db.executescript('''CREATE TABLE mentor (id TEXT PRIMARY KEY NOT NULL, topic TEXT NOT NULL);
              CREATE TABLE assignment (learner TEXT NOT NULL, mentor_id TEXT NOT NULL REFERENCES mentor(id), PRIMARY KEY(learner,mentor_id));
              INSERT INTO mentor VALUES ('M1','T1'),('M2','T1');
              INSERT INTO assignment VALUES ('L1','M1'),('L2','M2');''')
            query='SELECT learner,topic,mentor_id FROM assignment JOIN mentor ON mentor_id=mentor.id ORDER BY learner,mentor_id'
            self.assertEqual(db.execute(query).fetchall(), [('L1','T1','M1'),('L2','T1','M2')])
            # Assumed rule: (learner, topic) determines mentor; mentor determines topic.
            db.execute("INSERT INTO assignment VALUES ('L1','M2')")
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
            self.assertEqual(db.execute('SELECT learner,topic FROM assignment JOIN mentor ON mentor_id=mentor.id GROUP BY learner,topic HAVING count(*)>1').fetchall(), [('L1','T1')])
            db.executescript('''CREATE TABLE assigned (learner TEXT NOT NULL,topic TEXT NOT NULL,mentor_id TEXT NOT NULL,PRIMARY KEY(learner,topic));
              INSERT INTO assigned VALUES ('L1','T1','M1');''')
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("INSERT INTO assigned VALUES ('L1','T1','M2')")
            # The retained 3NF relation still needs enforcement of mentor -> topic; not a complete schema.
            self.assertEqual(db.execute('SELECT * FROM assigned').fetchall(), [('L1','T1','M1')])

    def test_relationship_lifecycle_and_versioned_history(self):
        with sqlite3.connect(':memory:') as db:
            db.execute('PRAGMA foreign_keys=ON')
            db.executescript('''CREATE TABLE protocol_version (protocol TEXT NOT NULL, version INTEGER NOT NULL, label TEXT NOT NULL, PRIMARY KEY(protocol,version));
              CREATE TABLE run (id INTEGER PRIMARY KEY, protocol TEXT NOT NULL, version INTEGER NOT NULL,
                 FOREIGN KEY(protocol,version) REFERENCES protocol_version(protocol,version) ON DELETE NO ACTION);
              CREATE TABLE draft (id INTEGER PRIMARY KEY, run_id INTEGER NOT NULL REFERENCES run(id) ON DELETE CASCADE);
              CREATE TABLE optional_tag (id INTEGER PRIMARY KEY);
              CREATE TABLE annotation (id INTEGER PRIMARY KEY, tag_id INTEGER REFERENCES optional_tag(id) ON DELETE SET NULL);
              INSERT INTO protocol_version VALUES ('R1',1,'baseline'),('R1',2,'revision');
              INSERT INTO run VALUES (10,'R1',1),(11,'R1',2);
              INSERT INTO draft VALUES (1,10),(2,11);
              INSERT INTO optional_tag VALUES (1);
              INSERT INTO annotation VALUES (1,1);''')
            old='SELECT run.id,label FROM run JOIN protocol_version USING(protocol,version) ORDER BY run.id'
            self.assertEqual(db.execute(old).fetchall(), [(10,'baseline'),(11,'revision')])
            db.execute("INSERT INTO protocol_version VALUES ('R1',3,'later')")
            self.assertEqual(db.execute(old).fetchall(), [(10,'baseline'),(11,'revision')])
            db.commit()
            with self.assertRaises(sqlite3.IntegrityError), db:
                db.execute("DELETE FROM protocol_version WHERE protocol='R1' AND version=1")
            self.assertEqual(db.execute(old).fetchall(), [(10,'baseline'),(11,'revision')])
            with self.assertRaises(sqlite3.IntegrityError), db:
                db.execute("INSERT INTO run VALUES (12,'R1',99)")
            # Cascade only for the disposable draft relationship; no production deletion authorization.
            db.execute('DELETE FROM run WHERE id=11')
            self.assertEqual(db.execute('SELECT * FROM draft').fetchall(), [(1,10)])
            self.assertEqual(db.execute('SELECT * FROM protocol_version ORDER BY version').fetchall(), [('R1',1,'baseline'),('R1',2,'revision'),('R1',3,'later')])
            db.execute('DELETE FROM optional_tag WHERE id=1')
            self.assertEqual(db.execute('SELECT * FROM annotation').fetchall(), [(1,None)])
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])

class IndexDesignLesson(unittest.TestCase):
    @staticmethod
    def data(start, end):
        return [(i, i % 100, i, i % 37, 'x' * 80) for i in range(start, end)]

    @staticmethod
    def database(index):
        db = sqlite3.connect(':memory:')
        db.execute('CREATE TABLE event (id INTEGER PRIMARY KEY, cohort INTEGER NOT NULL, tick INTEGER NOT NULL, score INTEGER NOT NULL, payload TEXT NOT NULL)')
        db.executemany('INSERT INTO event VALUES (?,?,?,?,?)', IndexDesignLesson.data(0, 40000))
        if index:
            db.execute('CREATE INDEX idx_event ON event(' + index + ')')
        db.execute('ANALYZE')
        db.commit()
        return db

    def test_index_order_covering_and_equivalent_results(self):
        import statistics
        import time
        query = 'SELECT tick,id,score FROM event WHERE cohort=? AND tick>=? AND tick<? ORDER BY tick,id'
        args = (7, 10000, 30000)
        expected = [(i,i,i%37) for i in range(10007,30000,100)]
        for index in ('', 'cohort', 'tick,cohort', 'cohort,tick', 'cohort,tick,id,score'):
            with self.subTest(index=index):
                db = self.database(index)
                try:
                    plan = ' | '.join(r[3] for r in db.execute('EXPLAIN QUERY PLAN '+query,args))
                    self.assertEqual(db.execute(query,args).fetchall(), expected)
                    steps = [0]
                    def count_step():
                        steps[0] += 1
                        return 0
                    db.set_progress_handler(count_step,1)
                    try:
                        self.assertEqual(db.execute(query,args).fetchall(), expected)
                    finally:
                        db.set_progress_handler(None,0)
                    elapsed = []
                    for _ in range(5):
                        start = time.perf_counter()
                        for _ in range(30):
                            db.execute(query,args).fetchall()
                        elapsed.append((time.perf_counter()-start)*1000/30)
                    if not index:
                        self.assertIn('SCAN event',plan)
                        self.assertIn('TEMP B-TREE',plan)
                    elif index == 'cohort':
                        self.assertIn('cohort=?',plan)
                        self.assertIn('TEMP B-TREE',plan)
                    elif index == 'tick,cohort':
                        self.assertIn('tick>? AND tick<?',plan)
                        self.assertNotIn('cohort=? AND',plan)
                    else:
                        self.assertIn('cohort=? AND tick>? AND tick<?',plan)
                        self.assertNotIn('TEMP B-TREE',plan)
                    if index == 'cohort,tick,id,score':
                        self.assertIn('COVERING INDEX',plan)
                        not_covered = ' | '.join(r[3] for r in db.execute('EXPLAIN QUERY PLAN '+query.replace('tick,id,score','tick,id,score,payload',1),args))
                        self.assertNotIn('COVERING INDEX',not_covered)
                    print('INDEX-READ',repr(index), 'plan='+plan, 'vm_steps='+str(steps[0]), 'median_ms=%.6f'%statistics.median(elapsed),flush=True)
                finally:
                    db.close()

    def test_index_write_and_space_tradeoff(self):
        import statistics
        import time
        for index in ('', 'cohort', 'cohort,tick', 'cohort,tick,id,score'):
            insert_ms, update_ms, sizes = [], [], []
            for _ in range(5):
                db = self.database(index)
                try:
                    sizes.append(db.execute('PRAGMA page_count').fetchone()[0]*db.execute('PRAGMA page_size').fetchone()[0])
                    batch = self.data(40000,45000)
                    start = time.perf_counter()
                    with db:
                        db.executemany('INSERT INTO event VALUES (?,?,?,?,?)',batch)
                    insert_ms.append((time.perf_counter()-start)*1000)
                    start = time.perf_counter()
                    with db:
                        db.execute('UPDATE event SET score=score+1 WHERE id>=40000')
                    update_ms.append((time.perf_counter()-start)*1000)
                    self.assertEqual(db.execute('SELECT id,cohort,tick,score,payload FROM event WHERE id>=40000 ORDER BY id').fetchall(), [(i,c,t,s+1,p) for i,c,t,s,p in batch])
                    self.assertEqual(db.execute('SELECT COUNT(*) FROM event').fetchone(),(45000,))
                    self.assertEqual(db.execute('PRAGMA integrity_check').fetchone(),('ok',))
                finally:
                    db.close()
            print('INDEX-WRITE',repr(index),'bytes='+str(sizes),'insert_ms=%.6f'%statistics.median(insert_ms),'update_ms=%.6f'%statistics.median(update_ms),flush=True)

if __name__ == '__main__': unittest.main(verbosity=2)
