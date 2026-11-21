"""Offline Chromium + temporary SQLite host bridge. Synthetic data only."""
import json
from contextlib import closing
import sqlite3
import shutil
import tempfile
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = r'''<!doctype html><meta charset="utf-8"><button id="start">Start</button>
<button id="retry">Interrupt and retry</button><div id="stim" hidden>●</div>
<output id="status">ready</output><script>
const doc=String(performance.timeOrigin)+':'+Math.random(), origin=performance.timeOrigin;
let a=null, onset=null, busy=false;
const stim=document.querySelector('#stim'), status=document.querySelector('#status');
async function begin(retry=false){
 if(busy)return 'BUSY';busy=true;
 try{const s=await bridge('read',{});const r=await bridge('begin',{doc,origin,retry,expected:s.attempts.at(-1)?.id??null});
 if(r.code==='STARTED'){a=r.id;stim.hidden=false;onset=performance.now();}
 status.textContent=r.code;return r.code;
 }finally{busy=false;}
}
window.args=()=>({id:a,doc,origin,onset,response:performance.now(),key:'KeyF'});
window.begin=begin;window.finish=async(p,fault='none')=>bridge('finish',{...p,fault});
const fail=()=>status.textContent='HOLD';
document.querySelector('#start').onclick=()=>begin().catch(fail);
document.querySelector('#retry').onclick=()=>begin(true).catch(fail);
window.addEventListener('keydown',e=>{if(!e.isTrusted||e.repeat||!a||stim.hidden||!['KeyF','KeyJ'].includes(e.code))return;
 stim.hidden=true;finish({...args(),response:e.timeStamp,key:e.code}).then(r=>status.textContent=r.code).catch(fail);
});</script>'''

class Store:
    def __init__(self,path):
        self.path=path
        with closing(sqlite3.connect(path)) as c, c:
            c.executescript('CREATE TABLE attempts(id INTEGER PRIMARY KEY, parent INTEGER, doc TEXT, origin REAL, status TEXT, rt REAL, onset REAL, response REAL, key TEXT, version TEXT); CREATE TABLE receipts(id INTEGER PRIMARY KEY,payload TEXT NOT NULL);')
    def call(self,op,p):
        with closing(sqlite3.connect(self.path)) as c, c:
            c.row_factory=sqlite3.Row
            if op=='read':
                return {t:[dict(r) for r in c.execute('SELECT * FROM '+t+' ORDER BY id')] for t in ('attempts','receipts')}
            c.execute('BEGIN IMMEDIATE')
            last=c.execute('SELECT * FROM attempts ORDER BY id DESC LIMIT 1').fetchone()
            if op=='begin':
                if (last['id'] if last else None)!=p['expected']:return {'code':'STALE'}
                if p['retry']:
                    if not last or last['status']!='pending':return {'code':'HOLD'}
                    c.execute("UPDATE attempts SET status='interrupted' WHERE id=?",(last['id'],))
                elif last:return {'code':'HOLD'}
                i=c.execute("INSERT INTO attempts(parent,doc,origin,status,version) VALUES (?,?,?,'pending','recovery-v1')",(last['id'] if last else None,p['doc'],p['origin'])).lastrowid
                return {'code':'STARTED','id':i}
            if op!='finish':return {'code':'INVALID'}
            keys=('id','doc','origin','onset','response','key');payload=json.dumps([p[k] for k in keys],allow_nan=False)
            old=c.execute('SELECT payload FROM receipts WHERE id=?',(p['id'],)).fetchone()
            if old:return {'code':'REPLAY' if old[0]==payload else 'CONFLICT'}
            if not last or last['id']!=p['id'] or last['status']!='pending' or (last['doc'],last['origin'])!=(p['doc'],p['origin']):return {'code':'STALE'}
            if not 0<=p['onset']<=p['response'] or p['key'] not in ('KeyF','KeyJ'):return {'code':'INVALID'}
            c.execute("UPDATE attempts SET status='valid',rt=?,onset=?,response=?,key=? WHERE id=?",(p['response']-p['onset'],p['onset'],p['response'],p['key'],p['id']))
            c.execute('INSERT INTO receipts VALUES (?,?)',(p['id'],payload))
            if p.get('fault')=='abort':c.rollback();return {'code':'HOLD'}
            c.commit()
            return {'code':'UNKNOWN' if p.get('fault')=='lost-ack' else 'COMMITTED'}

class Recovery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=sync_playwright().start();cls.b=cls.p.chromium.launch(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
        print('CHROMIUM',cls.b.version,'SQLITE',sqlite3.sqlite_version,flush=True)
    @classmethod
    def tearDownClass(cls):cls.b.close();cls.p.stop()
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);self.store=Store(Path(tmp.name)/'lab.sqlite')
        self.c=self.b.new_context(offline=True);self.addCleanup(self.c.close)
        self.c.expose_binding('bridge',lambda source,op,p:self.store.call(op,p));self.p1=self.newpage()
    def newpage(self):p=self.c.new_page();p.set_content(HTML);return p
    def reload(self):self.p1.reload();self.p1.set_content(HTML)
    def state(self):return self.store.call('read',{})
    def click(self,p,b,expected):p.locator('#'+b).click();p.wait_for_function('(v)=>document.querySelector("#status").textContent===v',arg=expected,timeout=3000)
    def start(self):self.click(self.p1,'start','STARTED')
    def finish(self,p,args,fault='none'):return p.evaluate('([a,f])=>finish(a,f)',[args,fault])['code']
    def test_reload_pending_retry(self):
        self.start();old=self.state()['attempts'][0];self.reload();self.assertEqual(self.state()['attempts'],[old]);self.assertFalse(self.p1.locator('#stim').is_visible())
        self.click(self.p1,'start','HOLD');self.click(self.p1,'retry','STARTED');a,b=self.state()['attempts'];self.assertEqual((a['status'],a['rt'],b['parent']),('interrupted',None,a['id']));self.assertNotEqual(a['origin'],b['origin'])
        self.p1.keyboard.press('f');self.p1.wait_for_function('document.querySelector("#status").textContent==="COMMITTED"',timeout=3000);self.assertEqual(len(self.state()['receipts']),1)
    def test_close_reopen(self):
        self.start();s=self.state();self.p1.close();self.p1=self.newpage();self.assertEqual(self.state(),s)
    def test_complete_reload(self):
        self.start();self.p1.keyboard.press('j');self.p1.wait_for_function('document.querySelector("#status").textContent==="COMMITTED"',timeout=3000);s=self.state();a=s['attempts'][0];self.assertEqual((a['status'],a['key']),('valid','KeyJ'));self.assertAlmostEqual(a['rt'],a['response']-a['onset']);self.reload();self.click(self.p1,'retry','HOLD');self.assertEqual(self.state(),s)
    def test_lost_ack(self):
        self.start();a=self.p1.evaluate('args()');self.assertEqual(self.finish(self.p1,a,'lost-ack'),'UNKNOWN');s=self.state();self.reload();self.assertEqual(self.state(),s);self.assertEqual(self.finish(self.p1,a),'REPLAY');a['key']='KeyJ';self.assertEqual(self.finish(self.p1,a),'CONFLICT');self.assertEqual(self.state(),s)
    def test_abort(self):
        self.start();s=self.state();self.assertEqual(self.finish(self.p1,self.p1.evaluate('args()'),'abort'),'HOLD');self.reload();self.assertEqual(self.state(),s)
    def test_two_tabs(self):
        p2=self.newpage();self.p1.evaluate('()=>{window.result=begin()}');p2.evaluate('()=>{window.result=begin()}');r=[self.p1.evaluate('result'),p2.evaluate('result')];self.assertEqual(r.count('STARTED'),1);self.assertIn(next(x for x in r if x!='STARTED'),('HOLD','STALE'));self.assertEqual(len(self.state()['attempts']),1)
    def test_old_tab(self):
        self.start();a=self.p1.evaluate('args()');p2=self.newpage();self.click(p2,'retry','STARTED');s=self.state();self.assertEqual(self.finish(self.p1,a),'STALE');self.assertEqual(self.state(),s)
    def test_origin(self):
        self.start();a=self.p1.evaluate('args()');a['origin']-=1000;s=self.state();self.assertEqual(self.finish(self.p1,a),'STALE');self.assertEqual(self.state(),s)
    def test_negative_rt(self):
        self.start();a=self.p1.evaluate('args()');a['response']=a['onset']-1;s=self.state();self.assertEqual(self.finish(self.p1,a),'INVALID');self.assertEqual(self.state(),s)

if __name__=='__main__':unittest.main(verbosity=2)
