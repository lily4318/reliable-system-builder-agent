"""Bind existing diagnostic CI reports to exact checkout/run and bytes.

Offline verification of a caller-supplied independently read context + report digest.
Not signed provenance, not proof of remote CI, never deployment authorization.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

FILES = (
    "evaluation-report.json", "recovery-acceptance.json",
    "capability-assignment.json", "capability-reference-report.json",
    "website-discovery-questions.json", "github-manual-steps.json",
    "website-scenario-evaluation.json", "website-scenario-tasks.json",
    "website-private-holdout-protocol.json",
)
REPORT = "quality-gate.json"
MAX_FILE = 4 * 1024 * 1024

def _unique(pairs):
    result = {}
    for key,value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result

def _read(path):
    # No symlink or special file; bounded read; no archive extraction.
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd,"rb") as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
            raise ValueError("not a regular artifact file")
        raw = f.read(MAX_FILE+1)
    if not raw or len(raw)>MAX_FILE:
        raise ValueError("invalid artifact size")
    return raw

def _parse(raw):
    def invalid_constant(_):
        raise ValueError("non-finite JSON number")
    return json.loads(raw.decode("utf-8"),object_pairs_hook=_unique,
                      parse_constant=invalid_constant)

def context(repository, checkout_sha, run_id, attempt):
    if (not isinstance(repository,str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",repository)
        or not isinstance(checkout_sha,str) or not re.fullmatch(r"[0-9a-f]{40}",checkout_sha)
        or type(run_id) is not int or run_id<1 or type(attempt) is not int or attempt<1):
        raise ValueError("invalid expected build identity")
    return dict(repository=repository,checkout_sha=checkout_sha,run_id=run_id,run_attempt=attempt)

def measure(directory):
    directory = Path(directory)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("invalid report directory")
    result={}
    for name in FILES:
        raw=_read(directory/name)
        _parse(raw)
        result[name]={"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
    return result

def bind(report, directory, expected, actual_checkout):
    if context(expected["repository"],expected["checkout_sha"],expected["run_id"],
               expected["run_attempt"]) != expected or actual_checkout != expected["checkout_sha"]:
        raise ValueError("checkout identity mismatch")
    if report.get("gate_passed") is not True:
        raise ValueError("quality gate not passed")
    if report.get("human_approval_completed") is not False or report.get("formal_release_created") is not False:
        raise ValueError("invalid authorization claim")
    return {**report,"artifact_binding":{"schema_version":1,"kind":"candidate_diagnostic_reports",
              "context":expected,"files":measure(directory),
              "remote_ci_verified":False,"formal_deployment_permitted":False}}

def bind_current_ci(report, directory, root):
    expected=context(os.environ["GITHUB_REPOSITORY"],os.environ["GITHUB_SHA"],
                     int(os.environ["GITHUB_RUN_ID"]),int(os.environ["GITHUB_RUN_ATTEMPT"]))
    actual=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True,timeout=10).strip()
    # Tracked inputs must still correspond to checkout; generated untracked reports are expected.
    diff=subprocess.run(["git","diff","--quiet","HEAD","--"],cwd=root,timeout=10)
    if diff.returncode:
        raise ValueError("tracked checkout changed")
    return bind(report,directory,expected,actual)

def verify(directory, expected, expected_report_sha256, observed_conclusion):
    # Caller must obtain expected context, digest and successful conclusion independently.
    if observed_conclusion!="success":
        raise ValueError("CI not successful")
    if not isinstance(expected_report_sha256,str) or not re.fullmatch(r"[0-9a-f]{64}",expected_report_sha256):
        raise ValueError("missing independent report digest")
    directory=Path(directory)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("invalid report directory")
    raw=_read(directory/REPORT)
    if hashlib.sha256(raw).hexdigest()!=expected_report_sha256:
        raise ValueError("quality report digest mismatch")
    report=_parse(raw)
    if not isinstance(report,dict):
        raise ValueError("invalid quality report")
    # Rebuild the entire binding from measured files and caller's expected identity.
    observed=report.get("artifact_binding")
    calc=bind(report,directory,expected,expected["checkout_sha"])["artifact_binding"]
    if json.dumps(observed,sort_keys=True)!=json.dumps(calc,sort_keys=True):
        raise ValueError("artifact content or identity mismatch")
    if set(p.name for p in directory.iterdir())!=set((*FILES,REPORT)):
        raise ValueError("unexpected artifact file set")
    return {"integrity_matches_supplied_evidence":True,"remote_ci_independently_verified":False,
            "formal_deployment_permitted":False,"context":expected}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory",type=Path)
    parser.add_argument("--repository",required=True)
    parser.add_argument("--sha",required=True)
    parser.add_argument("--run-id",type=int,required=True)
    parser.add_argument("--attempt",type=int,required=True)
    parser.add_argument("--report-sha256",required=True)
    parser.add_argument("--conclusion",required=True)
    a=parser.parse_args()
    try:
        print(json.dumps(verify(a.directory,context(a.repository,a.sha,a.run_id,a.attempt),
                  a.report_sha256,a.conclusion),sort_keys=True))
        return 0
    except (ValueError,OSError,KeyError,TypeError) as e:
        print("ARTIFACT_BLOCKED: "+str(e),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
