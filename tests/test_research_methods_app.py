"""M2 package 1: actual Chromium + downloaded CSV; no deployment or model."""
import csv
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen
from src.editorial_browser_test import CDP

ROOT = Path(__file__).resolve().parents[1] / "examples/research-methods"
ASSETS = {"/index.html": ("index.html", "text/html; charset=utf-8"),
          "/style.css": ("style.css", "text/css; charset=utf-8"),
          "/app.js": ("app.js", "text/javascript; charset=utf-8")}


class ResearchMethodsTest(unittest.TestCase):
    def test_academic_app_real_browser_and_download(self):
        exe = next((p for name in ("google-chrome","chromium","chromium-browser")
                    if (p := shutil.which(name))), None)
        if not exe:
            if os.environ.get("GITHUB_ACTIONS") == "true":
                self.fail("Chromium unavailable in required CI")
            self.skipTest("Chromium unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = {p: ((ROOT / f).read_bytes(), mime) for p,(f,mime) in ASSETS.items()}
            requests = []
            class Handler(BaseHTTPRequestHandler):
                def log_message(self,*_): pass
                def do_GET(self):
                    requests.append(self.path)
                    if self.path not in assets:
                        self.send_error(404); return
                    data,mime = assets[self.path]
                    self.send_response(200)
                    self.send_header("Content-Type",mime)
                    self.send_header("Content-Length",str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
            with ThreadingHTTPServer(("127.0.0.1",0),Handler) as server:
                thread = threading.Thread(target=server.serve_forever,daemon=True)
                thread.start()
                proc = None
                cdp = None
                try:
                    profile = root / "profile"
                    proc = subprocess.Popen([exe,"--headless","--no-sandbox","--disable-dev-shm-usage",
                        "--no-first-run","--disable-background-networking","--disable-sync",
                        "--disable-component-update","--no-default-browser-check",
                        "--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1",
                        "--no-proxy-server","--remote-debugging-address=127.0.0.1",
                        "--remote-debugging-port=0","--user-data-dir="+str(profile),"about:blank"],
                        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                    deadline = time.monotonic()+15
                    portfile = profile/"DevToolsActivePort"
                    while not portfile.exists() and time.monotonic()<deadline:
                        if proc.poll() is not None: self.fail("Chrome closed")
                        time.sleep(.1)
                    port = int(portfile.read_text().splitlines()[0])
                    with urlopen(f"http://127.0.0.1:{port}/json/list",timeout=5) as response:
                        pages = json.load(response)
                    cdp = CDP(next(p["webSocketDebuggerUrl"] for p in pages if p["type"]=="page"))
                    def js(expression):
                        r=cdp.command("Runtime.evaluate",{"expression":expression,"returnByValue":True})["result"]
                        self.assertNotIn("exceptionDetails",r)
                        return r["result"].get("value")
                    def wait(expression):
                        until=time.monotonic()+10
                        while time.monotonic()<until:
                            if js(expression): return
                            time.sleep(.05)
                        self.fail("wait timeout: "+expression)
                    def edit(field,value):
                        js(f"""(() => {{const el=document.getElementById({json.dumps(field)});el.value={json.dumps(value)};el.dispatchEvent(new Event('input',{{bubbles:true}}));}})()""")
                    def click(id):
                        js("document.getElementById("+json.dumps(id)+").click()")
                    def snapshot():
                        return js("Array.from(document.querySelectorAll('#rows tr'), tr=>Array.from(tr.cells, td=>td.textContent))")
                    def check_rows(rows,n):
                        self.assertEqual([r[0] for r in rows],[str(i) for i in range(1,n+1)])
                        for g,baseline in (("A",50),("B",58)):
                            vals=[int(r[2]) for r in rows if r[1]==g]
                            self.assertEqual(len(vals),n//2)
                            self.assertTrue(all(baseline-15<=v<=baseline+15 for v in vals))
                            self.assertAlmostEqual(float(js("document.querySelector('#mean-"+g.lower()+"').textContent")),sum(vals)/len(vals),delta=.051)
                    for width in (375,1280):
                        with self.subTest(width=width):
                            folder=root/str(width);folder.mkdir()
                            cdp.command("Page.setDownloadBehavior",{"behavior":"allow","downloadPath":str(folder)})
                            cdp.command("Emulation.setDeviceMetricsOverride",{"width":width,"height":900,"deviceScaleFactor":1,"mobile":width==375})
                            cdp.command("Page.navigate",{"url":f"http://127.0.0.1:{server.server_port}/index.html"})
                            wait("document.querySelectorAll('#rows tr').length===40")
                            self.assertEqual(js("innerWidth"),width)
                            self.assertEqual(js("document.documentElement.scrollWidth"),width)
                            self.assertEqual(js("getComputedStyle(document.querySelector('.panel')).borderRadius"),"12px")
                            base=snapshot();check_rows(base,40)
                            # Native Tab key and form submit, not a pure JS generator test.
                            js("document.getElementById('sample').focus()")
                            for event in ("keyDown","keyUp"):
                                cdp.command("Input.dispatchKeyEvent",{"type":event,"key":"Tab","code":"Tab","windowsVirtualKeyCode":9,"nativeVirtualKeyCode":9})
                            self.assertEqual(js("document.activeElement.id"),"seed")
                            click("generate");self.assertEqual(snapshot(),base)
                            for field,invalid in (("sample","21"),("sample",""),("sample","102"),("seed","4294967296"),("seed","=1+1"),("seed","1e2")):
                                edit("sample","40");edit("seed","1");click("generate")
                                edit(field,invalid)
                                self.assertTrue(js("document.getElementById('download').disabled"))
                                click("generate")
                                self.assertTrue(js("document.getElementById('results').hidden"))
                                self.assertEqual(snapshot(),[])
                                self.assertEqual(js("document.getElementById("+json.dumps(field)+").getAttribute('aria-invalid')"),"true")
                            edit("sample","20");edit("seed","0");click("generate");check_rows(snapshot(),20)
                            edit("sample","100");edit("seed","4294967295");click("generate")
                            rows=snapshot();check_rows(rows,100)
                            click("download")
                            path=folder/"research-methods-100-4294967295.csv"
                            until=time.monotonic()+10
                            while not path.is_file() and time.monotonic()<until: time.sleep(.05)
                            raw=path.read_bytes()
                            parsed=list(csv.reader(io.StringIO(raw.decode("utf-8"))))
                            self.assertEqual(parsed[0],["sample_id","group","simulated_score","sample_size","seed","simulation_version"])
                            self.assertEqual(parsed[1:],[r+["100","4294967295","sim-v1"] for r in rows])
                            edit("sample","40");edit("seed","2");click("generate")
                            self.assertNotEqual(snapshot(),base)
                            edit("seed","1");click("generate");self.assertEqual(snapshot(),base)
                            # No persistent browser data and no resource outside the local three assets.
                            self.assertTrue(js("localStorage.length===0&&sessionStorage.length===0&&document.cookie===''"))
                            self.assertTrue(js("performance.getEntriesByType('resource').every(e=>e.name.startsWith(location.origin+'/'))"))
                            self.assertEqual(js("document.querySelector('meta[http-equiv=Content-Security-Policy]').content.includes(\"connect-src 'none'\")"),True)
                            print("RESEARCH-METHODS-BROWSER_PASS",width,"actual_csv_rows",len(parsed)-1,"csv_bytes",len(raw),flush=True)
                    self.assertTrue(set(requests)<=set(ASSETS)|{"/favicon.ico"})
                finally:
                    if cdp: cdp.close()
                    if proc is not None and proc.poll() is None:
                        proc.terminate()
                        try: proc.wait(timeout=5)
                        except subprocess.TimeoutExpired: proc.kill();proc.wait()
                    server.shutdown();thread.join(5)
