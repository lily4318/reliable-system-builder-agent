"""Read-only bridge from the current local website review export to design review.

The export is an unauthenticated local statement, not proof of user identity,
formal approval, source authority or construction permission. No model or write.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from src.website_discovery import build_spec, IDS

MAX_BYTES = 1024 * 1024
FLAGS = ('real_agent_executed','specification_approved','write_authorized',
         'deployment_authorized','live_intake_authorized')
EXPORT_KEYS = {'kind','answers','specification_draft','local_decisions',
               'local_document_review_confirmed', *FLAGS}


def _canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('ascii')


def _digest(value):
    return hashlib.sha256(_canonical(value)).hexdigest()


def _unique(pairs):
    result = {}
    for key,value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def read_export(raw):
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_BYTES:
        raise ValueError('review export size invalid')
    return json.loads(raw.decode('utf-8-sig'), object_pairs_hook=_unique)


def prepare(review, expected_sha256=None):
    """Normalize reviewed local text; optionally compare a previously pinned digest.

    Never turn caller-supplied flags or a hash match into a human approval.
    """
    if (not isinstance(review,dict) or set(review)!=EXPORT_KEYS
        or review['kind']!='local_reviewed_website_draft'
        or review['local_document_review_confirmed'] is not True
        or any(review[k] is not False for k in FLAGS)):
        raise ValueError('exact local review export required; no authorization flags')
    answers = review['answers']
    if not isinstance(answers,dict) or set(answers)!=set(IDS):
        raise ValueError('all 13 answer keys required')
    fresh = build_spec(answers)
    # Canonical JSON comparison distinguishes False from 0 and True from 1.
    if _canonical(review['specification_draft']) != _canonical(fresh):
        raise ValueError('stale or mismatched specification draft; review current source')
    proposals = {p['title']:p for p in fresh['inferred_requirements_unconfirmed']}
    items = {r['id']:r for r in fresh['inferred_requirement_review_items']}
    decisions = review['local_decisions']
    if not isinstance(decisions,list) or len(decisions)!=len(items):
        raise ValueError('exact decision coverage required')
    seen = {}
    for decision in decisions:
        if (not isinstance(decision,dict)
            or set(decision)!={'id','title','choice','text','local_text_confirmed'}
            or not isinstance(decision['id'],str) or decision['id'] not in items
            or decision['id'] in seen or decision['title']!=items[decision['id']]['question']
            or decision['choice'] not in ('accept','modify','reject')
            or decision['local_text_confirmed'] is not True
            or not isinstance(decision['text'],str)
            or not 0<len(decision['text'])<=3000 or not decision['text'].strip()):
            raise ValueError('invalid, unconfirmed or mismatched decision')
        seen[decision['id']]=decision
    explicit=[]
    for row in fresh['requirement_traceability']:
        # Keep verbatim answers, including negative statements, separately
        # from proposed requirements. Unanswered entries cannot be filled in.
        explicit.append({'id':row['requirement_id'],'source_question':row['source_question'],
            'text':row['explicit_user_answer'],'status':row['status']})
    candidates,excluded=[],[]
    for rid,item in items.items():
        decision=seen[rid]
        proposal=proposals[item['question']]
        record={'id':rid,'title':item['question'],
            'source_questions':proposal['basis'],'choice':decision['choice']}
        if decision['choice']=='reject':
            excluded.append({**record,'reason':decision['text'],
                             'original_proposal':proposal['proposal']})
        else:
            candidates.append({**record,'text':decision['text'],
                               'status':'LOCAL_TEXT_REVIEWED_NOT_APPROVED'})
    packet={'schema_version':1,'kind':'website_design_review_handoff',
        'status':'NEEDS_REQUIREMENTS_CLARIFICATION' if fresh['unanswered_questions']
                 else 'DESIGN_REVIEW_INPUT_ONLY',
        'review_export_sha256':_digest(review),
        'explicit_requirements':explicit,'reviewed_inferences':candidates,
        'excluded_inferences':excluded,'unanswered_questions':fresh['unanswered_questions'],
        'next_skill':'requirements-spec','subsequent_skill':'architecture-design',
        'next_steps':['Review conflicts, negative requirements and unresolved questions.',
                      'Confirm the complete integrated specification with the user separately.',
                      'Check target, current source, architecture, acceptance criteria and independent write authority.'],
        'local_review_statement_only':True,'semantic_correctness_verified':False,
        'human_identity_verified':False,'construction_permitted':False,
        **{k:False for k in FLAGS}}
    packet['handoff_sha256']=_digest(packet)
    if expected_sha256 is not None:
        if (not isinstance(expected_sha256,str)
            or not re.fullmatch(r'[0-9a-f]{64}',expected_sha256)
            or packet['handoff_sha256']!=expected_sha256):
            raise ValueError('handoff digest mismatch; re-review instead of inheriting confirmation')
    return packet


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review',type=Path,required=True)
    parser.add_argument('--expected-sha256')
    args=parser.parse_args()
    try:
        with args.review.open('rb') as stream:
            raw=stream.read(MAX_BYTES+1)
        packet=prepare(read_export(raw),args.expected_sha256)
        print(json.dumps(packet,ensure_ascii=True,indent=2))
        return 0
    except (OSError,ValueError,TypeError,RecursionError):
        print('WEBSITE_HANDOFF_BLOCKED: invalid or stale reviewed export',file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
