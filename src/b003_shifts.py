"""B003 local prototype. Invalid-input UI policy remains unapproved."""


def valid(interval):
    return (isinstance(interval, (tuple, list)) and len(interval) == 2
            and all(type(x) is int for x in interval) and interval[0] < interval[1])


def assess(existing, proposed):
    """Half-open integer intervals. INVALID is an internal prototype state."""
    if not valid(proposed) or not isinstance(existing, (list, tuple)):
        return 'INVALID'
    if not all(valid(interval) for interval in existing):
        return 'INVALID'
    start, end = proposed
    return 'CONFLICT' if any(a < end and start < b for a, b in existing) else 'CLEAR'


def has_overlap(existing, proposed):
    """Fail closed for invalid inputs; not a final user-facing error policy."""
    return assess(existing, proposed) != 'CLEAR'


def assess_sorted(existing, proposed):
    """Alternative sweep PoC, same internal status contract."""
    if not valid(proposed) or not isinstance(existing, (list, tuple)) or not all(valid(x) for x in existing):
        return 'INVALID'
    start, end = proposed
    for a, b in sorted(existing):
        if a >= end:
            break
        if b > start:
            return 'CONFLICT'
    return 'CLEAR'
