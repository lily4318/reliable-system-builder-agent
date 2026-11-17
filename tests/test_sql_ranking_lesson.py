import sqlite3
import unittest


class RankingLesson(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)

    def test_ties_top_n_and_stable_order(self):
        d = self.db
        d.execute('CREATE TABLE scores(pid INTEGER PRIMARY KEY,score INTEGER)')
        d.executemany('INSERT INTO scores VALUES(?,?)', [(1,100),(2,90),(3,90),(4,80),(5,70)])
        d.execute('CREATE INDEX forward_idx ON scores(score DESC,pid ASC)')
        d.execute('CREATE INDEX reverse_idx ON scores(score DESC,pid DESC)')
        def top(index, stable):
            order = 'score DESC,pid' if stable else 'score DESC'
            return d.execute(f'SELECT pid FROM (SELECT pid, row_number() OVER(ORDER BY {order}) AS rn FROM scores INDEXED BY {index}) WHERE rn<=2 ORDER BY rn').fetchall()
        self.assertEqual(top('forward_idx',False),[(1,),(2,)])
        self.assertEqual(top('reverse_idx',False),[(1,),(3,)])
        self.assertEqual(top('forward_idx',True),[(1,),(2,)])
        self.assertEqual(top('reverse_idx',True),[(1,),(2,)])
        ranked = '''SELECT pid,score,row_number() OVER(ORDER BY score DESC,pid) rn,
            rank() OVER(ORDER BY score DESC) r,dense_rank() OVER(ORDER BY score DESC) dr FROM scores'''
        self.assertEqual(d.execute(ranked+' ORDER BY rn').fetchall(),[(1,100,1,1,1),(2,90,2,2,2),(3,90,3,2,2),(4,80,4,4,3),(5,70,5,5,4)])
        self.assertEqual(d.execute('SELECT pid FROM ('+ranked+') WHERE r<=3 ORDER BY rn').fetchall(),[(1,),(2,),(3,)])
        self.assertEqual(d.execute('SELECT pid FROM ('+ranked+') WHERE dr<=3 ORDER BY rn').fetchall(),[(1,),(2,),(3,),(4,)])
        self.assertEqual(d.execute('SELECT pid FROM ('+ranked+') WHERE r<=2 ORDER BY rn').fetchall(),[(1,),(2,),(3,)])
        self.assertEqual(d.execute('SELECT pid,rank() OVER(ORDER BY score DESC,pid) FROM scores ORDER BY pid').fetchall(),[(1,1),(2,2),(3,3),(4,4),(5,5)])
        self.assertEqual(d.execute('SELECT count(*) FROM scores').fetchone(),(5,))

    def test_partition_eligibility_and_analysis_population(self):
        d=self.db
        d.execute('CREATE TABLE measures(study TEXT,arm TEXT,pid INTEGER,score INTEGER,eligible INTEGER,PRIMARY KEY(study,arm,pid))')
        rows=[('A','X',1,90,1),('A','X',2,80,1),('A','X',3,None,1),('A','X',4,100,0),('A','Y',1,70,1),('A','Y',2,0,1),('B','X',1,99,1)]
        d.executemany('INSERT INTO measures VALUES(?,?,?,?,?)',rows)
        q='''SELECT study,arm,pid,score,rank() OVER(PARTITION BY study,arm ORDER BY score DESC) r
            FROM measures WHERE eligible=1 AND score IS NOT NULL'''
        self.assertEqual(d.execute(q+' ORDER BY study,arm,r,pid').fetchall(),[('A','X',1,90,1),('A','X',2,80,2),('A','Y',1,70,1),('A','Y',2,0,2),('B','X',1,99,1)])
        late='''SELECT pid,r FROM (SELECT *,rank() OVER(PARTITION BY study,arm ORDER BY score DESC) r FROM measures) WHERE study='A' AND arm='X' AND eligible=1 AND score IS NOT NULL ORDER BY pid'''
        self.assertEqual(d.execute(late).fetchall(),[(1,2),(2,3)])
        self.assertEqual(d.execute("SELECT study,pid,r FROM (SELECT *,rank() OVER(PARTITION BY arm ORDER BY score DESC) r FROM measures WHERE eligible=1 AND score IS NOT NULL) WHERE study='A' AND arm='X' ORDER BY pid").fetchall(),[('A',1,2),('A',2,3)])
        self.assertEqual(d.execute("SELECT pid,rank() OVER(ORDER BY coalesce(score,0)) FROM measures WHERE study='A' AND eligible=1 ORDER BY arm,pid").fetchall(),[(1,5),(2,4),(3,1),(1,3),(2,1)])
        self.assertEqual(d.execute("SELECT count(*),count(score) FROM measures WHERE study='A' AND eligible=1").fetchone(),(5,4))
        self.assertEqual(d.execute('SELECT * FROM measures ORDER BY study,arm,pid').fetchall(),rows)

    def test_ntile_ties_and_small_partitions(self):
        d=self.db
        d.execute('CREATE TABLE scores(g TEXT,pid INTEGER,score INTEGER,PRIMARY KEY(g,pid))')
        rows=[('A',i,s) for i,s in enumerate([100,90,90,90,80,70,60,50,40,30],1)]+[('B',1,50),('B',2,50)]
        d.executemany('INSERT INTO scores VALUES(?,?,?)',rows)
        q='SELECT g,pid,score,ntile(4) OVER(PARTITION BY g ORDER BY score DESC,pid) tile FROM scores'
        self.assertEqual(d.execute('SELECT g,tile,count(*) FROM ('+q+') GROUP BY g,tile ORDER BY g,tile').fetchall(),[('A',1,3),('A',2,3),('A',3,2),('A',4,2),('B',1,1),('B',2,1)])
        self.assertEqual(d.execute("SELECT pid,tile FROM ("+q+") WHERE g='A' AND score=90 ORDER BY pid").fetchall(),[(2,1),(3,1),(4,2)])
        self.assertEqual(d.execute("SELECT pid,tile FROM ("+q+") WHERE g='B' ORDER BY pid").fetchall(),[(1,1),(2,2)])
        self.assertEqual(d.execute("SELECT pid,rank() OVER(ORDER BY score DESC) FROM scores WHERE g='B' ORDER BY pid").fetchall(),[(1,1),(2,1)])
        with self.assertRaises(sqlite3.OperationalError):
            d.execute('SELECT ntile(0) OVER(ORDER BY score) FROM scores').fetchall()
        self.assertEqual(d.execute('SELECT * FROM scores ORDER BY g,pid').fetchall(),rows)


if __name__ == '__main__':
    print('SQLite',sqlite3.sqlite_version)
    unittest.main(verbosity=2)
