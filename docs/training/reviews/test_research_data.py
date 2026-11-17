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

class StagedImportLesson(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''CREATE TABLE target (code TEXT PRIMARY KEY NOT NULL, score INTEGER NOT NULL CHECK(score BETWEEN 0 AND 100), note TEXT NOT NULL) STRICT;
          INSERT INTO target VALUES ('EXIST',50,'old');
          CREATE TABLE manifest (batch TEXT PRIMARY KEY, digest TEXT NOT NULL, status TEXT NOT NULL);
          CREATE TABLE stage (batch TEXT REFERENCES manifest(batch), n INTEGER, code TEXT, score TEXT, note TEXT, PRIMARY KEY(batch,n));
          CREATE TABLE rejection (batch TEXT, n INTEGER, reason TEXT, PRIMARY KEY(batch,n,reason), FOREIGN KEY(batch,n) REFERENCES stage(batch,n));
          CREATE TABLE receipt (batch TEXT PRIMARY KEY REFERENCES manifest(batch), rows INTEGER NOT NULL);''')

    def stage(self, batch, raw):
        if len(raw) > 65536:
            raise ValueError('file size')
        reader = csv.reader(io.StringIO(raw.decode('utf-8-sig'), newline=''), strict=True)
        if next(reader, None) != ['code','score','note']:
            raise ValueError('header')
        rows = list(reader)
        if not 1 <= len(rows) <= 100 or any(len(r) != 3 for r in rows):
            raise ValueError('shape')
        with self.db:
            self.db.execute('INSERT INTO manifest VALUES (?,?,?)',(batch,hashlib.sha256(raw).hexdigest(),'STAGED'))
            self.db.executemany('INSERT INTO stage VALUES (?,?,?,?,?)',[(batch,n,*r) for n,r in enumerate(rows,1)])

    def errors(self, batch):
        rows = self.db.execute('SELECT n,code,score,note FROM stage WHERE batch=? ORDER BY n',(batch,)).fetchall()
        counts = {c: sum(r[1]==c for r in rows) for _,c,_,_ in rows}
        prior = {r[0] for r in self.db.execute('SELECT code FROM target')}
        errors = []
        for n,c,s,note in rows:
            for bad,reason in [(not re.fullmatch(r'[A-Z0-9]{1,12}',c),'CODE'),(not re.fullmatch(r'(?:0|[1-9][0-9]?|100)',s),'SCORE'),(len(note)>200 or chr(0) in note,'NOTE'),(counts[c]>1,'DUPLICATE'),(c in prior,'EXISTS')]:
                if bad:
                    errors.append((batch,n,reason))
        return sorted(errors)

    def promote(self, batch):
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            if self.db.execute('SELECT status FROM manifest WHERE batch=?',(batch,)).fetchone() != ('STAGED',):
                raise ValueError('not staged')
            errors = self.errors(batch)
            if errors:
                self.db.executemany('INSERT INTO rejection VALUES (?,?,?)',errors)
                self.db.execute("UPDATE manifest SET status='REJECTED' WHERE batch=?",(batch,))
                return False
            rows = self.db.execute('SELECT code,CAST(score AS INTEGER),note FROM stage WHERE batch=? ORDER BY n',(batch,)).fetchall()
            before = self.db.execute('SELECT * FROM target ORDER BY code').fetchall()
            self.db.executemany('INSERT INTO target VALUES (?,?,?)',rows)
            if self.db.execute('SELECT * FROM target ORDER BY code').fetchall() != sorted(before+rows):
                raise ValueError('reconciliation')
            self.db.execute('INSERT INTO receipt VALUES (?,?)',(batch,len(rows)))
            self.db.execute("UPDATE manifest SET status='COMMITTED' WHERE batch=?",(batch,))
        return True

    def snapshot(self):
        return tuple(self.db.execute('SELECT * FROM '+t+' ORDER BY 1,2').fetchall() for t in ('target','manifest','stage','rejection','receipt'))

    def test_lossless_staging_and_complete_rejection_report(self):
        raw = 'code,score,note\r\n001,9,"中文,引號"\r\nA2,abc,bad\r\nA2,101,bad\r\nEXIST,20,collision\r\n'.encode('utf-8')
        self.stage('bad',raw)
        self.assertEqual(self.db.execute('SELECT code,score,note FROM stage WHERE batch=? ORDER BY n',('bad',)).fetchall(), [('001','9','中文,引號'),('A2','abc','bad'),('A2','101','bad'),('EXIST','20','collision')])
        self.assertFalse(self.promote('bad'))
        self.assertEqual(self.db.execute('SELECT n,reason FROM rejection ORDER BY n,reason').fetchall(),[(2,'DUPLICATE'),(2,'SCORE'),(3,'DUPLICATE'),(3,'SCORE'),(4,'EXISTS')])
        self.assertEqual(self.db.execute('SELECT * FROM target').fetchall(),[('EXIST',50,'old')])
        self.assertEqual(self.db.execute('SELECT * FROM receipt').fetchall(),[])
        self.assertEqual(self.db.execute('SELECT digest,status FROM manifest').fetchone(),(hashlib.sha256(raw).hexdigest(),'REJECTED'))
        before = self.snapshot()
        for raw in (b'code,score,note\n001,1,\xff', b'score,code,note\n1,001,x', b'code,score,note\n001,1', b'code,score,note\n001,1,"unclosed'):
            with self.subTest(raw=raw), self.assertRaises((ValueError,csv.Error)):
                self.stage('invalid',raw)
            self.assertEqual(self.snapshot(),before)

    def test_late_receipt_failure_rolls_back_promotion(self):
        self.stage('good','code,score,note\n001,0,"多行\n內容"\n002,100,ok\n'.encode('utf-8-sig'))
        before = self.snapshot()
        self.db.execute("CREATE TRIGGER block_receipt BEFORE INSERT ON receipt BEGIN SELECT RAISE(ABORT,'receipt failure'); END")
        with self.assertRaisesRegex(sqlite3.IntegrityError,'receipt failure'):
            self.promote('good')
        self.assertEqual(self.snapshot(),before)
        self.db.execute('DROP TRIGGER block_receipt')
        self.assertTrue(self.promote('good'))
        self.assertEqual(self.db.execute('SELECT * FROM target ORDER BY code').fetchall(),[('001',0,'多行\n內容'),('002',100,'ok'),('EXIST',50,'old')])
        self.assertEqual(self.db.execute('SELECT * FROM receipt').fetchall(),[('good',2)])
        after = self.snapshot()
        with self.assertRaises(ValueError):
            self.promote('good')
        self.assertEqual(self.snapshot(),after)

    def test_equal_count_and_sum_can_hide_corruption(self):
        self.stage('swap',b'code,score,note\nA,10,x\nB,20,y\n')
        before = self.snapshot()
        self.db.execute("CREATE TRIGGER swap_score AFTER INSERT ON target WHEN NEW.code IN ('A','B') BEGIN UPDATE target SET score=30-NEW.score WHERE code=NEW.code; END")
        self.db.execute('SAVEPOINT unsafe_preview')
        self.db.execute("INSERT INTO target VALUES ('A',10,'x'),('B',20,'y')")
        self.assertEqual(self.db.execute("SELECT COUNT(*),SUM(score) FROM target WHERE code IN ('A','B')").fetchone(),(2,30))
        self.assertEqual(self.db.execute("SELECT code,score FROM target WHERE code IN ('A','B') ORDER BY code").fetchall(),[('A',20),('B',10)])
        self.db.execute('ROLLBACK TO unsafe_preview')
        self.db.execute('RELEASE unsafe_preview')
        self.assertEqual(self.snapshot(),before)
        with self.assertRaisesRegex(ValueError,'reconciliation'):
            self.promote('swap')
        self.assertEqual(self.snapshot(),before)
        self.db.execute('DROP TRIGGER swap_score')
        self.assertTrue(self.promote('swap'))
        self.assertEqual(self.db.execute('SELECT code,score FROM target WHERE code IN (\'A\',\'B\') ORDER BY code').fetchall(),[('A',10),('B',20)])
        self.assertEqual(self.db.execute('PRAGMA foreign_key_check').fetchall(),[])

class ImportSecurityLesson(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / 'import.sqlite'
        self.owner = self.connect()
        self.owner.executescript('''
          CREATE TABLE manifest(batch TEXT PRIMARY KEY, state TEXT NOT NULL);
          INSERT INTO manifest VALUES ('A','OPEN'),('B','OPEN');
          CREATE TABLE stage(batch TEXT NOT NULL, n INTEGER NOT NULL, raw TEXT NOT NULL, PRIMARY KEY(batch,n));
          CREATE TABLE target(batch TEXT, n INTEGER, score INTEGER, PRIMARY KEY(batch,n));
          INSERT INTO target VALUES ('B',1,99);
          CREATE TABLE rejection(batch TEXT,n INTEGER,reason TEXT,raw TEXT);
          INSERT INTO rejection VALUES ('A',1,'SCORE','synthetic-private-A'),('B',1,'SCORE','synthetic-private-B');
          CREATE VIEW incoming_a AS SELECT n,raw FROM stage WHERE batch='A';
          CREATE TRIGGER receive_a INSTEAD OF INSERT ON incoming_a BEGIN
            SELECT CASE WHEN (SELECT state FROM manifest WHERE batch='A') IS NOT 'OPEN' THEN RAISE(ABORT,'BATCH_CLOSED') END;
            SELECT CASE WHEN EXISTS(SELECT 1 FROM stage WHERE batch='A' AND n=NEW.n) THEN RAISE(ABORT,'ROW_EXISTS') END;
            INSERT INTO stage VALUES ('A',NEW.n,NEW.raw);
          END;
          CREATE VIEW report_a AS SELECT batch,n,reason FROM rejection WHERE batch='A';
          CREATE VIEW result_a AS SELECT batch,n,score FROM target WHERE batch='A';
          CREATE VIEW promote_a AS SELECT 1 AS request WHERE 0;
          CREATE TRIGGER commit_a INSTEAD OF INSERT ON promote_a BEGIN
            SELECT CASE WHEN NEW.request IS NOT 1 OR (SELECT state FROM manifest WHERE batch='A') IS NOT 'SEALED' THEN RAISE(ABORT,'NOT_APPROVED') END;
            SELECT CASE WHEN NOT EXISTS(SELECT 1 FROM stage WHERE batch='A') OR EXISTS(SELECT 1 FROM stage WHERE batch='A' AND (CAST(CAST(raw AS INTEGER) AS TEXT) != raw OR CAST(raw AS INTEGER) NOT BETWEEN 0 AND 100)) THEN RAISE(ABORT,'INVALID_BATCH') END;
            SELECT CASE WHEN EXISTS(SELECT 1 FROM target WHERE batch='A') THEN RAISE(ABORT,'TARGET_EXISTS') END;
            INSERT INTO target SELECT batch,n,CAST(raw AS INTEGER) FROM stage WHERE batch='A';
            UPDATE manifest SET state='COMMITTED' WHERE batch='A';
          END;
        ''')

    def connect(self):
        db = sqlite3.connect(self.path, cached_statements=0)
        self.addCleanup(db.close)
        db.execute('PRAGMA trusted_schema=OFF')
        return db

    def restricted(self, role):
        db = self.connect()
        def authorize(action, table, column, schema, source):
            allow = False
            if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_TRANSACTION):
                allow = True
            elif schema == 'main' and role == 'uploader':
                if action == sqlite3.SQLITE_INSERT:
                    allow = (table,source) in (('incoming_a',None),('stage','receive_a'))
                elif action == sqlite3.SQLITE_READ:
                    allow = (source == 'receive_a' and (table,column) in (('manifest','state'),('manifest','batch'),('stage','batch'),('stage','n'),('incoming_a','n'),('incoming_a','raw')))
            elif schema == 'main' and role == 'promoter':
                if action == sqlite3.SQLITE_INSERT:
                    allow = (table,source) in (('promote_a',None),('target','commit_a'))
                elif action == sqlite3.SQLITE_UPDATE:
                    allow = (table,column,source) == ('manifest','state','commit_a')
                elif action == sqlite3.SQLITE_READ:
                    allow = source == 'commit_a' and (table,column) in (('promote_a','request'),('manifest','state'),('manifest','batch'),('stage','batch'),('stage','n'),('stage','raw'),('target','batch'))
            elif schema == 'main' and role == 'reviewer' and action == sqlite3.SQLITE_READ:
                allow = ((source is None and table in ('report_a','result_a') and column in ('batch','n','reason','score')) or
                         (source == 'report_a' and table == 'rejection' and column in ('batch','n','reason')) or
                         (source == 'result_a' and table == 'target' and column in ('batch','n','score')))
            return sqlite3.SQLITE_OK if allow else sqlite3.SQLITE_DENY
        db.set_authorizer(authorize)
        return db

    def snapshot(self):
        return tuple(self.owner.execute('SELECT * FROM '+t+' ORDER BY 1,2').fetchall() for t in ('manifest','stage','target','rejection'))

    def denied(self, db, sql):
        before = self.snapshot()
        with self.assertRaises(sqlite3.DatabaseError) as caught, db:
            db.execute(sql).fetchall()
        self.assertEqual(caught.exception.sqlite_errorcode, sqlite3.SQLITE_AUTH)
        self.assertEqual(self.snapshot(),before)

    def test_uploader_append_only_and_sealed_batch(self):
        db = self.restricted('uploader')
        with db:
            db.execute('INSERT INTO incoming_a VALUES (?,?)',(1,'synthetic-input'))
        self.assertEqual(self.owner.execute('SELECT * FROM stage').fetchall(),[('A',1,'synthetic-input')])
        for sql in ("INSERT INTO stage VALUES ('B',2,'x')",'SELECT raw FROM stage','SELECT raw FROM incoming_a',
                    "UPDATE stage SET raw='changed'",'DELETE FROM stage',"UPDATE manifest SET state='OPEN'",
                    "INSERT INTO target VALUES ('A',1,10)","DELETE FROM target",'DROP TRIGGER receive_a',
                    'PRAGMA writable_schema=ON','INSERT INTO promote_a VALUES (1)',"ATTACH DATABASE ':memory:' AS extra"):
            with self.subTest(sql=sql): self.denied(db,sql)
        before = self.snapshot()
        for conflict in ('REPLACE','IGNORE'):
            with self.assertRaisesRegex(sqlite3.IntegrityError,'ROW_EXISTS'), db:
                db.execute('INSERT OR '+conflict+" INTO incoming_a VALUES (1,'changed')")
            self.assertEqual(self.snapshot(),before)
        with self.owner:
            self.owner.execute("UPDATE manifest SET state='SEALED' WHERE batch='A'")
        before = self.snapshot()
        with self.assertRaisesRegex(sqlite3.IntegrityError,'BATCH_CLOSED'), db:
            db.execute("INSERT INTO incoming_a VALUES (2,'late')")
        self.assertEqual(self.snapshot(),before)

    def test_reviewer_projection_scope_and_no_write(self):
        db = self.restricted('reviewer')
        self.assertEqual(db.execute('SELECT * FROM report_a').fetchall(),[('A',1,'SCORE')])
        self.assertEqual(db.execute('SELECT * FROM result_a').fetchall(),[])
        for sql in ('SELECT raw FROM rejection','SELECT * FROM rejection','SELECT * FROM stage','SELECT * FROM target',
                    'SELECT * FROM manifest',"UPDATE rejection SET reason='OK'",'DELETE FROM rejection',
                    'CREATE TEMP VIEW report_a AS SELECT raw FROM rejection', 'PRAGMA table_info(rejection)',
                    "INSERT INTO incoming_a VALUES (2,'reviewer')",'INSERT INTO promote_a VALUES (1)'):
            with self.subTest(sql=sql): self.denied(db,sql)
        self.assertEqual(db.execute("SELECT * FROM report_a WHERE batch='B'").fetchall(),[])

    def test_trusted_promotion_and_untrusted_diagnostics(self):
        uploader = self.restricted('uploader')
        reviewer = self.restricted('reviewer')
        promoter = self.restricted('promoter')
        with uploader:
            uploader.execute('INSERT INTO incoming_a VALUES (?,?)',(2,'42'))
        before = self.snapshot()
        with self.assertRaisesRegex(sqlite3.IntegrityError,'NOT_APPROVED'), promoter:
            promoter.execute('INSERT INTO promote_a VALUES (1)')
        self.assertEqual(self.snapshot(),before)
        with self.owner:
            self.owner.execute("UPDATE manifest SET state='SEALED' WHERE batch='A'")
        for sql in ("INSERT INTO target VALUES ('B',2,42)","UPDATE manifest SET state='SEALED'",'SELECT raw FROM stage','DELETE FROM target'):
            self.denied(promoter,sql)
        with promoter:
            promoter.execute('INSERT INTO promote_a VALUES (1)')
        self.assertEqual(self.owner.execute("SELECT state FROM manifest WHERE batch='A'").fetchone(),('COMMITTED',))
        self.assertEqual(reviewer.execute('SELECT * FROM result_a').fetchall(),[('A',2,42)])
        self.assertEqual(self.owner.execute('SELECT * FROM target ORDER BY batch,n').fetchall(),[('A',2,42),('B',1,99)])
        self.denied(reviewer,"UPDATE target SET score=0")
        self.denied(uploader,"UPDATE target SET score=0")
        # This trusted host maps database exceptions to a fixed client diagnostic.
        # The raw exception itself is not a supported public response contract.
        def client_insert(value):
            try:
                with uploader:
                    uploader.execute('INSERT INTO incoming_a VALUES (?,?)',(3,value))
            except sqlite3.DatabaseError:
                return {'code':'IMPORT_REJECTED'}
            return {'code':'ACCEPTED'}
        before = self.snapshot()
        self.assertEqual(client_insert('synthetic-private-input'),{'code':'IMPORT_REJECTED'})
        self.assertEqual(self.snapshot(),before)
        self.assertEqual(reviewer.execute('SELECT * FROM report_a').fetchall(),[('A',1,'SCORE')])

    def test_invalid_or_colliding_batch_never_promotes(self):
        uploader = self.restricted('uploader')
        promoter = self.restricted('promoter')
        with uploader:
            uploader.execute('INSERT INTO incoming_a VALUES (?,?)',(1,'42x'))
        with self.owner:
            self.owner.execute("UPDATE manifest SET state='SEALED' WHERE batch='A'")
        before = self.snapshot()
        with self.assertRaisesRegex(sqlite3.IntegrityError,'INVALID_BATCH'), promoter:
            promoter.execute('INSERT OR IGNORE INTO promote_a VALUES (1)')
        self.assertEqual(self.snapshot(),before)
        # Admin-only setup of a separate negative fixture; not an allowed uploader edit.
        with self.owner:
            self.owner.execute("UPDATE stage SET raw='42' WHERE batch='A'")
            self.owner.execute("INSERT INTO target VALUES ('A',1,7)")
        before = self.snapshot()
        with self.assertRaisesRegex(sqlite3.IntegrityError,'TARGET_EXISTS'), promoter:
            promoter.execute('INSERT OR REPLACE INTO promote_a VALUES (1)')
        self.assertEqual(self.snapshot(),before)

class SqlSemanticsLesson(unittest.TestCase):
    def test_case_scope_and_exact_approved_keys(self):
        with sqlite3.connect(':memory:') as db:
            db.executescript('''CREATE TABLE payment(study TEXT, id TEXT, year INTEGER, amount INTEGER, PRIMARY KEY(study,id));
              INSERT INTO payment VALUES ('A','1',2004,100),('A','2',2010,100),('A','3',2020,100),('A','4',NULL,100),('B','1',2004,100);''')
            snapshot = lambda: db.execute('SELECT * FROM payment ORDER BY study,id').fetchall()
            before = snapshot()
            approved = db.execute("SELECT id FROM payment WHERE study='A' AND year BETWEEN 2001 AND 2015 ORDER BY id").fetchall()
            self.assertEqual(approved,[('1',),('2',)])
            db.execute('SAVEPOINT unsafe')
            c = db.execute("UPDATE payment SET amount=CASE WHEN year BETWEEN 2001 AND 2005 THEN amount*2 WHEN year BETWEEN 2006 AND 2015 THEN amount+50 END WHERE study='A'")
            self.assertEqual(c.rowcount,4)
            self.assertEqual(db.execute("SELECT id,amount FROM payment WHERE study='A' ORDER BY id").fetchall(),[('1',200),('2',150),('3',None),('4',None)])
            db.execute('ROLLBACK TO unsafe')
            db.execute('RELEASE unsafe')
            self.assertEqual(snapshot(),before)
            changed = db.execute("UPDATE payment SET amount=CASE WHEN year BETWEEN 2001 AND 2005 THEN amount*2 WHEN year BETWEEN 2006 AND 2015 THEN amount+50 ELSE amount END WHERE study=? AND year BETWEEN ? AND ? RETURNING id,amount",('A',2001,2015)).fetchall()
            self.assertEqual(sorted(changed),[('1',200),('2',150)])
            self.assertEqual(snapshot(),[('A','1',2004,200),('A','2',2010,150),('A','3',2020,100),('A','4',None,100),('B','1',2004,100)])

    def test_per_record_version_and_returning_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = sqlite3.connect(Path(tmp)/'lesson.sqlite')
            b = sqlite3.connect(Path(tmp)/'lesson.sqlite')
            try:
                a.executescript('''CREATE TABLE review(study TEXT, id TEXT, version INTEGER NOT NULL, status TEXT, PRIMARY KEY(study,id));
                  INSERT INTO review VALUES ('A','1',1,'draft'),('A','2',1,'draft'),('B','1',1,'draft');''')
                sql = "UPDATE review SET status=?,version=version+1 WHERE study=? AND id=? AND version=? AND status='draft' RETURNING study,id,version,status"
                old = b.execute("SELECT version FROM review WHERE study='A' AND id='1'").fetchone()[0]
                with a:
                    self.assertEqual(a.execute(sql,('approved','A','1',old)).fetchall(),[('A','1',2,'approved')])
                with b:
                    self.assertEqual(b.execute(sql,('approved','A','1',old)).fetchall(),[])
                    self.assertEqual(b.execute(sql,('approved','A','1',2)).fetchall(),[])
                    self.assertEqual(b.execute(sql,('approved','A','missing',1)).fetchall(),[])
                    self.assertEqual(b.execute(sql,('approved','A',"1' OR 1=1 --",1)).fetchall(),[])
                    self.assertEqual(b.execute(sql,('approved','A','2',1)).fetchall(),[('A','2',2,'approved')])
                self.assertEqual(a.execute('SELECT * FROM review ORDER BY study,id').fetchall(),[('A','1',2,'approved'),('A','2',2,'approved'),('B','1',1,'draft')])
                # RETURNING reports the direct statement, not subsequent AFTER trigger effects or commit.
                a.execute("CREATE TRIGGER after_review AFTER UPDATE ON review WHEN NEW.study='B' BEGIN UPDATE review SET status='flagged' WHERE study=NEW.study AND id=NEW.id; END")
                with self.assertRaisesRegex(ValueError,'unexpected final state'), a:
                    rows = a.execute(sql,('approved','B','1',1)).fetchall()
                    self.assertEqual(rows,[('B','1',2,'approved')])
                    self.assertEqual(a.execute("SELECT status FROM review WHERE study='B'").fetchone(),('flagged',))
                    raise ValueError('unexpected final state')
                self.assertEqual(b.execute("SELECT version,status FROM review WHERE study='B'").fetchone(),(1,'draft'))
                c = a.execute("UPDATE review SET status=status WHERE study='B'")
                self.assertEqual(c.rowcount,1)
                a.rollback()
                self.assertEqual(b.execute("SELECT version,status FROM review WHERE study='B'").fetchone(),(1,'draft'))
            finally:
                a.close(); b.close()

    def test_set_multiplicity_and_null_anti_join(self):
        with sqlite3.connect(':memory:') as db:
            db.executescript('''CREATE TABLE expected(id TEXT NOT NULL); INSERT INTO expected VALUES ('A'),('B'),('C');
              CREATE TABLE observed(id TEXT); INSERT INTO observed VALUES ('A'),('A'),('B'),(NULL);''')
            self.assertEqual(db.execute('SELECT id FROM expected WHERE id NOT IN (SELECT id FROM observed)').fetchall(),[])
            self.assertEqual(db.execute('SELECT e.id FROM expected e WHERE NOT EXISTS (SELECT 1 FROM observed o WHERE e.id=o.id) ORDER BY e.id').fetchall(),[('C',)])
            self.assertEqual(db.execute('SELECT id FROM expected EXCEPT SELECT id FROM observed').fetchall(),[('C',)])
            self.assertEqual(db.execute('SELECT id FROM observed INTERSECT SELECT id FROM expected ORDER BY id').fetchall(),[('A',),('B',)])
            self.assertEqual(db.execute('SELECT COUNT(*) FROM (SELECT id FROM expected UNION SELECT id FROM observed)').fetchone(),(4,))
            self.assertEqual(db.execute('SELECT COUNT(*) FROM (SELECT id FROM expected UNION ALL SELECT id FROM observed)').fetchone(),(7,))
            self.assertEqual(db.execute('SELECT id,count(*) FROM observed GROUP BY id HAVING count(*)>1').fetchall(),[('A',2)])
            self.assertEqual(db.execute('SELECT count(*) FROM observed WHERE id IS NULL').fetchone(),(1,))
            # EXCEPT is distinct; equal sets can conceal different multiplicities.
            self.assertEqual(db.execute("SELECT id FROM observed WHERE id IS NOT NULL EXCEPT SELECT id FROM expected WHERE id<>'C'").fetchall(),[])
            self.assertEqual(db.execute("SELECT id FROM expected WHERE id<>'C' EXCEPT SELECT id FROM observed WHERE id IS NOT NULL").fetchall(),[])
            self.assertEqual(db.execute('SELECT count(*) FROM observed WHERE id IS NOT NULL').fetchone(),(3,))

class JoinGrainLesson(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)
        self.db.executescript('''CREATE TABLE participant(study TEXT, id TEXT, PRIMARY KEY(study,id));
          INSERT INTO participant VALUES ('A','P1'),('A','P2'),('A','P3'),('A','P4'),('B','P1');
          CREATE TABLE measurement(study TEXT, id TEXT, mid INTEGER PRIMARY KEY, phase TEXT, score INTEGER);
          INSERT INTO measurement VALUES ('A','P1',1,'post',10),('A','P1',2,'post',10),('A','P2',3,'post',40),('A','P3',4,'pre',20),('B','P1',5,'post',90);
          CREATE TABLE payment(study TEXT,id TEXT,payid INTEGER PRIMARY KEY, amount INTEGER);
          INSERT INTO payment VALUES ('A','P1',1,100),('A','P1',2,100),('A','P1',3,200),('A','P2',4,50),('B','P1',5,900);''')

    def test_outer_join_filter_count_and_missingness(self):
        base = ' FROM participant p LEFT JOIN measurement m ON p.study=m.study AND p.id=m.id '
        self.assertEqual(self.db.execute('SELECT p.id,m.mid'+base+"WHERE p.study='A' AND m.phase='post' ORDER BY p.id,m.mid").fetchall(), [('P1',1),('P1',2),('P2',3)])
        self.assertEqual(self.db.execute('SELECT p.id,m.mid'+base+"WHERE p.study='A' AND (m.phase='post' OR m.mid IS NULL) ORDER BY p.id,m.mid").fetchall(), [('P1',1),('P1',2),('P2',3),('P4',None)])
        eligible = base+"AND m.phase='post' WHERE p.study='A' "
        self.assertEqual(self.db.execute('SELECT p.id,m.mid'+eligible+'ORDER BY p.id,m.mid').fetchall(), [('P1',1),('P1',2),('P2',3),('P3',None),('P4',None)])
        self.assertEqual(self.db.execute('SELECT p.id,COUNT(*),COUNT(m.mid),AVG(m.score)'+eligible+'GROUP BY p.id ORDER BY p.id').fetchall(), [('P1',2,2,10.0),('P2',1,1,40.0),('P3',1,0,None),('P4',1,0,None)])
        self.assertEqual(self.db.execute('SELECT COUNT(DISTINCT p.id),COUNT(m.mid),COUNT(DISTINCT CASE WHEN m.mid IS NOT NULL THEN p.id END)'+eligible).fetchone(), (4,3,2))
        self.assertEqual(self.db.execute('SELECT p.id,SUM(m.score)'+eligible+'GROUP BY p.id HAVING SUM(m.score) IS NOT NULL ORDER BY p.id').fetchall(), [('P1',20),('P2',40)])
        self.assertEqual(self.db.execute('SELECT p.id FROM participant p LEFT JOIN measurement m ON p.id=m.id AND m.phase=\'post\' WHERE p.study=\'A\' AND m.study=\'B\'').fetchall(), [('P1',)])

    def test_multi_child_fanout_and_preaggregation(self):
        joined = ''' FROM participant p JOIN measurement m ON p.study=m.study AND p.id=m.id AND m.phase='post'
          JOIN payment q ON p.study=q.study AND p.id=q.id WHERE p.study='A' '''
        self.assertEqual(self.db.execute('SELECT p.id,COUNT(*),SUM(q.amount),SUM(m.score)'+joined+'GROUP BY p.id ORDER BY p.id').fetchall(), [('P1',6,800,60),('P2',1,50,40)])
        self.assertEqual(self.db.execute('SELECT COUNT(*),COUNT(DISTINCT p.id),SUM(q.amount),SUM(DISTINCT q.amount)'+joined).fetchone(), (7,2,850,350))
        wrong_avg = self.db.execute('SELECT AVG(m.score)'+joined).fetchone()[0]
        self.assertAlmostEqual(wrong_avg,100/7)
        query = '''WITH m AS (SELECT study,id,COUNT(*) n,AVG(score) mean FROM measurement WHERE phase='post' GROUP BY study,id),
          q AS (SELECT study,id,COUNT(*) n,SUM(amount) paid FROM payment GROUP BY study,id)
          SELECT p.id,COALESCE(m.n,0),m.mean,COALESCE(q.n,0),q.paid
          FROM participant p LEFT JOIN m ON p.study=m.study AND p.id=m.id
          LEFT JOIN q ON p.study=q.study AND p.id=q.id WHERE p.study='A' ORDER BY p.id'''
        rows = self.db.execute(query).fetchall()
        self.assertEqual(rows,[('P1',2,10.0,3,400),('P2',1,40.0,1,50),('P3',0,None,0,None),('P4',0,None,0,None)])
        self.assertEqual(self.db.execute('SELECT COUNT(*),SUM(amount) FROM payment WHERE study=\'A\'').fetchone(), (4,450))
        self.assertEqual(sum(r[4] for r in rows if r[4] is not None),450)
        self.assertEqual(self.db.execute("SELECT COUNT(*),AVG(score) FROM measurement WHERE study='A' AND phase='post'").fetchone(), (3,20.0))
        self.assertEqual(sum(r[2] for r in rows if r[2] is not None)/2,25.0)
        self.assertEqual(self.db.execute("SELECT p.id FROM participant p WHERE p.study='A' AND EXISTS(SELECT 1 FROM measurement m WHERE m.study=p.study AND m.id=p.id AND m.phase='post') ORDER BY p.id").fetchall(), [('P1',),('P2',)])

    def test_insert_select_and_dedup_at_correct_grain(self):
        self.db.execute('CREATE TABLE cohort(study TEXT,id TEXT,PRIMARY KEY(study,id))')
        before = self.db.execute('SELECT * FROM measurement ORDER BY mid').fetchall()
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO cohort SELECT p.study,p.id FROM participant p JOIN measurement m ON p.study=m.study AND p.id=m.id WHERE p.study='A' AND m.phase='post'")
        self.assertEqual(self.db.execute('SELECT * FROM cohort').fetchall(),[])
        self.db.execute("INSERT INTO cohort(study,id) SELECT p.study,p.id FROM participant p WHERE p.study='A' AND EXISTS(SELECT 1 FROM measurement m WHERE m.study=p.study AND m.id=p.id AND m.phase='post')")
        self.assertEqual(self.db.execute('SELECT * FROM cohort ORDER BY id').fetchall(),[('A','P1'),('A','P2')])
        self.assertEqual(self.db.execute('SELECT * FROM measurement ORDER BY mid').fetchall(),before)
        self.db.execute('SAVEPOINT wrong_dedup')
        deleted = self.db.execute('DELETE FROM measurement WHERE mid NOT IN (SELECT MIN(mid) FROM measurement GROUP BY study,id,phase,score) RETURNING mid').fetchall()
        self.assertEqual(deleted,[(2,)])  # same score is a legitimate separate event
        self.db.execute('ROLLBACK TO wrong_dedup')
        self.db.execute('RELEASE wrong_dedup')
        self.assertEqual(self.db.execute('SELECT * FROM measurement ORDER BY mid').fetchall(),before)

if __name__ == '__main__': unittest.main(verbosity=2)
