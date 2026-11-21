"""Native C# bounded iteration and methods: independent synthetic event-stream lab.

Tests a bounded parser, explicit stop semantics, nullable values, duplicate
event identities, pure method output, ref/out parameters, iterator disposal and
failure isolation. No participant data, third-party packages, external API or deployment.
"""
from itertools import product
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
using System.Collections.Generic;
using System.Linq;
using System.Globalization;

record Reply(string status, int inspected, int valid, int missing, int? sum);

static class Lab
{
    const int MaxBudget = 8;
    static int pulled;
    static int closed;
    static int faultDisposed;

    static Reply Error(string status, int steps = 0, int valid = 0, int missing = 0)
        => new(status, steps, valid, missing, null);

    static Reply Evaluate(JsonElement row)
    {
        if (row.ValueKind != JsonValueKind.Object) return Error("SHAPE");
        var fields = row.EnumerateObject().ToArray();
        if (fields.Length != 2 || fields.Select(p => p.Name).Distinct().Count() != 2
            || !row.TryGetProperty("events", out var events)
            || !row.TryGetProperty("limit", out var limit))
            return Error("SHAPE");
        if (events.ValueKind != JsonValueKind.Array) return Error("SHAPE");
        if (limit.ValueKind != JsonValueKind.Number || !limit.TryGetInt32(out int budget))
            return Error("TYPE");
        if (budget < 1 || budget > MaxBudget) return Error("LIMIT");

        int inspected = 0, valid = 0, missing = 0, sum = 0;
        var seen = new HashSet<string>(StringComparer.Ordinal);
        foreach (var item in events.EnumerateArray())
        {
            // Bound BEFORE inspecting the next event; a missing STOP cannot
            // provoke unbounded iteration or an accidental partial score.
            if (inspected >= budget) return Error("BUDGET", inspected, valid, missing);
            inspected++;
            if (item.ValueKind != JsonValueKind.Object)
                return Error("EVENT", inspected, valid, missing);
            var parts = item.EnumerateObject().ToArray();
            if (parts.Select(p => p.Name).Distinct().Count() != parts.Length
                || !item.TryGetProperty("kind", out var kind)
                || kind.ValueKind != JsonValueKind.String)
                return Error("EVENT", inspected, valid, missing);
            string? type = kind.GetString();
            if (type == "stop")
            {
                if (parts.Length != 1) return Error("EVENT", inspected, valid, missing);
                // Explicit early return. Following elements are outside this
                // synthetic stream's declared observation window.
                return new("STOP", inspected, valid, missing, sum);
            }
            if (type != "sample" || parts.Length != 3
                || !item.TryGetProperty("id", out var id)
                || !item.TryGetProperty("value", out var value))
                return Error("EVENT", inspected, valid, missing);
            if (id.ValueKind != JsonValueKind.String)
                return Error("TYPE", inspected, valid, missing);
            string? key = id.GetString();
            if (key is null || key.Length != 2 || key.Any(ch => ch < '0' || ch > '9'))
                return Error("EVENT", inspected, valid, missing);
            if (!seen.Add(key)) return Error("DUPLICATE", inspected, valid, missing);
            if (value.ValueKind == JsonValueKind.Null) { missing++; continue; }
            if (value.ValueKind != JsonValueKind.Number || !value.TryGetInt32(out int n))
                return Error("TYPE", inspected, valid, missing);
            if (n < 0 || n > 5) return Error("RANGE", inspected, valid, missing);
            sum = checked(sum + n);
            valid++;
        }
        return new("DONE", inspected, valid, missing, sum);
    }

    static int PureSum(ReadOnlySpan<int?> items)
    {
        int result = 0;
        foreach (int? item in items)
        {
            if (item.HasValue) result = checked(result + item.Value);
        }
        return result;
    }

    // out result is set only after all checks, not after each row.
    static bool TryBoundedSum(ReadOnlySpan<int?> items, int budget,
                              out int valid, out int total)
    {
        valid = 0;
        total = 0;
        if (budget < 0 || items.Length > budget) return false;
        int nextValid = 0, nextTotal = 0;
        foreach (int? item in items)
        {
            if (!item.HasValue) continue;
            if (item.Value < 0 || item.Value > 5) return false;
            nextValid++;
            nextTotal = checked(nextTotal + item.Value);
        }
        valid = nextValid; total = nextTotal;
        return true;
    }

    static void Rebind(int?[] items) { items = new int?[] { 5 }; }
    static void DeliberatelyMutate(int?[] items) { items[0] = 5; }
    static void Increment(ref int count) { count++; }

    static IEnumerable<int> Early()
    {
        try
        {
            for (int i = 0; i < 6; i++) { pulled++; yield return i; }
        }
        finally { closed++; }
    }

    static IEnumerable<int> Faulty()
    {
        try
        {
            yield return 2;
            throw new InvalidOperationException("synthetic iterator failure");
        }
        finally { faultDisposed++; }
    }

    static object Probe()
    {
        int?[] original = { 0, null, 2 };
        int pure = PureSum(original);
        bool good = TryBoundedSum(original, 3, out int goodCount, out int goodTotal);
        bool bad = TryBoundedSum(new int?[] { 0, 6 }, 2, out int badCount, out int badTotal);
        bool budgetBad = TryBoundedSum(original, 2, out int budgetCount, out int budgetTotal);
        Rebind(original);
        int?[] aliased = (int?[])original.Clone();
        DeliberatelyMutate(aliased);
        int counter = 2;
        Increment(ref counter);

        foreach (int n in Early()) { if (n == 2) break; }

        int? committed = null;
        bool caught = false;
        try
        {
            int pending = 0;
            foreach (int n in Faulty()) pending += n;
            committed = pending; // only publish after complete enumeration
        }
        catch (InvalidOperationException) { caught = true; }

        int whileCount = 0;
        while (false) { whileCount++; }
        int doCount = 0;
        do { doCount++; } while (false);
        int oddSum = 0;
        for (int i = 0; i < 4; i++)
        {
            if (i % 2 == 0) continue;
            oddSum += i;
        }
        return new
        {
            pure, good, goodCount, goodTotal,
            bad, badCount, badTotal,
            budgetBad, budgetCount, budgetTotal,
            sourceFirst = original[0], sourceLast = original[2],
            aliasFirst = aliased[0], counter,
            pulled, closed, caught, faultDisposed, committed,
            whileCount, doCount, oddSum
        };
    }

    static int Main(string[] args)
    {
        CultureInfo.CurrentCulture = CultureInfo.GetCultureInfo(args[1]);
        using var doc = JsonDocument.Parse(File.ReadAllBytes(args[0]));
        if (doc.RootElement.ValueKind != JsonValueKind.Array) return 2;
        Console.WriteLine(JsonSerializer.Serialize(new
        {
            probe = Probe(),
            rows = doc.RootElement.EnumerateArray().Select(Evaluate).ToArray()
        }));
        return 0;
    }
}
'''

class CsharpBoundedMethodsTests(unittest.TestCase):
    def test_native_bounded_iteration_and_method_side_effect_isolation(self):
        exe = shutil.which("dotnet")
        if not exe:
            if os.environ.get("GITHUB_ACTIONS") == "true":
                self.fail("PREINSTALLED_DOTNET_REQUIRED")
            self.skipTest("native .NET unavailable")
        exe = str(Path(exe).resolve())
        with tempfile.TemporaryDirectory(prefix="csharp-bounded-methods-") as tmp:
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
            app = root/"BoundedMethods"
            run("new","console","--framework","net10.0","--name","BoundedMethods",
                "--output",str(app),"--no-restore")
            program = app/"Program.cs"
            program.write_text(PROGRAM, encoding="utf-8")
            project = str(app/"BoundedMethods.csproj")
            run("restore",project,"--configfile",str(config),"--packages",str(root/"packages"),
                "--disable-build-servers","-p:NuGetAudit=false")
            assets = json.loads((app/"obj/project.assets.json").read_text())
            self.assertEqual(assets["libraries"], {})
            self.assertEqual(list((root/"packages").iterdir()), [])
            run("build",project,"--no-restore","--disable-build-servers","-p:UseAppHost=false")
            dll = app/"bin/Debug/net10.0/BoundedMethods.dll"
            self.assertTrue(dll.is_file())
            def sample(key, value):
                return {"kind": "sample", "id": key, "value": value}
            stop = {"kind": "stop"}
            rows = []
            expected = []

            def add(events, limit, status, inspected, valid, missing, score):
                rows.append(json.dumps({"events": events, "limit": limit},
                                       separators=(",", ":"), ensure_ascii=False))
                expected.append(dict(status=status, inspected=inspected,
                                     valid=valid, missing=missing, sum=score))

            def reject(raw, status, steps=0, valid=0, missing=0):
                rows.append(raw)
                expected.append(dict(status=status, inspected=steps,
                                     valid=valid, missing=missing, sum=None))

            add([], 1, "DONE", 0, 0, 0, 0)
            add([sample("00", 0)], 1, "DONE", 1, 1, 0, 0)
            add([sample("00", 5),sample("01", None)], 2, "DONE", 2, 1, 1, 5)
            add([sample("00", 1),stop,{"unread": True}], 2, "STOP", 2, 1, 0, 1)
            add([stop,{"unread": True}], 1, "STOP", 1, 0, 0, 0)
            add([sample("00", 2),sample("01", 3)], 2, "DONE", 2, 2, 0, 5)
            add([sample("00", 0),sample("01", 0),stop], 3, "STOP", 3, 2, 0, 0)
            add([sample("01", None),sample("02", None),stop], 3, "STOP", 3, 0, 2, 0)
            add([sample("00", 0),sample("01", None),sample("02", 3),sample("03", 2)],
                4, "DONE", 4, 3, 1, 5)
            add([sample("00", 1),sample("01", 2)], 1, "BUDGET", 1, 1, 0, None)
            add([sample("00", 1),stop], 1, "BUDGET", 1, 1, 0, None)
            add([sample("00", 0),sample("00", 1)], 3, "DUPLICATE", 2, 1, 0, None)
            add([sample("00", 0),sample("01", 6)], 2, "RANGE", 2, 1, 0, None)
            add([sample("00", 0),sample("01", True)], 2, "TYPE", 2, 1, 0, None)
            add([sample("00", 0),"wrong event"], 2, "EVENT", 2, 1, 0, None)
            add([sample("00", 0),{"kind":"bad"}], 2, "EVENT", 2, 1, 0, None)
            add([sample("00", 0),{"kind":"stop","extra":0}], 2, "EVENT", 2, 1, 0, None)
            add([sample("00", 0),sample("01", -1)], 2, "RANGE", 2, 1, 0, None)
            add([sample("00", 0),sample("01", 1.5)], 2, "TYPE", 2, 1, 0, None)
            add([sample("00", 0),sample("01", None),sample("02", 3),
                 sample("03", 2),sample("04", 1)], 4, "BUDGET", 4, 3, 1, None)

            reject("null", "SHAPE")
            reject('{"events":[]}', "SHAPE")
            reject('{"events":[],"limit":1,"limit":2}', "SHAPE")
            reject('{"events":{},"limit":1}', "SHAPE")
            reject('{"events":[],"limit":true}', "TYPE")
            reject('{"events":[],"limit":0}', "LIMIT")
            reject('{"events":[],"limit":9}', "LIMIT")
            reject('{"events":[{"kind":"sample","value":0}],"limit":1}',
                   "EVENT",1)
            reject('{"events":[{"kind":"sample","id":"x","value":0}],"limit":1}',
                   "EVENT",1)
            reject('{"events":[{"kind":"sample","id":1,"value":0}],"limit":1}',
                   "TYPE",1)
            reject('{"events":[{"kind":"sample","id":"00","value":0,"value":1}],"limit":1}',
                   "EVENT",1)
            reject('{"events":[{"kind":1}],"limit":1}', "EVENT",1)
            reject('{"events":[{"kind":"sample","id":"00","value":"0"}],"limit":1}',
                   "TYPE",1)

            # Independent Python oracle for a distinct small streaming domain:
            # three identities, four nullable values, three resource budgets.
            oracle_count = 0
            for values in product((None, 0, 2, 5), repeat=3):
                for limit in (1, 2, 3):
                    consumed = values[:limit]
                    valid = sum(v is not None for v in consumed)
                    missing = len(consumed)-valid
                    status = "BUDGET" if limit < len(values) else "DONE"
                    total = sum(v for v in consumed if v is not None) if status=="DONE" else None
                    add([sample(f"{i:02d}",v) for i,v in enumerate(values)],
                        limit, status, len(consumed), valid, missing, total)
                    oracle_count += 1

            payload = ("[" + ",".join(rows) + "]").encode("utf-8")
            sample_file = root/"stream.json"
            sample_file.write_bytes(payload)
            first = run(str(dll),str(sample_file),"en-US")
            second = run(str(dll),str(sample_file),"de-DE")
            self.assertEqual(first,second)
            output = json.loads(first)
            self.assertEqual(output["rows"],expected)
            self.assertEqual(sample_file.read_bytes(),payload)
            self.assertEqual(output["probe"],{
                "pure":2,"good":True,"goodCount":2,"goodTotal":2,
                "bad":False,"badCount":0,"badTotal":0,
                "budgetBad":False,"budgetCount":0,"budgetTotal":0,
                "sourceFirst":0,"sourceLast":2,"aliasFirst":5,"counter":3,
                "pulled":3,"closed":1,"caught":True,"faultDisposed":1,
                "committed":None,"whileCount":0,"doCount":1,"oddSum":4
            })

            # Genuine compiler rejects out/ref and loop-scope errors.
            compiler_errors = [
                ("for (int i=0;i<1;i++) {}\\nConsole.WriteLine(i);\\n", "CS0103"),
                ("void NeedsRef(ref int x) {}\\nint n = 1;\\nNeedsRef(n);\\n", "CS1620"),
                ("void MissingOut(out int x) {}\\nMissingOut(out int z);\\n", "CS0177")
            ]
            for index,(source,error) in enumerate(compiler_errors):
                program.write_text(source.replace("\\n","\n"), encoding="utf-8")
                failure_dir=root/f"bad-{index}"
                failure=run("build",project,"--no-restore","--disable-build-servers",
                            "-p:UseAppHost=false","--output",str(failure_dir),ok=False)
                self.assertIn(error,failure)
                self.assertFalse((failure_dir/"BoundedMethods.dll").exists())
            print(f"CSHARP-BOUNDED-METHODS-PASS sdk={sdk} "
                  f"fixed={len(expected)-oracle_count} oracle={oracle_count} "
                  "compiler-negative=3 early-stop duplicate-budget "
                  "nullable-pure-ref-out iterator-disposal exception-no-partial "
                  "culture-identical empty-feed",flush=True)
