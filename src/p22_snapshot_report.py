"""P2-2c: synthetic SQLite snapshot to versioned, deterministic report ZIP.

Trusted stable local paths and cooperating snapshot writers only. No production
data, external release, authentication, directory fsync or power-loss claims.
"""
import argparse
import hashlib
import io
import json
import os
import re
import sqlite3
import tempfile
import zipfile
from contextlib import closing
from pathlib import Path

GROUPS = ('paper', 'pencil', 'folder')
STATES = ('complete', 'pending', 'rejected')
MAX_ROWS = 1000


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode('ascii')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(path, expected_revision):
    """Read one SQLite transaction; never create a missing source."""
    if type(expected_revision) is not int or expected_revision < 1:
        raise ValueError('invalid expected source revision')
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('regular existing source required')
    with closing(sqlite3.connect(path.absolute().as_uri()+'?mode=ro', uri=True, timeout=5)) as db:
        db.execute('PRAGMA query_only=ON')
        db.execute('BEGIN')
        # Keep invalid variable-length metadata out of Python as well.
        revisions = db.execute(
            "SELECT CASE WHEN typeof(revision)='integer' THEN revision END FROM metadata LIMIT 2"
        ).fetchall()
        if revisions != [(expected_revision,)] or type(revisions[0][0]) is not int:
            raise ValueError('STALE_SOURCE_OR_INVALID_REVISION')
        # Allow at most 16 encoded bytes per text field: every valid value
        # has at most eight ASCII characters, including in UTF-16 databases.
        # BLOB length counts bytes (TEXT length stops at embedded NUL).
        # Preserve invalid rows as NULL sentinels; never filter them away.
        # Python still validates exact identifiers, enums and quantities.
        # This bounds returned values, not SQLite native scan/sort resources.
        rows = db.execute("""SELECT record_id, category, state, quantity FROM (
            SELECT CASE WHEN typeof(record_id)='text' AND length(CAST(record_id AS BLOB))<=16 THEN record_id END AS record_id,
                   CASE WHEN typeof(category)='text' AND length(CAST(category AS BLOB))<=16 THEN category END AS category,
                   CASE WHEN typeof(state)='text' AND length(CAST(state AS BLOB))<=16 THEN state END AS state,
                   CASE WHEN typeof(quantity)='integer' THEN quantity END AS quantity
            FROM records
        ) ORDER BY record_id LIMIT ?""", (MAX_ROWS+1,)).fetchall()
        if not rows or len(rows)>MAX_ROWS:
            raise ValueError('invalid row count')
        seen = set()
        for ident, group, state, qty in rows:
            if not isinstance(ident,str) or not re.fullmatch(r'SYN-[0-9]{4}',ident) or ident in seen:
                raise ValueError('invalid record ID')
            if group not in GROUPS or state not in STATES or type(qty) is not int or not 1<=qty<=999:
                raise ValueError('invalid source row')
            seen.add(ident)
        return rows


def report(rows, policy):
    if type(policy) is not int or policy not in (1,2):
        raise ValueError('unknown report policy')
    totals = {g:0 for g in GROUPS}
    counts = {s:0 for s in STATES}
    for _, group, state, qty in rows:
        counts[state] += 1
        if state == 'complete':
            totals[group] += qty
    result = {'policy_revision':policy,'completed_quantities':totals}
    if policy == 2:
        result['status_counts'] = counts
    return result


def bundle(source, expected_revision, policy):
    rows = snapshot(source, expected_revision)
    report_bytes = canonical(report(rows, policy))
    manifest = canonical({'schema_version':1,'source_revision':expected_revision,
        'policy_revision':policy,'snapshot_sha256':sha(canonical(rows)),
        'report_sha256':sha(report_bytes)})
    output = io.BytesIO()
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_STORED) as archive:
        for name,data in [('report.json', report_bytes),('manifest.json',manifest)]:
            info = zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
            info.create_system=3
            info.external_attr=0o600 << 16
            archive.writestr(info,data)
    return output.getvalue()


def reconcile(source, output, expected_revision, policy):
    # A missing/stale/unreadable source is a blocked verification, not an absent output.
    data = bundle(source, expected_revision, policy)
    output = Path(output)
    if output.is_symlink():
        return 'CONFLICT'
    if not output.exists():
        return 'NOT_OBSERVED'
    if not output.is_file():
        return 'CONFLICT'
    with output.open('rb') as f:
        return 'COMMITTED' if f.read(len(data)+1)==data else 'CONFLICT'


def publish(source, output, expected_revision, policy):
    return _publish_bundle(bundle(source, expected_revision, policy), output)


def _publish_bundle(data, output):
    """Publish already validated bytes; caller owns the source/policy check."""
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise FileExistsError('existing output; reconcile without overwrite')
    fd, staging = tempfile.mkstemp(prefix='.p22-report-',dir=output.parent)
    try:
        with os.fdopen(fd,'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(staging,output)
    finally:
        os.unlink(staging)
    return 'PUBLISHED'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('publish','reconcile'))
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--source-revision',type=int,required=True)
    p.add_argument('--policy-revision',type=int,required=True)
    a = p.parse_args()
    try:
        fn = publish if a.action=='publish' else reconcile
        print(json.dumps({'status':fn(a.source,a.output,a.source_revision,a.policy_revision)}))
        return 0
    except (ValueError,OSError,sqlite3.Error) as exc:
        p.exit(2,'REPORT_BLOCKED: '+str(exc)+'\n')


if __name__ == '__main__':
    raise SystemExit(main())
