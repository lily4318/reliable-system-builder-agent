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
        db.execute('INSERT INTO task_pool VALUES (?,?,?,?,?,?,?,NULL)',(task,title,priority,json.dumps(deps),json.dumps(gates),json.dumps(checks),'PENDING'))
    return {'task':task,'state':'PENDING'}


def _pool(db):
    rows = {r['id']:dict(r) for r in db.execute('SELECT * FROM task_pool ORDER BY priority,id')}
    open_gates = {r[0] for r in db.execute('SELECT id FROM task_decisions WHERE answer IS NULL')}
    for r in rows.values():
        for k in ('deps','gates','checks'):
            r[k] = json.loads(r[k])
        r['blocked_by'] = [x for x in r['deps'] if rows[x]['state']!='DONE']+[x for x in r['gates'] if x in open_gates]
        r['ready'] = r['state']=='PENDING' and not r['blocked_by']
    return rows


def start(path, task, session):
    task, session = _id(task), _id(session)
    with closing(wb.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        r = _pool(db).get(task)
        if not r or not r['ready']:
            raise ValueError('task not ready')
        db.execute('UPDATE task_pool SET state=?,session=? WHERE id=?',('RUNNING',session,task))
        db.execute('INSERT INTO task_events(task,session,kind,evidence,results) VALUES (?,?,?,?,?)',(task,session,'START','operator started','{}'))
    return {'task':task,'state':'RUNNING'}


def resume(path, task, previous_session, session, evidence, confirmed=False):
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
        db.execute('UPDATE task_pool SET session=? WHERE id=?',(session,task))
        db.execute('INSERT INTO task_events(task,session,kind,evidence,results) VALUES (?,?,?,?,?)',(task,session,'RESUME',evidence,json.dumps({'previous_session':previous_session})))
    return {'task':task,'state':'RUNNING','authorization_granted':False}


def finish(path, task, session, results, evidence):
    task, session = _id(task), _id(session)
    evidence = wb._text(evidence,'acceptance evidence',4000)
    with closing(wb.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        r = _pool(db).get(task)
        if not r or r['state']!='RUNNING' or r['session']!=session:
            raise ValueError('task not owned by this session')
        if not isinstance(results,dict) or set(results)!=set(r['checks']) or any(v not in ('PASS','FAIL') for v in results.values()):
            raise ValueError('all acceptance check results required')
        passed = all(v=='PASS' for v in results.values())
        status = 'DONE' if passed else 'PENDING'
        db.execute('UPDATE task_pool SET state=?,session=NULL WHERE id=?',(status,task))
        db.execute('INSERT INTO task_events(task,session,kind,evidence,results) VALUES (?,?,?,?,?)',(task,session,'PASS' if passed else 'FAIL',evidence,json.dumps(results,sort_keys=True)))
    return {'task':task,'state':status,'operator_declared_evidence':True,'authorization_granted':False}


def review(path):
    with closing(_ro(path)) as db:
        db.execute('BEGIN')
        tasks = list(_pool(db).values())
        events = [dict(r) for r in db.execute('SELECT * FROM task_events ORDER BY seq')]
        decisions = [dict(r) for r in db.execute('SELECT * FROM task_decisions ORDER BY id')]
        return {'tasks':tasks,'next_ready':[r['id'] for r in tasks if r['ready']],
                'running_review':[r['id'] for r in tasks if r['state']=='RUNNING'],
                'decisions':decisions,'open_decisions':[r for r in decisions if r['answer'] is None],
                'attempts':sum(e['kind'] in ('PASS','FAIL') for e in events),
                'failed_attempts':sum(e['kind']=='FAIL' for e in events),
                'completed':sum(r['state']=='DONE' for r in tasks),'history':events,
                'authorization_granted':False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('setup','question','resolve','add','start','resume','finish','review'))
    p.add_argument('--workspace',required=True,type=Path)
    p.add_argument('--input',type=Path)
    a = p.parse_args()
    try:
        args = json.loads(a.input.read_text(encoding='utf-8-sig')) if a.input else {}
        fn = {'setup':setup,'question':question,'resolve':resolve_decision,'add':add,'start':start,'resume':resume,'finish':finish,'review':review}[a.action]
        print(json.dumps(fn(a.workspace,**args),ensure_ascii=False,indent=2))
    except (ValueError,TypeError,KeyError,OSError,sqlite3.Error) as e:
        p.exit(2,'WORKBENCH_TASKS_BLOCKED: '+str(e)+'\n')


if __name__=='__main__':
    main()
