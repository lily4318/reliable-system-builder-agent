"""Synthetic MVC -> PostgreSQL durable receipt transfer, owned private cluster only.

Uses preinstalled psql as a narrow lab bridge (not a production .NET driver).
No external database, packages or real participants.
"""
import contextlib
import http.client as http_client
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from urllib.parse import urlencode
from test_dotnet_console_mvc import FormToken
from test_dotnet_scale_transfer import SERVICES, ENTRY

SCHEMA = """CREATE SCHEMA scale;
CREATE TABLE scale.slots(slot text PRIMARY KEY CHECK(slot IN ('SYN-A','SYN-B','SYN-C')));
INSERT INTO scale.slots VALUES ('SYN-A'),('SYN-B'),('SYN-C');
CREATE TABLE scale.issued(
 key uuid PRIMARY KEY, slot text NOT NULL REFERENCES scale.slots,
 UNIQUE(key,slot));
CREATE TABLE scale.answers(
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 slot text NOT NULL UNIQUE REFERENCES scale.slots,
 key uuid NOT NULL UNIQUE,
 version text NOT NULL CHECK(version='SYN-V1'),
 q1 integer NOT NULL CHECK(q1 BETWEEN 1 AND 5),
 q2 integer CHECK(q2 BETWEEN 1 AND 5),
 q3 integer NOT NULL CHECK(q3 BETWEEN 0 AND 4),
 FOREIGN KEY(key,slot) REFERENCES scale.issued(key,slot));
CREATE TABLE scale.receipts(
 answer_id integer PRIMARY KEY REFERENCES scale.answers,
 event text NOT NULL CHECK(event='ACCEPTED'));
CREATE FUNCTION scale.submit(s text,k uuid,a integer,b integer,c integer)
RETURNS text LANGUAGE plpgsql AS $$
DECLARE prior scale.answers%ROWTYPE; newid integer;
BEGIN
 IF a IS NULL OR a NOT BETWEEN 1 AND 5 OR c IS NULL OR c NOT BETWEEN 0 AND 4
    OR (b IS NOT NULL AND b NOT BETWEEN 1 AND 5) THEN RETURN '400'; END IF;
 -- Serialize all writers for the *business* slot, not merely the request key.
 PERFORM 1 FROM scale.slots WHERE slot=s FOR UPDATE;
 IF NOT FOUND THEN RETURN '400'; END IF;
 IF NOT EXISTS(SELECT 1 FROM scale.issued WHERE key=k AND slot=s) THEN RETURN '400'; END IF;
 SELECT * INTO prior FROM scale.answers WHERE slot=s;
 IF FOUND THEN
   IF prior.key=k AND prior.q1=a AND prior.q2 IS NOT DISTINCT FROM b AND prior.q3=c
   THEN RETURN '303|'||prior.id; END IF;
   RETURN '409';
 END IF;
 INSERT INTO scale.answers(slot,key,version,q1,q2,q3)
 VALUES(s,k,'SYN-V1',a,b,c) RETURNING id INTO newid;
 INSERT INTO scale.receipts VALUES(newid,'ACCEPTED');
 RETURN '303|'||newid;
END $$;
CREATE FUNCTION scale.reconcile(s text,k uuid) RETURNS text LANGUAGE sql STABLE AS $$
 SELECT CASE WHEN NOT EXISTS(SELECT 1 FROM scale.issued WHERE key=k AND slot=s) THEN '400'
 WHEN EXISTS(SELECT 1 FROM scale.answers WHERE key=k AND slot=s) THEN
  (SELECT '303|'||id FROM scale.answers WHERE key=k AND slot=s)
 ELSE '404' END
$$;
CREATE ROLE scale_writer LOGIN;
GRANT USAGE ON SCHEMA scale TO scale_writer;
GRANT SELECT, UPDATE ON scale.slots TO scale_writer;
GRANT SELECT, INSERT ON scale.issued,scale.answers,scale.receipts TO scale_writer;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA scale TO scale_writer;
REVOKE EXECUTE ON ALL FUNCTIONS IN SCHEMA scale FROM PUBLIC;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA scale TO scale_writer;
"""
HOST = '''using ScaleMvc.Data;
using ScaleMvc.Services;
var builder=WebApplication.CreateBuilder(args);
builder.Host.UseDefaultServiceProvider(o=>{o.ValidateScopes=true;o.ValidateOnBuild=true;});
builder.Services.AddControllersWithViews();
builder.Services.AddSingleton<ScaleStore>();
builder.Services.AddScoped<ScaleService>();
var app=builder.Build();
app.MapControllers();
app.Run();
'''
DATA = '''using System.Diagnostics;
using System.Globalization;
using System.Text.Json;
namespace ScaleMvc.Data;
public sealed record Answers(int Q1,int? Q2,int Q3);
public sealed record Receipt(int Id,string Slot,string Version,Answers Answers);
public sealed class ScaleStore {
    private readonly string exe=Environment.GetEnvironmentVariable("SCALE_PSQL")!;
    private readonly string socket=Environment.GetEnvironmentVariable("SCALE_SOCKET")!;
    // Fixed SQL templates only, psql literal variables via stdin (not interpolated SQL).
    private string Query(string sql,params (string Name,string Value)[] vars) {
        var p=new ProcessStartInfo(exe) {
            UseShellExecute=false,RedirectStandardInput=true,RedirectStandardOutput=true,RedirectStandardError=true
        };
        foreach(var s in new[]{"-X","-w","-qAt","-h",socket,"-p","5432","-U","scale_writer","-d","scale_lab","-v","ON_ERROR_STOP=1"})
            p.ArgumentList.Add(s);
        foreach(var (name,value) in vars) {p.ArgumentList.Add("-v");p.ArgumentList.Add(name+"="+value);}
        foreach(var name in p.Environment.Keys.Where(x=>x.StartsWith("PG",StringComparison.Ordinal)).ToArray()) p.Environment.Remove(name);
        using var proc=Process.Start(p)!;
        var output=proc.StandardOutput.ReadToEndAsync();
        var error=proc.StandardError.ReadToEndAsync();
        proc.StandardInput.WriteLine(sql);
        proc.StandardInput.Close();
        if(!proc.WaitForExit(10000)) {proc.Kill(true);proc.WaitForExit();throw new InvalidOperationException("lab database timeout");}
        if(proc.ExitCode!=0) throw new InvalidOperationException("lab database rejected transaction");
        return output.GetAwaiter().GetResult().Trim();
    }
    private static string Num(int? x)=>x?.ToString(CultureInfo.InvariantCulture)??"";
    public string Issue(string slot) {
        var key=Guid.NewGuid().ToString("D");
        Query("INSERT INTO scale.issued VALUES (:'k'::uuid,:'s');",("k",key),("s",slot));
        return key;
    }
    public (Receipt? Row,int Status) Save(string slot,string key,Answers a) {
        var result=Query("SELECT scale.submit(:'s',:'k'::uuid,:'a'::int,NULLIF(:'b','')::int,:'c'::int);",
            ("s",slot),("k",key),("a",Num(a.Q1)),("b",Num(a.Q2)),("c",Num(a.Q3)));
        var parts=result.Split('|');
        int status=int.Parse(parts[0],CultureInfo.InvariantCulture);
        return (status==303?new Receipt(int.Parse(parts[1],CultureInfo.InvariantCulture),slot,"SYN-V1",a):null,status);
    }
    public string Reconcile(string slot,string key)=>Query("SELECT scale.reconcile(:'s',:'k'::uuid);",("s",slot),("k",key));
    public Receipt? Find(int id) {
        var s=Query("SELECT json_build_object('id',id,'slot',slot,'version',version,'answers',json_build_object('q1',q1,'q2',q2,'q3',q3)) FROM scale.answers WHERE id=:'id'::int;",("id",Num(id)));
        return s==""?null:JsonSerializer.Deserialize<Receipt>(s,new JsonSerializerOptions(JsonSerializerDefaults.Web));
    }
    public object Snapshot()=>throw new NotSupportedException("independent SQL oracle only");
}
'''
CONTROLLER = '''using Microsoft.AspNetCore.Mvc;
using ScaleMvc.Services;
using ScaleMvc.Data;
namespace ScaleMvc.Controllers;
[Route("scale")]
public sealed class ScaleController(ScaleService service, ScaleStore store):Controller {
    [HttpGet("new/{slot}")]
    public IActionResult Entry([FromRoute]string slot)=>
        ScaleService.ValidSlot(slot)?View("Entry",service.Issue(slot)):NotFound();
    [HttpPost("new/{slot}"),ValidateAntiForgeryToken]
    public IActionResult Submit([FromRoute]string slot) {
        if(!ScaleService.ValidSlot(slot)) return NotFound();
        if(!Request.HasFormContentType) return BadRequest();
        var r=service.Submit(slot,Request.Form);
        if(r.Status!=303) return StatusCode(r.Status);
        // Owned synthetic fixture only: simulate committed response loss, not production fault API.
        if(Request.Headers["X-Synthetic-Lose-Ack"]=="1") {HttpContext.Abort();return new EmptyResult();}
        Response.Headers.Location=Url.Action(nameof(Receipt),new{id=r.Row!.Id})!;
        return StatusCode(303);
    }
    [HttpGet("reconcile/{slot}/{key}")]
    public IActionResult Reconcile([FromRoute]string slot,[FromRoute]string key) {
        if(!ScaleService.ValidSlot(slot)||!Guid.TryParseExact(key,"D",out _))return BadRequest();
        var parts=store.Reconcile(slot,key).Split('|');
        return parts[0]=="303"?Content("/scale/receipt/"+parts[1]):StatusCode(int.Parse(parts[0]));
    }
    [HttpGet("receipt/{id:int}")]
    public IActionResult Receipt([FromRoute]int id)=>service.Find(id) is null?NotFound():Content("Synthetic receipt "+id);
}
'''

class DotnetScalePersistenceTests(unittest.TestCase):
    def test_native_multi_host_postgres_receipt_recovery(self):
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
        with tempfile.TemporaryDirectory(prefix="scale-pg-") as tmp, contextlib.ExitStack() as stack:
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
            sql(SCHEMA)
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
            for name,source in {"Program.cs":HOST,"Data/ScaleStore.cs":DATA,"Services/ScaleService.cs":SERVICES,
                                "Controllers/ScaleController.cs":CONTROLLER,"Views/Scale/Entry.cshtml":ENTRY}.items():
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
            h1,p1=host("host1")
            h2,p2=host("host2")
            self.assertNotEqual(h1.pid,h2.pid)
            a,ac=form(p1,"SYN-A")
            a2,a2c=form(p2,"SYN-A")
            b,bc=form(p1,"SYN-B")
            b2,b2c=form(p2,"SYN-B")
            c,cc=form(p1,"SYN-C")
            initial=check_rows([],5)
            # DB constraints reject invalid direct writes, independently of MVC.
            for values,needle in [("0,NULL,0","check constraint"),("1,0,0","check constraint"),
                                  ("1,NULL,5","check constraint"),("NULL,NULL,0","not-null constraint")]:
                bad=sql("INSERT INTO scale.answers(slot,key,version,q1,q2,q3) VALUES ('SYN-A','"+a["Key"]+"','SYN-V1',"+values+");",ok=False)
                self.assertIn(needle,bad)
                self.assertEqual(snapshot(),initial)
            self.assertEqual(post(p1,"SYN-A",dict(a,Q1="0"),ac)[0],400)
            self.assertEqual(snapshot(),initial)
            # Force an actual late insert failure: no answer may remain without receipt.
            sql("CREATE FUNCTION scale.fail_receipt() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'synthetic receipt failure'; END $$; CREATE TRIGGER fail_receipt BEFORE INSERT ON scale.receipts FOR EACH ROW EXECUTE FUNCTION scale.fail_receipt();")
            self.assertEqual(post(p1,"SYN-C",c,cc)[0],500)
            self.assertEqual(snapshot(),initial)
            self.assertEqual(http(p2,"GET","/scale/reconcile/SYN-C/"+c["Key"])[0],404)
            sql("DROP TRIGGER fail_receipt ON scale.receipts; DROP FUNCTION scale.fail_receipt();")
            def race(slot,left,right):
                gate=Barrier(2)
                def send(item):
                    gate.wait(timeout=5)
                    return post(item[0],slot,item[1],item[2])
                with ThreadPoolExecutor(max_workers=2) as pool:
                    f=[pool.submit(send,x) for x in (left,right)]
                    return [x.result(timeout=20) for x in f]
            a2["Key"]=a["Key"]
            r=race("SYN-A",(p1,a,ac),(p2,a2,a2c))
            loc_a=receipt(r[0])
            self.assertEqual(receipt(r[1]),loc_a)
            ea=["SYN-A",a["Key"],"SYN-V1",1,None,0]
            check_rows([ea],5)
            b.update(Q1="5",Q2="5",Q3="4")
            b2.update(Q1="2",Q2="2",Q3="1")
            r=race("SYN-B",(p1,b,bc),(p2,b2,b2c))
            self.assertEqual(sorted(x[0] for x in r),[303,409])
            winning=b if r[0][0]==303 else b2
            loc_b=receipt(r[0] if r[0][0]==303 else r[1])
            eb=["SYN-B",winning["Key"],"SYN-V1",int(winning["Q1"]),int(winning["Q2"]),int(winning["Q3"])]
            check_rows([ea,eb],5)
            # Independent direct DB uniqueness check (not just application rejection).
            err=sql("INSERT INTO scale.answers(slot,key,version,q1,q2,q3) VALUES ('SYN-B','"+(b2 if winning is b else b)["Key"]+"','SYN-V1',1,NULL,0);",ok=False)
            self.assertIn("duplicate key",err)
            check_rows([ea,eb],5)
            c.update(Q1="3",Q2="2",Q3="0")
            with self.assertRaises((http_client.RemoteDisconnected,ConnectionResetError)):
                post(p1,"SYN-C",c,cc,lose=True)
            ec=["SYN-C",c["Key"],"SYN-V1",3,2,0]
            committed=check_rows([ea,eb,ec],5)
            stop(h1,hard=True)
            stop(h2,hard=True)
            # Restart the actual database engine as well as the MVC processes;
            # graceful database shutdown tests restart persistence, not power loss.
            run(pg/"pg_ctl","-D",data,"-m","fast","-w","stop")
            run(pg/"pg_ctl",*start_options)
            h3,p3=host("host3")
            self.assertNotIn(h3.pid,(h1.pid,h2.pid))
            self.assertEqual(snapshot(),committed)
            status,loc_c,_=http(p3,"GET","/scale/reconcile/SYN-C/"+c["Key"])
            self.assertEqual(status,200)
            self.assertEqual(loc_c,"/scale/receipt/"+str(committed["answers"][2][6]))
            self.assertEqual(http(p3,"GET",loc_c)[:2],(200,"Synthetic receipt "+loc_c.rsplit("/",1)[1]))
            self.assertEqual(http(p3,"GET","/scale/reconcile/SYN-A/"+c["Key"])[0],400)
            self.assertEqual(snapshot(),committed)
            # Fresh valid CSRF pair, original durable key. No blind retry before reconciliation.
            fresh,fc=form(p3,"SYN-C")
            fresh.update(Key=c["Key"],Q1="3",Q2="2",Q3="0")
            self.assertEqual(receipt(post(p3,"SYN-C",fresh,fc)),loc_c)
            self.assertEqual(post(p3,"SYN-C",dict(fresh,Q2="4"),fc)[0],409)
            check_rows([ea,eb,ec],6)
            print(f"DOTNET-PG-SCALE-PERSISTENCE-PASS sdk={sdk} pg={version} two-host-race db-constraints late-rollback lost-ack host-db-restart readonly-reconcile rows=3 receipts=3",flush=True)
