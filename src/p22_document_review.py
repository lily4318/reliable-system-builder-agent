"""P2-2 controlled transfer: local synthetic document review and publication.

Publication means updating a local pointer, never external release. Actor labels
are trusted test inputs, not authentication. Baseline intentionally ablates
three controls; never use Baseline in a real application.
"""
import argparse
import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path


class ReviewStore:
    def __init__(self,path):
        self.path=Path(path).resolve()

    def connect(self,mode):
        return sqlite3.connect(self.path.as_uri()+'?mode='+mode,uri=True,timeout=5)

    def initialize(self):
        with self.path.open('xb'):
            pass
        with closing(self.connect('rw')) as db, db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('CREATE TABLE versions (revision INTEGER PRIMARY KEY, body TEXT NOT NULL)')
            db.execute('CREATE TABLE state (id INTEGER PRIMARY KEY CHECK(id=1), head INTEGER NOT NULL, published INTEGER)')
            db.execute('CREATE TABLE approvals (revision INTEGER PRIMARY KEY, actor TEXT NOT NULL)')
            db.execute('CREATE TABLE decisions (actor TEXT NOT NULL, token TEXT NOT NULL, payload TEXT NOT NULL, result TEXT NOT NULL, PRIMARY KEY(actor,token))')
            db.execute("INSERT INTO versions VALUES(1,'Synthetic initial text')")
            db.execute('INSERT INTO state VALUES(1,1,NULL)')

    def snapshot(self):
        with closing(self.connect('ro')) as db:
            db.execute('BEGIN')
            head,published=db.execute('SELECT head,published FROM state').fetchone()
            return {'head':head,'published':published,
                    'versions':db.execute('SELECT revision,body FROM versions ORDER BY revision').fetchall(),
                    'approvals':db.execute('SELECT revision,actor FROM approvals ORDER BY revision').fetchall(),
                    'decisions':db.execute('SELECT actor,token,payload,result FROM decisions ORDER BY actor,token').fetchall()}

    def receipt(self,actor,token):
        with closing(self.connect('ro')) as db:
            row=db.execute('SELECT payload,result FROM decisions WHERE actor=? AND token=?',(actor,token)).fetchone()
            return None if row is None else {'payload':json.loads(row[0]),'result':row[1]}

    def _approved(self,db,revision):
        return db.execute('SELECT 1 FROM approvals WHERE revision=?',(revision,)).fetchone() is not None

    def _record(self,result):
        return True

    def _before_receipt(self,db):
        pass

    def action(self,actor,token,operation,expected_revision,body=None,*,fault=False):
        roles={'edit':'editor','approve':'reviewer','publish':'publisher'}
        if roles.get(operation)!=actor or operation not in roles:
            raise PermissionError('operation not permitted')
        if not isinstance(token,str) or not re.fullmatch('[a-f0-9]{32}',token):
            raise ValueError('invalid token')
        if type(expected_revision) is not int or expected_revision<1:
            raise ValueError('invalid revision')
        if operation=='edit':
            if not isinstance(body,str) or not body.strip() or len(body)>2000:
                raise ValueError('invalid text')
        elif body is not None:
            raise ValueError('unexpected body')
        payload=json.dumps([operation,expected_revision,body],ensure_ascii=False,separators=(',',':'))
        with closing(self.connect('rw')) as db, db:
            db.execute('BEGIN IMMEDIATE')
            prior=db.execute('SELECT payload,result FROM decisions WHERE actor=? AND token=?',(actor,token)).fetchone()
            if prior:
                if prior[0]!=payload:
                    raise ValueError('token conflict')
                return prior[1]
            head,published=db.execute('SELECT head,published FROM state').fetchone()
            if head!=expected_revision:
                result='STALE'
            elif operation=='edit':
                db.execute('INSERT INTO versions VALUES(?,?)',(head+1,body))
                db.execute('UPDATE state SET head=? WHERE id=1',(head+1,))
                result='EDITED'
            elif operation=='approve':
                db.execute('INSERT OR IGNORE INTO approvals VALUES(?,?)',(head,actor))
                result='APPROVED'
            elif not self._approved(db,head):
                result='UNAPPROVED'
            else:
                db.execute('UPDATE state SET published=? WHERE id=1',(head,))
                result='PUBLISHED'
            self._before_receipt(db)
            if fault:
                raise RuntimeError('synthetic interruption before receipt')
            if self._record(result):
                db.execute('INSERT INTO decisions VALUES(?,?,?,?)',(actor,token,payload,result))
            return result


class Baseline(ReviewStore):
    """Explicit controlled ablation; preserves happy-path and actor checks.

    Not an independently produced no-memory agent answer.
    """
    def _approved(self,db,revision):
        return db.execute('SELECT 1 FROM approvals LIMIT 1').fetchone() is not None

    def _record(self,result):
        return result not in ('STALE','UNAPPROVED')

    def _before_receipt(self,db):
        db.commit()  # intentionally unsafe split transaction for comparison


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('init','snapshot','receipt','action'))
    parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--input',type=Path)
    args=parser.parse_args()
    store=ReviewStore(args.database)
    try:
        data=json.loads(args.input.read_text(encoding='utf-8')) if args.input else {}
        if not isinstance(data,dict) or 'fault' in data:
            raise ValueError('invalid CLI input')
        if args.command=='init':
            if data: raise ValueError('unexpected input')
            store.initialize()
            result={'initialized':True}
        else:
            result=getattr(store,args.command)(**data)
        print(json.dumps(result,ensure_ascii=False))
    except (ValueError,TypeError,PermissionError,OSError,sqlite3.Error) as error:
        parser.exit(2,'REVIEW_BLOCKED: '+str(error)+'\n')


if __name__=='__main__':
    main()
