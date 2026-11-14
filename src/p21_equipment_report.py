"""Synthetic equipment report training slice, no external service or deployment.

The caller must supply an authenticated actor. This module is not an auth
endpoint. V1 is retained solely as the executable pre-revision baseline.
"""
from .p21_equipment_site import MEMBERS


def _snapshot(store, actor):
    if actor not in (*MEMBERS, 'admin'):
        raise PermissionError('unknown actor')
    return store.view(None if actor == 'admin' else actor,
                      lifecycle=True, actor=actor)


def report_v1(store, actor):
    """Revision 1: active quantity only, scoped to the actor."""
    _, _, rows, _ = _snapshot(store, actor)
    return {'active_quantity': sum(row[2] for row in rows if row[4]=='RESERVED')}


def report_v2(store, actor):
    """Revision 2: explicit state quantities and own denied operation count.

    Admin sees all reservation quantities and global inventory, but only
    their own action attempts; members see only their own reservation data
    and their own action attempts, never global inventory or other actors.
    All values come from one read-only SQLite snapshot.
    """
    stock, reserved, rows, attempts = _snapshot(store, actor)
    quantities = {state: 0 for state in ('RESERVED','CANCELLED','RETURNED','INSUFFICIENT')}
    for row in rows:
        quantities[row[4]] += row[2]
    result = {'active_quantity': quantities['RESERVED'],
              'cancelled_quantity': quantities['CANCELLED'],
              'returned_quantity': quantities['RETURNED'],
              'insufficient_quantity': quantities['INSUFFICIENT'],
              'denied_operations': sum(row[4]=='NOT_ACTIVE' for row in attempts)}
    if actor=='admin':
        if quantities['RESERVED'] != reserved:
            raise ValueError('inventory invariant mismatch')
        result['inventory'] = {'stock':stock,'reserved':reserved,'available':stock-reserved}
    return result
