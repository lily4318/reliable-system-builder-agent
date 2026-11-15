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
