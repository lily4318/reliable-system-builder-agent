"""Native Git collaboration in disposable, file-only repositories.
No existing checkout, external remote, force push, or deployment.
"""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier


class GitNativeCollaborationTests(unittest.TestCase):
    def test_conflicts_dirty_worktree_revert_and_concurrent_push(self):
        exe = shutil.which("git")
        if not exe:
            if os.environ.get("GITHUB_ACTIONS") == "true":
                self.fail("PREINSTALLED_GIT_REQUIRED")
            self.skipTest("Git not available")
        with tempfile.TemporaryDirectory(prefix="git-training-") as tmp:
            root = Path(tmp).resolve()
            home = root / "home"
            home.mkdir()
            env = {"PATH": os.defpath, "HOME": str(home), "LC_ALL": "C",
                   "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                   "GIT_ALLOW_PROTOCOL": "file", "GIT_TERMINAL_PROMPT": "0",
                   "GIT_AUTHOR_NAME": "Synthetic", "GIT_AUTHOR_EMAIL": "lab@example.invalid",
                   "GIT_COMMITTER_NAME": "Synthetic", "GIT_COMMITTER_EMAIL": "lab@example.invalid"}
            def git(repo, *args, ok=True):
                self.assertTrue(repo == root or root in repo.parents)
                p = subprocess.run([exe, "-c", "commit.gpgsign=false", "-c", "core.hooksPath="+os.devnull,
                                    "-C", str(repo), *args], env=env, capture_output=True, text=True, timeout=20)
                self.assertEqual(p.returncode == 0, ok, (args, p.stdout, p.stderr))
                return p.stdout.strip() if ok else p.stdout+p.stderr
            def head(repo):
                return git(repo, "rev-parse", "HEAD")
            def put(repo, name, value):
                (repo/name).write_text(value+"\n", encoding="utf-8")
            def commit(repo, name, value, message):
                put(repo, name, value)
                git(repo, "add", "--", name)
                git(repo, "commit", "-m", message)
                return head(repo)
            def remote_head(repo):
                return git(repo, "ls-remote", "--refs", "origin", "refs/heads/lab").split()[0]
            remote = root/"remote.git"
            a, b = root/"a", root/"b"
            git(root, "init", "--bare", "--initial-branch=lab", str(remote))
            git(root, "clone", str(remote), str(a))
            base = commit(a, "policy.txt", "scope=base", "base")
            git(a, "push", "origin", "HEAD:refs/heads/lab")
            git(root, "clone", str(remote), str(b))
            self.assertEqual(head(b), base)
            self.assertEqual(remote_head(a), base)
            # Divergent branches and a real three-stage merge conflict.
            git(a, "switch", "-c", "feature")
            feature = commit(a, "policy.txt", "scope=feature", "feature")
            git(a, "switch", "lab")
            local = commit(a, "policy.txt", "scope=review", "review")
            self.assertEqual(git(a, "merge-base", "HEAD", "feature"), base)
            conflict = git(a, "merge", "--no-edit", "feature", ok=False)
            self.assertIn("CONFLICT", conflict)
            self.assertEqual(head(a), local)
            stages = git(a, "ls-files", "-u").splitlines()
            self.assertEqual([s.split()[2] for s in stages], ["1", "2", "3"])
            self.assertEqual(git(a, "show", ":1:policy.txt"), "scope=base")
            self.assertEqual(git(a, "show", ":2:policy.txt"), "scope=review")
            self.assertEqual(git(a, "show", ":3:policy.txt"), "scope=feature")
            git(a, "merge", "--abort")
            self.assertEqual(head(a), local)
            self.assertEqual(git(a, "status", "--porcelain"), "")
            # Dirty index plus unstaged and untracked changes must survive denial.
            put(a, "policy.txt", "staged draft")
            git(a, "add", "policy.txt")
            put(a, "policy.txt", "unstaged draft")
            put(a, "notes.txt", "private synthetic notes")
            def dirty():
                return (head(a), git(a, "status", "--porcelain"), git(a, "diff", "--binary"),
                        git(a, "diff", "--cached", "--binary"), (a/"notes.txt").read_bytes())
            before = dirty()
            git(a, "switch", "feature", ok=False)
            self.assertEqual(dirty(), before)
            git(a, "merge", "--no-edit", "feature", ok=False)
            self.assertEqual(dirty(), before)
            git(a, "stash", "push", "--include-untracked", "-m", "owned drafts")
            stash = git(a, "rev-parse", "refs/stash")
            self.assertEqual(git(a, "status", "--porcelain"), "")
            git(a, "stash", "apply", "--index", stash)
            self.assertEqual(dirty(), before)
            self.assertEqual(git(a, "rev-parse", "refs/stash"), stash)
            git(a, "stash", "push", "--include-untracked", "-m", "retain drafts")
            self.assertEqual(git(a, "status", "--porcelain"), "")
            git(a, "merge", "--no-edit", "feature", ok=False)
            merged = commit(a, "policy.txt", "scope=feature+review", "resolve explicitly")
            self.assertEqual(git(a, "rev-list", "--parents", "-n", "1", merged).split(), [merged, local, feature])
            self.assertEqual(git(a, "show", base+":policy.txt"), "scope=base")
            git(a, "push", "origin", "HEAD:refs/heads/lab")
            self.assertEqual(remote_head(a), merged)
            # Two clones with the same observed tip race to advance one ref.
            git(b, "fetch", "origin")
            git(b, "merge", "--ff-only", "origin/lab")
            ax = commit(a, "a.txt", "research A", "actor A")
            bx = commit(b, "b.txt", "research B", "actor B")
            barrier = Barrier(2)
            def push(repo):
                barrier.wait(timeout=10)
                p = subprocess.run([exe, "-C", str(repo), "push", "--porcelain", "origin", "HEAD:refs/heads/lab"],
                                   env=env, capture_output=True, text=True, timeout=20)
                return p.returncode
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(push, repo) for repo in (a,b)]
                results = [f.result(timeout=25) for f in futures]
            self.assertEqual(sum(code == 0 for code in results), 1)
            winner, loser = (a,b) if results[0] == 0 else (b,a)
            winning, losing = head(winner), head(loser)
            self.assertEqual({winning, losing}, {ax,bx})
            self.assertEqual(remote_head(a), winning)
            git(loser, "fetch", "origin")
            self.assertEqual(git(loser, "rev-parse", "origin/lab"), winning)
            git(loser, "merge", "--no-edit", "origin/lab")
            combined = head(loser)
            for rev in (winning, losing, merged):
                git(loser, "merge-base", "--is-ancestor", rev, combined)
            git(loser, "push", "origin", "HEAD:refs/heads/lab")
            self.assertEqual(remote_head(a), combined)
            self.assertEqual(git(remote, "show", combined+":a.txt"), "research A")
            self.assertEqual(git(remote, "show", combined+":b.txt"), "research B")
            # CAS against a dedicated non-checked-out ref, not a force push.
            git(remote, "update-ref", "refs/heads/probe", merged)
            git(remote, "update-ref", "refs/heads/probe", combined, merged)
            git(remote, "update-ref", "refs/heads/probe", winning, merged, ok=False)
            self.assertEqual(git(remote, "rev-parse", "refs/heads/probe"), combined)
            # Revert a known bad commit, preserving unrelated later history.
            bad = commit(loser, "bad.txt", "synthetic bad change", "bad")
            later = commit(loser, "later.txt", "keep later work", "later")
            git(loser, "revert", "--no-edit", bad)
            reverted = head(loser)
            self.assertEqual(git(loser, "rev-parse", "HEAD^"), later)
            git(loser, "merge-base", "--is-ancestor", bad, reverted)
            self.assertFalse((loser/"bad.txt").exists())
            self.assertEqual((loser/"later.txt").read_text(), "keep later work\n")
            git(loser, "push", "origin", "HEAD:refs/heads/lab")
            self.assertEqual(remote_head(a), reverted)
            git(remote, "fsck", "--full")
            self.assertEqual(git(remote, "for-each-ref", "--format=%(refname)", "refs/heads").splitlines(),
                             ["refs/heads/lab", "refs/heads/probe"])
            self.assertEqual(git(a, "show", stash+":policy.txt"), "unstaged draft")
            self.assertEqual(git(a, "show", stash+"^2:policy.txt"), "staged draft")
            self.assertEqual(git(a, "show", stash+"^3:notes.txt"), "private synthetic notes")
            print(f"GIT-COLLABORATION-PASS {git(root, '--version')} conflict-stages=3 dirty-preserved stash-index-untracked concurrent-winner=1 stale-cas-denied revert-history-preserved head={reverted}", flush=True)
