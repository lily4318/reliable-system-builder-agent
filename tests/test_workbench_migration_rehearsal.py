"""Synthetic evidence for workbench snapshot migration and rollback.

Uses the existing workbench APIs. SQLite copies and intentionally incomplete
copies stay inside temporary directories. This is not a production cutover.
"""
from contextlib import closing
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from src import delivery_routes, team_workbench as wb, workbench_learning as learning
from src import workbench_tasks as tasks

DB = "workbench.sqlite3"
SOURCE_REF = "evidence/audit.txt"


def backup(source, target):
    target.mkdir()
    uri = (source / DB).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as original, \
            closing(sqlite3.connect(target / DB)) as clone:
        original.backup(clone)


def logical_restore(snapshot, target):
    target.mkdir()
    with closing(wb.connect(snapshot)) as original, \
            closing(sqlite3.connect(target / DB)) as clone:
        original.execute("BEGIN")
        clone.executescript("\n".join(original.iterdump()))


def database_state(path):
    with closing(wb.connect(path)) as db:
        db.execute("BEGIN")
        integrity = db.execute("PRAGMA integrity_check").fetchall()
        if [row[0] for row in integrity] != ["ok"] or db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("snapshot failed integrity checks")
        schema = [tuple(row) for row in db.execute(
            "SELECT type,name,tbl_name,sql FROM sqlite_schema "
            "WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name"
        )]
        tables = {}
        for kind, table, _, _ in schema:
            if kind == "table":
                quoted = '"' + table.replace('"', '""') + '"'
                tables[table] = sorted(
                    (tuple(row) for row in db.execute("SELECT * FROM " + quoted)), key=repr
                )
        return schema, tables


class WorkbenchMigrationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def finish(self, path, task, session, result="PASS", revision=1, artifact=None):
        tasks.finish(path, task, session, {"check": result}, SOURCE_REF,
                     expected_revision=revision, artifact=artifact)

    def fixture(self):
        path = wb.initialize(self.root / "original", "Synthetic migration")
        tasks.setup(path)
        learning.setup(path)
        (path / "evidence").mkdir()
        (path / SOURCE_REF).write_text("Synthetic acceptance appendix\n", encoding="utf-8")
        tasks.question(path, "D_SCOPE", "Confirm synthetic scope")
        tasks.question(path, "D_RELEASE", "Future decision")
        tasks.resolve_decision(path, "D_SCOPE", "approved", "synthetic scope record", True)
        definitions = (
            ("website-intake", [], ["D_SCOPE"]),
            ("website-spec", ["website-intake"], []),
            ("booking-inflight", ["website-spec"], []),
            ("booking-release", [], ["D_RELEASE"]),
            ("website-audit", [], []),
            ("website-active", [], []),
        )
        for priority, (task, deps, gates) in enumerate(definitions):
            tasks.add(path, task, task, priority, deps, gates, ["check"])
        root = wb.handoff(path, "project-intake", "Scope v1", SOURCE_REF)["artifact_id"]
        bindings = dict.fromkeys(task for task, _, _ in definitions)
        bindings.update({"website-intake": "requirements", "website-spec": "specification"})
        tasks.bind_artifacts(path, bindings, dict.fromkeys(bindings, 1), root,
                             "binding-audit", "Synthetic binding evidence", True)
        tasks.start(path, "website-intake", "intake-1", expected_revision=2)
        self.finish(path, "website-intake", "intake-1", revision=2,
                    artifact={"expected_artifact_id": root, "inputs": {}})
        tasks.start(path, "website-spec", "spec-1", expected_revision=2)
        self.finish(path, "website-spec", "spec-1", revision=2, artifact={
            "expected_artifact_id": None, "inputs": {"requirements": root},
            "content": "Specification v1", "source_ref": SOURCE_REF,
        })
        for session, verdict in (("audit-1", "FAIL"), ("audit-2", "PASS")):
            tasks.start(path, "website-audit", session, expected_revision=1)
            self.finish(path, "website-audit", session, verdict)
        tasks.start(path, "booking-inflight", "booking-old", expected_revision=2)
        tasks.revise(path, "website-intake", 2, "change-2", "Confirmed scope v2",
                     confirmed=True, requirement={
                         "expected_artifact_id": root, "content": "Scope v2",
                         "source_ref": SOURCE_REF,
                     })
        tasks.start(path, "website-active", "owner-old", expected_revision=1)
        wb.remember(path, "preference", "handoff", "Short note", SOURCE_REF, "user-stated")
        return path

    def test_backup_and_logical_restore_preserve_records_and_behavior(self):
        source = self.fixture()
        checkpoint = self.root / "checkpoint"
        candidate = self.root / "candidate"
        backup(source, checkpoint)
        logical_restore(checkpoint, candidate)
        before = database_state(source)
        old_review = tasks.review(source)
        context = wb.context(source, "architecture-design")
        self.assertEqual(old_review["completed"], 1)
        self.assertEqual(old_review["failed_attempts"], 1)
        self.assertEqual(old_review["recovery_review"], ["booking-inflight"])
        self.assertEqual(old_review["running_review"], ["website-active"])
        self.assertEqual([d["id"] for d in old_review["open_decisions"]], ["D_RELEASE"])
        self.assertFalse(context["artifacts"]["requirements"]["current"])
        self.assertFalse(context["artifacts"]["specification"]["current"])
        self.assertEqual(context["artifacts"]["requirements"]["content"], "Scope v2")
        self.assertEqual(tasks.revision_status(source, "change-2")["status"], "COMMITTED")
        for path in (checkpoint, candidate):
            with self.subTest(path=path.name):
                self.assertEqual(database_state(path), before)
                self.assertEqual(wb.context(path, "architecture-design"), context)
                review = tasks.review(path)
                self.assertEqual(review, old_review)
                self.assertEqual(delivery_routes.route("resume", review),
                                 delivery_routes.route("resume", old_review))
                self.assertEqual(tasks.revision_status(path, "change-2"),
                                 tasks.revision_status(source, "change-2"))
                with self.assertRaisesRegex(ValueError, "not owned"):
                    self.finish(path, "website-active", "new-owner")
                with self.assertRaisesRegex(ValueError, "not ready"):
                    tasks.start(path, "booking-release", "new-owner", expected_revision=1)
                self.assertEqual(database_state(path), before)
        self.assertFalse((candidate / SOURCE_REF).exists())
        (candidate / "evidence").mkdir()
        shutil.copyfile(source / SOURCE_REF, candidate / SOURCE_REF)
        self.assertEqual((candidate / SOURCE_REF).read_bytes(), (source / SOURCE_REF).read_bytes())
        print("WORKBENCH_MIGRATION_EQUIVALENCE tables={} rows={} evidence_file_separate=1".format(
            len(before[1]), sum(map(len, before[1].values()))))

    def test_rollback_requires_writing_fence_and_post_checkpoint_reconciliation(self):
        source = self.fixture()
        checkpoint = self.root / "checkpoint"
        candidate = self.root / "candidate"
        backup(source, checkpoint)
        before = database_state(checkpoint)
        logical_restore(checkpoint, candidate)
        self.finish(candidate, "website-active", "owner-old")
        old_peer = self.root / "old-peer"
        backup(checkpoint, old_peer)
        # The same owner can still finish on a different writable copy.
        self.finish(old_peer, "website-active", "owner-old", result="FAIL")
        self.assertNotEqual(tasks.review(candidate)["history"], tasks.review(old_peer)["history"])
        tasks.resolve_decision(candidate, "D_RELEASE", "approved-after-copy", "new evidence", True)
        post_cutover = self.root / "post-cutover"
        backup(candidate, post_cutover)

        rollback = self.root / "rollback"
        backup(checkpoint, rollback)
        self.assertEqual(database_state(rollback), before)
        self.assertEqual(tasks.review(rollback), tasks.review(checkpoint))
        self.assertEqual(delivery_routes.route("resume", tasks.review(rollback)),
                         delivery_routes.route("resume", tasks.review(checkpoint)))
        old = tasks.review(rollback)
        new = tasks.review(post_cutover)
        self.assertEqual(old["completed"], 1)
        self.assertEqual(new["completed"], 2)
        self.assertEqual([d["id"] for d in old["open_decisions"]], ["D_RELEASE"])
        self.assertFalse(new["open_decisions"])
        self.assertEqual(new["history"][:-1], old["history"])
        self.assertEqual(new["history"][-1]["kind"], "PASS")
        self.assertEqual(database_state(candidate), database_state(post_cutover))
        self.assertEqual(database_state(source), before)
        print("WORKBENCH_ROLLBACK_EQUIVALENCE checkpoint=1 later_pass=1 later_decision=1 dual_writer=1")

    def test_omitted_binding_changes_read_behavior_with_same_task_rows(self):
        source = self.fixture()
        projection = self.root / "projection"
        backup(source, projection)
        with closing(wb.connect(projection)) as db, db:
            db.execute("DROP TABLE task_artifact_bindings")
        main = database_state(source)[1]
        partial = database_state(projection)[1]
        self.assertEqual({k: v for k, v in main.items() if k != "task_artifact_bindings"}, partial)
        self.assertFalse(wb.context(source, "requirements-spec")["artifacts"]["requirements"]["current"])
        self.assertTrue(wb.context(projection, "requirements-spec")["artifacts"]["requirements"]["current"])
        print("WORKBENCH_NON_EQUIVALENT omitted_binding_reactivates_requirement=1")

    def test_wal_main_file_copy_misses_committed_decision(self):
        source = self.fixture()
        naive = self.root / "main-only"
        naive.mkdir()
        with closing(wb.connect(source)) as keeper:
            self.assertEqual(keeper.execute("PRAGMA journal_mode=WAL").fetchone()[0], "wal")
            keeper.execute("PRAGMA wal_autocheckpoint=0")
            keeper.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            keeper.execute("BEGIN IMMEDIATE")
            keeper.execute("INSERT INTO task_decisions(id, question) VALUES (?, ?)",
                           ("D_WAL", "Committed during copy window"))
            keeper.commit()
            shutil.copyfile(source / DB, naive / DB)
            complete = self.root / "wal-aware"
            backup(source, complete)
        self.assertNotIn("D_WAL", {d["id"] for d in tasks.review(naive)["decisions"]})
        self.assertIn("D_WAL", {d["id"] for d in tasks.review(complete)["decisions"]})
        self.assertEqual(database_state(source), database_state(complete))
        print("WORKBENCH_NON_EQUIVALENT main_file_only_omits_committed_wal=1")
