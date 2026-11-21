"""Native C# constants, operators and decision branches: original synthetic policy.

Reuses an already accepted offline .NET 10 / empty-feed harness. No clinical
instrument, participant data, external package, API or deployment.
"""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

PROGRAM = r'''
using System.Text.Json;
using System.Linq;

sealed record ResearchRule(string Version, int Required);

static class Lab
{
    // Compile-time structural constant. Research policy itself is versioned at runtime.
    const int EntryCount = 4;
    const string SyntheticContract = "demonstration-only-v1";

    static ResearchRule? RuleFor(string? version) => version switch
    {
        "v1" => new ResearchRule("v1", 3),
        "v2" => new ResearchRule("v2", 4),
        _ => null
    };

    static object Classify(JsonElement row)
    {
        object Reject(string reason) => new { status = reason };
        if (row.ValueKind != JsonValueKind.Object) return Reject("SHAPE");
        var fields = row.EnumerateObject().ToArray();
        if (fields.Length != 4 || fields.Select(p => p.Name).Distinct().Count() != 4 ||
            !row.TryGetProperty("version", out var version) ||
            !row.TryGetProperty("observations", out var observations) ||
            !row.TryGetProperty("consent", out var consent) ||
            !row.TryGetProperty("qualityFlag", out var flag))
            return Reject("SHAPE");
        if (version.ValueKind != JsonValueKind.String ||
            (consent.ValueKind != JsonValueKind.True &&
             consent.ValueKind != JsonValueKind.False &&
             consent.ValueKind != JsonValueKind.Null) ||
            (flag.ValueKind != JsonValueKind.True && flag.ValueKind != JsonValueKind.False))
            return Reject("TYPE");
        ResearchRule? rule = RuleFor(version.GetString());
        if (rule is null) return Reject("VERSION");
        if (observations.ValueKind != JsonValueKind.Array ||
            observations.GetArrayLength() != EntryCount)
            return Reject("SHAPE");

        int valid = 0;
        foreach (var item in observations.EnumerateArray())
        {
            if (item.ValueKind == JsonValueKind.Null) continue;
            if (item.ValueKind != JsonValueKind.Number || !item.TryGetInt32(out int n))
                return Reject("TYPE");
            if (n < 0 || n > 5) return Reject("RANGE");
            valid++;
        }
        bool? authorized = consent.ValueKind switch
        {
            JsonValueKind.True => true, JsonValueKind.False => false, _ => null
        };
        bool hold = flag.GetBoolean();

        // Precedence is intentional: deny and pending dominate ALL policy branches.
        // Do not allow quality override or partial input to bypass authorization.
        string status = authorized switch
        {
            false => "DENIED",
            null => "PENDING",
            true when hold => "QUALITY_HOLD",
            true when valid < rule.Required => "INSUFFICIENT",
            true => "READY"
        };
        return new { status, version = rule.Version, observed = valid,
                     missing = EntryCount - valid, required = rule.Required };
    }

    static object Probe()
    {
        int calls = 0;
        bool Check() { calls++; return true; }
        bool skippedAnd = false && Check();
        bool eagerAnd = false & Check();
        bool skippedOr = true || Check();
        bool eagerOr = true | Check();
        bool precedence = true || false && false;
        bool grouped = (true || false) && false;
        bool? unknown = null;
        bool? liftedAnd = unknown & false;
        bool? liftedOr = unknown | false;
        bool dangerousUnknownNotFalse = unknown != false;
        string? label = null;
        string before = label ?? "fallback";
        label ??= "v1";
        bool qualityOverride = true, authorized = false, enough = true;
        bool unsafeOverride = enough && authorized || qualityOverride;
        bool guarded = enough && authorized && !qualityOverride;
        return new {
            contract = SyntheticContract,
            skippedAnd, eagerAnd, skippedOr, eagerOr, calls,
            precedence, grouped,
            liftedAnd, liftedOr, dangerousUnknownNotFalse,
            coalescedAuthorization = unknown ?? false,
            before, after = label, unsafeOverride, guarded
        };
    }
    static int Main(string[] args)
    {
        // No dependency on current culture for machine-readable outputs.
        System.Globalization.CultureInfo.CurrentCulture =
            System.Globalization.CultureInfo.GetCultureInfo(args[1]);
        using var document = JsonDocument.Parse(File.ReadAllBytes(args[0]));
        if (document.RootElement.ValueKind != JsonValueKind.Array) return 2;
        Console.WriteLine(JsonSerializer.Serialize(new {
            probe = Probe(),
            rows = document.RootElement.EnumerateArray().Select(Classify).ToArray()
        }));
        return 0;
    }
}
'''

class CsharpPolicyBranchingTests(unittest.TestCase):
    def test_native_versioned_policy_and_decision_boundaries(self):
        exe = shutil.which("dotnet")
        if not exe:
            if os.environ.get("GITHUB_ACTIONS") == "true":
                self.fail("PREINSTALLED_DOTNET_REQUIRED")
            self.skipTest("native .NET unavailable")
        exe = str(Path(exe).resolve())
        with tempfile.TemporaryDirectory(prefix="csharp-policy-branching-") as tmp:
            root = Path(tmp).resolve()
            for name in ("home", "feed", "packages"):
                (root/name).mkdir(mode=0o700)
            env = {"PATH":os.defpath, "HOME":str(root/"home"),
                   "DOTNET_CLI_HOME":str(root/"home"), "NUGET_PACKAGES":str(root/"packages"),
                   "NUGET_HTTP_CACHE_PATH":str(root/"http-cache"),
                   "DOTNET_CLI_TELEMETRY_OPTOUT":"1", "DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE":"true",
                   "DOTNET_NOLOGO":"1", "DOTNET_GENERATE_ASPNET_CERTIFICATE":"false",
                   "MSBUILDDISABLENODEREUSE":"1", "LC_ALL":"C.UTF-8"}
            def run(*args, ok=True):
                p = subprocess.run([exe,*args], cwd=root, env=env, capture_output=True,
                                   text=True, timeout=60)
                self.assertEqual(p.returncode == 0, ok, (args,(p.stdout+p.stderr)[-4000:]))
                return p.stdout if ok else p.stdout+p.stderr
            versions = []
            for line in run("--list-sdks").splitlines():
                match = re.fullmatch(r"(10\.0\.\d+) \[(.+)\]", line.strip())
                if match:
                    v, sdkdir = match.groups()
                    base = Path(sdkdir).parent
                    if all(any((base/p).glob("10.0.*")) for p in
                           ("packs/Microsoft.NETCore.App.Ref","shared/Microsoft.NETCore.App")):
                        versions.append(v)
            self.assertTrue(versions, "installed .NET 10 SDK/ref/runtime required")
            sdk = max(versions, key=lambda v:tuple(map(int,v.split("."))))
            (root/"global.json").write_text(json.dumps({"sdk":{"version":sdk,"rollForward":"disable","allowPrerelease":False}}))
            for name in ("Directory.Build.props","Directory.Build.targets"):
                (root/name).write_text("<Project />")
            (root/"Directory.Build.rsp").write_text("")
            config = root/"NuGet.Config"
            config.write_text('<configuration><packageSources><clear/><add key="local" value="feed"/></packageSources></configuration>')
            self.assertEqual(run("--version").strip(), sdk)
            app = root/"PolicyBranching"
            run("new","console","--framework","net10.0","--name","PolicyBranching",
                "--output",str(app),"--no-restore")
            program = app/"Program.cs"
            program.write_text(PROGRAM, encoding="utf-8")
            project = str(app/"PolicyBranching.csproj")
            run("restore",project,"--configfile",str(config),"--packages",str(root/"packages"),
                "--disable-build-servers","-p:NuGetAudit=false")
            assets = json.loads((app/"obj/project.assets.json").read_text())
            self.assertEqual(assets["libraries"], {})
            self.assertEqual(list((root/"packages").iterdir()), [])
            run("build",project,"--no-restore","--disable-build-servers","-p:UseAppHost=false")
            dll = app/"bin/Debug/net10.0/PolicyBranching.dll"
            self.assertTrue(dll.is_file())
            # External fixed oracle: compare branch, observed/missing and version.
            cases = []
            def scenario(version, values, consent=True, hold=False):
                return json.dumps(dict(version=version, observations=values,
                                       consent=consent, qualityFlag=hold))
            def accepted(version, values, consent, hold, status, observed, required):
                cases.append((scenario(version, values, consent, hold),
                              dict(status=status, version=version, observed=observed,
                                   missing=4-observed, required=required)))
            def rejected(raw, status):
                cases.append((raw, dict(status=status)))

            accepted("v1", [0, 1, 2, None], True, False, "READY", 3, 3)
            accepted("v2", [0, 1, 2, None], True, False, "INSUFFICIENT", 3, 4)
            accepted("v2", [0, 1, 2, 3], True, False, "READY", 4, 4)
            accepted("v1", [None, None, None, None], True, False, "INSUFFICIENT", 0, 3)
            accepted("v1", [0, 0, 0, None], False, False, "DENIED", 3, 3)
            accepted("v1", [0, 0, 0, None], None, False, "PENDING", 3, 3)
            accepted("v1", [0, 0, 0, None], True, True, "QUALITY_HOLD", 3, 3)
            accepted("v1", [0, 0, 0, None], False, True, "DENIED", 3, 3)
            accepted("v1", [0, 0, 0, None], None, True, "PENDING", 3, 3)
            accepted("v1", [0, 5, None, None], True, False, "INSUFFICIENT", 2, 3)
            accepted("v2", [0, 0, 0, 0], True, True, "QUALITY_HOLD", 4, 4)
            accepted("v1", [5, 0, 5, None], True, False, "READY", 3, 3)

            rejected("null", "SHAPE")
            rejected('{"version":"v1","observations":[1,2,3,null],"consent":true}',"SHAPE")
            rejected('{"version":"v1","observations":[1,2,3,null],"consent":true,"qualityFlag":false,"version":"v2"}',"SHAPE")
            rejected('{"version":"v3","observations":[1,2,3,null],"consent":true,"qualityFlag":false}',"VERSION")
            rejected('{"version":1,"observations":[1,2,3,null],"consent":true,"qualityFlag":false}',"TYPE")
            rejected('{"version":"v1","observations":[1,2,3,null],"consent":1,"qualityFlag":false}',"TYPE")
            rejected('{"version":"v1","observations":[1,2,3,null],"consent":true,"qualityFlag":null}',"TYPE")
            rejected('{"version":"v1","observations":[],"consent":true,"qualityFlag":false}',"SHAPE")
            rejected('{"version":"v1","observations":null,"consent":true,"qualityFlag":false}',"SHAPE")
            rejected('{"version":"v1","observations":[0,true,1,null],"consent":true,"qualityFlag":false}',"TYPE")
            rejected('{"version":"v1","observations":[0,1.5,1,null],"consent":true,"qualityFlag":false}',"TYPE")
            rejected('{"version":"v1","observations":[0,6,1,null],"consent":true,"qualityFlag":false}',"RANGE")
            rejected('{"version":"v1","observations":[0,-1,1,null],"consent":true,"qualityFlag":false}',"RANGE")
            rejected('{"version":"v1","observations":[0,2147483648,1,null],"consent":true,"qualityFlag":false}',"TYPE")
            rejected('{"version":"v1","observations":[0,"1",1,null],"consent":true,"qualityFlag":false}',"TYPE")
            expected = [value for _,value in cases]
            payload = ("[" + ",".join(row for row,_ in cases) + "]").encode("utf-8")
            sample = root/"sample.json"
            sample.write_bytes(payload)
            first = run(str(dll),str(sample),"en-US")
            second = run(str(dll),str(sample),"de-DE")
            self.assertEqual(first,second)
            result = json.loads(first)
            self.assertEqual(result["rows"],expected)
            self.assertEqual(sample.read_bytes(),payload)
            self.assertEqual(result["probe"],{
                "contract":"demonstration-only-v1",
                "skippedAnd":False,"eagerAnd":False,"skippedOr":True,"eagerOr":True,"calls":2,
                "precedence":True,"grouped":False,
                "liftedAnd":False,"liftedOr":None,"dangerousUnknownNotFalse":True,
                "coalescedAuthorization":False,
                "before":"fallback","after":"v1","unsafeOverride":True,"guarded":False
            })
            # Compiler diagnostics are genuine negative tests, no previous DLL reuse.
            for index,(source,error) in enumerate([
                ("const int Rule = 3;\nRule = 4;\n", "CS0131"),
                ("const int Rule = DateTime.Now.Day;\nConsole.WriteLine(Rule);\n","CS0133"),
                ("if (1) Console.WriteLine(1);\n","CS0029")
            ]):
                program.write_text(source, encoding="utf-8")
                bad_dir=root/f"bad-output-{index}"
                failure=run("build",project,"--no-restore","--disable-build-servers",
                            "-p:UseAppHost=false","--output",str(bad_dir),ok=False)
                self.assertIn(error,failure)
                self.assertFalse((bad_dir/"PolicyBranching.dll").exists())
            print(f"CSHARP-POLICY-BRANCHING-PASS sdk={sdk} positive=12 negative=15 "
                  "compiler-negative=3 versioned-policy precedence nullable-authorization "
                  "short-circuit-side-effects culture-identical empty-feed",flush=True)
