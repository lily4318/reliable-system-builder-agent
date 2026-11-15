"""TD-004: offline structural validation, NOT curriculum reading or assessment."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs/training/curriculum-coverage.json"
CATALOG = ROOT / "config/skill-catalog.json"
LEVEL_EVIDENCE = ("principles", "analysis", "implementation", "repair",
                  "transfer", "handoff")
MAX_UNITS = 2000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def sha256_pin(value):
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None


def unique_strings(values):
    return (isinstance(values, list) and all(nonblank(x) for x in values)
            and len(values) == len(set(values)))


def validate(matrix, catalog):
    """Check claims against declared inventory, not against external ground truth."""
    require(isinstance(matrix, dict) and type(matrix.get("schema_version")) is int
            and matrix["schema_version"] == 1, "schema")
    require(set(matrix) == {"schema_version", "source_links", "inventory_status",
                           "inventory_sha256", "expected_ids", "units"}, "matrix fields")
    require(unique_strings(matrix["source_links"]) and matrix["source_links"],
            "source links required")
    status = matrix["inventory_status"]
    require(status in ("BLOCKED_SOURCE", "PARTIAL", "COMPLETE_DECLARED"), "inventory status")
    expected = matrix["expected_ids"]
    units = matrix["units"]
    require(unique_strings(expected) and len(expected) <= MAX_UNITS, "inventory IDs")
    require(isinstance(units, list) and len(units) <= MAX_UNITS, "unit count")
    require(isinstance(catalog, dict) and isinstance(catalog.get("skills"), list), "catalog")
    skills = {x["id"]: x["role"] for x in catalog["skills"]}
    roles = set(skills.values())
    if status == "BLOCKED_SOURCE":
        require(expected == [] and units == [] and matrix["inventory_sha256"] is None,
                "unknown inventory cannot claim units or source pin")
    else:
        require(sha256_pin(matrix["inventory_sha256"]) and expected,
                "readable inventory pin and IDs required")
    by_id = {}
    for u in units:
        require(isinstance(u, dict) and set(u) == {
            "id", "source_url", "source_sha256", "access", "owner", "collaborators",
            "skill", "prerequisites", "maturity", "evidence"
        }, "unit fields")
        uid = u["id"]
        require(nonblank(uid) and uid in expected and uid not in by_id, "duplicate/unknown unit")
        require(nonblank(u["source_url"]), "source URL")
        require(isinstance(u["owner"], str) and u["owner"] in roles, "single catalog owner")
        require(unique_strings(u["collaborators"]) and set(u["collaborators"]) <= roles
                and u["owner"] not in u["collaborators"], "collaborators")
        require(isinstance(u["skill"], str) and skills.get(u["skill"]) == u["owner"],
                "skill must belong to owner")
        require(unique_strings(u["prerequisites"]) and uid not in u["prerequisites"]
                and set(u["prerequisites"]) <= set(expected), "prerequisites")
        level = u["maturity"]
        require(type(level) is int and 0 <= level <= 6, "maturity")
        evidence = u["evidence"]
        require(isinstance(evidence, dict) and set(evidence) == set(LEVEL_EVIDENCE[:level])
                and all(nonblank(x) for x in evidence.values()), "level evidence references")
        require(u["access"] in ("BLOCKED_SOURCE", "UNREAD", "READABLE"), "unit access")
        if u["access"] == "READABLE":
            require(sha256_pin(u["source_sha256"]), "readable unit pin")
        else:
            require(level == 0 and u["source_sha256"] is None,
                    "unread/blocked source cannot claim maturity or pin")
        by_id[uid] = u
    if status == "COMPLETE_DECLARED":
        require(set(by_id) == set(expected), "missing inventory unit")
    # Kahn ordering: partial missing prerequisites stay unresolved, not invalid cycles.
    incoming = {uid: set(u["prerequisites"]) & by_id.keys() for uid, u in by_id.items()}
    children = {uid: [] for uid in by_id}
    for uid, deps in incoming.items():
        for dep in deps:
            children[dep].append(uid)
    queue = [uid for uid, deps in incoming.items() if not deps]
    seen = 0
    while queue:
        uid = queue.pop()
        seen += 1
        for child in children[uid]:
            incoming[child].remove(uid)
            if not incoming[child]:
                queue.append(child)
    require(seen == len(by_id), "dependency cycle")
    candidates = [
        uid for uid, u in by_id.items()
        if u["access"] == "READABLE" and u["maturity"] < 6
        and all(dep in by_id and by_id[dep]["maturity"] >= 2 for dep in u["prerequisites"])
    ]
    return {"inventory_status": status, "listed_units": len(expected),
            "assigned_units": len(by_id), "review_candidates": sorted(candidates),
            "unknown_total": status != "COMPLETE_DECLARED",
            "coverage_percent": None, "source_verified": False,
            "evidence_verified": False, "curriculum_completed": False,
            "model_improvement_verified": False}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def load_json(path):
    # Limit local input; never retrieve or execute source URLs or examples.
    with Path(path).open("rb") as file:
        raw = file.read(2_000_001)
    require(len(raw) <= 2_000_000, "input too large")
    return json.loads(raw, object_pairs_hook=_unique_object)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=MATRIX)
    args = parser.parse_args()
    try:
        print(json.dumps(validate(load_json(args.matrix), load_json(CATALOG)), ensure_ascii=False))
    except (ValueError, TypeError, KeyError, OSError, RecursionError) as exc:
        parser.exit(1, "Invalid curriculum metadata: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
