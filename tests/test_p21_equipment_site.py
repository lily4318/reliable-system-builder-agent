import http.client
import re
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlencode
from src.p21_equipment_site import Store, Site


class SiteTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store=Store(Path(tmp.name)/'demo.sqlite')
        self.store.initialize()
        self.site=Site(self.store)
        thread=threading.Thread(target=self.site.serve_forever,daemon=True)
        thread.start()
        self.addCleanup(self.site.server_close)
        self.addCleanup(thread.join,5)
        self.addCleanup(self.site.shutdown)

    def req(self,method,path,cookie='',data=None,origin=None,host=None):
        headers={}
        if cookie: headers['Cookie']=cookie
        if host: headers['Host']=host
        body=None
        if data is not None:
            body=urlencode(data)
            headers.update({'Content-Type':'application/x-www-form-urlencoded','Origin':origin or self.site.origin})
        conn=http.client.HTTPConnection('127.0.0.1',self.site.server_port,timeout=5)
        try:
            conn.request(method,path,body,headers)
            r=conn.getresponse()
            return r.status,r.read().decode(),r.getheader('Set-Cookie') or ''
        finally: conn.close()

    def login(self,user):
        status,_,cookie=self.req('POST','/login',data={'user':user,'password':self.site.credentials[user]})
        self.assertEqual(status,200)
        self.assertIn('HttpOnly; SameSite=Strict',cookie)
        return cookie.split(';')[0]

    def form(self,cookie,qty=1):
        status,body,_=self.req('GET','/',cookie)
        self.assertEqual(status,200)
        return {'csrf':re.search('name="csrf" value="([^"]+)"',body)[1],'token':re.search('name="token" value="([^"]+)"',body)[1],'qty':qty}

    def test_member_admin_end_to_end(self):
        m=self.login('member'); other=self.login('member2'); admin=self.login('admin')
        data=self.form(m,7)
        self.assertIn('RESERVED',self.req('POST','/reserve',m,data)[1])
        self.assertIn(data['token'],self.req('GET','/',m)[1])
        self.assertNotIn(data['token'],self.req('GET','/',other)[1])
        self.assertIn(data['token'],self.req('GET','/admin',admin)[1])
        self.assertIn('Available: 3',self.req('GET','/admin',admin)[1])
        self.assertIn('INSUFFICIENT',self.req('POST','/reserve',other,self.form(other,4))[1])
        self.assertEqual(self.store.view(None)[:2],(10,7))

    def test_auth_csrf_and_role(self):
        self.assertEqual(self.req('GET','/admin')[0],401)
        self.assertEqual(self.req('POST','/login',data={'user':'admin','password':'wrong'})[0],401)
        m=self.login('member'); admin=self.login('admin'); data=self.form(m)
        self.assertEqual(self.req('GET','/admin',m)[0],403)
        self.assertEqual(self.req('POST','/reserve',m,data,origin='https://foreign.invalid')[0],403)
        self.assertEqual(self.req('GET','/',m,host='foreign.invalid')[0],403)
        self.assertEqual(self.req('POST','/reserve',m,{**data,'csrf':'bad'})[0],403)
        admin_csrf=re.search('name="csrf" value="([^"]+)"',self.req('GET','/admin',admin)[1])[1]
        self.assertEqual(self.req('POST','/reserve',admin,{**data,'csrf':admin_csrf})[0],403)
        self.assertEqual(self.store.view(None)[:2],(10,0))

    def test_replay_and_payload_conflict(self):
        m=self.login('member'); data=self.form(m,2)
        for _ in range(2): self.assertIn('RESERVED',self.req('POST','/reserve',m,data)[1])
        self.assertEqual(self.req('POST','/reserve',m,{**data,'qty':3})[0],400)
        self.assertEqual(self.req('POST','/reserve',m,{**data,'owner':'admin'})[0],400)
        self.assertEqual(self.store.view(None)[:2],(10,2))

    def test_concurrent_reservations(self):
        m=self.login('member'); data=[self.form(m,3) for _ in range(8)]
        with ThreadPoolExecutor(max_workers=8) as pool:
            results=list(pool.map(lambda d:self.req('POST','/reserve',m,d),data))
        self.assertEqual(sum('id="result">RESERVED' in r[1] for r in results),3)
        self.assertEqual(self.store.view(None)[:2],(10,9))

    def test_rollback_and_readonly_reconciliation(self):
        with self.assertRaises(RuntimeError): self.store.reserve('member','a'*32,4,True)
        self.assertEqual(self.store.view(None),(10,0,[]))
        m=self.login('member'); data=self.form(m,3)
        self.req('POST','/reserve',m,data)
        before=self.store.path.read_bytes()
        self.assertIn(data['token'],self.req('GET','/',m)[1])
        self.assertEqual(before,self.store.path.read_bytes())
        self.store.path.unlink()
        self.assertEqual(self.req('GET','/',m)[0],503)
        self.assertEqual(self.req('POST','/reserve',m,data)[0],503)
        self.assertFalse(self.store.path.exists())

    def test_logout_expiry_and_invalid_inputs(self):
        m=self.login('member'); data=self.form(m)
        for qty in (-1,0,11,'1.5','1 OR 1=1'):
            self.assertEqual(self.req('POST','/reserve',m,{**data,'qty':qty})[0],400)
        self.assertEqual(self.req('POST','/reserve',m,{**data,'token':'<script>'})[0],400)
        self.assertEqual(self.req('POST','/logout',m,{'csrf':data['csrf']})[0],200)
        self.assertEqual(self.req('POST','/reserve',m,data)[0],401)
        m=self.login('member'); sid=m.split('=')[1]; s=self.site.sessions[sid]
        self.site.sessions[sid]=(s[0],s[1],0)
        self.assertEqual(self.req('GET','/admin',m)[0],401)
        self.assertEqual(self.store.view(None),(10,0,[]))
