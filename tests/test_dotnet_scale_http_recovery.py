"""Native synthetic MVC recovery with real TCP disconnect and owned DB role fence.

No external database, real participant data, deployment or package downloads.
The old bridge is deliberately not canceled on HTTP abort to reproduce ambiguity.
Role fence is a controlled lab boundary, not a production distributed protocol.
"""
import contextlib
import http.client as http_client
import json
import os
from pathlib import Path
import re
import shutil
import socket as tcp_socket
import struct
import subprocess
import tempfile
import time
import unittest
from urllib.parse import urlencode
from test_dotnet_console_mvc import FormToken
from test_dotnet_scale_transfer import SERVICES, ENTRY
from test_dotnet_scale_persistence import SCHEMA, HOST, DATA, CONTROLLER
from test_pg_scale_inflight import RECONCILE, Live

# Dedicated role identities for this isolated cluster. Recovery cannot log in
# until the old writer is fenced; the observer can only read.
FENCE_SCHEMA = """
CREATE ROLE scale_observer LOGIN;
GRANT USAGE ON SCHEMA scale TO scale_observer;
GRANT SELECT ON scale.issued,scale.answers,scale.receipts TO scale_observer;
GRANT EXECUTE ON FUNCTION scale.observe_intent(text,uuid) TO scale_observer;
CREATE ROLE scale_recovery NOLOGIN IN ROLE scale_writer;
CREATE FUNCTION scale.lab_barrier() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE s text;
BEGIN
 SELECT slot INTO s FROM scale.answers WHERE id=NEW.answer_id;
 IF s='SYN-A' THEN PERFORM pg_advisory_xact_lock(91401);
 ELSIF s='SYN-B' THEN PERFORM pg_advisory_xact_lock(91402);
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER lab_barrier AFTER INSERT ON scale.receipts
FOR EACH ROW EXECUTE FUNCTION scale.lab_barrier();
REVOKE EXECUTE ON FUNCTION scale.lab_barrier() FROM PUBLIC;
"""

# Reuse the tested input validation and fixed psql-parameter bridge.
# No role selection or SQL text is obtained from the HTTP client.
HTTP_DATA = DATA.replace(
    'private readonly string exe=',
    '''private readonly string role=Environment.GetEnvironmentVariable("SCALE_ROLE") switch {
        "scale_writer"=>"scale_writer", "scale_observer"=>"scale_observer",
        "scale_recovery"=>"scale_recovery", _=>throw new InvalidOperationException("lab role required")
    };
    private readonly string exe=''',
    1).replace('"-U","scale_writer"','"-U",role',1).replace(
    'WaitForExit(10000)','WaitForExit(45000)',1).replace(
    'SELECT scale.reconcile(:\'s\',:\'k\'::uuid);',
    'BEGIN READ ONLY; SELECT scale.observe_intent(:\'s\',:\'k\'::uuid); COMMIT;',1)

# Deliberately record client cancellation but leave transaction outcome
# uncertain. The lab simulates a writer not canceled by transport failure.
HTTP_CONTROLLER = CONTROLLER.replace(
    'var r=service.Submit(slot,Request.Form);',
    '''using var abort=HttpContext.RequestAborted.Register(
            ()=>Console.WriteLine("SYNTHETIC_CLIENT_ABORTED"));
        var r=service.Submit(slot,Request.Form);''',1).replace(
    '''        // Owned synthetic fixture only: simulate committed response loss, not production fault API.
        if(Request.Headers["X-Synthetic-Lose-Ack"]=="1") {HttpContext.Abort();return new EmptyResult();}
''','',1).replace(
    '''        if(!ScaleService.ValidSlot(slot)||!Guid.TryParseExact(key,"D",out _))return BadRequest();
        var parts=store.Reconcile(slot,key).Split('|');
        return parts[0]=="303"?Content("/scale/receipt/"+parts[1]):StatusCode(int.Parse(parts[0]));''',
    '''        Response.Headers.CacheControl="no-store";
        if(!ScaleService.ValidSlot(slot)||!Guid.TryParseExact(key,"D",out _))return BadRequest();
        var parts=store.Reconcile(slot,key).Split('|');
        return parts[0] switch {
            "UNKNOWN" when parts.Length==1 => StatusCode(202,new {state="UNKNOWN"}),
            "COMMITTED" when parts.Length==2 && int.TryParse(parts[1],out _) =>
                Ok(new {state="COMMITTED",receipt=Url.Action(nameof(Receipt),new{id=int.Parse(parts[1])})}),
            "CONFLICT" when parts.Length==1 => StatusCode(409,new {state="CONFLICT"}),
            "DENIED" when parts.Length==1 => StatusCode(403,new {state="DENIED"}),
            _ => StatusCode(503,new {state="UNAVAILABLE"})
        };''',1)


class DotnetScaleHttpRecoveryTests(unittest.TestCase):
    def test_native_http_disconnect_readonly_reconcile_and_role_fence(self):
        exe=shutil.which("dotnet")
        bins=sorted((p for p in Path("/usr/lib/postgresql").glob("*/bin")
                     if all((p/b).is_file() for b in ("initdb","pg_ctl","psql"))),
                    key=lambda p:int(p.parent.name),reverse=True)
        if not exe or not bins or os.geteuid()==0:
            if os.environ.get("GITHUB_ACTIONS")=="true":
                self.fail("PREINSTALLED_DOTNET_AND_NONROOT_POSTGRES_REQUIRED")
            self.skipTest("native .NET and non-root PostgreSQL unavailable")
        exe=str(Path(exe).resolve())
        pg=bins[0]
        with tempfile.TemporaryDirectory(prefix="scale-http-recovery-") as tmp, contextlib.ExitStack() as stack:
            root=Path(tmp).resolve()
            for name in ("home","feed","packages","socket"):
                (root/name).mkdir(mode=0o700)
            env={"PATH":os.defpath,"HOME":str(root/"home"),"DOTNET_CLI_HOME":str(root/"home"),
                 "NUGET_PACKAGES":str(root/"packages"),"NUGET_HTTP_CACHE_PATH":str(root/"http-cache"),
                 "DOTNET_CLI_TELEMETRY_OPTOUT":"1","DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE":"true",
                 "DOTNET_NOLOGO":"1","DOTNET_GENERATE_ASPNET_CERTIFICATE":"false","MSBUILDDISABLENODEREUSE":"1",
                 "LC_ALL":"C.UTF-8","ASPNETCORE_ENVIRONMENT":"Production","ASPNETCORE_URLS":"http://127.0.0.1:0",
                 "SCALE_PSQL":str(pg/"psql"),"SCALE_SOCKET":str(root/"socket")}
            def run(program,*args,cwd=root,ok=True):
                result=subprocess.run([str(program),*args],cwd=cwd,env=env,capture_output=True,text=True,timeout=45)
                self.assertEqual(result.returncode==0,ok,(result.stdout+result.stderr)[-4000:])
                return result.stdout.strip() if ok else result.stderr
            data=str(root/"data")
            run(pg/"initdb","-D",data,"-U","lab_admin","--auth-local=trust","--auth-host=scram-sha-256","--no-locale")
            start_options=("-D",data,"-l",str(root/"pg.log"),"-o",
                           "-c listen_addresses='' -c unix_socket_directories="+str(root/"socket")+" -c unix_socket_permissions=0700 -p 5432","-w","start")
            run(pg/"pg_ctl",*start_options)
            stack.callback(run,pg/"pg_ctl","-D",data,"-m","immediate","-w","stop")
            def sql(query,db="scale_lab",ok=True):
                return run(pg/"psql","-X","-w","-qAt","-h",str(root/"socket"),"-p","5432","-U","lab_admin","-d",db,"-v","ON_ERROR_STOP=1","-c",query,ok=ok)
            sql("CREATE DATABASE scale_lab;","postgres")
            sql(SCHEMA+RECONCILE+FENCE_SCHEMA)
            version=sql("SHOW server_version;")
            self.assertEqual(sql("SHOW listen_addresses;"),"")
            sdk_versions=[]
            for line in run(exe,"--list-sdks").splitlines():
                m=re.fullmatch(r"(10\.0\.\d+) \[(.+)\]",line.strip())
                if m:
                    v,sdkdir=m.groups()
                    base=Path(sdkdir).parent
                    needed=("packs/Microsoft.NETCore.App.Ref","packs/Microsoft.AspNetCore.App.Ref","shared/Microsoft.NETCore.App","shared/Microsoft.AspNetCore.App")
                    if all(any((base/x).glob("10.0.*")) for x in needed):sdk_versions.append(v)
            self.assertTrue(sdk_versions,"missing installed SDK/runtime/reference packs")
            sdk=max(sdk_versions,key=lambda v:tuple(map(int,v.split("."))))
            (root/"global.json").write_text(json.dumps({"sdk":{"version":sdk,"rollForward":"disable","allowPrerelease":False}}))
            for name in ("Directory.Build.props","Directory.Build.targets"):(root/name).write_text("<Project />")
            (root/"Directory.Build.rsp").write_text("")
            config=root/"NuGet.Config"
            config.write_text('<configuration><packageSources><clear/><add key="local" value="feed"/></packageSources></configuration>')
            self.assertEqual(run(exe,"--version"),sdk)
            app=root/"ScaleMvc"
            run(exe,"new","mvc","--name","ScaleMvc","--output",str(app),"--no-restore","--no-https","--auth","None","--exclude-launch-settings")
            for name,source in {"Program.cs":HOST,"Data/ScaleStore.cs":HTTP_DATA,"Services/ScaleService.cs":SERVICES,
                                "Controllers/ScaleController.cs":HTTP_CONTROLLER,"Views/Scale/Entry.cshtml":ENTRY}.items():
                p=app/name
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text(source)
            project=str(app/"ScaleMvc.csproj")
            run(exe,"restore",project,"--configfile",str(config),"--packages",str(root/"packages"),"--disable-build-servers","-p:NuGetAudit=false")
            run(exe,"build",project,"--no-restore","--disable-build-servers","-p:UseAppHost=false")
            dll=str(app/"bin/Debug/net10.0/ScaleMvc.dll")
            def stop(proc,hard=False):
                if proc.poll() is None:
                    (proc.kill if hard else proc.terminate)()
                    try:proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
            def host(label,role):
                path=root/(label+".log")
                with path.open("wb") as log:
                    proc=subprocess.Popen([exe,dll],cwd=app,env=dict(env,SCALE_ROLE=role),stdout=log,stderr=subprocess.STDOUT)
                stack.callback(stop,proc)
                deadline=time.monotonic()+20
                while time.monotonic()<deadline:
                    body=path.read_text(errors="replace")
                    self.assertIsNone(proc.poll(),body[-3000:])
                    m=re.search(r"Now listening on: http://127\.0\.0\.1:(\d+)",body)
                    if m:return proc,int(m.group(1))
                    time.sleep(.05)
                self.fail("host not ready: "+path.read_text(errors="replace")[-3000:])
            def http(port,method,path,fields=None,cookie=None,lose=False):
                headers={}
                if fields is not None:headers["Content-Type"]="application/x-www-form-urlencoded"
                if cookie:headers["Cookie"]=cookie
                if lose:headers["X-Synthetic-Lose-Ack"]="1"
                conn=http_client.HTTPConnection("127.0.0.1",port,timeout=15)
                try:
                    conn.request(method,path,body=urlencode(fields) if fields is not None else None,headers=headers)
                    r=conn.getresponse()
                    return r.status,r.read(65536).decode(),r.getheaders()
                finally:conn.close()
            def form(port,slot):
                status,body,hs=http(port,"GET","/scale/new/"+slot)
                self.assertEqual(status,200)
                token=FormToken(body).tokens
                self.assertEqual(len(token),1)
                key=re.search(r'name="Key" value="([0-9a-f-]{36})"',body)
                self.assertIsNotNone(key)
                cookies=[v.split(";",1)[0] for k,v in hs if k.lower()=="set-cookie" and v.startswith(".AspNetCore.Antiforgery.")]
                self.assertEqual(len(cookies),1)
                return {"Key":key.group(1),"Version":"SYN-V1","Q1":"1","Q2":"","Q3":"0","__RequestVerificationToken":token[0]},cookies[0]
            def post(port,slot,data,cookie,lose=False):
                return http(port,"POST","/scale/new/"+slot,data,cookie,lose)
            def receipt(reply):
                self.assertEqual(reply[0],303)
                urls=[v for k,v in reply[2] if k.lower()=="location"]
                self.assertEqual(len(urls),1)
                return urls[0]
            # Independent admin SQL oracle, no application snapshot API.
            def snapshot():
                return json.loads(sql("""SELECT json_build_object(
                  'answers',COALESCE((SELECT json_agg(json_build_array(slot,key::text,version,q1,q2,q3,id) ORDER BY slot) FROM scale.answers),'[]'::json),
                  'receipts',COALESCE((SELECT json_agg(json_build_array(answer_id,event) ORDER BY answer_id) FROM scale.receipts),'[]'::json),
                  'issued',(SELECT count(*) FROM scale.issued));"""))
            def check_rows(expect,issued):
                got=snapshot()
                self.assertEqual(got["issued"],issued)
                self.assertEqual([row[:6] for row in got["answers"]],expect)
                ids=sorted(row[6] for row in got["answers"])
                self.assertEqual(got["receipts"],[[i,"ACCEPTED"] for i in ids])
                return got
            # Independent observer does not need, and cannot acquire, writer rights.
            self.assertIn("BEGIN READ ONLY", HTTP_DATA)
            self.assertIn("SYNTHETIC_CLIENT_ABORTED", HTTP_CONTROLLER)
            self.assertNotIn("X-Synthetic-Lose-Ack", HTTP_CONTROLLER)
            self.assertIn('"-U",role', HTTP_DATA)
            self.assertEqual(sql("SHOW fsync;"),"on")
            self.assertEqual(sql("SHOW synchronous_commit;"),"on")
            def as_role(role,query,ok=True):
                return run(pg/"psql","-X","-w","-qAt","-h",str(root/"socket"),
                           "-p","5432","-U",role,"-d","scale_lab","-v","ON_ERROR_STOP=1",
                           "-c",query,ok=ok)
            self.assertIn("not permitted to log in",as_role("scale_recovery","SELECT 1",False))
            self.assertIn("permission denied",as_role("scale_observer","DELETE FROM scale.answers",False))
            old,p1=host("old","scale_writer")
            reader,p2=host("observer","scale_observer")
            a,ac=form(p1,"SYN-A")
            alternate,_=form(p1,"SYN-A")
            b,bc=form(p1,"SYN-B")
            b.update(Q1="5",Q2="5",Q3="4")
            initial=check_rows([],3)
            def observe(slot,key,code,state,location=None):
                status,body,headers=http(p2,"GET","/scale/reconcile/"+slot+"/"+key)
                self.assertEqual(status,code,body)
                self.assertIn("no-store",dict((k.lower(),v) for k,v in headers).get("cache-control",""))
                expected={"state":state}
                if location is not None:expected["receipt"]=location
                self.assertEqual(json.loads(body),expected)
            def wait_for(check,label,seconds=10):
                deadline=time.monotonic()+seconds
                while time.monotonic()<deadline:
                    value=check()
                    if value:return value
                    time.sleep(.05)
                self.fail("condition not observed: "+label)
            guard=Live([str(pg/"psql"),"-X","-w","-qAt","-h",str(root/"socket"),
                        "-p","5432","-U","lab_admin","-d","scale_lab","-v","ON_ERROR_STOP=1"],env)
            stack.callback(guard.close)
            state,pid=guard.execute("SELECT pg_backend_pid()")
            self.assertEqual(state,"00000")
            holder=int(pid)
            def locked_backend():
                # Derive exact waiting backend from PostgreSQL, not a timing guess.
                got=sql("SELECT pid FROM pg_stat_activity WHERE usename='scale_writer' "
                        "AND datname='scale_lab' AND wait_event_type='Lock' "
                        f"AND {holder}=ANY(pg_blocking_pids(pid));")
                if not got:return None
                self.assertEqual(len(got.splitlines()),1)
                return int(got)
            def acquire(number):
                self.assertEqual(guard.execute(f"SELECT pg_advisory_lock({number})")[0],"00000")
            def release(number):
                self.assertEqual(guard.execute(f"SELECT pg_advisory_unlock({number})"),("00000","t"))
            def start_post(slot,fields,cookie):
                payload=urlencode(fields).encode("ascii")
                s=tcp_socket.create_connection(("127.0.0.1",p1),timeout=5)
                stack.callback(s.close)
                s.sendall((f"POST /scale/new/{slot} HTTP/1.1\r\nHost: 127.0.0.1:{p1}\r\n"
                           f"Content-Type: application/x-www-form-urlencoded\r\nCookie: {cookie}\r\n"
                           f"Content-Length: {len(payload)}\r\nConnection: close\r\n\r\n").encode("ascii")+payload)
                return s
            def disconnect(s,expected_count):
                # Actual abortive TCP close after proving the request is in DB.
                s.setsockopt(tcp_socket.SOL_SOCKET,tcp_socket.SO_LINGER,struct.pack("ii",1,0))
                s.close()
                wait_for(lambda:(root/"old.log").read_text(errors="replace").count("SYNTHETIC_CLIENT_ABORTED")>=expected_count,
                         "Kestrel request-aborted callback")
            unknown=lambda slot,key:observe(slot,key,202,"UNKNOWN")
            unknown("SYN-A",a["Key"])
            observe("SYN-B",a["Key"],403,"DENIED")
            self.assertEqual(http(p2,"GET","/scale/reconcile/SYN-A/not-a-guid")[0],400)
            self.assertEqual(snapshot(),initial)
            # A: request has staged both answer and receipt, AFTER INSERT barrier.
            acquire(91401)
            first=start_post("SYN-A",a,ac)
            pid_a=wait_for(locked_backend,"first HTTP writer blocked in database")
            unknown("SYN-A",a["Key"])
            self.assertEqual(snapshot(),initial)
            disconnect(first,1)
            self.assertEqual(locked_backend(),pid_a)
            unknown("SYN-A",a["Key"])
            self.assertEqual(snapshot(),initial)
            release(91401)
            wait_for(lambda:sql("SELECT count(*) FROM scale.answers WHERE slot='SYN-A'")=="1",
                     "late commit after client disconnect")
            ea=["SYN-A",a["Key"],"SYN-V1",1,None,0]
            committed=check_rows([ea],3)
            loc_a="/scale/receipt/"+str(committed["answers"][0][6])
            observe("SYN-A",a["Key"],200,"COMMITTED",loc_a)
            observe("SYN-A",alternate["Key"],409,"CONFLICT")
            self.assertEqual(http(p2,"GET",loc_a)[:2],(200,"Synthetic receipt "+loc_a.rsplit("/",1)[1]))
            unknown("SYN-B",b["Key"])
            self.assertEqual(snapshot(),committed)
            # B: the same transport failure, but a different DB outcome.
            acquire(91402)
            second=start_post("SYN-B",b,bc)
            pid_b=wait_for(locked_backend,"second HTTP writer blocked in database")
            self.assertNotEqual(pid_a,pid_b)
            disconnect(second,2)
            self.assertEqual(locked_backend(),pid_b)
            unknown("SYN-B",b["Key"])
            self.assertEqual(snapshot(),committed)
            # Fence the entire old login generation before releasing the lock.
            # NOLOGIN alone does not end existing sessions: prove both.
            sql("ALTER ROLE scale_writer NOLOGIN;")
            self.assertIn("not permitted to log in",as_role("scale_writer","SELECT 1",False))
            self.assertEqual(sql(f"SELECT pg_terminate_backend({pid_b});"),"t")
            wait_for(lambda:sql("SELECT count(*) FROM pg_stat_activity WHERE usename='scale_writer'")=="0",
                     "old writer generation drained")
            stop(old,hard=True)
            self.assertIsNotNone(old.poll())
            self.assertEqual(sql("SELECT rolcanlogin FROM pg_roles WHERE rolname='scale_writer'"),"f")
            self.assertEqual(sql("SELECT count(*) FROM pg_stat_activity WHERE usename='scale_writer'"),"0")
            release(91402)
            unknown("SYN-B",b["Key"])
            self.assertEqual(snapshot(),committed)
            self.assertIn("not permitted to log in",as_role("scale_recovery","SELECT 1",False))
            # Explicit recovery authorization in this owned test only.
            # No automatic retry, no newly issued intent for SYN-B.
            sql("ALTER ROLE scale_recovery LOGIN;")
            new,p3=host("recovery","scale_recovery")
            self.assertNotEqual(new.pid,old.pid)
            # Obtain a fresh CSRF pair on the otherwise unused synthetic slot.
            fresh,fc=form(p3,"SYN-C")
            fresh.update(Key=b["Key"],Q1=b["Q1"],Q2=b["Q2"],Q3=b["Q3"])
            eb=["SYN-B",b["Key"],"SYN-V1",5,5,4]
            loc_b=receipt(post(p3,"SYN-B",fresh,fc))
            final=check_rows([ea,eb],4)
            self.assertEqual(loc_b,"/scale/receipt/"+str(final["answers"][1][6]))
            observe("SYN-B",b["Key"],200,"COMMITTED",loc_b)
            self.assertEqual(receipt(post(p3,"SYN-B",fresh,fc)),loc_b)
            self.assertEqual(post(p3,"SYN-B",dict(fresh,Q2="4"),fc)[0],409)
            self.assertEqual(snapshot(),final)
            self.assertIn("not permitted to log in",as_role("scale_writer","SELECT 1",False))
            self.assertEqual(sql("SELECT count(*) FROM pg_stat_activity WHERE usename='scale_writer'"),"0")
            print(f"DOTNET-PG-HTTP-RECOVERY-PASS sdk={sdk} pg={version} tcp-aborts=2 actual-db-blockers=2 late-commit role-fence rollback same-key-recovery readonly-four-states rows=2 receipts=2",flush=True)
