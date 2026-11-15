"""Synthetic service-layer authorization lab; no network or real research data."""
import sqlite3, tempfile, unittest, hashlib, os
from pathlib import Path
from contextlib import closing

class Service:
    def __init__(self, path, scoped=True):
        self.path, self.scoped = path, scoped
    def call(self, session, operation, study, row=None):
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('BEGIN IMMEDIATE' if operation == 'update' else 'BEGIN')
            actor = db.execute('SELECT actor FROM sessions WHERE token=?', (session,)).fetchone()
            if not actor:
                raise PermissionError('denied')
            # Compare a global-role-only gate with current actor+study membership.
            if self.scoped:
                role = db.execute('SELECT role FROM membership WHERE actor=? AND study=?', (actor[0],study)).fetchone()
            else:
                role = db.execute('SELECT role FROM membership WHERE actor=?', (actor[0],)).fetchone()
            if not role or operation not in {'read','export','update'} or (operation == 'update' and role[0] != 'editor'):
                raise PermissionError('denied')
            if operation == 'export':
                return db.execute('SELECT id,value FROM records WHERE study=? ORDER BY id',(study,)).fetchall()
            if operation == 'read':
                item=db.execute('SELECT value FROM records WHERE study=? AND id=?',(study,row)).fetchone()
                if not item: raise PermissionError('denied')
                return item[0]
            changed=db.execute('UPDATE records SET value=value+1 WHERE study=? AND id=?',(study,row)).rowcount
            if changed != 1: raise PermissionError('denied')
            db.execute('INSERT INTO events VALUES(?,?,?)',(actor[0],study,row))
            return changed

class ResearchScope(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'lab.sqlite'
        with closing(sqlite3.connect(self.path)) as db, db:
            db.executescript('''CREATE TABLE sessions(token PRIMARY KEY,actor);
            CREATE TABLE membership(actor,study,role,PRIMARY KEY(actor,study));
            CREATE TABLE records(study,id,value,PRIMARY KEY(study,id));
            CREATE TABLE events(actor,study,id);
            INSERT INTO sessions VALUES('s-a','a'),('s-b','b'),('s-r','r');
            INSERT INTO membership VALUES('a','A','editor'),('b','B','editor'),('r','A','reader');
            INSERT INTO records VALUES('A',1,10),('B',1,20);''')
        self.svc=Service(self.path,scoped=os.environ.get('LAB_MODE','scoped')=='scoped')
    def snapshot(self):
        with closing(sqlite3.connect(self.path)) as db:
            return (db.execute('SELECT * FROM records ORDER BY study,id').fetchall(),db.execute('SELECT * FROM events').fetchall(),hashlib.sha256(self.path.read_bytes()).hexdigest())
    def denied(self,*args):
        before=self.snapshot()
        with self.assertRaises(PermissionError): self.svc.call(*args)
        self.assertEqual(before,self.snapshot())
    def test_same_id_cross_study_read(self): self.denied('s-a','read','B',1)
    def test_cross_study_export(self): self.denied('s-a','export','B')
    def test_cross_study_update(self): self.denied('s-a','update','B',1)
    def test_reader_denial(self): self.denied('s-r','update','A',1)
    def test_missing_session(self): self.denied('unknown','export','A')
    def test_revocation_existing_session(self):
        with closing(sqlite3.connect(self.path)) as db, db: db.execute("DELETE FROM membership WHERE actor='a' AND study='A'"); db.execute("INSERT INTO membership VALUES('a','B','editor')")
        self.denied('s-a','read','A',1)
        self.denied('s-a','update','A',1)
    def test_positive_and_isolated_side_effect(self):
        self.assertEqual(self.svc.call('s-a','read','A',1),10)
        self.assertEqual(self.svc.call('s-r','export','A'),[(1,10)])
        self.assertEqual(self.svc.call('s-a','update','A',1),1)
        self.assertEqual(self.svc.call('s-b','export','B'),[(1,20)])
        rows,events,_=self.snapshot(); self.assertEqual(rows,[('A',1,11),('B',1,20)]); self.assertEqual(events,[('a','A',1)])
    def test_missing_row_no_effect(self): self.denied('s-a','update','A',999)

if __name__=='__main__': unittest.main(verbosity=2)
