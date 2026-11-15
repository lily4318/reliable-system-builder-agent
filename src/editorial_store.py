"""WEB-EDITORIAL-01: local synthetic editorial workflow, never a public service."""
from contextlib import closing
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import time

CATEGORIES = ('生活','文化','科技')
ROLES = {'author-a':'author','author-b':'author','editor':'editor'}
OPEN = ('DRAFT','SUBMITTED','RETURNED','APPROVED')
SESSION_SECONDS = 1800
VERSION = 1
TOKEN = re.compile(r'[a-f0-9]{64}')
ACTION_TOKEN = re.compile(r'[a-f0-9]{32}')
SCHEMA = """
CREATE TABLE accounts(id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('author','editor')), salt BLOB NOT NULL,
  password_hash BLOB NOT NULL, active INTEGER NOT NULL CHECK(active IN (0,1)));
CREATE TABLE sessions(token_hash TEXT PRIMARY KEY, account_id INTEGER NOT NULL REFERENCES accounts(id),
  expires INTEGER NOT NULL);
CREATE TABLE articles(id INTEGER PRIMARY KEY, owner INTEGER NOT NULL REFERENCES accounts(id),
  version INTEGER NOT NULL CHECK(version>=1), published_revision_id INTEGER,
  FOREIGN KEY(id,published_revision_id) REFERENCES article_revisions(article_id,id));
CREATE TABLE article_revisions(id INTEGER PRIMARY KEY, article_id INTEGER NOT NULL REFERENCES articles(id),
  revision_no INTEGER NOT NULL CHECK(revision_no>=1), title TEXT NOT NULL, category TEXT NOT NULL,
  body TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN
  ('DRAFT','SUBMITTED','RETURNED','APPROVED','PUBLISHED','SUPERSEDED','WITHDRAWN')),
  reason TEXT NOT NULL DEFAULT '', created INTEGER NOT NULL, updated INTEGER NOT NULL,
  UNIQUE(article_id,revision_no), UNIQUE(article_id,id));
CREATE UNIQUE INDEX one_open ON article_revisions(article_id)
  WHERE status IN ('DRAFT','SUBMITTED','RETURNED','APPROVED');
CREATE UNIQUE INDEX one_public ON article_revisions(article_id) WHERE status='PUBLISHED';
CREATE TABLE action_receipts(actor INTEGER NOT NULL REFERENCES accounts(id), token TEXT NOT NULL,
  payload_hash TEXT NOT NULL, result TEXT NOT NULL, PRIMARY KEY(actor,token));
CREATE TABLE audit_events(id INTEGER PRIMARY KEY, actor INTEGER NOT NULL REFERENCES accounts(id),
  article_id INTEGER NOT NULL REFERENCES articles(id), revision_id INTEGER NOT NULL REFERENCES article_revisions(id),
  action TEXT NOT NULL, before_state TEXT, after_state TEXT NOT NULL, article_version INTEGER NOT NULL,
  at INTEGER NOT NULL);
PRAGMA user_version=1;
"""


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def password_hash(password, salt):
    return hashlib.pbkdf2_hmac('sha256',password.encode('utf-8'),salt,600000)


def bounded_text(value, limit):
    if (not isinstance(value,str) or not value.strip() or len(value)>limit
        or '\x00' in value or any(0xd800<=ord(c)<=0xdfff for c in value)):
        raise ValueError('invalid text length/content')
    return value


def content(payload):
    title=bounded_text(payload['title'],120)
    body=bounded_text(payload['body'],10000)
    category=payload['category']
    if category not in CATEGORIES:
        raise ValueError('invalid category')
    return title,category,body


def valid_action(payload):
    if not isinstance(payload,dict):
        raise ValueError('invalid action')
    op=payload.get('op')
    token=payload.get('token')
    if not isinstance(token,str) or not ACTION_TOKEN.fullmatch(token):
        raise ValueError('invalid action token')
    if not isinstance(op,str) or op not in ('create','edit','submit','return','approve','publish','clone','withdraw'):
        raise ValueError('invalid operation')
    keys={'op','token'}
    if op!='create':
        keys|={'article_id','revision_id','expected'}
    if op in ('create','edit'):
        keys|={'title','category','body'}
    if op=='return':
        keys.add('reason')
    if set(payload)!=keys:
        raise ValueError('unexpected/missing action field')
    for key in ('article_id','revision_id','expected'):
        if key in payload and (type(payload[key]) is not int or not 0<payload[key]<2**63):
            raise ValueError('invalid revision/id')
    if op in ('create','edit'):
        content(payload)
    if op=='return':
        bounded_text(payload['reason'],500)
    return op


class Store:
    def __init__(self,path):
        self.path=Path(path).resolve()

    def connect(self,mode):
        db=sqlite3.connect(self.path.as_uri()+'?mode='+mode,uri=True,timeout=5)
        db.row_factory=sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        if mode=='ro':
            db.execute('PRAGMA query_only=ON')
        return db

    def current(self,db):
        if db.execute('PRAGMA user_version').fetchone()[0]!=VERSION:
            raise sqlite3.DatabaseError('wrong schema version')
        tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if tables!={'accounts','sessions','articles','article_revisions','action_receipts','audit_events'}:
            raise sqlite3.DatabaseError('wrong database schema')

    @staticmethod
    def exclusive(path):
        fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        os.close(fd)

    def initialize(self,passwords):
        if not isinstance(passwords,dict) or set(passwords)!=set(ROLES):
            raise ValueError('three synthetic accounts required')
        for v in passwords.values():
            bounded_text(v,128)
            if len(v)<12:
                raise ValueError('password min 12 characters')
        self.exclusive(self.path)
        with closing(self.connect('rw')) as db, db:
            db.executescript('BEGIN IMMEDIATE;'+SCHEMA)
            for username,role in ROLES.items():
                salt=secrets.token_bytes(16)
                db.execute('INSERT INTO accounts(username,role,salt,password_hash,active) VALUES(?,?,?,?,1)',
                           (username,role,salt,password_hash(passwords[username],salt)))

    def verify(self):
        with closing(self.connect('ro')) as db:
            self.current(db)
            if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchone():
                raise sqlite3.DatabaseError('database integrity failure')

    def transfer(self,target,*,restore=False):
        dst=Store(target)
        self.verify()
        self.exclusive(dst.path)
        with closing(self.connect('ro')) as src, closing(dst.connect('rw')) as out:
            src.backup(out)
            if restore:
                with out:
                    out.execute('DELETE FROM sessions')
        dst.verify()

    def login(self,username,password,previous=None):
        bounded_text(username,80)
        bounded_text(password,128)
        with closing(self.connect('rw')) as db, db:
            db.execute('BEGIN IMMEDIATE')
            self.current(db)
            account=db.execute('SELECT * FROM accounts WHERE username=? AND active=1',(username,)).fetchone()
            salt=account['salt'] if account else b'\0'*16
            candidate=password_hash(password,salt)
            if not account or not hmac.compare_digest(candidate,account['password_hash']):
                return None
            if isinstance(previous,str) and TOKEN.fullmatch(previous):
                db.execute('DELETE FROM sessions WHERE token_hash=?',(digest(previous),))
            db.execute('DELETE FROM sessions WHERE expires<=?',(int(time.time()),))
            token=secrets.token_hex(32)
            db.execute('INSERT INTO sessions VALUES(?,?,?)',
                       (digest(token),account['id'],int(time.time())+SESSION_SECONDS))
            return token

    def _actor(self,db,token):
        if not isinstance(token,str) or not TOKEN.fullmatch(token):
            raise PermissionError('authentication required')
        row=db.execute("""SELECT a.id,a.username,a.role FROM accounts a JOIN sessions s ON a.id=s.account_id
                          WHERE s.token_hash=? AND s.expires>? AND a.active=1""",
                       (digest(token),int(time.time()))).fetchone()
        if row is None:
            raise PermissionError('authentication required')
        return row

    def actor(self,token):
        with closing(self.connect('ro')) as db:
            self.current(db)
            return dict(self._actor(db,token))

    def logout(self,token):
        with closing(self.connect('rw')) as db, db:
            db.execute('BEGIN IMMEDIATE')
            self.current(db)
            self._actor(db,token)
            db.execute('DELETE FROM sessions WHERE token_hash=?',(digest(token),))

    def public_list(self,query='',category='',page=1):
        if (not isinstance(query,str) or len(query)>120 or not isinstance(category,str)
            or category not in ('',*CATEGORIES) or type(page) is not int or not 1<=page<=1_000_000):
            raise ValueError('invalid search')
        with closing(self.connect('ro')) as db:
            self.current(db)
            db.execute('BEGIN')
            where="""FROM articles a JOIN article_revisions r
                    ON r.id=a.published_revision_id AND r.article_id=a.id
                    WHERE r.status='PUBLISHED' AND instr(lower(r.title),lower(?))>0
                    AND (?='' OR r.category=?)"""
            # instr(X,'')=1, so empty query lists all.
            args=(query,category,category)
            total=db.execute('SELECT count(*) '+where,args).fetchone()[0]
            rows=db.execute('SELECT a.id,r.title,r.category '+where+
                            ' ORDER BY a.id DESC LIMIT 20 OFFSET ?',(*args,(page-1)*20)).fetchall()
            return {'items':[dict(r) for r in rows],'page':page,'total':total}

    def public_detail(self,article_id):
        with closing(self.connect('ro')) as db:
            self.current(db)
            row=db.execute("""SELECT a.id,r.title,r.category,r.body FROM articles a
              JOIN article_revisions r ON a.published_revision_id=r.id AND r.article_id=a.id
              WHERE a.id=? AND r.status='PUBLISHED'""",(article_id,)).fetchone()
            return dict(row) if row else None

    def workspace(self,token):
        with closing(self.connect('ro')) as db:
            self.current(db)
            db.execute('BEGIN')
            actor=self._actor(db,token)
            if actor['role']=='author':
                where,args='a.owner=?',(actor['id'],)
            else:
                where,args="r.status!='DRAFT'",()
            rows=db.execute("""SELECT r.*, a.version, a.published_revision_id, ac.username AS owner
                   FROM article_revisions r JOIN articles a ON a.id=r.article_id
                   JOIN accounts ac ON ac.id=a.owner WHERE """+where+
                   ' ORDER BY r.article_id DESC,r.revision_no DESC',args).fetchall()
            events=db.execute("""SELECT e.id,e.article_id,e.revision_id,e.action,e.before_state,e.after_state,
                         e.article_version,e.at,ac.username AS actor
                         FROM audit_events e JOIN article_revisions r ON r.id=e.revision_id
                         JOIN articles a ON a.id=e.article_id JOIN accounts ac ON ac.id=e.actor
                         WHERE """+where+' ORDER BY e.id DESC',args).fetchall()
            return {'actor':dict(actor),'revisions':[dict(r) for r in rows],
                    'events':[dict(r) for r in events]}

    def receipt(self,session,token):
        if not isinstance(token,str) or not ACTION_TOKEN.fullmatch(token):
            raise ValueError('invalid action token')
        with closing(self.connect('ro')) as db:
            self.current(db)
            db.execute('BEGIN')
            actor=self._actor(db,session)
            row=db.execute('SELECT result FROM action_receipts WHERE actor=? AND token=?',
                           (actor['id'],token)).fetchone()
            return {'observed':bool(row),'result':json.loads(row[0]) if row else None}

    def action(self,session,payload,*,fault=False):
        op=valid_action(payload)
        fingerprint=digest(json.dumps(payload,sort_keys=True,ensure_ascii=True,separators=(',',':')))
        with closing(self.connect('rw')) as db, db:
            db.execute('BEGIN IMMEDIATE')
            self.current(db)
            actor=self._actor(db,session)
            prior=db.execute('SELECT payload_hash,result FROM action_receipts WHERE actor=? AND token=?',
                             (actor['id'],payload['token'])).fetchone()
            if prior:
                return json.loads(prior['result']) if prior['payload_hash']==fingerprint else {'ok':False,'code':'TOKEN_CONFLICT'}
            result=self._change(db,actor,op,payload)
            if fault:
                raise RuntimeError('synthetic fault before receipt')
            db.execute('INSERT INTO action_receipts VALUES(?,?,?,?)',
                       (actor['id'],payload['token'],fingerprint,json.dumps(result,separators=(',',':'))))
            return result

    def _change(self,db,actor,op,p):
        def deny(code):
            return {'ok':False,'code':code}
        role='author' if op in ('create','edit','submit','clone') else 'editor'
        if actor['role']!=role:
            return deny('FORBIDDEN')
        now=int(time.time())
        before=None
        if op=='create':
            aid=db.execute('INSERT INTO articles(owner,version) VALUES(?,1)',(actor['id'],)).lastrowid
            rid=db.execute("""INSERT INTO article_revisions(article_id,revision_no,title,category,body,status,created,updated)
                            VALUES(?,1,?,?,?,'DRAFT',?,?)""",(aid,*content(p),now,now)).lastrowid
            version=1
            after='DRAFT'
        else:
            aid,rid=p['article_id'],p['revision_id']
            a=db.execute('SELECT * FROM articles WHERE id=?',(aid,)).fetchone()
            r=db.execute('SELECT * FROM article_revisions WHERE id=? AND article_id=?',(rid,aid)).fetchone()
            if not a or not r or (role=='author' and a['owner']!=actor['id']) or (role=='editor' and r['status']=='DRAFT'):
                return deny('NOT_FOUND')
            if a['version']!=p['expected']:
                return deny('STALE')
            before=r['status']
            target={'edit':('DRAFT','RETURNED'),'submit':('DRAFT',),'return':('SUBMITTED',),
                    'approve':('SUBMITTED',),'publish':('APPROVED',),'clone':('PUBLISHED','WITHDRAWN'),
                    'withdraw':('PUBLISHED',)}[op]
            if before not in target:
                return deny('INVALID_STATE')
            version=a['version']+1
            if op=='clone':
                if db.execute("""SELECT 1 FROM article_revisions WHERE article_id=? AND
                               status IN ('DRAFT','SUBMITTED','RETURNED','APPROVED')""",(aid,)).fetchone():
                    return deny('OPEN_REVISION')
                latest=db.execute('SELECT max(revision_no) FROM article_revisions WHERE article_id=?',(aid,)).fetchone()[0]
                if r['revision_no']!=latest:
                    return deny('INVALID_STATE')
                rid=db.execute("""INSERT INTO article_revisions(article_id,revision_no,title,category,body,status,created,updated)
                                 VALUES(?,?,?,?,?,'DRAFT',?,?)""",(aid,latest+1,r['title'],r['category'],r['body'],now,now)).lastrowid
                after='DRAFT'
                before=None
            elif op=='edit':
                after='DRAFT'
                db.execute("UPDATE article_revisions SET title=?,category=?,body=?,status='DRAFT',reason='',updated=? WHERE id=?",
                           (*content(p),now,rid))
            elif op=='publish':
                after='PUBLISHED'
                old=a['published_revision_id']
                if old is not None:
                    db.execute("UPDATE article_revisions SET status='SUPERSEDED',updated=? WHERE id=? AND article_id=?",(now,old,aid))
                    self._audit(db,actor['id'],aid,old,'supersede','PUBLISHED','SUPERSEDED',version,now)
                db.execute("UPDATE article_revisions SET status='PUBLISHED',updated=? WHERE id=?",(now,rid))
                db.execute('UPDATE articles SET published_revision_id=? WHERE id=?',(rid,aid))
            elif op=='withdraw':
                if a['published_revision_id']!=rid:
                    return deny('INVALID_STATE')
                after='WITHDRAWN'
                db.execute("UPDATE article_revisions SET status='WITHDRAWN',updated=? WHERE id=?",(now,rid))
                db.execute('UPDATE articles SET published_revision_id=NULL WHERE id=?',(aid,))
            else:
                after={'submit':'SUBMITTED','return':'RETURNED','approve':'APPROVED'}[op]
                db.execute('UPDATE article_revisions SET status=?,reason=?,updated=? WHERE id=?',
                           (after,p.get('reason',''),now,rid))
            db.execute('UPDATE articles SET version=? WHERE id=?',(version,aid))
        self._audit(db,actor['id'],aid,rid,op,before,after,version,now)
        return {'ok':True,'code':'COMMITTED','article_id':aid,'revision_id':rid,'version':version,'state':after}

    @staticmethod
    def _audit(db,actor,aid,rid,op,before,after,version,now):
        db.execute("""INSERT INTO audit_events(actor,article_id,revision_id,action,before_state,after_state,article_version,at)
                      VALUES(?,?,?,?,?,?,?,?)""",(actor,aid,rid,op,before,after,version,now))
