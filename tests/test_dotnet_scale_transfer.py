"""Owned synthetic scale transfer; real local MVC, no participant data."""
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

HOST = '''using ScaleMvc.Data;
using ScaleMvc.Services;
var builder = WebApplication.CreateBuilder(args);
builder.Host.UseDefaultServiceProvider(o => { o.ValidateScopes = true; o.ValidateOnBuild = true; });
builder.Services.AddControllersWithViews();
builder.Services.AddSingleton<ScaleStore>();
builder.Services.AddScoped<ScaleService>();
var app = builder.Build();
app.MapControllers();
app.Run();
'''
DATA = '''namespace ScaleMvc.Data;
public sealed record Answers(int Q1, int? Q2, int Q3);
public sealed record Receipt(int Id, string Slot, string Version, Answers Answers);
public sealed class ScaleStore {
    private readonly object gate = new();
    private readonly Dictionary<string,string> issued = new();
    private readonly Dictionary<string,Receipt> keys = new();
    private readonly Dictionary<string,Receipt> slots = new();
    public string Issue(string slot) {
        lock (gate) {
            var key = Guid.NewGuid().ToString("D");
            issued.Add(key,slot);
            return key;
        }
    }
    public (Receipt? Row,int Status) Save(string slot,string key,Answers answers) {
        lock (gate) {
            if (!issued.TryGetValue(key,out var owner) || owner != slot) return (null,400);
            if (keys.TryGetValue(key,out var prior))
                return prior.Answers == answers ? (prior,303) : (null,409);
            if (slots.ContainsKey(slot)) return (null,409);
            var row = new Receipt(slots.Count+1,slot,"SYN-V1",answers);
            slots.Add(slot,row);
            keys.Add(key,row);
            return (row,303);
        }
    }
    public object Snapshot() {
        lock (gate) return new { rows=slots.Values.OrderBy(r=>r.Id).ToArray(),
            receiptCount=keys.Count, issuedCount=issued.Count };
    }
    public Receipt? Find(int id) { lock(gate) return slots.Values.SingleOrDefault(r=>r.Id==id); }
}
'''
SERVICES = '''using Microsoft.AspNetCore.Http;
using ScaleMvc.Data;
namespace ScaleMvc.Services;
public sealed class ScaleService(ScaleStore store) {
    private static readonly HashSet<string> Allowed=new(StringComparer.Ordinal) {
        "Key","Version","Q1","Q2","Q3","__RequestVerificationToken"
    };
    public static bool ValidSlot(string slot) => slot is "SYN-A" or "SYN-B" or "SYN-C";
    private static bool Item(string raw,int min,int max,out int value) {
        value=-1;
        if (raw.Length!=1 || raw[0]<'0' || raw[0]>'9') return false;
        value=raw[0]-'0'; return value>=min && value<=max;
    }
    public string Issue(string slot)=>store.Issue(slot);
    public (Receipt? Row,int Status) Submit(string slot,IFormCollection form) {
        if (!ValidSlot(slot) || form.Files.Count!=0 ||
            form.Any(x=>!Allowed.Contains(x.Key) || x.Value.Count!=1)) return (null,400);
        if (!form.TryGetValue("Version",out var v) || v[0]!="SYN-V1" ||
            !form.TryGetValue("Key",out var k) || !Guid.TryParseExact(k[0],"D",out _) ||
            !form.TryGetValue("Q1",out var q1) || !Item(q1[0]!,1,5,out var a) ||
            !form.TryGetValue("Q3",out var q3) || !Item(q3[0]!,0,4,out var c)) return (null,400);
        int? b=null;
        if (form.TryGetValue("Q2",out var q2) && q2[0]!="") {
            if (!Item(q2[0]!,1,5,out var parsed)) return (null,400);
            b=parsed;
        }
        return store.Save(slot,k[0]!,new Answers(a,b,c));
    }
    public object Snapshot()=>store.Snapshot();
    public Receipt? Find(int id)=>store.Find(id);
}
'''
CONTROLLER = '''using Microsoft.AspNetCore.Mvc;
using ScaleMvc.Services;
namespace ScaleMvc.Controllers;
[Route("scale")]
public sealed class ScaleController(ScaleService service):Controller {
    [HttpGet("new/{slot}")]
    public IActionResult Entry([FromRoute]string slot) =>
        ScaleService.ValidSlot(slot) ? View("Entry",service.Issue(slot)) : NotFound();
    [HttpPost("new/{slot}"),ValidateAntiForgeryToken]
    public IActionResult Submit([FromRoute]string slot) {
        if (!ScaleService.ValidSlot(slot)) return NotFound();
        if (!Request.HasFormContentType) return BadRequest();
        var r=service.Submit(slot,Request.Form);
        if (r.Status!=303) return StatusCode(r.Status);
        Response.Headers.Location=Url.Action(nameof(Receipt),new {id=r.Row!.Id})!;
        return StatusCode(303);
    }
    [HttpGet("receipt/{id:int}")]
    public IActionResult Receipt([FromRoute]int id)=>service.Find(id) is null ? NotFound() : Content("Synthetic receipt "+id);
    // Test-only observation endpoint; NEVER a production API.
    [HttpGet("test-snapshot")]
    public IActionResult Snapshot()=>Json(service.Snapshot());
}
'''
ENTRY = '''@model string
@{ Layout=null; }
<html><body><form method="post">@Html.AntiForgeryToken()
<input type="hidden" name="Key" value="@Model" />
<input type="hidden" name="Version" value="SYN-V1" />
<input name="Q1" /><input name="Q2" /><input name="Q3" />
<button type="submit">Synthetic submit</button>
</form></body></html>
'''

class DotnetScaleTransferTests(unittest.TestCase):
    def test_native_scale_validation_atomic_replay_if_preinstalled(self):
        exe = shutil.which("dotnet")
        if not exe:
            self.skipTest("DOTNET_NOT_PREINSTALLED")
        exe = str(Path(exe).resolve())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            for name in ("home", "feed", "packages"):
                (root / name).mkdir()
            env = {"PATH": os.defpath, "HOME": str(root / "home"), "DOTNET_CLI_HOME": str(root / "home"),
                   "NUGET_PACKAGES": str(root / "packages"), "NUGET_HTTP_CACHE_PATH": str(root / "http-cache"),
                   "DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE": "true",
                   "DOTNET_NOLOGO": "1", "DOTNET_GENERATE_ASPNET_CERTIFICATE": "false", "MSBUILDDISABLENODEREUSE": "1",
                   "LC_ALL": "C.UTF-8", "ASPNETCORE_ENVIRONMENT": "Production", "ASPNETCORE_URLS": "http://127.0.0.1:0"}
            def run(*args, code=0, cwd=root):
                p = subprocess.run([exe, *args], cwd=cwd, env=env, capture_output=True, text=True, timeout=45)
                self.assertEqual(p.returncode, code, (p.stdout+p.stderr)[-3000:])
                return p
            versions = []
            for line in run("--list-sdks").stdout.splitlines():
                m = re.fullmatch(r"(10\.0\.\d+) \[(.+)\]", line.strip())
                if m:
                    v, sdkdir = m.groups()
                    base = Path(sdkdir).parent
                    needed = ("packs/Microsoft.NETCore.App.Ref", "packs/Microsoft.AspNetCore.App.Ref",
                              "shared/Microsoft.NETCore.App", "shared/Microsoft.AspNetCore.App")
                    if all(any((base / x).glob("10.0.*")) for x in needed):
                        versions.append(v)
            if not versions:
                self.skipTest("NO_MATCHING_PREINSTALLED_DOTNET10_ASPNETCORE")
            sdk = max(versions, key=lambda v: tuple(map(int, v.split("."))))
            (root / "global.json").write_text(json.dumps({"sdk":{"version":sdk,"rollForward":"disable","allowPrerelease":False}}))
            for name in ("Directory.Build.props", "Directory.Build.targets"):
                (root / name).write_text("<Project />")
            (root / "Directory.Build.rsp").write_text("")
            config = root / "NuGet.Config"
            config.write_text('<configuration><packageSources><clear/><add key="local" value="feed"/></packageSources></configuration>')
            self.assertEqual(run("--version").stdout.strip(), sdk)
            app=root/"ScaleMvc"
            run("new","mvc","--name","ScaleMvc","--output",str(app),"--no-restore","--no-https","--auth","None","--exclude-launch-settings")
            for name,source in {"Program.cs":HOST,"Data/ScaleStore.cs":DATA,"Services/ScaleService.cs":SERVICES,
                                "Controllers/ScaleController.cs":CONTROLLER,"Views/Scale/Entry.cshtml":ENTRY}.items():
                p=app/name
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text(source)
            project = app / "ScaleMvc.csproj"
            run("restore",str(project),"--configfile",str(config),"--packages",str(root/"packages"),"--disable-build-servers","-p:NuGetAudit=false")
            run("build",str(project),"--no-restore","--disable-build-servers","-p:UseAppHost=false")
            dll = app / "bin/Debug/net10.0/ScaleMvc.dll"
            log = root / "host.log"
            with log.open("wb") as out:
                proc = subprocess.Popen([exe,str(dll)],cwd=app,env=env,stdout=out,stderr=subprocess.STDOUT)
                try:
                    port = None
                    deadline = time.monotonic()+20
                    while time.monotonic()<deadline:
                        self.assertIsNone(proc.poll(),"HOST_EARLY_EXIT")
                        m = re.search(r"Now listening on: http://127\.0\.0\.1:(\d+)",log.read_text(errors="replace"))
                        if m:
                            port=int(m.group(1))
                            break
                        time.sleep(.05)
                    self.assertIsNotNone(port,"HOST_NOT_READY")
                    def http(method,path,fields=None,cookie=None):
                        headers={}
                        if fields is not None: headers["Content-Type"]="application/x-www-form-urlencoded"
                        if cookie: headers["Cookie"]=cookie
                        c=http_client.HTTPConnection("127.0.0.1",port,timeout=5)
                        try:
                            c.request(method,path,body=urlencode(fields) if fields is not None else None,headers=headers)
                            r=c.getresponse()
                            return r.status,r.read(65536).decode(),r.getheaders()
                        finally:
                            c.close()
                    # Black-box HTTP oracle uses literal expected values, not C# validator.
                    def snapshot():
                        status,body,_=http("GET","/scale/test-snapshot")
                        self.assertEqual(status,200)
                        return json.loads(body)
                    def form(slot):
                        status,body,hs=http("GET","/scale/new/"+slot)
                        self.assertEqual(status,200)
                        tokens=FormToken(body).tokens
                        self.assertEqual(len(tokens),1)
                        key=re.search(r'name="Key" value="([0-9a-f-]{36})"',body)
                        self.assertIsNotNone(key)
                        cookies=[v.split(";",1)[0] for k,v in hs if k.lower()=="set-cookie" and v.startswith(".AspNetCore.Antiforgery.")]
                        self.assertEqual(len(cookies),1)
                        return {"Key":key.group(1),"Version":"SYN-V1","Q1":"1","Q2":"","Q3":"0","__RequestVerificationToken":tokens[0]},cookies[0]
                    def post(slot,fields,cookie):
                        return http("POST","/scale/new/"+slot,fields,cookie)
                    def loc(response):
                        self.assertEqual(response[0],303)
                        urls=[v for k,v in response[2] if k.lower()=="location"]
                        self.assertEqual(len(urls),1)
                        return urls[0]
                    a,ac=form("SYN-A")
                    b,bc=form("SYN-B")
                    c,cc=form("SYN-C")
                    d,dc=form("SYN-C")
                    initial={"rows":[],"receiptCount":0,"issuedCount":4}
                    self.assertEqual(snapshot(),initial)
                    bad=[(dict(a,**{k:v}),ac,"SYN-A",400) for k,v in [
                        ("Q1","0"),("Q1","6"),("Q1",""),("Q1","1.0"),("Q1","true"),
                        ("Q1"," 1"),("Q1","１"),("Q2","0"),("Q2"," "),("Q2","6"),
                        ("Q3","5"),("Version","SYN-V0"),("Total","999"),
                        ("Key","11111111-1111-1111-1111-111111111111"),("__RequestVerificationToken","bad")]]
                    bad += [({k:v for k,v in a.items() if k!=missing},ac,"SYN-A",400)
                            for missing in ("Q1","Q3","Version","Key")]
                    bad += [(list(a.items())+[("Q1","5")],ac,"SYN-A",400),
                            (list(a.items())+[("Version","SYN-V0")],ac,"SYN-A",400),
                            (a,ac,"SYN-B",400),(a,None,"SYN-A",400),(a,ac,"SYN-UNKNOWN",404)]
                    for i,(data,cookie,slot,status) in enumerate(bad):
                        with self.subTest(case=i):
                            response=post(slot,data,cookie)
                            self.assertEqual(response[0],status)
                            self.assertFalse(any(k.lower()=="location" for k,v in response[2]))
                            self.assertEqual(snapshot(),initial)
                    ra={"id":1,"slot":"SYN-A","version":"SYN-V1","answers":{"q1":1,"q2":None,"q3":0}}
                    receipt=loc(post("SYN-A",a,ac))
                    self.assertEqual(receipt,"/scale/receipt/1")
                    expected={"rows":[ra],"receiptCount":1,"issuedCount":4}
                    self.assertEqual(snapshot(),expected)
                    for _ in range(2):
                        self.assertEqual(http("GET",receipt)[:2],(200,"Synthetic receipt 1"))
                        self.assertEqual(snapshot(),expected)
                    self.assertEqual(loc(post("SYN-A",{k:v for k,v in a.items() if k!="Q2"},ac)),receipt)
                    self.assertEqual(post("SYN-A",dict(a,Q2="1"),ac)[0],409)
                    self.assertEqual(snapshot(),expected)
                    def race(slot,left,right):
                        gate=Barrier(2)
                        def send(pair):
                            gate.wait(timeout=5)
                            return post(slot,*pair)
                        with ThreadPoolExecutor(max_workers=2) as pool:
                            futures=[pool.submit(send,pair) for pair in (left,right)]
                            return [f.result(timeout=10) for f in futures]
                    b.update(Q1="5",Q2="5",Q3="4")
                    replies=race("SYN-B",(b,bc),(b,bc))
                    self.assertEqual([loc(r) for r in replies],["/scale/receipt/2"]*2)
                    rb={"id":2,"slot":"SYN-B","version":"SYN-V1","answers":{"q1":5,"q2":5,"q3":4}}
                    self.assertEqual(snapshot(),{"rows":[ra,rb],"receiptCount":2,"issuedCount":4})
                    c.update(Q1="2",Q2="2",Q3="1")
                    d.update(Q1="4",Q2="4",Q3="3")
                    replies=race("SYN-C",(c,cc),(d,dc))
                    self.assertEqual(sorted(r[0] for r in replies),[303,409])
                    winner=0 if replies[0][0]==303 else 1
                    self.assertEqual(loc(replies[winner]),"/scale/receipt/3")
                    rc={"id":3,"slot":"SYN-C","version":"SYN-V1","answers":(
                        {"q1":2,"q2":2,"q3":1} if winner==0 else {"q1":4,"q2":4,"q3":3})}
                    self.assertEqual(snapshot(),{"rows":[ra,rb,rc],"receiptCount":3,"issuedCount":4})
                    print(f"DOTNET-SCALE-TRANSFER-PASS sdk={sdk} invalid={len(bad)} null-vs-zero exact-replay concurrent-key concurrent-slot rows=3",flush=True)
                finally:
                    if proc.poll() is None:
                        proc.terminate()
                        try: proc.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                            proc.wait(timeout=5)
                    self.assertIsNotNone(proc.poll())


if __name__ == "__main__":
    unittest.main()
