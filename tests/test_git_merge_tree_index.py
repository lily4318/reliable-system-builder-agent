"""Native Git merge preview and partial staging in disposable repositories.

No real PR mutation, remote network, GUI, force push, or deployment.
"""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class GitMergeTreeIndexTests(unittest.TestCase):
    def test_merge_preview_and_partial_index_preserve_worktree(self):
        exe = shutil.which("git")
        if not exe:
            if os.environ.get("GITHUB_ACTIONS") == "true":
                self.fail("PREINSTALLED_GIT_REQUIRED")
            self.skipTest("Git unavailable")
        with tempfile.TemporaryDirectory(prefix="git-preview-") as tmp:
            root = Path(tmp).resolve()
            repo = root / "repo"
            home = root / "home"
            home.mkdir()
            env = {"PATH": os.defpath, "HOME": str(home), "LC_ALL": "C",
                   "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                   "GIT_ALLOW_PROTOCOL": "file", "GIT_TERMINAL_PROMPT": "0",
                   "GIT_AUTHOR_NAME": "Synthetic", "GIT_AUTHOR_EMAIL": "lab@example.invalid",
                   "GIT_COMMITTER_NAME": "Synthetic", "GIT_COMMITTER_EMAIL": "lab@example.invalid"}
            def git(cwd, *args, code=0, data=None):
                self.assertTrue(cwd == root or root in cwd.parents)
                p = subprocess.run([exe, "--no-optional-locks", "-c", "commit.gpgsign=false",
                                    "-c", "core.hooksPath="+os.devnull, "-C", str(cwd), *args],
                                   input=data, env=env, capture_output=True, timeout=20)
                self.assertEqual(p.returncode, code, (args, p.stdout, p.stderr))
                return p.stdout
            def oid(cwd, ref="HEAD"):
                return git(cwd, "rev-parse", ref).decode().strip()
            def put(name, data):
                (repo/name).write_bytes(data)
            def commit(message):
                git(repo, "add", "--all")
                git(repo, "commit", "-m", message)
                return oid(repo)
            git(root, "init", "--initial-branch=lab", str(repo))
            put("policy.txt", b"scope=base\n")
            put("draft file.txt", b"first=old\nsecond=old\n")
            base = commit("base")
            git(repo, "switch", "-c", "clean")
            put("lesson.txt", b"lesson=approved\n")
            clean = commit("independent change")
            git(repo, "switch", "-c", "conflict", base)
            put("policy.txt", b"scope=other\n")
            conflict = commit("conflicting change")
            git(repo, "switch", "lab")
            put("policy.txt", b"scope=review\n")
            lab = commit("review")
            self.assertEqual(oid(repo, "lab"), lab)
            # Partial staging of one file, with a second edit and a new file.
            path = "draft file.txt"
            full = b"first=staged\nsecond=unstaged\n"
            part = b"first=staged\nsecond=old\n"
            put(path, full)
            put("notes.txt", b"untracked draft\n")
            patch = (b"diff --git a/draft file.txt b/draft file.txt\n"
                     b"--- a/draft file.txt\n+++ b/draft file.txt\n"
                     b"@@ -1,2 +1,2 @@\n-first=old\n+first=staged\n second=old\n")
            git(repo, "apply", "--cached", "--check", data=patch)
            git(repo, "apply", "--cached", data=patch)
            self.assertEqual(git(repo, "show", ":"+path), part)
            self.assertEqual((repo/path).read_bytes(), full)
            self.assertEqual(git(repo, "status", "--porcelain=v1", "-z"),
                             b"MM draft file.txt\0?? notes.txt\0")
            index = repo/".git/index"
            def snapshot():
                return (oid(repo), git(repo, "symbolic-ref", "HEAD"),
                        git(repo, "show-ref"), index.read_bytes(),
                        git(repo, "status", "--porcelain=v1", "-z"),
                        git(repo, "diff", "--binary"), git(repo, "diff", "--cached", "--binary"),
                        (repo/path).read_bytes(), (repo/"notes.txt").read_bytes(),
                        (repo/"policy.txt").read_bytes())
            before = snapshot()
            # Stale partial patch cannot be reapplied to an already edited index.
            git(repo, "apply", "--cached", "--check", code=1, data=patch)
            self.assertEqual(snapshot(), before)
            # True modern merge-tree works on pinned commits, not dirty files.
            tree = git(repo, "merge-tree", "--write-tree", lab, clean).decode().strip()
            self.assertEqual(git(repo, "cat-file", "-t", tree), b"tree\n")
            self.assertEqual(git(repo, "show", tree+":"+path), b"first=old\nsecond=old\n")
            self.assertEqual(git(repo, "show", tree+":policy.txt"), b"scope=review\n")
            self.assertEqual(git(repo, "show", tree+":lesson.txt"), b"lesson=approved\n")
            self.assertEqual(snapshot(), before)
            bad = git(repo, "merge-tree", "--write-tree", lab, conflict, code=1)
            self.assertIn(b"CONFLICT", bad)
            # A tree object may exist even when the merge is conflicted.
            badtree = bad.splitlines()[0].decode()
            self.assertEqual(git(repo, "cat-file", "-t", badtree), b"tree\n")
            self.assertEqual(snapshot(), before)
            # Independent actual merge in a detached worktree matches clean preview.
            detached = root/"detached"
            git(repo, "worktree", "add", "--detach", str(detached), lab)
            git(detached, "merge", "--no-commit", "--no-ff", clean)
            self.assertEqual(oid(detached), lab)
            self.assertEqual(git(detached, "write-tree").decode().strip(), tree)
            git(detached, "merge", "--abort")
            git(repo, "worktree", "remove", str(detached))
            self.assertEqual(snapshot(), before)
            # Unstage only; working content and untracked bytes stay intact.
            git(repo, "restore", "--staged", "--", path)
            self.assertEqual(git(repo, "show", ":"+path), b"first=old\nsecond=old\n")
            self.assertEqual((repo/path).read_bytes(), full)
            self.assertEqual((repo/"notes.txt").read_bytes(), b"untracked draft\n")
            git(repo, "apply", "--cached", data=patch)
            git(repo, "commit", "-m", "commit only selected change")
            new = oid(repo)
            self.assertEqual(oid(repo, "HEAD^"), lab)
            self.assertEqual(git(repo, "show", new+":"+path), part)
            self.assertEqual((repo/path).read_bytes(), full)
            self.assertEqual(git(repo, "status", "--porcelain=v1", "-z"),
                             b" M draft file.txt\0?? notes.txt\0")
            # Old evidence is bound to the old pair even when the new merge is clean.
            self.assertNotEqual(new, lab)
            newtree = git(repo, "merge-tree", "--write-tree", new, clean).decode().strip()
            self.assertNotEqual(newtree, tree)
            self.assertEqual(git(repo, "show", newtree+":"+path), part)
            self.assertEqual(git(repo, "show", base+":"+path), b"first=old\nsecond=old\n")
            self.assertEqual(git(repo, "show", new+":policy.txt"), b"scope=review\n")
            git(repo, "fsck", "--full")
            print("GIT-MERGE-TREE-INDEX-PASS " + git(repo, "--version").decode().strip()
                  + " clean-preview actual-tree-match conflict-tree-rejected stale-preview"
                  + " partial-stage stale-patch-denied unstage-preserved commit-index-only"
                  + " dirty-worktree-preserved", flush=True)
