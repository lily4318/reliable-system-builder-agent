"""Functional workspace regression, using synthetic project artifacts only."""
import tempfile
from pathlib import Path
import unittest
from src.team_workbench import (ROOT, catalog, initialize, context, handoff,
                                remember, distill, resolve, connect)
from contextlib import closing


class TeamWorkbenchTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/"private"
        initialize(self.root,"synthetic workshop")
    def test_skill_catalog_all_roles_and_files(self):
        c=catalog()
        self.assertEqual(len(c),12)
        self.assertEqual(len({s["role"] for s in c.values()}),7)
        self.assertTrue(all((ROOT/s["path"]).is_file() for s in c.values()))
        self.assertTrue(all(set(s["requires"]) <= {v["produces"] for v in c.values()} for s in c.values()))
    def test_real_content_handoff_and_resume(self):
        self.assertEqual(context(self.root,"architecture-design")["status"],"NEEDS_PREREQUISITES")
        handoff(self.root,"project-intake","REQ-1: synthetic registration","fixture")
        handoff(self.root,"requirements-spec","Confirmed synthetic specification","fixture")
        handoff(self.root,"architecture-design","SQLite transaction with uniqueness constraint","fixture")
        handoff(self.root,"task-planning","Task 1 -> Task 2","fixture")
        handoff(self.root,"implement-feature","Local implementation candidate","fixture")
        revisited=context(self.root,"resume-project")
        self.assertIn("SQLite transaction",revisited["artifacts"]["architecture"]["content"])
        self.assertFalse(revisited["authorization_granted"])
        self.assertFalse(revisited["model_or_subagent_invoked"])
    def test_revised_requirement_invalidates_downstream(self):
        handoff(self.root,"project-intake","first","fixture")
        handoff(self.root,"requirements-spec","first spec","fixture")
        handoff(self.root,"architecture-design","first architecture","fixture")
        handoff(self.root,"project-intake","edited","fixture")
        self.assertFalse(context(self.root,"resume-project")["artifacts"]["architecture"]["current"])
        with self.assertRaises(ValueError):
            handoff(self.root,"task-planning","stale plan","fixture")
    def test_latest_only_materializes_current_heads_preserving_history(self):
        import sqlite3
        from src.team_workbench import _latest
        with closing(connect(self.root)) as db, db:
            # Seed history directly in the original schema, not a new application.
            kinds=["requirements","specification","architecture"]
            db.executemany(
                "INSERT INTO artifacts(kind,skill,source_ref,content,dependencies) VALUES(?,?,?,?,?)",
                [(kinds[i%3],"fixture","source-"+str(i),"x"*2048+str(i),"{}")
                 for i in range(300)])
            # Uneven latest revisions: first appearance order must not change.
            db.execute("INSERT INTO artifacts(kind,skill,source_ref,content,dependencies) VALUES(?,?,?,?,?)",
                       ("requirements","fixture","edited","newest","{}"))
            old_rows=db.execute("SELECT * FROM artifacts ORDER BY id").fetchall()
            expected={r["kind"]:dict(r) for r in old_rows}
            materialized=[]
            def count_rows(cursor,row):
                materialized.append(row[0])
                return sqlite3.Row(cursor,row)
            db.row_factory=count_rows
            actual=_latest(db)
            db.row_factory=sqlite3.Row
            self.assertEqual(actual,expected)
            self.assertEqual(list(actual),list(expected))
            self.assertEqual(len(materialized),len(kinds),
                             "current-head lookup must not materialize history")
            self.assertEqual(db.execute("SELECT count(*) FROM artifacts").fetchone()[0],301)

    def test_latest_empty_original_schema(self):
        from src.team_workbench import _latest
        with closing(connect(self.root)) as db:
            self.assertEqual(_latest(db),{})

    def test_learning_dedup_conflict_review_and_history(self):
        a=remember(self.root,"preference","UI","Editable choices","explicit fixture","user-stated")
        b=remember(self.root,"preference","UI","Editable choices","explicit fixture","user-stated")
        self.assertEqual(a["memory_id"],b["memory_id"])
        self.assertTrue(b["duplicate"])
        c=remember(self.root,"preference","UI","Editable choices and cancel","later explicit fixture","user-stated")
        self.assertTrue(distill(self.root)["groups"][0]["review_needed"])
        resolve(self.root,a["memory_id"],c["memory_id"],"synthetic explicit confirmation")
        self.assertEqual(len(context(self.root,"project-intake")["memory"]),1)
        with closing(connect(self.root)) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM memory").fetchone()[0],2)
    def test_case_and_knowledge_reuse(self):
        remember(self.root,"case","booking","Duplicate registration repro and fix","synthetic test case","observed")
        remember(self.root,"knowledge","booking","Use database uniqueness constraint","synthetic reference","candidate")
        ctx=context(self.root,"debug-and-repair","booking")
        self.assertEqual(len(ctx["memory"]),2)
        self.assertEqual({m["basis"] for m in ctx["memory"]},{"observed","candidate"})
    def test_private_location_and_project_separation(self):
        with self.assertRaises(ValueError):
            initialize(ROOT/"private","bad")
        other=Path(self.tmp.name)/"other"
        initialize(other,"other synthetic project")
        remember(self.root,"lesson","work","Project one note","fixture","candidate")
        self.assertEqual(context(other,"resume-project")["memory"],[])
    def test_candidate_cannot_override_statement(self):
        a=remember(self.root,"preference","UI","Explicit preference","fixture","user-stated")
        b=remember(self.root,"preference","UI","Inferred preference","fixture","candidate")
        with self.assertRaises(ValueError):
            resolve(self.root,a["memory_id"],b["memory_id"],"invalid override")


if __name__=="__main__":
    unittest.main()
