"""Native project backup, console publish, and isolated PostgreSQL restore.

Only synthetic data and preinstalled SDK/client tools. No deployment.
The post-backup authority checkpoint is separately held by the trusted lab
operator; it is not taken from the old backup or from a web request.
"""
import contextlib
import hashlib
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
import zipfile
from urllib.parse import urlencode
from test_dotnet_console_mvc import FormToken
from test_dotnet_scale_transfer import SERVICES
from test_dotnet_scale_persistence import SCHEMA
from test_pg_scale_inflight import RECONCILE
from test_dotnet_mvc_admin_authz import (
    ACCESS_SCHEMA, ACCOUNT_CONTROLLER, OWNER_CONTROLLER, LOGIN_VIEW, SESSION_VIEW, ADMIN_VIEW,
)
from test_dotnet_mvc_admin_revocation import REVOCATION_SCHEMA, REV_HOST, REV_ACCESS, REV_ADMIN, REV_DATA

# Both host variants use the same persisted ASP.NET data-protection key ring
# under the lab HOME. The negative control intentionally keeps the old generation.
BACKUP_HOST = REV_HOST.replace(
    'if(current.Length!=3 || stamp!=current[2])c.RejectPrincipal();',
    '''if(current.Length!=3 || stamp!=current[2] ||
            c.Principal?.FindFirstValue("restore_generation")!=
            Environment.GetEnvironmentVariable("SCALE_RESTORE_GENERATION"))c.RejectPrincipal();''',1)
BACKUP_ACCESS = REV_ACCESS.replace(
    'new("auth_epoch",state[2])};',
    '''new("auth_epoch",state[2]),new("restore_generation",
        Environment.GetEnvironmentVariable("SCALE_RESTORE_GENERATION") ??
        throw new InvalidOperationException("missing generation"))};''',1)
BACKUP_DATA = REV_DATA.replace(
    'private readonly string exe=',
    '''private readonly string db=Environment.GetEnvironmentVariable("SCALE_DATABASE") switch {
        "scale_lab"=>"scale_lab", "scale_stage"=>"scale_stage",
        _=>throw new InvalidOperationException("owned lab database required")
    };
    private readonly string exe=''',1).replace(
    '"-d","scale_lab"','"-d",db',1)

# A small real console app, published framework-dependent using the installed
# runtime. Trust root is the independently supplied manifest digest, not a
# checksum bundled with untrusted files. No execution of archive contents.
CONSOLE = '''using System.Security.Cryptography;
using System.Text.Json;
using System.Text.RegularExpressions;
if(args.Length!=2)return 2;
try {
    var root=Path.GetFullPath(args[0]);
    if(!Regex.IsMatch(args[1],"^[a-f0-9]{64}$"))return 2;
    if(!Directory.Exists(root))return 3;
    var expected=new[]{"manifest.json","research.dump","source.zip"};
    var entries=Directory.GetFileSystemEntries(root).Select(Path.GetFileName)
        .OrderBy(x=>x,StringComparer.Ordinal).ToArray();
    if(!entries.SequenceEqual(expected))return 3;
    foreach(var name in expected) {
        var info=new FileInfo(Path.Combine(root,name));
        if(!info.Exists || info.LinkTarget is not null ||
            (info.Attributes&FileAttributes.ReparsePoint)!=0)return 3;
    }
    string Digest(string name) {
        using var stream=File.OpenRead(Path.Combine(root,name));
        return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
    }
    if(Digest("manifest.json")!=args[1])return 4;
    using var doc=JsonDocument.Parse(File.ReadAllBytes(Path.Combine(root,"manifest.json")));
    var props=doc.RootElement.EnumerateObject().ToArray();
    if(props.Length!=2 || props.Select(p=>p.Name).Distinct().Count()!=2)return 4;
    foreach(var name in new[]{"research.dump","source.zip"}) {
        if(!doc.RootElement.TryGetProperty(name,out var item) ||
            item.GetProperty("sha256").GetString()!=Digest(name) ||
            item.GetProperty("size").GetInt64()!=new FileInfo(Path.Combine(root,name)).Length)return 4;
    }
    Console.WriteLine("BUNDLE_VERIFIED");
    return 0;
} catch {return 4;}
'''

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inventory(folder):
    files={}
    for p in sorted(folder.rglob("*")):
        if p.is_symlink():
            raise AssertionError("symlink in publish output")
        if p.is_file():
            files[p.relative_to(folder).as_posix()]=(p.stat().st_size,digest(p))
    return files

class DotnetBackupPublishTests(unittest.TestCase):
    def test_native_backup_restore_generation_and_console_publish(self):
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
        with tempfile.TemporaryDirectory(prefix="backup-publish-") as tmp, contextlib.ExitStack() as stack:
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
            for name,source in {"Program.cs":BACKUP_HOST,"Data/ScaleStore.cs":BACKUP_DATA,"Services/ScaleService.cs":SERVICES,
                                "Controllers/ScaleController.cs":OWNER_CONTROLLER,"Controllers/AccountController.cs":ACCOUNT_CONTROLLER,
                                "Security/Access.cs":BACKUP_ACCESS,"Areas/Admin/Controllers/StudiesController.cs":REV_ADMIN,
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
            def snap(db="scale_lab"):
                return json.loads(sql("""SELECT json_build_array(
                  COALESCE((SELECT json_agg(json_build_array(slot,key::text,q1,q2,q3,id) ORDER BY slot) FROM scale.answers),'[]'::json),
                  COALESCE((SELECT json_agg(json_build_array(answer_id,event) ORDER BY answer_id) FROM scale.receipts),'[]'::json),
                  COALESCE((SELECT json_agg(json_build_array(key::text,slot) ORDER BY key) FROM scale.issued),'[]'::json),
                  COALESCE((SELECT json_agg(json_build_array(answer_id,actor) ORDER BY answer_id) FROM scale.reviewed),'[]'::json));""",db))
            source_host,port=host("source")
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
            self.assertIn("restore_generation",BACKUP_ACCESS)
            self.assertIn("SCALE_RESTORE_GENERATION",BACKUP_HOST)
            self.assertIn('"-d",db',BACKUP_DATA)
            self.assertEqual(snap(),[[],[],[],[]])
            def submit(slot,name,q1):
                jar,t=login(name)
                result=request("POST","/scale/issue/"+slot,jar,{"__RequestVerificationToken":t})
                self.assertEqual(result[0],200)
                key=result[1]
                fields={"Key":key,"Version":"SYN-V1","Q1":str(q1),"Q2":"","Q3":"0","__RequestVerificationToken":t}
                result=request("POST","/scale/new/"+slot,jar,fields)
                self.assertEqual(result[0],303,result[1])
                loc=dict((k.lower(),v) for k,v in result[2])["location"]
                return jar,key,loc
            alpha,key,receipt=submit("SYN-A","alpha",1)
            admin,at=login("staff-a")
            old=dict(admin)
            independent,bt=login("staff-b")
            self.assertEqual(request("GET","/admin/studies/STUDY-A",old)[0],200)
            def authority(db="scale_lab"):
                return json.loads(sql("""SELECT json_build_array(
                  (SELECT json_agg(json_build_array(actor,role_name,can_review,epoch) ORDER BY actor) FROM scale.actor_state),
                  (SELECT json_agg(json_build_array(actor,study) ORDER BY actor,study) FROM scale.study_grant));""",db))
            oldstate=authority()
            historical=snap()
            self.assertEqual(len(historical[0]),1)
            bundle=root/"bundle"
            bundle.mkdir(mode=0o700)
            connection=("-h",str(root/"socket"),"-p","5432","-U","lab_admin")
            dump=bundle/"research.dump"
            run(pg/"pg_dump",*connection,"-Fc","--file",str(dump),"scale_lab")
            self.assertGreater(dump.stat().st_size,0)
            # Source backup is a declared console project, not a copy of HOME,
            # obj/bin, the DB cluster, the data protection keys or auth env.
            console=root/"ConsoleSource"
            run(exe,"new","console","--name","RestoreCheck","--output",str(console),"--no-restore")
            (console/"Program.cs").write_text(CONSOLE)
            source_names=("Program.cs","RestoreCheck.csproj")
            source_original={name:(console/name).read_bytes() for name in source_names}
            with zipfile.ZipFile(bundle/"source.zip","x",compression=zipfile.ZIP_DEFLATED) as z:
                for name in source_names:z.writestr(name,source_original[name])
            manifest={name:{"size":(bundle/name).stat().st_size,"sha256":digest(bundle/name)}
                      for name in ("research.dump","source.zip")}
            (bundle/"manifest.json").write_text(json.dumps(manifest,sort_keys=True,separators=(",",":")))
            pin=digest(bundle/"manifest.json")
            # Safe restore of our own allowlisted source archive; no arbitrary
            # extractall, no overwriting an existing project.
            restored=root/"RestoredSource"
            restored.mkdir(mode=0o700)
            with zipfile.ZipFile(bundle/"source.zip") as z:
                self.assertEqual(sorted(z.namelist()),sorted(source_names))
                for name in source_names:
                    raw=z.read(name)
                    self.assertEqual(raw,source_original[name])
                    with (restored/name).open("xb") as out:out.write(raw)
            project=str(restored/"RestoreCheck.csproj")
            run(exe,"restore",project,"--configfile",str(config),"--packages",str(root/"packages"),
                "--disable-build-servers","-p:NuGetAudit=false")
            published=root/"published"
            run(exe,"publish",project,"-c","Release","--no-restore","--no-self-contained",
                "--disable-build-servers","-p:UseAppHost=false","-o",str(published))
            files=inventory(published)
            self.assertEqual(set(files),{"RestoreCheck.dll","RestoreCheck.deps.json",
                                         "RestoreCheck.runtimeconfig.json","RestoreCheck.pdb"})
            self.assertTrue(all(size>0 for size,_ in files.values()))
            runtime=json.loads((published/"RestoreCheck.runtimeconfig.json").read_text())
            self.assertEqual(runtime["runtimeOptions"]["tfm"],"net10.0")
            # A second explicit publish of the same restored source/path.
            second=root/"published-again"
            run(exe,"publish",project,"-c","Release","--no-restore","--no-self-contained",
                "--disable-build-servers","-p:UseAppHost=false","-o",str(second))
            self.assertEqual(inventory(second),files)
            # Only run an exact verified copied publish directory, without
            # depending on the project's obj/bin or source files.
            isolated=root/"execution"
            shutil.copytree(published,isolated)
            self.assertEqual(inventory(isolated),files)
            shutil.rmtree(restored)
            shutil.rmtree(console)
            shutil.rmtree(published)
            shutil.rmtree(second)
            dll_path=str(isolated/"RestoreCheck.dll")
            def verify(folder,expected=pin,code=0):
                p=subprocess.run([exe,dll_path,str(folder),expected],cwd=root,env=env,
                                 capture_output=True,text=True,timeout=15)
                self.assertEqual(p.returncode,code,(p.stdout+p.stderr)[-1000:])
                if code==0:self.assertEqual(p.stdout.strip(),"BUNDLE_VERIFIED")
                else:self.assertNotIn("BUNDLE_VERIFIED",p.stdout)
            verify(bundle)
            verify(bundle,"0"*64,4)
            corrupt=root/"corrupt"
            shutil.copytree(bundle,corrupt)
            (corrupt/"research.dump").write_bytes(dump.read_bytes()+b"x")
            verify(corrupt,code=4)
            shutil.rmtree(corrupt)
            shutil.copytree(bundle,corrupt)
            (corrupt/"source.zip").unlink()
            verify(corrupt,code=3)
            shutil.rmtree(corrupt)
            shutil.copytree(bundle,corrupt)
            (corrupt/"extra.bin").write_bytes(b"unapproved")
            verify(corrupt,code=3)
            shutil.rmtree(corrupt)
            shutil.copytree(bundle,corrupt)
            (corrupt/"source.zip").unlink()
            (corrupt/"source.zip").symlink_to(bundle/"source.zip")
            verify(corrupt,code=3)
            # Separate artifact pin obtained before damage: refuse changed bytes
            # before execution (the altered DLL must not be started).
            changed=root/"changed-publish"
            shutil.copytree(isolated,changed)
            (changed/"RestoreCheck.dll").write_bytes((changed/"RestoreCheck.dll").read_bytes()+b"x")
            self.assertNotEqual(inventory(changed),files)
            self.assertEqual(inventory(isolated),files)
            # New legitimate work and authority changes after backup.
            _,_,late_receipt=submit("SYN-B","beta",2)
            self.assertNotEqual(late_receipt,receipt)
            sql("UPDATE scale.actor_state SET role_name='Viewer',can_review=false WHERE actor='staff-a';")
            sql("DELETE FROM scale.study_grant WHERE actor='staff-a' AND study='STUDY-A';")
            self.assertEqual(request("GET","/admin/studies/STUDY-A",old)[0],401)
            current=authority()
            current_business=snap()
            self.assertEqual(len(current_business[0]),2)
            self.assertEqual(len(current_business[1]),2)
            self.assertNotEqual(current,oldstate)
            # Independent current authority checkpoint outside the archived
            # data; held only after the controlled source writer is stopped.
            stop(source_host)
            self.assertIsNotNone(source_host.poll())
            self.assertEqual(sql("SELECT count(*) FROM pg_stat_activity WHERE datname='scale_lab' AND usename='scale_writer'"),"0")
            self.assertEqual(authority(),current)
            checkpoint=root/"current-authority.json"
            with checkpoint.open("xb") as out:
                out.write(json.dumps(current,separators=(",",":")).encode())
            checkpoint.chmod(0o600)
            authority_pin=digest(checkpoint)
            # Stage in a different database, never overwrite the source.
            verify(bundle)
            sql("CREATE DATABASE scale_stage;","postgres")
            run(pg/"pg_restore",*connection,"--exit-on-error","--single-transaction",
                "-d","scale_stage",str(dump))
            self.assertEqual(snap("scale_stage"),historical)
            self.assertEqual(authority("scale_stage"),oldstate)
            self.assertEqual(snap(),current_business)
            self.assertEqual(authority(),current)
            # Unsafe negative control: old archive + old generation + original
            # data protection keys actually accepts the revoked old cookie.
            # This is an isolated loopback host only, no production activation.
            env["SCALE_DATABASE"]="scale_stage"
            unsafe,port=host("unsafe-restore")
            self.assertEqual(request("GET","/admin/studies/STUDY-A",old)[0],200)
            stop(unsafe)
            self.assertIsNotNone(unsafe.poll())
            self.assertEqual(sql("SELECT count(*) FROM pg_stat_activity WHERE datname='scale_stage' AND usename='scale_writer'","scale_stage"),"0")
            # Rotate restore generation outside the dump, and separately
            # reapply authoritative role/membership checkpoint atomically.
            self.assertEqual(digest(checkpoint),authority_pin)
            restored_auth=json.loads(checkpoint.read_text())
            self.assertEqual(restored_auth,current)
            # All values are synthetic fixed fixture data; quote SQL literals
            # using an explicit escape and strict allowlist before replay.
            def literal(s):
                self.assertRegex(s,r"^[A-Za-z0-9-]+$")
                return "'"+s+"'"
            actors=",".join("("+",".join((literal(a),literal(role),
                   "true" if allowed else "false",str(int(epoch))))+")"
                   for a,role,allowed,epoch in restored_auth[0])
            grants=",".join("("+literal(a)+","+literal(study)+")" for a,study in restored_auth[1])
            sql("BEGIN; DELETE FROM scale.study_grant; DELETE FROM scale.actor_state; "
                "INSERT INTO scale.actor_state(actor,role_name,can_review,epoch) VALUES "+actors+
                "; INSERT INTO scale.study_grant(actor,study) VALUES "+grants+"; COMMIT;","scale_stage")
            self.assertEqual(authority("scale_stage"),current)
            env["SCALE_RESTORE_GENERATION"]=secrets.token_hex(16)
            self.assertNotEqual(env["SCALE_RESTORE_GENERATION"],generation)
            fixed,port=host("safe-restore")
            # Unchanged actor epoch, same keys: generation alone blocks old cookie.
            self.assertEqual(request("GET","/account/session",independent)[0],401)
            self.assertEqual(request("GET","/admin/studies/STUDY-A",old)[0],401)
            demoted,dt=login("staff-a")
            self.assertEqual(request("GET","/admin/studies/STUDY-A",demoted)[0],403)
            self.assertEqual(request("POST",f"/admin/studies/STUDY-A/review/{historical[0][0][-1]}",
                 demoted,{"__RequestVerificationToken":dt})[0],403)
            allowed,_=login("staff-b")
            self.assertEqual(request("GET","/admin/studies/STUDY-B",allowed)[0],200)
            fresh_alpha,_=login("alpha")
            reply=request("GET","/scale/reconcile/SYN-A/"+key,fresh_alpha)
            self.assertEqual(reply[0],200)
            self.assertEqual(json.loads(reply[1]),{"state":"COMMITTED","receipt":receipt})
            self.assertEqual(request("GET",receipt,fresh_alpha)[0],200)
            self.assertEqual(snap("scale_stage"),historical)
            self.assertEqual(authority("scale_stage"),current)
            # The missing later answer/receipt is a real restore gap. Do not
            # promote the stage or silently declare data recovery complete.
            self.assertEqual(snap(),current_business)
            self.assertNotEqual(snap("scale_stage"),current_business)
            self.assertEqual(len(snap("scale_stage")[0]),1)
            self.assertEqual(len(current_business[0]),2)
            self.assertEqual(inventory(isolated),files)
            stop(fixed)
            print(f"DOTNET-BACKUP-PUBLISH-PASS sdk={sdk} pg={version} source-zip-exact publish-files={len(files)} repeat-publish-identical executed-isolated digest-negative=5 unsafe-cookie-resurrection-observed generation-rotated authority-checkpoint-restored receipt-preserved source-unchanged restore-gap=1 no-promotion",flush=True)
