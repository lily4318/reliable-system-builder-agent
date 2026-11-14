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

    def action(self,cookie,target,token,owner=None):
        status,body,_=self.req('GET','/',cookie)
        self.assertEqual(status,200)
        data={'csrf':re.search('name="csrf" value="([^"]+)"',body)[1],
              'target':target,'action_token':token}
        if owner is not None: data['owner']=owner
        return data

    def test_lifecycle_cancel_return_and_audit(self):
        m=self.login('member'); other=self.login('member2'); admin=self.login('admin')
        first=self.form(m,4); second=self.form(other,3)
        self.req('POST','/reserve',m,first)
        self.req('POST','/reserve',other,second)
        self.assertIn('action="/cancel"',self.req('GET','/',m)[1])
        self.assertIn('action="/return"',self.req('GET','/admin',admin)[1])
        cancel=self.action(m,first['token'],'b'*32)
        for _ in range(2):
            status,body,_=self.req('POST','/cancel',m,cancel)
            self.assertEqual(status,200); self.assertIn('CANCELLED',body)
        returned=self.action(admin,second['token'],'c'*32,'member2')
        for _ in range(2):
            status,body,_=self.req('POST','/return',admin,returned)
            self.assertEqual(status,200); self.assertIn('RETURNED',body)
        self.assertEqual(self.store.view(None)[:2],(10,0))
        audit=self.req('GET','/admin',admin)[1]
        for value in ('CANCELLED','RETURNED','b'*32,'c'*32):
            self.assertIn(value,audit)
        self.assertNotIn('c'*32,self.req('GET','/',m)[1])
        self.assertNotIn('action="/cancel"',self.req('GET','/',m)[1])
        self.assertEqual(self.req('POST','/cancel',m,{**cancel,'action_token':'d'*32})[0],409)
        self.assertEqual(self.req('POST','/reserve',m,first)[0],200)
        self.assertEqual(self.store.view(None)[:2],(10,0))

    def test_lifecycle_permission_conflicts_and_insufficient(self):
        m=self.login('member'); other=self.login('member2'); admin=self.login('admin')
        first=self.form(m,10); self.req('POST','/reserve',m,first)
        second=self.form(other,1); self.req('POST','/reserve',other,second)
        cancel=self.action(m,first['token'],'a'*32)
        foreign=self.action(other,first['token'],'b'*32)
        self.assertEqual(self.req('POST','/cancel',other,foreign)[0],409)
        self.assertEqual(self.req('POST','/cancel',other,{**foreign,'owner':'member'})[0],400)
        self.assertEqual(self.req('POST','/return',m,{**cancel,'owner':'member'})[0],403)
        self.assertEqual(self.req('POST','/cancel',admin,self.action(admin,first['token'],'c'*32))[0],403)
        self.assertEqual(self.req('POST','/cancel',m,{**cancel,'csrf':'bad'})[0],403)
        self.assertEqual(self.req('POST','/cancel',m,cancel,origin='https://foreign.invalid')[0],403)
        self.assertEqual(self.req('POST','/cancel','',cancel)[0],401)
        denied=self.action(admin,second['token'],'d'*32,'member2')
        self.assertEqual(self.req('POST','/return',admin,denied)[0],409)
        self.assertEqual(self.store.view(None)[:2],(10,10))
        self.assertEqual(self.req('POST','/cancel',m,cancel)[0],200)
        self.assertEqual(self.req('POST','/cancel',m,{**cancel,'target':second['token']})[0],400)
        self.assertEqual(self.store.view(None)[:2],(10,0))

    def test_cancel_return_race(self):
        m=self.login('member'); admin=self.login('admin')
        first=self.form(m,7); self.req('POST','/reserve',m,first)
        cancel=self.action(m,first['token'],'a'*32)
        returned=self.action(admin,first['token'],'b'*32,'member')
        jobs=[('/cancel',m,{**cancel,'action_token':format(i,'032x')}) if i%2 else
              ('/return',admin,{**returned,'action_token':format(i,'032x')}) for i in range(1,9)]
        with ThreadPoolExecutor(max_workers=8) as pool:
            results=list(pool.map(lambda j:self.req('POST',j[0],j[1],j[2])[0],jobs))
        self.assertEqual(sorted(results),[200]+[409]*7)
        self.assertEqual(self.store.view(None)[:2],(10,0))
        with self.store.connect('ro') as db:
            self.assertEqual(db.execute('SELECT count(*) FROM lifecycle').fetchone()[0],1)

    def test_release_failure_rollback_and_missing_db(self):
        m=self.login('member')
        first=self.form(m,6); self.req('POST','/reserve',m,first)
        with self.assertRaises(RuntimeError):
            self.store.release('member','member',first['token'],'a'*32,'cancel',fault=True)
        self.assertEqual(self.store.view(None)[:2],(10,6))
        self.assertEqual(self.store.view('member',lifecycle=True)[2][0][4],'RESERVED')
        action=self.action(m,first['token'],'a'*32)
        self.assertEqual(self.req('POST','/cancel',m,action)[0],200)
        before=self.store.path.read_bytes()
        self.assertIn('a'*32,self.req('GET','/',m)[1])
        self.assertEqual(self.store.path.read_bytes(),before)
        self.store.path.unlink()
        self.assertEqual(self.req('POST','/cancel',m,action)[0],503)
        self.assertFalse(self.store.path.exists())
