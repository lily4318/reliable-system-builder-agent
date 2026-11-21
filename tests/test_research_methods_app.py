"""M2 package 1: actual Chromium + downloaded CSV; no deployment or model."""
import csv
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
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


# Public CI logs retain fixed diagnostic codes, never raw stderr, argv or env values.
class _ChromeStartupLog:
    _markers = (
        (b"Running as root without --no-sandbox", "ROOT_SANDBOX_REFUSAL"),
        (b"No usable sandbox", "SANDBOX_UNAVAILABLE"),
        (b"DevTools listening on", "DEVTOOLS_LISTENING"),
        (b"Failed to connect to the bus", "DBUS_UNAVAILABLE"),
        (b"SingletonLock", "PROFILE_LOCK"),
        (b"Permission denied", "PERMISSION_DENIED"),
        (b"No space left on device", "NO_SPACE"),
        (b"chrome_crashpad_handler", "CRASHPAD_DIAGNOSTIC"),
    )

    def __init__(self, pipe):
        self.codes = set()
        self.bytes_seen = 0
        self.lock = threading.Lock()
        def drain():
            tail = b""
            try:
                with pipe:
                    while chunk := pipe.read1(4096):
                        data = tail + chunk
                        with self.lock:
                            self.bytes_seen += len(chunk)
                            self.codes.update(code for marker, code in self._markers
                                              if marker in data)
                        tail = data[-128:]
            except (OSError, ValueError):
                with self.lock:
                    self.codes.add("STDERR_READ_FAILED")
        self.thread = threading.Thread(target=drain, daemon=True)
        self.thread.start()

    def summary(self):
        with self.lock:
            if self.codes:
                return ",".join(sorted(self.codes))
            return "UNCLASSIFIED_STDERR" if self.bytes_seen else "NO_STDERR"


def _chrome_process_state(proc):
    # Only a coarse local kernel state code, no raw /proc lines or argv in CI.
    try:
        stat = (Path("/proc") / str(proc.pid) / "stat").read_text()
        code = stat.rsplit(")", 1)[1].split()[0]
    except (OSError, IndexError):
        return "UNAVAILABLE"
    return {"R":"RUNNING", "S":"SLEEPING", "D":"IO_WAIT",
            "T":"STOPPED", "Z":"ZOMBIE", "I":"IDLE"}.get(code,"OTHER")


def _chrome_failure_state(proc, portfile):
    profile = "PROFILE_PRESENT" if portfile.parent.is_dir() else "PROFILE_MISSING"
    return f"process={_chrome_process_state(proc)} profile={profile}"


def _wait_devtools_port(proc, portfile, diagnostics, timeout=15):
    deadline = time.monotonic() + timeout
    state = "PORT_FILE_MISSING"
    while True:
        if proc.poll() is not None:
            diagnostics.thread.join(.2)
            raise RuntimeError(f"CHROME_EARLY_EXIT rc={proc.returncode} "
                               f"state={state} {_chrome_failure_state(proc, portfile)} "
                               f"stderr_codes={diagnostics.summary()}")
        try:
            lines = portfile.read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            state = "PORT_FILE_MISSING"
        except (OSError, UnicodeError):
            state = "PORT_FILE_UNREADABLE"
        else:
            state = "PORT_FILE_INVALID"
            if (len(lines) == 2 and lines[0].isascii() and lines[0].isdigit()
                    and len(lines[0]) <= 5 and 1 <= int(lines[0]) <= 65535
                    and lines[1].startswith("/devtools/browser/")):
                if proc.poll() is None:
                    return int(lines[0])
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError(f"CHROME_READINESS_TIMEOUT state={state} "
                               f"{_chrome_failure_state(proc, portfile)} "
                               f"stderr_codes={diagnostics.summary()}")
        time.sleep(min(.1, remaining))


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
                diagnostics = None
                try:
                    profile = root / "profile"
                    proc = subprocess.Popen([exe,"--headless","--no-sandbox","--disable-dev-shm-usage",
                        "--no-first-run","--disable-background-networking","--disable-sync",
                        "--disable-component-update","--no-default-browser-check",
                        "--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1",
                        "--no-proxy-server","--remote-debugging-address=127.0.0.1",
                        "--remote-debugging-port=0","--user-data-dir="+str(profile),"about:blank"],
                        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                    diagnostics = _ChromeStartupLog(proc.stderr)
                    port = _wait_devtools_port(proc, profile/"DevToolsActivePort", diagnostics)
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
                            self.assertLessEqual(js("document.documentElement.scrollWidth"),
                                                 js("document.documentElement.clientWidth"))
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
                    if diagnostics is not None: diagnostics.thread.join(.5)
                    server.shutdown();thread.join(5)

    def test_chrome_startup_failure_is_classified_without_raw_stderr(self):
        with tempfile.TemporaryDirectory() as tmp:
            portfile = Path(tmp) / "DevToolsActivePort"
            # Real owned subprocess, deliberate early exit; not a Chromium root-cause claim.
            proc = subprocess.Popen([sys.executable, "-c",
                "import sys; sys.stderr.write('Permission denied SYNTHETIC_PRIVATE_SENTINEL'); sys.exit(17)"],
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            diagnostics = _ChromeStartupLog(proc.stderr)
            try:
                with self.assertRaisesRegex(RuntimeError, "CHROME_EARLY_EXIT rc=17") as failure:
                    _wait_devtools_port(proc, portfile, diagnostics, timeout=2)
                self.assertIn("PERMISSION_DENIED", str(failure.exception))
                self.assertNotIn("SYNTHETIC_PRIVATE_SENTINEL", str(failure.exception))
                self.assertIn("profile=PROFILE_PRESENT", str(failure.exception))
            finally:
                if proc.poll() is None: proc.kill()
                proc.wait(timeout=2)
                diagnostics.thread.join(.5)
            # Alive subprocess, missing then malformed readiness receipt: fail closed.
            proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(10)"],
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            diagnostics = _ChromeStartupLog(proc.stderr)
            try:
                with self.assertRaisesRegex(RuntimeError, "CHROME_READINESS_TIMEOUT state=PORT_FILE_MISSING") as missing:
                    _wait_devtools_port(proc, portfile, diagnostics, timeout=.15)
                self.assertIn("profile=PROFILE_PRESENT",str(missing.exception))
                self.assertIn("stderr_codes=NO_STDERR",str(missing.exception))
                self.assertRegex(str(missing.exception),r"process=(RUNNING|SLEEPING|IO_WAIT|STOPPED|ZOMBIE|IDLE|OTHER|UNAVAILABLE)")
                portfile.write_text("70000\n/devtools/browser/stale\n", encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError, "CHROME_READINESS_TIMEOUT state=PORT_FILE_INVALID"):
                    _wait_devtools_port(proc, portfile, diagnostics, timeout=.15)
                self.assertIsNone(proc.poll())
            finally:
                if proc.poll() is None: proc.terminate()
                try: proc.wait(timeout=2)
                except subprocess.TimeoutExpired: proc.kill(); proc.wait(timeout=2)
                diagnostics.thread.join(.5)
