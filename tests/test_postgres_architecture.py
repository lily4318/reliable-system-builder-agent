"""Real native PostgreSQL RLS/transactions/migration; disposable Unix socket only.

No external DB connection or Supabase Auth simulation. CI must execute, not skip.
"""
from concurrent.futures import ThreadPoolExecutor
import os
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
