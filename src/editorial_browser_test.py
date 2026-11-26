"""Real Chromium DOM acceptance at exact CSS widths via local CDP only."""
import argparse
import base64
import json
import os
from pathlib import Path
import shutil
import secrets
import socket
import struct
import subprocess
import tempfile
import threading
import time
from urllib.request import urlopen
from urllib.parse import urlsplit

from src.editorial_store import Store
from src.editorial_site import create_server

# Only public synthetic fixture credentials for ephemeral databases.
PASSWORDS={'author-a':'SyntheticAuthorA-2026','author-b':'SyntheticAuthorB-2026','editor':'SyntheticEditor-2026'}
EXPECTED={'exact_viewport','initial_empty','keyboard_focus','wrong_login','author_create',
          'page_one','page_two','lost_ack_pending','read_only_reconcile','workspace_no_overflow','review_reason_history',
          'real_tab_navigation','reconcile_owner_guard','reconcile_after_relogin',
          'author_keyboard_field','other_author_hidden','unsubmitted_hidden','submitted_visible',
          'return_reason','literal_private','approved_not_public','literal_public','search_category',
          'filter_empty','old_public_retained','atomic_public_switch','withdraw_hidden','republished',
          'responsive_no_overflow'}


class CDP:
    """Minimal client for trusted local Chrome text frames; no external URL."""
    def __init__(self,url):
        u=urlsplit(url)
        if u.scheme!='ws' or u.hostname!='127.0.0.1':
            raise RuntimeError('unsafe debug endpoint')
        self.sock=socket.create_connection(('127.0.0.1',u.port),timeout=10)
        self.reader=self.sock.makefile('rb')
        key=base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f'GET {u.path} HTTP/1.1\r\nHost: 127.0.0.1:{u.port}\r\n'
                           'Upgrade: websocket\r\nConnection: Upgrade\r\n'
                           f'Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
        if b' 101 ' not in self.reader.readline():
            raise RuntimeError('CDP handshake failure')
        while self.reader.readline() not in (b'\r\n',b''):
            pass
        self.id=0

    def command(self,method,params):
        self.id+=1
        raw=json.dumps({'id':self.id,'method':method,'params':params}).encode()
        mask=os.urandom(4)
        n=len(raw)
        if n<126:head=bytes((0x81,0x80|n))
        else:head=bytes((0x81,0xfe))+struct.pack('!H',n)
        self.sock.sendall(head+mask+bytes(b^mask[i%4] for i,b in enumerate(raw)))
        while True:
            head=self.reader.read(2)
            if not head or len(head)!=2:raise RuntimeError('CDP closed')
            if head[0]!=0x81:raise RuntimeError('unexpected CDP frame')
            n=head[1]&127
            if n==126:n=struct.unpack('!H',self.reader.read(2))[0]
            elif n==127:n=struct.unpack('!Q',self.reader.read(8))[0]
            if n>1_000_000 or head[1]&128:raise RuntimeError('invalid CDP response')
            result=json.loads(self.reader.read(n))
            if result.get('id')==self.id:
                if 'error' in result:raise RuntimeError('CDP command rejected')
                return result

    def close(self):
        self.reader.close();self.sock.close()


def run_one(executable,width):
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);store=Store(root/'site.sqlite');store.initialize(PASSWORDS)
        author=store.login('author-b',PASSWORDS['author-b'])
        editor=store.login('editor',PASSWORDS['editor'])
        for i in range(21):
            result=store.action(author,{'op':'create','token':secrets.token_hex(16),'title':f'分頁資料 {i:02d}','body':'合成分頁測試','category':'科技'})
            for op,session in (('submit',author),('approve',editor),('publish',editor)):
                result=store.action(session,{'op':op,'token':secrets.token_hex(16),'article_id':result['article_id'],
                                            'revision_id':result['revision_id'],'expected':result['version']})
                if result['ok'] is not True:raise RuntimeError('pagination seed failed')
        store.logout(author);store.logout(editor)
        with create_server(store.path,0,test_mode=True) as server:
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            proc=None;cdp=None
            try:
                profile=root/'profile'
                proc=subprocess.Popen([executable,'--headless','--no-sandbox','--disable-dev-shm-usage',
                    '--no-first-run','--disable-background-networking','--disable-sync','--disable-component-update',
                    '--no-default-browser-check','--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1',
                    '--no-proxy-server','--remote-debugging-address=127.0.0.1','--remote-debugging-port=0',
                    '--user-data-dir='+str(profile),'about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                deadline=time.monotonic()+15
                portfile=profile/'DevToolsActivePort'
                while not portfile.exists() and time.monotonic()<deadline:
                    if proc.poll() is not None:raise RuntimeError('Chrome closed')
                    time.sleep(.1)
                port=int(portfile.read_text().splitlines()[0])
                with urlopen(f'http://127.0.0.1:{port}/json/list',timeout=5) as r:
                    pages=json.load(r)
                cdp=CDP(next(p['webSocketDebuggerUrl'] for p in pages if p['type']=='page'))
                cdp.command('Emulation.setDeviceMetricsOverride',{'width':width,'height':900,'deviceScaleFactor':1,'mobile':width==375})
                cdp.command('Page.navigate',{'url':f'http://127.0.0.1:{server.server_port}/'})
                # The page deliberately pauses on the focused username field.
                # A native CDP key event, not a synthetic focus() assertion,
                # must move focus to the password field.
                deadline=time.monotonic()+15
                while time.monotonic()<deadline:
                    result=cdp.command('Runtime.evaluate',{'expression':'document.body?.dataset.keyboardReady==="1"','returnByValue':True})
                    if result['result']['result'].get('value') is True:break
                    if server.test_result is not None:break
                    time.sleep(.05)
                else:
                    raise RuntimeError('keyboard readiness timeout')
                if server.test_result is None:
                    for event in ('keyDown','keyUp'):
                        cdp.command('Input.dispatchKeyEvent',{'type':event,'key':'Tab','code':'Tab',
                                    'windowsVirtualKeyCode':9,'nativeVirtualKeyCode':9})
                deadline=time.monotonic()+60
                while server.test_result is None and time.monotonic()<deadline:
                    if proc.poll() is not None:raise RuntimeError('Chrome closed')
                    time.sleep(.1)
                result=server.test_result
                if (not result or result.get('status')!='PASS' or result.get('width')!=width
                    or set(result.get('checks',{}))!=EXPECTED or not all(v is True for v in result['checks'].values())):
                    raise RuntimeError('EDITORIAL browser failed: '+json.dumps(result,ensure_ascii=False))
                return result
            finally:
                if cdp:cdp.close()
                if proc is not None and proc.poll() is None:
                    proc.terminate()
                    try:proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:proc.kill();proc.wait()
                server.shutdown();thread.join(5)


def run(browser=None):
    exe=browser or next((p for name in ('google-chrome','chromium','chromium-browser') if (p:=shutil.which(name))),None)
    if not exe:raise RuntimeError('Chromium unavailable')
    return {'status':'EDITORIAL_BROWSER_PASS','views':[run_one(exe,w) for w in (375,1280)],
            'actual_browser_dom_events':True,'manual_uat_completed':False,'external_deployment':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--browser');args=p.parse_args()
    print('EDITORIAL-BROWSER: '+json.dumps(run(args.browser),ensure_ascii=False))
