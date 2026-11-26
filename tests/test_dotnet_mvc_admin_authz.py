"""Real ASP.NET Core auth middleware, MVC area and PostgreSQL resource scope.
Synthetic users/passwords generated for each owned loopback fixture only.
No production credentials, external database, packages or deployment.
"""
import contextlib
import http.client as http_client
import html
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
from test_dotnet_scale_persistence import SCHEMA, DATA
from test_pg_scale_inflight import RECONCILE

ACCESS_SCHEMA = """
CREATE TABLE scale.slot_access(
 slot text PRIMARY KEY REFERENCES scale.slots, study text NOT NULL, owner_id text NOT NULL);
INSERT INTO scale.slot_access VALUES
 ('SYN-A','STUDY-A','alpha'),('SYN-B','STUDY-A','beta'),('SYN-C','STUDY-B','gamma');
CREATE TABLE scale.study_grant(actor text NOT NULL, study text NOT NULL,
 PRIMARY KEY(actor,study));
INSERT INTO scale.study_grant VALUES
 ('staff-a','STUDY-A'),('staff-b','STUDY-B'),('reader-a','STUDY-A');
CREATE TABLE scale.reviewed(answer_id integer PRIMARY KEY REFERENCES scale.answers,
 actor text NOT NULL);
GRANT SELECT ON scale.slot_access,scale.study_grant TO scale_writer;
GRANT SELECT, INSERT ON scale.reviewed TO scale_writer;
"""
AUTH_HOST = '''using ScaleMvc.Data;
using ScaleMvc.Services;
using ScaleMvc.Security;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authorization;
var builder=WebApplication.CreateBuilder(args);
builder.Host.UseDefaultServiceProvider(o=>{o.ValidateScopes=true;o.ValidateOnBuild=true;});
builder.Services.AddControllersWithViews();
builder.Services.AddSingleton<ScaleStore>();
builder.Services.AddScoped<ScaleService>();
builder.Services.AddSingleton<LabAccounts>();
builder.Services.AddSingleton<IAuthorizationHandler,ScopeHandler>();
builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
 .AddCookie(o=>{
    o.Cookie.Name=".ScaleLab.Auth";
    o.Cookie.HttpOnly=true;
    o.Cookie.SameSite=SameSiteMode.Strict;
    o.Cookie.SecurePolicy=CookieSecurePolicy.SameAsRequest; // loopback HTTP lab only
    o.ExpireTimeSpan=TimeSpan.FromMinutes(10);
    o.SlidingExpiration=false;
    o.Events.OnRedirectToLogin=c=>{c.Response.StatusCode=401;return Task.CompletedTask;};
    o.Events.OnRedirectToAccessDenied=c=>{c.Response.StatusCode=403;return Task.CompletedTask;};
 });
builder.Services.AddAuthorization(o=>{
    o.FallbackPolicy=new AuthorizationPolicyBuilder().RequireAuthenticatedUser().Build();
    o.AddPolicy("Owner",p=>p.RequireAuthenticatedUser().RequireRole("Participant").AddRequirements(new ScopeRequirement()));
    o.AddPolicy("Study",p=>p.RequireAuthenticatedUser().RequireRole("Researcher").AddRequirements(new ScopeRequirement()));
    o.AddPolicy("Review",p=>p.RequireAuthenticatedUser().RequireRole("Researcher").RequireClaim("permission","review"));
});
var app=builder.Build();
app.UseRouting();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.Run();
'''
AUTH_DATA = DATA.replace(
    '    public object Snapshot()=>',
    '''    public bool Owns(string actor,string slot)=>Query(
        "SELECT EXISTS(SELECT 1 FROM scale.slot_access WHERE owner_id=:'actor' AND slot=:'slot');",
        ("actor",actor),("slot",slot))=="t";
    public bool HasStudy(string actor,string study)=>Query(
        "SELECT EXISTS(SELECT 1 FROM scale.study_grant WHERE actor=:'actor' AND study=:'study');",
        ("actor",actor),("study",study))=="t";
    public string StudyRows(string actor,string study)=>Query(
        @"SELECT COALESCE(json_agg(json_build_object('id',a.id,'slot',a.slot,'q1',a.q1,
           'reviewed',r.answer_id IS NOT NULL) ORDER BY a.id),'[]'::json) FROM scale.answers a
           JOIN scale.slot_access s ON s.slot=a.slot
           JOIN scale.study_grant g ON g.study=s.study AND g.actor=:'actor'
           LEFT JOIN scale.reviewed r ON r.answer_id=a.id WHERE s.study=:'study';",
        ("actor",actor),("study",study));
    public bool Review(string actor,string study,int id)=>Query(
        @"WITH written AS (INSERT INTO scale.reviewed(answer_id,actor)
           SELECT a.id,:'actor' FROM scale.answers a JOIN scale.slot_access s ON s.slot=a.slot
           JOIN scale.study_grant g ON g.study=s.study AND g.actor=:'actor'
           WHERE a.id=:'id'::int AND s.study=:'study'
           ON CONFLICT(answer_id) DO NOTHING RETURNING answer_id)
           SELECT count(*) FROM written;",
        ("actor",actor),("study",study),("id",Num(id)))=="1";
    public object Snapshot()=>''',1).replace(
    'SELECT scale.reconcile(:\'s\',:\'k\'::uuid);',
    'BEGIN READ ONLY; SELECT scale.observe_intent(:\'s\',:\'k\'::uuid); COMMIT;',1)

ACCESS = '''using System.Security.Claims;
using System.Text.Json;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Authentication.Cookies;
using ScaleMvc.Data;
namespace ScaleMvc.Security;
public sealed class LabAccounts {
    private readonly Dictionary<string,(string Hash,string Role,bool Review)> accounts=new();
    private readonly PasswordHasher<string> hasher=new();
    public LabAccounts() {
        var supplied=JsonSerializer.Deserialize<Dictionary<string,string>>(
            Environment.GetEnvironmentVariable("SCALE_LAB_ACCOUNTS")!)!;
        foreach(var name in new[]{"alpha","beta","gamma","staff-a","staff-b","reader-a"}) {
            bool participant=name is "alpha" or "beta" or "gamma";
            accounts.Add(name,(hasher.HashPassword(name,supplied[name]),
                participant?"Participant":"Researcher",name is "staff-a" or "staff-b"));
        }
    }
    public ClaimsPrincipal? Verify(string name,string password) {
        if(!accounts.TryGetValue(name,out var account) || password.Length>128 ||
            hasher.VerifyHashedPassword(name,account.Hash,password)==PasswordVerificationResult.Failed)
            return null;
        var claims=new List<Claim>{new(ClaimTypes.NameIdentifier,name),new(ClaimTypes.Name,name),
             new(ClaimTypes.Role,account.Role)};
        if(account.Review)claims.Add(new Claim("permission","review"));
        return new ClaimsPrincipal(new ClaimsIdentity(claims,CookieAuthenticationDefaults.AuthenticationScheme));
    }
}
public sealed record SlotResource(string Slot);
public sealed record StudyResource(string Study);
public sealed class ScopeRequirement:IAuthorizationRequirement {}
public sealed class ScopeHandler(ScaleStore store):AuthorizationHandler<ScopeRequirement> {
    protected override Task HandleRequirementAsync(AuthorizationHandlerContext context,ScopeRequirement requirement) {
        var id=context.User.FindFirstValue(ClaimTypes.NameIdentifier);
        if(id is not null && context.Resource switch {
            SlotResource s=>context.User.IsInRole("Participant") && store.Owns(id,s.Slot),
            StudyResource s=>context.User.IsInRole("Researcher") && store.HasStudy(id,s.Study),
            _=>false
        }) context.Succeed(requirement);
        return Task.CompletedTask;
    }
}
'''
# Parenthesize switch expression explicitly for C# operator precedence.
ACCESS = ACCESS.replace('id is not null && context.Resource switch {','id is not null && (context.Resource switch {').replace('        }) context.Succeed','        })) context.Succeed')

ACCOUNT_CONTROLLER = '''using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Mvc;
using ScaleMvc.Security;
namespace ScaleMvc.Controllers;
[Route("account")]
public sealed class AccountController(LabAccounts accounts):Controller {
    [AllowAnonymous,HttpGet("login")]
    public IActionResult Login()=>View();
    [AllowAnonymous,HttpPost("login"),ValidateAntiForgeryToken]
    public async Task<IActionResult> LoginPost() {
        if(!Request.HasFormContentType)return BadRequest();
        var f=Request.Form;
        if(f.Files.Count!=0 || f.Any(x=>x.Value.Count!=1 ||
            x.Key is not ("Name" or "Password" or "__RequestVerificationToken")) ||
            !f.TryGetValue("Name",out var n) || !f.TryGetValue("Password",out var p))return BadRequest();
        var identity=accounts.Verify(n.ToString(),p.ToString());
        if(identity is null)return Unauthorized();
        await HttpContext.SignInAsync(CookieAuthenticationDefaults.AuthenticationScheme,identity);
        return NoContent();
    }
    [Authorize,HttpGet("session")]
    public IActionResult Session()=>View();
    [Authorize,HttpPost("logout"),ValidateAntiForgeryToken]
    public async Task<IActionResult> Logout() {
        await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
        return NoContent();
    }
}
'''
LOGIN_VIEW = '''@{Layout=null;}
<form method="post">@Html.AntiForgeryToken()<input name="Name"/><input name="Password" type="password"/></form>
'''
SESSION_VIEW = '''@{Layout=null;}
<form method="post">@Html.AntiForgeryToken()</form>
'''
OWNER_CONTROLLER = '''using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ScaleMvc.Security;
using ScaleMvc.Services;
using ScaleMvc.Data;
namespace ScaleMvc.Controllers;
[Authorize(Roles="Participant"),Route("scale")]
public sealed class ScaleController(ScaleService service,ScaleStore store,IAuthorizationService auth):Controller {
    private async Task<bool> Owns(string slot)=>ScaleService.ValidSlot(slot) &&
        (await auth.AuthorizeAsync(User,new SlotResource(slot),"Owner")).Succeeded;
    [HttpPost("issue/{slot}"),ValidateAntiForgeryToken]
    public async Task<IActionResult> Issue(string slot) {
        if(!await Owns(slot))return NotFound();
        Response.Headers.CacheControl="no-store";
        return Content(service.Issue(slot));
    }
    [HttpPost("new/{slot}"),ValidateAntiForgeryToken]
    public async Task<IActionResult> Submit(string slot) {
        if(!await Owns(slot))return NotFound();
        if(!Request.HasFormContentType)return BadRequest();
        var r=service.Submit(slot,Request.Form);
        if(r.Status!=303)return StatusCode(r.Status);
        Response.Headers.Location=Url.Action(nameof(Receipt),new{id=r.Row!.Id})!;
        return StatusCode(303);
    }
    [HttpGet("reconcile/{slot}/{key}")]
    public async Task<IActionResult> Reconcile(string slot,string key) {
        Response.Headers.CacheControl="no-store";
        if(!await Owns(slot))return NotFound();
        if(!Guid.TryParseExact(key,"D",out _))return BadRequest();
        var parts=store.Reconcile(slot,key).Split('|');
        return parts[0] switch {
            "UNKNOWN" when parts.Length==1=>StatusCode(202,new{state="UNKNOWN"}),
            "COMMITTED" when parts.Length==2 && int.TryParse(parts[1],out _)=>
                Ok(new{state="COMMITTED",receipt=Url.Action(nameof(Receipt),new{id=int.Parse(parts[1])})}),
            "CONFLICT" when parts.Length==1=>StatusCode(409,new{state="CONFLICT"}),
            "DENIED" when parts.Length==1=>StatusCode(403,new{state="DENIED"}),
            _=>StatusCode(503,new{state="UNAVAILABLE"})
        };
    }
    [HttpGet("receipt/{id:int}")]
    public async Task<IActionResult> Receipt(int id) {
        Response.Headers.CacheControl="no-store";
        var row=service.Find(id);
        if(row is null || !await Owns(row.Slot))return NotFound();
        return Content("Synthetic receipt "+id);
    }
}
'''
ADMIN_CONTROLLER = '''using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ScaleMvc.Data;
using ScaleMvc.Security;
namespace ScaleMvc.Areas.Admin.Controllers;
[Area("Admin"),Authorize(Roles="Researcher"),Route("admin/studies")]
public sealed class StudiesController(ScaleStore store,IAuthorizationService auth):Controller {
    private string Actor=>User.FindFirstValue(ClaimTypes.NameIdentifier)!;
    private async Task<bool> Allowed(string study)=>(await auth.AuthorizeAsync(User,new StudyResource(study),"Study")).Succeeded;
    [HttpGet("{study}")]
    public async Task<IActionResult> Index(string study) {
        Response.Headers.CacheControl="no-store";
        if(!await Allowed(study))return NotFound();
        return View("Index",store.StudyRows(Actor,study));
    }
    [HttpPost("{study}/review/{id:int}"),Authorize(Policy="Review"),ValidateAntiForgeryToken]
    public async Task<IActionResult> Review(string study,int id) {
        if(!await Allowed(study))return NotFound();
        // Query binds the actual answer's study as well as the granted study.
        return store.Review(Actor,study,id)?NoContent():Conflict();
    }
}
'''
ADMIN_VIEW = '''@model string
@{Layout=null;}
<h1>Synthetic research administration</h1><pre id="rows">@Model</pre>
<form method="post">@Html.AntiForgeryToken()</form>
'''
class DotnetMvcAdminAuthzTests(unittest.TestCase):
    def test_native_cookie_role_policy_scope_and_receipt_owner(self):
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
        with tempfile.TemporaryDirectory(prefix="mvc-admin-") as tmp, contextlib.ExitStack() as stack:
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
            sql(SCHEMA+RECONCILE+ACCESS_SCHEMA)
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
            for name,source in {"Program.cs":AUTH_HOST,"Data/ScaleStore.cs":AUTH_DATA,"Services/ScaleService.cs":SERVICES,
                                "Controllers/ScaleController.cs":OWNER_CONTROLLER,"Controllers/AccountController.cs":ACCOUNT_CONTROLLER,
                                "Security/Access.cs":ACCESS,"Areas/Admin/Controllers/StudiesController.cs":ADMIN_CONTROLLER,
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
                conn=http_client.HTTPConnection("127.0.0.1",port,timeout=15)
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
            empty=snap()
            self.assertEqual(empty,[[],[],[],[]])
            for path in ("/admin/studies/STUDY-A","/scale/receipt/1","/scale/reconcile/SYN-A/11111111-1111-4111-8111-111111111111"):
                self.assertEqual(request("GET",path)[0],401)
            self.assertEqual(request("GET","/admin/studies/STUDY-A",extra={"X-Role":"Researcher","X-User":"staff-a"})[0],401)
            badjar={}
            t=token("/account/login",badjar)
            self.assertEqual(request("POST","/account/login",badjar,{"Name":"alpha","Password":credentials["alpha"]})[0],400)
            self.assertEqual(request("POST","/account/login",badjar,{"Name":"alpha","Password":credentials["alpha"],"Role":"Researcher","__RequestVerificationToken":t})[0],400)
            actors={name:login(name) for name in credentials}
            alpha,at=actors["alpha"]
            beta,bt=actors["beta"]
            gamma,gt=actors["gamma"]
            sa,st=actors["staff-a"]
            sb,sbt=actors["staff-b"]
            ra,rt=actors["reader-a"]
            forged=dict(alpha)
            v=forged[".ScaleLab.Auth"]
            forged[".ScaleLab.Auth"]=("A" if v[0]!="A" else "B")+v[1:]
            self.assertEqual(request("GET","/account/session",forged)[0],401)
            self.assertEqual(request("GET","/admin/studies/STUDY-A",alpha)[0],403)
            self.assertEqual(request("GET","/admin/studies/STUDY-A",alpha,extra={"X-Role":"Researcher","X-User":"staff-a"})[0],403)
            self.assertEqual(request("POST","/scale/issue/SYN-B",alpha,{"__RequestVerificationToken":at})[0],404)
            self.assertEqual(request("POST","/scale/issue/SYN-A",alpha,{})[0],400)
            self.assertEqual(request("POST","/scale/issue/SYN-A",sa,{"__RequestVerificationToken":st})[0],403)
            self.assertEqual(snap(),empty)
            def issue(slot,jar,t):
                status,key,_=request("POST","/scale/issue/"+slot,jar,{"__RequestVerificationToken":t})
                self.assertEqual(status,200)
                self.assertRegex(key,r"^[0-9a-f-]{36}$")
                return key
            a=issue("SYN-A",alpha,at)
            alt=issue("SYN-A",alpha,at)
            b=issue("SYN-B",beta,bt)
            c=issue("SYN-C",gamma,gt)
            def rec(slot,key,jar,code,state=None):
                reply=request("GET","/scale/reconcile/"+slot+"/"+key,jar)
                self.assertEqual(reply[0],code,reply[1])
                if state:self.assertEqual(json.loads(reply[1])["state"],state)
                if code in (202,200,409,403) and state:
                    self.assertIn("no-store",dict((k.lower(),v) for k,v in reply[2]).get("cache-control",""))
                return reply
            def answer(slot,key,jar,t,q1):
                return request("POST","/scale/new/"+slot,jar,
                    {"Key":key,"Version":"SYN-V1","Q1":str(q1),"Q2":"","Q3":"0","__RequestVerificationToken":t})
            initial=snap()
            self.assertEqual(len(initial[2]),4)
            rec("SYN-A",a,alpha,202,"UNKNOWN")
            rec("SYN-A",b,alpha,403,"DENIED")
            rec("SYN-A",a,beta,404)
            rec("SYN-A",a,sa,403)
            self.assertEqual(answer("SYN-A",a,beta,bt,2)[0],404)
            self.assertEqual(answer("SYN-A",b,alpha,at,2)[0],400)
            badfields={"Key":a,"Version":"SYN-V1","Q1":"1","Q2":"","Q3":"0","Owner":"beta","__RequestVerificationToken":at}
            self.assertEqual(request("POST","/scale/new/SYN-A",alpha,badfields)[0],400)
            self.assertEqual(snap(),initial)
            ids=[]
            for slot,key,jar,t,q1 in (("SYN-A",a,alpha,at,1),("SYN-B",b,beta,bt,2),("SYN-C",c,gamma,gt,3)):
                reply=answer(slot,key,jar,t,q1)
                self.assertEqual(reply[0],303,reply[1])
                loc=dict((k.lower(),v) for k,v in reply[2])["location"]
                id=int(loc.rsplit("/",1)[1])
                ids.append(id)
                self.assertEqual(json.loads(rec(slot,key,jar,200,"COMMITTED")[1])["receipt"],loc)
                self.assertEqual(request("GET",loc,jar)[:2],(200,"Synthetic receipt "+str(id)))
            ia,ib,ic=ids
            committed=snap()
            self.assertEqual(committed,[[["SYN-A",a,1,None,0,ia],["SYN-B",b,2,None,0,ib],["SYN-C",c,3,None,0,ic]],
                [[i,"ACCEPTED"] for i in sorted(ids)],initial[2],[]])
            rec("SYN-A",alt,alpha,409,"CONFLICT")
            rec("SYN-A",a,beta,404)
            self.assertEqual(request("GET",f"/scale/receipt/{ia}",beta)[:2],
                             request("GET","/scale/receipt/999999",beta)[:2])
            self.assertEqual(request("GET",f"/scale/receipt/{ia}",beta)[0],404)
            self.assertEqual(request("GET",f"/scale/receipt/{ic}",alpha)[0],404)
            self.assertEqual(request("GET",f"/scale/receipt/{ia}",sa)[0],403)
            self.assertEqual(answer("SYN-A",a,alpha,at,1)[0],303)
            self.assertEqual(answer("SYN-A",a,alpha,at,5)[0],409)
            self.assertEqual(snap(),committed)
            def admin(study,jar):
                reply=request("GET","/admin/studies/"+study,jar)
                self.assertEqual(reply[0],200,reply[1])
                self.assertIn("Synthetic research administration",reply[1])
                raw=re.search(r'<pre id="rows">(.*?)</pre>',reply[1],re.S)
                self.assertIsNotNone(raw)
                return json.loads(html.unescape(raw.group(1)))
            self.assertEqual(admin("STUDY-A",sa),[{"id":ia,"slot":"SYN-A","q1":1,"reviewed":False},
                                                 {"id":ib,"slot":"SYN-B","q1":2,"reviewed":False}])
            self.assertEqual(admin("STUDY-B",sb),[{"id":ic,"slot":"SYN-C","q1":3,"reviewed":False}])
            self.assertEqual(admin("STUDY-A",ra),admin("STUDY-A",sa))
            self.assertEqual(request("GET","/admin/studies/STUDY-B",sa)[0],404)
            self.assertEqual(request("GET","/admin/studies/STUDY-A",sb)[0],404)
            def review(study,id,jar,t):
                return request("POST",f"/admin/studies/{study}/review/{id}",jar,{"__RequestVerificationToken":t})
            self.assertEqual(review("STUDY-A",ia,alpha,at)[0],403)
            self.assertEqual(review("STUDY-A",ia,ra,rt)[0],403)
            self.assertEqual(review("STUDY-B",ic,sa,st)[0],404)
            self.assertEqual(review("STUDY-A",ic,sa,st)[0],409)
            self.assertEqual(review("STUDY-A",999999,sa,st)[0],409)
            self.assertEqual(review("STUDY-A",ia,sa,bt)[0],400)
            self.assertEqual(snap(),committed)
            self.assertEqual(review("STUDY-A",ia,sa,st)[0],204)
            self.assertEqual(review("STUDY-B",ic,sb,sbt)[0],204)
            self.assertEqual(review("STUDY-A",ia,sa,st)[0],409)
            final=snap()
            self.assertEqual(final,committed[:3]+[sorted([[ia,"staff-a"],[ic,"staff-b"]])])
            self.assertTrue(admin("STUDY-A",sa)[0]["reviewed"])
            self.assertFalse(admin("STUDY-A",sa)[1]["reviewed"])
            logout=request("POST","/account/logout",alpha,{"__RequestVerificationToken":at})
            self.assertEqual(logout[0],204)
            cookies(logout,alpha)
            self.assertEqual(request("GET","/account/session",alpha)[0],401)
            self.assertEqual(snap(),final)
            print(f"DOTNET-MVC-ADMIN-AUTHZ-PASS sdk={sdk} pg={version} cookie-password-verification tamper-reject roles policy area scope owner-reconcile-receipt csrf full-negative-snapshot rows=3 reviews=2",flush=True)
