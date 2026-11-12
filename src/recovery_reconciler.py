"""Offline, fail-closed reconciliation of partial remote deployments.

Input is a **sanitized snapshot** of an existing external project's evidence.
No Google/GitHub API client, network access, credentials, mutations or retries.
This is a decision aid, not proof that a remote system has actually been read.
"""
from __future__ import annotations

from typing import Any

GET_ACTIONS = (
    "GET_HEAD", "GET_VERSIONS", "GET_DEPLOYMENTS",
    "GET_VERSION_CONTENT", "GET_DEPLOYMENT_DETAIL",
)
BLOCK_ACTIONS = ("HUMAN_REVIEW",)

def _error(label: str) -> ValueError:
    return ValueError("invalid sanitized evidence: " + label)

def _snapshot(data: Any, label: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise _error(label)
    if type(data.get("head_sha")) is not str or not data["head_sha"]:
        raise _error(label + ".head_sha")
    vv = data.get("versions")
    dd = data.get("deployments")
    if not isinstance(vv, list) or not isinstance(dd, list):
        raise _error(label + ".inventory")
    if any(type(x) is not int or x <= 0 for x in vv) or len(vv) != len(set(vv)):
        raise _error(label + ".versions")
    seen = set()
    head_count = 0
    for dep in dd:
        if not isinstance(dep, dict) or type(dep.get("id")) is not str:
            raise _error(label + ".deployment_shape")
        ident = dep["id"]
        if not ident or ident in seen:
            raise _error(label + ".deployment_id")
        seen.add(ident)
        kind = dep.get("kind")
        version = dep.get("version")
        if kind == "HEAD":
            head_count += 1
            if version is not None:
                raise _error(label + ".head_version")
        elif kind == "VERSIONED":
            if type(version) is not int or version <= 0:
                raise _error(label + ".versioned_version")
        else:
            raise _error(label + ".deployment_kind")
        if dep.get("access") not in ("MYSELF", "ANYONE", "ANYONE_ANONYMOUS", "DOMAIN", "UNKNOWN"):
            raise _error(label + ".access")
        if dep.get("execute_as") not in ("USER_DEPLOYING", "USER_ACCESSING", "UNKNOWN"):
            raise _error(label + ".execute_as")
    if head_count != 1:
        raise _error(label + ".head_count")
    return data

def _result(code: str, detail: str, needs_get: bool = True) -> dict[str, Any]:
    # Safety property: this module never recommends POST, deployment or launch.
    return {
        "classification": code,
        "reason": detail,
        "allowed_next_actions": list(GET_ACTIONS if needs_get else BLOCK_ACTIONS),
        "mutation_allowed": False,
        "formal_launch_allowed": False,
        "requires_human_review": True,
    }

def reconcile(evidence: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(evidence, dict):
        raise _error("root")
    if evidence.get("target_isolated") is not True:
        return _result("BLOCK_TARGET", "Target isolation not established", False)
    if evidence.get("source_verified") is not True:
        return _result("BLOCK_SOURCE", "Source/commit authority not verified", False)
    baseline = _snapshot(evidence.get("before"), "before")
    later = evidence.get("after")
    if later is None:
        return _result("READBACK_MISSING", "Fresh read-only inventory required")
    after = _snapshot(later, "after")

    if evidence.get("intake_closed") is not True:
        return _result("BLOCK_LIVE_INTAKE", "Real intake must remain disabled", False)
    if baseline["head_sha"] != after["head_sha"]:
        return _result("BLOCK_HEAD_DRIFT", "Remote HEAD hash changed", False)
    for dep in after["deployments"]:
        if dep["access"] != "MYSELF" or dep["execute_as"] != "USER_DEPLOYING":
            return _result("BLOCK_UNSAFE_ACL", "Remote access/identity not private", False)

    stage = evidence.get("post_stage")
    if stage not in ("none", "create_version_success", "create_version_unknown",
                     "create_deployment_success", "create_deployment_unknown"):
        raise _error("post_stage")

    before_v = set(baseline["versions"])
    after_v = set(after["versions"])
    old_ids = {d["id"] for d in baseline["deployments"]}
    after_ids = {d["id"] for d in after["deployments"]}
    if not before_v <= after_v or not old_ids <= after_ids:
        return _result("BLOCK_INVENTORY_REMOVAL", "Existing remote resource disappeared", False)
    changed_existing = any(
        next(d for d in after["deployments"] if d["id"] == old["id"]) != old
        for old in baseline["deployments"]
    )
    if changed_existing:
        return _result("BLOCK_EXISTING_DEPLOYMENT_CHANGE", "Original deployment changed", False)

    new_v = after_v - before_v
    new_deps = [d for d in after["deployments"] if d["id"] not in old_ids]
    reported_version = evidence.get("returned_version")
    if reported_version is not None and (type(reported_version) is not int or reported_version <= 0):
        raise _error("returned_version")
    immutable_verified = evidence.get("immutable_sha_verified") is True

    if stage in ("create_version_unknown", "create_deployment_unknown"):
        return _result("UNKNOWN_POST_RESULT", "Non-idempotent write may have succeeded; reconcile by GET")
    if stage == "none":
        if new_v or new_deps:
            return _result("UNATTRIBUTED_REMOTE_CHANGE", "Observed changes have no matching authorized POST", False)
        return _result("NO_MUTATION_OBSERVED", "No remote changes visible in supplied snapshots")
    if stage == "create_version_success":
        if reported_version is None or not immutable_verified:
            return _result("VERSION_PROOF_INCOMPLETE", "Version response or immutable content not verified")
        if new_deps or any(v != reported_version for v in new_v):
            return _result("BLOCK_UNEXPECTED_DELTA", "Unexpected resource written", False)
        if reported_version not in after_v:
            return _result("VERSION_LIST_LAG", "Immutable content verified but list does not yet show it")
        if len(new_v) != 1:
            return _result("BLOCK_UNEXPECTED_DELTA", "Version count not a single increment", False)
        return _result("ORPHAN_VERSION_CONFIRMED", "One immutable version exists with no new deployment")
    if stage in ("create_deployment_success",):
        if reported_version is None or not immutable_verified:
            return _result("DEPLOYMENT_PROOF_INCOMPLETE", "Immutable version not verified")
        if reported_version not in after_v:
            return _result("DEPLOYMENT_INVENTORY_LAG", "Created version missing from list")
        if len(new_v) != 1 or new_v != {reported_version}:
            return _result("BLOCK_UNEXPECTED_DELTA", "Unexpected immutable version delta", False)
        if not new_deps:
            return _result("DEPLOYMENT_LIST_LAG", "Deployment POST returned but list not yet updated")
        if len(new_deps) != 1 or new_deps[0]["kind"] != "VERSIONED" or new_deps[0]["version"] != reported_version:
            return _result("BLOCK_UNEXPECTED_DELTA", "Unexpected new deployment", False)
        return _result("PRIVATE_DEPLOYMENT_PRESENT_NEEDS_UAT", "Private endpoint present; real UI/formal gates remain separate")
    raise _error("unhandled stage")
