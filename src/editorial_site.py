"""Local-only synthetic editorial website. No external deployment or real personal data."""
import argparse
import getpass
import hmac
from http.cookies import SimpleCookie,CookieError
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import sqlite3
import sys
from urllib.parse import parse_qs, urlsplit

from src.editorial_store import Store, ROLES, TOKEN, digest, CATEGORIES

ASSETS=Path(__file__).resolve().parents[1]/'examples/editorial-site'
MAX_BODY=131072
SOCKET_IDLE_TIMEOUT=5.0


def unique(pairs):
    data={}
    for key,value in pairs:
        if key in data:
            raise ValueError('duplicate key')
        data[key]=value
    return data


def csrf(token):
    return digest('editorial-csrf:'+token)


def create_server(path,port=8777,*,test_mode=False):
    store=Store(path)
    store.verify()
    assets={'/':('index.html','text/html; charset=utf-8'),
            '/app.js':('app.js','text/javascript; charset=utf-8'),
            '/style.css':('style.css','text/css; charset=utf-8')}
    if test_mode:
        assets['/browser-test.js']=('browser-test.js','text/javascript; charset=utf-8')
    class Handler(BaseHTTPRequestHandler):
        # Bounded idle socket operations, not an overall request deadline.
        timeout=SOCKET_IDLE_TIMEOUT

        def log_message(self,*args):
            pass

        def send_data(self,status,data,mime,cookies=()):
            self.close_connection=True
            self.send_response(status)
            self.send_header('Connection','close')
            self.send_header('Content-Type',mime)
            self.send_header('Content-Length',str(len(data)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('X-Frame-Options','DENY')
            self.send_header('Referrer-Policy','no-referrer')
            self.send_header('Content-Security-Policy',
                "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; "
                "base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
            for item in cookies:
                self.send_header('Set-Cookie',item)
            self.end_headers()
            self.wfile.write(data)

        def respond(self,status,value,cookies=()):
            self.send_data(status,json.dumps(value,ensure_ascii=True,separators=(',',':')).encode('ascii'),
                           'application/json; charset=utf-8',cookies)

        def cookie(self,name):
            try:
                c=SimpleCookie(self.headers.get('Cookie',''))
                value=c[name].value if name in c else ''
                return value if TOKEN.fullmatch(value) else ''
            except (ValueError,TypeError,CookieError):
                return ''

        def valid_host(self):
            return self.headers.get_all('Host')==[f'127.0.0.1:{self.server.server_port}']

        def params(self,allowed):
            raw=urlsplit(self.path)
            if len(raw.query)>2048:
                raise ValueError('query too long')
            values=parse_qs(raw.query,keep_blank_values=True,max_num_fields=4)
            if set(values)-set(allowed) or any(len(v)!=1 for v in values.values()):
                raise ValueError('invalid query')
            return {k:v[0] for k,v in values.items()}

        def do_GET(self):
            if not self.valid_host():
                return self.respond(403,{'error':'FORBIDDEN'})
            try:
                path=urlsplit(self.path).path
                if path in assets:
                    filename,mime=assets[path]
                    data=(ASSETS/filename).read_bytes()
                    if path=='/' and test_mode:
                        data=data.replace(b'</body>',b'<script src="/browser-test.js" defer></script></body>')
                    return self.send_data(200,data,mime)
                if path=='/api/bootstrap':
                    self.params(())
                    token=self.cookie('editorial_session')
                    try:
                        actor=store.actor(token)
                        return self.respond(200,{'actor':actor,'csrf':csrf(token),'categories':CATEGORIES})
                    except PermissionError:
                        nonce=secrets.token_hex(32)
                        return self.respond(200,{'actor':None,'csrf':csrf(nonce),'categories':CATEGORIES},
                            (f'editorial_preauth={nonce}; Path=/; HttpOnly; SameSite=Strict; Max-Age=600',
                             'editorial_session=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0'))
                if path=='/api/articles':
                    q=self.params(('q','category','page'))
                    return self.respond(200,store.public_list(q.get('q',''),q.get('category',''),int(q.get('page','1'))))
                if path=='/api/article':
                    q=self.params(('id',))
                    aid=int(q.get('id','0'))
                    if not 0<aid<2**63:
                        raise ValueError('invalid id')
                    result=store.public_detail(aid)
                    return self.respond(200,result) if result else self.respond(404,{'error':'NOT_FOUND'})
                if path=='/api/workspace':
                    self.params(())
                    return self.respond(200,store.workspace(self.cookie('editorial_session')))
                if path=='/api/receipt':
                    q=self.params(('token',))
                    return self.respond(200,store.receipt(self.cookie('editorial_session'),q.get('token')))
                return self.respond(404,{'error':'NOT_FOUND'})
            except PermissionError:
                return self.respond(401,{'error':'AUTH_REQUIRED'})
            except (ValueError,TypeError,OverflowError):
                return self.respond(400,{'error':'INVALID_INPUT'})
            except (OSError,sqlite3.Error):
                return self.respond(503,{'error':'UNAVAILABLE'})

        def do_POST(self):
            if not self.valid_host() or self.headers.get_all('Origin')!=[f'http://127.0.0.1:{self.server.server_port}']:
                return self.respond(403,{'error':'FORBIDDEN'})
            path=self.path
            if path not in ('/api/login','/api/logout','/api/action') and not (test_mode and path=='/test-result'):
                return self.respond(404,{'error':'NOT_FOUND'})
            session=self.cookie('editorial_session')
            # Bootstrap nonce protects login; authenticated mutation uses a
            # domain-separated hash of the current random session cookie.
            # Test-only report still requires the current bootstrap token.
            token=(session or self.cookie('editorial_preauth')) if path in ('/api/login','/test-result') else session
            header=self.headers.get('X-CSRF-Token','')
            if not token or not TOKEN.fullmatch(header) or not hmac.compare_digest(header,csrf(token)):
                return self.respond(403,{'error':'FORBIDDEN'})
            try:
                sizes=self.headers.get_all('Content-Length') or []
                if len(sizes)!=1 or self.headers.get_all('Transfer-Encoding') is not None or self.headers.get_content_type()!='application/json':
                    raise ValueError('invalid body')
                # RFC 9110 8.6 / RFC 9112 6.3: decimal octets, not Python's
                # permissive int grammar. Strip only HTTP optional whitespace.
                raw_size=sizes[0].strip(' \t')
                significant=raw_size.lstrip('0')
                if (not raw_size.isascii() or not raw_size.isdecimal()
                        or not significant or len(significant)>len(str(MAX_BODY))):
                    raise ValueError('invalid size')
                size=int(significant)
                if not 0<size<=MAX_BODY:
                    raise ValueError('invalid size')
                try:
                    raw_body=self.rfile.read(size)
                except TimeoutError:
                    return self.respond(408,{'error':'INCOMPLETE_REQUEST'})
                if len(raw_body)!=size:
                    raise ValueError('incomplete body')
                data=json.loads(raw_body.decode('utf-8'),object_pairs_hook=unique)
                if not isinstance(data,dict):
                    raise ValueError('object required')
                if path=='/api/login':
                    if set(data)!={'username','password'}:
                        raise ValueError('invalid login')
                    fresh=store.login(data['username'],data['password'],session)
                    if fresh is None:
                        return self.respond(401,{'error':'INVALID_LOGIN'})
                    actor=store.actor(fresh)
                    return self.respond(200,{'actor':actor,'csrf':csrf(fresh)},(
                        f'editorial_session={fresh}; Path=/; HttpOnly; SameSite=Strict; Max-Age=1800',
                        'editorial_preauth=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0'))
                if path=='/api/logout':
                    if data:
                        raise ValueError('invalid logout')
                    store.logout(session)
                    nonce=secrets.token_hex(32)
                    return self.respond(200,{'actor':None,'csrf':csrf(nonce)},(
                        'editorial_session=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0',
                        f'editorial_preauth={nonce}; Path=/; HttpOnly; SameSite=Strict; Max-Age=600'))
                if path=='/test-result':
                    if data.get('status') not in ('PASS','FAIL') or self.server.test_result is not None:
                        raise ValueError('invalid test report')
                    self.server.test_result=data
                    return self.respond(200,{'recorded':True})
                result=store.action(session,data)
                if result['ok']:
                    status=200
                else:
                    status={'FORBIDDEN':403,'NOT_FOUND':404}.get(result['code'],409)
                return self.respond(status,result)
            except PermissionError:
                return self.respond(401,{'error':'AUTH_REQUIRED'})
            except (ValueError,TypeError,UnicodeError,RecursionError,OverflowError):
                return self.respond(400,{'error':'INVALID_INPUT'})
            except (OSError,sqlite3.Error):
                return self.respond(503,{'error':'UNAVAILABLE_RECONCILE'})

    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    server.test_result=None
    return server


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=('init','serve','verify','backup','restore'))
    p.add_argument('--db',type=Path,required=True)
    p.add_argument('--target',type=Path)
    p.add_argument('--port',type=int,default=8777)
    args=p.parse_args()
    try:
        store=Store(args.db)
        if args.command=='init':
            if store.path.exists():
                raise FileExistsError('database exists')
            passwords={n:getpass.getpass('Synthetic '+n+' password (min 12 chars): ') for n in ROLES}
            store.initialize(passwords)
            print('EDITORIAL_INITIALIZED')
        elif args.command=='serve':
            with create_server(args.db,args.port) as server:
                print(f'Local synthetic site: http://127.0.0.1:{server.server_port}/',flush=True)
                server.serve_forever()
        elif args.command=='verify':
            store.verify()
            print('EDITORIAL_INTEGRITY_OK')
        else:
            if args.target is None:
                raise ValueError('new target path required')
            store.transfer(args.target,restore=args.command=='restore')
            print('EDITORIAL_COPY_VERIFIED')
        return 0
    except KeyboardInterrupt:
        return 0
    except (OSError,ValueError,sqlite3.Error):
        print('EDITORIAL_BLOCKED: verify path, schema, permissions and input; existing files not overwritten',file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
