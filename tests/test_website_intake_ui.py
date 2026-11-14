"""Local-only HTTP and schema regression tests (browser runner separate)."""
import json
import threading
import unittest
from urllib.request import urlopen, Request
from urllib.error import HTTPError

from src.website_intake_ui import create_server
from src.website_scenario_eval import load_cases
from src.website_discovery import build_spec


class LocalIntakeTest(unittest.TestCase):
    def setUp(self):
        self.server=create_server(0,{"purpose":"合成既有需求"})
        self.addCleanup(self.server.server_close)
        thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        thread.start()
        self.addCleanup(thread.join,3)
        self.addCleanup(self.server.shutdown)
        self.url=f"http://127.0.0.1:{self.server.server_port}"
        self.boot=self.get("/bootstrap")
    def get(self,path):
        with urlopen(self.url+path,timeout=3) as r:
            return json.load(r)
    def post(self,answers,token=None,origin=None,path="/draft"):
        req=Request(self.url+path,data=json.dumps(answers).encode(),headers={
            "Content-Type":"application/json","X-Local-Token":self.boot["token"] if token is None else token,
            "Origin":self.url if origin is None else origin},method="POST")
        with urlopen(req,timeout=3) as r:
            return json.load(r)
    def test_bootstrap_13_questions_6_examples_prefill_no_gold(self):
        self.assertEqual(len(self.boot["questions"]),13)
        self.assertEqual(len(self.boot["examples"]),6)
        self.assertEqual(self.boot["prefill"],{"purpose":"合成既有需求"})
        self.assertTrue(all(set(c)=={"id","title","answers"} for c in self.boot["examples"]))
        self.assertEqual(self.server.server_address[0],"127.0.0.1")
    def test_all_six_specs_match_original_generator(self):
        for c in load_cases():
            with self.subTest(c=c["id"]):
                self.assertEqual(self.post(c["answers"]),build_spec(c["answers"]))
    def test_no_write_or_deploy_authorization(self):
        result=self.post({"purpose":"合成回答","forms":"需要報名表單"})
        self.assertFalse(result["specification_approved"])
        self.assertFalse(result["write_authorized"])
        self.assertFalse(result["deployment_authorized"])
    def test_unknown_key_and_oversized_answer_rejected(self):
        for data in ({"unknown":"x"},{"purpose":"x"*2001},["not object"]):
            with self.assertRaises(HTTPError) as e:
                self.post(data)
            self.assertEqual(e.exception.code,400)
    def test_wrong_origin_or_token_rejected(self):
        for kw in ({"origin":"https://invalid.example"},{"token":"bad"}):
            with self.assertRaises(HTTPError) as e:
                self.post({},**kw)
            self.assertEqual(e.exception.code,403)
    def test_no_test_endpoint_in_normal_mode(self):
        with self.assertRaises(HTTPError) as e:
            self.post({"status":"PASS"},path="/test-result")
        self.assertEqual(e.exception.code,404)
        with self.assertRaises(HTTPError) as e:
            self.get("/browser-test.js")
        self.assertEqual(e.exception.code,404)
    def test_assets_not_arbitrary_files_and_csp(self):
        with self.assertRaises(HTTPError) as e:
            self.get("/../../AGENTS.md")
        self.assertEqual(e.exception.code,404)
        with urlopen(self.url+"/",timeout=3) as resp:
            self.assertIn("connect-src 'self'",resp.headers["Content-Security-Policy"])
            self.assertEqual(resp.headers["Cache-Control"],"no-store")
            self.assertNotIn(b"browser-test.js",resp.read())
    def test_invalid_prefill(self):
        with self.assertRaises(ValueError):
            create_server(0,["bad"])


if __name__=="__main__":
    unittest.main()
