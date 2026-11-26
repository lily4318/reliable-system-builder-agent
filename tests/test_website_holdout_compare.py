"""Offline synthetic tests only; these ratings are NOT real human reviews."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from src.website_discovery import KEYS, build_spec
from src.website_holdout_compare import (
    DIMENSIONS, ROOT, canonical, digest, seal_private_cases,
    validate_manifest, compare, blind_review_packet, protocol_contract,
)


class WebsitePrivateHoldoutContractTest(unittest.TestCase):
    def fixture(self, dirpath, num_cases=5):
        root=Path(dirpath)
        case_file=root/"private_cases.json"
        cases=[
            {"id":f"H{i:03d}",
             "brief":f"獨立審查者提供的私人合成建站情境第 {i} 題，僅作協定合成測試。",
             "answers":{key:f"第 {i} 題的合成回答；尚未經真人核准。"
                        for key in KEYS}}
            for i in range(1,num_cases+1)]
        case_file.write_bytes(canonical({
            "schema_version":1,"kind":"independent_private_website_cases",
            "cases":cases}))
        manifest=seal_private_cases(case_file)
        workspace=root/"workspace"
        (workspace/"specifications").mkdir(parents=True)
        profiles={
            "before":{"agent_sha":"1"*40,"prompt_sha":"a"*64,
                      "model_id":"synthetic_engine_no_model",
                      "runner_id":"offline_protocol_only",
                      "resource_budget":"fixed_synthetic_budget"},
            "after":{"agent_sha":"2"*40,"prompt_sha":"b"*64,
                     "model_id":"synthetic_engine_no_model",
                     "runner_id":"offline_protocol_only",
                     "resource_budget":"fixed_synthetic_budget"},
        }
        rows=[]
        reviews=[]
        for i,case in enumerate(cases,1):
            for phase in ("before","after"):
                uid=f"OPAQUEID{i:03d}{'X' if phase=='before' else 'Y'}98765"
                spec=build_spec(case["answers"])
                path=f"specifications/{uid}.json"
                data=canonical(spec)
                (workspace/path).write_bytes(data)
                rows.append({
                    "id":uid,"case_id":case["id"],"phase":phase,
                    "case_sha256":manifest["commitments"][i-1]["case_sha256"],
                    "path":path,"sha256":digest(data),
                })
                for rater in ("REVIEWERONE000001","REVIEWERTWO000002"):
                    reviews.append({
                        "output_id":uid,"reviewer_id":rater,
                        "scores":{dimension:2 if phase=="before" else 3
                                  for dimension in DIMENSIONS},
                        "evidence":{dimension:
                            "獨立人工標註的合成評語，僅用於測試分數計算與契約驗證。"
                            for dimension in DIMENSIONS},
                    })
        bundle={"schema_version":1,
                "kind":"externally_supplied_website_outputs_unverified",
                "official_model_execution_verified":False,
                "profiles":profiles,"outputs":rows}
        annotations={"schema_version":1,
                     "kind":"independent_blinded_human_website_reviews",
                     "model_or_agent_run_verified":False,
                     "ratings":reviews,"adjudications":[]}
        return manifest,bundle,annotations,workspace,case_file

    def test_private_commitments_do_not_disclose_prompts(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,*_=self.fixture(d)
            self.assertEqual(manifest["case_count"],5)
            self.assertEqual(len(validate_manifest(manifest)),5)
            text=json.dumps(manifest,ensure_ascii=False)
            self.assertNotIn("brief",text)
            self.assertFalse(manifest["case_text_or_answers_embedded"])
            self.assertTrue(all(set(x)=={"id","case_sha256"} for x in manifest["commitments"]))
            self.assertNotIn('"brief":',text)
            self.assertNotIn('"answers":',text)
            self.assertFalse(manifest["case_independence_independently_verified"])
            self.assertFalse(manifest["actual_agent_runner_executed"])

    def test_complete_synthetic_paired_delta_cannot_claim_actual_skill_gain(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,bundle,ratings,workspace,_=self.fixture(d)
            result=compare(manifest,bundle,ratings,workspace)
            self.assertEqual(result["case_count"],5)
            self.assertEqual(result["rating_count"],20)
            self.assertEqual(result["paired_mean_delta_on_0_to_4_scale"],1.0)
            self.assertTrue(all(x["paired_delta"]==1.0
                                for x in result["case_summaries"]))
            self.assertTrue(result["output_integrity_sha256_checked"])
            self.assertTrue(result["two_ratings_per_artifact"])
            for key in ("actual_model_or_agent_execution_verified",
                        "sealed_holdout_independence_verified",
                        "model_capability_improvement_verified",
                        "human_semantic_truth_independently_verified_by_software",
                        "releases_or_live_websites_authorized"):
                self.assertFalse(result[key])

    def test_blinded_review_packet_hides_phase_model_and_version(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,bundle,ratings,workspace,_=self.fixture(d)
            packet=blind_review_packet(manifest,bundle,workspace)
            self.assertEqual(packet["kind"],"private_blinded_website_review_packet")
            self.assertEqual(len(packet["outputs"]),10)
            self.assertFalse(packet["before_after_phase_included"])
            self.assertFalse(packet["model_or_runner_metadata_included"])
            self.assertFalse(packet["human_blinding_independently_verified"])
            self.assertTrue(all(set(x)=={"output_id","specification"}
                                for x in packet["outputs"]))
            text=json.dumps(packet,ensure_ascii=False)
            for prohibited in ("model_id","runner_id","phase","agent_sha","prompt_sha"):
                self.assertNotIn('"'+prohibited+'"',text)

    def test_public_protocol_includes_no_fake_runner_or_holdout_claims(self):
        p=protocol_contract()
        self.assertEqual(p["dimensions"],list(DIMENSIONS))
        self.assertEqual(p["required_independent_raters_per_artifact"],2)
        self.assertEqual(p["minimum_private_unseen_case_count"],5)
        self.assertFalse(p["real_model_or_agent_run_verified"])
        self.assertFalse(p["case_independence_independently_verified"])
        self.assertFalse(p["synthetic_tests_measure_real_skill"])
        self.assertFalse(p["automatic_release_allowed"])

    def test_sealing_requires_five_cases(self):
        with tempfile.TemporaryDirectory() as d:
            _,_,_,_,source=self.fixture(d)
            data=json.loads(source.read_text(encoding="utf-8"))
            data["cases"]=data["cases"][:4]
            source.write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"five"):
                seal_private_cases(source)

    def test_private_holdout_cannot_be_placed_in_repo(self):
        with self.assertRaisesRegex(ValueError,"cannot be stored"):
            seal_private_cases(ROOT/"evaluations/interaction/website-scenarios.json")

    def test_duplicate_case_id_blocks_sealing(self):
        with tempfile.TemporaryDirectory() as d:
            *_,source=self.fixture(d)
            data=json.loads(source.read_text())
            data["cases"][1]["id"]=data["cases"][0]["id"]
            source.write_text(json.dumps(data),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"duplicated"):
                seal_private_cases(source)

    def test_manifest_misrepresents_private_status_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,bundle,ratings,workspace,_=self.fixture(d)
            manifest["case_independence_independently_verified"]=True
            with self.assertRaisesRegex(ValueError,"claims"):
                compare(manifest,bundle,ratings,workspace)

    def test_missing_one_side_blocks_paired_comparison(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,bundle,ratings,workspace,_=self.fixture(d)
            bundle["outputs"].pop()
            with self.assertRaisesRegex(ValueError,"paired"):
                compare(manifest,bundle,ratings,workspace)

    def test_duplicate_blind_id_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,bundle,ratings,workspace,_=self.fixture(d)
            bundle["outputs"][1]["id"]=bundle["outputs"][0]["id"]
            with self.assertRaisesRegex(ValueError,"unblinded"):
                compare(manifest,bundle,ratings,workspace)

    def test_version_must_change(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,bundle,ratings,workspace,_=self.fixture(d)
            bundle["profiles"]["after"]["agent_sha"]=bundle["profiles"]["before"]["agent_sha"]
            with self.assertRaisesRegex(ValueError,"must differ"):
                compare(manifest,bundle,ratings,workspace)

    def test_confounded_model_runner_or_budget_rejected(self):
        for field in ("model_id","runner_id","resource_budget"):
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory() as d:
                    manifest,bundle,ratings,workspace,_=self.fixture(d)
                    bundle["profiles"]["after"][field]="different_budget_or_model"
                    with self.assertRaisesRegex(ValueError,"must match"):
                        compare(manifest,bundle,ratings,workspace)

    def test_tampered_file_digest_detected(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,bundle,ratings,workspace,_=self.fixture(d)
            f=workspace / bundle["outputs"][0]["path"]
            f.write_text("{}")
            with self.assertRaisesRegex(ValueError,"digest mismatch"):
                compare(manifest,bundle,ratings,workspace)

    def test_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,bundle,ratings,workspace,_=self.fixture(d)
            bundle["outputs"][0]["path"]="../../outside.json"
            with self.assertRaisesRegex(ValueError,"outside private"):
                compare(manifest,bundle,ratings,workspace)

    def test_symlinked_spec_source_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,bundle,ratings,workspace,_=self.fixture(d)
            f=workspace/bundle["outputs"][0]["path"]
            other=workspace/"other.json"
            other.write_bytes(f.read_bytes())
            f.unlink()
            f.symlink_to(other)
            with self.assertRaisesRegex(ValueError,"unsafe specification"):
                compare(manifest,bundle,ratings,workspace)

    def test_fake_provider_model_verification_disallowed(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,bundle,ratings,workspace,_=self.fixture(d)
            bundle["official_model_execution_verified"]=True
            with self.assertRaisesRegex(ValueError,"self-certify"):
                compare(manifest,bundle,ratings,workspace)

    def test_missing_one_reviewer_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,bundle,ratings,workspace,_=self.fixture(d)
            ratings["ratings"].pop()
            with self.assertRaisesRegex(ValueError,"two independent"):
                compare(manifest,bundle,ratings,workspace)

    def test_duplicate_reviewer_id_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,bundle,ratings,workspace,_=self.fixture(d)
            ratings["ratings"][1]["reviewer_id"]=ratings["ratings"][0]["reviewer_id"]
            with self.assertRaisesRegex(ValueError,"duplicate"):
                compare(manifest,bundle,ratings,workspace)

    def test_missing_dimension_reason_and_noninteger_score_rejected(self):
        for mutation in ("missing_dimension","blank_evidence","float","out_of_range"):
            with self.subTest(mutation=mutation):
                with tempfile.TemporaryDirectory() as d:
                    manifest,bundle,ratings,workspace,_=self.fixture(d)
                    row=ratings["ratings"][0]
                    if mutation=="missing_dimension":
                        row["scores"].pop(DIMENSIONS[0])
                    elif mutation=="blank_evidence":
                        row["evidence"][DIMENSIONS[0]]="?"
                    elif mutation=="float":
                        row["scores"][DIMENSIONS[0]]=3.0
                    else:
                        row["scores"][DIMENSIONS[0]]=6
                    with self.assertRaises(ValueError):
                        compare(manifest,bundle,ratings,workspace)

    def test_disagreement_needs_independent_third_reviewer(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,bundle,ratings,workspace,_=self.fixture(d)
            row=ratings["ratings"][1]
            row["scores"][DIMENSIONS[0]]=0
            with self.assertRaisesRegex(ValueError,"adjudication"):
                compare(manifest,bundle,ratings,workspace)
            ratings["adjudications"].append({
                "output_id":row["output_id"],"dimension":DIMENSIONS[0],
                "adjudicator_id":"THIRDPERSON000123","score":1,
                "reason":"第三位人工仲裁者根據相同評分錨點獨立核對，此處僅合成測試。",
            })
            result=compare(manifest,bundle,ratings,workspace)
            self.assertEqual(result["adjudicated_disagreements"],1)

    def test_adjudicator_cannot_be_original_reviewer(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,bundle,ratings,workspace,_=self.fixture(d)
            ratings["ratings"][1]["scores"][DIMENSIONS[0]]=0
            ratings["adjudications"].append({
                "output_id":ratings["ratings"][0]["output_id"],
                "dimension":DIMENSIONS[0],
                "adjudicator_id":ratings["ratings"][0]["reviewer_id"],
                "score":1,"reason":"不允許同一人擔任自己的仲裁者，不能跳過第三人。"
            })
            with self.assertRaisesRegex(ValueError,"adjudication"):
                compare(manifest,bundle,ratings,workspace)

    def test_unblinded_output_id_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,bundle,ratings,workspace,_=self.fixture(d)
            bundle["outputs"][0]["id"]="before_candidate_output_01"
            with self.assertRaisesRegex(ValueError,"unblinded"):
                compare(manifest,bundle,ratings,workspace)

    def test_unsafe_auto_send_is_reported_as_structure_failure(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,bundle,ratings,workspace,_=self.fixture(d)
            row=bundle["outputs"][0]
            p=workspace/row["path"]
            data=json.loads(p.read_text())
            data["inferred_requirements_unconfirmed"]=[
                {"title":"狀態與通知","origin":"agent_inference","user_confirmed":False}]
            data["inferred_requirement_review_items"]=[{
                "id":"unsafe_choice","editable_text_on_select":False,
                "auto_submit_on_select":True,"approval_state":"APPROVED",
                "choices":[]}]
            content=canonical(data)
            p.write_bytes(content)
            row["sha256"]=digest(content)
            report=compare(manifest,bundle,ratings,workspace)
            self.assertFalse(report["case_summaries"][0]["before_structure_pass"])
            self.assertFalse(report["model_capability_improvement_verified"])

    def test_empty_fake_human_evidence_cannot_be_published_as_comparison(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,bundle,ratings,workspace,_=self.fixture(d)
            ratings["ratings"][0]["evidence"][DIMENSIONS[1]]="OK"
            with self.assertRaisesRegex(ValueError,"supporting reason"):
                compare(manifest,bundle,ratings,workspace)

    def test_unknown_holdout_case_digest_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            manifest,bundle,ratings,workspace,_=self.fixture(d)
            bundle["outputs"][0]["case_sha256"]="0"*64
            with self.assertRaisesRegex(ValueError,"unpaired"):
                compare(manifest,bundle,ratings,workspace)


if __name__=="__main__":
    unittest.main()
