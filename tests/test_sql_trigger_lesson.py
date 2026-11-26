"""Native SQLite trigger regressions; synthetic data only."""
import sqlite3
import unittest


class SQLTriggerLesson(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)
        self.db.execute('PRAGMA recursive_triggers=ON')

    def rows(self, sql):
        return self.db.execute(sql).fetchall()

    def test_multirow_delta_and_audit(self):
        self.db.executescript('''
            CREATE TABLE total(grp TEXT PRIMARY KEY, n INTEGER NOT NULL);
            INSERT INTO total VALUES ('A',30),('B',7);
            CREATE TABLE item(id INTEGER PRIMARY KEY, grp TEXT, amount INTEGER);
            INSERT INTO item VALUES (1,'A',10),(2,'A',20),(3,'B',7);
            CREATE TABLE audit(id INTEGER, old_grp TEXT, new_grp TEXT, old_n INTEGER, new_n INTEGER);
            CREATE TRIGGER wrong AFTER UPDATE OF grp,amount ON item BEGIN
                UPDATE total SET n=n+NEW.amount WHERE grp=NEW.grp;
            END;
        ''')
        self.db.execute('UPDATE item SET amount=amount+1 WHERE grp=\'A\'')
        self.assertEqual(self.rows('SELECT * FROM total ORDER BY grp'), [('A',62),('B',7)])
        self.db.rollback()
        self.db.executescript('''
            DROP TRIGGER wrong;
            CREATE TRIGGER delta AFTER UPDATE OF grp,amount ON item
            WHEN OLD.grp IS NOT NEW.grp OR OLD.amount IS NOT NEW.amount BEGIN
                UPDATE total SET n=n-OLD.amount WHERE grp=OLD.grp;
                UPDATE total SET n=n+NEW.amount WHERE grp=NEW.grp;
                INSERT INTO audit VALUES(NEW.id,OLD.grp,NEW.grp,OLD.amount,NEW.amount);
            END;
        ''')
        self.db.execute("UPDATE item SET grp='B',amount=amount+1 WHERE grp='A'")
        self.assertEqual(self.rows('SELECT * FROM total ORDER BY grp'), [('A',0),('B',39)])
        self.assertEqual(self.rows('SELECT * FROM audit ORDER BY id'), [(1,'A','B',10,11),(2,'A','B',20,21)])
        self.assertEqual(self.rows('SELECT grp,SUM(amount) FROM item GROUP BY grp'), [('B',39)])
        self.db.execute('UPDATE item SET amount=amount')
        self.assertEqual(self.rows('SELECT COUNT(*) FROM audit'), [(2,)])
        self.db.commit()
        self.assertEqual(self.rows('SELECT * FROM total ORDER BY grp'), [('A',0),('B',39)])

    def test_recursion_limit_and_convergence(self):
        self.db.executescript('''
            CREATE TABLE counter(id INTEGER PRIMARY KEY, n INTEGER);
            INSERT INTO counter VALUES (1,0);
            CREATE TABLE trace(n INTEGER);
            CREATE TRIGGER loop AFTER UPDATE OF n ON counter BEGIN
                INSERT INTO trace VALUES(NEW.n);
                UPDATE counter SET n=NEW.n+1 WHERE id=NEW.id;
            END;
        ''')
        self.db.setlimit(sqlite3.SQLITE_LIMIT_TRIGGER_DEPTH, 8)
        with self.assertRaisesRegex(sqlite3.OperationalError, 'too many levels'):
            self.db.execute('UPDATE counter SET n=1 WHERE id=1')
        self.assertTrue(self.db.in_transaction)
        self.assertEqual(self.rows('SELECT n FROM counter'), [(9,)])
        self.assertEqual(self.rows('SELECT n FROM trace ORDER BY rowid'), [(i,) for i in range(1,9)])
        self.db.rollback()
        self.assertEqual(self.rows('SELECT n FROM counter'), [(0,)])
        self.assertEqual(self.rows('SELECT * FROM trace'), [])
        self.db.executescript('''
            DROP TRIGGER loop;
            CREATE TRIGGER bounded AFTER UPDATE OF n ON counter
            WHEN NEW.n<3 AND NEW.n IS NOT OLD.n BEGIN
                INSERT INTO trace VALUES(NEW.n);
                UPDATE counter SET n=NEW.n+1 WHERE id=NEW.id;
            END;
        ''')
        self.db.execute('UPDATE counter SET n=1 WHERE id=1')
        self.assertEqual(self.rows('SELECT n FROM counter'), [(3,)])
        self.assertEqual(self.rows('SELECT n FROM trace ORDER BY rowid'), [(1,),(2,)])
        self.db.execute('UPDATE counter SET n=n WHERE id=1')
        self.assertEqual(self.rows('SELECT COUNT(*) FROM trace'), [(2,)])

    def test_nested_failure_scope_and_transaction(self):
        for mode, expected_items, expected_audit, active in (
            ('FAIL', [(1,),(2,)], [(1,),(2,)], True),
            ('ABORT', [], [], True),
            ('ROLLBACK', [], [], False),
        ):
            with self.subTest(mode=mode):
                db=sqlite3.connect(':memory:')
                self.addCleanup(db.close)
                db.executescript(f'''
                    CREATE TABLE item(id INTEGER PRIMARY KEY);
                    CREATE TABLE audit(id INTEGER PRIMARY KEY);
                    CREATE TABLE marker(id INTEGER);
                    CREATE TRIGGER log_item AFTER INSERT ON item BEGIN
                        INSERT INTO audit VALUES(NEW.id);
                    END;
                    CREATE TRIGGER reject_audit AFTER INSERT ON audit WHEN NEW.id=2 BEGIN
                        SELECT RAISE({mode},'blocked audit');
                    END;
                ''')
                db.execute('BEGIN')
                db.execute('INSERT INTO marker VALUES(9)')
                with self.assertRaisesRegex(sqlite3.IntegrityError, 'blocked audit'):
                    db.execute('INSERT INTO item VALUES(1),(2),(3)')
                self.assertEqual(db.execute('SELECT * FROM item ORDER BY id').fetchall(), expected_items)
                self.assertEqual(db.execute('SELECT * FROM audit ORDER BY id').fetchall(), expected_audit)
                self.assertEqual(db.in_transaction, active)
                self.assertEqual(db.execute('SELECT * FROM marker').fetchall(), [(9,)] if active else [])
                db.rollback()
                self.assertEqual(db.execute('SELECT * FROM item').fetchall(), [])
                self.assertEqual(db.execute('SELECT * FROM audit').fetchall(), [])
                self.assertEqual(db.execute('SELECT * FROM marker').fetchall(), [])
                db.execute('INSERT INTO item VALUES(1),(3)')
                db.commit()
                self.assertEqual(db.execute('SELECT * FROM audit ORDER BY id').fetchall(), [(1,),(3,)])

    def test_update_of_typo_and_null_safe_audit(self):
        self.db.executescript('''
            CREATE TABLE obs(id INTEGER PRIMARY KEY, score INTEGER);
            INSERT INTO obs VALUES(1,NULL),(2,0);
            CREATE TABLE audit(id INTEGER, old_score INTEGER, new_score INTEGER);
            CREATE TRIGGER typo AFTER UPDATE OF socre ON obs BEGIN
                INSERT INTO audit VALUES(NEW.id,OLD.score,NEW.score);
            END;
        ''')
        self.db.execute('UPDATE obs SET score=7 WHERE id=1')
        self.assertEqual(self.rows('SELECT * FROM audit'), [])
        self.assertEqual(self.rows('SELECT score FROM obs WHERE id=1'), [(7,)])
        self.db.rollback()
        self.db.executescript('''
            DROP TRIGGER typo;
            CREATE TRIGGER changed AFTER UPDATE OF score ON obs
            WHEN OLD.score IS NOT NEW.score BEGIN
                INSERT INTO audit VALUES(NEW.id,OLD.score,NEW.score);
            END;
        ''')
        self.db.execute('UPDATE obs SET score=0')
        self.assertEqual(self.rows('SELECT * FROM audit'), [(1,None,0)])
        self.db.execute('UPDATE obs SET score=NULL WHERE id=2')
        self.assertEqual(self.rows('SELECT * FROM audit ORDER BY id'), [(1,None,0),(2,0,None)])
        self.db.execute('UPDATE obs SET score=score')
        self.assertEqual(self.rows('SELECT COUNT(*) FROM audit'), [(2,)])


if __name__ == '__main__':
    unittest.main(verbosity=2)
