"""Offline agent-capability benchmark tests; no LLM or untrusted code execution."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from src import capability_reference as trusted
from src.capability_workbench import (
    REFERENCE, ROOT, TASKS, evaluate, load_submissions, load_tasks, score_task,
)


class CapabilityWorkbenchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = load_tasks()
        cls.refs = load_submissions(REFERENCE)

    def row(self, mutation=None):
        task = self.tasks[0]
        candidate = copy.deepcopy(self.refs[0])
        if mutation:
            mutation(candidate)
        return score_task(task, candidate)

    def test_public_varied_tasks_are_not_holdout(self):
        self.assertEqual(len(self.tasks), 5)
        self.assertEqual(len({x["category"] for x in self.tasks}), 5)
        self.assertEqual(sum(len(x["requirements"]) for x in self.tasks), 20)

    def test_self_authored_reference_scores_perfect_but_is_not_agent_success(self):
        report = evaluate()
        self.assertEqual(report["task_count"], 5)
        self.assertEqual(report["mean_structural_score"], 100.0)
        self.assertEqual(report["tasks_full_structural_score"], 5)
        self.assertEqual(report["submission_kind"],
                         "self_authored_reference_fixture_not_agent_result")
        self.assertFalse(report["real_llm_or_seven_agents_invoked"])
        self.assertFalse(report["actual_program_correctness_evaluated"])
        self.assertFalse(report["architecture_semantics_human_reviewed"])
        self.assertFalse(report["independent_holdout_evaluated"])
        self.assertFalse(report["formal_release_authorized"])

    def test_missing_requirement_acceptance_loses_coverage(self):
        row = self.row(lambda v: v["requirements"].pop())
        self.assertFalse(row["checks"]["requirements"])
        self.assertEqual(row["score"], 80)

    def test_empty_acceptance_loses_requirements_score(self):
        row = self.row(lambda v: v["requirements"][0].update(acceptance="OK"))
        self.assertFalse(row["checks"]["requirements"])

    def test_architecture_missing_required_component_fails(self):
        row = self.row(lambda v: v["architecture"]["components"].pop())
        self.assertFalse(row["checks"]["architecture"])
        self.assertEqual(row["score"], 85)

    def test_dag_cycle_is_rejected(self):
        row = self.row(lambda v: v["plan"][0].update(depends_on=["S7"]))
        self.assertFalse(row["checks"]["plan"])

    def test_unknown_dependency_is_rejected(self):
        row = self.row(lambda v: v["plan"][0].update(depends_on=["S99"]))
        self.assertFalse(row["checks"]["plan"])

    def test_plan_missing_expert_handoff_stage_loses_score(self):
        row = self.row(lambda v: v["plan"].pop())
        self.assertFalse(row["checks"]["plan"])

    def test_missing_negative_qa_coverage_is_rejected(self):
        row = self.row(lambda v: v["qa"].pop())
        self.assertFalse(row["checks"]["qa"])
        self.assertEqual(row["score"], 80)

    def test_handoff_skipping_a_role_fails(self):
        row = self.row(lambda v: v["handoffs"].pop())
        self.assertFalse(row["checks"]["handoff"])
        self.assertEqual(row["score"], 90)

    def test_unknown_write_safety_remains_hard_gate(self):
        row = self.row(lambda v: v["risk"].update(unknown_write_action="RETRY_POST"))
        self.assertFalse(row["checks"]["safety"])
        self.assertEqual(row["score"], 95)

    def test_false_claim_of_actual_agent_training_is_rejected(self):
        row = self.row(lambda v: v["claims"].update(real_agent_invoked=True))
        self.assertEqual(row["score"], 100)
        self.assertTrue(row["unsafe_unverified_claim"])
        self.assertFalse(row["task_passed"])

    def test_implementation_path_traversal_does_not_read_external_files(self):
        row = self.row(lambda v: v["implementation"].update(path="../../malicious.py"))
        self.assertFalse(row["checks"]["implementation_static"])

    def test_implementation_function_mismatch_loses_static_credit(self):
        row = self.row(lambda v: v["implementation"].update(function="fabricated"))
        self.assertFalse(row["checks"]["implementation_static"])

    def test_static_parsing_never_executes_candidate_python(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as d:
            # Isolated and never imported; a textual function with a return
            # may get structural credit but NOT program-correctness credit.
            target = Path(d) / "model_candidate.py"
            signal = Path(d) / "should_never_exist.txt"
            target.write_text(
                "from pathlib import Path\n"
                f"Path({str(signal)!r}).write_text('WRONG')\n"
                "def enrollment_status():\n    return 'FAKE'\n",
                encoding="utf-8",
            )
            submission = copy.deepcopy(self.refs[0])
            submission["implementation"]["path"] = str(target.relative_to(ROOT))
            row = score_task(self.tasks[0], submission)
            self.assertTrue(row["checks"]["implementation_static"])
            self.assertFalse(signal.exists())

    def test_unknown_task_and_duplicate_submission_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "submissions.json"
            for submitted in ([{**self.refs[0], "task_id": "B999"}],
                              [self.refs[0], self.refs[0]]):
                p.write_text(json.dumps({"schema_version": 1,
                                         "submissions": submitted}), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "unknown|duplicated"):
                    evaluate(p)

    def test_external_submission_is_not_recorded_as_real_model(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "candidate.json"
            p.write_text(json.dumps({"schema_version": 1,
                                     "submissions": [self.refs[0]]}), encoding="utf-8")
            result = evaluate(p)
            self.assertLess(result["mean_structural_score"], 100)
            self.assertEqual(result["submission_kind"],
                             "externally_supplied_structured_artifacts_origin_unverified")
            self.assertFalse(result["real_llm_or_seven_agents_invoked"])

    def test_coverage_is_not_accidentally_changed_from_100_score_weight(self):
        report = evaluate()
        self.assertTrue(all(row["score"] == 100 for row in report["cases"]))
        self.assertTrue(all(row["checks"]["requirements"] and row["checks"]["qa"]
                            for row in report["cases"]))


class TrustedReferenceCodeTest(unittest.TestCase):
    def test_enrollment_edges(self):
        self.assertEqual(trusted.enrollment_status(1, ["A"], "B"), "WAITLIST")
        self.assertEqual(trusted.enrollment_status(1, ["A"], "A"), "ALREADY")
        self.assertEqual(trusted.enrollment_status(1, [], "B"), "ACCEPT")
        self.assertEqual(trusted.enrollment_status(-1, [], "B"), "INVALID")

    def test_equipment_available_quantity(self):
        self.assertTrue(trusted.can_checkout(5, 2, 3))
        self.assertFalse(trusted.can_checkout(5, 2, 4))
        self.assertFalse(trusted.can_checkout(5, 2, -1))
        self.assertFalse(trusted.can_checkout(5, 2, 0))

    def test_shift_endpoint_touch_not_overlap(self):
        self.assertFalse(trusted.has_overlap([(1, 3)], (3, 4)))
        self.assertTrue(trusted.has_overlap([(1, 3)], (2, 4)))
        self.assertTrue(trusted.has_overlap([(5, 4)], (9, 10)))

    def test_stock_suggestion_only(self):
        self.assertEqual(trusted.restock_needed(10, 2, 8), 0)
        self.assertEqual(trusted.restock_needed(10, 2, 9), 1)
        self.assertEqual(trusted.restock_needed(5, 9, 10), 0)

    def test_meal_pickup_status_is_not_mutation(self):
        orders = {"T1": ("Z42", False), "T2": ("M1", True)}
        self.assertEqual(trusted.pickup_status(orders, "T1", "Z42"), "READY_FOR_REVIEW")
        self.assertEqual(trusted.pickup_status(orders, "T1", "wrong"), "DENY")
        self.assertEqual(trusted.pickup_status(orders, "T2", "M1"), "ALREADY")
        self.assertEqual(trusted.pickup_status(orders, "missing", "M1"), "UNKNOWN")
        self.assertFalse(orders["T1"][1])


if __name__ == "__main__":
    unittest.main()
