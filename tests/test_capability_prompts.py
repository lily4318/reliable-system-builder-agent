"""Public benchmark task packet is independent of public authored gold."""
import unittest
from src.capability_prompts import task_prompt


class CapabilityTaskPacketTest(unittest.TestCase):
    def test_prompt_has_user_needs_not_reference_components(self):
        task = task_prompt("B001")
        self.assertEqual(task["task_id"], "B001")
        self.assertEqual(len(task["requirements"]), 4)
        self.assertFalse(task["benchmark_gold_components_included"])
        self.assertFalse(task["reference_code_included"])
        self.assertFalse(task["actual_model_execution_by_generator"])
        self.assertNotIn("required_components", task)
        self.assertNotIn("capacity-policy", str(task))
        self.assertIn("unknown_write_action", task["submission_shape"]["risk"])

    def test_all_five_realistic_task_packets_distinct(self):
        packets = [task_prompt(f"B{i:03d}") for i in range(1, 6)]
        self.assertEqual(len({p["brief"] for p in packets}), 5)
        self.assertEqual(len({p["required_python_function"] for p in packets}), 5)

    def test_unknown_task_must_not_look_like_a_valid_assignment(self):
        with self.assertRaisesRegex(ValueError, "unknown"):
            task_prompt("B999")


if __name__ == "__main__":
    unittest.main()
