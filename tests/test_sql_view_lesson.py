"""Native SQLite view-contract regressions; synthetic, no production data."""
import sqlite3
import unittest


class SQLViewLesson(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)
        self.db.executescript('''
            CREATE TABLE observation(id INTEGER PRIMARY KEY, study TEXT,
                score INTEGER, approved INTEGER, private_note TEXT);
            INSERT INTO observation VALUES
                (1,'A',0,1,'secret-a'),(2,'A',NULL,1,'secret-b'),
                (3,'A',99,0,'secret-c'),(4,'B',80,1,'secret-d');
            CREATE VIEW report_a(id, value) AS
                SELECT id,score FROM observation WHERE study='A' AND approved=1;
        ''')

    def rows(self, sql):
        return self.db.execute(sql).fetchall()

    def columns(self, view):
        return [d[0] for d in self.db.execute('SELECT * FROM ' + view).description]

    def test_live_projection_and_schema_drift(self):
        self.db.execute('CREATE VIEW unsafe_export AS SELECT * FROM observation')
        self.assertEqual(self.columns('report_a'), ['id','value'])
        self.assertEqual(self.rows('SELECT * FROM report_a ORDER BY id'), [(1,0),(2,None)])
        self.db.execute('ALTER TABLE observation ADD COLUMN new_private TEXT')
        self.db.execute("UPDATE observation SET new_private='hidden',score=17 WHERE id=1")
        self.assertIn('new_private', self.columns('unsafe_export'))
        self.assertNotIn('new_private', self.columns('report_a'))
        self.assertEqual(self.rows('SELECT * FROM report_a ORDER BY id'), [(1,17),(2,None)])
        self.db.execute('ALTER TABLE observation RENAME COLUMN score TO raw_score')
        self.assertEqual(self.columns('report_a'), ['id','value'])
        self.assertEqual(self.rows('SELECT * FROM report_a ORDER BY id'), [(1,17),(2,None)])

    def test_read_only_view_does_not_protect_base(self):
        before = self.rows('SELECT * FROM observation ORDER BY id')
        for sql in ("UPDATE report_a SET value=8 WHERE id=1",
                    'DELETE FROM report_a WHERE id=1',
                    'INSERT INTO report_a VALUES (5,9)'):
            with self.assertRaisesRegex(sqlite3.OperationalError, 'cannot modify'):
                self.db.execute(sql)
        self.assertEqual(self.rows('SELECT * FROM observation ORDER BY id'), before)
        self.assertEqual(self.rows('SELECT private_note FROM observation WHERE id=4'), [('secret-d',)])
        self.db.execute('UPDATE observation SET approved=0 WHERE id=1')
        self.assertEqual(self.rows('SELECT * FROM report_a ORDER BY id'), [(2,None)])
        self.assertEqual(self.rows('SELECT COUNT(*) FROM observation'), [(4,)])
        self.assertEqual(self.rows('SELECT COUNT(*), COUNT(value) FROM report_a'), [(1,0)])

    def test_versioned_view_replacement_rollback(self):
        self.db.execute('CREATE VIEW consumer AS SELECT id,value FROM report_a')
        self.db.commit()
        before = self.rows('SELECT * FROM consumer ORDER BY id')
        self.db.execute('BEGIN')
        self.db.execute('DROP VIEW report_a')
        self.db.execute('CREATE VIEW report_a AS SELECT id,score AS renamed FROM observation')
        with self.assertRaisesRegex(sqlite3.OperationalError, 'no such column'):
            self.rows('SELECT * FROM consumer')
        self.db.rollback()
        self.assertEqual(self.rows('SELECT * FROM consumer ORDER BY id'), before)
        self.db.execute('BEGIN')
        self.db.execute('DROP VIEW report_a')
        self.db.execute("CREATE VIEW report_a(id,value) AS SELECT id,score FROM observation WHERE study='A' AND approved=1")
        self.assertEqual(self.columns('consumer'), ['id','value'])
        self.assertEqual(self.rows('SELECT * FROM consumer ORDER BY id'), before)
        self.db.commit()
        self.assertEqual(self.rows('SELECT * FROM consumer ORDER BY id'), [(1,0),(2,None)])


if __name__ == '__main__':
    unittest.main(verbosity=2)
