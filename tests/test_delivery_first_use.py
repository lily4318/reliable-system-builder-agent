"""First-use acceptance for the default delivery entry with synthetic data."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from src import delivery_routes as delivery, team_workbench as wb, workbench_tasks as tasks


class DeliveryFirstUseTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.workspace = self.root / "fresh"

    def run_cli(self, intent, *flags, check=True):
        return subprocess.run(
            [sys.executable, "-m", "src.delivery_routes", intent,
             "--workspace", str(self.workspace), *flags],
            capture_output=True, check=check, timeout=15,
        )

    def test_clean_cli_initialization_then_delivery_and_resume(self):
        new = json.loads(self.run_cli("init", "--label", "Synthetic study").stdout)
        self.assertEqual(new["status"], "WORKSPACE_INITIALIZED")
        self.assertFalse(new["authorization_granted"])
        self.assertFalse(new["deployment_verified"])
        database = self.workspace / "workbench.sqlite3"
        frozen = database.read_bytes()
        self.assertFalse(tasks.review(self.workspace)["tasks"])
        self.assertEqual(wb.context(self.workspace, "project-intake")["project"], "Synthetic study")
        self.assertGreater(len(new["seeded_case_keys"]), 0)
        answers = self.root / "answers.json"
        answers.write_text(json.dumps({"purpose": "Synthetic study booking"}), encoding="utf-8")
        website = json.loads(self.run_cli("website", "--answers", str(answers)).stdout)
        self.assertNotIn("purpose", [q["id"] for q in website["missing_intake_questions"]])
        self.assertFalse(website["specification_draft"]["specification_approved"])
        self.assertEqual(database.read_bytes(), frozen)

        tasks.question(self.workspace, "D_NOTICE", "Confirm the sample notification?")
        tasks.add(self.workspace, "website-form", "Form", 0, [], [], ["accept"])
        tasks.add(self.workspace, "booking-notice", "Notice", 1, ["website-form"],
                  ["D_NOTICE"], ["accept"])
        website = json.loads(self.run_cli("website").stdout)
        self.assertEqual(website["next_task_ids"], ["website-form"])
        self.assertEqual(website["current_questions"], [])
        tasks.start(self.workspace, "website-form", "fixture-owner", expected_revision=1)
        tasks.finish(self.workspace, "website-form", "fixture-owner", {"accept": "PASS"},
                     "Synthetic form evidence", expected_revision=1)
        resumed = json.loads(self.run_cli("resume").stdout)
        booking = json.loads(self.run_cli("booking").stdout)
        self.assertEqual(booking["ask_decision_ids"], ["D_NOTICE"])
        self.assertEqual(resumed["current_questions"], booking["current_questions"])
        self.assertFalse(booking["authorization_granted"])
        before = database.read_bytes()
        rejected = self.run_cli("init", "--label", "Second initialization", check=False)
        self.assertEqual(rejected.returncode, 2)
        self.assertEqual(database.read_bytes(), before)
        print("DELIVERY_FIRST_USE_PASS workspace=1 website=1 booking=1 resume=1")

    def test_failed_setup_leaves_destination_available_for_fresh_init(self):
        with patch.object(delivery.workbench_learning, "setup", side_effect=OSError("fixture")):
            with self.assertRaisesRegex(OSError, "fixture"):
                delivery.initialize_workspace(self.workspace, "Synthetic failure")
        self.assertEqual(list(self.root.iterdir()), [])
        self.assertEqual(delivery.initialize_workspace(self.workspace, "Retry")["status"],
                         "WORKSPACE_INITIALIZED")

    def test_existing_empty_directory_is_rejected(self):
        self.workspace.mkdir()
        with self.assertRaises(FileExistsError):
            delivery.initialize_workspace(self.workspace, "Synthetic project")
        self.assertEqual(list(self.workspace.iterdir()), [])
