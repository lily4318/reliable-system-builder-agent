import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from src.ci_evidence_bundle import FILES, REPORT, bind, context, verify

class EvidenceBundleTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        self.ctx=context("example/training","a"*40,123,2)
        self.report={"gate_passed":True,"human_approval_completed":False,"formal_release_created":False}
        for f in FILES:
            (self.root/f).write_text(json.dumps({"name":f}),encoding="utf-8")
        self.bound=bind(self.report,self.root,self.ctx,"a"*40)
        self.digest=self.write_report(self.bound)
    def write_report(self,report):
        raw=json.dumps(report,sort_keys=True).encode()
        (self.root/REPORT).write_bytes(raw)
        return hashlib.sha256(raw).hexdigest()
    def check(self,ctx=None,digest=None,conclusion="success"):
        return verify(self.root,ctx or self.ctx,digest or self.digest,conclusion)
    def test_matching_files_and_identity(self):
        result=self.check()
        self.assertTrue(result["integrity_matches_supplied_evidence"])
        self.assertFalse(result["remote_ci_independently_verified"])
        self.assertFalse(result["formal_deployment_permitted"])
    def test_wrong_sha_run_attempt_and_repo(self):
        for change in ({"checkout_sha":"b"*40},{"run_id":124},{"run_attempt":1},{"repository":"other/training"}):
            with self.subTest(change=change),self.assertRaises(ValueError):
                self.check({**self.ctx,**change})
        with self.assertRaises(ValueError):
            bind(self.report,self.root,self.ctx,"b"*40)
    def test_failed_missing_or_cancelled_run_refused(self):
        for status in ("failure","cancelled","in_progress","unknown"):
            with self.subTest(status=status),self.assertRaises(ValueError):
                self.check(conclusion=status)
        with self.assertRaises(ValueError):
            bind({**self.report,"gate_passed":False},self.root,self.ctx,"a"*40)
    def test_tampered_report_or_payload_rejected(self):
        self.write_report({**self.bound,"injected":True})
        with self.assertRaises(ValueError): self.check()
        self.write_report(self.bound)
        (self.root/FILES[0]).write_text('{"changed":true}')
        with self.assertRaises(ValueError): self.check()
        # Rebuilding self-described hashes cannot match independently read old digest.
        self.write_report(bind(self.report,self.root,self.ctx,"a"*40))
        with self.assertRaises(ValueError): self.check()
    def test_missing_extra_and_symlink_rejected(self):
        p=self.root/FILES[0]
        raw=p.read_bytes()
        p.unlink()
        with self.assertRaises(OSError): self.check()
        p.symlink_to(self.root/FILES[1])
        with self.assertRaises(OSError): self.check()
        p.unlink();p.write_bytes(raw)
        (self.root/"unexpected.txt").write_text("extra")
        with self.assertRaises(ValueError): self.check()
    def test_duplicate_key_json_blocked_at_producer(self):
        (self.root/FILES[1]).write_text('{"a":1,"a":2}')
        with self.assertRaises(ValueError):
            bind(self.report,self.root,self.ctx,"a"*40)
