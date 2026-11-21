"""Evidence-limited repository understanding, not a DeepWiki or LLM evaluation.

Use reviewed project code and an isolated Git snapshot of public source files.
A valid citation establishes provenance, not the semantic truth of a claim.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from src import capability_workbench, engineering_workflow, workbench_learning

ROOT = Path(__file__).resolve().parents[1]
FILES = ("config/agent-policy.yaml", "config/skill-catalog.json",
         "src/engineering_workflow.py", "src/workbench_learning.py",
         "src/capability_workbench.py", "docs/ARCHITECTURE.md")


def validate_citation(citation, expected_ref, read):
    """Check provenance against a pinned snapshot, never execute cited text."""
    if type(citation) is not dict or citation.get("ref") != expected_ref:
        return "STALE_OR_UNBOUND"
    path = citation.get("path")
    if not isinstance(path, str) or path not in FILES:
        return "PATH_DENIED"
    start, end = citation.get("start"), citation.get("end")
    if type(start) is not int or type(end) is not int or not 1 <= start <= end:
        return "RANGE_INVALID"
    raw = read(expected_ref, path)
    if hashlib.sha256(raw).hexdigest() != citation.get("sha256"):
        return "SOURCE_CHANGED"
    lines = raw.decode("utf-8").splitlines()
    if end > len(lines):
        return "RANGE_INVALID"
    if "\n".join(lines[start-1:end]) != citation.get("excerpt"):
        return "QUOTE_MISMATCH"
    return "PROVENANCE_ONLY"


class SourceGroundedArchitectureTests(unittest.TestCase):
    def test_version_bound_citation_and_actual_runtime_claims(self):
        exe = shutil.which("git")
        if not exe:
            if os.environ.get("GITHUB_ACTIONS") == "true":
                self.fail("PREINSTALLED_GIT_REQUIRED")
            self.skipTest("Git unavailable")
        with tempfile.TemporaryDirectory(prefix="source-grounding-") as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            home = root / "home"
            home.mkdir()
            env = {"PATH": os.defpath, "HOME": str(home), "LC_ALL": "C",
                   "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                   "GIT_ALLOW_PROTOCOL": "file", "GIT_TERMINAL_PROMPT": "0",
                   "GIT_AUTHOR_NAME": "Synthetic", "GIT_AUTHOR_EMAIL": "lab@example.invalid",
                   "GIT_COMMITTER_NAME": "Synthetic", "GIT_COMMITTER_EMAIL": "lab@example.invalid"}
            def git(*args):
                p = subprocess.run([exe, "-c", "commit.gpgsign=false", "-c",
                                    "core.hooksPath="+os.devnull, "-C", str(repo), *args],
                                   env=env, capture_output=True, timeout=20)
                self.assertEqual(p.returncode, 0, (args, p.stderr))
                return p.stdout
            git("init", "--initial-branch=lab")
            for path in FILES:
                dest = repo/path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((ROOT/path).read_bytes())
            git("add", "--all")
            git("commit", "-m", "owned source snapshot")
            ref = git("rev-parse", "HEAD").decode().strip()
            def read(revision, path):
                return git("show", revision+":"+path)
            for path in FILES:
                self.assertEqual(read(ref, path), (ROOT/path).read_bytes())
            path = "src/engineering_workflow.py"
            raw = read(ref, path)
            lines = raw.decode().splitlines()
            start = next(i for i, s in enumerate(lines, 1) if '"mutation_permitted": False' in s)
            quote = {"ref":ref, "path":path, "start":start, "end":start,
                     "sha256":hashlib.sha256(raw).hexdigest(), "excerpt":lines[start-1]}
            self.assertEqual(validate_citation(quote, ref, read), "PROVENANCE_ONLY")
            for key, value, expected in (
                ("ref", "main", "STALE_OR_UNBOUND"),
                ("path", "../outside.py", "PATH_DENIED"),
                ("start", True, "RANGE_INVALID"),
                ("end", len(lines)+1, "RANGE_INVALID"),
                ("sha256", "0"*64, "SOURCE_CHANGED"),
                ("excerpt", '"mutation_permitted": True', "QUOTE_MISMATCH"),
            ):
                with self.subTest(key=key):
                    self.assertEqual(validate_citation(dict(quote, **{key:value}), ref, read), expected)
            # An unchanged blob does not prove that a previous revision is current.
            doc = repo/"docs/ARCHITECTURE.md"
            doc.write_bytes(doc.read_bytes()+b"\nSynthetic review note.\n")
            git("add", "--", "docs/ARCHITECTURE.md")
            git("commit", "-m", "change only architecture note")
            current = git("rev-parse", "HEAD").decode().strip()
            self.assertNotEqual(current, ref)
            self.assertEqual(read(current, path), raw)
            self.assertEqual(validate_citation(quote, current, read), "STALE_OR_UNBOUND")
            self.assertEqual(validate_citation(quote, ref, read), "PROVENANCE_ONLY")
            self.assertEqual(validate_citation(dict(quote, ref=current), current, read), "PROVENANCE_ONLY")
            # Independently execute actual reviewed code for bounded semantic claims.
            settings = {"target_confirmed":True, "source_sha":ref, "current_head_sha":ref,
                        "stage":"patch", "requirements_confirmed":True,
                        "acceptance_criteria":True, "dependencies_mapped":True,
                        "rollback_reviewed":True, "data_classified":True, "acl_reviewed":True,
                        "candidate_patch_authorized":True}
            for update, expected in (
                ({}, "READY_FOR_CANDIDATE_PATCH"),
                ({"current_head_sha":current}, "HOLD_SOURCE"),
                ({"write_outcome":"UNKNOWN"}, "READ_ONLY_RECONCILE"),
                ({"write_outcome":"PARTIAL"}, "READ_ONLY_RECONCILE"),
            ):
                result = engineering_workflow.route(dict(settings, **update))
                self.assertEqual(result["decision"], expected)
                self.assertIs(result["mutation_permitted"], False)
            catalog = json.loads(read(ref, "config/skill-catalog.json"))
            self.assertTrue(any(s["id"]=="deployment" for s in catalog["skills"]))
            review = workbench_learning.public_context("deployment", "SYN-WIKI", "deployment rollback")
            self.assertEqual(review["mode"], "PUBLIC_READ_ONLY")
            for key in ("private_workspace_read", "private_resolution_state_checked",
                        "prerequisites_verified", "authority_granted", "citation_persisted", "model_invoked"):
                self.assertIs(review[key], False)
            # A structurally valid implementation need not even be safe to import.
            # The canary exists only as text and must never be imported or executed.
            candidate = root/"candidate.py"
            sentinel = root/"should-not-exist"
            candidate.write_text("from pathlib import Path\nPath("+repr(str(sentinel))+
                                 ").write_text('executed')\ndef answer():\n    return 0\n")
            passed = capability_workbench._implementation_static(
                {"implementation":{"path":"candidate.py","function":"answer"}},
                {"implementation_function":"answer"}, root)
            self.assertIs(passed, True)
            self.assertFalse(sentinel.exists())
            self.assertEqual(git("status", "--porcelain"), b"")
            print("SOURCE-GROUNDED-ARCHITECTURE-PASS citation-negative=6 stale-same-blob-denied "
                  "historical-valid route-advisory public-context-no-authority AST-not-execution", flush=True)
