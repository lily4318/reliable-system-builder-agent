"""Private skill workbench. Local artifacts and learning, not a model runner.

The AI chooses and performs skills with its available tools; this module
persists handoffs and retrieves context. Nothing here deploys or calls an API.
"""
from __future__ import annotations
import argparse
import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "config/skill-catalog.json"
KINDS = ("preference", "lesson", "knowledge", "case")
MAX_TEXT = 250000


def catalog():
    return {s["id"]: s for s in json.loads(CATALOG.read_text(encoding="utf-8"))["skills"]}


def private_root(path):
    p = Path(path).expanduser().resolve()
    if p.is_relative_to(ROOT) or ROOT.is_relative_to(p):
        raise ValueError("choose a separate private workspace outside the repository")
    return p


def initialize(path, label):
    p = private_root(path)
    if not isinstance(label, str) or not label.strip() or len(label) > 120:
        raise ValueError("short project label required")
    p.mkdir(mode=0o700)
    with closing(sqlite3.connect(p / "workbench.sqlite3")) as db, db:
        db.executescript("""
            CREATE TABLE metadata (project TEXT NOT NULL);
            CREATE TABLE artifacts (
              id INTEGER PRIMARY KEY, kind TEXT NOT NULL, skill TEXT NOT NULL,
              source_ref TEXT NOT NULL, content TEXT NOT NULL,
              dependencies TEXT NOT NULL, created TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE memory (
              id INTEGER PRIMARY KEY, kind TEXT NOT NULL, topic TEXT NOT NULL,
              content TEXT NOT NULL, evidence TEXT NOT NULL,
              basis TEXT NOT NULL, created TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE resolutions (
              retired INTEGER PRIMARY KEY REFERENCES memory(id),
              retained INTEGER NOT NULL REFERENCES memory(id), reason TEXT NOT NULL);
        """)
        db.execute("INSERT INTO metadata VALUES (?)", (label,))
    return p


def connect(path):
    file = private_root(path) / "workbench.sqlite3"
    if file.is_symlink() or not file.is_file():
        raise ValueError("initialize the private workspace first")
    db = sqlite3.connect(file.resolve().as_uri() + "?mode=rw", uri=True)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db


def _text(value, name, limit=MAX_TEXT):
    if not isinstance(value,str) or not value.strip() or len(value)>limit:
        raise ValueError("invalid "+name)
    # Keep credentials out of persistent notes, even in private workspaces.
    if re.search(r"ghp_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{35,}|AIza[A-Za-z0-9_-]{30,}",value):
        raise ValueError("credential-looking value rejected")
    return value.strip()


def _latest(db):
    rows=db.execute("SELECT * FROM artifacts ORDER BY id").fetchall()
    return {r["kind"]:dict(r) for r in rows}


def current_artifacts(db):
    latest=_latest(db)
    def valid(row, seen):
        if row["id"] in seen:
            return False
        deps=json.loads(row["dependencies"])
        return all(k in latest and latest[k]["id"]==ident
                   and valid(latest[k],seen|{row["id"]})
                   for k,ident in deps.items())
    return {k:{**v,"current":valid(v,set())} for k,v in latest.items()}


def _handoff_in_transaction(db, skill, content, source_ref):
    """Internal helper: caller owns BEGIN IMMEDIATE and commit/rollback."""
    if not db.in_transaction:
        raise ValueError("handoff requires an active transaction")
    s=catalog()[skill]
    content=_text(content,"artifact")
    source_ref=_text(source_ref,"source reference",500)
    latest=current_artifacts(db)
    missing=[k for k in s["requires"] if k not in latest or not latest[k]["current"]]
    if missing:
        raise ValueError("missing or stale prerequisite: "+", ".join(missing))
    deps={k:latest[k]["id"] for k in s["requires"]}
    cur=db.execute("INSERT INTO artifacts(kind,skill,source_ref,content,dependencies) VALUES(?,?,?,?,?)",
          (s["produces"],skill,source_ref,content,json.dumps(deps,sort_keys=True)))
    return {"artifact_id":cur.lastrowid,"kind":s["produces"],
            "stored_not_independently_verified":True}


def handoff(path, skill, content, source_ref):
    with closing(connect(path)) as db, db:
        db.execute("BEGIN IMMEDIATE")
        return _handoff_in_transaction(db,skill,content,source_ref)


def remember(path, kind, topic, content, evidence, basis):
    if kind not in KINDS or basis not in ("user-stated","observed","candidate"):
        raise ValueError("invalid memory classification")
    if kind=="preference" and basis not in ("user-stated","candidate"):
        raise ValueError("preference requires actual user statement or candidate status")
    topic=_text(topic,"topic",120)
    content=_text(content,"memory",8000)
    evidence=_text(evidence,"evidence",2000)
    with closing(connect(path)) as db, db:
        db.execute("BEGIN IMMEDIATE")
        row=db.execute("""SELECT id FROM memory WHERE kind=? AND topic=? AND content=?
            AND evidence=? AND basis=? AND id NOT IN (SELECT retired FROM resolutions)""",
            (kind,topic,content,evidence,basis)).fetchone()
        if row:
            return {"memory_id":row[0],"duplicate":True}
        cur=db.execute("INSERT INTO memory(kind,topic,content,evidence,basis) VALUES(?,?,?,?,?)",
                       (kind,topic,content,evidence,basis))
        return {"memory_id":cur.lastrowid,"duplicate":False,
                "basis_is_operator_declared":True}


def active_memory(db):
    return [dict(r) for r in db.execute(
        "SELECT * FROM memory WHERE id NOT IN (SELECT retired FROM resolutions) ORDER BY id")]


def distill(path):
    with closing(connect(path)) as db:
        groups={}
        for row in active_memory(db):
            groups.setdefault((row["kind"],row["topic"]),[]).append(row)
        return {"groups":[{"kind":k[0],"topic":k[1],"entries":v,
                   "review_needed":len(v)>1} for k,v in groups.items()],
                "automatic_changes":False,
                "review_note":"Repeated or conflicting entries need explicit resolution; no latest-date automatic override."}


def resolve(path, retired, retained, reason):
    reason=_text(reason,"user-confirmed resolution reason",2000)
    if retired==retained:
        raise ValueError("different IDs required")
    with closing(connect(path)) as db, db:
        db.execute("BEGIN IMMEDIATE")
        rows={r["id"]:r for r in active_memory(db)}
        if retired not in rows or retained not in rows:
            raise ValueError("both entries must be active")
        a,b=rows[retired],rows[retained]
        if (a["kind"],a["topic"])!=(b["kind"],b["topic"]):
            raise ValueError("resolve within same kind and topic")
        if b["basis"]=="candidate" and a["basis"]!="candidate":
            raise ValueError("candidate cannot replace user-stated or observed memory")
        db.execute("INSERT INTO resolutions VALUES (?,?,?)",(retired,retained,reason))
        return {"retired":retired,"retained":retained,"history_preserved":True}


def context(path, skill, topic=None):
    s=catalog()[skill]
    with closing(connect(path)) as db:
        latest=current_artifacts(db)
        missing=[k for k in s["requires"] if k not in latest or not latest[k]["current"]]
        rows=active_memory(db)
        if topic is not None:
            rows=[r for r in rows if r["topic"]==topic or r["kind"]=="preference"]
        return {"project":db.execute("SELECT project FROM metadata").fetchone()[0],
                "skill":s,"status":"NEEDS_PREREQUISITES" if missing else "READY_TO_REVIEW_INPUTS",
                "missing":missing,"artifacts":latest,
                "memory":rows,"memory_review_recommended":len(rows)>20,
                "authorization_granted":False,"model_or_subagent_invoked":False,
                "instruction":"Read skill file, actual source and artifact contents; user decisions and formal safety rules prevail over notes."}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest="cmd",required=True)
    sub.add_parser("skills")
    for name in ("init","context","handoff","remember","distill","resolve"):
        cmd=sub.add_parser(name)
        cmd.add_argument("--workspace",type=Path,required=True)
        if name=="init": cmd.add_argument("--label",required=True)
        if name in ("context","handoff"): cmd.add_argument("--skill",choices=tuple(catalog()),required=True)
        if name=="context": cmd.add_argument("--topic")
        if name=="handoff":
            cmd.add_argument("--file",type=Path,required=True)
            cmd.add_argument("--source-ref",required=True)
        if name=="remember":
            cmd.add_argument("--kind",choices=KINDS,required=True)
            cmd.add_argument("--topic",required=True)
            cmd.add_argument("--file",type=Path,required=True)
            cmd.add_argument("--evidence",required=True)
            cmd.add_argument("--basis",choices=("user-stated","observed","candidate"),required=True)
        if name=="resolve":
            cmd.add_argument("--retired",type=int,required=True)
            cmd.add_argument("--retained",type=int,required=True)
            cmd.add_argument("--reason",required=True)
            cmd.add_argument("--confirm",action="store_true",required=True)
    a=p.parse_args()
    try:
        if a.cmd=="skills": result=catalog()
        elif a.cmd=="init": result={"workspace":str(initialize(a.workspace,a.label))}
        elif a.cmd=="context": result=context(a.workspace,a.skill,a.topic)
        elif a.cmd=="handoff":
            result=handoff(a.workspace,a.skill,a.file.read_text(encoding="utf-8-sig"),a.source_ref)
        elif a.cmd=="remember":
            result=remember(a.workspace,a.kind,a.topic,a.file.read_text(encoding="utf-8-sig"),a.evidence,a.basis)
        elif a.cmd=="distill": result=distill(a.workspace)
        else: result=resolve(a.workspace,a.retired,a.retained,a.reason)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except (OSError,ValueError,KeyError,sqlite3.Error) as ex:
        print("WORKBENCH_BLOCKED: "+str(ex),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
