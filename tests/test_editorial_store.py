import copy
import secrets
import sqlite3
import json
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path

from src.editorial_store import Store, ROLES


class EditorialStoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.root=Path(cls.tmp.name)
        cls.passwords={name:secrets.token_hex(12) for name in ROLES}
        cls.template=Store(cls.root/'template.sqlite')
        cls.template.initialize(cls.passwords)
        cls.sessions={name:cls.template.login(name,pw) for name,pw in cls.passwords.items()}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.store=Store(self.root/(secrets.token_hex(8)+'.sqlite'))
        self.template.transfer(self.store.path)
        self.a,self.b,self.e=(self.sessions[n] for n in ROLES)

    def payload(self,op,prior=None,**kwargs):
        p={'op':op,'token':secrets.token_hex(16)}
        if prior:
            p.update(article_id=prior['article_id'],revision_id=prior['revision_id'],expected=prior['version'])
        p.update(kwargs)
        return p

    def act(self,s,op,prior=None,**kwargs):
        return self.store.action(s,self.payload(op,prior,**kwargs))

    def create(self,session=None,title='合成文章',body='初稿'):
        return self.act(session or self.a,'create',title=title,category='文化',body=body)

    def publish(self):
        x=self.create()
        x=self.act(self.a,'submit',x)
        x=self.act(self.e,'approve',x)
        return self.act(self.e,'publish',x)

    def test_review_publish_revise_withdraw_republish(self):
        x=self.create()
        aid=x['article_id']
        self.assertIsNone(self.store.public_detail(aid))
        self.assertEqual(self.store.workspace(self.e)['revisions'],[])
        self.assertEqual(self.store.workspace(self.b)['revisions'],[])
        x=self.act(self.a,'submit',x)
        self.assertEqual(self.act(self.a,'edit',x,title='x',category='文化',body='x')['code'],'INVALID_STATE')
        x=self.act(self.e,'return',x,reason='請修改')
        self.assertEqual(self.store.workspace(self.a)['revisions'][0]['reason'],'請修改')
        x=self.act(self.a,'edit',x,title='新標題',category='科技',body='<script>純文字</script>')
        self.assertEqual(self.store.workspace(self.e)['revisions'],[])
        author_history=self.store.workspace(self.a)
        self.assertEqual(author_history['revisions'][0]['version_counter'],4)
        self.assertEqual(next(e for e in author_history['events'] if e['action']=='return')['review_reason'],'請修改')
        x=self.act(self.a,'submit',x)
        x=self.act(self.e,'approve',x)
        self.assertIsNone(self.store.public_detail(aid))
        x=self.act(self.e,'publish',x)
        self.assertEqual(self.store.public_detail(aid)['body'],'<script>純文字</script>')
        old=x
        x=self.act(self.a,'clone',x)
        self.assertEqual(self.act(self.a,'clone',old,expected=x['version'])['code'],'OPEN_REVISION')
        x=self.act(self.a,'edit',x,title='第二版',category='生活',body='只供草稿')
        self.assertEqual(self.store.public_detail(aid)['title'],'新標題')
        x=self.act(self.a,'submit',x)
        x=self.act(self.e,'approve',x)
        self.assertEqual(self.store.public_detail(aid)['title'],'新標題')
        x=self.act(self.e,'publish',x)
        self.assertEqual(self.store.public_detail(aid)['title'],'第二版')
        self.assertEqual([r['status'] for r in self.store.workspace(self.a)['revisions']],['PUBLISHED','SUPERSEDED'])
        x=self.act(self.e,'withdraw',x)
        self.assertIsNone(self.store.public_detail(aid))
        x=self.act(self.a,'clone',x)
        x=self.act(self.a,'submit',x)
        x=self.act(self.e,'approve',x)
        self.assertTrue(self.act(self.e,'publish',x)['ok'])
        self.assertEqual(self.store.public_list(category='生活',query='第二')['total'],1)

    def test_ownership_and_role_negative(self):
        x=self.create()
        for s,op,kw in ((self.b,'submit',{}),(self.e,'approve',{}),(self.a,'publish',{}),
                       (self.e,'edit',{'title':'x','body':'x','category':'文化'})):
            self.assertFalse(self.act(s,op,x,**kw)['ok'])
        self.assertFalse(self.create(self.e)['ok'])
        self.assertEqual(len(self.store.workspace(self.a)['events']),1)
        self.assertIsNone(self.store.public_detail(x['article_id']))
        with self.assertRaises(PermissionError):
            self.store.action('bad',self.payload('submit',x))

    def test_race_receipt_and_fault(self):
        x=self.create()
        p=self.payload('submit',x)
        q=self.payload('submit',x)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda v:self.store.action(self.a,v),(p,q)))
        self.assertEqual(sorted(r['code'] for r in results),['COMMITTED','STALE'])
        self.assertEqual(self.store.action(self.a,p),results[0])
        self.assertEqual(self.store.receipt(self.a,p['token'])['result'],results[0])
        self.assertFalse(self.store.receipt(self.b,p['token'])['observed'])
        changed={**p,'expected':2}
        self.assertEqual(self.store.action(self.a,changed)['code'],'TOKEN_CONFLICT')
        current=next(r for r in results if r['ok'])
        approve=self.payload('approve',current)
        before=self.store.workspace(self.e)
        with self.assertRaises(RuntimeError):
            self.store.action(self.e,approve,fault=True)
        self.assertFalse(self.store.receipt(self.e,approve['token'])['observed'])
        self.assertEqual(self.store.workspace(self.e),before)
        new=self.store.action(self.e,approve)
        self.assertTrue(new['ok'])
        publish=self.payload('publish',new)
        first=self.store.action(self.e,publish)
        self.assertEqual(self.store.action(self.e,publish),first)
        self.assertEqual(len([x for x in self.store.workspace(self.e)['events'] if x['action']=='publish']),1)

    def test_validation_and_pagination(self):
        for kw in ({'title':' '},{'body':'x'*10001},{'category':'invalid'},{'title':'x'*121},{'body':'a\0b'}):
            data={'title':'ok','body':'ok','category':'文化',**kw}
            with self.assertRaises(ValueError):
                self.act(self.a,'create',**data)
        self.assertEqual(self.store.workspace(self.a)['revisions'],[])
        for i in range(21):
            x=self.create(title='測試 %02d'%i,body='x'*10000 if i==0 else '內容')
            x=self.act(self.a,'submit',x)
            x=self.act(self.e,'approve',x)
            self.assertTrue(self.act(self.e,'publish',x)['ok'])
        self.assertEqual(len(self.store.public_list()['items']),20)
        self.assertEqual(len(self.store.public_list(page=2)['items']),1)
        self.assertEqual(self.store.public_list(page=3)['items'],[])
        self.assertEqual(self.store.public_list(query="' OR 1=1 --")['items'],[])
        self.assertEqual(self.store.public_list(category='科技')['total'],0)

    def test_auth_expiry_rotation_and_backup_restore(self):
        self.assertIsNone(self.store.login('author-a','wrong password'))
        token=self.store.login('author-a',self.passwords['author-a'],self.a)
        with self.assertRaises(PermissionError):
            self.store.actor(self.a)
        self.assertEqual(self.store.actor(token)['role'],'author')
        with closing(self.store.connect('rw')) as db,db:
            db.execute('UPDATE sessions SET expires=0 WHERE account_id=1')
        with self.assertRaises(PermissionError):
            self.store.actor(token)
        self.a=self.store.login('author-a',self.passwords['author-a'])
        x=self.publish()
        backup=Store(self.root/(secrets.token_hex(8)+'.backup'))
        self.store.transfer(backup.path)
        restored=Store(self.root/(secrets.token_hex(8)+'.restore'))
        backup.transfer(restored.path,restore=True)
        self.assertEqual(restored.public_detail(x['article_id']),self.store.public_detail(x['article_id']))
        with self.assertRaises(PermissionError):
            restored.actor(self.a)
        with self.assertRaises(FileExistsError):
            self.store.transfer(backup.path)
        with self.assertRaises(FileExistsError):
            self.store.initialize(self.passwords)
        missing=Store(self.root/'absent.sqlite')
        with self.assertRaises(sqlite3.Error):
            missing.public_list()
        self.assertFalse(missing.path.exists())
        self.store.logout(self.a)
        with self.assertRaises(PermissionError):
            self.store.actor(self.a)


    def test_process_cut_atomic_receipt_and_cli_backup_restore(self):
        x=self.create()
        x=self.act(self.a,'submit',x)
        x=self.act(self.e,'approve',x)
        p=self.payload('publish',x)
        before=self.store.workspace(self.e)
        script="""import json,os,sys
from src.editorial_store import Store
s=Store(sys.argv[1]); token,payload=json.load(sys.stdin)
original=Store._audit
def cut(*args,**kwargs):
    original(*args,**kwargs)
    os._exit(17)
Store._audit=staticmethod(cut)
s.action(token,payload)
"""
        proc=subprocess.run([sys.executable,'-c',script,str(self.store.path)],
                            input=json.dumps([self.e,p]),text=True,capture_output=True,timeout=10)
        self.assertEqual(proc.returncode,17)
        self.assertEqual(self.store.workspace(self.e),before)
        self.assertIsNone(self.store.public_detail(x['article_id']))
        self.assertFalse(self.store.receipt(self.e,p['token'])['observed'])
        self.assertTrue(self.store.action(self.e,p)['ok'])
        first=self.root/(secrets.token_hex(8)+'.backup')
        second=self.root/(secrets.token_hex(8)+'.restored')
        for op,source,target in (('backup',self.store.path,first),('restore',first,second)):
            result=subprocess.run([sys.executable,'-m','src.editorial_site',op,'--db',str(source),'--target',str(target)],
                                  capture_output=True,check=True,timeout=10)
            self.assertIn(b'EDITORIAL_COPY_VERIFIED',result.stdout)
        restored=Store(second)
        self.assertEqual(restored.public_detail(x['article_id']),self.store.public_detail(x['article_id']))
        self.assertEqual(restored.public_list(),self.store.public_list())
        with self.assertRaises(PermissionError):
            restored.actor(self.e)
