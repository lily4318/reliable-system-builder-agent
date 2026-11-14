"""Offline, two-source provider evidence comparison with replay detection.

All inputs are local private OFFLINE copies. "provider official export" means
a purported provider-side read-only export, NOT authenticated provider data.
A forged local manifest plus forged external export can agree. Independent
provider-origin authentication and human permission must remain false.
No network, secret, API, model, POST, file mutation, or automatic ledger update.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys

from src.llm_provider_evidence import (
    _private_json, _canonical, _sha, _utc, _string, _status,
    audit_evidence, MANIFEST_FIELDS,
)
from src.llm_requirements_eval import ROOT

EXPORT_KEYS = frozenset((
    "schema_version", "source_kind", "acquisition_channel",
    "retrieved_by_ref", "runner_operator_ref", "collected_at_utc",
    "official_account_ref", "records",
))
PROVIDER_RECORD_KEYS = frozenset((
    "provider", "request_id", "response_id", "model", "model_version",
    "status", "created_at_utc", "output_sha256",
))
LEDGER_KEYS = frozenset((
    "schema_version", "scope", "snapshot_at_utc", "prior_requests",
))
PRIOR_KEYS = frozenset(("request_id", "response_id"))
RESPONSE_KEYS = frozenset((
    "provider", "model", "model_version", "request_id", "response_id",
    "status", "created_at_utc", "output",
))


def _blocked(code: str, *, local_match: bool = False) -> dict:
    return {
        **_status(code),
        "local_integrity_consistent": local_match,
        "two_source_fields_consistent": False,
        "external_export_origin_authenticated": False,
        "official_api_response_authenticated": False,
        "human_authorization_independently_verified": False,
        "replay_free_globally_verified": False,
        "model_version_provider_authenticated": False,
        "real_llm_performance_measured": False,
        "provider_calls_by_audit": 0,
        "registry_mutations_by_audit": 0,
    }


def audit_two_sources(manifest_path: Path | None = None,
                      runner_config: Path | None = None,
                      provider_export: Path | None = None,
                      previous_ids_ledger: Path | None = None) -> dict:
    """Fail closed and never equate two matching copies to official provenance."""
    if any(p is None for p in (
        manifest_path, runner_config, provider_export, previous_ids_ledger
    )):
        return _blocked("BLOCKED_DUAL_SOURCE_AND_LEDGER_REQUIRED")
    paths = [Path(p) for p in (
        manifest_path, runner_config, provider_export, previous_ids_ledger
    )]
    # Separate directories reduce accidental re-use of one runner-produced file.
    # They do not authenticate real acquisition independence.
    resolved = [p.resolve() for p in paths]
    if len(set(resolved)) != 4 or not all(p.is_absolute() for p in paths):
        return _blocked("BLOCKED_SOURCE_PATH_NOT_INDEPENDENT")
    if paths[0].parent.resolve() == paths[2].parent.resolve():
        return _blocked("BLOCKED_EXPORT_NOT_SEPARATELY_STORED")
    local_result = audit_evidence(manifest_path, runner_config)
    if local_result.get("local_integrity_consistent") is not True:
        return _blocked("BLOCKED_LOCAL_SOURCE_INVALID")
    manifest_obj = _private_json(manifest_path)
    official_obj = _private_json(provider_export)
    ledger_obj = _private_json(previous_ids_ledger)
    if manifest_obj is None or official_obj is None or ledger_obj is None:
        return _blocked("BLOCKED_PRIVATE_SOURCE_OR_LEDGER_MISSING", local_match=True)
    m, _ = manifest_obj
    export, _ = official_obj
    ledger, _ = ledger_obj
    if not isinstance(m, dict) or set(m) != MANIFEST_FIELDS:
        return _blocked("BLOCKED_LOCAL_SCHEMA_CHANGED")
    if not isinstance(export, dict) or set(export) != EXPORT_KEYS or (
        type(export.get("schema_version")) is not int or
        export["schema_version"] != 1 or
        export.get("source_kind") != "claimed_provider_readonly_export" or
        export.get("acquisition_channel") != "out_of_band_readonly"
    ):
        return _blocked("BLOCKED_EXTERNAL_EXPORT_SCHEMA", local_match=True)
    if not all(_string(export.get(k)) for k in (
        "retrieved_by_ref", "runner_operator_ref", "official_account_ref"
    )) or export["retrieved_by_ref"] == export["runner_operator_ref"]:
        return _blocked("BLOCKED_SOURCE_CUSTODY_CONFLICT", local_match=True)
    export_time = _utc(export.get("collected_at_utc"))
    call_end = _utc(m["call_finished_at_utc"])
    if export_time is None or call_end is None or export_time < call_end:
        return _blocked("BLOCKED_EXPORT_CHRONOLOGY", local_match=True)
    records = export.get("records")
    if not isinstance(records, list) or not records or len(records) > 100:
        return _blocked("BLOCKED_EXPORT_RECORDS", local_match=True)
    seen_requests, seen_responses = set(), set()
    official_record = None
    for record in records:
        if not isinstance(record, dict) or set(record) != PROVIDER_RECORD_KEYS:
            return _blocked("BLOCKED_EXPORT_RECORD_SCHEMA", local_match=True)
        if not all(_string(record.get(k)) for k in (
            "provider", "request_id", "response_id", "model", "model_version"
        )) or record.get("status") != "completed" or (
            not isinstance(record.get("output_sha256"), str) or
            len(record["output_sha256"]) != 64 or
            any(c not in "0123456789abcdef" for c in record["output_sha256"])
        ):
            return _blocked("BLOCKED_EXPORT_RECORD_VALUES", local_match=True)
        if record["request_id"] in seen_requests or (
            record["response_id"] in seen_responses
        ):
            return _blocked("BLOCKED_DUPLICATE_EXPORT_REQUEST_OR_RESPONSE_ID",
                            local_match=True)
        seen_requests.add(record["request_id"])
        seen_responses.add(record["response_id"])
        if record["request_id"] == m["request_id"]:
            official_record = record
    if official_record is None:
        return _blocked("BLOCKED_NO_PROVIDER_SOURCE_MATCH", local_match=True)
    if any(official_record[k] != m[mk] for k, mk in (
        ("provider", "provider"),
        ("request_id", "request_id"),
        ("response_id", "response_id"),
        ("model", "requested_model"),
        ("model_version", "requested_model_version"),
    )):
        return _blocked("BLOCKED_PROVIDER_RECORD_MISMATCH", local_match=True)
    if not isinstance(ledger, dict) or set(ledger) != LEDGER_KEYS or (
        type(ledger.get("schema_version")) is not int or
        ledger["schema_version"] != 1 or ledger.get("scope") != "public_dev"
    ):
        return _blocked("BLOCKED_LEDGER_SCHEMA", local_match=True)
    ledger_time = _utc(ledger.get("snapshot_at_utc"))
    start_time = _utc(m["call_started_at_utc"])
    if ledger_time is None or start_time is None or ledger_time > start_time:
        return _blocked("BLOCKED_LEDGER_SNAPSHOT_AFTER_REQUEST", local_match=True)
    prior = ledger.get("prior_requests")
    if not isinstance(prior, list) or len(prior) > 500:
        return _blocked("BLOCKED_LEDGER_RECORDS", local_match=True)
    seen_prior_r, seen_prior_s = set(), set()
    for entry in prior:
        if not isinstance(entry, dict) or set(entry) != PRIOR_KEYS or (
            not all(_string(entry.get(k)) for k in PRIOR_KEYS)
        ):
            return _blocked("BLOCKED_LEDGER_RECORD_SCHEMA", local_match=True)
        if entry["request_id"] in seen_prior_r or (
            entry["response_id"] in seen_prior_s
        ):
            return _blocked("BLOCKED_DUPLICATE_LEDGER_RECORD", local_match=True)
        seen_prior_r.add(entry["request_id"])
        seen_prior_s.add(entry["response_id"])
    if m["request_id"] in seen_prior_r or m["response_id"] in seen_prior_s:
        return _blocked("BLOCKED_REPLAYED_REQUEST_OR_RESPONSE_ID", local_match=True)
    local_response = _private_json(Path(m["response_path"]))
    if local_response is None:
        return _blocked("BLOCKED_LOCAL_RESPONSE_UNAVAILABLE", local_match=True)
    resp, _ = local_response
    if not isinstance(resp, dict) or set(resp) != RESPONSE_KEYS:
        return _blocked("BLOCKED_RESPONSE_SCHEMA_CHANGED", local_match=True)
    if resp["created_at_utc"] != official_record["created_at_utc"]:
        return _blocked("BLOCKED_PROVIDER_RESPONSE_TIME_MISMATCH", local_match=True)
    if _sha(_canonical(resp["output"])) != official_record["output_sha256"]:
        return _blocked("BLOCKED_PROVIDER_OUTPUT_SHA_MISMATCH", local_match=True)
    return {
        **_blocked("TWO_SOURCE_FIELDS_MATCH_ORIGIN_AND_AUTHORIZATION_UNVERIFIED",
                   local_match=True),
        "two_source_fields_consistent": True,
        "official_export_local_file_sha256": _sha(official_obj[1]),
        "replay_ledger_local_file_sha256": _sha(ledger_obj[1]),
        "request_id_sha256": _sha(m["request_id"].encode("utf-8")),
        "response_id_sha256": _sha(m["response_id"].encode("utf-8")),
        # The export and ledger are non-cryptographic, unverified attestations.
        "custody_claim_only": True,
        "complete_replay_protection_not_proven": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit",))
    parser.add_argument("--local-manifest", type=Path)
    parser.add_argument("--runner-config", type=Path)
    parser.add_argument("--provider-export", type=Path)
    parser.add_argument("--previous-ids-ledger", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-two-source-match", action="store_true")
    args = parser.parse_args()
    try:
        result = audit_two_sources(args.local_manifest, args.runner_config,
                                   args.provider_export, args.previous_ids_ledger)
        report = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        print(report)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(report, encoding="utf-8")
        if args.require_two_source_match and not result["two_source_fields_consistent"]:
            return 2
        return 0
    except (ValueError, OSError, UnicodeError):
        print("TWO_SOURCE_AUDIT_BLOCKED", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
