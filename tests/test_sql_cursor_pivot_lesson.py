import sqlite3
import unittest


class CursorPivotLesson(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)

    def test_cursor_order_and_running_total(self):
        d = self.db
        d.execute('CREATE TABLE event(id INTEGER PRIMARY KEY, tick INTEGER, amount INTEGER)')
        d.executemany('INSERT INTO event VALUES(?,?,?)', [(1,2,7),(2,1,6),(3,1,5),(4,2,-4)])
        # Stateful decisions: threshold crossings, with deterministic tie order.
        def crossings(cursor):
            total = 0
            out = []
            try:
                for key, amount in cursor:
                    previous, total = total, total + amount
                    if previous < 10 <= total:
                        out.append(key)
            finally:
                cursor.close()
            return out
        self.assertEqual(crossings(d.execute('SELECT id, amount FROM event ORDER BY tick,id')), [3])
        self.assertEqual(crossings(d.execute('SELECT id, amount FROM event ORDER BY tick,id DESC')), [2,1])
        query = '''WITH running AS (
          SELECT id,tick,SUM(amount) OVER (ORDER BY tick,id ROWS UNBOUNDED PRECEDING) AS balance FROM event
        ), prior AS (
          SELECT id,tick,balance,LAG(balance,1,0) OVER (ORDER BY tick,id) AS prev FROM running
        ) SELECT id FROM prior WHERE prev < 10 AND balance >= 10 ORDER BY tick,id'''
        self.assertEqual(d.execute(query).fetchall(), [(3,)])
        # Default RANGE treats peers together; it is NOT a row-ordered running total.
        self.assertEqual(d.execute('SELECT id,SUM(amount) OVER (ORDER BY tick) FROM event ORDER BY tick,id').fetchall(), [(2,11),(3,11),(1,14),(4,14)])
        self.assertEqual(d.execute('SELECT id,SUM(amount) OVER (ORDER BY tick,id ROWS UNBOUNDED PRECEDING) FROM event ORDER BY tick,id').fetchall(), [(2,6),(3,11),(1,18),(4,14)])
        self.assertEqual(d.execute('SELECT id,amount FROM event ORDER BY id').fetchall(), [(1,7),(2,6),(3,5),(4,-4)])

    def test_cursor_reexecution_and_query_count(self):
        d = self.db
        d.execute('CREATE TABLE person(id INTEGER PRIMARY KEY)')
        d.execute('CREATE TABLE score(pid INTEGER, value INTEGER)')
        d.executemany('INSERT INTO person VALUES(?)', [(i,) for i in range(1,101)])
        d.executemany('INSERT INTO score VALUES(?,?)', [(1,0),(2,None),(3,7),(3,7)])
        cur = d.cursor()
        bad = []
        for (pid,) in cur.execute('SELECT id FROM person ORDER BY id'):
            bad.append((pid,cur.execute('SELECT count(*) FROM score WHERE pid=?',(pid,)).fetchone()[0]))
        cur.close()
        self.assertEqual(bad, [(1,1)])
        traces = []
        d.set_trace_callback(traces.append)
        try:
            with_rows = [(pid,*d.execute('SELECT count(*),count(value),sum(value) FROM score WHERE pid=?',(pid,)).fetchone()) for (pid,) in d.execute('SELECT id FROM person ORDER BY id')]
            self.assertEqual(len(traces), 101)
            traces.clear()
            set_rows = d.execute('''SELECT p.id,count(s.pid),count(s.value),sum(s.value) FROM person p LEFT JOIN score s ON p.id=s.pid GROUP BY p.id ORDER BY p.id''').fetchall()
            self.assertEqual(len(traces), 1)
        finally:
            d.set_trace_callback(None)
        expected = [(1,1,1,0),(2,1,0,None),(3,2,2,14)] + [(i,0,0,None) for i in range(4,101)]
        self.assertEqual(with_rows, expected)
        self.assertEqual(set_rows, expected)

    def test_pivot_missing_multiplicity_and_schema(self):
        d = self.db
        d.execute('CREATE TABLE trial(id INTEGER PRIMARY KEY,pid INTEGER,phase TEXT,value INTEGER)')
        rows = [(1,1,'pre',0),(2,1,'post',10),(3,1,'post',10),(4,2,'pre',None),(5,3,'post',0),(6,4,'extra',5)]
        d.executemany('INSERT INTO trial VALUES(?,?,?,?)',rows)
        def report(phases):
            allowed = {'pre','post','followup'}
            if not phases or len(set(phases)) != len(phases) or not set(phases) <= allowed:
                raise ValueError('unapproved/duplicate phase')
            fields, args = [], []
            for phase in phases:
                for expr, suffix in [('count(*) FILTER(WHERE phase=?)','rows'),('count(value) FILTER(WHERE phase=?)','valid'),('sum(value) FILTER(WHERE phase=?)','sum')]:
                    fields.append(f'{expr} AS "{phase}_{suffix}"')
                    args.append(phase)
            cur = d.execute('SELECT pid,'+','.join(fields)+' FROM trial GROUP BY pid ORDER BY pid',args)
            return [x[0] for x in cur.description],cur.fetchall()
        phases = ['pre','post','followup']
        headers, result = report(phases)
        self.assertEqual(headers,['pid','pre_rows','pre_valid','pre_sum','post_rows','post_valid','post_sum','followup_rows','followup_valid','followup_sum'])
        self.assertEqual(result,[(1,1,1,0,2,2,20,0,0,None),(2,1,0,None,0,0,None,0,0,None),(3,0,0,None,1,1,0,0,0,None),(4,0,0,None,0,0,None,0,0,None)])
        self.assertEqual(d.execute('SELECT phase,count(*) FROM trial WHERE phase NOT IN (?,?,?) GROUP BY phase',phases).fetchall(), [('extra',1)])
        self.assertEqual(d.execute("SELECT pid,sum(CASE WHEN phase='pre' THEN coalesce(value,0) ELSE 0 END) FROM trial GROUP BY pid ORDER BY pid").fetchall(),[(1,0),(2,0),(3,0),(4,0)])
        self.assertEqual(d.execute("SELECT sum(DISTINCT value),sum(value) FROM trial WHERE pid=1 AND phase='post'").fetchone(),(10,20))
        for invalid in [[],['pre','pre'],['extra'],['x\"; DROP TABLE trial;--']]:
            with self.assertRaises(ValueError):
                report(invalid)
        self.assertEqual(report(['post','pre'])[0],['pid','post_rows','post_valid','post_sum','pre_rows','pre_valid','pre_sum'])
        # Aggregation is lossy: unpivoting the single sum cannot recover trial IDs or repeated values.
        self.assertEqual(d.execute("SELECT count(*),sum(value) FROM trial WHERE pid=1 AND phase='post'").fetchone(),(2,20))
        self.assertEqual(d.execute('SELECT * FROM trial ORDER BY id').fetchall(),rows)


if __name__ == '__main__':
    print('SQLite', sqlite3.sqlite_version)
    unittest.main(verbosity=2)
