"""Actual local HTTP routes, no credentials/real identities in repo."""
from contextlib import closing
from http.cookiejar import CookieJar
import json
import queue
import re
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request,build_opener,HTTPCookieProcessor

from src.editorial_store import Store,ROLES
from src.editorial_site import create_server,MAX_BODY


class Client:
    def __init__(self,url):
        self.url=url
        self.jar=CookieJar()
        self.opener=build_opener(HTTPCookieProcessor(self.jar))
        self.csrf=self.get('/api/bootstrap')[1]['csrf']

    def call(self,path,data=None,headers=None,raw=None):
        args={}
        if data is not None or raw is not None:
            args={'data':raw if raw is not None else json.dumps(data).encode(),
                  'method':'POST'}
        h={'Origin':self.url,'X-CSRF-Token':getattr(self,'csrf',''),'Content-Type':'application/json'}
        h.update(headers or {})
        try:
            response=self.opener.open(Request(self.url+path,headers=h,**args),timeout=5)
        except HTTPError as e:
            response=e
        with response:
            return response.status,json.load(response)

    def get(self,path,headers=None):
        return self.call(path,headers=headers)

    def login(self,name,password):
        status,data=self.call('/api/login',{'username':name,'password':password})
        if status==200:
            self.csrf=data['csrf']
        return status,data

    def logout(self):
        status,data=self.call('/api/logout',{})
        if status==200:self.csrf=data['csrf']
        return status,data

    def action(self,op,prior=None,**values):
        payload={'op':op,'token':secrets.token_hex(16),**values}
        if prior:payload.update(article_id=prior['article_id'],revision_id=prior['revision_id'],expected=prior['version'])
        return self.call('/api/action',payload)


class EditorialHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.root=Path(cls.tmp.name)
        cls.passwords={n:secrets.token_hex(12) for n in ROLES}
        cls.template=Store(cls.root/'template.sqlite')
        cls.template.initialize(cls.passwords)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.store=Store(self.root/(secrets.token_hex(8)+'.sqlite'))
        self.template.transfer(self.store.path)
        self.server=create_server(self.store.path,0)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.thread.join,5)
        self.addCleanup(self.server.shutdown)
        self.url=f'http://127.0.0.1:{self.server.server_port}'
        self.a,self.b,self.e,self.reader=(Client(self.url) for _ in range(4))
        for client,name in zip((self.a,self.b,self.e),ROLES):
            self.assertEqual(client.login(name,self.passwords[name])[0],200)

    def create(self,title='PRIVATE-ONLY',body='合成內容'):
        status,result=self.a.action('create',title=title,category='文化',body=body)
        self.assertEqual(status,200)
        return result

    def test_http_public_pointer_and_role_boundaries(self):
        x=self.create()
        aid=x['article_id']
        self.assertEqual(self.reader.get('/api/articles')[1]['total'],0)
        self.assertEqual(self.reader.get('/api/article?id='+str(aid))[0],404)
        self.assertEqual(self.reader.get('/api/workspace')[0],401)
        self.assertEqual(self.b.get('/api/workspace')[1]['revisions'],[])
        self.assertEqual(self.e.get('/api/workspace')[1]['revisions'],[])
        self.assertEqual(self.b.action('submit',x)[0],404)
        self.assertEqual(self.e.action('approve',x)[0],404)
        self.assertEqual(self.a.action('approve',x)[0],403)
        self.assertEqual(self.a.action('submit',x,actor='editor')[0],400)
        x=self.a.action('submit',x)[1]
        x=self.e.action('approve',x)[1]
        self.assertEqual(self.reader.get('/api/article?id='+str(aid))[0],404)
        x=self.e.action('publish',x)[1]
        self.assertTrue(x['ok'])
        article=self.reader.get('/api/article?id='+str(aid))[1]
        self.assertEqual(set(article),{'id','title','category','body'})
        self.assertEqual(article['title'],'PRIVATE-ONLY')
        rev=self.a.action('clone',x)[1]
        self.a.action('edit',rev,title='HIDDEN-NEW',category='科技',body='hidden')
        self.assertNotIn('HIDDEN-NEW',json.dumps(self.reader.get('/api/articles')[1]))
        self.assertNotIn('HIDDEN-NEW',json.dumps(self.e.get('/api/workspace')[1]))
        self.assertEqual(self.reader.get('/api/article?id='+str(aid))[1]['title'],'PRIVATE-ONLY')
        self.assertEqual(self.reader.get('/api/articles?q=HIDDEN-NEW')[1]['total'],0)

    def test_http_csrf_origin_shape_and_cookie_guards(self):
        x=self.create()
        payload={'op':'submit','token':secrets.token_hex(16),'article_id':x['article_id'],
                 'revision_id':x['revision_id'],'expected':x['version']}
        for headers in ({'X-CSRF-Token':''},{'Origin':'https://invalid.example'},{'Host':'attacker.invalid'}):
            self.assertEqual(self.a.call('/api/action',payload,headers)[0],403)
        self.assertEqual(self.a.call('/api/action',raw=b'{"op":"create","op":"submit"}')[0],400)
        self.assertEqual(self.a.call('/api/action',raw=b'x'*(MAX_BODY+1))[0],400)
        self.assertEqual(self.a.get('/api/articles?page=1&page=2')[0],400)
        self.assertEqual(self.a.get('/api/articles?page=-1')[0],400)
        self.assertEqual(self.a.get('/api/articles?q='+('x'*121))[0],400)
        self.assertEqual(self.a.call('/test-result',{'status':'PASS'})[0],404)
        self.assertEqual(self.a.get('/api/receipt?token='+payload['token'])[1]['observed'],False)
        self.assertEqual(self.a.get('/api/workspace')[1]['revisions'][0]['status'],'DRAFT')
        first=self.a.call('/api/action',payload)
        self.assertEqual(first,self.a.call('/api/action',payload))
        self.assertEqual(self.a.get('/api/receipt?token='+payload['token'])[1]['result'],first[1])
        self.assertFalse(self.b.get('/api/receipt?token='+payload['token'])[1]['observed'])
        raw=self.a.opener.open(self.url+'/')
        with raw:
            self.assertIn("frame-ancestors 'none'",raw.headers['Content-Security-Policy'])
            self.assertEqual(raw.headers['Cache-Control'],'no-store')
            self.assertNotIn(b'browser-test.js',raw.read())

    def test_http_session_expiry_logout_and_restart_persistence(self):
        self.assertEqual(self.reader.login('author-a','bad password')[0],401)
        token=next(c.value for c in self.a.jar if c.name=='editorial_session')
        cookie='editorial_session='+token
        self.assertEqual(self.a.logout()[0],200)
        self.assertEqual(self.reader.get('/api/workspace',{'Cookie':cookie})[0],401)
        self.a.login('author-a',self.passwords['author-a'])
        with closing(self.store.connect('rw')) as db,db:
            db.execute("UPDATE sessions SET expires=0 WHERE account_id=(SELECT id FROM accounts WHERE username='author-a')")
        self.assertEqual(self.a.get('/api/workspace')[0],401)
        self.a=Client(self.url)
        self.a.login('author-a',self.passwords['author-a'])
        x=self.create(title='RESTART')
        x=self.a.action('submit',x)[1]
        x=self.e.action('approve',x)[1]
        x=self.e.action('publish',x)[1]
        # New process reading exactly the same durable database.
        out=subprocess.run([sys.executable,'-c','from src.editorial_store import Store;import sys,json;print(json.dumps(Store(sys.argv[1]).public_list()))',str(self.store.path)],
                           capture_output=True,check=True,timeout=10)
        self.assertEqual(json.loads(out.stdout)['items'][0]['title'],'RESTART')
        second=create_server(self.store.path,0)
        thread=threading.Thread(target=second.serve_forever,daemon=True)
        thread.start()
        try:
            client=Client(f'http://127.0.0.1:{second.server_port}')
            self.assertEqual(client.get('/api/article?id='+str(x['article_id']))[1]['title'],'RESTART')
        finally:
            second.shutdown();second.server_close();thread.join(5)


    def test_cli_fresh_initialization_and_two_process_restarts(self):
        fresh=Store(self.root/(secrets.token_hex(8)+'.fresh'))
        cmd=[sys.executable,'-m','src.editorial_site']
        result=subprocess.run(cmd+['init','--db',str(fresh.path)],
            input='\n'.join(self.passwords[n] for n in ROLES)+'\n',text=True,
            capture_output=True,check=True,timeout=15)
        self.assertIn('EDITORIAL_INITIALIZED',result.stdout)
        verified=subprocess.run(cmd+['verify','--db',str(fresh.path)],capture_output=True,check=True,timeout=10)
        self.assertIn(b'EDITORIAL_INTEGRITY_OK',verified.stdout)
        for phase in (0,1):
            proc=subprocess.Popen(cmd+['serve','--db',str(fresh.path),'--port','0'],
                                  stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            try:
                lines=queue.Queue()
                threading.Thread(target=lambda:lines.put(proc.stdout.readline()),daemon=True).start()
                line=lines.get(timeout=15)
                match=re.fullmatch(r'Local synthetic site: (http://127\.0\.0\.1:[0-9]+/)\n',line)
                self.assertIsNotNone(match)
                client=Client(match.group(1).rstrip('/'))
                if phase==0:
                    self.assertEqual(client.get('/api/articles')[1]['total'],0)
                    self.assertEqual(client.login('author-a',self.passwords['author-a'])[0],200)
                    x=client.action('create',title='CLI persisted',category='生活',body='first process')[1]
                    x=client.action('submit',x)[1]
                    self.assertEqual(client.logout()[0],200)
                    self.assertEqual(client.login('editor',self.passwords['editor'])[0],200)
                    x=client.action('approve',x)[1]
                    self.assertTrue(client.action('publish',x)[1]['ok'])
                else:
                    self.assertEqual(client.get('/api/articles')[1]['items'][0]['title'],'CLI persisted')
            finally:
                if proc.poll() is None:
                    proc.terminate()
                    try:proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:proc.kill();proc.wait()
                proc.stdout.close();proc.stderr.close()
