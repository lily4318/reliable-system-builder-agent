"""Read-only runner configuration provenance audit; never contacts a model.

A passing local file SHA or claimed approval is NOT authentication of the LLM
provider, permission to spend tokens, or proof a model response came from it.
The CLI prints only non-sensitive statuses, never paths or credentials.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from src.llm_requirements_eval import PROMPT, ROOT

HEX64 = re.compile(r"^[0-9a-f]{64}$")
FIELDS = frozenset({
    "schema_version", "provider", "model_id", "runner_path",
    "runner_sha256", "prompt_sha256", "evaluator_sha256",
    "approval_scope", "approval_reference", "data_handling_reviewed",
})
MAX_BYTES = 8192


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _outside_repo(path: Path) -> bool:
    return not path.resolve().is_relative_to(ROOT.resolve())


def audit(config_path: Path | None = None) -> dict:
    """Audit private declared provenance without reading secrets or running inference."""
    state = {
        "audit_type": "local_runner_config_integrity_only",
        "status": "BLOCKED_NO_PRIVATE_RUNNER_CONFIG",
        "runner_script_sha256_verified": False,
        "prompt_sha256_verified": False,
        "evaluator_sha256_verified": False,
        "authorized_public_dev_scope_declared": False,
        "model_id_provider_authenticated": False,
        "approval_independently_verified": False,
        "provider_response_origin_verified": False,
        "real_llm_executed": False,
        "live_inference_authorized_by_this_audit": False,
        "model_accuracy_measured": False,
        # These public source hashes do NOT authenticate provider execution.
        "source_prompt_sha256": _sha(PROMPT.encode("utf-8")),
        "source_evaluator_sha256": _sha((ROOT / "src/llm_requirements_eval.py").read_bytes()),
    }
    if config_path is None:
        return state
    path = Path(config_path).resolve()
    if not _outside_repo(path) or not path.is_file():
        return {**state, "status": "BLOCKED_CONFIG_MISSING_OR_PUBLIC"}
    try:
        if path.stat().st_size > MAX_BYTES:
            return {**state, "status": "BLOCKED_CONFIG_INVALID"}
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        return {**state, "status": "BLOCKED_CONFIG_INVALID"}
    if not isinstance(config, dict) or set(config) != FIELDS or (
        type(config.get("schema_version")) is not int or
        config["schema_version"] != 1 or
        type(config.get("data_handling_reviewed")) is not bool or
        config["data_handling_reviewed"] is not True or
        config.get("approval_scope") != "public_dev"
    ):
        return {**state, "status": "BLOCKED_CONFIG_SCHEMA_OR_SCOPE"}
    if any(not isinstance(config[k], str) or not config[k].strip() or
           len(config[k]) > 512 for k in (
               "provider", "model_id", "runner_path", "approval_reference"
           )):
        return {**state, "status": "BLOCKED_UNIDENTIFIED_PROVIDER_OR_APPROVAL"}
    if not config["runner_path"].startswith("/"):
        return {**state, "status": "BLOCKED_RUNNER_NOT_ABSOLUTE"}
    runner = Path(config["runner_path"]).resolve()
    if not _outside_repo(runner) or not runner.is_file() or runner.is_symlink():
        return {**state, "status": "BLOCKED_RUNNER_MISSING_OR_PUBLIC"}
    if not all(isinstance(config[k], str) and HEX64.fullmatch(config[k]) for k in (
        "runner_sha256", "prompt_sha256", "evaluator_sha256"
    )):
        return {**state, "status": "BLOCKED_INTEGRITY_HASH_FORMAT"}
    try:
        runner_matches = _sha(runner.read_bytes()) == config["runner_sha256"]
        prompt_matches = _sha(PROMPT.encode("utf-8")) == config["prompt_sha256"]
        evaluator_matches = _sha((ROOT / "src/llm_requirements_eval.py").read_bytes()) == config["evaluator_sha256"]
    except OSError:
        return {**state, "status": "BLOCKED_HASH_READ_ERROR"}
    report = {
        **state,
        "runner_script_sha256_verified": runner_matches,
        "prompt_sha256_verified": prompt_matches,
        "evaluator_sha256_verified": evaluator_matches,
        "authorized_public_dev_scope_declared": True,
    }
    if not (runner_matches and prompt_matches and evaluator_matches):
        return {**report, "status": "BLOCKED_INTEGRITY_MISMATCH"}
    return {
        **report,
        "status": "CONFIG_HASHES_MATCH_PROVIDER_AND_APPROVAL_STILL_UNVERIFIED",
        # Explicitly do not call this READY_FOR_REAL_MODEL_RUN.
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit",))
    parser.add_argument("--config", type=Path)
    parser.add_argument("--require-config", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.config)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    if args.require_config and result["status"] != "CONFIG_HASHES_MATCH_PROVIDER_AND_APPROVAL_STILL_UNVERIFIED":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
