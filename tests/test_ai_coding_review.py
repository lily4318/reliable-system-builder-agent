"""Offline authored fixtures: no model, provider, network, or production tool."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def sha(data):
    return hashlib.sha256(data).hexdigest()


# Trusted synthetic data classification, not a generic secret scanner.
def context_packet(root, requested, approved, cap=256):
    result = {}
    for name in requested:
        if name not in approved or name in result:
            raise ValueError("CONTEXT_SCOPE")
        path = root / name
        if path.is_symlink() or path.resolve() != root / name:
            raise ValueError("CONTEXT_PATH")
        data = path.read_bytes()
        if sha(data) != approved[name]:
            raise ValueError("CONTEXT_DRIFT")
        result[name] = data.decode("utf-8")
    payload = json.dumps(result, sort_keys=True).encode()
    if len(payload) > cap:
        raise ValueError("CONTEXT_BUDGET")
    return payload


class Budget:
    """Single-process synthetic integer units; no provider billing semantics."""
    def __init__(self, limit):
        self.remaining = limit
        self.pending = None
        self.seen = set()

    def reserve(self, attempt, maximum):
        if self.pending is not None or attempt in self.seen:
            raise ValueError("RECONCILE_FIRST")
        if type(maximum) is not int or not 0 < maximum <= self.remaining:
            raise ValueError("BUDGET_STOP")
        self.remaining -= maximum
        self.pending = (attempt, maximum)
        self.seen.add(attempt)

    def settle(self, attempt, actual):
        if (self.pending is None or self.pending[0] != attempt or
                type(actual) is not int or not 0 <= actual <= self.pending[1]):
            raise ValueError("USAGE_UNKNOWN_OR_INVALID")
        self.remaining += self.pending[1] - actual
        self.pending = None


# Two fixed, self-authored implementations; never run arbitrary candidate code.
GOOD = b"def can_edit(role, requested, assigned):\n    return role == 'editor' and requested == assigned\n"
BAD = b"def can_edit(role, requested, assigned):\n    return role == 'editor'\n"
BASE = b"def can_edit(role, requested, assigned):\n    return False\n"
ORACLE = """import candidate
assert candidate.can_edit('editor', 'A', 'A') is True
assert candidate.can_edit('editor', 'B', 'A') is False
assert candidate.can_edit('reader', 'A', 'A') is False
"""


def review_write(root, target, before, proposed, approval):
    # Narrow owned lab, trusted writer; no shell/general tool dispatcher.
    if target != "candidate.py" or proposed not in (GOOD, BAD):
        raise ValueError("TOOL_SCOPE")
    p = root / target
    if p.is_symlink() or p.read_bytes() != before:
        raise ValueError("SOURCE_DRIFT")
    if approval != ("synthetic-reviewer", target, sha(before), sha(proposed)):
        raise ValueError("APPROVAL_MISMATCH")
    p.write_bytes(proposed)


class AICodingReviewTests(unittest.TestCase):
    def test_context_actual_bytes_and_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            public = root / "spec.txt"
            public.write_text("synthetic public scope")
            private = root / "excluded.txt"
            private.write_text("SYNTHETIC_PRIVATE_CANARY")
            approved = {"spec.txt": sha(public.read_bytes())}
            payload = context_packet(root, ["spec.txt"], approved)
            self.assertEqual(json.loads(payload), {"spec.txt": "synthetic public scope"})
            self.assertNotIn(b"SYNTHETIC_PRIVATE_CANARY", payload)
            for request in (["excluded.txt"], ["../excluded.txt"], ["spec.txt", "spec.txt"]):
                with self.assertRaisesRegex(ValueError, "CONTEXT_SCOPE"):
                    context_packet(root, request, approved)
            with self.assertRaisesRegex(ValueError, "CONTEXT_BUDGET"):
                context_packet(root, ["spec.txt"], approved, cap=1)
            public.write_text("changed instructions")
            with self.assertRaisesRegex(ValueError, "CONTEXT_DRIFT"):
                context_packet(root, ["spec.txt"], approved)
            public.unlink()
            public.symlink_to(private)
            with self.assertRaisesRegex(ValueError, "CONTEXT_PATH"):
                context_packet(root, ["spec.txt"], approved)

    def test_reservation_unknown_usage_and_no_replay(self):
        b = Budget(5)
        b.reserve("attempt-1", 4)
        self.assertEqual(b.remaining, 1)
        # Lost usage receipt: keep full reservation, even a cheap next request stops.
        for attempt in ("attempt-1", "attempt-2"):
            with self.assertRaisesRegex(ValueError, "RECONCILE_FIRST"):
                b.reserve(attempt, 1)
        for actual in (None, True, -1, 5):
            with self.assertRaisesRegex(ValueError, "USAGE_UNKNOWN_OR_INVALID"):
                b.settle("attempt-1", actual)
        self.assertEqual((b.remaining, b.pending), (1, ("attempt-1", 4)))
        b.settle("attempt-1", 2)
        self.assertEqual(b.remaining, 3)
        with self.assertRaisesRegex(ValueError, "RECONCILE_FIRST"):
            b.reserve("attempt-1", 1)
        for maximum in (None, True, -1, 4):
            with self.assertRaisesRegex(ValueError, "BUDGET_STOP"):
                b.reserve("attempt-2", maximum)
        b.reserve("attempt-2", 3)
        b.settle("attempt-2", 3)
        self.assertEqual(b.remaining, 0)

    def test_review_binding_and_real_functional_oracle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            target = root / "candidate.py"
            target.write_bytes(BASE)
            other = root / "unrelated.txt"
            other.write_bytes(b"keep")
            oracle = root / "oracle.py"
            oracle.write_text(ORACLE)
            approval = ("synthetic-reviewer", "candidate.py", sha(BASE), sha(GOOD))
            with self.assertRaisesRegex(ValueError, "APPROVAL_MISMATCH"):
                review_write(root, "candidate.py", BASE, BAD, approval)
            with self.assertRaisesRegex(ValueError, "TOOL_SCOPE"):
                review_write(root, "unrelated.txt", BASE, GOOD, approval)
            self.assertEqual(target.read_bytes(), BASE)
            self.assertEqual(other.read_bytes(), b"keep")
            # Run only the two trusted authored fixtures, on the same untouched oracle.
            for proposed, expected in ((BAD, 1), (GOOD, 0)):
                before = target.read_bytes()
                receipt = ("synthetic-reviewer", "candidate.py", sha(before), sha(proposed))
                review_write(root, "candidate.py", before, proposed, receipt)
                self.assertEqual(target.read_bytes(), proposed)
                proc = subprocess.run([sys.executable, "-E", "-s", "-B", str(oracle)],
                                      cwd=root, env={}, capture_output=True, timeout=5)
                self.assertEqual(proc.returncode, expected)
                if expected:
                    self.assertIn(b"AssertionError", proc.stderr)
            self.assertEqual(oracle.read_text(), ORACLE)
            self.assertEqual(other.read_bytes(), b"keep")
            with self.assertRaisesRegex(ValueError, "SOURCE_DRIFT"):
                review_write(root, "candidate.py", BASE, GOOD, approval)
            self.assertEqual(target.read_bytes(), GOOD)


if __name__ == "__main__":
    unittest.main()
