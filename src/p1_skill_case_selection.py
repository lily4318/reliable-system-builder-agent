"""Bounded model-selected skill and case lookup for the P1-2 public pilot.

No dynamic code execution, user data, private existing workspaces or deployment.
Model choices are proposals; the host permits only catalog role skills and
observed public cases. Missing artifact prerequisites are explicit, not PASS.
"""
import json
from . import team_workbench as wb, workbench_learning as learn

MODES=('default','curated')


def initialize(root,mode):
    if mode not in MODES:
        raise ValueError('invalid case mode')
    work=wb.initialize(root/'public-case-workbench','Public P1-2 synthetic pilot')
    learn.setup(work,include_training_cases=(mode=='curated'))
    return work


def menu(role):
    return [{'id':s['id'],'trigger':s['trigger'],'requires':s['requires']}
            for s in wb.catalog().values() if s['role']==role]


def plan(answer,role):
    value=json.loads(answer)
    if not isinstance(value,dict) or set(value)!={'skill','query','reason'}:
        raise ValueError('expected exact skill routing object')
    if value['skill'] not in {s['id'] for s in menu(role)}:
        raise ValueError('outside role skill allowlist')
    for key,bound in [('query',400),('reason',600)]:
        wb._text(value[key],key,bound)
    return value


def lookup(work,role,task,selection):
    selected=plan(json.dumps(selection),role)
    skill=wb.catalog()[selected['skill']]
    # Catalog is the trusted path owner; model cannot supply a filesystem path.
    path=(wb.ROOT/skill['path']).resolve()
    if not path.is_relative_to((wb.ROOT/'.agents'/'skills').resolve()) or not path.is_file():
        raise ValueError('catalog skill source unavailable')
    source=path.read_text(encoding='utf-8')
    if len(source)>20000:
        raise ValueError('skill exceeds pilot budget')
    context=learn.task_context(work,skill['id'],task,selected['query'],budget=6000,limit=4)
    # Private workbench is newly generated for this public run. Never feed a
    # real existing workspace, unresolved candidates or personal preferences.
    cases=[{k:m[k] for k in ('id','topic','content','evidence','matched_terms')}
           for m in context['memory'] if m['kind']=='case' and m['basis']=='observed']
    return {'selection':selected,'skill_text':source,'prerequisite_status':context['status'],
            'missing_prerequisites':context['missing'],'requires_full_read':context['requires_full_read'],
            'cases':cases,'authority_granted':False}


def assess(work,task,role,session,material,answer):
    value=json.loads(answer)
    if not isinstance(value,dict) or set(value)!={'artifact','case_decisions','limitations'}:
        raise ValueError('expected exact role result object')
    wb._text(value['artifact'],'candidate artifact',12000)
    wb._text(value['limitations'],'limitations',2000)
    rows=value['case_decisions']
    if not isinstance(rows,list) or len(rows)>4:
        raise ValueError('invalid case decision list')
    expected={m['id'] for m in material['cases']}
    seen=set()
    for r in rows:
        if not isinstance(r,dict) or set(r)!={'memory_id','decision','reason'} or type(r['memory_id']) is not int or r['memory_id'] not in expected or r['memory_id'] in seen or r['decision'] not in ('applied','not_applicable'):
            raise ValueError('unknown, duplicate or invalid case decision')
        wb._text(r['reason'],'case decision rationale',1000)
        seen.add(r['memory_id'])
    if seen!=expected:
        raise ValueError('explicit applicability decision required for each retrieved case')
    if material['prerequisite_status']!='READY_TO_REVIEW_INPUTS':
        # No artifact is silently marked accepted just because model returned it.
        disposition='CANDIDATE_MISSING_PREREQUISITES'
    else:
        disposition='CANDIDATE_REVIEW_REQUIRED'
    receipts=[]
    for r in rows:
        receipts.append(learn.cite(work,material['selection']['skill'],task,session,
            material['selection']['query'],r['memory_id'],r['decision'],
            'Model-declared applicability, not verified: '+r['reason'],budget=6000,limit=4))
    return {'artifact':value['artifact'],'limitations':value['limitations'],
            'case_decisions':rows,'citation_receipts':receipts,'status':disposition,
            'semantic_correctness_verified':False,'authority_granted':False}
