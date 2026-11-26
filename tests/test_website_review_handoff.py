"""Handoff contract, actual local export shape; no approval or external action."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src import website_review_handoff as handoff
from src.website_discovery import build_spec, IDS
from src.website_scenario_eval import load_cases


def fixture(answers):
    answers={k:answers.get(k) or '' for k in IDS}
    spec=build_spec(answers)
    choices=('accept','modify','reject')
    return {'kind':'local_reviewed_website_draft','answers':answers,
        'specification_draft':spec,'local_document_review_confirmed':True,
        'local_decisions':[{'id':item['id'],'title':item['question'],
            'choice':choices[i%3],'text':'Reviewed text '+str(i),
            'local_text_confirmed':True}
            for i,item in enumerate(spec['inferred_requirement_review_items'])],
        **{k:False for k in handoff.FLAGS}}


class ReviewHandoffTests(unittest.TestCase):
    def setUp(self):
        self.review=fixture({'purpose':'synthetic site','forms':'需要報名表單',
            'slots':'需要預約','notice':'需要通知','privacy':'待確認',
            'identity':'不需要登入'})

    def test_all_six_exports_apply_edits_and_exclude_rejected(self):
        for case in load_cases():
            with self.subTest(case=case['id']):
                export=fixture(case['answers'])
                packet=handoff.prepare(export)
                decisions={r['id']:r for r in export['local_decisions']}
                self.assertEqual(len(packet['explicit_requirements']),13)
                self.assertEqual(packet['unanswered_questions'],
                                 export['specification_draft']['unanswered_questions'])
                for row in packet['reviewed_inferences']:
                    self.assertEqual(row['text'],decisions[row['id']]['text'])
                    self.assertNotEqual(row['choice'],'reject')
                    self.assertNotIn('original_proposal',row)
                for row in packet['excluded_inferences']:
                    self.assertEqual(row['choice'],'reject')
                    self.assertEqual(row['reason'],decisions[row['id']]['text'])
                self.assertEqual({r['id'] for r in packet['reviewed_inferences']}|
                     {r['id'] for r in packet['excluded_inferences']},set(decisions))
                self.assertEqual(handoff.prepare(export,packet['handoff_sha256']),packet)
                self.assertTrue(all(packet[k] is False for k in handoff.FLAGS))
                self.assertFalse(packet['construction_permitted'])
        packet=handoff.prepare(self.review)
        self.assertEqual(packet['explicit_requirements'][4]['text'],'不需要登入')
        self.assertEqual(packet['status'],'NEEDS_REQUIREMENTS_CLARIFICATION')
        self.assertEqual(len(packet['excluded_inferences']),1)

    def test_stale_missing_duplicate_mismatched_and_malformed_block(self):
        mutations=[
            lambda r:r['answers'].update(purpose='new answer'),
            lambda r:r['specification_draft']['functional_spec'].update(data_forms='injected'),
            lambda r:r['specification_draft'].update(write_authorized=0),
            lambda r:r['local_decisions'].pop(),
            lambda r:r['local_decisions'].__setitem__(1,r['local_decisions'][0]),
            lambda r:r['local_decisions'][0].update(title='wrong'),
            lambda r:r['local_decisions'][0].update(id=[]),
            lambda r:r['local_decisions'][0].update(text=' '),
            lambda r:r['local_decisions'][0].update(local_text_confirmed=1),
            lambda r:r.update(local_document_review_confirmed=1),
            lambda r:r.update(deployment_authorized=True),
            lambda r:r.update(specification_approved=True),
            lambda r:r['answers'].pop('release'),
        ]
        for i,mutate in enumerate(mutations):
            with self.subTest(i=i):
                bad=copy.deepcopy(self.review)
                mutate(bad)
                with self.assertRaises(ValueError):
                    handoff.prepare(bad)

    def test_digest_changes_for_edit_choice_and_source(self):
        old=handoff.prepare(self.review)['handoff_sha256']
        for changes in ({'text':'new review'}, {'choice':'reject'}):
            changed=copy.deepcopy(self.review)
            changed['local_decisions'][0].update(changes)
            with self.assertRaisesRegex(ValueError,'digest mismatch'):
                handoff.prepare(changed,old)
        new=fixture({**self.review['answers'],'purpose':'new purpose'})
        with self.assertRaisesRegex(ValueError,'digest mismatch'):
            handoff.prepare(new,old)

    def test_empty_inferences_and_fully_answered_still_not_approval(self):
        packet=handoff.prepare(fixture({k:'不適用' for k in IDS}))
        self.assertEqual(packet['status'],'DESIGN_REVIEW_INPUT_ONLY')
        self.assertFalse(packet['reviewed_inferences'])
        self.assertFalse(packet['specification_approved'])
        self.assertFalse(packet['construction_permitted'])

    def test_cli_readonly_duplicate_json_and_stale_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'review.json'
            p.write_text(json.dumps(self.review),encoding='utf-8')
            before=p.read_bytes()
            cmd=[sys.executable,'-m','src.website_review_handoff','--review',str(p)]
            result=subprocess.run(cmd,capture_output=True,check=True,timeout=10)
            self.assertEqual(json.loads(result.stdout),handoff.prepare(self.review))
            self.assertEqual(p.read_bytes(),before)
            blocked=subprocess.run(cmd+['--expected-sha256','0'*64],capture_output=True,timeout=10)
            self.assertEqual(blocked.returncode,2)
            self.assertFalse(blocked.stdout)
            self.assertEqual(list(Path(tmp).iterdir()),[p])
            with self.assertRaises(ValueError):
                handoff.read_export(b'{"kind":"a","kind":"b"}')
            with self.assertRaises(ValueError):
                handoff.read_export(b'x'*(handoff.MAX_BYTES+1))
