"""Real native PostgreSQL RLS/transactions/migration; disposable Unix socket only.

No external DB connection or Supabase Auth simulation. CI must execute, not skip.
"""
from concurrent.futures import ThreadPoolExecutor
import os
from contextlib import contextmanager
import queue
import time
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "examples/postgres-architecture"
ROLES = ("lab_admin", "lab_alice", "lab_bob", "lab_anon", "lab_writer")
BIN = sorted((p for p in Path("/usr/lib/postgresql").glob("*/bin")
              if all((p / b).is_file() for b in ("initdb", "pg_ctl", "psql"))),
             key=lambda p: int(p.parent.name), reverse=True)


class PostgresArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not BIN or (hasattr(os, "geteuid") and os.geteuid() == 0):
            if os.environ.get("GITHUB_ACTIONS") == "true":
                raise RuntimeError("PostgreSQL non-root local engine required in CI")
            raise unittest.SkipTest("local non-root PostgreSQL binaries unavailable")
        cls.bin = BIN[0]
        cls.tmp = tempfile.TemporaryDirectory(prefix="pg-lab-")
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root = Path(cls.tmp.name)
        cls.data = cls.root / "data"
        cls.socket = cls.root / "socket"
        cls.socket.mkdir(mode=0o700)
        # No inherited PG connection parameters, password files or service names.
        cls.env = {k:v for k,v in os.environ.items() if not k.startswith("PG")}
        cls.env.update({"LC_ALL":"C", "PGPASSFILE":str(cls.root / "no-pgpass")})
        cls.command("initdb", "-D", str(cls.data), "-U", "lab_admin",
                    "--auth-local=trust", "--auth-host=scram-sha-256", "--no-locale")
        cls.command("pg_ctl", "-D", str(cls.data), "-l", str(cls.root / "server.log"),
                    "-o", "-c listen_addresses='' -c unix_socket_directories="+str(cls.socket)
                    +" -c unix_socket_permissions=0700 -p 5432", "-w", "start")
        cls.addClassCleanup(cls.command, "pg_ctl", "-D", str(cls.data), "-m", "immediate", "-w", "stop")
        cls.sql("CREATE ROLE lab_member NOLOGIN; "
                "CREATE ROLE lab_alice LOGIN IN ROLE lab_member; "
                "CREATE ROLE lab_bob LOGIN IN ROLE lab_member; "
                "CREATE ROLE lab_anon LOGIN; CREATE ROLE lab_writer LOGIN; "
                "SELECT 1;", db="postgres")
        cls.sql("CREATE DATABASE lab_case;",db="postgres")
        print("PG-ARCH-ENGINE:", cls.sql("SHOW server_version;",db="postgres"),
              "private Unix socket; TCP disabled", flush=True)

    @classmethod
    def command(cls, program, *args):
        return subprocess.run([str(cls.bin / program), *args], env=cls.env,
                              check=True, capture_output=True, text=True, timeout=30)

    @classmethod
    def sql(cls, query, role="lab_admin", db="lab_case", *, fail=False):
        assert role in ROLES and db in ("lab_case","postgres")
        result = subprocess.run([str(cls.bin/"psql"), "-X", "-w", "-qAt",
                                 "-h", str(cls.socket), "-p", "5432", "-U", role,
                                 "-d", db, "-v", "ON_ERROR_STOP=1",
                                 "-c", query], env=cls.env, text=True,
                                capture_output=True, timeout=15)
        if fail:
            if result.returncode == 0:
                raise AssertionError("expected SQL refusal")
            return result.stderr
        if result.returncode:
            raise AssertionError("unexpected SQL error: "+result.stderr)
        return result.stdout.strip()

    def setUp(self):
        self.sql("DROP SCHEMA IF EXISTS lab CASCADE;")
        self.sql((SQL/"01-baseline.sql").read_text())

    def migrate(self):
        self.sql((SQL/"02-rls-transaction.sql").read_text())
        self.sql((SQL/"03-decision-version.sql").read_text())

    def test_unprotected_grant_negative_control_and_rls_isolation(self):
        # Deliberately weaken ONLY this ephemeral fixture, then apply candidate.
        self.sql("GRANT USAGE ON SCHEMA lab TO lab_member; GRANT SELECT ON lab.drafts TO lab_member;")
        self.assertEqual(self.sql("SELECT count(*) FROM lab.drafts;","lab_alice"),"2")
        self.migrate()
        for actor,body in (("lab_alice","A"),("lab_bob","B")):
            self.assertEqual(self.sql("SELECT session_user,current_user; ",actor),actor+"|"+actor)
            self.assertEqual(self.sql("SELECT body FROM lab.drafts;",actor),body)
            self.assertEqual(self.sql("SELECT body FROM lab.draft_view;",actor),body)
            self.assertEqual(self.sql("SELECT count(*) FROM lab.stock;",actor),"1")
        self.assertIn("permission denied",self.sql("SELECT * FROM lab.drafts;","lab_anon",fail=True))
        self.assertIn("permission denied",self.sql("SELECT * FROM lab.draft_view;","lab_anon",fail=True))
        self.assertEqual(self.sql("SELECT count(*) FROM pg_roles WHERE rolname IN "
                                  "('lab_alice','lab_bob','lab_writer','lab_anon') "
                                  "AND (rolsuper OR rolbypassrls);"),"0")

    def test_insert_update_and_owner_transfer(self):
        self.migrate()
        self.sql("INSERT INTO lab.drafts(owner,id,body) VALUES('lab_alice','new','yes');","lab_alice")
        self.assertIn("row-level security",self.sql(
            "INSERT INTO lab.drafts(owner,id,body) VALUES('lab_bob','new','no');","lab_alice",fail=True))
        self.assertEqual(self.sql("UPDATE lab.drafts SET body='changed' WHERE owner='lab_bob' RETURNING id;","lab_alice"),"")
        self.assertIn("permission denied",self.sql(
            "UPDATE lab.drafts SET owner='lab_bob' WHERE id='new';","lab_alice",fail=True))
        self.sql("UPDATE lab.drafts SET body='own',label='v2' WHERE id='new';","lab_alice")
        self.assertEqual(self.sql("SELECT body,label FROM lab.drafts WHERE id='new';","lab_alice"),"own|v2")
        self.assertEqual(self.sql("SELECT body FROM lab.drafts;","lab_bob"),"B")

    def test_backend_only_mutation_and_receipt_isolation(self):
        self.migrate()
        for actor in ("lab_alice","lab_anon"):
            for query in ("UPDATE lab.stock SET remaining=0;", 
                          "INSERT INTO lab.receipts VALUES('lab_bob','x',1,'RESERVED');",
                          "SELECT lab.reserve('lab_bob','x',1);"):
                self.assertIn("permission denied",self.sql(query,actor,fail=True))
        self.assertEqual(self.sql("SELECT lab.reserve('lab_bob','x',2);","lab_writer"),"RESERVED")
        self.assertEqual(self.sql("SELECT count(*) FROM lab.receipts;","lab_alice"),"0")
        self.assertEqual(self.sql("SELECT qty,outcome FROM lab.receipts;","lab_bob"),"2|RESERVED")
        self.assertEqual(self.sql("SELECT remaining FROM lab.stock ORDER BY owner;"),"10\n8")

    def test_real_concurrent_stock_and_idempotent_decisions(self):
        self.migrate()
        ready=threading.Barrier(2)
        def reserve(token):
            ready.wait(timeout=5)
            return self.sql("BEGIN; SELECT lab.reserve('lab_alice','"+token+"',7); "
                            "SELECT pg_sleep(0.2); COMMIT;","lab_writer").strip()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(reserve,("first","second")))
        self.assertEqual(sorted(results),["INSUFFICIENT","RESERVED"])
        self.assertEqual(self.sql("SELECT remaining FROM lab.stock WHERE owner='lab_alice';"),"3")
        self.assertEqual(self.sql("SELECT count(*) FROM lab.receipts;"),"2")
        for token,decision in zip(("first","second"),results):
            self.assertEqual(self.sql("SELECT lab.reserve('lab_alice','"+token+"',7);","lab_writer"),decision)
        self.assertIn("token conflict",self.sql("SELECT lab.reserve('lab_alice','first',2);","lab_writer",fail=True))
        self.assertEqual(self.sql("SELECT remaining FROM lab.stock WHERE owner='lab_alice';"),"3")
        self.assertEqual(self.sql("SELECT count(*) FROM lab.receipts;"),"2")

    def test_transaction_failure_rolls_back_stock_and_receipt(self):
        self.migrate()
        self.assertIn("division by zero",self.sql(
            "BEGIN; SELECT lab.reserve('lab_alice','abort',4); SELECT 1/0; COMMIT;",
            "lab_writer",fail=True))
        self.assertEqual(self.sql("SELECT remaining FROM lab.stock WHERE owner='lab_alice';"),"10")
        self.assertEqual(self.sql("SELECT count(*) FROM lab.receipts;"),"0")
        self.assertEqual(self.sql("SELECT lab.reserve('lab_alice','abort',4);","lab_writer"),"RESERVED")

    def test_migration_preserves_rows_and_old_column_contract(self):
        self.sql("INSERT INTO lab.drafts(owner,id,body) VALUES('lab_alice','old','before');")
        self.migrate()
        self.assertEqual(self.sql("SELECT body,label FROM lab.drafts WHERE id='old';","lab_alice"),"before|")
        self.sql("INSERT INTO lab.drafts(owner,id,body) VALUES('lab_alice','legacy-client','ok');","lab_alice")
        self.assertEqual(self.sql("SELECT body FROM lab.drafts WHERE id='legacy-client';","lab_alice"),"ok")
        self.assertEqual(self.sql("SELECT convalidated FROM pg_constraint WHERE conname='stock_max' AND conrelid='lab.stock'::regclass;"),"t")
        self.assertIn("check constraint",self.sql("UPDATE lab.stock SET remaining=11 WHERE owner='lab_alice';","lab_writer",fail=True))

    def test_invalid_legacy_data_aborts_migration_without_partial_schema(self):
        self.sql("UPDATE lab.stock SET remaining=11 WHERE owner='lab_alice';")
        self.assertIn("check constraint",self.sql((SQL/"02-rls-transaction.sql").read_text(),fail=True))
        self.assertEqual(self.sql("SELECT remaining FROM lab.stock WHERE owner='lab_alice';"),"11")
        self.assertEqual(self.sql("SELECT count(*) FROM pg_constraint WHERE conname='stock_max' AND conrelid='lab.stock'::regclass;"),"0")
        self.assertEqual(self.sql("SELECT count(*) FROM information_schema.columns WHERE table_schema='lab' AND table_name='drafts' AND column_name='label';"),"0")
        self.assertEqual(self.sql("SELECT relrowsecurity FROM pg_class WHERE oid='lab.drafts'::regclass;"),"f")
        self.assertIn("permission denied",self.sql("SELECT * FROM lab.drafts;","lab_alice",fail=True))
        self.sql("UPDATE lab.stock SET remaining=10 WHERE owner='lab_alice';")
        self.migrate()
        self.assertEqual(self.sql("SELECT count(*) FROM lab.drafts;","lab_alice"),"1")

    @contextmanager
    def live_session(self, role="lab_admin"):
        # Actual long-lived psql connection; expose SQLSTATE, not error wording.
        # The private cluster and fixed role allowlist are inherited from setUpClass.
        self.assertIn(role, ROLES)
        with tempfile.TemporaryFile(mode="w+t") as errors:
            proc = subprocess.Popen(
                [str(self.bin/"psql"), "-X", "-w", "-qAt", "-h", str(self.socket),
                 "-p", "5432", "-U", role, "-d", "lab_case", "-v", "ON_ERROR_STOP=0"],
                env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=errors, text=True, bufsize=1)
            lines = queue.Queue()
            def collect():
                for line in proc.stdout:
                    lines.put(line.rstrip("\n"))
                lines.put(None)
            reader = threading.Thread(target=collect, daemon=True)
            reader.start()
            def execute(query):
                proc.stdin.write(query.rstrip(";") + ";\n\\echo __LAB_DONE__ :SQLSTATE\n")
                proc.stdin.flush()
                result = []
                deadline = time.monotonic() + 12
                while True:
                    line = lines.get(timeout=max(0.1, deadline-time.monotonic()))
                    if line is None:
                        raise AssertionError("live test connection exited")
                    if line.startswith("__LAB_DONE__ "):
                        return line.split()[1], "\n".join(result)
                    result.append(line)
            try:
                yield execute
            finally:
                proc.stdin.close()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)
                reader.join(timeout=5)
                proc.stdout.close()

    def migration_snapshot(self):
        # Include catalogue policies, object ACLs, columns, constraints, function
        # signatures, view definitions, and the actual persisted business rows.
        return self.sql("""
          SELECT jsonb_build_array(
            (SELECT jsonb_agg(to_jsonb(c) ORDER BY c.relname) FROM
              (SELECT relname,relkind,relacl,relrowsecurity,relforcerowsecurity,reloptions
               FROM pg_class WHERE relnamespace='lab'::regnamespace) c),
            (SELECT jsonb_agg(to_jsonb(c) ORDER BY c.table_name,c.ordinal_position)
               FROM information_schema.columns c WHERE table_schema='lab'),
            (SELECT jsonb_agg(to_jsonb(c) ORDER BY c.conname)
               FROM (SELECT conname,convalidated,pg_get_constraintdef(oid) AS def
               FROM pg_constraint WHERE connamespace='lab'::regnamespace) c),
            (SELECT jsonb_agg(to_jsonb(p) ORDER BY p.tablename,p.policyname)
               FROM pg_policies p WHERE schemaname='lab'),
            (SELECT jsonb_agg(to_jsonb(p) ORDER BY p.proname)
               FROM (SELECT proname,proacl,pg_get_functiondef(oid) AS def
               FROM pg_proc WHERE pronamespace='lab'::regnamespace) p),
            (SELECT jsonb_agg(to_jsonb(v) ORDER BY v.viewname)
               FROM pg_views v WHERE schemaname='lab'),
            (SELECT nspacl FROM pg_namespace WHERE nspname='lab'),
            (SELECT jsonb_agg(to_jsonb(d) ORDER BY owner,id) FROM lab.drafts d),
            (SELECT jsonb_agg(to_jsonb(s) ORDER BY owner) FROM lab.stock s),
            (SELECT jsonb_agg(to_jsonb(r) ORDER BY owner,token) FROM lab.receipts r));
        """)

    def test_pg_advanced_migration_lock_timeout_no_partial_change(self):
        before=self.migration_snapshot()
        with self.live_session() as held:
            self.assertEqual(held("BEGIN; LOCK TABLE lab.drafts IN ACCESS SHARE MODE")[0],"00000")
            self.assertIn("lock timeout",self.sql((SQL/"02-rls-transaction.sql").read_text(),fail=True))
            self.assertEqual(self.migration_snapshot(),before)
            self.assertEqual(held("ROLLBACK")[0],"00000")
        self.migrate()
        self.assertEqual(self.sql("SELECT count(*) FROM lab.draft_view","lab_alice"),"1")

    def test_pg_advanced_late_migration_failure_preserves_existing_objects(self):
        # Existing view collides late, after table, policy and grant statements.
        self.sql("CREATE VIEW lab.draft_view AS SELECT owner,id FROM lab.drafts;")
        before=self.migration_snapshot()
        self.assertIn("already exists",self.sql((SQL/"02-rls-transaction.sql").read_text(),fail=True))
        self.assertEqual(self.migration_snapshot(),before)
        self.sql("DROP VIEW lab.draft_view;")  # synthetic fixture only, reviewed conflict
        self.migrate()
        self.assertEqual(self.sql("SELECT body FROM lab.draft_view","lab_alice"),"A")

    def test_pg_advanced_live_old_prepared_projection_and_new_column(self):
        with self.live_session() as old:
            self.assertEqual(old("PREPARE explicit_v1 AS SELECT owner,id,body FROM lab.drafts ORDER BY owner; "
                                 "PREPARE wildcard_v1 AS SELECT * FROM lab.drafts ORDER BY owner")[0],"00000")
            self.assertEqual(old("EXECUTE explicit_v1"),("00000","lab_alice|draft|A\nlab_bob|draft|B"))
            self.assertEqual(old("EXECUTE wildcard_v1")[0],"00000")
            self.migrate()
            self.assertEqual(old("EXECUTE explicit_v1"),("00000","lab_alice|draft|A\nlab_bob|draft|B"))
            # SELECT * has a different result shape. Do not claim it is compatible.
            self.assertEqual(old("EXECUTE wildcard_v1")[0],"0A000")
            self.sql("UPDATE lab.drafts SET label='new-v2' WHERE id='draft'","lab_alice")
            self.assertEqual(old("EXECUTE explicit_v1"),("00000","lab_alice|draft|A\nlab_bob|draft|B"))
            self.assertEqual(old("DEALLOCATE wildcard_v1")[0],"00000")
        self.assertEqual(self.sql("SELECT body,label FROM lab.drafts","lab_alice"),"A|new-v2")

    def test_pg_advanced_same_token_actual_wait_replay_and_namespace(self):
        self.migrate()
        for token,qty,second_qty,expected in (
                ("same",4,4,("00000","RESERVED")),
                ("conflict",1,2,("22023","")),
                ("denied",10,10,("00000","INSUFFICIENT"))):
            with self.subTest(token=token):
                with self.live_session("lab_writer") as first, self.live_session("lab_writer") as second:
                    self.assertEqual(first("BEGIN")[0],"00000")
                    self.assertEqual(first(f"SELECT lab.reserve('lab_alice','{token}',{qty})")[0],"00000")
                    self.assertEqual(second("SET application_name='pg_lab_waiter'")[0],"00000")
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        pending=pool.submit(second,f"SELECT lab.reserve('lab_alice','{token}',{second_qty})")
                        try:
                            deadline=time.monotonic()+5
                            observed=False
                            while time.monotonic()<deadline:
                                if self.sql("SELECT count(*) FROM pg_stat_activity WHERE "
                                            "application_name='pg_lab_waiter' AND cardinality(pg_blocking_pids(pid))>0")=="1":
                                    observed=True
                                    break
                                time.sleep(.05)
                            self.assertTrue(observed, "expected actual blocked DB session")
                            self.assertEqual(first("COMMIT")[0],"00000")
                            self.assertEqual(pending.result(timeout=12),expected)
                        finally:
                            if not pending.done():
                                first("ROLLBACK")
                self.assertEqual(self.sql(f"SELECT count(*) FROM lab.receipts WHERE owner='lab_alice' AND token='{token}'"),"1")
        self.assertEqual(self.sql("SELECT remaining FROM lab.stock WHERE owner='lab_alice'"),"5")
        self.assertEqual(self.sql("SELECT lab.reserve('lab_bob','same',4)","lab_writer"),"RESERVED")
        self.assertEqual(self.sql("SELECT count(*) FROM lab.receipts WHERE token='same'"),"2")
        self.assertEqual(self.sql("SELECT remaining FROM lab.stock WHERE owner='lab_bob'"),"6")

    def test_pg_advanced_repeatable_read_stale_denial_is_retryable(self):
        self.migrate()
        self.sql("SELECT lab.reserve('lab_alice','fill',10)","lab_writer")
        with self.live_session("lab_writer") as stale:
            self.assertEqual(stale("BEGIN ISOLATION LEVEL REPEATABLE READ")[0],"00000")
            self.assertEqual(stale("SELECT remaining FROM lab.stock WHERE owner='lab_alice'"),("00000","0"))
            # Overlapping transaction commits a durable denial while the other
            # session still holds the old snapshot. It has no stock decrement.
            self.assertEqual(self.sql("SELECT lab.reserve('lab_alice','rr-denied',1)","lab_writer"),"INSUFFICIENT")
            code,_=stale("SELECT lab.reserve('lab_alice','rr-denied',1)")
            self.assertEqual(code,"40001")
            self.assertEqual(stale("ROLLBACK")[0],"00000")
        self.assertEqual(self.sql("SELECT lab.reserve('lab_alice','rr-denied',1)","lab_writer"),"INSUFFICIENT")
        self.assertEqual(self.sql("SELECT count(*) FROM lab.receipts WHERE token='rr-denied'"),"1")
        self.assertEqual(self.sql("SELECT remaining FROM lab.stock WHERE owner='lab_alice'"),"0")

    def test_pg_advanced_v2_to_v3_preserves_receipts_and_acl(self):
        self.sql((SQL/"02-rls-transaction.sql").read_text())
        self.assertEqual(self.sql("SELECT lab.reserve('lab_alice','existing',9)","lab_writer"),"RESERVED")
        self.assertEqual(self.sql("SELECT lab.reserve('lab_alice','old-denial',2)","lab_writer"),"INSUFFICIENT")
        before=self.sql("""SELECT jsonb_build_array(
          (SELECT jsonb_agg(to_jsonb(s) ORDER BY owner) FROM lab.stock s),
          (SELECT jsonb_agg(to_jsonb(r) ORDER BY owner,token) FROM lab.receipts r),
          (SELECT proacl FROM pg_proc WHERE oid='lab.reserve(name,text,integer)'::regprocedure));""")
        self.sql((SQL/"03-decision-version.sql").read_text())
        after=self.sql("""SELECT jsonb_build_array(
          (SELECT jsonb_agg(to_jsonb(s) ORDER BY owner) FROM lab.stock s),
          (SELECT jsonb_agg(to_jsonb(r) ORDER BY owner,token) FROM lab.receipts r),
          (SELECT proacl FROM pg_proc WHERE oid='lab.reserve(name,text,integer)'::regprocedure));""")
        self.assertEqual(after,before)
        self.assertEqual(self.sql("SELECT lab.reserve('lab_alice','existing',9)","lab_writer"),"RESERVED")
        self.assertEqual(self.sql("SELECT lab.reserve('lab_alice','old-denial',2)","lab_writer"),"INSUFFICIENT")
        self.assertIn("permission denied",self.sql("SELECT lab.reserve('lab_alice','x',1)","lab_alice",fail=True))
        self.assertEqual(self.sql("SELECT remaining FROM lab.stock WHERE owner='lab_alice'"),"1")
        self.assertEqual(self.sql("SELECT count(*) FROM lab.receipts;"),"2")

    def shared_setup(self, *, migrate=True):
        # All changes stay in the existing disposable lab_case database.
        self.sql("DROP SCHEMA IF EXISTS sharedlab CASCADE;")
        self.sql("DO $$ BEGIN IF NOT EXISTS(SELECT FROM pg_roles WHERE rolname='lab_shared_exec') "
                 "THEN CREATE ROLE lab_shared_exec NOLOGIN NOSUPERUSER NOBYPASSRLS; END IF; END $$;")
        self.sql((SQL/"shared/01-reserve.sql").read_text())
        self.addCleanup(self.sql,"DROP SCHEMA IF EXISTS sharedlab CASCADE;")
        if migrate:
            self.sql((SQL/"shared/02-cancel.sql").read_text())

    def shared_state(self):
        # Oracle uses actual business rows, independent of function responses.
        self.assertEqual(self.sql("SELECT remaining+coalesce((SELECT sum(qty) "
                                  "FROM sharedlab.bookings WHERE active),0)=capacity "
                                  "FROM sharedlab.pool"),"t")
        return self.sql("SELECT remaining,decision_version FROM sharedlab.pool")

    def shared_wait(self, first_role, first_query, second_role, second_query, expected_first, expected_second):
        with self.live_session(first_role) as first, self.live_session(second_role) as second:
            self.assertEqual(first("BEGIN")[0],"00000")
            self.assertEqual(first(first_query),("00000",expected_first))
            self.assertEqual(second("SET application_name='shared_lab_waiter'")[0],"00000")
            with ThreadPoolExecutor(max_workers=1) as pool:
                pending=pool.submit(second,second_query)
                try:
                    until=time.monotonic()+5
                    while time.monotonic()<until:
                        if self.sql("SELECT count(*) FROM pg_stat_activity WHERE "
                                    "application_name='shared_lab_waiter' AND cardinality(pg_blocking_pids(pid))>0")=="1":
                            break
                        time.sleep(.05)
                    else:
                        self.fail("no real shared-resource lock wait observed")
                    self.assertEqual(first("COMMIT")[0],"00000")
                    self.assertEqual(pending.result(timeout=12),expected_second)
                finally:
                    if not pending.done():
                        first("ROLLBACK")

    def test_pg_shared_cross_actor_actual_contention_and_replay(self):
        self.shared_setup()
        self.shared_wait("lab_alice","SELECT sharedlab.reserve('same',7)",
                         "lab_bob","SELECT sharedlab.reserve('same',7)",
                         "RESERVED",("00000","INSUFFICIENT"))
        self.assertEqual(self.shared_state(),"3|2")
        self.assertEqual(self.sql("SELECT count(*) FROM sharedlab.decisions WHERE token='same'"),"2")
        self.assertEqual(self.sql("SELECT sharedlab.reserve('same',7)","lab_bob"),"INSUFFICIENT")
        self.assertEqual(self.shared_state(),"3|2")
        self.assertEqual(self.sql("SELECT sharedlab.cancel('release','same')","lab_alice"),"CANCELLED")
        self.assertEqual(self.shared_state(),"10|3")
        self.assertEqual(self.sql("SELECT sharedlab.reserve('same',7)","lab_bob"),"INSUFFICIENT")
        self.assertEqual(self.sql("SELECT sharedlab.reserve('fresh',7)","lab_bob"),"RESERVED")
        self.assertEqual(self.shared_state(),"3|4")

    def test_pg_shared_cancel_actual_contention_and_exactly_once_restore(self):
        self.shared_setup()
        self.sql("SELECT sharedlab.reserve('book',6)","lab_alice")
        self.shared_wait("lab_alice","SELECT sharedlab.cancel('c1','book')",
                         "lab_alice","SELECT sharedlab.cancel('c2','book')",
                         "CANCELLED",("00000","NOT_ACTIVE"))
        self.assertEqual(self.shared_state(),"10|3")
        self.assertEqual(self.sql("SELECT sharedlab.cancel('c1','book')","lab_alice"),"CANCELLED")
        self.assertEqual(self.sql("SELECT sharedlab.cancel('c2','book')","lab_alice"),"NOT_ACTIVE")
        self.assertEqual(self.sql("SELECT sharedlab.reserve('book',6)","lab_alice"),"RESERVED")
        self.assertEqual(self.sql("SELECT active FROM sharedlab.bookings WHERE token='book'"),"f")
        self.assertEqual(self.shared_state(),"10|3")

    def test_pg_shared_identity_rls_function_acl_and_foreign_cancel(self):
        self.shared_setup()
        self.sql("SELECT sharedlab.reserve('private-a',4)","lab_alice")
        self.sql("SELECT sharedlab.reserve('private-b',3)","lab_bob")
        self.assertEqual(self.sql("SELECT token FROM sharedlab.bookings","lab_alice"),"private-a")
        self.assertEqual(self.sql("SELECT token FROM sharedlab.decisions","lab_bob"),"private-b")
        for query in ("UPDATE sharedlab.pool SET remaining=10",
                      "UPDATE sharedlab.bookings SET active=false",
                      "INSERT INTO sharedlab.decisions VALUES('lab_bob','fake','cancel','x',NULL,'CANCELLED')",
                      "SET ROLE lab_shared_exec",
                      "SET SESSION AUTHORIZATION lab_alice"):
            self.assertIn("permission denied",self.sql(query,"lab_bob",fail=True))
        for query in ("SELECT * FROM sharedlab.bookings","SELECT sharedlab.reserve('x',1)",
                      "SELECT sharedlab.cancel('x','private-a')"):
            self.assertIn("permission denied",self.sql(query,"lab_anon",fail=True))
        self.assertEqual(self.sql("SELECT rolcanlogin OR rolsuper OR rolbypassrls "
                                  "FROM pg_roles WHERE rolname='lab_shared_exec'"),"f")
        self.assertEqual(self.sql("SELECT count(*) FROM pg_proc p JOIN pg_roles r ON r.oid=p.proowner "
                                  "WHERE p.pronamespace='sharedlab'::regnamespace AND p.prosecdef "
                                  "AND r.rolname='lab_shared_exec'"),"2")
        self.assertEqual(self.sql("SELECT sharedlab.cancel('foreign','private-a')","lab_bob"),"NOT_ACTIVE")
        self.assertEqual(self.shared_state(),"3|3")
        self.assertEqual(self.sql("SELECT active FROM sharedlab.bookings WHERE token='private-a'"),"t")

    def test_pg_shared_token_conflict_negative_replay_and_transaction_abort(self):
        self.shared_setup()
        self.assertEqual(self.sql("SELECT sharedlab.cancel('early','future')","lab_alice"),"NOT_ACTIVE")
        self.sql("SELECT sharedlab.reserve('future',4)","lab_alice")
        self.assertEqual(self.sql("SELECT sharedlab.cancel('early','future')","lab_alice"),"NOT_ACTIVE")
        for query in ("SELECT sharedlab.reserve('future',5)",
                      "SELECT sharedlab.cancel('future','future')",
                      "SELECT sharedlab.cancel('early','other')"):
            self.assertIn("token conflict",self.sql(query,"lab_alice",fail=True))
        before=self.shared_state()
        self.assertIn("division by zero",self.sql("BEGIN; SELECT sharedlab.cancel('abort','future'); SELECT 1/0; COMMIT;",
                                                 "lab_alice",fail=True))
        self.assertEqual(self.shared_state(),before)
        self.assertEqual(self.sql("SELECT count(*) FROM sharedlab.decisions WHERE token='abort'"),"0")
        self.assertEqual(self.sql("SELECT sharedlab.cancel('abort','future')","lab_alice"),"CANCELLED")
        self.assertEqual(self.shared_state(),"10|3")

    def test_pg_shared_migration_preserves_v1_history_and_old_contract(self):
        self.shared_setup(migrate=False)
        self.sql("SELECT sharedlab.reserve('v1-accepted',8)","lab_alice")
        self.sql("SELECT sharedlab.reserve('v1-denied',4)","lab_bob")
        before=self.sql("SELECT owner,token,operation,target,qty,outcome FROM sharedlab.decisions ORDER BY owner,token")
        with self.live_session("lab_alice") as old:
            self.assertEqual(old("PREPARE old_booking AS SELECT token,qty FROM sharedlab.bookings")[0],"00000")
            self.assertEqual(old("EXECUTE old_booking"),("00000","v1-accepted|8"))
            self.sql((SQL/"shared/02-cancel.sql").read_text())
            self.assertEqual(old("EXECUTE old_booking"),("00000","v1-accepted|8"))
            self.assertEqual(old("SELECT sharedlab.reserve('v1-accepted',8)"),("00000","RESERVED"))
        self.assertEqual(self.sql("SELECT owner,token,operation,target,qty,outcome FROM sharedlab.decisions ORDER BY owner,token"),before)
        self.assertEqual(self.shared_state(),"2|2")
        self.assertEqual(self.sql("SELECT sharedlab.cancel('new-cancel','v1-accepted')","lab_alice"),"CANCELLED")
        self.assertEqual(self.shared_state(),"10|3")
        self.assertEqual(self.sql("SELECT sharedlab.reserve('v1-denied',4)","lab_bob"),"INSUFFICIENT")

    def test_pg_shared_repeatable_read_new_denial_versions_shared_resource(self):
        self.shared_setup()
        self.sql("SELECT sharedlab.reserve('fill',10)","lab_alice")
        with self.live_session("lab_bob") as stale:
            self.assertEqual(stale("BEGIN ISOLATION LEVEL REPEATABLE READ")[0],"00000")
            self.assertEqual(stale("SELECT remaining FROM sharedlab.pool"),("00000","0"))
            self.assertEqual(self.sql("SELECT sharedlab.reserve('denied',1)","lab_bob"),"INSUFFICIENT")
            self.assertEqual(stale("SELECT sharedlab.reserve('denied',1)")[0],"40001")
            self.assertEqual(stale("ROLLBACK")[0],"00000")
        self.assertEqual(self.sql("SELECT sharedlab.reserve('denied',1)","lab_bob"),"INSUFFICIENT")
        self.assertEqual(self.shared_state(),"0|2")
        self.assertEqual(self.sql("SELECT count(*) FROM sharedlab.decisions WHERE token='denied'"),"1")

    def test_pg_shared_cancel_rebook_competes_for_same_resource(self):
        self.shared_setup()
        self.sql("SELECT sharedlab.reserve('full',10)","lab_alice")
        self.shared_wait("lab_alice","SELECT sharedlab.cancel('release','full')",
                         "lab_bob","SELECT sharedlab.reserve('take',10)",
                         "CANCELLED",("00000","RESERVED"))
        self.assertEqual(self.shared_state(),"0|3")
        self.assertEqual(self.sql("SELECT owner FROM sharedlab.bookings WHERE active"),"lab_bob")

    def procedure_setup(self):
        # Synthetic schema, using the same disposable cluster and psql helper.
        # No public EXECUTE, no new role or external database.
        self.sql("""
            DROP SCHEMA IF EXISTS procdemo CASCADE;
            CREATE SCHEMA procdemo;
            REVOKE ALL ON SCHEMA procdemo FROM PUBLIC;
            CREATE TABLE procdemo.record(
                id integer PRIMARY KEY, actor name NOT NULL,
                note text NOT NULL, revision integer NOT NULL CHECK (revision>0));
            INSERT INTO procdemo.record VALUES
                (1,'lab_alice','old-a',1),(2,'lab_bob','old-b',1);
            CREATE TABLE procdemo.audit(id integer NOT NULL, revision integer NOT NULL);
            CREATE TABLE procdemo.stage(n integer PRIMARY KEY);
            GRANT USAGE ON SCHEMA procdemo TO lab_alice,lab_bob,lab_writer;
            GRANT SELECT (id,actor,revision), UPDATE(note,revision)
                ON procdemo.record TO lab_writer;
            GRANT INSERT ON procdemo.audit TO lab_writer;
            CREATE PROCEDURE procdemo.revise(
                IN p_id integer, IN p_note text, INOUT p_revision integer, OUT outcome text)
            LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
            DECLARE new_rev integer;
            BEGIN
                IF p_id IS NULL OR p_id<=0 OR p_revision IS NULL OR p_revision<=0
                   OR p_note IS NULL OR btrim(p_note)='' OR char_length(p_note)>40 THEN
                    RAISE EXCEPTION USING ERRCODE='22023', MESSAGE='invalid input';
                END IF;
                UPDATE procdemo.record AS r SET note=p_note,revision=r.revision+1
                  WHERE r.id=p_id AND r.actor=session_user AND r.revision=p_revision
                  RETURNING r.revision INTO new_rev;
                IF NOT FOUND THEN
                    RAISE EXCEPTION USING ERRCODE='P0002', MESSAGE='record unavailable';
                END IF;
                INSERT INTO procdemo.audit VALUES(p_id,new_rev);
                p_revision:=new_rev;
                outcome:='UPDATED';
            END;
            $$;
            GRANT CREATE ON SCHEMA procdemo TO lab_writer;
            ALTER PROCEDURE procdemo.revise(integer,text,integer) OWNER TO lab_writer;
            REVOKE CREATE ON SCHEMA procdemo FROM lab_writer;
            REVOKE ALL ON PROCEDURE procdemo.revise(integer,text,integer) FROM PUBLIC;
            GRANT EXECUTE ON PROCEDURE procdemo.revise(integer,text,integer) TO lab_alice;
            CREATE PROCEDURE procdemo.invoker_read(IN p_id integer, OUT result text)
                LANGUAGE plpgsql SECURITY INVOKER AS $$
                BEGIN
                    SELECT note INTO result FROM procdemo.record WHERE id=p_id;
                END;
                $$;
            REVOKE ALL ON PROCEDURE procdemo.invoker_read(integer) FROM PUBLIC;
            GRANT EXECUTE ON PROCEDURE procdemo.invoker_read(integer) TO lab_alice;
        """)

    def procedure_snapshot(self):
        return self.sql("""SELECT jsonb_build_array(
            (SELECT jsonb_agg(to_jsonb(r) ORDER BY id) FROM procdemo.record r),
            (SELECT jsonb_agg(to_jsonb(a) ORDER BY id,revision) FROM procdemo.audit a),
            (SELECT jsonb_agg(n ORDER BY n) FROM procdemo.stage));""")

    def test_pg_procedure_named_inputs_output_and_errors(self):
        self.procedure_setup()
        self.assertEqual(self.sql("""SELECT prokind::text,array_to_string(proargmodes,',')
            FROM pg_proc WHERE oid='procdemo.revise(integer,text,integer)'::regprocedure"""),
            "p|i,i,b,o")
        before=self.procedure_snapshot()
        with self.live_session("lab_alice") as call:
            for cmd in ("CALL procdemo.revise(NULL,'x',1,NULL)",
                        "CALL procdemo.revise(1,NULL,1,NULL)",
                        "CALL procdemo.revise(1,'   ',1,NULL)",
                        "CALL procdemo.revise(1,repeat('x',41),1,NULL)",
                        "CALL procdemo.revise(1,'x',0,NULL)",
                        "CALL procdemo.revise(1,'x',NULL,NULL)"):
                with self.subTest(cmd=cmd):
                    self.assertEqual(call(cmd)[0], "22023")
                    self.assertEqual(self.procedure_snapshot(),before)
            for cmd in ("CALL procdemo.revise(2,'x',1,NULL)",
                        "CALL procdemo.revise(99,'x',1,NULL)",
                        "CALL procdemo.revise(1,'x',9,NULL)"):
                self.assertEqual(call(cmd)[0],"P0002")
                self.assertEqual(self.procedure_snapshot(),before)
            # Named parameters may appear in a different order. OUT placeholder is NULL.
            self.assertEqual(call("CALL procdemo.revise(p_note=>'new',p_id=>1,"
                                  "p_revision=>1,outcome=>NULL)"),("00000","2|UPDATED"))
            self.assertEqual(call("CALL procdemo.revise(1,'a''; SELECT 99;--',2,NULL)"),
                             ("00000","3|UPDATED"))
        self.assertEqual(self.sql("SELECT id,note,revision FROM procdemo.record ORDER BY id"),
                         "1|a'; SELECT 99;--|3\n2|old-b|1")
        self.assertEqual(self.sql("SELECT id,revision FROM procdemo.audit ORDER BY revision"),
                         "1|2\n1|3")

    def test_pg_procedure_execute_only_role_and_invoker_boundary(self):
        self.procedure_setup()
        before=self.procedure_snapshot()
        with self.live_session("lab_alice") as alice:
            self.assertEqual(alice("SELECT note FROM procdemo.record")[0],"42501")
            self.assertEqual(alice("UPDATE procdemo.record SET note='bad'")[0],"42501")
            self.assertEqual(alice("INSERT INTO procdemo.audit VALUES(1,99)")[0],"42501")
            self.assertEqual(alice("CALL procdemo.invoker_read(1,NULL)")[0],"42501")
            self.assertEqual(alice("SET ROLE lab_writer")[0],"42501")
            self.assertEqual(self.procedure_snapshot(),before)
            self.assertEqual(alice("CREATE TEMP TABLE record(id int, note text)")[0],"00000")
            self.assertEqual(alice("INSERT INTO record VALUES(1,'decoy')")[0],"00000")
            self.assertEqual(alice("CALL procdemo.revise(1,'legit',1,NULL)"),
                             ("00000","2|UPDATED"))
            self.assertEqual(alice("SELECT note FROM record"),("00000","decoy"))
        after=self.procedure_snapshot()
        for actor in ("lab_bob","lab_anon"):
            with self.live_session(actor) as denied:
                self.assertEqual(denied("CALL procdemo.revise(2,'bad',1,NULL)")[0],"42501")
                self.assertEqual(self.procedure_snapshot(),after)
        self.assertEqual(self.sql("SELECT id,note,revision FROM procdemo.record ORDER BY id"),
                         "1|legit|2\n2|old-b|1")
        self.assertEqual(self.sql("""SELECT rolname,rolsuper,rolbypassrls FROM pg_roles
            WHERE rolname='lab_writer'"""),"lab_writer|f|f")
        self.assertEqual(self.sql("""SELECT pg_get_userbyid(proowner),prosecdef FROM pg_proc
            WHERE oid='procdemo.revise(integer,text,integer)'::regprocedure"""),
            "lab_writer|t")

    def test_pg_procedure_caught_exception_subtransaction_output(self):
        self.procedure_setup()
        self.sql("""
            CREATE PROCEDURE procdemo.stage_one(
                IN requested_failure boolean, OUT result text, OUT attempted integer)
            LANGUAGE plpgsql AS $$
            BEGIN
                result:='OK';
                attempted:=0;
                BEGIN
                    INSERT INTO procdemo.stage VALUES(7);
                    attempted:=1;
                    IF requested_failure THEN
                        RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='fixture refusal';
                    END IF;
                EXCEPTION WHEN check_violation THEN
                    GET STACKED DIAGNOSTICS result=RETURNED_SQLSTATE;
                END;
            END;
            $$;
            REVOKE ALL ON PROCEDURE procdemo.stage_one(boolean) FROM PUBLIC;
        """)
        with self.live_session() as call:
            self.assertEqual(call("BEGIN")[0],"00000")
            self.assertEqual(call("INSERT INTO procdemo.stage VALUES(9)")[0],"00000")
            # SQL command success does not mean business success. Local variable
            # survives the caught subtransaction, while inserted row 7 rolls back.
            self.assertEqual(call("CALL procdemo.stage_one(true,NULL,NULL)"),
                             ("00000","23514|1"))
            self.assertEqual(call("SELECT n FROM procdemo.stage ORDER BY n"),("00000","9"))
            self.assertEqual(call("COMMIT")[0],"00000")
            self.assertEqual(self.sql("SELECT n FROM procdemo.stage ORDER BY n"),"9")
            self.assertEqual(call("CALL procdemo.stage_one(false,NULL,NULL)"),
                             ("00000","OK|1"))
            self.assertEqual(self.sql("SELECT n FROM procdemo.stage ORDER BY n"),"7\n9")

    def test_pg_procedure_transaction_control_is_not_atomic_call(self):
        self.procedure_setup()
        self.sql("""
            CREATE PROCEDURE procdemo.segmented()
            LANGUAGE plpgsql AS $$
            BEGIN
                INSERT INTO procdemo.stage VALUES(1);
                COMMIT;
                INSERT INTO procdemo.stage VALUES(2);
                RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='late failure';
            END;
            $$;
            CREATE PROCEDURE procdemo.definer_commit()
            LANGUAGE plpgsql SECURITY DEFINER AS $$
            BEGIN COMMIT; END;
            $$;
            CREATE PROCEDURE procdemo.configured_commit()
            LANGUAGE plpgsql SET search_path=pg_catalog AS $$
            BEGIN COMMIT; END;
            $$;
            REVOKE ALL ON PROCEDURE procdemo.segmented() FROM PUBLIC;
            REVOKE ALL ON PROCEDURE procdemo.definer_commit() FROM PUBLIC;
            REVOKE ALL ON PROCEDURE procdemo.configured_commit() FROM PUBLIC;
        """)
        with self.live_session() as call:
            self.assertEqual(call("BEGIN")[0],"00000")
            self.assertEqual(call("CALL procdemo.segmented()")[0],"2D000")
            self.assertEqual(call("SELECT 1")[0],"25P02")
            self.assertEqual(call("ROLLBACK")[0],"00000")
            self.assertEqual(self.sql("SELECT n FROM procdemo.stage"),"")
            self.assertEqual(call("CALL procdemo.definer_commit()")[0],"2D000")
            self.assertEqual(call("CALL procdemo.configured_commit()")[0],"2D000")
            # Top-level CALL may commit internally. Later error cannot undo
            # first committed segment, verified from a fresh connection.
            self.assertEqual(call("CALL procdemo.segmented()")[0],"22023")
            self.assertEqual(self.sql("SELECT n FROM procdemo.stage ORDER BY n"),"1")
            self.assertEqual(call("SELECT n FROM procdemo.stage ORDER BY n"),("00000","1"))

    def function_setup(self):
        self.sql("""
            DROP SCHEMA IF EXISTS fnlesson CASCADE;
            CREATE SCHEMA fnlesson;
            REVOKE ALL ON SCHEMA fnlesson FROM PUBLIC;
            CREATE TABLE fnlesson.people(id integer PRIMARY KEY);
            INSERT INTO fnlesson.people VALUES(1),(2),(3),(4);
            CREATE TABLE fnlesson.obs(id integer PRIMARY KEY, person integer, score integer);
            INSERT INTO fnlesson.obs VALUES(1,1,0),(2,1,NULL),(3,2,5),(4,2,5),(5,4,NULL);
            CREATE TABLE fnlesson.config(factor integer NOT NULL);
            INSERT INTO fnlesson.config VALUES(10);
            CREATE TABLE fnlesson.counter(n integer NOT NULL);
            INSERT INTO fnlesson.counter VALUES(0);
        """)

    def test_pg_function_scalar_set_and_null_contracts(self):
        self.function_setup()
        self.sql("""
            CREATE FUNCTION fnlesson.scalar_score(p integer) RETURNS integer
                LANGUAGE sql STABLE STRICT AS $$
                SELECT score FROM fnlesson.obs WHERE person=p ORDER BY id
                $$;
            CREATE FUNCTION fnlesson.scores(p integer)
                RETURNS TABLE(observation_id integer, score integer)
                LANGUAGE sql STABLE STRICT AS $$
                SELECT o.id,o.score FROM fnlesson.obs o WHERE o.person=p
                $$;
            CREATE FUNCTION fnlesson.strict_default(x integer) RETURNS integer
                LANGUAGE sql IMMUTABLE STRICT AS $$ SELECT coalesce(x,99) $$;
            CREATE FUNCTION fnlesson.explicit_default(x integer) RETURNS integer
                LANGUAGE sql IMMUTABLE CALLED ON NULL INPUT AS $$ SELECT coalesce(x,99) $$;
            REVOKE ALL ON ALL FUNCTIONS IN SCHEMA fnlesson FROM PUBLIC;
        """)
        self.assertEqual(self.sql("SELECT fnlesson.scalar_score(1),fnlesson.scalar_score(2),"
                                  "fnlesson.scalar_score(3) IS NULL,fnlesson.scalar_score(4) IS NULL"),
                         "0|5|t|t")
        self.assertEqual(self.sql("SELECT * FROM fnlesson.scores(2) ORDER BY observation_id"),"3|5\n4|5")
        self.assertEqual(self.sql("SELECT count(*) FROM fnlesson.scores(NULL::integer)"),"0")
        self.assertEqual(self.sql("SELECT fnlesson.strict_default(NULL::integer) IS NULL,"
                                  "fnlesson.explicit_default(NULL::integer),fnlesson.strict_default(0)"),
                         "t|99|0")
        # CROSS LATERAL removes the person with no observation; LEFT preserves it.
        self.assertEqual(self.sql("""SELECT p.id,count(*) FROM fnlesson.people p
             CROSS JOIN LATERAL fnlesson.scores(p.id) s GROUP BY p.id ORDER BY p.id"""),
                         "1|2\n2|2\n4|1")
        self.assertEqual(self.sql("""SELECT p.id,count(s.observation_id),count(s.score),
                   coalesce(sum(s.score)::text,'NULL')
             FROM fnlesson.people p LEFT JOIN LATERAL fnlesson.scores(p.id) s ON true
             GROUP BY p.id ORDER BY p.id"""),"1|2|1|0\n2|2|2|10\n3|0|0|NULL\n4|1|0|NULL")
        self.assertEqual(self.sql("""SELECT proretset,proisstrict,provolatile::text
             FROM pg_proc WHERE oid='fnlesson.scores(integer)'::regprocedure"""),"t|t|s")
        self.assertEqual(self.sql("SELECT id,person,score FROM fnlesson.obs ORDER BY id"),
                         "1|1|0\n2|1|\n3|2|5\n4|2|5\n5|4|")

    def function_lookup_setup(self):
        self.sql("""
            -- Deliberately incorrect volatility, only inside the disposable fixture.
            CREATE FUNCTION fnlesson.bad_factor(x integer) RETURNS integer
                LANGUAGE plpgsql IMMUTABLE STRICT AS $$
                BEGIN RETURN x*(SELECT factor FROM fnlesson.config); END;
                $$;
            CREATE FUNCTION fnlesson.live_factor(x integer) RETURNS integer
                LANGUAGE plpgsql STABLE STRICT AS $$
                BEGIN RETURN x*(SELECT factor FROM fnlesson.config); END;
                $$;
            CREATE FUNCTION fnlesson.pure_scale(x integer,f integer) RETURNS integer
                LANGUAGE plpgsql IMMUTABLE STRICT AS $$
                BEGIN RETURN x*f; END;
                $$;
            REVOKE ALL ON ALL FUNCTIONS IN SCHEMA fnlesson FROM PUBLIC;
        """)

    def test_pg_function_false_immutable_cached_plan(self):
        self.function_setup()
        self.function_lookup_setup()
        with self.live_session() as old:
            self.assertEqual(old("SET plan_cache_mode=force_generic_plan")[0],"00000")
            self.assertEqual(old("PREPARE factors AS SELECT fnlesson.bad_factor(2),"
                                 "fnlesson.live_factor(2)")[0],"00000")
            self.assertEqual(old("EXECUTE factors"),("00000","20|20"))
            self.sql("UPDATE fnlesson.config SET factor=100")
            # Cached constant remains stale while the stable lookup sees the new statement snapshot.
            self.assertEqual(old("EXECUTE factors"),("00000","20|200"))
            self.assertEqual(self.sql("SELECT fnlesson.bad_factor(2),fnlesson.live_factor(2)"),"200|200")
            self.assertEqual(old("ALTER FUNCTION fnlesson.bad_factor(integer) STABLE")[0],"00000")
            self.assertEqual(old("DEALLOCATE factors")[0],"00000")
            self.assertEqual(old("PREPARE factors AS SELECT fnlesson.bad_factor(2),"
                                 "fnlesson.live_factor(2)")[0],"00000")
            self.assertEqual(old("EXECUTE factors"),("00000","200|200"))
            self.sql("UPDATE fnlesson.config SET factor=3")
            self.assertEqual(old("EXECUTE factors"),("00000","6|6"))
        self.assertEqual(self.sql("SELECT fnlesson.pure_scale(2,100),fnlesson.pure_scale(2,3)"),"200|6")

    def test_pg_function_strict_side_effect_and_snapshot(self):
        self.function_setup()
        self.sql("""
            CREATE FUNCTION fnlesson.bump(x integer) RETURNS integer
                LANGUAGE plpgsql VOLATILE STRICT AS $$
                DECLARE v integer;
                BEGIN UPDATE fnlesson.counter SET n=n+1 RETURNING n INTO v; RETURN v; END;
                $$;
            CREATE FUNCTION fnlesson.illegal_stable() RETURNS integer
                LANGUAGE plpgsql STABLE AS $$
                BEGIN UPDATE fnlesson.counter SET n=n+10; RETURN 10; END;
                $$;
            CREATE FUNCTION fnlesson.read_stable() RETURNS integer LANGUAGE plpgsql STABLE AS $$
                BEGIN RETURN (SELECT n FROM fnlesson.counter); END;
                $$;
            CREATE FUNCTION fnlesson.read_volatile() RETURNS integer LANGUAGE plpgsql VOLATILE AS $$
                BEGIN RETURN (SELECT n FROM fnlesson.counter); END;
                $$;
            REVOKE ALL ON ALL FUNCTIONS IN SCHEMA fnlesson FROM PUBLIC;
        """)
        with self.live_session() as c:
            self.assertEqual(c("SELECT fnlesson.bump(NULL::integer) IS NULL"),("00000","t"))
            self.assertEqual(self.sql("SELECT n FROM fnlesson.counter"),"0")
            self.assertEqual(c("SELECT sum(fnlesson.bump(g)) FROM generate_series(1,3) g"),("00000","6"))
            self.assertEqual(self.sql("SELECT n FROM fnlesson.counter"),"3")
            self.assertEqual(c("SELECT fnlesson.illegal_stable()")[0],"0A000")
            self.assertEqual(self.sql("SELECT n FROM fnlesson.counter"),"3")
            # One UPDATE statement: stable sees its starting snapshot; volatile sees the update.
            self.assertEqual(c("UPDATE fnlesson.counter SET n=9 RETURNING "
                               "fnlesson.read_stable(),fnlesson.read_volatile()"),("00000","3|9"))
            self.assertEqual(c("SELECT fnlesson.read_stable(),fnlesson.read_volatile()"),("00000","9|9"))
        self.assertEqual(self.sql("SELECT n FROM fnlesson.counter"),"9")

    def test_pg_function_expression_index_wrong_result_and_repair(self):
        self.function_setup()
        self.function_lookup_setup()
        self.sql("""
            CREATE TABLE fnlesson.item(id integer PRIMARY KEY, base integer NOT NULL);
            INSERT INTO fnlesson.item SELECT g,g FROM generate_series(1,100) g;
            CREATE INDEX fnlesson_bad_idx ON fnlesson.item(fnlesson.bad_factor(base));
            ANALYZE fnlesson.item;
        """)
        with self.live_session() as c:
            self.assertEqual(c("CREATE INDEX fnlesson_invalid_idx ON "
                               "fnlesson.item(fnlesson.live_factor(base))")[0],"42P17")
            self.assertEqual(c("SET enable_seqscan=off")[0],"00000")
            self.assertEqual(c("SET enable_bitmapscan=off")[0],"00000")
            q="SELECT id FROM fnlesson.item WHERE fnlesson.bad_factor(base)=20"
            code,plan=c("EXPLAIN (COSTS OFF) "+q)
            self.assertEqual(code,"00000")
            self.assertIn("Index Scan using fnlesson_bad_idx",plan)
            self.assertEqual(c(q),("00000","2"))
            self.sql("UPDATE fnlesson.config SET factor=100")
            # Index entries still contain values computed under factor=10.
            self.assertEqual(c(q),("00000","2"))
            self.assertEqual(c("SELECT fnlesson.bad_factor(2)"),("00000","200"))
            self.assertEqual(c("SET enable_seqscan=on")[0],"00000")
            self.assertEqual(c("SET enable_indexscan=off")[0],"00000")
            self.assertEqual(c("SET enable_indexonlyscan=off")[0],"00000")
            code,plan=c("EXPLAIN (COSTS OFF) "+q)
            self.assertEqual(code,"00000")
            self.assertIn("Seq Scan",plan)
            self.assertEqual(c(q),("00000",""))
            self.assertEqual(c("DROP INDEX fnlesson.fnlesson_bad_idx")[0],"00000")
            self.assertEqual(c("ALTER FUNCTION fnlesson.bad_factor(integer) STABLE")[0],"00000")
            self.assertEqual(c("SELECT id FROM fnlesson.item WHERE fnlesson.bad_factor(base)=200"),
                             ("00000","2"))
            # Explicit fixed factor is a different, genuinely immutable contract.
            self.assertEqual(c("CREATE INDEX fnlesson_pure_idx ON "
                               "fnlesson.item(fnlesson.pure_scale(base,100))")[0],"00000")
            self.assertEqual(c("SET enable_indexscan=on")[0],"00000")
            self.assertEqual(c("SET enable_seqscan=off")[0],"00000")
            good="SELECT id FROM fnlesson.item WHERE fnlesson.pure_scale(base,100)=200"
            code,plan=c("EXPLAIN (COSTS OFF) "+good)
            self.assertEqual(code,"00000")
            self.assertIn("Index Scan using fnlesson_pure_idx",plan)
            self.assertEqual(c(good),("00000","2"))
            self.assertEqual(c("SET enable_seqscan=on")[0],"00000")
            self.assertEqual(c("SET enable_indexscan=off")[0],"00000")
            self.assertEqual(c(good),("00000","2"))
        self.assertEqual(self.sql("SELECT count(*),sum(base) FROM fnlesson.item"),"100|5050")

    def debug_setup(self):
        self.sql("""
            DROP SCHEMA IF EXISTS debuglesson CASCADE;
            CREATE SCHEMA debuglesson;
            REVOKE ALL ON SCHEMA debuglesson FROM PUBLIC;
        """)

    def debug_plan(self, query):
        import json
        # Only fixed synthetic SELECTs are passed to this helper.
        return json.loads(self.sql("EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) "
                                   +query))[0]["Plan"]

    def debug_nodes(self, node):
        yield node
        for child in node.get("Plans", []):
            yield from self.debug_nodes(child)

    def test_pg_debug_sqlstate_constraint_context_and_silent_conflict(self):
        self.debug_setup()
        self.sql("""
            CREATE TABLE debuglesson.registration(
              id integer, alias text,
              CONSTRAINT reg_id PRIMARY KEY(id),
              CONSTRAINT reg_alias UNIQUE(alias));
            INSERT INTO debuglesson.registration VALUES(1,'fixture-a');
            CREATE FUNCTION debuglesson.try_insert(p_id integer,p_alias text)
                RETURNS jsonb LANGUAGE plpgsql AS $$
            DECLARE s text; ns text; tbl text; con text; detail text; ctx text;
            BEGIN
                INSERT INTO debuglesson.registration VALUES(p_id,p_alias);
                RETURN jsonb_build_object('code','OK');
            EXCEPTION WHEN unique_violation THEN
                GET STACKED DIAGNOSTICS s=RETURNED_SQLSTATE,ns=SCHEMA_NAME,
                    tbl=TABLE_NAME,con=CONSTRAINT_NAME,detail=PG_EXCEPTION_DETAIL,
                    ctx=PG_EXCEPTION_CONTEXT;
                -- Inspect sensitive fields only inside the synthetic fixture.
                -- The diagnostic output contains presence/shape, not raw values.
                RETURN jsonb_build_object('code',s,'schema',ns,'table',tbl,
                    'constraint',con,'detail_present',length(detail)>0,
                    'context_matches',position('try_insert' in ctx)>0);
            END;
            $$;
            REVOKE ALL ON FUNCTION debuglesson.try_insert(integer,text) FROM PUBLIC;
        """)
        import json
        for expr, constraint in (("1,'fixture-b'","reg_id"),
                                 ("2,'fixture-a'","reg_alias")):
            actual=json.loads(self.sql("SELECT debuglesson.try_insert("+expr+")"))
            self.assertEqual(actual,dict(code="23505",schema="debuglesson",
                table="registration",constraint=constraint,detail_present=True,
                context_matches=True))
        self.assertEqual(self.sql("SELECT id,alias FROM debuglesson.registration"),"1|fixture-a")
        # Bad import treats all unique violations as harmless duplicates.
        self.assertEqual(self.sql("INSERT INTO debuglesson.registration VALUES(2,'fixture-a') "
                                  "ON CONFLICT DO NOTHING RETURNING id"),"")
        self.assertEqual(self.sql("SELECT count(*) FROM debuglesson.registration"),"1")
        with self.live_session() as c:
            # Target only the intended conflict, surface a different constraint.
            fixed="INSERT INTO debuglesson.registration VALUES"
            tail=" ON CONFLICT ON CONSTRAINT reg_id DO NOTHING RETURNING id"
            self.assertEqual(c(fixed+"(2,'fixture-a')"+tail)[0],"23505")
            self.assertEqual(c(fixed+"(1,'fixture-a')"+tail),("00000",""))
            self.assertEqual(c(fixed+"(2,'fixture-b')"+tail),("00000","2"))
        self.assertEqual(self.sql("SELECT id,alias FROM debuglesson.registration ORDER BY id"),
                         "1|fixture-a\n2|fixture-b")
        self.assertEqual(json.loads(self.sql("SELECT debuglesson.try_insert(3,'fixture-c')")),
                         {"code":"OK"})
        print("PG-DEBUG-CONSTRAINT: same 23505, reg_id vs reg_alias; broad conflict suppressed new row; targeted conflict surfaces alias",flush=True)

    def test_pg_debug_actual_cardinality_and_extended_statistics(self):
        self.debug_setup()
        self.sql("""
            CREATE TABLE debuglesson.measurement(a integer,b integer);
            INSERT INTO debuglesson.measurement
              SELECT g%100,g%100 FROM generate_series(1,10000) g;
            ALTER TABLE debuglesson.measurement ALTER COLUMN a SET STATISTICS 1000;
            ALTER TABLE debuglesson.measurement ALTER COLUMN b SET STATISTICS 1000;
            ANALYZE debuglesson.measurement;
        """)
        query="SELECT a,b FROM debuglesson.measurement WHERE a=7 AND b=7"
        old=self.debug_plan(query)
        self.assertEqual(old["Actual Rows"],100)
        self.assertLess(old["Plan Rows"],10)
        self.assertEqual(old["Actual Loops"],1)
        self.assertIn("Shared Hit Blocks",old)
        self.sql("CREATE STATISTICS debuglesson.measurement_dep (dependencies) "
                 "ON a,b FROM debuglesson.measurement; ANALYZE debuglesson.measurement;")
        new=self.debug_plan(query)
        self.assertEqual(new["Actual Rows"],100)
        self.assertLessEqual(abs(new["Plan Rows"]-100),10)
        self.assertLess(abs(new["Plan Rows"]-100),abs(old["Plan Rows"]-100))
        self.assertEqual(self.sql("SELECT count(*),sum(a),sum(b) FROM debuglesson.measurement"),
                         "10000|495000|495000")
        # Dependencies fix some estimates, not arbitrary impossible combinations.
        self.assertEqual(self.debug_plan("SELECT a,b FROM debuglesson.measurement WHERE a=7 AND b=8")["Actual Rows"],0)
        print("PG-DEBUG-CARDINALITY:",old["Plan Rows"],new["Plan Rows"],new["Actual Rows"],flush=True)

    def test_pg_debug_repeated_scan_and_set_based_repair(self):
        self.debug_setup()
        self.sql("""
            CREATE TABLE debuglesson.person(id integer PRIMARY KEY);
            INSERT INTO debuglesson.person SELECT g FROM generate_series(1,200) g;
            CREATE TABLE debuglesson.observation(person integer, score integer);
            INSERT INTO debuglesson.observation
                SELECT (g%199)+1, CASE WHEN g%5=0 THEN NULL ELSE g%7 END
                FROM generate_series(1,2000) g;
            ANALYZE debuglesson.person;
            ANALYZE debuglesson.observation;
        """)
        bad="""SELECT p.id,(SELECT count(o.score) FROM debuglesson.observation o
                 WHERE o.person=p.id) AS n FROM debuglesson.person p ORDER BY p.id"""
        fixed="""SELECT p.id,coalesce(o.n,0) AS n FROM debuglesson.person p
                 LEFT JOIN (SELECT person,count(score) AS n FROM debuglesson.observation
                            GROUP BY person) o ON o.person=p.id ORDER BY p.id"""
        before=self.debug_plan(bad)
        after=self.debug_plan(fixed)
        def scans(plan):
            return [n for n in self.debug_nodes(plan) if n.get("Relation Name")=="observation"]
        b,a=scans(before),scans(after)
        self.assertEqual(len(b),1)
        self.assertEqual(len(a),1)
        self.assertEqual(b[0]["Actual Loops"],200)
        self.assertEqual(a[0]["Actual Loops"],1)
        self.assertEqual(b[0]["Node Type"],"Seq Scan")
        self.assertEqual(a[0]["Node Type"],"Seq Scan")
        self.assertGreater(b[0]["Shared Hit Blocks"],a[0]["Shared Hit Blocks"])
        old_rows=self.sql(bad)
        new_rows=self.sql(fixed)
        expected={i:0 for i in range(1,201)}
        for g in range(1,2001):
            if g%5:
                expected[(g%199)+1]+=1
        self.assertEqual(old_rows,new_rows)
        self.assertEqual(new_rows,"\n".join(f"{i}|{n}" for i,n in expected.items()))
        self.assertEqual(self.sql("SELECT count(*),count(score) FROM debuglesson.observation"),"2000|1600")
        self.assertEqual(new_rows.splitlines()[-1],"200|0")
        print("PG-DEBUG-SCAN:",b[0]["Actual Loops"],a[0]["Actual Loops"],
              "buffer_hits",b[0]["Shared Hit Blocks"],a[0]["Shared Hit Blocks"],flush=True)

    def test_pg_debug_bounded_timeout_and_error_classification(self):
        self.debug_setup()
        with self.live_session() as c:
            self.assertEqual(c("SET statement_timeout='40ms'")[0],"00000")
            self.assertEqual(c("SELECT pg_sleep(0.5)")[0],"57014")
            self.assertEqual(c("SET statement_timeout=0")[0],"00000")
            self.assertEqual(c("SELECT 1/0")[0],"22012")
            self.assertEqual(c("SELECT 1 FROM debuglesson.missing")[0],"42P01")
            self.assertEqual(c("SELECT 1"),("00000","1"))
        self.assertEqual(self.sql("SELECT count(*) FROM information_schema.tables "
                                  "WHERE table_schema='debuglesson'"),"0")
        print("PG-DEBUG-TIMEOUT: bounded 57014; 22012 and 42P01 distinct; connection recovered",flush=True)

    def isolation_setup(self, count=2):
        self.assertIn(count,(2,3))
        self.sql("""
            DROP SCHEMA IF EXISTS isolesson CASCADE;
            CREATE SCHEMA isolesson;
            REVOKE ALL ON SCHEMA isolesson FROM PUBLIC;
            CREATE TABLE isolesson.reviewer(id integer PRIMARY KEY, active boolean NOT NULL);
            CREATE TABLE isolesson.change_log(id integer PRIMARY KEY);
            INSERT INTO isolesson.reviewer SELECT g,true FROM generate_series(1,"""
            +str(count)+""") g;
        """)

    def isolation_begin(self, session, level):
        self.assertIn(level,("REPEATABLE READ","SERIALIZABLE"))
        self.assertEqual(session("SET statement_timeout='5s'")[0],"00000")
        self.assertEqual(session("BEGIN ISOLATION LEVEL "+level)[0],"00000")
        self.assertEqual(session("SHOW transaction_isolation"),
                         ("00000",level.lower()))
        code,pid=session("SELECT pg_backend_pid()")
        self.assertEqual(code,"00000")
        return int(pid)

    def test_pg_isolation_repeatable_read_write_skew(self):
        self.isolation_setup()
        count="SELECT count(*) FROM isolesson.reviewer WHERE active"
        with self.live_session() as a,self.live_session() as b:
            pa=self.isolation_begin(a,"REPEATABLE READ")
            pb=self.isolation_begin(b,"REPEATABLE READ")
            self.assertNotEqual(pa,pb)
            self.assertEqual(a(count),("00000","2"))
            self.assertEqual(b(count),("00000","2"))
            self.assertEqual(self.sql("SELECT count(*) FROM pg_stat_activity "
                f"WHERE pid IN ({pa},{pb}) AND state='idle in transaction'"),"2")
            # Both locally valid decisions write different rows.
            for session,i in ((a,1),(b,2)):
                self.assertEqual(session(f"UPDATE isolesson.reviewer SET active=false "
                    f"WHERE id={i} RETURNING id"),("00000",str(i)))
                self.assertEqual(session("INSERT INTO isolesson.change_log VALUES"
                    f"({i})")[0],"00000")
                self.assertEqual(session(count),("00000","1"))
            self.assertEqual(self.sql(count),"2")
            self.assertEqual(a("COMMIT")[0],"00000")
            self.assertEqual(b("COMMIT")[0],"00000")
        self.assertEqual(self.sql(count),"0")
        self.assertEqual(self.sql("SELECT id,active FROM isolesson.reviewer ORDER BY id"),
                         "1|f\n2|f")
        self.assertEqual(self.sql("SELECT id FROM isolesson.change_log ORDER BY id"),"1\n2")
        print("PG-ISOLATION-RR: overlapping distinct backends; both commit; active=0",flush=True)

    def test_pg_isolation_serializable_full_retry_recomputes_decision(self):
        count="SELECT count(*) FROM isolesson.reviewer WHERE active"
        # Two reviewers: retry must deny. Three: retry can safely succeed.
        for initial in (2,3):
            with self.subTest(initial=initial):
                self.isolation_setup(initial)
                with self.live_session() as a,self.live_session() as b:
                    pa=self.isolation_begin(a,"SERIALIZABLE")
                    pb=self.isolation_begin(b,"SERIALIZABLE")
                    self.assertNotEqual(pa,pb)
                    for session in (a,b):
                        self.assertEqual(session(count),("00000",str(initial)))
                    self.assertEqual(self.sql("SELECT count(*) FROM pg_stat_activity "
                        f"WHERE pid IN ({pa},{pb}) AND state='idle in transaction'"),"2")
                    statuses={}
                    # Capture conflict at either write or COMMIT; never interpret
                    # COMMIT on an already-aborted transaction as success.
                    for session,i in ((a,1),(b,2)):
                        code,_=session(f"UPDATE isolesson.reviewer SET active=false "
                                       f"WHERE id={i} RETURNING id")
                        if code=="00000":
                            code,_=session(f"INSERT INTO isolesson.change_log VALUES({i})")
                        self.assertIn(code,("00000","40001"))
                        statuses[i]=code
                    for session,i in ((a,1),(b,2)):
                        if statuses[i]=="00000":
                            statuses[i]=session("COMMIT")[0]
                        else:
                            self.assertEqual(session("ROLLBACK")[0],"00000")
                        self.assertIn(statuses[i],("00000","40001"))
                    self.assertEqual(sorted(statuses.values()),["00000","40001"])
                winner=next(i for i,s in statuses.items() if s=="00000")
                loser=next(i for i,s in statuses.items() if s=="40001")
                self.assertEqual(self.sql(count),str(initial-1))
                self.assertEqual(self.sql("SELECT id FROM isolesson.change_log"),str(winner))
                self.assertEqual(self.sql(f"SELECT active FROM isolesson.reviewer WHERE id={loser}"),"t")
                # A known rollback permits a bounded, complete new transaction;
                # recompute the decision rather than reissue the old UPDATE.
                with self.live_session() as retry:
                    self.isolation_begin(retry,"SERIALIZABLE")
                    code,remaining=retry(count)
                    self.assertEqual(code,"00000")
                    self.assertEqual(int(remaining),initial-1)
                    if int(remaining)>1:
                        self.assertEqual(retry(f"UPDATE isolesson.reviewer SET active=false "
                            f"WHERE id={loser} RETURNING id"),("00000",str(loser)))
                        self.assertEqual(retry(f"INSERT INTO isolesson.change_log VALUES({loser})")[0],"00000")
                        decision="ALLOWED"
                    else:
                        decision="DENIED"
                    self.assertEqual(retry("COMMIT")[0],"00000")
                self.assertEqual(decision,"DENIED" if initial==2 else "ALLOWED")
                self.assertEqual(self.sql(count),"1")
                self.assertEqual(self.sql("SELECT id FROM isolesson.change_log ORDER BY id"),
                    str(winner) if initial==2 else "1\n2")
                print("PG-ISOLATION-SSI:",initial,"statuses",statuses,
                      "fresh retry",decision,"active=1",flush=True)

    def test_pg_isolation_savepoint_locks_snapshot_and_sequence(self):
        self.isolation_setup()
        self.sql("""
            CREATE TABLE isolesson.notes(id integer PRIMARY KEY, note text NOT NULL);
            INSERT INTO isolesson.notes VALUES(1,'a'),(2,'b');
            CREATE SEQUENCE isolesson.number_seq;
        """)
        with self.live_session() as a,self.live_session() as b:
            pa=self.isolation_begin(a,"REPEATABLE READ")
            code,pb=b("SELECT pg_backend_pid()")
            self.assertEqual(code,"00000")
            self.assertNotEqual(pa,int(pb))
            self.assertEqual(a("UPDATE isolesson.notes SET note='kept' WHERE id=1")[0],"00000")
            self.assertEqual(a("SAVEPOINT item")[0],"00000")
            self.assertEqual(a("UPDATE isolesson.notes SET note='discarded' WHERE id=2")[0],"00000")
            self.assertEqual(a("SELECT nextval('isolesson.number_seq')"),("00000","1"))
            self.assertEqual(b("SELECT id FROM isolesson.notes WHERE id=2 FOR UPDATE NOWAIT")[0],"55P03")
            self.assertEqual(a("INSERT INTO isolesson.notes VALUES(2,'duplicate')")[0],"23505")
            self.assertEqual(a("SELECT 1")[0],"25P02")
            self.assertEqual(a("ROLLBACK TO SAVEPOINT item")[0],"00000")
            self.assertEqual(a("SELECT id,note FROM isolesson.notes ORDER BY id"),("00000","1|kept\n2|b"))
            # The pre-savepoint lock survives; the later one is released.
            self.assertEqual(b("SELECT id FROM isolesson.notes WHERE id=1 FOR UPDATE NOWAIT")[0],"55P03")
            self.assertEqual(b("SELECT id FROM isolesson.notes WHERE id=2 FOR UPDATE NOWAIT"),
                             ("00000","2"))
            self.assertEqual(b("UPDATE isolesson.notes SET note='external' WHERE id=2")[0],"00000")
            # Rolling back a savepoint doesn't obtain a fresh RR snapshot.
            self.assertEqual(a("SELECT note FROM isolesson.notes WHERE id=2"),("00000","b"))
            self.assertEqual(self.sql("SELECT id,note FROM isolesson.notes ORDER BY id"),"1|a\n2|external")
            self.assertEqual(a("SELECT nextval('isolesson.number_seq')"),("00000","2"))
            self.assertEqual(a("RELEASE SAVEPOINT item")[0],"00000")
            self.assertEqual(a("COMMIT")[0],"00000")
            self.assertEqual(b("SELECT id FROM isolesson.notes WHERE id=1 FOR UPDATE NOWAIT"),
                             ("00000","1"))
        self.assertEqual(self.sql("SELECT id,note FROM isolesson.notes ORDER BY id"),"1|kept\n2|external")
        self.assertEqual(self.sql("SELECT last_value FROM isolesson.number_seq"),"2")
        print("PG-ISOLATION-SAVEPOINT: later lock released, earlier retained; RR snapshot unchanged; sequence gap retained",flush=True)

