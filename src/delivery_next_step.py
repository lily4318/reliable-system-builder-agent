"""Read-only, minimally interruptive next-step selector for an existing workbench.

TD-007 synthetic transfer. This is NOT a scheduler, permission grant, or
proof of deployment or human-in-the-loop performance. It reads the existing
workbench_tasks.review() snapshot, never adds tables or changes task states.
"""
import argparse
import json
import sqlite3
from pathlib import Path

from . import workbench_tasks


def choose(snapshot):
    """Choose only actionable work or the earliest currently necessary human gate.

    Other future human decisions remain deferred. An active or quarantined
    worker is never implicitly resumed/recovered. Independent ready work
    remains available. All decisions require the existing external consent
    and workbench gate; the output never authorizes an action.
    """
    if not isinstance(snapshot, dict):
        raise ValueError('workbench review snapshot required')
    rows = snapshot.get('tasks')
    open_items = snapshot.get('open_decisions')
    if not isinstance(rows, list) or not isinstance(open_items, list):
        raise ValueError('complete review snapshot required')
    if any(not isinstance(r, dict) or not isinstance(r.get('id'), str) or
           not isinstance(r.get('deps'), list) or not isinstance(r.get('gates'), list) or
           not isinstance(r.get('ready'), bool) or
           type(r.get('priority')) is not int or
           not isinstance(r.get('state'), str) for r in rows):
        raise ValueError('invalid task row; reconcile the source')
    if len({r['id'] for r in rows}) != len(rows):
        raise ValueError('duplicate task ID; reconcile')
    if any(not isinstance(d, dict) or not isinstance(d.get('id'), str) for d in open_items):
        raise ValueError('invalid decision; reconcile')
    if len({d['id'] for d in open_items}) != len(open_items):
        raise ValueError('duplicate decision ID; reconcile')
    by_id = {r['id']: r for r in rows}
    ordered = sorted(rows, key=lambda r: (r['priority'], r['id']))
    ready = [r['id'] for r in ordered if r['ready']]
    running = [r['id'] for r in ordered if r['state'] == 'RUNNING']
    recovery = [r['id'] for r in ordered if r['state'] == 'RECOVERY_REQUIRED']
    base = {
        'authorization_granted': False,
        'external_writes_performed': False,
        'deployment_verified': False,
        'independent_acceptance_verified': False,
        'protected_inflight_task_ids': running,
        'recovery_required_task_ids': recovery,
    }
    if ready:
        return {**base, 'status': 'AUTONOMOUS_CONTINUE_WITHIN_EXISTING_SCOPE',
                'ready_task_ids': ready, 'ask_decision_ids': []}
    if recovery or running:
        return {**base, 'status': 'READ_ONLY_RECONCILE',
                'ready_task_ids': [], 'ask_decision_ids': []}
    if not rows:
        return {**base, 'status': 'NEEDS_EXISTING_PROJECT_SCOPE',
                'ready_task_ids': [], 'ask_decision_ids': []}
    if all(r['state'] == 'DONE' for r in rows):
        return {**base, 'status': 'TASK_POOL_DONE_REQUIRES_INDEPENDENT_REVIEW',
                'ready_task_ids': [], 'ask_decision_ids': []}
    open_ids = {d['id'] for d in open_items}
    for r in ordered:
        if r['state'] != 'PENDING':
            continue
        if any(dep not in by_id or by_id[dep]['state'] != 'DONE'
               for dep in r['deps']):
            continue
        pending = [g for g in r['gates'] if g in open_ids]
        if pending:
            return {**base, 'status': 'NEEDS_CURRENT_HUMAN_DECISION',
                    'blocked_task_id': r['id'], 'ready_task_ids': [],
                    'ask_decision_ids': pending}
    return {**base, 'status': 'BLOCKED_NEEDS_SOURCE_AND_PREREQUISITE_REVIEW',
            'ready_task_ids': [], 'ask_decision_ids': []}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = choose(workbench_tasks.review(args.workspace))
    except (ValueError, KeyError, TypeError, OSError, sqlite3.Error) as exc:
        parser.exit(2, 'DELIVERY_NEXT_STEP_BLOCKED: ' + str(exc) + '\n')
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == '__main__':
    main()
