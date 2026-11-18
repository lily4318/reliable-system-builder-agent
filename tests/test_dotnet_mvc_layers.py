"""Owned MVC layering, real DI container and PRG; no external packages."""
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
from urllib.parse import urlencode

from test_dotnet_console_mvc import FormToken

HOST = '''using FlowMvc.Services;
using FlowMvc.Data;
var builder = WebApplication.CreateBuilder(args);
builder.Host.UseDefaultServiceProvider(o => { o.ValidateScopes = true; o.ValidateOnBuild = true; });
builder.Services.AddControllersWithViews();
builder.Services.AddSingleton<StudyStore>();
builder.Services.AddSingleton<SharedProbe>();
builder.Services.AddScoped<RequestProbe>();
builder.Services.AddTransient<FreshProbe>();
builder.Services.AddScoped<StudyService>();
if (args.Contains("--bad-scope")) builder.Services.AddSingleton<BadCapture>();
WebApplication app;
try { app = builder.Build(); }
catch (AggregateException e) when (args.Contains("--bad-scope") && e.ToString().Contains("Cannot consume scoped service")) {
    Console.Error.WriteLine("CAPTIVE_SCOPE_REJECTED");
    return 23;
}
app.MapControllers();
app.Run();
return 0;
'''
DATA = '''namespace FlowMvc.Data;
public sealed record Receipt(int Id, string Key, string Title, int Score);
public sealed class StudyStore {
    private readonly object gate = new();
    private readonly Dictionary<string, Receipt> rows = new();
    public (Receipt? Row, bool Conflict) Save(string key, string title, int score) {
        lock (gate) {
            if (rows.TryGetValue(key, out var prior))
                return prior.Title == title && prior.Score == score ? (prior, false) : (null, true);
            var row = new Receipt(rows.Count + 1, key, title, score);
            rows.Add(key, row);
            return (row, false);
        }
    }
    public Receipt? Find(int id) { lock (gate) return rows.Values.SingleOrDefault(r => r.Id == id); }
    public int Count { get { lock (gate) return rows.Count; } }
}
'''
SERVICES = '''using FlowMvc.Data;
namespace FlowMvc.Services;
public sealed class RequestProbe { public Guid Id { get; } = Guid.NewGuid(); }
public sealed class SharedProbe { public Guid Id { get; } = Guid.NewGuid(); }
public sealed class FreshProbe { public Guid Id { get; } = Guid.NewGuid(); }
public sealed class BadCapture(RequestProbe scoped) { public RequestProbe Captured { get; } = scoped; }
public sealed class StudyService(StudyStore store, RequestProbe probe) {
    public Guid ScopeId => probe.Id;
    public (Receipt? Row, string Status) Submit(string key, string title, int score) {
        // Synthetic domain rule, deliberately stronger than the form annotations.
        if (!Guid.TryParseExact(key, "D", out _) || string.IsNullOrWhiteSpace(title) ||
            title.Length > 40 || score is < 1 or > 5 || (score == 5 && title.Trim().Length < 3))
            return (null, "invalid");
        var result = store.Save(key, title, score);
        return (result.Row, result.Conflict ? "conflict" : "ok");
    }
    public Receipt? Find(int id) => store.Find(id);
    public int Count => store.Count;
}
'''
CONTROLLER = '''using System.ComponentModel.DataAnnotations;
using Microsoft.AspNetCore.Mvc;
using FlowMvc.Services;
namespace FlowMvc.Controllers;
public sealed class EntryInput {
    [Required] public string? Key { get; set; }
    [Required, StringLength(40)] public string? Title { get; set; }
    [Required, Range(1, 5)] public int? Score { get; set; }
}
[Route("flow")]
public sealed class FlowController(StudyService service, RequestProbe scoped, SharedProbe shared, FreshProbe fresh) : Controller {
    [HttpGet("new")]
    public IActionResult Entry() => View("Entry", new EntryInput { Key = Guid.NewGuid().ToString("D") });
    [HttpGet("lifetimes")]
    public IActionResult Lifetimes([FromServices] RequestProbe again, [FromServices] FreshProbe other) =>
        Json(new { scope = scoped.Id, service = service.ScopeId, again = again.Id, shared = shared.Id, fresh = fresh.Id, other = other.Id });
    [HttpGet("count")]
    public IActionResult Count() => Content(service.Count.ToString(System.Globalization.CultureInfo.InvariantCulture));
    [HttpPost("new"), ValidateAntiForgeryToken]
    public IActionResult Submit([FromForm] EntryInput input) {
        if (!ModelState.IsValid) { Response.StatusCode = 400; return View("Entry", input); }
        var result = service.Submit(input.Key!, input.Title!, input.Score!.Value);
        if (result.Status == "conflict") return Conflict();
        if (result.Status == "invalid") { ModelState.AddModelError("", "domain-invalid"); Response.StatusCode = 400; return View("Entry", input); }
        Response.Headers.Location = Url.Action(nameof(Receipt), new { id = result.Row!.Id })!;
        return StatusCode(303);
    }
    [HttpGet("receipt/{id:int}")]
    public IActionResult Receipt(int id) {
        var row = service.Find(id);
        return row is null ? NotFound() : View("Receipt", row);
    }
}
'''
ENTRY = '''@model FlowMvc.Controllers.EntryInput
@{ Layout = null; }
<html><body><form method="post" action="/flow/new">@Html.AntiForgeryToken()
<input type="hidden" name="Key" value="@Model.Key" />
<input name="Title" value="@Model.Title" /><input name="Score" value="@Model.Score" />
@Html.ValidationSummary(false)<button type="submit">Submit</button></form></body></html>
'''
RECEIPT = '''@model FlowMvc.Data.Receipt
@{ Layout = null; }
<html><body><p id="receipt">Receipt @Model.Id: @Model.Title / @Model.Score</p></body></html>
'''


class DotnetMvcLayersTests(unittest.TestCase):
    def test_native_layered_mvc_di_prg_if_preinstalled(self):
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
            app = root / "FlowMvc"
            run("new","mvc","--name","FlowMvc","--output",str(app),"--no-restore","--no-https","--auth","None","--exclude-launch-settings")
            for name, source in {"Program.cs": HOST, "Data/StudyStore.cs": DATA, "Services/StudyService.cs": SERVICES,
                                 "Controllers/FlowController.cs": CONTROLLER, "Views/Flow/Entry.cshtml": ENTRY,
                                 "Views/Flow/Receipt.cshtml": RECEIPT}.items():
                p = app / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(source)
            project = app / "FlowMvc.csproj"
            run("restore",str(project),"--configfile",str(config),"--packages",str(root/"packages"),"--disable-build-servers","-p:NuGetAudit=false")
            run("build",str(project),"--no-restore","--disable-build-servers","-p:UseAppHost=false")
            dll = app / "bin/Debug/net10.0/FlowMvc.dll"
            red = run(str(dll),"--bad-scope",code=23,cwd=app)
            self.assertIn("CAPTIVE_SCOPE_REJECTED", red.stderr)
            self.assertNotIn("Now listening on:", red.stdout)
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
                    def count(n):
                        self.assertEqual(http("GET","/flow/count")[:2],(200,str(n)))
                    def probe():
                        status,body,_=http("GET","/flow/lifetimes")
                        self.assertEqual(status,200)
                        p=json.loads(body)
                        self.assertEqual(p["scope"],p["service"])
                        self.assertEqual(p["scope"],p["again"])
                        self.assertNotEqual(p["fresh"],p["other"])
                        return p
                    p,q=probe(),probe()
                    self.assertNotEqual(p["scope"],q["scope"])
                    self.assertEqual(p["shared"],q["shared"])
                    self.assertNotEqual(p["fresh"],q["fresh"])
                    print(f"DOTNET-MVC-DI-PASS sdk={sdk} scoped transient singleton captive-reject",flush=True)
                    def form():
                        status,body,hs=http("GET","/flow/new")
                        self.assertEqual(status,200)
                        tokens=FormToken(body).tokens
                        self.assertEqual(len(tokens),1)
                        key=re.search(r'name="Key" value="([0-9a-f-]{36})"',body)
                        self.assertIsNotNone(key)
                        cookies=[v.split(";",1)[0] for k,v in hs if k.lower()=="set-cookie" and v.startswith(".AspNetCore.Antiforgery.")]
                        self.assertEqual(len(cookies),1)
                        return {"Key":key.group(1),"Title":"Synthetic","Score":"3","__RequestVerificationToken":tokens[0]},cookies[0]
                    fields,cookie=form()
                    count(0)
                    for bad in (dict(fields, Score="x"), dict(fields, Title="X", Score="5"), dict(fields, Key="bad")):
                        status,body,hs=http("POST","/flow/new",bad,cookie)
                        self.assertEqual(status,400)
                        self.assertFalse(any(k.lower()=="location" for k,v in hs))
                        count(0)
                    self.assertEqual(http("POST","/flow/new",fields)[0],400)
                    count(0)
                    def submit(data):
                        status,_,hs=http("POST","/flow/new?returnUrl=https%3A%2F%2Fexample.invalid",data,cookie)
                        self.assertEqual(status,303)
                        locations=[v for k,v in hs if k.lower()=="location"]
                        self.assertEqual(len(locations),1)
                        return locations[0]
                    loc=submit(fields)
                    self.assertEqual(loc,"/flow/receipt/1")
                    count(1)
                    for _ in range(2):
                        status,body,_=http("GET",loc)
                        self.assertEqual(status,200)
                        self.assertIn("Receipt 1: Synthetic / 3",body)
                        count(1)
                    self.assertEqual(submit(fields),loc)
                    count(1)
                    self.assertEqual(http("POST","/flow/new",dict(fields,Score="4"),cookie)[0],409)
                    count(1)
                    self.assertEqual(http("GET","/flow/receipt/99")[0],404)
                    self.assertEqual(http("PUT","/flow/new")[0],405)
                    print("DOTNET-MVC-PRG-PASS 303 local receipt refresh replay conflict domain-invalid count=1",flush=True)
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
