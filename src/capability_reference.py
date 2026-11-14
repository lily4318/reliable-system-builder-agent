"""Tiny trusted public example implementations; these are NOT agent-generated.

Only these known reviewable functions are executed by the repository unit tests.
Never import unknown candidate model-generated code into CI without isolation.
"""
from __future__ import annotations


def enrollment_status(capacity: int, enrolled: list[str], applicant: str) -> str:
    if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 0:
        return "INVALID"
    if not isinstance(applicant, str) or not applicant.strip():
        return "INVALID"
    if applicant in enrolled:
        return "ALREADY"
    return "ACCEPT" if len(set(enrolled)) < capacity else "WAITLIST"


def can_checkout(stock: int, reserved: int, quantity: int) -> bool:
    if any(not isinstance(v, int) or isinstance(v, bool) for v in (stock, reserved, quantity)):
        return False
    return stock >= 0 and 0 <= reserved <= stock and 0 < quantity <= stock - reserved


def has_overlap(existing: list[tuple[int, int]], proposed: tuple[int, int]) -> bool:
    if (not isinstance(proposed, tuple) or len(proposed) != 2 or
        any(type(x) is not int for x in proposed) or proposed[0] >= proposed[1]):
        return True
    for item in existing:
        if (not isinstance(item, tuple) or len(item) != 2 or
            any(type(x) is not int for x in item) or item[0] >= item[1]):
            return True
        if item[0] < proposed[1] and proposed[0] < item[1]:
            return True
    return False


def restock_needed(on_hand: int, reserved: int, minimum: int) -> int:
    if (any(type(x) is not int for x in (on_hand, reserved, minimum)) or
        on_hand < 0 or reserved < 0 or minimum < 0 or reserved > on_hand):
        return 0
    return max(0, minimum - (on_hand - reserved))


def pickup_status(orders: dict[str, tuple[str, bool]], ticket: str, code: str) -> str:
    if not isinstance(orders, dict) or not isinstance(ticket, str) or not isinstance(code, str):
        return "INVALID"
    record = orders.get(ticket)
    if record is None:
        return "UNKNOWN"
    expected, claimed = record
    if code != expected:
        return "DENY"
    return "ALREADY" if claimed else "READY_FOR_REVIEW"
