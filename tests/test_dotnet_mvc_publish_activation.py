"""Native MVC Release publish and local activation with verified recovery checkpoint.
Only owned temporary PostgreSQL and loopback hosts. No deployment or third-party packages.
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
from urllib.parse import urlencode
from test_dotnet_console_mvc import FormToken
from test_dotnet_scale_transfer import SERVICES
from test_dotnet_scale_persistence import SCHEMA
from test_pg_scale_inflight import RECONCILE
from test_dotnet_mvc_admin_authz import (
    ACCESS_SCHEMA, ACCOUNT_CONTROLLER, OWNER_CONTROLLER, LOGIN_VIEW, SESSION_VIEW, ADMIN_VIEW,
)
from test_dotnet_mvc_admin_revocation import REVOCATION_SCHEMA, REV_ADMIN
from test_dotnet_backup_publish import BACKUP_HOST, BACKUP_ACCESS, BACKUP_DATA, inventory

RELEASE_SCHEMA = """
CREATE TABLE scale.release_contract(id integer PRIMARY KEY CHECK(id=1), revision integer NOT NULL);
INSERT INTO scale.release_contract VALUES(1,2);
GRANT SELECT ON scale.release_contract TO scale_writer;
"""
PUBLISH_DATA = BACKUP_DATA.replace(
    '    public string ActorState(string actor)=>',
    '''    public bool Ready() {
        try {
            return Query(@"BEGIN READ ONLY;
                SELECT (SELECT revision=2 FROM scale.release_contract WHERE id=1)
                  AND (SELECT count(*)>=0 FROM
                    (SELECT a.id,a.slot,a.key,a.version,a.q1,a.q2,a.q3,r.event,p.epoch,
                            p.role_name,p.can_review,g.study,s.owner_id
                     FROM scale.answers a JOIN scale.receipts r ON r.answer_id=a.id
                     JOIN scale.slot_access s ON s.slot=a.slot
                     CROSS JOIN scale.actor_state p CROSS JOIN scale.study_grant g LIMIT 0) required_columns)
                  AND has_function_privilege(current_user,'scale.review_locked(text,text,integer,integer)','EXECUTE')
                  AND has_function_privilege(current_user,'scale.observe_intent(text,uuid)','EXECUTE');
                COMMIT;")=="t";
        } catch {return false;}
    }
    public string ActorState(string actor)=>''',1)
READINESS = '''using Microsoft.Extensions.Diagnostics.HealthChecks;
using ScaleMvc.Data;
namespace ScaleMvc.Security;
public sealed class ReleaseReadiness(ScaleStore store):IHealthCheck {
    public Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context,
            CancellationToken cancellationToken=default) =>
        Task.FromResult(store.Ready()?HealthCheckResult.Healthy():HealthCheckResult.Unhealthy());
}
'''
PUBLISH_HOST = 'using Microsoft.AspNetCore.Diagnostics.HealthChecks;\nusing System.Text.RegularExpressions;\n'+BACKUP_HOST.replace(
    'var builder=WebApplication.CreateBuilder(args);',
    '''var builder=WebApplication.CreateBuilder(args);
var db=builder.Configuration["Release:Database"];
var label=builder.Configuration["Release:Label"];
if(db is not ("scale_lab" or "scale_stage") || label is not ("source" or "candidate") ||
    !Regex.IsMatch(Environment.GetEnvironmentVariable("SCALE_RESTORE_GENERATION")??"","^[a-f0-9]{32}$"))
    throw new InvalidOperationException("RELEASE_CONFIG_INVALID");
Environment.SetEnvironmentVariable("SCALE_DATABASE",db);
builder.Services.AddHealthChecks().AddCheck<ReleaseReadiness>("schema",tags:new[]{"ready"});''',1).replace(
    "app.UseAuthentication();",
    '''app.Use(async (ctx,next)=>{
    if(!ctx.Request.Path.StartsWithSegments("/health") &&
        !ctx.RequestServices.GetRequiredService<ScaleStore>().Ready()) {
        ctx.Response.StatusCode=503;
        ctx.Response.Headers.CacheControl="no-store";
        await ctx.Response.WriteAsync("Unavailable");
        return;
    }
    await next();
});
app.UseAuthentication();''',1).replace(
    'app.MapControllers();',
    '''app.UseStaticFiles();
app.MapHealthChecks("/health/live",new HealthCheckOptions{Predicate=_=>false}).AllowAnonymous();
app.MapHealthChecks("/health/ready",new HealthCheckOptions{Predicate=c=>c.Tags.Contains("ready")}).AllowAnonymous();
app.MapGet("/release",()=>Results.Text(label!)).AllowAnonymous();
app.MapControllers();''',1)

class DotnetMvcPublishActivationTests(unittest.TestCase):
    def test_native_mvc_release_health_and_restore_activation_gate(self):
        exe=shutil.which("dotnet")
        bins=sorted((p for p in Path("/usr/lib/postgresql").glob("*/bin")
                     if all((p/b).is_file() for b in ("initdb","pg_ctl","psql","pg_dump","pg_restore"))),
                    key=lambda p:int(p.parent.name),reverse=True)
        if not exe or not bins or os.geteuid()==0:
            if os.environ.get("GITHUB_ACTIONS")=="true":
                self.fail("PREINSTALLED_DOTNET_AND_NONROOT_POSTGRES_REQUIRED")
            self.skipTest("native .NET and non-root PostgreSQL unavailable")
        exe=str(Path(exe).resolve())
        pg=bins[0]
        with tempfile.TemporaryDirectory(prefix="mvc-publish-") as tmp, contextlib.ExitStack() as stack:
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
            generation=secrets.token_hex(16)
            env["SCALE_RESTORE_GENERATION"]=generation
            env["SCALE_DATABASE"]="scale_lab"
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
            sql(SCHEMA+RECONCILE+ACCESS_SCHEMA+REVOCATION_SCHEMA+RELEASE_SCHEMA)
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
            for name,source in {"Program.cs":PUBLISH_HOST,"Data/ScaleStore.cs":PUBLISH_DATA,"Services/ScaleService.cs":SERVICES,
                                "Controllers/ScaleController.cs":OWNER_CONTROLLER,"Controllers/AccountController.cs":ACCOUNT_CONTROLLER,
                                "Security/Access.cs":BACKUP_ACCESS,"Security/Readiness.cs":READINESS,"Areas/Admin/Controllers/StudiesController.cs":REV_ADMIN,
                                "Views/Account/Login.cshtml":LOGIN_VIEW,"Views/Account/Session.cshtml":SESSION_VIEW,
                                "Areas/Admin/Views/Studies/Index.cshtml":ADMIN_VIEW}.items():
                p=app/name
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text(source)
            (app/"appsettings.json").write_text(json.dumps({"Release":{"Database":"disabled","Label":"unconfigured"}}))
            (app/"wwwroot"/"release-marker.txt").write_text("SYNTHETIC MVC RELEASE\n")
            project=str(app/"ScaleMvc.csproj")
            run(exe,"restore",project,"--configfile",str(config),"--packages",str(root/"packages"),"--disable-build-servers","-p:NuGetAudit=false")
            publish=root/"published"
            run(exe,"publish",project,"-c","Release","--no-restore","--no-self-contained",
                "--disable-build-servers","-p:UseAppHost=false","-o",str(publish))
            pin=inventory(publish)
            self.assertTrue({"ScaleMvc.dll","ScaleMvc.deps.json","ScaleMvc.runtimeconfig.json",
                             "appsettings.json","wwwroot/release-marker.txt"}.issubset(pin))
            self.assertEqual(json.loads((publish/"ScaleMvc.runtimeconfig.json").read_text())["runtimeOptions"]["tfm"],"net10.0")
            for f in publish.rglob("*"):
                if f.is_file():
                    raw=f.read_bytes()
                    self.assertTrue(all(value.encode() not in raw for value in [generation,*credentials.values()]))
            artifact=root/"isolated"
            shutil.copytree(publish,artifact)
            self.assertEqual(inventory(artifact),pin)
            shutil.rmtree(app)
            shutil.rmtree(publish)
            dll=str(artifact/"ScaleMvc.dll")
            def stop(proc,hard=False):
                if proc.poll() is None:
                    (proc.kill if hard else proc.terminate)()
                    try:proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
            def host(label,db="scale_lab",expect_failure=False):
                self.assertEqual(inventory(artifact),pin)
                local=dict(env,Release__Database=db,Release__Label=label)
                path=root/(label+".log")
                with path.open("wb") as log:
                    proc=subprocess.Popen([exe,dll,"--contentRoot",str(artifact)],cwd=root,env=local,stdout=log,stderr=subprocess.STDOUT)
                stack.callback(stop,proc)
                deadline=time.monotonic()+20
                while time.monotonic()<deadline:
                    body=path.read_text(errors="replace")
                    if expect_failure and proc.poll() is not None:
                        self.assertNotEqual(proc.returncode,0)
                        self.assertIn("RELEASE_CONFIG_INVALID",body)
                        self.assertNotIn("Now listening on:",body)
                        return proc,None
                    self.assertIsNone(proc.poll(),body[-3000:])
                    m=re.search(r"Now listening on: http://127\.0\.0\.1:(\d+)",body)
                    if m:
                        self.assertFalse(expect_failure)
                        return proc,int(m.group(1))
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
            def snap(db="scale_lab"):
                return json.loads(sql("""SELECT json_build_array(
                  COALESCE((SELECT json_agg(json_build_array(slot,key::text,q1,q2,q3,id) ORDER BY slot) FROM scale.answers),'[]'::json),
                  COALESCE((SELECT json_agg(json_build_array(answer_id,event) ORDER BY answer_id) FROM scale.receipts),'[]'::json),
                  COALESCE((SELECT json_agg(json_build_array(key::text,slot) ORDER BY key) FROM scale.issued),'[]'::json),
                  COALESCE((SELECT json_agg(json_build_array(answer_id,actor) ORDER BY answer_id) FROM scale.reviewed),'[]'::json));""",db))
            source_host,port=host("source")
            source_port=port
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
            self.assertIn("AddHealthChecks",PUBLISH_HOST)
            self.assertIn("public bool Ready()",PUBLISH_DATA)
            self.assertEqual(snap(),[[],[],[],[]])
            self.assertFalse(app.exists())
            self.assertFalse(publish.exists())
            self.assertEqual(request("GET","/health/live")[:2],(200,"Healthy"))
            self.assertEqual(request("GET","/health/ready")[:2],(200,"Healthy"))
            self.assertEqual(request("GET","/release")[:2],(200,"source"))
            self.assertEqual(request("GET","/release-marker.txt")[:2],(200,"SYNTHETIC MVC RELEASE\n"))
            _,badport=host("candidate","invalid_database",True)
            self.assertIsNone(badport)
            def submit(slot,name,q1):
                jar,t=login(name)
                reply=request("POST","/scale/issue/"+slot,jar,{"__RequestVerificationToken":t})
                self.assertEqual(reply[0],200)
                key=reply[1]
                form={"Key":key,"Version":"SYN-V1","Q1":str(q1),"Q2":"","Q3":"0","__RequestVerificationToken":t}
                reply=request("POST","/scale/new/"+slot,jar,form)
                self.assertEqual(reply[0],303,reply[1])
                return jar,key,dict((k.lower(),v) for k,v in reply[2])["location"]
            alpha,a,ra=submit("SYN-A","alpha",1)
            staff,st=login("staff-a")
            self.assertEqual(request("GET","/admin/studies/STUDY-A",staff)[0],200)
            original=snap()
            connection=("-h",str(root/"socket"),"-p","5432","-U","lab_admin")
            old_dump=root/"old.dump"
            run(pg/"pg_dump",*connection,"-Fc","--file",str(old_dump),"scale_lab")
            beta,b,rb=submit("SYN-B","beta",2)
            current=snap()
            self.assertEqual(len(current[0]),2)
            self.assertEqual(len(current[1]),2)
            self.assertEqual(sql("SELECT count(*) FROM scale.issued"),"2")
            def authority(db):
                return json.loads(sql("""SELECT json_build_array(
                 (SELECT json_agg(to_jsonb(p) ORDER BY actor) FROM scale.actor_state p),
                 (SELECT json_agg(to_jsonb(g) ORDER BY actor,study) FROM scale.study_grant g),
                 (SELECT json_agg(to_jsonb(s) ORDER BY slot) FROM scale.slot_access s));""",db))
            roles=authority("scale_lab")
            sql("CREATE DATABASE scale_stage;","postgres")
            run(pg/"pg_restore",*connection,"--exit-on-error","--single-transaction","-d","scale_stage",str(old_dump))
            self.assertEqual(snap("scale_stage"),original)
            self.assertEqual(authority("scale_stage"),roles)
            candidate,candidate_port=host("candidate","scale_stage")
            def check(port,path):
                return http(port,"GET",path)[:2]
            self.assertEqual(check(candidate_port,"/health/ready"),(200,"Healthy"))
            self.assertEqual(check(candidate_port,"/release"),(200,"candidate"))
            self.assertEqual(check(candidate_port,"/release-marker.txt"),(200,"SYNTHETIC MVC RELEASE\n"))
            # Persistent local target pointer consumed by a test client, not an
            # external load balancer. Single trusted controller owns all clients.
            active=root/"active.json"
            def pointer(label,port):
                return json.dumps({"label":label,"port":port},sort_keys=True).encode()
            with active.open("xb") as f:f.write(pointer("source",source_port))
            old_pointer=active.read_bytes()
            def active_get(path):
                return check(json.loads(active.read_bytes())["port"],path)
            self.assertEqual(active_get("/release"),(200,"source"))
            def activate(expected_business,expected_authority,port):
                if active.read_bytes()!=old_pointer:return "STALE"
                if check(port,"/health/ready")!=(200,"Healthy"):return "NOT_READY"
                if snap("scale_stage")!=expected_business:return "RESTORE_GAP"
                if authority("scale_stage")!=expected_authority:return "AUTHORITY_GAP"
                if inventory(artifact)!=pin:return "ARTIFACT_CHANGED"
                temp=root/"active.next"
                with temp.open("xb") as f:
                    f.write(pointer("candidate",port));f.flush();os.fsync(f.fileno())
                os.replace(temp,active)
                fd=os.open(root,os.O_RDONLY)
                try:os.fsync(fd)
                finally:os.close(fd)
                return "ACTIVATED"
            self.assertEqual(activate(current,roles,candidate_port),"RESTORE_GAP")
            self.assertEqual(active.read_bytes(),old_pointer)
            self.assertEqual(active_get("/release"),(200,"source"))
            self.assertEqual(snap(),current)
            sql("UPDATE scale.release_contract SET revision=1","scale_stage")
            self.assertEqual(check(candidate_port,"/health/live"),(200,"Healthy"))
            self.assertEqual(check(candidate_port,"/health/ready"),(503,"Unhealthy"))
            self.assertEqual(check(candidate_port,"/account/login"),(503,"Unavailable"))
            self.assertEqual(activate(current,roles,candidate_port),"NOT_READY")
            self.assertEqual(active.read_bytes(),old_pointer)
            sql("UPDATE scale.release_contract SET revision=2","scale_stage")
            self.assertEqual(check(candidate_port,"/health/ready"),(200,"Healthy"))
            sql("ALTER TABLE scale.answers RENAME COLUMN q1 TO q1_old","scale_stage")
            self.assertEqual(check(candidate_port,"/health/live"),(200,"Healthy"))
            self.assertEqual(check(candidate_port,"/health/ready"),(503,"Unhealthy"))
            self.assertEqual(check(candidate_port,"/account/login"),(503,"Unavailable"))
            self.assertEqual(activate(current,roles,candidate_port),"NOT_READY")
            sql("ALTER TABLE scale.answers RENAME COLUMN q1_old TO q1","scale_stage")
            self.assertEqual(check(candidate_port,"/health/ready"),(200,"Healthy"))
            sql("REVOKE SELECT ON scale.release_contract FROM scale_writer","scale_stage")
            self.assertEqual(check(candidate_port,"/health/ready"),(503,"Unhealthy"))
            self.assertEqual(check(candidate_port,"/health/live"),(200,"Healthy"))
            sql("GRANT SELECT ON scale.release_contract TO scale_writer","scale_stage")
            self.assertEqual(check(candidate_port,"/health/ready"),(200,"Healthy"))
            self.assertEqual(snap("scale_stage"),original)
            self.assertEqual(snap(),current)
            self.assertEqual(active.read_bytes(),old_pointer)
            self.assertEqual(active_get("/release"),(200,"source"))
            # Stop known source and stage hosts before obtaining new current
            # checkpoint; the fixture owns all clients and writers.
            stop(candidate)
            stop(source_host)
            self.assertEqual(sql("SELECT count(*) FROM pg_stat_activity WHERE datname IN ('scale_lab','scale_stage') AND usename='scale_writer'"),"0")
            self.assertEqual(snap(),current)
            self.assertEqual(authority("scale_lab"),roles)
            fresh_dump=root/"current.dump"
            run(pg/"pg_dump",*connection,"-Fc","--file",str(fresh_dump),"scale_lab")
            sql("DROP DATABASE scale_stage;","postgres")
            sql("CREATE DATABASE scale_stage;","postgres")
            run(pg/"pg_restore",*connection,"--exit-on-error","--single-transaction","-d","scale_stage",str(fresh_dump))
            self.assertEqual(snap("scale_stage"),current)
            self.assertEqual(authority("scale_stage"),roles)
            env["SCALE_RESTORE_GENERATION"]=secrets.token_hex(16)
            replacement,port=host("candidate","scale_stage")
            self.assertEqual(check(port,"/health/ready"),(200,"Healthy"))
            self.assertEqual(request("GET","/account/session",staff)[0],401)
            sql("UPDATE scale.answers SET q1=5 WHERE slot='SYN-B'","scale_stage")
            self.assertEqual(len(snap("scale_stage")[0]),2)
            self.assertEqual(activate(current,roles,port),"RESTORE_GAP")
            self.assertEqual(active.read_bytes(),old_pointer)
            sql("UPDATE scale.answers SET q1=2 WHERE slot='SYN-B'","scale_stage")
            sql("DELETE FROM scale.study_grant WHERE actor='staff-a' AND study='STUDY-A'","scale_stage")
            self.assertEqual(snap("scale_stage"),current)
            self.assertEqual(activate(current,roles,port),"AUTHORITY_GAP")
            self.assertEqual(active.read_bytes(),old_pointer)
            sql("INSERT INTO scale.study_grant VALUES('staff-a','STUDY-A')","scale_stage")
            self.assertEqual(authority("scale_stage"),roles)
            # No direct writes from clients between checkpoint comparison and
            # local pointer replacement. No claim of distributed CAS.
            self.assertEqual(activate(current,roles,port),"ACTIVATED")
            self.assertNotEqual(active.read_bytes(),old_pointer)
            self.assertEqual(active_get("/release"),(200,"candidate"))
            self.assertEqual(active_get("/health/ready"),(200,"Healthy"))
            self.assertEqual(activate(current,roles,port),"STALE")
            for name,slot,key,receipt in (("alpha","SYN-A",a,ra),("beta","SYN-B",b,rb)):
                jar,_=login(name)
                reply=request("GET","/scale/reconcile/"+slot+"/"+key,jar)
                self.assertEqual(reply[0],200)
                self.assertEqual(json.loads(reply[1]),{"state":"COMMITTED","receipt":receipt})
                self.assertEqual(request("GET",receipt,jar)[0],200)
            fresh_staff,_=login("staff-a")
            self.assertEqual(request("GET","/admin/studies/STUDY-A",fresh_staff)[0],200)
            self.assertEqual(request("GET","/admin/studies/STUDY-B",fresh_staff)[0],404)
            self.assertEqual(snap("scale_stage"),current)
            self.assertEqual(snap(),current)
            self.assertEqual(authority("scale_stage"),roles)
            self.assertEqual(inventory(artifact),pin)
            stop(replacement)
            print(f"DOTNET-MVC-PUBLISH-ACTIVATION-PASS sdk={sdk} pg={version} artifact-files={len(pin)} release-isolated config-rejected liveness-readiness version-column-acl-negative restore-gap count-equal-content-gap authority-gap durable-local-pointer stale-denied receipts=2 source-unchanged",flush=True)
