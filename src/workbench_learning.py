"""Task-focused learning extension for the existing private SQLite workbench.

No model calls. Retrieval is lexical; recorded use is operator-declared.
"""
import argparse
import json
import re
import sqlite3
from collections import Counter
from contextlib import closing
from pathlib import Path
from . import team_workbench as wb

CASES = (
    ('B001-CASE-001', 'SQLite 唯讀 缺庫 mode=ro query_only recovery reconcile',
     'Use mode=ro before connecting; query_only alone can create a missing database. Verify missing-file negative tests. Scope: local single SQLite database; not remote API or multi-node locking.',
     'docs/AGENT_CAPABILITY_TRAINING.md B001-CASE-001; d531eb09798e69003280cc981a20094969d4f381; test_readonly_reconcile_missing_database_does_not_create_file'),
    ('B002-CASE-001', 'SQLite 唯讀 缺庫 初始化 交易 庫存 保留 並行 回退 mode=rw mode=ro transaction inventory concurrency rollback idempotency ledger',
     'Separate exclusive creation, mode=ro reads and mode=rw updates. Check resource invariants and save the request result in the same transaction. Reconcile unknown outcomes without retry; COMMITTED is not necessarily RESERVED. Scope: local single SQLite database, synthetic faults; not distributed locking or crash recovery.',
     'docs/AGENT_CAPABILITY_TRAINING.md B002-CASE-001; 20c4e85bd6572831ac78a33b56d4344b376b8572; test_missing_database_never_created_by_read_or_reserve and test_rollback_after_inventory_before_ledger'),
)
# Explicit opt-in curated public engineering cases; default corpus unchanged.
TRAINING_CASES = (
    ('P21-CASE-003','SQLite idempotency ledger actor token payload negative decisions denied replay receipt',
     'Persist valid negative decisions as well as successful state transitions. Bind actor/token to exact payload; save state change and decision atomically. Known replay returns original decision; unknown outcome requires read-only reconciliation. Scope: trusted local single SQLite, not distributed transactions or external service receipts.',
     'docs/AGENT_CAPABILITY_TRAINING.md P21-CASE-003; 64a5f2ed8fe5dff429fe38d8edf191c6532b7c51; CI 43576453447'),
    ('P21-CASE-005','SQLite atomic transaction revision compare and swap artifact state event receipt interruption',
     'When related indexes are in one SQLite database, compare both expected versions and commit state, artifact and event in one transaction. Recover split historical states only after independently confirming the authoritative requirement; use a new revision. Scope: local coordinated route, not all legacy clients or external writes.',
     'docs/AGENT_CAPABILITY_TRAINING.md P21-CASE-005; f6ad1e35eaef281a09eec3ce102fffd2e1c35eec; CI 43606395473'),
    ('P21-CASE-006','browser native form origin policy Chromium DOM CLI migration rollback boundary',
     'HTTP success does not prove real browser form compatibility. Reproduce actual DOM flow, preserve strict Origin/CSRF guards and run negative tests. Validate migration, process restart and rollback separately; old snapshots cannot replace new committed writes. Scope: synthetic local Chromium/CLI, not manual UAT, external deployment or power-loss recovery.',
     'docs/AGENT_CAPABILITY_TRAINING.md P21-CASE-006; 0f4f536d4c3daf05304add614d24e2563b42b1ef; CI 43607088233'),
    ('P22-CASE-002','CSV file intake schema validation deterministic JSON bundle hash exclusive publication hard link reconcile interruption',
     'Validate all rows before publication; bind canonical output to exact input bytes with hashes in one bundle. Use exclusive publication rather than overwrite; after unknown outcome recompute and compare exact bytes read-only. Distinguish NOT_OBSERVED from CONFLICT; a leftover temporary file does not prove the final output failed. Scope: trusted stable local directory, compatible filesystem, synthetic data; not hostile paths, changing source, power-loss durability, distributed transactions or automatic cleanup.',
     'docs/AGENT_CAPABILITY_TRAINING.md P22-CASE-002; 088c8264d4e622ba3bb09e8212e220c91ed05caf; CI 43667714699/job 132670734319'),
    ('P22-CASE-003','SQLite snapshot revision policy report aggregate ZIP manifest logical hash readonly export reconciliation',
     'Bind a report to the source snapshot revision and the report policy revision separately. Read a consistent local SQLite snapshot in one read-only transaction; export only required aggregates, with a deterministic manifest binding logical snapshot and report hashes. Preserve old outputs, publish exclusively to a new path and reconcile exact bytes using the matching snapshot and policy. A stale or missing source blocks verification, not NOT_OBSERVED. Scope: cooperating local sources and trusted compatible filesystem; not live-source CAS at publication, historical verification without original snapshot, anonymity, hostile paths, Windows or power-loss durability.',
     'docs/AGENT_CAPABILITY_TRAINING.md P22-CASE-003; c1f5a605976925dd3ff281894f4e7ceb7be5fb2e; CI 43668235893/job 132672315245'),
    ('P22-CASE-004','bound task artifact generation root revision stale worker report ZIP acceptance recovery reconciliation prerequisite hash',
     'Pin source revision, logical snapshot hash and policy revision to a root artifact. On confirmed change atomically revise the root and invalidate dependent task/artifact generations; keep unrelated work and historical files. Name actual output by root ID; verify its exact bytes and require current task/session/prerequisite IDs and QA evidence before acceptance. If a stale worker published a file before invalidation, retain it as historical evidence, reconcile and explicitly recover before regenerating; never assume file publication and database acceptance are one transaction. Scope: controlled local bound workflow with trusted operators, not automated source watching, direct SQL or generic API bypass protection, external deployment, independent model QA or power-loss durability.',
     'docs/AGENT_CAPABILITY_TRAINING.md P22-CASE-004; 8639a359491b9eb923e64efa1db1f8c51b0d628b; CI 43668854174/job 132674236212'),
)
EVENTS = {'test_failure':'case', 'test_fix':'case', 'qa_rejection':'lesson',
          'requirement_change':'lesson', 'preference':'preference'}


def _ro(path):
    file = wb.private_root(path) / 'workbench.sqlite3'
    if file.is_symlink() or not file.is_file():
        raise ValueError('initialize the private workspace first')
    db = sqlite3.connect(file.as_uri()+'?mode=ro', uri=True, timeout=5)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA query_only=ON')
    return db


def setup(path, include_training_cases=False):
    """Explicit, repeatable additive migration; opt in to curated public cases."""
    if type(include_training_cases) is not bool:
        raise ValueError('explicit boolean required for training case import')
    selected = CASES + (TRAINING_CASES if include_training_cases else ())
    with closing(wb.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        db.execute('CREATE TABLE IF NOT EXISTS learning_cases (case_key TEXT PRIMARY KEY, memory_id INTEGER UNIQUE NOT NULL REFERENCES memory(id), tags TEXT NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS learning_events (event_id TEXT PRIMARY KEY, task TEXT NOT NULL, session TEXT NOT NULL, event_type TEXT NOT NULL, memory_id INTEGER NOT NULL REFERENCES memory(id))')
        db.execute('CREATE TABLE IF NOT EXISTS learning_uses (id INTEGER PRIMARY KEY, task TEXT NOT NULL, session TEXT NOT NULL, skill TEXT NOT NULL, query TEXT NOT NULL, memory_id INTEGER NOT NULL REFERENCES memory(id), decision TEXT NOT NULL, evidence TEXT NOT NULL)')
        for key, tags, content, evidence in selected:
            old = db.execute('SELECT * FROM learning_cases WHERE case_key=?', (key,)).fetchone()
            if old:
                continue
            if db.execute('SELECT 1 FROM memory WHERE kind=? AND topic=?', ('case',key)).fetchone():
                raise ValueError('existing case requires review: '+key)
            mid = db.execute('INSERT INTO memory(kind,topic,content,evidence,basis) VALUES (?,?,?,?,?)',
                             ('case',key,content,evidence,'observed')).lastrowid
            db.execute('INSERT INTO learning_cases VALUES (?,?,?)', (key,mid,tags))
    return {'setup':True, 'seeded_case_keys':[c[0] for c in selected]}


def _terms(value):
    terms = set()
    for word in re.findall(r'[a-z0-9]+|[\u3400-\u9fff]+', value.casefold()):
        if re.fullmatch(r'[\u3400-\u9fff]+', word):
            terms.update(word[i:i+2] for i in range(len(word)-1))
        elif len(word)>1 and word not in {'the','and','for','with','task','system','new'}:
            terms.add(word)
    return terms


def public_context(skill, task, query, budget=6000, limit=4, include_training_cases=False):
    """Read-only retrieval from the same public seed constants, without a workspace.

    Candidate engineering knowledge only: no personal memory, artifact acceptance,
    private case retirement state, or automatic authority. Callers must read the
    actual task prerequisites and assess applicability themselves.
    """
    if type(include_training_cases) is not bool:
        raise ValueError('explicit boolean required for training case retrieval')
    if type(budget) is not int or not 256 <= budget <= 20000 or type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError('invalid context bounds')
    task = wb._text(task, 'task ID', 120)
    target = _terms(wb._text(query, 'task query', 2000))
    s = wb.catalog()[skill]
    selected = CASES + (TRAINING_CASES if include_training_cases else ())
    ranked = []
    for case_key, tags, content, evidence in selected:
        matched = sorted(target & _terms(tags))
        if matched:
            ranked.append((len(matched), case_key, content, evidence, matched))
    remaining, matches = budget, []
    for score, case_key, content, evidence, matched in sorted(ranked, key=lambda r: (-r[0], r[1])):
        if len(matches) >= limit:
            break
        cost = len(content) + len(evidence)
        if cost > remaining:
            continue
        matches.append({'case_key':case_key, 'content':content, 'evidence':evidence,
                        'matched_terms':matched, 'score':score, 'basis':'observed_public'})
        remaining -= cost
    return {'task':task, 'skill':skill, 'mode':'PUBLIC_READ_ONLY',
            'status':'PUBLIC_CASE_REVIEW_ONLY',
            'required_artifact_types':list(s['requires']), 'memory':matches,
            'payload_chars':budget-remaining, 'curated':include_training_cases,
            'private_workspace_read':False, 'private_resolution_state_checked':False,
            'prerequisites_verified':False, 'authority_granted':False,
            'citation_persisted':False, 'model_invoked':False}


def _context(db, skill, task, query, budget, limit):
    if type(budget) is not int or not 256 <= budget <= 20000 or type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError('invalid context bounds')
    target = _terms(wb._text(query,'task query',2000))
    task = wb._text(task,'task ID',120)
    s = wb.catalog()[skill]
    latest = wb.current_artifacts(db)
    index = {k:{'id':v['id'],'current':v['current'],'source_ref':v['source_ref']} for k,v in latest.items()}
    missing = [k for k in s['requires'] if k not in latest or not latest[k]['current']]
    payload, memory, omitted = {}, [], []
    remaining = budget
    for k in s['requires']:
        if k in missing:
            continue
        content = latest[k]['content']
        if len(content)>remaining:
            omitted.append(k)
        else:
            payload[k] = content
            remaining -= len(content)
    rows = wb.active_memory(db)
    groups = Counter((r['kind'],r['topic']) for r in rows)
    tags = {r['memory_id']:r['tags'] for r in db.execute('SELECT * FROM learning_cases')}
    # TP-010: explicit workspace preferences are mandatory review inputs,
    # not optional lexical hits or authority.
    work_preferences, preference_review, omitted_preferences = [], [], []
    preference_groups = {}
    for row in rows:
        if row['kind'] == 'preference':
            preference_groups.setdefault(row['topic'], []).append(row)
    for topic, entries in sorted(preference_groups.items()):
        confirmed = [row for row in entries if row['basis'] == 'user-stated']
        if not confirmed:
            continue
        if len(entries) != 1:
            preference_review.append({'topic':topic,'ids':[row['id'] for row in entries]})
            continue
        row = confirmed[0]
        cost = len(row['content']) + len(row['evidence'])
        if cost > remaining:
            omitted_preferences.append(row['id'])
            continue
        work_preferences.append(row)
        remaining -= cost
    selected_preference_ids = {r['id'] for r in work_preferences}
    ranked, review = [], []
    for r in rows:
        if r['id'] in selected_preference_ids or r['id'] in omitted_preferences:
            continue
        matched = sorted(target & _terms(tags.get(r['id'],r['topic']+' '+r['content'])))
        if not matched:
            continue
        if r['basis']=='candidate' or groups[(r['kind'],r['topic'])]>1:
            review.append({'id':r['id'],'topic':r['topic'],'basis':r['basis']})
            continue
        ranked.append((len(matched),r,matched))
    for score,r,matched in sorted(ranked,key=lambda x:(-x[0],x[1]['id'])):
        if omitted_preferences or len(memory)>=limit:
            break
        cost = len(r['content'])+len(r['evidence'])
        if cost>remaining:
            continue
        memory.append({**r,'matched_terms':matched,'score':score})
        remaining -= cost
    return {'project':db.execute('SELECT project FROM metadata').fetchone()[0], 'task':task,'skill':skill,
            'status':'NEEDS_PREREQUISITES' if missing else 'NEEDS_FULL_READ' if (omitted or omitted_preferences) else 'READY_TO_REVIEW_INPUTS',
            'missing':missing,'requires_full_read':omitted,'artifact_index':index,'artifact_content':payload,
            'memory':memory,'work_preferences':work_preferences,'preference_review':preference_review,
            'omitted_work_preference_ids':omitted_preferences,'review_candidates':review[:limit], 'matching_review_count':len(review),
            'payload_chars':budget-remaining,'payload_limit':budget,
            'authorization_granted':False,'model_or_subagent_invoked':False,
            'instruction':'work_preferences are explicit workspace inputs, not authority. Review conflicts, never apply candidates; read omitted preferences and prerequisites before relying on them. Other memory is lexical suggestions; verify case limits and formal sources.'}


def task_context(path, skill, task, query, budget=8000, limit=5):
    with closing(_ro(path)) as db:
        db.execute('BEGIN')
        return _context(db,skill,task,query,budget,limit)


def feedback(path, task, session, event_id, event_type, topic, content, evidence):
    if event_type not in EVENTS:
        raise ValueError('invalid feedback event')
    task,session,event_id,topic = [wb._text(v,'event identifier',120) for v in (task,session,event_id,topic)]
    content = wb._text(content,'feedback',8000)
    evidence = wb._text(evidence,'evidence',2000)
    kind = EVENTS[event_type]
    with closing(wb.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        old = db.execute('SELECT e.*,m.topic,m.content,m.evidence FROM learning_events e JOIN memory m ON m.id=e.memory_id WHERE event_id=?',(event_id,)).fetchone()
        if old:
            if tuple(old[k] for k in ('task','session','event_type','topic','content','evidence')) != (task,session,event_type,topic,content,evidence):
                raise ValueError('feedback event ID conflict')
            return {'memory_id':old['memory_id'],'duplicate':True,'basis':'candidate'}
        existing = db.execute('SELECT id FROM memory WHERE kind=? AND topic=? AND content=? AND evidence=? AND basis=? AND id NOT IN (SELECT retired FROM resolutions)',(kind,topic,content,evidence,'candidate')).fetchone()
        mid = existing[0] if existing else db.execute('INSERT INTO memory(kind,topic,content,evidence,basis) VALUES (?,?,?,?,?)',(kind,topic,content,evidence,'candidate')).lastrowid
        db.execute('INSERT INTO learning_events VALUES (?,?,?,?,?)',(event_id,task,session,event_type,mid))
        return {'memory_id':mid,'duplicate':False,'basis':'candidate','review_required':True}


def cite(path, skill, task, session, query, memory_id, decision, evidence, budget=8000, limit=5):
    if decision not in ('applied','not_applicable') or type(memory_id) is not int:
        raise ValueError('invalid citation')
    task = wb._text(task,'task ID',120)
    session = wb._text(session,'session ID',120)
    evidence = wb._text(evidence,'citation evidence',2000)
    query = wb._text(query,'query',2000)
    with closing(wb.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        ctx = _context(db,skill,task,query,budget,limit)
        if memory_id not in [m['id'] for m in ctx['memory'] if m['kind']=='case']:
            raise ValueError('case not in current relevant selection')
        ident = db.execute('INSERT INTO learning_uses(task,session,skill,query,memory_id,decision,evidence) VALUES (?,?,?,?,?,?,?)',(task,session,skill,query,memory_id,decision,evidence)).lastrowid
        return {'citation_id':ident,'operator_declared_not_independently_verified':True}


def history(path, task):
    task = wb._text(task,'task ID',120)
    with closing(_ro(path)) as db:
        db.execute('BEGIN')
        return {'events':[dict(r) for r in db.execute('SELECT * FROM learning_events WHERE task=? ORDER BY rowid',(task,))],
                'uses':[dict(r) for r in db.execute('SELECT u.*,m.topic FROM learning_uses u JOIN memory m ON m.id=u.memory_id WHERE u.task=? ORDER BY u.id',(task,))]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('setup','context','feedback','cite','history','public-context'))
    p.add_argument('--workspace',type=Path,help='required except public-context')
    p.add_argument('--input',type=Path,help='JSON object with function arguments; required except setup')
    a = p.parse_args()
    try:
        args = json.loads(a.input.read_text(encoding='utf-8-sig')) if a.input else {}
        if not isinstance(args,dict):
            raise ValueError('input must be a JSON object')
        if a.action == 'public-context':
            if a.workspace is not None:
                raise ValueError('public-context never accepts a private workspace')
            print(json.dumps(public_context(**args),ensure_ascii=False,indent=2))
            return 0
        if a.workspace is None:
            raise ValueError('private workspace required for this action')
        fn = {'setup':setup,'context':task_context,'feedback':feedback,'cite':cite,'history':history}[a.action]
        print(json.dumps(fn(a.workspace,**args),ensure_ascii=False,indent=2))
        return 0
    except (ValueError,TypeError,KeyError,OSError,sqlite3.Error) as e:
        p.exit(2,'WORKBENCH_LEARNING_BLOCKED: '+str(e)+'\n')


if __name__ == '__main__':
    raise SystemExit(main())
