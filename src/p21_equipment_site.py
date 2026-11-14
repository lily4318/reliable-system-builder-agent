"""Loopback-only synthetic equipment site; never deploy or use real identities."""
import argparse
import hmac
import html
import re
import secrets
import sqlite3
import threading
import time
from contextlib import closing
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs


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
            db.execute('INSERT INTO inventory VALUES(1,10,0)')

    def view(self, owner):
        with closing(self.connect('ro')) as db:
            db.execute('BEGIN')
            stock,reserved = db.execute('SELECT stock,reserved FROM inventory').fetchone()
            rows = db.execute('SELECT owner,token,qty,result FROM requests WHERE owner=? ORDER BY token',(owner,)).fetchall() if owner is not None else db.execute('SELECT owner,token,qty,result FROM requests ORDER BY owner,token').fetchall()
        return stock,reserved,rows

    def reserve(self, owner, token, qty, fault=False):
        if owner not in ('member','member2') or not re.fullmatch(r'[a-f0-9]{32}',token) or type(qty) is not int or not 1 <= qty <= 10:
            raise ValueError('invalid reservation')
        with closing(self.connect('rw')) as db, db:
            db.execute('BEGIN IMMEDIATE')
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
            stock,reserved,rows=self.server.store.view(None if user=='admin' else user)
        except sqlite3.Error:
            return self.page(503,'Unavailable; review database, do not recreate')
        table='<table><thead><tr><th>Account</th><th>Request</th><th>Quantity</th><th>Result</th></tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in r)+'</tr>' for r in rows)+'</tbody></table>'
        form='' if user=='admin' else '<form method="post" action="/reserve"><input type="hidden" name="csrf" value="'+csrf+'"><input type="hidden" name="token" value="'+secrets.token_hex(16)+'"><label>Quantity <input name="qty" type="number" min="1" max="10" required></label><button>Reserve</button></form>'
        self.page(200,'<p>Signed in: '+user+'</p><p id="available">Available: '+str(stock-reserved)+'</p>'+form+table+'<form method="post" action="/logout"><input type="hidden" name="csrf" value="'+csrf+'"><button>Sign out</button></form>')

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
    p.add_argument('--initialize',action='store_true')
    p.add_argument('--port',type=int,default=8765)
    a=p.parse_args()
    store=Store(a.database)
    if a.initialize:
        store.initialize()
    store.view('member')
    with Site(store,a.port) as server:
        print(server.origin,flush=True)
        print('Temporary synthetic credentials:',server.credentials,flush=True)
        server.serve_forever()


if __name__=='__main__':
    main()
