"""Synthetic operator-interface tests; no model or actual private case."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from src.website_holdout_walkthrough import (
    rehearse, prepare_review, rating_template, combine_reviews,
)
from src.website_holdout_compare import ROOT, DIMENSIONS


class HoldoutWalkthroughTest(unittest.TestCase):
    def load(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def cli(self,*args):
        return subprocess.run([sys.executable,"-m","src.website_holdout_walkthrough",
                              *map(str,args)],cwd=ROOT,capture_output=True,text=True)

    def test_cli_rehearsal_five_cases_ten_specs_twenty_synthetic_ratings(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"trial"
            result=self.cli("rehearse","--directory",root)
            self.assertEqual(result.returncode,0,result.stderr)
            summary=json.loads(result.stdout)
            self.assertEqual(summary["status"],"SYNTHETIC_REHEARSAL_ONLY")
            self.assertEqual(summary["case_count"],5)
            self.assertEqual(summary["outputs"],10)
            self.assertEqual(summary["rating_count"],20)
            self.assertEqual(summary["paired_mean_delta"],0)
            self.assertFalse(summary["real_agent_executed"])
            self.assertFalse(summary["real_holdout_created"])
            report=self.load(root/"comparison.json")
            self.assertTrue(report["ratings_are_synthetic"])
            self.assertFalse(report["model_capability_improvement_verified"])
            self.assertEqual(len(list((root/"specifications").glob("*.json"))),10)

    def test_reviewer_packet_includes_source_but_not_phase_or_profile(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"trial"
            rehearse(root)
            packet=self.load(root/"review-packet.json")
            bundle=self.load(root/"bundle.json")
            cases={r["id"]:r for r in self.load(root/"cases.json")["cases"]}
            mapping={r["id"]:r["case_id"] for r in bundle["outputs"]}
            self.assertFalse(packet["phase_mapping_included"])
            self.assertFalse(packet["ground_truth_included"])
            for row in packet["outputs"]:
                self.assertEqual(set(row),{"output_id","brief","answers","specification"})
                self.assertEqual(row["answers"],cases[mapping[row["output_id"]]]["answers"])
                self.assertEqual(row["brief"],cases[mapping[row["output_id"]]]["brief"])
            self.assertTrue(packet["manual_blinding_check_required"])

    def test_private_review_cli_checks_sealed_case_content(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"trial"
            rehearse(root)
            output=root/"new-review.json"
            args=["prepare-review","--cases",root/"cases.json","--manifest",root/"manifest.json",
                  "--bundle",root/"bundle.json","--workspace",root,"--output",output]
            self.assertEqual(self.cli(*args).returncode,0)
            self.assertTrue(output.is_file())
            source=self.load(root/"cases.json")
            source["cases"][0]["answers"]["purpose"]="Changed after sealing"
            (root/"cases.json").write_text(json.dumps(source),encoding="utf-8")
            args[-1]=root/"bad-review.json"
            self.assertEqual(self.cli(*args).returncode,2)
            self.assertFalse(args[-1].exists())

    def test_rating_template_cli_leaves_editable_scores_and_reasons_blank(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"trial"
            rehearse(root)
            path=root/"reviewer-custom.json"
            result=self.cli("rating-template","--packet",root/"review-packet.json",
                            "--reviewer-id","REVIEWER_CUSTOM_1","--output",path)
            self.assertEqual(result.returncode,0,result.stderr)
            ratings=self.load(path)["ratings"]
            self.assertEqual(len(ratings),10)
            for row in ratings:
                self.assertEqual(set(row["scores"]),set(DIMENSIONS))
                self.assertTrue(all(v is None for v in row["scores"].values()))
                self.assertTrue(all(v=="" for v in row["evidence"].values()))

    def test_combine_refuses_unfinished_forms_and_same_reviewer(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"trial"
            rehearse(root)
            blank=self.load(root/"reviewer-1-blank.json")
            filled=self.load(root/"reviewer-2-synthetic.json")
            with self.assertRaises(ValueError):
                combine_reviews(blank,filled)
            with self.assertRaises(ValueError):
                combine_reviews(filled,filled)
            completed=combine_reviews(self.load(root/"reviewer-1-synthetic.json"),filled)
            self.assertEqual(len(completed["ratings"]),20)

    def test_no_overwrite_or_repository_output(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"trial"
            rehearse(root)
            path=root/"comparison.json"
            original=path.read_bytes()
            self.assertEqual(self.cli("rehearse","--directory",root).returncode,2)
            self.assertEqual(path.read_bytes(),original)
            args=["rating-template","--packet",root/"review-packet.json",
                  "--reviewer-id","REVIEWER_CUSTOM_1","--output"]
            self.assertEqual(self.cli(*args,ROOT/"private-review-forbidden.json").returncode,2)
            self.assertEqual(self.cli(*args,path).returncode,2)
            self.assertEqual(path.read_bytes(),original)


if __name__=="__main__":
    unittest.main()
