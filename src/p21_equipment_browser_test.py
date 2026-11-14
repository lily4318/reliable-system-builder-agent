"""Drive the synthetic equipment website in real Chromium via local CDP.

No downloads, external pages, real identities, or model invocation.
Node >=22 provides the native WebSocket client; all forms use DOM submit.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import time

from src.p21_equipment_site import Site, Store


DRIVER = r"""
const assert = (ok, label) => {if (!ok) throw Error(label)};
const input = JSON.parse(await new Promise(resolve => {
    let s=''; process.stdin.setEncoding('utf8');
    process.stdin.on('data', x=>s+=x); process.stdin.on('end',()=>resolve(s));
}));
const targets = await (await fetch('http://127.0.0.1:'+input.port+'/json/list')).json();
const target = targets.find(x=>x.type==='page');
assert(target, 'no Chromium page');
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((ok,fail)=>{ws.onopen=ok; ws.onerror=fail;});
let id=0; const pending=new Map();
ws.onmessage = ev=> {
    const msg=JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
        const [ok,fail]=pending.get(msg.id); pending.delete(msg.id);
        msg.error ? fail(Error(msg.error.message)) : ok(msg.result);
    }
};
const cmd=(method,params={})=>new Promise((ok,fail)=>{
    const key=++id; pending.set(key,[ok,fail]); ws.send(JSON.stringify({id:key,method,params}));
});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function evaluate(expression) {
    const out=await cmd('Runtime.evaluate',{expression,returnByValue:true});
    if(out.exceptionDetails) throw Error('DOM evaluation failed');
    return out.result.value;
}
async function wait(expression,label) {
    for (let n=0;n<100;n++) {
        try {if(await evaluate(expression)) return;} catch(e) {}
        await sleep(50);
    }
    const actual=await evaluate('document.body ? document.body.innerText.slice(0,180) : ""').catch(()=>'unavailable');
    throw Error(label+'; visible page: '+actual);
}
async function navigate(path) {
    await cmd('Page.navigate',{url:input.origin+path});
    await wait('location.href==='+JSON.stringify(input.origin+path)+' && document.readyState==="complete"', 'navigation '+path);
}
async function click(selector,expected,label) {
    const expression='(()=>{const e=document.querySelector('+JSON.stringify(selector)+'); if(!e) return false; e.click(); return true})()';
    assert(await evaluate(expression), 'missing button '+selector);
    await wait(expected,label);
}
const has = text => 'document.body.innerText.includes('+JSON.stringify(text)+')';
const field = async (selector,value) => {
    const expression='(()=>{const e=document.querySelector('+JSON.stringify(selector)+'); if(!e)return false;e.value='+JSON.stringify(value)+';e.dispatchEvent(new Event("input",{bubbles:true}));e.dispatchEvent(new Event("change",{bubbles:true}));return true})()';
    assert(await evaluate(expression),'missing field '+selector);
};
async function login(actor,valid=true) {
    await navigate('/login');
    await field('input[name=user]',actor);
    await field('input[name=password]',valid?input.credentials[actor]:'synthetic-wrong');
    await click('form[action="/login"] button',has(valid?'Signed in':'Invalid credentials'),'login '+actor);
    if(valid) {
        await click('a[href="/"]',has('Signed in: '+actor),'dashboard '+actor);
        assert(await evaluate('document.cookie.indexOf("sid=")===-1'),'session cookie must be HttpOnly');
    }
}
async function logout() {
    await click('form[action="/logout"] button',has('Signed out'),'sign out');
    await navigate('/admin');
    assert(await evaluate(has('Sign in required')),'logged out admin access');
}
async function reserve(qty,result) {
    await field('input[name=qty]',String(qty));
    await click('form[action="/reserve"] button',has(result),'reserve '+result);
    await click('a[href="/"]',has('Signed in:'),'reserve dashboard');
}
const row = token => 'table:first-of-type tbody tr';
const seen = token => 'Array.from(document.querySelectorAll('+JSON.stringify(row(token))+')).some(r=>r.cells[1].textContent==='+JSON.stringify(token)+')';
const owns = (token,state) => 'Array.from(document.querySelectorAll("table:first-of-type tbody tr")).some(r=>r.cells[1].textContent==='+JSON.stringify(token)+'&&r.cells[4].textContent==='+JSON.stringify(state)+')';
const available = n => 'document.querySelector("#available")?.innerText==='+JSON.stringify('Available: '+n);
try {
    await cmd('Page.enable');
    await navigate('/admin');
    assert(await evaluate(has('Sign in required')),'anonymous admin');
    await login('member',false);
    await login('member');
    assert(await evaluate(available(10)),'initial inventory');
    await field('input[name=qty]','11');
    assert(await evaluate('!document.querySelector("input[name=qty]").checkValidity()'),'quantity browser constraint');
    await click('form[action="/reserve"] button','location.pathname==="/"','invalid quantity remains on form');
    assert(await evaluate(available(10)),'invalid quantity mutated stock');
    const first=await evaluate('document.querySelector("input[name=token]").value');
    await reserve(4,'RESERVED');
    assert(await evaluate(owns(first,'RESERVED')),'member reservation row');
    assert(await evaluate(available(6)),'reservation stock');
    await navigate('/admin');
    assert(await evaluate(has('Admin only')),'member admin guard');
    await navigate('/');
    await logout();
    await login('member2');
    assert(!await evaluate(seen(first)),'foreign request leaked');
    const second=await evaluate('document.querySelector("input[name=token]").value');
    await reserve(3,'RESERVED');
    await reserve(8,'INSUFFICIENT');
    assert(await evaluate(available(3)),'insufficient request changed stock');
    await logout();
    await login('member');
    assert(!await evaluate(seen(second)),'foreign request leaked to member');
    await click('form[action="/cancel"] button',has('CANCELLED'),'cancel');
    await click('a[href="/"]',has('Signed in: member'),'cancel dashboard');
    assert(await evaluate(owns(first,'CANCELLED')),'cancel row');
    assert(await evaluate(available(7)),'cancel stock');
    assert(await evaluate('!document.querySelector("form[action=\\"/cancel\\"]")'),'cancel action remains');
    await logout();
    await login('admin');
    await navigate('/admin');
    assert(await evaluate(seen(first)+' && '+seen(second)),'admin all requests');
    assert(await evaluate('!document.querySelector("form[action=\\"/reserve\\"]")'),'admin reserve available');
    await click('form[action="/return"] button',has('RETURNED'),'return');
    await click('a[href="/"]',has('Signed in: admin'),'return dashboard');
    assert(await evaluate(owns(second,'RETURNED')),'return row');
    assert(await evaluate(available(10)),'final stock');
    assert(await evaluate('!document.querySelector("form[action=\\"/return\\"]")'),'return action remains');
    await logout();
    await login('member2');
    assert(await evaluate(owns(second,'RETURNED')),'member2 return visibility');
    assert(!await evaluate(seen(first)),'foreign request leaked after return');
    await logout();
    console.log(JSON.stringify({status:'PASS',actual_browser_dom_events:true,roles:3,stock:10,reserved:0,manual_uat:false}));
} finally { ws.close(); }
"""


def run(browser=None):
    executable=browser or next((p for name in ('google-chrome','chromium','chromium-browser')
                                if (p:=shutil.which(name))),None)
    node=shutil.which('node')
    if not executable or not node:
        raise RuntimeError('Chromium and Node >=22 required')
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        store=Store(root/'equipment.sqlite')
        store.initialize()
        with Site(store) as server:
            thread=threading.Thread(target=server.serve_forever,daemon=True)
            thread.start()
            proc=None
            try:
                proc=subprocess.Popen([executable,'--headless','--no-sandbox','--disable-dev-shm-usage',
                    '--no-first-run','--no-default-browser-check','--disable-background-networking',
                    '--disable-sync','--disable-component-update','--no-proxy-server',
                    '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1',
                    '--remote-debugging-address=127.0.0.1','--remote-debugging-port=0',
                    '--user-data-dir='+str(root/'profile'),'about:blank'],
                    stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                marker=root/'profile'/'DevToolsActivePort'
                deadline=time.monotonic()+15
                while not marker.exists() and time.monotonic()<deadline:
                    if proc.poll() is not None:
                        raise RuntimeError('Chromium exited before CDP startup')
                    time.sleep(.05)
                if not marker.exists(): raise RuntimeError('Chromium CDP unavailable')
                port=int(marker.read_text().splitlines()[0])
                result=subprocess.run([node,'--input-type=module','-e',DRIVER],
                    input=json.dumps({'port':port,'origin':server.origin,'credentials':server.credentials}),
                    text=True,capture_output=True,timeout=90)
                if result.returncode:
                    raise RuntimeError('Equipment browser failure: '+result.stderr[-2000:])
                data=json.loads(result.stdout)
                if data.get('status')!='PASS' or store.view(None)[:2]!=(10,0):
                    raise RuntimeError('Equipment browser final inventory mismatch')
                rows=store.view(None,lifecycle=True)[2]
                if sorted(r[4] for r in rows)!=['CANCELLED','INSUFFICIENT','RETURNED']:
                    raise RuntimeError('Equipment browser lifecycle mismatch')
                return data
            finally:
                if proc is not None and proc.poll() is None:
                    proc.terminate()
                    try: proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait()
                server.shutdown()
                thread.join(timeout=5)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser')
    args=parser.parse_args()
    print(json.dumps(run(args.browser)))
