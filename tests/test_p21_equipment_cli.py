"""P2-1d: real CLI process migration, startup, restart and rollback boundary."""
import ast
import http.client
import queue
import re
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import closing, contextmanager
from pathlib import Path
from urllib.parse import urlencode, urlsplit

from src.p21_equipment_site import Store


class EquipmentCLITests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        self.old=self.root/'old.sqlite'
        self.new=self.root/'new.sqlite'

    def legacy(self, three=False):
        with closing(sqlite3.connect(self.old)) as db, db:
            db.execute('CREATE TABLE inventory(id INTEGER PRIMARY KEY CHECK(id=1), stock INTEGER NOT NULL, reserved INTEGER NOT NULL CHECK(reserved>=0 AND reserved<=stock))')
            db.execute("CREATE TABLE requests(owner TEXT NOT NULL, token TEXT NOT NULL, qty INTEGER NOT NULL CHECK(qty>0), result TEXT NOT NULL CHECK(result IN ('RESERVED','INSUFFICIENT')), PRIMARY KEY(owner,token))")
            db.execute('INSERT INTO inventory VALUES(1,10,?)',(3 if three else 7,))
            db.executemany('INSERT INTO requests VALUES(?,?,?,?)',[
                ('member','1'*32,4,'RESERVED'),('member2','2'*32,3,'RESERVED'),
                ('member2','3'*32,8,'INSUFFICIENT')])
            if three:
                db.execute("""CREATE TABLE lifecycle(
                    actor TEXT NOT NULL, action_token TEXT NOT NULL,
                    owner TEXT NOT NULL, target_token TEXT NOT NULL,
                    result TEXT NOT NULL CHECK(result IN ('CANCELLED','RETURNED')),
                    PRIMARY KEY(actor,action_token), UNIQUE(owner,target_token))""")
                db.execute('INSERT INTO lifecycle VALUES(?,?,?,?,?)',('admin','4'*32,'member','1'*32,'RETURNED'))

    def args(self, db, *args):
        return [sys.executable,'-m','src.p21_equipment_site','--database',str(db),'--port','0',*map(str,args)]

    def cli(self, db, *args):
        return subprocess.run(self.args(db,*args),capture_output=True,text=True,timeout=20)

    def migrate(self, target):
        r=self.cli(target,'--migrate-from',self.old,'--confirm-source-offline')
        self.assertEqual(r.returncode,0,'migration CLI failed')
        self.assertEqual(r.stderr,'')
        result=ast.literal_eval(r.stdout.strip())
        self.assertEqual(result['schema_version'],1)
        return result

    @contextmanager
    def serving(self, db, *args):
        # Read only the two startup lines; never print synthetic passwords.
        proc=subprocess.Popen(self.args(db,*args),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        lines=queue.Queue()
        def read():
            for line in proc.stdout: lines.put(line.rstrip('\n'))
            lines.put(None)
        reader=threading.Thread(target=read,daemon=True)
        reader.start()
        try:
            origin=lines.get(timeout=12)
            creds=lines.get(timeout=5) if origin else None
            self.assertIsNotNone(origin,'server exited before startup')
            self.assertRegex(origin,r'^http://127\.0\.0\.1:\d+$')
            self.assertTrue(creds and creds.startswith('Temporary synthetic credentials: '))
            credentials=ast.literal_eval(creds.split(': ',1)[1])
            self.assertEqual(set(credentials),{'member','member2','admin'})
            yield origin,credentials
        finally:
            if proc.poll() is None:
                proc.terminate()
                try: proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill(); proc.wait(timeout=5)
            reader.join(timeout=5)
            proc.stdout.close()
            proc.stderr.close()
        self.assertIsNotNone(proc.returncode)

    def http(self, origin, path, cookie='', data=None):
        port=urlsplit(origin).port
        conn=http.client.HTTPConnection('127.0.0.1',port,timeout=5)
        headers={'Cookie':cookie} if cookie else {}
        if data is not None:
            headers.update({'Origin':origin,'Content-Type':'application/x-www-form-urlencoded'})
        try:
            conn.request('POST' if data is not None else 'GET',path,None if data is None else urlencode(data),headers)
            r=conn.getresponse()
            return r.status,r.read().decode(),r.getheader('Set-Cookie') or ''
        finally: conn.close()

    def login(self, origin, credentials, actor):
        status,_,cookie=self.http(origin,'/login',data={'user':actor,'password':credentials[actor]})
        self.assertEqual(status,200)
        return cookie.split(';')[0]

    def test_migration_cli_two_and_three_table_then_readonly_cutover_rollback(self):
        for three in (False,True):
            with self.subTest(three=three):
                self.old=self.root/('legacy3.sqlite' if three else 'legacy2.sqlite')
                self.new=self.root/('copy3.sqlite' if three else 'copy2.sqlite')
                self.legacy(three)
                original=self.old.read_bytes()
                rejected=self.cli(self.old)
                self.assertNotEqual(rejected.returncode,0)
                self.assertEqual(self.old.read_bytes(),original)
                self.assertEqual(self.migrate(self.new),{'schema_version':1,'requests':3,'lifecycle':int(three)})
                candidate=self.new.read_bytes()
                with self.serving(self.new) as (origin,credentials):
                    admin=self.login(origin,credentials,'admin')
                    code,body,_=self.http(origin,'/admin',admin)
                    self.assertEqual(code,200)
                    self.assertIn('Available: '+str(7 if three else 3),body)
                    self.assertIn('1'*32,body)
                    if three: self.assertIn('RETURNED',body)
                # No candidate write occurred: return to the preserved source
                # snapshot is safe for data; the legacy server is not executed.
                self.assertEqual(self.new.read_bytes(),candidate)
                self.assertEqual(self.old.read_bytes(),original)
                self.assertEqual(Store(self.old).view(None)[:2],(10,3 if three else 7))
                second=self.root/('retry3.sqlite' if three else 'retry2.sqlite')
                self.assertEqual(self.migrate(second)['requests'],3)
                self.assertEqual(Store(second).view(None,lifecycle=True),Store(self.new).view(None,lifecycle=True))
                self.assertEqual(self.old.read_bytes(),original)
        print('P21-CLI-CUTOVER: both legacy schemas; real process startup/stop; read-only pre-write rollback snapshot preserved',flush=True)

    def test_migration_cli_negative_paths_no_overwrite(self):
        self.legacy(True)
        before=self.old.read_bytes()
        for args in [('--migrate-from',self.old),('--initialize','--migrate-from',self.old,'--confirm-source-offline'),('--confirm-source-offline',)]:
            r=self.cli(self.new,*args)
            self.assertNotEqual(r.returncode,0)
            self.assertFalse(self.new.exists())
        self.new.write_bytes(b'existing target')
        r=self.cli(self.new,'--migrate-from',self.old,'--confirm-source-offline')
        self.assertNotEqual(r.returncode,0)
        self.assertEqual(self.new.read_bytes(),b'existing target')
        self.assertEqual(self.old.read_bytes(),before)
        self.new.unlink()
        missing=self.root/'missing.sqlite'
        r=self.cli(self.new,'--migrate-from',missing,'--confirm-source-offline')
        self.assertNotEqual(r.returncode,0)
        self.assertFalse(missing.exists()); self.assertFalse(self.new.exists())
        self.assertEqual(self.old.read_bytes(),before)

    def test_restart_persists_writes_and_old_snapshot_is_not_postwrite_rollback(self):
        self.legacy(True)
        original=self.old.read_bytes()
        self.migrate(self.new)
        with self.serving(self.new) as (origin,credentials):
            m=self.login(origin,credentials,'member')
            _,body,_=self.http(origin,'/',m)
            data={'csrf':re.search('name="csrf" value="([^"]+)"',body)[1],
                  'token':re.search('name="token" value="([^"]+)"',body)[1],'qty':2}
            status,body,_=self.http(origin,'/reserve',m,data)
            self.assertEqual(status,200); self.assertIn('RESERVED',body)
        self.assertEqual(Store(self.new).view(None)[:2],(10,5))
        with self.serving(self.new) as (origin,credentials):
            self.assertEqual(self.http(origin,'/admin',m)[0],401)
            admin=self.login(origin,credentials,'admin')
            status,body,_=self.http(origin,'/admin',admin)
            self.assertEqual(status,200)
            self.assertIn(data['token'],body); self.assertIn('Available: 5',body)
        self.assertEqual(self.old.read_bytes(),original)
        self.assertEqual(Store(self.old).view(None)[:2],(10,3))
        self.assertNotEqual(Store(self.old).view(None)[2],Store(self.new).view(None)[2])
        print('P21-CLI-RESTART: committed reservation survived restart; old snapshot diverged; post-write downgrade unsafe',flush=True)

    def test_initialize_cli_and_missing_start(self):
        r=self.cli(self.new)
        self.assertNotEqual(r.returncode,0)
        self.assertFalse(self.new.exists())
        with self.serving(self.new,'--initialize') as (origin,credentials):
            admin=self.login(origin,credentials,'admin')
            self.assertIn('Available: 10',self.http(origin,'/admin',admin)[1])
        before=self.new.read_bytes()
        self.assertNotEqual(self.cli(self.new,'--initialize').returncode,0)
        self.assertEqual(self.new.read_bytes(),before)
