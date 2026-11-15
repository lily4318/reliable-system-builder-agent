"""Exercise the trusted local UI in an actual Chromium-family browser.

No model, credentials, third-party pages, private answers or package downloads.
The test page drives DOM events; export payload is inspected before disk download.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import time

from src.website_intake_ui import create_server
from src.website_scenario_eval import load_cases


def run(browser=None):
    executable=browser or next((p for name in ("google-chrome","chromium","chromium-browser")
                                if (p:=shutil.which(name))),None)
    if not executable:
        raise RuntimeError("Chromium-family browser not found; install locally or use --browser")
    with tempfile.TemporaryDirectory() as tmp, create_server(
        0,{"purpose":"合成既有答案（啟動預填）"},test_mode=True
    ) as server:
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        proc=None
        try:
            proc=subprocess.Popen([
                executable,"--headless","--no-sandbox","--disable-dev-shm-usage",
                "--no-first-run","--disable-background-networking","--disable-sync",
                "--disable-component-update","--no-default-browser-check",
                "--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1",
                "--no-proxy-server","--user-data-dir="+str(Path(tmp)/"profile"),
                f"http://127.0.0.1:{server.server_port}/",
            ],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            deadline=time.monotonic()+60
            while server.test_result is None and time.monotonic()<deadline:
                if proc.poll() is not None:
                    raise RuntimeError("Browser closed before reporting")
                time.sleep(.1)
            result=server.test_result
            if result is None:
                raise RuntimeError("Browser acceptance timed out")
            expected={c["id"]:len(c["expected"]) for c in load_cases()}
            actual={c["id"]:c["review_count"] for c in result.get("cases",[]) if c.get("pass")}
            if (result.get("status")!="PASS" or actual!=expected or
                len(result.get("cases",[]))!=len(expected) or
                not result.get("import_test") or not result.get("export_payload_test")
                or result.get("model_executed") is not False):
                raise RuntimeError("Browser acceptance failed: "+json.dumps(result,ensure_ascii=False))
            return {"status":"SYNTHETIC_BROWSER_ACCEPTANCE_PASS","cases":result["cases"],
                    "case_count":len(actual),"import_test":True,"export_payload_test":True,
                    "actual_browser_dom_events":True,"real_agent_executed":False,
                    "manual_uat_completed":False,"actual_download_verified":False}
        finally:
            if proc is not None and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
            server.shutdown()
            thread.join(timeout=5)



# This separate browser check exercises the existing editable-decision example,
# not the website-intake fixture or Python confirmation state in isolation.
def run_decision_review(browser=None):
    import hashlib
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    executable=browser or next((p for name in ("google-chrome","chromium","chromium-browser")
                                if (p:=shutil.which(name))),None)
    if not executable:
        raise RuntimeError("Chromium-family browser unavailable")
    original=(Path(__file__).resolve().parents[1]/"examples/editable-decision-review.html").read_bytes()
    # The test-only script submits only booleans to an ephemeral loopback receiver.
    script=r"""
const result=(() => {
  const draft=document.getElementById('draft'), ok=document.getElementById('confirm'),
    cancel=document.getElementById('cancel'), preview=document.getElementById('preview');
  const checked=()=>document.querySelectorAll('input[name=decision]:checked').length;
  const choose=id=>document.querySelector('input[value="'+id+'"]').click();
  const edit=text=>{draft.value=text;draft.dispatchEvent(new Event('input',{bubbles:true}));};
  const confirmed=()=>preview.textContent.startsWith('已確認文字');
  const checks={};
  checks.initial=draft.disabled&&ok.disabled&&checked()===0;
  choose('A');checks.select_only=!draft.disabled&&!ok.disabled&&!confirmed();
  edit('first edit');ok.click();checks.edited_confirm=confirmed()&&preview.textContent.endsWith('first edit');
  edit('second edit');checks.edit_invalidates=!confirmed()&&!preview.textContent.includes('first edit');
  ok.click();checks.reconfirm=confirmed()&&preview.textContent.endsWith('second edit');
  edit('   ');checks.blank_disabled=ok.disabled;
  ok.click();checks.blank_invalidates=!confirmed()&&!preview.textContent.includes('second edit');
  edit('third edit');checks.nonblank_enabled=!ok.disabled;ok.click();choose('B');
  checks.reselect=!confirmed()&&!preview.textContent.includes('third edit')&&draft.value===document.querySelector('input[value="B"]').dataset.draft;
  ok.click();cancel.click();checks.cancel=draft.disabled&&ok.disabled&&draft.value===''&&checked()===0&&preview.textContent.includes('已取消');
  choose('C');checks.reopen=!draft.disabled&&!ok.disabled&&draft.value===document.querySelector('input[value="C"]').dataset.draft;
  const literal='<img src=x onerror="document.body.remove()">';
  edit(literal);ok.click();checks.literal_text=confirmed()&&preview.textContent.endsWith(literal)&&preview.querySelector('img')===null;
  return checks;
})();
fetch('/result',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(result)});
"""
    if original.count(b"</body>")!=1:
        raise RuntimeError("expected a single document body")
    # No application submission or external fetch is needed. The CSP permits
    # only inline example/test scripts and the local test-result request.
    page=original.replace(b"</body>",("<script>"+script+"</script></body>").encode("utf-8"))
    expected={"initial","select_only","edited_confirm","edit_invalidates","reconfirm",
              "blank_disabled","blank_invalidates","nonblank_enabled","reselect","cancel","reopen","literal_text"}
    result=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):
            pass
        def do_GET(self):
            if self.path!="/":
                self.send_error(404);return
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Security-Policy","default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; form-action 'none'; base-uri 'none'")
            self.send_header("Content-Length",str(len(page)))
            self.end_headers();self.wfile.write(page)
        def do_POST(self):
            try:
                if self.path!="/result" or self.headers.get("Origin")!=f"http://127.0.0.1:{self.server.server_port}" or result:
                    raise ValueError("unexpected test report")
                size=int(self.headers.get("Content-Length","0"))
                if not 0<size<=4096:
                    raise ValueError("invalid test report size")
                value=json.loads(self.rfile.read(size))
                if not isinstance(value,dict) or set(value)!=expected or any(type(v) is not bool for v in value.values()):
                    raise ValueError("invalid test report")
            except (ValueError,TypeError):
                self.send_error(400);return
            result.append(value)
            self.send_response(204);self.end_headers()
    with tempfile.TemporaryDirectory() as tmp, ThreadingHTTPServer(("127.0.0.1",0),Handler) as server:
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        proc=None
        try:
            proc=subprocess.Popen([executable,"--headless","--no-sandbox","--disable-dev-shm-usage",
                "--no-first-run","--disable-background-networking","--disable-sync","--disable-component-update",
                "--no-default-browser-check","--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1",
                "--no-proxy-server","--user-data-dir="+str(Path(tmp)/"profile"),
                f"http://127.0.0.1:{server.server_port}/"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            deadline=time.monotonic()+30
            while not result and time.monotonic()<deadline:
                if proc.poll() is not None:
                    raise RuntimeError("Decision browser closed before reporting")
                time.sleep(.1)
            if not result or not all(result[0].values()):
                raise RuntimeError("Editable decision browser failure: "+json.dumps(result,ensure_ascii=False))
            return {"status":"EDITABLE_DECISION_BROWSER_PASS","checks":result[0],
                    "source_sha256":hashlib.sha256(original).hexdigest(),
                    "actual_browser_dom_events":True,"manual_uat_completed":False,
                    "application_transmitted":False,"external_approval_granted":False}
        finally:
            if proc is not None and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill();proc.wait()
            server.shutdown();thread.join(timeout=5)

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--browser")
    args=p.parse_args()
    print(json.dumps(run(args.browser),ensure_ascii=False))
    print('EDITABLE-DECISION-BROWSER: '+json.dumps(run_decision_review(args.browser),ensure_ascii=False))
    from src.p21_equipment_browser_test import run as run_equipment
    print('P21-EQUIPMENT-BROWSER: '+json.dumps(run_equipment(args.browser),ensure_ascii=False))
