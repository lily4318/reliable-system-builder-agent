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


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--browser")
    args=p.parse_args()
    print(json.dumps(run(args.browser),ensure_ascii=False))
