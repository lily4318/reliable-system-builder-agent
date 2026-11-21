"""Native built-in console/MVC fixtures; no third-party packages or external host."""
import http.client
from html.parser import HTMLParser
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

CONSOLE = '''using System.Globalization;
string? input = args.Length == 1 ? args[0] : args.Length == 0 ? Console.ReadLine() : null;
if (!int.TryParse(input, NumberStyles.None, CultureInfo.InvariantCulture, out int score) || score < 1 || score > 5) {
    Console.Error.WriteLine("invalid-score");
    return 2;
}
Console.WriteLine($"score={score}");
return 0;
'''
CONTROLLER = '''using System.ComponentModel.DataAnnotations;
using Microsoft.AspNetCore.Mvc;
namespace StudyMvc.Controllers;
public sealed class StudyInput {
    [Required, StringLength(40)] public string? Title { get; set; }
    [Required, Range(1, 5)] public int? Score { get; set; }
}
[Route("study")]
public sealed class StudyController : Controller {
    private static int accepted;
    [HttpGet("{id:int}")]
    public IActionResult Entry([FromRoute] int id, [FromQuery] string? note) {
        if (id != 7) return NotFound();
        ViewData["Note"] = note;
        return View("Entry", new StudyInput());
    }
    [HttpPost("{id:int}"), ValidateAntiForgeryToken]
    public IActionResult Submit([FromRoute] int id, [FromForm] StudyInput input) {
        if (id != 7) return NotFound();
        if (!ModelState.IsValid) { Response.StatusCode = 400; return View("Entry", input); }
        Interlocked.Increment(ref accepted);
        return View("Receipt", input);
    }
    [HttpGet("count")]
    public IActionResult Count() => Content(Volatile.Read(ref accepted).ToString(System.Globalization.CultureInfo.InvariantCulture));
}
'''
ENTRY = '''@model StudyMvc.Controllers.StudyInput
@{ Layout = null; }
<!DOCTYPE html><html><body><p id="note">@ViewData["Note"]</p>
<form method="post" action="/study/7">@Html.AntiForgeryToken()
<label for="Title">Title</label><input id="Title" name="Title" value="@Model.Title" />
<label for="Score">Score</label><input id="Score" name="Score" value="@Model.Score" />
@Html.ValidationSummary(false)<button type="submit">Submit</button></form></body></html>
'''
RECEIPT = '''@model StudyMvc.Controllers.StudyInput
@{ Layout = null; }
<!DOCTYPE html><html><body><p id="receipt">Accepted: @Model.Title / @Model.Score</p></body></html>
'''


class FormToken(HTMLParser):
    def __init__(self, body):
        super().__init__()
        self.tokens = []
        self.feed(body)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "input" and a.get("name") == "__RequestVerificationToken":
            self.tokens.append(a.get("value"))


class DotnetConsoleMvcTests(unittest.TestCase):
    def test_native_console_and_mvc_if_preinstalled(self):
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
                   "DOTNET_NOLOGO": "1", "DOTNET_GENERATE_ASPNET_CERTIFICATE": "false", "MSBUILDDISABLENODEREUSE": "1", "LC_ALL": "C.UTF-8"}

            def run(*args, code=0, stdin="", cwd=root):
                p = subprocess.run([exe, *args], cwd=cwd, env=env, input=stdin, capture_output=True, text=True, timeout=45)
                self.assertEqual(p.returncode, code, (p.stdout + p.stderr)[-3000:])
                return p

            versions = []
            for line in run("--list-sdks").stdout.splitlines():
                m = re.fullmatch(r"(10\.0\.\d+) \[(.+)\]", line.strip())
                if m:
                    v, sdkdir = m.groups()
                    base = Path(sdkdir).parent
                    needed = ["packs/Microsoft.NETCore.App.Ref", "packs/Microsoft.AspNetCore.App.Ref",
                              "shared/Microsoft.NETCore.App", "shared/Microsoft.AspNetCore.App"]
                    if all(any((base / x).glob("10.0.*")) for x in needed):
                        versions.append(v)
            if not versions:
                self.skipTest("NO_MATCHING_PREINSTALLED_DOTNET10_ASPNETCORE")
            sdk = max(versions, key=lambda v: tuple(map(int, v.split('.'))))
            (root / "global.json").write_text(json.dumps({"sdk": {"version": sdk, "rollForward": "disable", "allowPrerelease": False}}))
            for name in ("Directory.Build.props", "Directory.Build.targets"):
                (root / name).write_text("<Project />")
            (root / "Directory.Build.rsp").write_text("")
            config = root / "NuGet.Config"
            config.write_text('<configuration><packageSources><clear/><add key="local" value="feed"/></packageSources></configuration>')
            self.assertEqual(run("--version").stdout.strip(), sdk)

            def build(name):
                project = root / name / (name + ".csproj")
                run("restore", str(project), "--configfile", str(config), "--packages", str(root / "packages"), "--disable-build-servers", "-p:NuGetAudit=false")
                run("build", str(project), "--no-restore", "--disable-build-servers", "-p:UseAppHost=false")
                return root / name / "bin/Debug/net10.0" / (name + ".dll")

            run("new", "console", "--name", "ScoreCli", "--output", str(root / "ScoreCli"), "--no-restore")
            (root / "ScoreCli/Program.cs").write_text(CONSOLE)
            cli = str(build("ScoreCli"))
            for args, stdin, expected in [(('1',), '', 'score=1'), (('5',), '', 'score=5'), ((), '3\n', 'score=3')]:
                p = run(cli, *args, stdin=stdin)
                self.assertEqual(p.stdout.strip(), expected)
                self.assertEqual(p.stderr, "")
            for args, stdin in [(('0',), ''), (('6',), ''), (('x',), ''), (('2147483648',), ''), (('2','3'), ''), ((), '')]:
                p = run(cli, *args, stdin=stdin, code=2)
                self.assertEqual(p.stdout, "")
                self.assertEqual(p.stderr.strip(), "invalid-score")
            print(f"DOTNET-CONSOLE-PASS sdk={sdk} valid=3 invalid=6", flush=True)

            mvc = root / "StudyMvc"
            run("new", "mvc", "--name", "StudyMvc", "--output", str(mvc), "--no-restore", "--no-https", "--auth", "None", "--exclude-launch-settings")
            self.assertTrue((mvc / "Controllers/HomeController.cs").is_file())
            (mvc / "Controllers/StudyController.cs").write_text(CONTROLLER)
            views = mvc / "Views/Study"
            views.mkdir()
            (views / "Entry.cshtml").write_text(ENTRY)
            (views / "Receipt.cshtml").write_text(RECEIPT)
            dll = build("StudyMvc")
            log = root / "host.log"
            host_env = dict(env, ASPNETCORE_URLS="http://127.0.0.1:0", ASPNETCORE_ENVIRONMENT="Production")
            with log.open("wb") as out:
                proc = subprocess.Popen([exe, str(dll)], cwd=mvc, env=host_env, stdout=out, stderr=subprocess.STDOUT)
                try:
                    deadline = time.monotonic() + 20
                    port = None
                    while time.monotonic() < deadline:
                        if proc.poll() is not None:
                            self.fail(f"HOST_EARLY_EXIT {proc.returncode}")
                        match = re.search(r"Now listening on: http://127\.0\.0\.1:(\d+)", log.read_text(errors="replace"))
                        if match:
                            port = int(match.group(1))
                            break
                        time.sleep(.05)
                    self.assertIsNotNone(port, "HOST_READINESS_TIMEOUT")

                    def request(method, path, fields=None, cookie=None):
                        headers = {}
                        if fields is not None:
                            headers["Content-Type"] = "application/x-www-form-urlencoded"
                        if cookie:
                            headers["Cookie"] = cookie
                        con = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                        try:
                            con.request(method, path, body=urlencode(fields) if fields is not None else None, headers=headers)
                            response = con.getresponse()
                            return response.status, response.read(65536).decode(), response.getheaders()
                        finally:
                            con.close()

                    def count(n):
                        status, body, _ = request("GET", "/study/count")
                        self.assertEqual((status, body), (200, str(n)))

                    status, body, headers = request("GET", "/study/7?note=%3Cscript%3E")
                    self.assertEqual(status, 200)
                    self.assertIn("&lt;script&gt;", body)
                    self.assertNotIn("<script>", body)
                    tokens = FormToken(body).tokens
                    self.assertEqual(len(tokens), 1)
                    token = tokens[0]
                    self.assertTrue(token)
                    cookies = [v.split(';', 1)[0] for k, v in headers if k.lower() == "set-cookie" and v.startswith(".AspNetCore.Antiforgery.")]
                    self.assertEqual(len(cookies), 1)
                    cookie = cookies[0]
                    count(0)
                    for path, code in [("/study/abc", 404), ("/study/8", 404), ("/missing", 404)]:
                        self.assertEqual(request("GET", path)[0], code)
                    self.assertEqual(request("PUT", "/study/7")[0], 405)
                    base = {"Title": "Synthetic", "Score": "3", "__RequestVerificationToken": token}
                    for fields, c in [({"Title":"Synthetic", "Score":"3"}, cookie), (base, None), (dict(base, __RequestVerificationToken="invalid"), cookie)]:
                        self.assertEqual(request("POST", "/study/7", fields, c)[0], 400)
                        count(0)
                    for bad in [dict(base, Score="x"), dict(base, Score="0"), dict(base, Score="6"), dict(base, Score=""), dict(base, Title=""), dict(base, Title="A"*41)]:
                        status, body, _ = request("POST", "/study/7", bad, cookie)
                        self.assertEqual(status, 400)
                        self.assertIn("validation-summary-errors", body)
                        count(0)
                    self.assertEqual(request("POST", "/study/8", base, cookie)[0], 404)
                    count(0)
                    status, body, _ = request("POST", "/study/7?Score=5", dict(base, Title="<b>Sample</b>", id="8", IsAdmin="true"), cookie)
                    self.assertEqual(status, 200)
                    self.assertIn("Accepted: &lt;b&gt;Sample&lt;/b&gt; / 3", body)
                    self.assertNotIn("<b>Sample</b>", body)
                    count(1)
                    print(f"DOTNET-MVC-NATIVE-PASS sdk={sdk} route binding validation antiforgery encoding count=1", flush=True)
                finally:
                    if proc.poll() is None:
                        proc.terminate()
                        try:
                            proc.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                            proc.wait(timeout=5)
                    self.assertIsNotNone(proc.poll())


if __name__ == "__main__":
    unittest.main()
