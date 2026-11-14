"""Additive task pool in the existing authorized workbench database."""
import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from . import team_workbench as wb
from .workbench_learning import _ro


def _id(value):
    return wb._text(value, 'identifier', 120)


def _ids(values):
    if not isinstance(values, list):
        raise ValueError('expected ID list')
    out = [_id(v) for v in values]
    if len(out) != len(set(out)):
        raise ValueError('duplicate ID')
    return out


def setup(path):
    with closing(wb.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        db.execute('CREATE TABLE IF NOT EXISTS task_decisions (id TEXT PRIMARY KEY, question TEXT NOT NULL, answer TEXT, source TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS task_pool (id TEXT PRIMARY KEY, title TEXT NOT NULL, priority INTEGER NOT NULL, deps TEXT NOT NULL, gates TEXT NOT NULL, checks TEXT NOT NULL, state TEXT NOT NULL, session TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS task_events (seq INTEGER PRIMARY KEY, task TEXT NOT NULL REFERENCES task_pool(id), session TEXT NOT NULL, kind TEXT NOT NULL, evidence TEXT NOT NULL, results TEXT NOT NULL)')
        if 'revision' not in {r[1] for r in db.execute('PRAGMA table_info(task_pool)')}:
            db.execute('ALTER TABLE task_pool ADD COLUMN revision INTEGER NOT NULL DEFAULT 1 CHECK(revision>=1)')
            for row in db.execute("SELECT id,session FROM task_pool WHERE state='RUNNING'").fetchall():
                db.execute("UPDATE task_pool SET state='RECOVERY_REQUIRED',revision=2 WHERE id=?",(row['id'],))
                _event(db,row['id'],'migration','MIGRATION_FENCE','Legacy running task requires explicit recovery',{'old_session':row['session'],'revision':2})
    return {'setup':True}


def question(path, decision, prompt):
    decision, prompt = _id(decision), wb._text(prompt,'decision question',2000)
    with closing(wb.connect(path)) as db, db:
        db.execute('INSERT INTO task_decisions(id,question) VALUES (?,?)',(decision,prompt))
    return {'decision':decision,'state':'OPEN'}


def resolve_decision(path, decision, answer, source, confirmed=False):
    if confirmed is not True:
        raise ValueError('explicit confirmation required')
    decision, answer, source = _id(decision), wb._text(answer,'answer',2000), wb._text(source,'decision source',2000)
    with closing(wb.connect(path)) as db, db:
        cur = db.execute('UPDATE task_decisions SET answer=?,source=? WHERE id=? AND answer IS NULL',(answer,source,decision))
        if cur.rowcount != 1:
            raise ValueError('unknown or resolved decision; preserve history')
    return {'decision':decision,'operator_declared_confirmation':True,'authorization_granted':False}


def add(path, task, title, priority, deps, gates, checks):
    task, title = _id(task), wb._text(title,'title',500)
    deps, gates, checks = _ids(deps), _ids(gates), _ids(checks)
    if type(priority) is not int or not 0 <= priority <= 99 or not checks:
        raise ValueError('priority or acceptance checks invalid')
    with closing(wb.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        if task in deps or any(not db.execute('SELECT 1 FROM task_pool WHERE id=?',(x,)).fetchone() for x in deps):
            raise ValueError('dependency must already exist; DAG only')
        if any(not db.execute('SELECT 1 FROM task_decisions WHERE id=?',(x,)).fetchone() for x in gates):
            raise ValueError('unknown decision gate')
        db.execute('INSERT INTO task_pool(id,title,priority,deps,gates,checks,state,session) VALUES (?,?,?,?,?,?,?,NULL)',(task,title,priority,json.dumps(deps),json.dumps(gates),json.dumps(checks),'PENDING'))
    return {'task':task,'state':'PENDING'}


def _pool(db):
    rows = {r['id']:dict(r) for r in db.execute('SELECT * FROM task_pool ORDER BY priority,id')}
    if 'revision' not in {r[1] for r in db.execute('PRAGMA table_info(task_pool)')}:
        raise ValueError('explicit task pool setup/migration required')
    open_gates = {r[0] for r in db.execute('SELECT id FROM task_decisions WHERE answer IS NULL')}
    for r in rows.values():
        for k in ('deps','gates','checks'):
            r[k] = json.loads(r[k])
        if any(x not in rows for x in r['deps']):
            raise ValueError('unknown dependency; review required')
    # Do not start revised upstream work while an invalidated downstream worker
    # has not yet been reconciled. Independent branches remain available.
    recovery = {k:[] for k in rows}
    for key,r in rows.items():
        if r['state']!='RECOVERY_REQUIRED':
            continue
        seen,stack = set(),list(r['deps'])
        while stack:
            dep = stack.pop()
            if dep in seen:
                continue
            seen.add(dep)
            recovery[dep].append(key)
            stack.extend(rows[dep]['deps'])
    for key,r in rows.items():
        r['blocked_by'] = [x for x in r['deps'] if rows[x]['state']!='DONE']+[x for x in r['gates'] if x in open_gates]
        r['recovery_blockers'] = sorted(recovery[key])
        r['ready'] = r['state']=='PENDING' and not r['blocked_by'] and not r['recovery_blockers']
    return rows


def _event(db, task, session, kind, evidence, results):
    db.execute('INSERT INTO task_events(task,session,kind,evidence,results) VALUES (?,?,?,?,?)',
               (task,session,kind,evidence,json.dumps(results,sort_keys=True)))


def _revision(row, expected):
    if expected is None and row['revision']==1:
        return  # legacy API only for never-revised tasks
    if type(expected) is not int or expected!=row['revision']:
        raise ValueError('stale or missing expected revision; review first')


def _new_session(db, task, session):
    if db.execute("SELECT 1 FROM task_events WHERE task=? AND session=? AND kind IN ('START','RESUME')",(task,session)).fetchone():
        raise ValueError('session already used for this task; choose a new execution ID')


def _validate_graph(rows):
    # Iterative topological elimination; no recursive depth limit.
    pending = {k:set(r['deps']) for k,r in rows.items()}
    while pending:
        roots = {k for k,v in pending.items() if not v}
        if not roots:
            raise ValueError('dependency cycle or unknown dependency')
        pending = {k:v-roots for k,v in pending.items() if k not in roots}


def revise(path, task, expected_revision, session, evidence, confirmed=False,
           title=None, deps=None, gates=None, checks=None):
    """Reopen a task and its transitive dependants; fence in-flight work."""
    if confirmed is not True or type(expected_revision) is not int or expected_revision<1:
        raise ValueError('explicit confirmed revision and current revision required')
    task,session = _id(task),_id(session)
    evidence = wb._text(evidence,'confirmed change source/evidence',4000)
    with closing(wb.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        rows = _pool(db)
        if task not in rows:
            raise ValueError('unknown task')
        root = rows[task]
        _revision(root,expected_revision)
        old = {k:root[k] for k in ('title','deps','gates','checks')}
        new = dict(old)
        for k,v in (('deps',deps),('gates',gates),('checks',checks)):
            if v is not None:
                new[k] = _ids(v)
        if title is not None:
            new['title'] = wb._text(title,'title',500)
        if not new['checks'] or any(k not in rows for k in new['deps']):
            raise ValueError('unknown dependency or empty acceptance checks')
        if any(not db.execute('SELECT 1 FROM task_decisions WHERE id=?',(g,)).fetchone() for g in new['gates']):
            raise ValueError('unknown decision gate')
        rows[task] = {**root,**new}
        _validate_graph(rows)
        affected = {task}
        while True:
            more = {k for k,r in rows.items() if affected.intersection(r['deps'])}
            if more <= affected:
                break
            affected |= more
        db.execute('UPDATE task_pool SET title=?,deps=?,gates=?,checks=? WHERE id=?',
                   (new['title'],json.dumps(new['deps']),json.dumps(new['gates']),json.dumps(new['checks']),task))
        for k in sorted(affected):
            row = rows[k]
            state = 'RECOVERY_REQUIRED' if row['state'] in ('RUNNING','RECOVERY_REQUIRED') else 'PENDING'
            owner = row['session'] if state=='RECOVERY_REQUIRED' else None
            db.execute('UPDATE task_pool SET revision=?,state=?,session=? WHERE id=?',(row['revision']+1,state,owner,k))
            detail = {'root':task,'old_revision':row['revision'],'revision':row['revision']+1,
                      'old_state':row['state'],'old_session':row['session'],'state':state}
            if k==task:
                detail.update({'before':old,'after':new})
            _event(db,k,session,'REVISE' if k==task else 'INVALIDATE',evidence,detail)
    return {'task':task,'revision':expected_revision+1,'affected':sorted(affected),'authorization_granted':False}


def recover(path, task, expected_revision, previous_session, session, evidence, confirmed=False):
    """Acknowledge stopped invalidated work; never revive its acceptance."""
    if confirmed is not True or type(expected_revision) is not int:
        raise ValueError('explicit recovery confirmation and revision required')
    task,previous_session,session = [_id(v) for v in (task,previous_session,session)]
    evidence = wb._text(evidence,'verified stopped worker and reconciliation evidence',4000)
    if session==previous_session:
        raise ValueError('new recovery reviewer session required')
    with closing(wb.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        r = _pool(db).get(task)
        if not r or r['state']!='RECOVERY_REQUIRED' or r['session']!=previous_session:
            raise ValueError('recovery owner/state changed; review first')
        _revision(r,expected_revision)
        db.execute("UPDATE task_pool SET state='PENDING',session=NULL WHERE id=?",(task,))
        _event(db,task,session,'RECOVER',evidence,{'previous_session':previous_session,'revision':r['revision']})
    return {'task':task,'state':'PENDING','revision':expected_revision,'authorization_granted':False}


def start(path, task, session, expected_revision=None):
    task, session = _id(task), _id(session)
    with closing(wb.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        r = _pool(db).get(task)
        if not r or not r['ready']:
            raise ValueError('task not ready')
        _revision(r,expected_revision)
        _new_session(db,task,session)
        db.execute('UPDATE task_pool SET state=?,session=? WHERE id=?',('RUNNING',session,task))
        _event(db,task,session,'START','operator started',{'revision':r['revision']})
    return {'task':task,'state':'RUNNING','revision':r['revision']}


def resume(path, task, previous_session, session, evidence, confirmed=False, expected_revision=None):
    if confirmed is not True:
        raise ValueError('explicit interrupted-task review required')
    task, previous_session, session = [_id(v) for v in (task,previous_session,session)]
    evidence = wb._text(evidence,'resume evidence',4000)
    if previous_session == session:
        raise ValueError('new session required')
    with closing(wb.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        r = _pool(db).get(task)
        if not r or r['state']!='RUNNING' or r['session']!=previous_session:
            raise ValueError('running owner changed; read back before retry')
        _revision(r,expected_revision)
        _new_session(db,task,session)
        if r['blocked_by'] or r['recovery_blockers']:
            raise ValueError('prerequisites or recovery blocked')
        db.execute('UPDATE task_pool SET session=? WHERE id=?',(session,task))
        _event(db,task,session,'RESUME',evidence,{'previous_session':previous_session,'revision':r['revision']})
    return {'task':task,'state':'RUNNING','revision':r['revision'],'authorization_granted':False}


def finish(path, task, session, results, evidence, expected_revision=None):
    task, session = _id(task), _id(session)
    evidence = wb._text(evidence,'acceptance evidence',4000)
    with closing(wb.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        r = _pool(db).get(task)
        if not r or r['state']!='RUNNING' or r['session']!=session:
            raise ValueError('task not owned by this session')
        _revision(r,expected_revision)
        if r['blocked_by'] or r['recovery_blockers']:
            raise ValueError('prerequisites or recovery blocked')
        if not isinstance(results,dict) or set(results)!=set(r['checks']) or any(v not in ('PASS','FAIL') for v in results.values()):
            raise ValueError('all acceptance check results required')
        passed = all(v=='PASS' for v in results.values())
        status = 'DONE' if passed else 'PENDING'
        db.execute('UPDATE task_pool SET state=?,session=NULL WHERE id=?',(status,task))
        _event(db,task,session,'PASS' if passed else 'FAIL',evidence,{'revision':r['revision'],'checks':results})
    return {'task':task,'state':status,'revision':r['revision'],'operator_declared_evidence':True,'authorization_granted':False}


def review(path):
    with closing(_ro(path)) as db:
        db.execute('BEGIN')
        tasks = list(_pool(db).values())
        events = [dict(r) for r in db.execute('SELECT * FROM task_events ORDER BY seq')]
        decisions = [dict(r) for r in db.execute('SELECT * FROM task_decisions ORDER BY id')]
        return {'tasks':tasks,'next_ready':[r['id'] for r in tasks if r['ready']],
                'running_review':[r['id'] for r in tasks if r['state']=='RUNNING'],
                'recovery_review':[r['id'] for r in tasks if r['state']=='RECOVERY_REQUIRED'],
                'decisions':decisions,'open_decisions':[r for r in decisions if r['answer'] is None],
                'attempts':sum(e['kind'] in ('PASS','FAIL') for e in events),
                'failed_attempts':sum(e['kind']=='FAIL' for e in events),
                'completed':sum(r['state']=='DONE' for r in tasks),'history':events,
                'authorization_granted':False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('setup','question','resolve','add','start','resume','finish','review','revise','recover'))
    p.add_argument('--workspace',required=True,type=Path)
    p.add_argument('--input',type=Path)
    a = p.parse_args()
    try:
        args = json.loads(a.input.read_text(encoding='utf-8-sig')) if a.input else {}
        fn = {'setup':setup,'question':question,'resolve':resolve_decision,'add':add,'start':start,'resume':resume,'finish':finish,'review':review,'revise':revise,'recover':recover}[a.action]
        print(json.dumps(fn(a.workspace,**args),ensure_ascii=False,indent=2))
    except (ValueError,TypeError,KeyError,OSError,sqlite3.Error) as e:
        p.exit(2,'WORKBENCH_TASKS_BLOCKED: '+str(e)+'\n')


if __name__=='__main__':
    main()
