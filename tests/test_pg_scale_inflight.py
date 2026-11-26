"""Actual PostgreSQL contention and pre-commit process loss for synthetic scale.

Reuse the verified scale schema. No external DB, HTTP deployment, real data or
installations. The conservative read-only contract does not authorize retries.
"""
import contextlib
import json
import os
from pathlib import Path
import queue
import subprocess
import tempfile
import threading
import time
import unittest

from test_dotnet_scale_persistence import SCHEMA

RECONCILE = """
CREATE FUNCTION scale.observe_intent(s text,k uuid) RETURNS text
LANGUAGE sql STABLE AS $$
 SELECT CASE
 WHEN NOT EXISTS(SELECT 1 FROM scale.issued WHERE key=k AND slot=s) THEN 'DENIED'
 WHEN EXISTS(SELECT 1 FROM scale.answers a JOIN scale.receipts r ON r.answer_id=a.id
             WHERE a.slot=s AND a.key=k AND r.event='ACCEPTED')
 THEN (SELECT 'COMMITTED|'||id FROM scale.answers WHERE slot=s AND key=k)
 WHEN EXISTS(SELECT 1 FROM scale.answers WHERE slot=s AND key<>k) THEN 'CONFLICT'
 ELSE 'UNKNOWN' END
$$;
REVOKE EXECUTE ON FUNCTION scale.observe_intent(text,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION scale.observe_intent(text,uuid) TO scale_writer;
"""

A="11111111-1111-4111-8111-111111111111"
B="22222222-2222-4222-8222-222222222222"
C="33333333-3333-4333-8333-333333333333"
D="44444444-4444-4444-8444-444444444444"


class Live:
    """Bounded, real psql session with explicit dispatch/result boundary."""
    def __init__(self, args, env):
        self.errors=tempfile.TemporaryFile(mode="w+t")
        self.proc=subprocess.Popen(args,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                                   stderr=self.errors,text=True,bufsize=1)
        self.lines=queue.Queue()
        self.reader=threading.Thread(target=self.collect,daemon=True)
        self.reader.start()
        self.pending=False

    def collect(self):
        for line in self.proc.stdout:
            self.lines.put(line.rstrip("\n"))
        self.lines.put(None)

    def send(self, sql):
        if self.pending:
            raise AssertionError("cannot dispatch while an SQL command is pending")
        self.pending=True
        self.proc.stdin.write(sql.rstrip(";")+";\n\\echo __SCALE_RESULT__ :SQLSTATE\n")
        self.proc.stdin.flush()

    def receive(self):
        deadline=time.monotonic()+12
        out=[]
        while True:
            line=self.lines.get(timeout=max(.1,deadline-time.monotonic()))
            if line is None:
                self.errors.seek(0)
                raise AssertionError("owned psql exited: "+self.errors.read()[-2000:])
            if line.startswith("__SCALE_RESULT__ "):
                self.pending=False
                return line.split()[1],"\n".join(out)
            out.append(line)

    def execute(self,sql):
        self.send(sql)
        return self.receive()

    def close(self):
        if self.proc.poll() is None:
            self.proc.kill()
            self.proc.wait(timeout=5)
        self.proc.stdin.close()
        self.reader.join(timeout=5)
        self.proc.stdout.close()
        self.errors.close()


class PgScaleInFlightTests(unittest.TestCase):
    def test_native_observed_lock_precommit_cut_and_unknown_intent(self):
        bins=sorted((p for p in Path("/usr/lib/postgresql").glob("*/bin")
                     if all((p/b).is_file() for b in ("initdb","pg_ctl","psql"))),
                    key=lambda p:int(p.parent.name),reverse=True)
        if not bins or os.geteuid()==0:
            if os.environ.get("GITHUB_ACTIONS")=="true":
                self.fail("PREINSTALLED_NONROOT_POSTGRES_REQUIRED")
            self.skipTest("nonroot PostgreSQL unavailable")
        pg=bins[0]
        with tempfile.TemporaryDirectory(prefix="scale-flight-") as tmp, contextlib.ExitStack() as stack:
            root=Path(tmp).resolve()
            socket=root/"socket"
            socket.mkdir(mode=0o700)
            env={"PATH":os.defpath,"HOME":str(root),"LC_ALL":"C"}
            def run(program,*args):
                p=subprocess.run([str(pg/program),*args],env=env,capture_output=True,text=True,timeout=30)
                self.assertEqual(p.returncode,0,(p.stdout+p.stderr)[-3000:])
                return p.stdout.strip()
            data=str(root/"data")
            run("initdb","-D",data,"-U","lab_admin","--auth-local=trust","--auth-host=scram-sha-256","--no-locale")
            run("pg_ctl","-D",data,"-l",str(root/"pg.log"),"-o",
                "-c listen_addresses='' -c unix_socket_directories="+str(socket)+" -c unix_socket_permissions=0700 -p 5432",
                "-w","start")
            stack.callback(run,"pg_ctl","-D",data,"-m","immediate","-w","stop")
            def args(role="lab_admin",db="scale_lab"):
                self.assertIn(role,("lab_admin","scale_writer"))
                return ["-X","-w","-qAt","-h",str(socket),"-p","5432","-U",role,"-d",db,"-v","ON_ERROR_STOP=1"]
            def sql(query,role="lab_admin",db="scale_lab"):
                return run("psql",*args(role,db),"-c",query)
            sql("CREATE DATABASE scale_lab;",db="postgres")
            sql(SCHEMA+RECONCILE)
            self.assertEqual(sql("SHOW listen_addresses;"),"")
            self.assertEqual(sql("SHOW default_transaction_isolation;"),"read committed")
            self.assertEqual(sql("SHOW fsync;"),"on")
            self.assertEqual(sql("SHOW synchronous_commit;"),"on")
            sql("INSERT INTO scale.issued VALUES "+
                ",".join("('%s','%s')"%(k,s) for k,s in [(A,"SYN-A"),(B,"SYN-B"),(C,"SYN-C"),(D,"SYN-C")]))
            def session():
                s=Live([str(pg/"psql"),*args("scale_writer")],env)
                stack.callback(s.close)
                state,pid=s.execute("SELECT pg_backend_pid()")
                self.assertEqual(state,"00000")
                self.assertEqual(s.execute("SET statement_timeout='20s'")[0],"00000")
                return s,int(pid)
            def call(slot,key,q1=1,q2="NULL",q3=0):
                # Only literal owned constants/integers, no user input.
                return "SELECT scale.submit('%s','%s',%s,%s,%s)"%(slot,key,q1,q2,q3)
            def observe(slot,key):
                return sql("BEGIN READ ONLY; SELECT scale.observe_intent('%s','%s'); COMMIT;"%(slot,key),"scale_writer")
            def snapshot():
                return json.loads(sql("""SELECT json_build_array(
                  COALESCE((SELECT json_agg(json_build_array(slot,key::text,version,q1,q2,q3,id)
                    ORDER BY slot) FROM scale.answers),'[]'::json),
                  COALESCE((SELECT json_agg(json_build_array(answer_id,event)
                    ORDER BY answer_id) FROM scale.receipts),'[]'::json),
                  (SELECT count(*) FROM scale.issued));"""))
            def wait_for(query,expected):
                deadline=time.monotonic()+8
                actual=None
                while time.monotonic()<deadline:
                    actual=sql(query)
                    if actual==expected:return
                    time.sleep(.05)
                self.fail("observed condition not reached: "+str(actual)+" expected "+expected)
            def blocked(waiter,holder):
                wait_for(f"SELECT EXISTS(SELECT 1 FROM pg_stat_activity WHERE pid={waiter} "
                         f"AND wait_event_type='Lock' AND {holder}=ANY(pg_blocking_pids(pid)));","t")
            def result(s,query):
                state,value=s.execute(query)
                self.assertEqual(state,"00000")
                return value
            def accepted(row,slot,key,values):
                self.assertEqual(row[:6],[slot,key,"SYN-V1",*values])
                return row[6]
            self.assertEqual(snapshot(),[[],[],4])
            # A request has performed the write inside a still-open transaction.
            first,pid1=session()
            second,pid2=session()
            self.assertNotEqual(pid1,pid2)
            self.assertEqual(result(first,"BEGIN"),"")
            tentative=result(first,call("SYN-A",A))
            self.assertTrue(tentative.startswith("303|"))
            self.assertEqual(result(first,"SELECT count(*) FROM scale.receipts"),"1")
            # This is the original dangerous inference: the old result is 404
            # even while a transaction can later commit.
            self.assertEqual(sql(f"SELECT scale.reconcile('SYN-A','{A}')","scale_writer"),"404")
            self.assertEqual(observe("SYN-A",A),"UNKNOWN")
            self.assertEqual(snapshot(),[[],[],4])
            second.send(call("SYN-A",A))
            blocked(pid2,pid1)
            self.assertEqual(observe("SYN-A",A),"UNKNOWN")
            self.assertEqual(snapshot(),[[],[],4])
            self.assertEqual(result(first,"COMMIT"),"")
            self.assertEqual(second.receive(),("00000",tentative))
            self.assertEqual(observe("SYN-A",A),"COMMITTED|"+tentative.split("|")[1])
            committed=snapshot()
            id_a=accepted(committed[0][0],"SYN-A",A,[1,None,0])
            self.assertEqual(committed,[[["SYN-A",A,"SYN-V1",1,None,0,id_a]],[[id_a,"ACCEPTED"]],4])
            self.assertEqual(observe("SYN-B",A),"DENIED")
            # Process cut after both writes but before COMMIT. Kill only the
            # owned local psql process. Observe backend exit, not just client exit.
            cut,pid_cut=session()
            self.assertEqual(result(cut,"BEGIN"),"")
            staged=result(cut,call("SYN-B",B,5,"5",4))
            self.assertTrue(staged.startswith("303|"))
            self.assertEqual(result(cut,"SELECT count(*) FROM scale.answers WHERE slot='SYN-B'"),"1")
            self.assertEqual(result(cut,"SELECT count(*) FROM scale.receipts"),"2")
            self.assertEqual(observe("SYN-B",B),"UNKNOWN")
            self.assertEqual(snapshot(),committed)
            cut.proc.kill()
            cut.proc.wait(timeout=5)
            wait_for(f"SELECT NOT EXISTS(SELECT 1 FROM pg_stat_activity WHERE pid={pid_cut});","t")
            self.assertEqual(snapshot(),committed)
            self.assertEqual(observe("SYN-B",B),"UNKNOWN")
            # Recovery authorization here is NOT the UNKNOWN observation:
            # owned writer is proven terminated and no other writer was launched
            # for this intent. The test explicitly permits the same-key retry.
            recovered=sql(call("SYN-B",B,5,"5",4),"scale_writer")
            self.assertTrue(recovered.startswith("303|"))
            self.assertEqual(observe("SYN-B",B),"COMMITTED|"+recovered.split("|")[1])
            after_cut=snapshot()
            id_b=accepted(after_cut[0][1],"SYN-B",B,[5,5,4])
            self.assertNotEqual(id_b,int(staged.split("|")[1]))
            self.assertEqual(after_cut[0][0],committed[0][0])
            self.assertEqual(after_cut[1],sorted([[id_a,"ACCEPTED"],[id_b,"ACCEPTED"]]))
            self.assertEqual(after_cut[2],4)
            # Different keys compete for the same business slot; prove actual
            # blocked backend identity, return conflict, preserve winner.
            winner,pid_w=session()
            loser,pid_l=session()
            self.assertEqual(result(winner,"BEGIN"),"")
            winning=result(winner,call("SYN-C",C,2,"NULL",1))
            self.assertTrue(winning.startswith("303|"))
            loser.send(call("SYN-C",D,4,"4",3))
            blocked(pid_l,pid_w)
            self.assertEqual(observe("SYN-C",C),"UNKNOWN")
            self.assertEqual(observe("SYN-C",D),"UNKNOWN")
            self.assertEqual(snapshot(),after_cut)
            self.assertEqual(result(winner,"COMMIT"),"")
            self.assertEqual(loser.receive(),("00000","409"))
            self.assertEqual(observe("SYN-C",D),"CONFLICT")
            self.assertEqual(observe("SYN-C",C),"COMMITTED|"+winning.split("|")[1])
            final=snapshot()
            id_c=accepted(final[0][2],"SYN-C",C,[2,None,1])
            self.assertEqual(final[0][:2],after_cut[0])
            self.assertEqual(final[1],sorted([[id_a,"ACCEPTED"],[id_b,"ACCEPTED"],[id_c,"ACCEPTED"]]))
            self.assertEqual(final[2],4)
            print("PG-SCALE-INFLIGHT-PASS",sql("SHOW server_version;"),
                  "observed-blockers=2 precommit-client-kill backend-exit unknown-to-commit conflict rows=3 receipts=3",flush=True)
