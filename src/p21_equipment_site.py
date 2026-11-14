"""Loopback-only synthetic equipment site; never deploy or use real identities."""
import argparse
import hmac
import html
import os
import re
import secrets
import sqlite3
import threading
import tempfile
import time
from contextlib import closing
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs


SCHEMA_VERSION = 1
MEMBERS = ('member', 'member2')


class Store:
    def __init__(self, path):
        self.path = Path(path).resolve()

    def connect(self, mode):
        return sqlite3.connect(self.path.as_uri()+'?mode='+mode, uri=True, timeout=5)

    def initialize(self):
        with self.path.open('xb'):
            pass
        with closing(self.connect('rw')) as db, db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('CREATE TABLE inventory(id INTEGER PRIMARY KEY CHECK(id=1), stock INTEGER NOT NULL, reserved INTEGER NOT NULL CHECK(reserved>=0 AND reserved<=stock))')
            db.execute('CREATE TABLE requests(owner TEXT NOT NULL, token TEXT NOT NULL, qty INTEGER NOT NULL CHECK(qty>0), result TEXT NOT NULL CHECK(result IN (\'RESERVED\',\'INSUFFICIENT\')), PRIMARY KEY(owner,token))')
            db.execute("""CREATE TABLE lifecycle(
                actor TEXT NOT NULL, action_token TEXT NOT NULL,
                owner TEXT NOT NULL, target_token TEXT NOT NULL,
                result TEXT NOT NULL CHECK(result IN ('CANCELLED','RETURNED')),
                PRIMARY KEY(actor,action_token), UNIQUE(owner,target_token))""")
            db.execute("""CREATE TABLE action_attempts(
                actor TEXT NOT NULL, action_token TEXT NOT NULL,
                owner TEXT NOT NULL, target_token TEXT NOT NULL,
                operation TEXT NOT NULL CHECK(operation IN ('cancel','return')),
                result TEXT NOT NULL CHECK(result IN ('CANCELLED','RETURNED','NOT_ACTIVE')),
                PRIMARY KEY(actor,action_token),
                CHECK(result='NOT_ACTIVE' OR (operation='cancel' AND result='CANCELLED')
                    OR (operation='return' AND result='RETURNED')))""")
            db.execute('INSERT INTO inventory VALUES(1,10,0)')
            db.execute('PRAGMA user_version='+str(SCHEMA_VERSION))

    @staticmethod
    def require_current(db):
        if db.execute('PRAGMA user_version').fetchone()[0] != SCHEMA_VERSION:
            raise sqlite3.DatabaseError('schema mismatch; explicit offline migration required')
        tables = {r[0] for r in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        if tables != {'inventory','requests','lifecycle','action_attempts'}:
            raise sqlite3.DatabaseError('schema mismatch')

    @staticmethod
    def legacy_snapshot(db):
        # Only the two known unversioned synthetic formats, never arbitrary data.
        if db.execute('PRAGMA user_version').fetchone()[0] != 0:
            raise sqlite3.DatabaseError('unsupported legacy version')
        if db.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
            raise sqlite3.DatabaseError('legacy integrity failure')
        objects = db.execute("SELECT type,name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'").fetchall()
        names = {n for t,n in objects if t=='table'}
        if any(t != 'table' for t,n in objects) or names not in (
                {'inventory','requests'}, {'inventory','requests','lifecycle'}):
            raise sqlite3.DatabaseError('unsupported legacy schema')
        columns = {'inventory':['id','stock','reserved'],
                   'requests':['owner','token','qty','result'],
                   'lifecycle':['actor','action_token','owner','target_token','result']}
        for name in names:
            if [row[1] for row in db.execute('PRAGMA table_info('+name+')')] != columns[name]:
                raise sqlite3.DatabaseError('unsupported legacy columns')
        inventory = db.execute('SELECT id,stock,reserved FROM inventory').fetchall()
        if (len(inventory)!=1 or any(type(x) is not int for x in inventory[0])
                or inventory[0][:2]!=(1,10) or not 0<=inventory[0][2]<=10):
            raise sqlite3.DatabaseError('invalid legacy inventory')
        requests = db.execute('SELECT owner,token,qty,result FROM requests ORDER BY owner,token').fetchall()
        lifecycle = db.execute('SELECT actor,action_token,owner,target_token,result FROM lifecycle ORDER BY actor,action_token').fetchall() if 'lifecycle' in names else []
        def token(value):
            return isinstance(value,str) and re.fullmatch(r'[a-f0-9]{32}',value)
        by_target = {}
        for owner,key,qty,result in requests:
            if (owner not in MEMBERS or not token(key) or type(qty) is not int
                    or not 1<=qty<=10 or result not in ('RESERVED','INSUFFICIENT')
                    or (owner,key) in by_target):
                raise sqlite3.DatabaseError('invalid legacy request')
            by_target[owner,key]=(qty,result)
        terminal = set()
        attempt_keys = set()
        attempts = []
        for actor,key,owner,target,result in lifecycle:
            operation = 'cancel' if result=='CANCELLED' else 'return'
            allowed = ((result=='CANCELLED' and actor==owner and owner in MEMBERS)
                       or (result=='RETURNED' and actor=='admin' and owner in MEMBERS))
            if (not allowed or not token(key) or not token(target)
                    or (actor,key) in attempt_keys or (owner,target) in terminal
                    or by_target.get((owner,target),(0,None))[1]!='RESERVED'):
                raise sqlite3.DatabaseError('invalid legacy lifecycle')
            attempt_keys.add((actor,key))
            terminal.add((owner,target))
            attempts.append((actor,key,owner,target,operation,result))
        expected = sum(qty for key,(qty,result) in by_target.items()
                       if result=='RESERVED' and key not in terminal)
        if expected!=inventory[0][2]:
            raise sqlite3.DatabaseError('legacy stock mismatch')
        return inventory,requests,lifecycle,attempts

    def migrate_from(self, source, *, confirm_offline=False, fault=False):
        """Create a new synthetic DB only; original is the rollback copy.
        Operator must stop old writers and keep them stopped through cutover.
        Publish via exclusive hard link on the same filesystem, never replace.
        """
        source=Store(source)
        if confirm_offline is not True or source.path==self.path:
            raise ValueError('distinct target and offline confirmation required')
        if self.path.exists():
            raise FileExistsError(self.path)
        def sidecars(store):
            return any(Path(str(store.path)+suffix).exists()
                       for suffix in ('-wal','-shm','-journal'))
        if sidecars(source) or sidecars(self):
            raise sqlite3.DatabaseError('sidecar files require offline reconciliation')
        with closing(source.connect('ro')) as old:
            old.execute('BEGIN')
            if old.execute('PRAGMA journal_mode').fetchone()[0]!='delete':
                raise sqlite3.DatabaseError('only offline rollback-journal source supported')
            inventory,requests,lifecycle,attempts=self.legacy_snapshot(old)
            # Staging is private and on the destination filesystem.
            with tempfile.TemporaryDirectory(prefix='.p21-migrate-',dir=self.path.parent) as directory:
                staged=Store(Path(directory)/'candidate.sqlite')
                staged.initialize()
                with closing(staged.connect('rw')) as db, db:
                    db.execute('BEGIN IMMEDIATE')
                    db.execute('UPDATE inventory SET stock=?,reserved=? WHERE id=1',inventory[0][1:])
                    db.executemany('INSERT INTO requests VALUES(?,?,?,?)',requests)
                    db.executemany('INSERT INTO lifecycle VALUES(?,?,?,?,?)',lifecycle)
                    db.executemany('INSERT INTO action_attempts VALUES(?,?,?,?,?,?)',attempts)
                    if fault:
                        raise RuntimeError('synthetic migration interruption')
                with closing(staged.connect('ro')) as db:
                    staged.require_current(db)
                    actual=(db.execute('SELECT id,stock,reserved FROM inventory').fetchall(),
                            db.execute('SELECT owner,token,qty,result FROM requests ORDER BY owner,token').fetchall(),
                            db.execute('SELECT actor,action_token,owner,target_token,result FROM lifecycle ORDER BY actor,action_token').fetchall(),
                            db.execute('SELECT actor,action_token,owner,target_token,operation,result FROM action_attempts ORDER BY actor,action_token').fetchall())
                    if db.execute('PRAGMA integrity_check').fetchall()!=[('ok',)] or actual!=(inventory,requests,lifecycle,attempts):
                        raise sqlite3.DatabaseError('migration verification failed')
                if sidecars(source) or sidecars(self):
                    raise sqlite3.DatabaseError('sidecars appeared; reconcile before publication')
                os.link(staged.path,self.path)
        return {'schema_version':SCHEMA_VERSION,'requests':len(requests),'lifecycle':len(lifecycle)}


    def view(self, owner, lifecycle=False, actor=None):
        with closing(self.connect('ro')) as db:
            db.execute('BEGIN')
            stock,reserved = db.execute('SELECT stock,reserved FROM inventory').fetchone()
            rows = db.execute('SELECT owner,token,qty,result FROM requests WHERE owner=? ORDER BY token',(owner,)).fetchall() if owner is not None else db.execute('SELECT owner,token,qty,result FROM requests ORDER BY owner,token').fetchall()
            if lifecycle:
                self.require_current(db)
                query = """SELECT r.owner,r.token,r.qty,r.result,
                    COALESCE(a.result,r.result),COALESCE(a.actor,''),COALESCE(a.action_token,'')
                    FROM requests r LEFT JOIN lifecycle a ON r.owner=a.owner AND r.token=a.target_token"""
                rows = db.execute(query + ' WHERE r.owner=? ORDER BY r.token',(owner,)).fetchall() if owner is not None else db.execute(query+' ORDER BY r.owner,r.token').fetchall()
            if actor is not None:
                self.require_current(db)
                if not ((actor=='admin' and owner is None) or actor==owner and actor in MEMBERS):
                    raise PermissionError('invalid audit scope')
                attempts=db.execute('SELECT action_token,owner,target_token,operation,result FROM action_attempts WHERE actor=? ORDER BY action_token',(actor,)).fetchall()
                return stock,reserved,rows,attempts
        return stock,reserved,rows

    def reserve(self, owner, token, qty, fault=False):
        if owner not in ('member','member2') or not re.fullmatch(r'[a-f0-9]{32}',token) or type(qty) is not int or not 1 <= qty <= 10:
            raise ValueError('invalid reservation')
        with closing(self.connect('rw')) as db, db:
            db.execute('BEGIN IMMEDIATE')
            self.require_current(db)
            prior = db.execute('SELECT qty,result FROM requests WHERE owner=? AND token=?',(owner,token)).fetchone()
            if prior:
                if prior[0]!=qty:
                    raise ValueError('request conflict')
                return prior[1]
            changed=db.execute('UPDATE inventory SET reserved=reserved+? WHERE id=1 AND stock-reserved>=?',(qty,qty)).rowcount
            result='RESERVED' if changed else 'INSUFFICIENT'
            if fault:
                raise RuntimeError('synthetic interruption')
            db.execute('INSERT INTO requests VALUES(?,?,?,?)',(owner,token,qty,result))
            return result

    def release(self, actor, owner, target, action_token, operation, fault=False):
        if operation == 'cancel' and actor in ('member','member2') and actor == owner:
            result = 'CANCELLED'
        elif operation == 'return' and actor == 'admin' and owner in ('member','member2'):
            result = 'RETURNED'
        else:
            raise PermissionError('not permitted')
        if not all(isinstance(x,str) and re.fullmatch(r'[a-f0-9]{32}',x) for x in (target,action_token)):
            raise ValueError('invalid token')
        with closing(self.connect('rw')) as db, db:
            db.execute('BEGIN IMMEDIATE')
            self.require_current(db)
            prior=db.execute('SELECT owner,target_token,operation,result FROM action_attempts WHERE actor=? AND action_token=?',(actor,action_token)).fetchone()
            if prior:
                if prior[:3] != (owner,target,operation):
                    raise ValueError('action token conflict')
                return prior[3]
            req=db.execute('SELECT qty,result FROM requests WHERE owner=? AND token=?',(owner,target)).fetchone()
            if req is None or req[1] != 'RESERVED' or db.execute('SELECT 1 FROM lifecycle WHERE owner=? AND target_token=?',(owner,target)).fetchone():
                result='NOT_ACTIVE'
            else:
                changed=db.execute('UPDATE inventory SET reserved=reserved-? WHERE id=1 AND reserved>=?',(req[0],req[0])).rowcount
                if changed != 1:
                    raise sqlite3.DatabaseError('inventory invariant')
                db.execute('INSERT INTO lifecycle VALUES(?,?,?,?,?)',(actor,action_token,owner,target,result))
            db.execute('INSERT INTO action_attempts VALUES(?,?,?,?,?,?)',(actor,action_token,owner,target,operation,result))
            if fault:
                raise RuntimeError('synthetic interruption')
            return result


class Site(ThreadingHTTPServer):
    def __init__(self, store, port=0):
        self.store=store
        self.credentials={u:secrets.token_urlsafe(18) for u in ('member','member2','admin')}
        self.sessions={}
        self.lock=threading.Lock()
        super().__init__(('127.0.0.1',port), Handler)
        self.origin='http://127.0.0.1:'+str(self.server_port)


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):
        pass

    def page(self,status,body,cookie=None):
        payload=('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Synthetic equipment training</title><main><h1>Equipment training</h1>'+body+'</main></html>').encode()
        self.send_response(status)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.send_header('Content-Security-Policy',"default-src 'none'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Cache-Control','no-store')
        self.send_header('Referrer-Policy','no-referrer')
        if cookie is not None:
            self.send_header('Set-Cookie','sid='+cookie+'; Path=/; HttpOnly; SameSite=Strict'+('' if cookie else '; Max-Age=0'))
        self.send_header('Content-Length',str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def host_ok(self):
        return self.headers.get_all('Host')==[self.server.origin.removeprefix('http://')]

    def session(self):
        jar=SimpleCookie()
        try:
            jar.load(self.headers.get('Cookie',''))
        except Exception:
            return '',None
        sid=jar['sid'].value if 'sid' in jar else ''
        with self.server.lock:
            s=self.server.sessions.get(sid)
            if s and s[2]<=time.monotonic():
                self.server.sessions.pop(sid,None)
                s=None
        return sid,s

    def do_GET(self):
        if not self.host_ok():
            return self.page(403,'Invalid host')
        _,s=self.session()
        if self.path=='/login' or (self.path=='/' and not s):
            return self.page(200,'<form method="post" action="/login"><label>Account <input name="user" required></label><label>Password <input type="password" name="password" required></label><button>Sign in</button></form>')
        if not s:
            return self.page(401,'Sign in required')
        if self.path not in ('/','/admin'):
            return self.page(404,'Not found')
        user,csrf,_=s
        if self.path=='/admin' and user!='admin':
            return self.page(403,'Admin only')
        try:
            stock,reserved,rows,attempts=self.server.store.view(None if user=='admin' else user,lifecycle=True,actor=user)
        except sqlite3.Error:
            return self.page(503,'Unavailable; review database, do not recreate')
        def action(row):
            owner,target,_,_,state,_,_=row
            if state!='RESERVED':
                return ''
            operation='return' if user=='admin' else 'cancel'
            owner_field='<input type="hidden" name="owner" value="'+html.escape(owner,quote=True)+'">' if user=='admin' else ''
            return '<form method="post" action="/'+operation+'"><input type="hidden" name="csrf" value="'+csrf+'">'+owner_field+'<input type="hidden" name="target" value="'+html.escape(target,quote=True)+'"><input type="hidden" name="action_token" value="'+secrets.token_hex(16)+'"><button>'+operation.title()+'</button></form>'
        table='<table><thead><tr><th>Account</th><th>Request</th><th>Quantity</th><th>Original decision</th><th>Current state</th><th>Action actor</th><th>Action ID</th><th>Action</th></tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in r)+'<td>'+action(r)+'</td></tr>' for r in rows)+'</tbody></table>'
        form='' if user=='admin' else '<form method="post" action="/reserve"><input type="hidden" name="csrf" value="'+csrf+'"><input type="hidden" name="token" value="'+secrets.token_hex(16)+'"><label>Quantity <input name="qty" type="number" min="1" max="10" required></label><button>Reserve</button></form>'
        decisions='<h2>Your operation decisions</h2><table><thead><tr><th>Action ID</th><th>Account</th><th>Request</th><th>Operation</th><th>Decision</th></tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in row)+'</tr>' for row in attempts)+'</tbody></table>'
        self.page(200,'<p>Signed in: '+user+'</p><p id="available">Available: '+str(stock-reserved)+'</p>'+form+table+decisions+'<form method="post" action="/logout"><input type="hidden" name="csrf" value="'+csrf+'"><button>Sign out</button></form>')

    def do_POST(self):
        if not self.host_ok() or self.headers.get_all('Origin')!=[self.server.origin]:
            return self.page(403,'Invalid origin')
        try:
            lengths=self.headers.get_all('Content-Length')
            if not lengths or len(lengths)!=1 or self.headers.get('Transfer-Encoding') or self.headers.get_content_type()!='application/x-www-form-urlencoded':
                raise ValueError()
            n=int(lengths[0])
            if not 0<n<=4096:
                raise ValueError()
            self.connection.settimeout(5)
            fields=parse_qs(self.rfile.read(n).decode('utf-8'),strict_parsing=True,max_num_fields=8)
            if any(len(v)!=1 for v in fields.values()):
                raise ValueError()
            data={k:v[0] for k,v in fields.items()}
        except (ValueError,UnicodeError,OSError):
            return self.page(400,'Invalid form')
        sid,s=self.session()
        if self.path=='/login':
            user=data.get('user','')
            expected=self.server.credentials.get(user)
            if set(data)!={'user','password'} or expected is None or not hmac.compare_digest(expected.encode(),data.get('password','').encode()):
                return self.page(401,'Invalid credentials')
            new=secrets.token_hex(32)
            with self.server.lock:
                self.server.sessions.pop(sid,None)
                self.server.sessions[new]=(user,secrets.token_hex(32),time.monotonic()+1800)
            return self.page(200,'<p>Signed in</p><a href="/">Dashboard</a>',new)
        if not s:
            return self.page(401,'Sign in required')
        user,csrf,_=s
        if not hmac.compare_digest(csrf.encode(),data.get('csrf','').encode()):
            return self.page(403,'Invalid CSRF')
        if self.path=='/logout' and set(data)=={'csrf'}:
            with self.server.lock:
                self.server.sessions.pop(sid,None)
            return self.page(200,'<a href="/login">Signed out</a>','')
        if self.path in ('/cancel','/return'):
            operation=self.path[1:]
            if (operation=='return' and user!='admin') or (operation=='cancel' and user=='admin'):
                return self.page(403,'Not permitted')
            expected={'csrf','target','action_token'} | ({'owner'} if operation=='return' else set())
            if set(data)!=expected:
                return self.page(400,'Invalid action')
            try:
                result=self.server.store.release(user,data.get('owner',user),data['target'],data['action_token'],operation)
            except PermissionError:
                return self.page(403,'Not permitted')
            except ValueError:
                return self.page(400,'Invalid action or conflicting token')
            except sqlite3.Error:
                return self.page(503,'Unknown result; open dashboard to reconcile, do not retry automatically')
            return self.page(409 if result=='NOT_ACTIVE' else 200,'<p id="result">'+result+'</p><a href="/">Dashboard / read-only reconciliation</a>')
        if self.path!='/reserve':
            return self.page(404,'Not found')
        if user=='admin':
            return self.page(403,'Members only')
        try:
            if set(data)!={'csrf','token','qty'} or not re.fullmatch(r'[1-9]|10',data['qty']):
                raise ValueError()
            result=self.server.store.reserve(user,data['token'],int(data['qty']))
        except ValueError:
            return self.page(400,'Invalid request or conflicting token')
        except sqlite3.Error:
            return self.page(503,'Unknown result; open dashboard to reconcile, do not retry automatically')
        self.page(200,'<p id="result">'+result+'</p><a href="/">Dashboard / read-only reconciliation</a>')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--database',type=Path,required=True)
    modes=p.add_mutually_exclusive_group()
    modes.add_argument('--initialize',action='store_true')
    modes.add_argument('--migrate-from',type=Path)
    p.add_argument('--confirm-source-offline',action='store_true')
    p.add_argument('--port',type=int,default=8765)
    a=p.parse_args()
    store=Store(a.database)
    if a.confirm_source_offline and a.migrate_from is None:
        p.error('--confirm-source-offline requires --migrate-from')
    if a.migrate_from is not None:
        if not a.confirm_source_offline:
            p.error('stop all source writers and confirm --confirm-source-offline')
        print(store.migrate_from(a.migrate_from,confirm_offline=True),flush=True)
        return  # No automatic start/cutover.
    if a.initialize:
        store.initialize()
    store.view('member',lifecycle=True)
    with Site(store,a.port) as server:
        print(server.origin,flush=True)
        print('Temporary synthetic credentials:',server.credentials,flush=True)
        server.serve_forever()


if __name__=='__main__':
    main()
