"""Hand-authored beginner scenarios; no real registration or authentication."""
import json
import subprocess
import sys
import unittest
from src.account_onboarding import route, PROVIDERS

def state(**kw):
    return dict(account="ready",connection="connected",readback="verified",
                capability="supported",cost="free_confirmed",**{}) | kw
def profile(p="github",**kw):
    return {"required":[p],"states":{p:state(**kw)}}

class AccountOnboardingTest(unittest.TestCase):
    def test_no_stack_no_setup(self):
        self.assertEqual(route({"required":[],"states":{}})["status"],"SELECT_REQUIRED_SERVICES_FIRST")
    def test_unknown_account_not_assumed_missing(self):
        self.assertEqual(route(profile(account="unknown"))["status"],"CHECK_ACCOUNT")
    def test_signup_all_four(self):
        for p in PROVIDERS:
            with self.subTest(p=p):
                r=route(profile(p,account="missing",connection="missing",readback="unknown"))
                self.assertEqual(r["status"],"GUIDE_SIGNUP")
                self.assertGreaterEqual(len(r["steps"]),5)
                self.assertTrue(all(set(s)=={"action","verification","if_blocked"} for s in r["steps"]))
    def test_connect_all_four(self):
        for p in PROVIDERS:
            r=route(profile(p,connection="missing",readback="unknown"))
            self.assertEqual(r["status"],"GUIDE_CONNECT")
            self.assertEqual(len(r["steps"]),6)
            self.assertIn("Settings",r["steps"][0]["action"])
            self.assertIn("唯讀",r["steps"][-1]["action"])
    def test_existing_account_skips_registration(self):
        self.assertEqual(route(profile(connection="unknown"))["status"],"DISCOVER_CONNECTION")
        self.assertEqual(route(profile(readback="unknown"))["status"],"VERIFY_CONNECTION_READONLY")
    def test_wrong_target_has_global_priority(self):
        r=route({"required":["github","supabase"],"states":{
            "github":state(account="missing",connection="missing"),
            "supabase":state(readback="wrong_target")}})
        self.assertEqual(r["status"],"WRONG_ACCOUNT_OR_TARGET_HOLD")
        self.assertEqual(r["provider"],"supabase")
    def test_wrong_account_and_conflict(self):
        self.assertEqual(route(profile(connection="wrong_account"))["status"],"WRONG_ACCOUNT_OR_TARGET_HOLD")
        self.assertEqual(route(profile(account="missing"))["status"],"STATE_CONFLICT_HOLD")
    def test_security_and_denial(self):
        self.assertEqual(route(profile(account="security_pending"))["status"],"GUIDE_ACCOUNT_SECURITY")
        self.assertEqual(route(profile(connection="denied"))["status"],"PERMISSION_DENIED_HOLD")
    def test_unavailable_and_readback_failure(self):
        self.assertEqual(route(profile(connection="unavailable"))["status"],"ALTERNATIVE_PATH_HOLD")
        self.assertEqual(route(profile(readback="failed"))["status"],"READBACK_FAILED_HOLD")
    def test_gas_connection_not_deployment_capability(self):
        r=route(profile("google",capability="unsupported"))
        self.assertEqual(r["status"],"CAPABILITY_GAP_HOLD")
    def test_capability_unknown(self):
        self.assertEqual(route(profile(capability="unknown"))["status"],"VERIFY_REQUIRED_CAPABILITY")
    def test_cost_unknown_and_paid(self):
        self.assertEqual(route(profile(cost="unknown"))["status"],"VERIFY_PLAN_AND_COST")
        self.assertEqual(route(profile(cost="not_free_or_uncertain"))["status"],"COST_HOLD")
    def test_existing_provider_skipped_in_multi_stack(self):
        r=route({"required":["github","cloudflare"],"states":{"github":state(),"cloudflare":state(connection="missing")}})
        self.assertEqual(r["provider"],"cloudflare")
        self.assertEqual(r["status"],"GUIDE_CONNECT")
    def test_all_ready_is_evidence_review_not_authorization(self):
        r=route(profile())
        self.assertEqual(r["status"],"READY_FOR_C1_EVIDENCE_REVIEW")
        for k in ("account_verified_by_router","connection_verified_by_router","c1_pass","external_write_permitted","deployment_permitted","payment_permitted"):
            self.assertIs(r[k],False)
    def test_malformed_no_secrets_or_forged_approval(self):
        for x in [None,[],{},{"required":[[]],"states":{}},
                  {"required":["github","github"],"states":{"github":state()}},
                  {"required":["github"],"states":{"github":state(),"google":state()}},
                  profile(account=True),profile(token="x"),profile(deployment_permitted=True),
                  profile(cost=[])]:
            r=route(x)
            self.assertEqual(r["status"],"INVALID_PROFILE")
            self.assertFalse(r["deployment_permitted"])
    def test_cli_bounded_and_duplicate(self):
        cmd=[sys.executable,"-m","src.account_onboarding"]
        for payload,rc in [(json.dumps(profile()).encode(),0),(b'{"required":[],"required":[]}',2),(b'x'*16385,2),(b'\xff',2)]:
            p=subprocess.run(cmd,input=payload,capture_output=True,timeout=10)
            self.assertEqual(p.returncode,rc)
            self.assertFalse(json.loads(p.stdout)["c1_pass"])
