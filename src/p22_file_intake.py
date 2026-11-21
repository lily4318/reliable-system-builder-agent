"""P2-2b public synthetic CSV intake: deterministic, no-overwrite local bundle.

Trusted local directory; no production data, network, authentication or deployment.
"""
import argparse
import csv
import hashlib
import io
import json
import os
import re
import tempfile
from pathlib import Path

MAX_BYTES = 64 * 1024
MAX_ROWS = 1000
HEADER = ['record_id', 'category', 'quantity']
CATEGORIES = ('paper', 'pencil', 'folder')


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True) + '\n').encode('ascii')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_input(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('regular synthetic input required')
    with path.open('rb') as stream:
        data = stream.read(MAX_BYTES + 1)
    if not data or len(data) > MAX_BYTES:
        raise ValueError('input size out of bounds')
    return data


def transform(data):
    """Validate entire input before any output, including duplicate record IDs."""
    if not data or len(data) > MAX_BYTES:
        raise ValueError('input size out of bounds')
    totals = {key: 0 for key in CATEGORIES}
    seen = set()
    try:
        reader = csv.reader(io.StringIO(data.decode('utf-8'), newline=''), strict=True)
        if next(reader, None) != HEADER:
            raise ValueError('unexpected header')
        for row in reader:
            if len(seen) >= MAX_ROWS or len(row) != 3:
                raise ValueError('row count or shape invalid')
            ident, category, count = row
            if not re.fullmatch(r'R[0-9]{4}', ident) or ident in seen:
                raise ValueError('invalid or duplicate record ID')
            if category not in totals or not re.fullmatch(r'[1-9][0-9]{0,2}', count):
                raise ValueError('invalid category or quantity')
            seen.add(ident)
            totals[category] += int(count)
    except (csv.Error, UnicodeError) as exc:
        raise ValueError('invalid CSV encoding or syntax') from exc
    if not seen:
        raise ValueError('empty data')
    result = {'row_count': len(seen), 'totals': totals}
    return canonical({'schema_version': 1, 'input_sha256': digest(data),
                      'result_sha256': digest(canonical(result)), 'result': result})


def reconcile(input_path, output_path):
    """Read-only: verify complete bytes against independently recomputed input."""
    expected = transform(read_input(input_path))
    output = Path(output_path)
    if output.is_symlink():
        return 'CONFLICT'
    if not output.exists():
        return 'NOT_OBSERVED'
    if not output.is_file():
        return 'CONFLICT'
    with output.open('rb') as source:
        return 'COMMITTED' if source.read(len(expected) + 1) == expected else 'CONFLICT'


def publish(input_path, output_path, fault_before_link=False):
    """Single immutable bundle; output is never replaced, even on replay.

    os.link is the exclusive visibility boundary; do not retry unknown outcomes.
    A process killed before cleanup can leave a private temporary file.
    Does not promise directory fsync, power-loss or nonlocal filesystem durability.
    """
    output = Path(output_path)
    bundle = transform(read_input(input_path))
    if output.exists() or output.is_symlink():
        raise FileExistsError('output already exists; reconcile read-only')
    fd, temporary = tempfile.mkstemp(prefix='.p22-intake-', dir=output.parent)
    try:
        with os.fdopen(fd, 'wb') as target:
            target.write(bundle)
            target.flush()
            os.fsync(target.fileno())
        if fault_before_link:
            raise RuntimeError('injected pre-publication fault')
        os.link(temporary, output)
    finally:
        os.unlink(temporary)
    return 'PUBLISHED'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('publish', 'reconcile'))
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        func = publish if args.action == 'publish' else reconcile
        print(json.dumps({'status': func(args.input, args.output)}))
        return 0
    except (ValueError, OSError) as exc:
        parser.exit(2, 'INTAKE_BLOCKED: ' + str(exc) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
