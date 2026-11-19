"""Native MVC session revocation and serialized research authorization.

Only owned synthetic .NET/PostgreSQL lab. No real accounts or deployment.
The admin mutation locks role state, membership and actual resource through commit.
"""
import contextlib
import http.client as http_client
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode
from test_dotnet_console_mvc import FormToken
from test_dotnet_scale_transfer import SERVICES
from test_dotnet_scale_persistence import SCHEMA
from test_pg_scale_inflight import RECONCILE, Live
from test_dotnet_mvc_admin_authz import (
    ACCESS_SCHEMA, AUTH_HOST, AUTH_DATA, ACCESS, ACCOUNT_CONTROLLER,
    OWNER_CONTROLLER, ADMIN_CONTROLLER, LOGIN_VIEW, SESSION_VIEW, ADMIN_VIEW,
)

REVOCATION_SCHEMA = """
CREATE TABLE scale.actor_state(
 actor text PRIMARY KEY,
 role_name text NOT NULL CHECK(role_name IN ('Participant','Researcher','Viewer')),
 can_review boolean NOT NULL,
 epoch integer NOT NULL DEFAULT 1 CHECK(epoch>0));
INSERT INTO scale.actor_state(actor,role_name,can_review) VALUES
 ('alpha','Participant',false),('beta','Participant',false),('gamma','Participant',false),
 ('staff-a','Researcher',true),('staff-b','Researcher',true),('reader-a','Researcher',false);
CREATE FUNCTION scale.bump_epoch() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 NEW.epoch:=OLD.epoch+1;
 RETURN NEW;
END $$;
CREATE TRIGGER bump_epoch BEFORE UPDATE ON scale.actor_state
FOR EACH ROW EXECUTE FUNCTION scale.bump_epoch();
REVOKE EXECUTE ON FUNCTION scale.bump_epoch() FROM PUBLIC;
GRANT SELECT ON scale.actor_state TO scale_writer;

-- One statement snapshot for the scoped read; no stale authorization alone.
CREATE FUNCTION scale.scoped_study(who text,which text,stamp int)
RETURNS text LANGUAGE sql STABLE AS $$
 SELECT CASE WHEN NOT EXISTS(
  SELECT 1 FROM scale.actor_state p JOIN scale.study_grant g ON g.actor=p.actor
  WHERE p.actor=who AND p.role_name='Researcher' AND p.epoch=stamp AND g.study=which)
 THEN 'DENIED' ELSE (SELECT COALESCE(json_agg(json_build_object(
 'id',a.id,'slot',a.slot,'q1',a.q1,'reviewed',r.answer_id IS NOT NULL)
 ORDER BY a.id),'[]'::json)::text FROM scale.answers a
 JOIN scale.slot_access s ON s.slot=a.slot
 LEFT JOIN scale.reviewed r ON r.answer_id=a.id WHERE s.study=which) END
$$;
-- The trusted web role cannot directly INSERT review rows or change grants.
-- This function is the only review writer; all permission changes in this lab
-- are admin-owned UPDATE/DELETE on the exact same rows. RC row locks stay to commit.
REVOKE INSERT ON scale.reviewed FROM scale_writer;
CREATE FUNCTION scale.review_locked(who text,which text,stamp int,target int)
RETURNS text LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,scale AS $$
BEGIN
 PERFORM 1 FROM scale.actor_state p
 WHERE p.actor=who AND p.role_name='Researcher' AND p.can_review AND p.epoch=stamp
 FOR SHARE;
 IF NOT FOUND THEN RETURN 'STALE'; END IF;
 PERFORM 1 FROM scale.study_grant g WHERE g.actor=who AND g.study=which FOR SHARE;
 IF NOT FOUND THEN RETURN 'DENIED'; END IF;
 PERFORM 1 FROM scale.answers a JOIN scale.slot_access s ON s.slot=a.slot
 WHERE a.id=target AND s.study=which FOR SHARE OF a,s;
 IF NOT FOUND THEN RETURN 'CONFLICT'; END IF;
 INSERT INTO scale.reviewed(answer_id,actor) VALUES(target,who)
 ON CONFLICT(answer_id) DO NOTHING;
 IF NOT FOUND THEN RETURN 'CONFLICT'; END IF;
 RETURN 'APPLIED';
END $$;
REVOKE EXECUTE ON FUNCTION scale.review_locked(text,text,int,int) FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION scale.scoped_study(text,text,int) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION scale.review_locked(text,text,int,int),scale.scoped_study(text,text,int) TO scale_writer;
-- Owned test barrier AFTER review insert and before transaction commit: prove
-- an admin attempting role revocation must actually wait for this writer.
CREATE FUNCTION scale.revocation_barrier() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF NEW.actor='staff-b' THEN PERFORM pg_advisory_xact_lock(92501); END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER revocation_barrier AFTER INSERT ON scale.reviewed
FOR EACH ROW EXECUTE FUNCTION scale.revocation_barrier();
REVOKE EXECUTE ON FUNCTION scale.revocation_barrier() FROM PUBLIC;
"""
REV_DATA = AUTH_DATA[:AUTH_DATA.index("    public string StudyRows(")] + '''
    public string ActorState(string actor)=>Query(
        "SELECT role_name||'|'||can_review::text||'|'||epoch::text FROM scale.actor_state WHERE actor=:'actor';",
        ("actor",actor));
    public string StudyRowsAt(string actor,string study,string stamp)=>Query(
        "SELECT scale.scoped_study(:'actor',:'study',:'stamp'::int);",
        ("actor",actor),("study",study),("stamp",stamp));
    public string ReviewAt(string actor,string study,string stamp,int id)=>Query(
        "SELECT scale.review_locked(:'actor',:'study',:'stamp'::int,:'id'::int);",
        ("actor",actor),("study",study),("stamp",stamp),("id",Num(id)));
''' + AUTH_DATA[AUTH_DATA.index("    public object Snapshot()=>"):]
REV_DATA = REV_DATA.replace("WaitForExit(10000)","WaitForExit(25000)",1)
REV_ACCESS = ACCESS.replace("public sealed class LabAccounts {","public sealed class LabAccounts {",1).replace(
    "    public LabAccounts() {",
    "    private readonly ScaleStore store;\n    public LabAccounts(ScaleStore store) {\n        this.store=store;",1).replace(
    "        var claims=new List<Claim>",
    '''        var state=store.ActorState(name).Split('|');
        if(state.Length!=3)return null;
        var claims=new List<Claim>''',1).replace(
    'new(ClaimTypes.Role,account.Role)};',
    'new(ClaimTypes.Role,state[0]),new("auth_epoch",state[2])};',1).replace(
    'if(account.Review)claims.Add',
    'if(state[1]=="true")claims.Add',1)
REV_HOST = "using System.Security.Claims;\n"+AUTH_HOST.replace(
    "    o.Events.OnRedirectToLogin=",
    '''    o.Events.OnValidatePrincipal=c=>{
        var actor=c.Principal?.FindFirstValue(ClaimTypes.NameIdentifier);
        var stamp=c.Principal?.FindFirstValue("auth_epoch");
        var current=actor is null ? Array.Empty<string>() :
            c.HttpContext.RequestServices.GetRequiredService<ScaleStore>().ActorState(actor).Split('|');
        if(current.Length!=3 || stamp!=current[2])c.RejectPrincipal();
        return Task.CompletedTask;
    };
    o.Events.OnRedirectToLogin=''',1)
REV_ADMIN = ADMIN_CONTROLLER.replace(
    '    private async Task<bool> Allowed',
    '    private string Stamp=>User.FindFirstValue("auth_epoch")!;\n    private async Task<bool> Allowed',1).replace(
    'return View("Index",store.StudyRows(Actor,study));',
    'var rows=store.StudyRowsAt(Actor,study,Stamp);\n        return rows=="DENIED"?NotFound():View("Index",rows);',1).replace(
    'return store.Review(Actor,study,id)?NoContent():Conflict();',
    '''return store.ReviewAt(Actor,study,Stamp,id) switch {
            "APPLIED"=>NoContent(), "DENIED"=>NotFound(),
            "STALE"=>StatusCode(403), "CONFLICT"=>Conflict(),
            _=>StatusCode(503)
        };''',1)

class DotnetMvcAdminRevocationTests(unittest.TestCase):
    def test_native_session_revocation_and_locked_scope(self):
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
        with tempfile.TemporaryDirectory(prefix="mvc-revoke-") as tmp, contextlib.ExitStack() as stack:
            root=Path(tmp).resolve()
            for name in ("home","feed","packages","socket"):
                (root/name).mkdir(mode=0o700)
            env={"PATH":os.defpath,"HOME":str(root/"home"),"DOTNET_CLI_HOME":str(root/"home"),
                 "NUGET_PACKAGES":str(root/"packages"),"NUGET_HTTP_CACHE_PATH":str(root/"http-cache"),
                 "DOTNET_CLI_TELEMETRY_OPTOUT":"1","DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE":"true",
                 "DOTNET_NOLOGO":"1","DOTNET_GENERATE_ASPNET_CERTIFICATE":"false","MSBUILDDISABLENODEREUSE":"1",
                 "LC_ALL":"C.UTF-8","ASPNETCORE_ENVIRONMENT":"Production","ASPNETCORE_URLS":"http://127.0.0.1:0",
                 "SCALE_PSQL":str(pg/"psql"),"SCALE_SOCKET":str(root/"socket")}
            credentials={name:secrets.token_hex(20) for name in ("alpha","beta","gamma","staff-a","staff-b","reader-a")}
            env["SCALE_LAB_ACCOUNTS"]=json.dumps(credentials)
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
            sql(SCHEMA+RECONCILE+ACCESS_SCHEMA+REVOCATION_SCHEMA)
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
            for name,source in {"Program.cs":REV_HOST,"Data/ScaleStore.cs":REV_DATA,"Services/ScaleService.cs":SERVICES,
                                "Controllers/ScaleController.cs":OWNER_CONTROLLER,"Controllers/AccountController.cs":ACCOUNT_CONTROLLER,
                                "Security/Access.cs":REV_ACCESS,"Areas/Admin/Controllers/StudiesController.cs":REV_ADMIN,
                                "Views/Account/Login.cshtml":LOGIN_VIEW,"Views/Account/Session.cshtml":SESSION_VIEW,
                                "Areas/Admin/Views/Studies/Index.cshtml":ADMIN_VIEW}.items():
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
            def host(label):
                path=root/(label+".log")
                with path.open("wb") as log:
                    proc=subprocess.Popen([exe,dll],cwd=app,env=env,stdout=log,stderr=subprocess.STDOUT)
                stack.callback(stop,proc)
                deadline=time.monotonic()+20
                while time.monotonic()<deadline:
                    body=path.read_text(errors="replace")
                    self.assertIsNone(proc.poll(),body[-3000:])
                    m=re.search(r"Now listening on: http://127\.0\.0\.1:(\d+)",body)
                    if m:return proc,int(m.group(1))
                    time.sleep(.05)
                self.fail("host not ready: "+path.read_text(errors="replace")[-3000:])
            def http(port,method,path,fields=None,cookie=None,extra=None):
                headers={}
                if fields is not None:headers["Content-Type"]="application/x-www-form-urlencoded"
                if cookie:headers["Cookie"]=cookie
                if extra:headers.update(extra)
                conn=http_client.HTTPConnection("127.0.0.1",port,timeout=30)
                try:
                    conn.request(method,path,body=urlencode(fields) if fields is not None else None,headers=headers)
                    r=conn.getresponse()
                    return r.status,r.read(65536).decode(),r.getheaders()
                finally:conn.close()
            def snap():
                return json.loads(sql("""SELECT json_build_array(
                  COALESCE((SELECT json_agg(json_build_array(slot,key::text,q1,q2,q3,id) ORDER BY slot) FROM scale.answers),'[]'::json),
                  COALESCE((SELECT json_agg(json_build_array(answer_id,event) ORDER BY answer_id) FROM scale.receipts),'[]'::json),
                  COALESCE((SELECT json_agg(json_build_array(key::text,slot) ORDER BY key) FROM scale.issued),'[]'::json),
                  COALESCE((SELECT json_agg(json_build_array(answer_id,actor) ORDER BY answer_id) FROM scale.reviewed),'[]'::json));"""))
            _,port=host("authz")
            def cookies(reply,jar):
                for k,v in reply[2]:
                    if k.lower()=="set-cookie":
                        pair=v.split(";",1)[0]
                        name,value=pair.split("=",1)
                        if value:jar[name]=value
                        else:jar.pop(name,None)
            def request(method,path,jar=None,fields=None,extra=None):
                return http(port,method,path,fields,
                    "; ".join(k+"="+v for k,v in jar.items()) if jar else None,extra)
            def token(path,jar):
                res=request("GET",path,jar)
                self.assertEqual(res[0],200,res[1])
                cookies(res,jar)
                tokens=FormToken(res[1]).tokens
                self.assertEqual(len(tokens),1)
                return tokens[0]
            def login(name):
                jar={}
                t=token("/account/login",jar)
                bad=request("POST","/account/login",jar,{"Name":name,"Password":"invalid","__RequestVerificationToken":t})
                self.assertEqual(bad[0],401)
                self.assertNotIn(".ScaleLab.Auth",jar)
                good=request("POST","/account/login",jar,{"Name":name,"Password":credentials[name],"__RequestVerificationToken":t})
                self.assertEqual(good[0],204)
                auth=[v for k,v in good[2] if k.lower()=="set-cookie" and v.startswith(".ScaleLab.Auth=")]
                self.assertEqual(len(auth),1)
                self.assertIn("httponly",auth[0].lower())
                self.assertIn("samesite=strict",auth[0].lower())
                cookies(good,jar)
                self.assertTrue(jar.get(".ScaleLab.Auth"))
                return jar,token("/account/session",jar)
            self.assertIn("OnValidatePrincipal",REV_HOST)
            self.assertIn('new("auth_epoch",state[2])',REV_ACCESS)
            self.assertIn("ReviewAt(Actor,study,Stamp,id)",REV_ADMIN)
            self.assertEqual(sql("SHOW transaction_isolation;"),"read committed")
            self.assertEqual(sql("SHOW fsync;"),"on")
            self.assertEqual(snap(),[[],[],[],[]])
            # Seed via real authenticated HTTP, not by bypassing the owner path.
            ids=[]
            for slot,name,q1 in (("SYN-A","alpha",1),("SYN-B","beta",2),("SYN-C","gamma",3)):
                jar,t=login(name)
                response=request("POST","/scale/issue/"+slot,jar,{"__RequestVerificationToken":t})
                self.assertEqual(response[0],200)
                key=response[1]
                form={"Key":key,"Version":"SYN-V1","Q1":str(q1),"Q2":"","Q3":"0","__RequestVerificationToken":t}
                response=request("POST","/scale/new/"+slot,jar,form)
                self.assertEqual(response[0],303,response[1])
                loc=dict((k.lower(),v) for k,v in response[2])["location"]
                ids.append(int(loc.rsplit("/",1)[1]))
            ia,ib,ic=ids
            baseline=snap()
            self.assertEqual(len(baseline[0]),3)
            self.assertEqual(len(baseline[1]),3)
            self.assertEqual(len(baseline[2]),3)
            self.assertEqual(baseline[3],[])
            sa,st=login("staff-a")
            sb,sbt=login("staff-b")
            olda=dict(sa)
            oldb=dict(sb)
            def read(study,jar):
                return request("GET","/admin/studies/"+study,jar)[0]
            def review(study,id,jar,t):
                return request("POST",f"/admin/studies/{study}/review/{id}",jar,{"__RequestVerificationToken":t})[0]
            def as_writer(query,ok=True):
                return run(pg/"psql","-X","-w","-qAt","-h",str(root/"socket"),"-p","5432",
                           "-U","scale_writer","-d","scale_lab","-v","ON_ERROR_STOP=1","-c",query,ok=ok)
            self.assertIn("permission denied",as_writer(f"INSERT INTO scale.reviewed VALUES({ia},'staff-a')",False))
            self.assertIn("permission denied",as_writer("UPDATE scale.actor_state SET can_review=true WHERE actor='reader-a'",False))
            self.assertEqual(read("STUDY-A",sa),200)
            self.assertEqual(read("STUDY-B",sa),404)
            self.assertEqual(read("STUDY-B",sb),200)
            # First exercise committed membership withdrawal with the same cookie.
            sql("DELETE FROM scale.study_grant WHERE actor='staff-a' AND study='STUDY-A';")
            self.assertEqual(request("GET","/account/session",sa)[0],200)
            self.assertEqual(read("STUDY-A",sa),404)
            self.assertEqual(review("STUDY-A",ia,sa,st),404)
            self.assertEqual(snap(),baseline)
            sql("INSERT INTO scale.study_grant VALUES('staff-a','STUDY-A');")
            self.assertEqual(read("STUDY-A",sa),200)
            # Controlled membership grant changes are live, role epochs invalidate
            # existing cookies even when the role is subsequently restored.
            def admin_session():
                live=Live([str(pg/"psql"),"-X","-w","-qAt","-h",str(root/"socket"),"-p","5432",
                           "-U","lab_admin","-d","scale_lab","-v","ON_ERROR_STOP=1"],env)
                stack.callback(live.close)
                state,pid=live.execute("SELECT pg_backend_pid()")
                self.assertEqual(state,"00000")
                return live,int(pid)
            revoker,rpid=admin_session()
            guard,gpid=admin_session()
            def wait_block(holder,role=None,pid=None):
                deadline=time.monotonic()+10
                clause=(f" AND pid={pid}" if pid is not None else f" AND usename='{role}'")
                while time.monotonic()<deadline:
                    rows=sql("SELECT pid FROM pg_stat_activity WHERE datname='scale_lab' "
                             "AND wait_event_type='Lock' "+clause+
                             f" AND {holder}=ANY(pg_blocking_pids(pid));")
                    if rows:
                        self.assertEqual(len(rows.splitlines()),1)
                        return int(rows)
                    time.sleep(.05)
                self.fail("actual backend lock not observed")
            # R1: revoked membership still invisible to middleware at dispatch,
            # but the review function must wait and re-evaluate after COMMIT.
            self.assertEqual(revoker.execute("BEGIN")[0],"00000")
            self.assertEqual(revoker.execute("DELETE FROM scale.study_grant WHERE actor='staff-a' AND study='STUDY-A'")[0],"00000")
            with ThreadPoolExecutor(max_workers=1) as pool:
                f=pool.submit(review,"STUDY-A",ia,sa,st)
                try:
                    wait_block(rpid,role="scale_writer")
                    self.assertEqual(snap(),baseline)
                    self.assertFalse(f.done())
                finally:
                    self.assertEqual(revoker.execute("COMMIT")[0],"00000")
                self.assertEqual(f.result(timeout=30),404)
            self.assertEqual(snap(),baseline)
            self.assertEqual(read("STUDY-A",sa),404)
            sql("INSERT INTO scale.study_grant VALUES('staff-a','STUDY-A');")
            # R2: role revocation wins after an earlier authenticated request.
            self.assertEqual(revoker.execute("BEGIN")[0],"00000")
            self.assertEqual(revoker.execute("UPDATE scale.actor_state SET role_name='Viewer',can_review=false WHERE actor='staff-a'")[0],"00000")
            with ThreadPoolExecutor(max_workers=1) as pool:
                f=pool.submit(review,"STUDY-A",ia,sa,st)
                try:
                    wait_block(rpid,role="scale_writer")
                    self.assertEqual(snap(),baseline)
                    self.assertFalse(f.done())
                finally:
                    self.assertEqual(revoker.execute("COMMIT")[0],"00000")
                self.assertEqual(f.result(timeout=30),403)
            self.assertEqual(snap(),baseline)
            self.assertEqual(request("GET","/account/session",olda)[0],401)
            self.assertEqual(read("STUDY-A",olda),401)
            self.assertEqual(review("STUDY-A",ia,olda,st),401)
            viewer,vt=login("staff-a")
            self.assertEqual(read("STUDY-A",viewer),403)
            self.assertEqual(review("STUDY-A",ia,viewer,vt),403)
            sql("UPDATE scale.actor_state SET role_name='Researcher',can_review=true WHERE actor='staff-a';")
            self.assertEqual(sql("SELECT epoch FROM scale.actor_state WHERE actor='staff-a'"),"3")
            self.assertEqual(read("STUDY-A",olda),401)
            self.assertEqual(read("STUDY-A",viewer),401)
            newa,newt=login("staff-a")
            self.assertEqual(read("STUDY-A",newa),200)
            self.assertEqual(review("STUDY-A",ic,newa,newt),409)
            self.assertEqual(snap(),baseline)
            self.assertEqual(review("STUDY-A",ia,newa,newt),204)
            one=baseline[:3]+[[[ia,"staff-a"]]]
            self.assertEqual(snap(),one)
            # Remove only review permission, not the researcher role or membership.
            sql("UPDATE scale.actor_state SET can_review=false WHERE actor='staff-a';")
            self.assertEqual(read("STUDY-A",newa),401)
            readonly,rt=login("staff-a")
            self.assertEqual(read("STUDY-A",readonly),200)
            self.assertEqual(review("STUDY-A",ib,readonly,rt),403)
            self.assertEqual(snap(),one)
            # R3: the already-authorized write wins; revoke must wait until commit.
            self.assertEqual(guard.execute("SELECT pg_advisory_lock(92501)")[0],"00000")
            with ThreadPoolExecutor(max_workers=1) as pool:
                f=pool.submit(review,"STUDY-B",ic,sb,sbt)
                released=False
                try:
                    wpid=wait_block(gpid,role="scale_writer")
                    self.assertEqual(snap(),one)
                    self.assertEqual(revoker.execute("BEGIN")[0],"00000")
                    revoker.send("UPDATE scale.actor_state SET role_name='Viewer',can_review=false WHERE actor='staff-b'")
                    self.assertEqual(wait_block(wpid,pid=rpid),rpid)
                    self.assertEqual(snap(),one)
                    self.assertFalse(f.done())
                    self.assertEqual(guard.execute("SELECT pg_advisory_unlock(92501)"),("00000","t"))
                    released=True
                    self.assertEqual(f.result(timeout=30),204)
                    self.assertEqual(revoker.receive()[0],"00000")
                    self.assertEqual(revoker.execute("COMMIT")[0],"00000")
                finally:
                    if not released:
                        guard.execute("SELECT pg_advisory_unlock(92501)")
                    if revoker.pending:
                        revoker.receive()
                    revoker.execute("ROLLBACK")
            final=baseline[:3]+[sorted([[ia,"staff-a"],[ic,"staff-b"]])]
            self.assertEqual(snap(),final)
            self.assertEqual(read("STUDY-B",oldb),401)
            self.assertEqual(review("STUDY-B",ic,oldb,sbt),401)
            freshb,fbt=login("staff-b")
            self.assertEqual(read("STUDY-B",freshb),403)
            self.assertEqual(review("STUDY-B",ic,freshb,fbt),403)
            self.assertEqual(snap(),final)
            self.assertEqual(sql("SELECT epoch||'|'||role_name FROM scale.actor_state WHERE actor='staff-b'"),"2|Viewer")
            self.assertEqual(sql("SELECT count(*) FROM scale.reviewed WHERE answer_id="+str(ib)),"0")
            print(f"DOTNET-MVC-ADMIN-REVOCATION-PASS sdk={sdk} pg={version} live-membership epoch-cookie role-permission-downgrade actual-locks=4 revoke-first=2 writer-first=1 scoped-read locked-review direct-dml-denied rows=3 reviews=2",flush=True)
