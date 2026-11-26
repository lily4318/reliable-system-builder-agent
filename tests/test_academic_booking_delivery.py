"""Same-case comparison and actual local WSGI/SQLite delivery exercise."""
import io
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from wsgiref.util import setup_testing_defaults
from wsgiref.validate import validator

from examples.academic_booking import AcademicBooking
from src import delivery_next_step, delivery_routes, team_workbench, website_discovery, workbench_tasks

FIXTURE = Path(__file__).resolve().parents[1] / "evaluations/interaction/academic-booking-delivery.json"


class AcademicDeliveryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.answers = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.workspace = team_workbench.initialize(self.root / "workbench", "Synthetic academic")
        workbench_tasks.setup(self.workspace)

    def view(self, intent, **kwargs):
        return delivery_routes.route(intent, workbench_tasks.review(self.workspace), **kwargs)

    def complete(self, task, session, evidence):
        workbench_tasks.start(self.workspace, task, session, expected_revision=1)
        workbench_tasks.finish(self.workspace, task, session, {"accept": "PASS"},
                               evidence, expected_revision=1)

    def test_same_case_baseline_intake_and_route(self):
        baseline = website_discovery.draft_spec(self.answers)
        snapshot = workbench_tasks.review(self.workspace)
        self.assertEqual(baseline["question_count"], 13)
        self.assertEqual(baseline["unanswered_questions"], ["admin"])
        self.assertTrue(baseline["user_review_required"])
        self.assertEqual(delivery_next_step.choose(snapshot)["status"],
                         "NEEDS_EXISTING_PROJECT_SCOPE")
        website = self.view("做網站", answers=self.answers)
        self.assertEqual([q["id"] for q in website["missing_intake_questions"]], ["admin"])
        self.assertEqual(website["specification_draft"], baseline)
        self.assertFalse(website["authorization_granted"])
        self.assertEqual(self.view("接預約")["status"], "NEEDS_EXISTING_PROJECT_SCOPE")
        self.assertEqual(self.view("修復")["skills"][1], "debug-and-repair")

    def test_website_booking_and_process_resume_with_local_services(self):
        app = AcademicBooking.create(self.root / "booking")
        application = validator(app)

        def request(method, path, content=b"", query=""):
            environ = {
                "REQUEST_METHOD": method, "SCRIPT_NAME": "", "PATH_INFO": path,
                "QUERY_STRING": query,
                "CONTENT_LENGTH": str(len(content)), "wsgi.input": io.BytesIO(content),
            }
            setup_testing_defaults(environ)
            called = []
            def start_response(status, headers, exc_info=None):
                called.append(status)
            iterable = application(environ, start_response)
            try:
                payload = b"".join(iterable)
            finally:
                iterable.close()
            return called[0].split()[0], payload

        workbench_tasks.question(self.workspace, "D_NOTICE", "Approve the local notice exercise?")
        for task, priority, deps, gates in (
            ("website-form", 1, [], []),
            ("website-mobile", 2, [], []),
            ("booking-receipt", 3, ["website-form", "website-mobile"], ["D_NOTICE"]),
        ):
            workbench_tasks.add(self.workspace, task, task, priority, deps, gates, ["accept"])
        legacy = delivery_next_step.choose(workbench_tasks.review(self.workspace))
        self.assertEqual(legacy["ready_task_ids"], ["website-form", "website-mobile"])
        self.assertEqual(self.view("做網站")["next_task_ids"], legacy["ready_task_ids"])
        self.assertEqual(self.view("逐步查看")["next_task_ids"], ["website-form"])
        self.assertFalse(self.view("做網站")["current_questions"])
        self.assertFalse(self.view("接預約")["current_questions"])

        status, page = request("GET", "/")
        self.assertEqual(status, "200")
        self.assertIn(b'<form action="/book" method="post">', page)
        self.assertIn(b'name="viewport"', page)
        self.complete("website-form", "before-interruption", "WSGI form action observed")
        self.complete("website-mobile", "before-interruption", "Viewport declaration observed; layout UAT pending")

        args = [sys.executable, "-m", "src.delivery_routes", "booking", "--workspace",
                str(self.workspace)]
        before = (self.workspace / "workbench.sqlite3").read_bytes()
        child = subprocess.run(args, check=True, capture_output=True, timeout=15)
        view = json.loads(child.stdout)
        self.assertEqual(view["status"], "NEEDS_CURRENT_HUMAN_DECISION")
        self.assertEqual(view["current_questions"], [
            {"id": "D_NOTICE", "question": "Approve the local notice exercise?"}])
        self.assertEqual((self.workspace / "workbench.sqlite3").read_bytes(), before)
        with self.assertRaises(ValueError):
            workbench_tasks.start(self.workspace, "booking-receipt", "rejected",
                                  expected_revision=1)
        workbench_tasks.resolve_decision(self.workspace, "D_NOTICE", "approved",
                                        "Explicit synthetic fixture evidence", True)
        self.assertEqual(self.view("幫我做")["next_task_ids"], ["booking-receipt"])

        # The reservation commits even when the simulated notification store is down.
        with patch.object(app, "notice", side_effect=sqlite3.OperationalError("fixture")):
            status, data = request("POST", "/book", b"request=SYN-001")
        self.assertEqual(status, "503")
        self.assertEqual(json.loads(data)["synthetic_notice_count"], 0)
        status, data = request("GET", "/status", query="request=SYN-001")
        self.assertEqual(status, "200")
        self.assertEqual(json.loads(data)["result"], "RESERVED")
        self.assertEqual(json.loads(data)["synthetic_notice_count"], 0)
        # After reconciliation, repeat the same synthetic commitment key.
        for _ in range(2):
            status, data = request("POST", "/book", b"request=SYN-001")
            self.assertEqual(status, "200")
            self.assertEqual(json.loads(data)["synthetic_notice_count"], 1)
        status, data = request("POST", "/book", b"request=SYN-002")
        self.assertEqual(status, "409")
        self.assertEqual(json.loads(data)["synthetic_notice_count"], 0)
        self.assertEqual(request("POST", "/book", b"request=ordinary")[0], "400")
        self.assertEqual(app.reservations.snapshot()["reserved"], 1)
        self.complete("booking-receipt", "after-interruption", "One reservation and one receipt")
        self.assertEqual(self.view("繼續")["status"], "TASK_POOL_DONE_REQUIRES_INDEPENDENT_REVIEW")
        self.assertFalse(self.view("繼續")["deployment_verified"])
        print("ACADEMIC_DELIVERY_PASS local_form=1 booking=1 notice=1 recovery=1 process_resume=1")


if __name__ == "__main__":
    unittest.main()
