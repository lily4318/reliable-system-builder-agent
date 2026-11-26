"""Native C# language lab: synthetic scoring, not a validated instrument.

Uses only the installed .NET SDK/framework and a separate Python oracle.
No external package source, real participant data, MVC host or deployment.
"""
from decimal import Decimal, ROUND_HALF_UP
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
using System.Globalization;
using System.Text.Json;

static class Lab
{
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

    static object Score(JsonElement row)
    {
        if (row.ValueKind != JsonValueKind.Array || row.GetArrayLength() != 4)
            return new { status = "SHAPE" };
        int?[] values = new int?[4];
        int index = 0;
        foreach (var item in row.EnumerateArray())
        {
            if (item.ValueKind == JsonValueKind.Null) { index++; continue; }
            if (item.ValueKind != JsonValueKind.String)
                return new { status = "TYPE" };
            string? text = item.GetString();
            // TryParse alone can accept syntax outside this synthetic dictionary.
            if (text is null || text.Length == 0 ||
                text.Any(ch => ch < '0' || ch > '9') ||
                (text.Length > 1 && text[0] == '0'))
                return new { status = "FORMAT" };
            if (!int.TryParse(text, NumberStyles.None, Inv, out int value))
                return new { status = "RANGE" };
            if (value < 0 || value > 5)
                return new { status = "RANGE" };
            values[index++] = value;
        }
        int valid = 0, sum = 0;
        for (int i = 0; i < values.Length; i++)
        {
            if (values[i] is not int value) continue;
            valid++;
            sum = checked(sum + ((i == 1 || i == 3) ? 5-value : value));
        }
        if (valid < 3)
            return new { status = "INSUFFICIENT", valid, missing = 4-valid,
                         sum = (int?)null, mean = (string?)null };
        decimal mean = Math.Round((decimal)sum / valid, 3, MidpointRounding.AwayFromZero);
        return new { status = "OK", valid, missing = 4-valid,
                     sum = (int?)sum, mean = mean.ToString("F3", Inv) };
    }

    static bool Overflow(Action action)
    {
        try { action(); return false; }
        catch (OverflowException) { return true; }
    }

    static bool DivideByZero(Action action)
    {
        try { action(); return false; }
        catch (DivideByZeroException) { return true; }
    }

    static int Main(string[] args)
    {
        CultureInfo.CurrentCulture = CultureInfo.GetCultureInfo(args[1]);
        int maximum = int.MaxValue, one = 1, zero = 0, five = 5, two = 2;
        int min = int.MinValue, minusOne = -1;
        int calls = 0;
        bool Probe() { calls++; return true; }
        bool shortAnd = false && Probe();
        bool shortOr = true || Probe();
        bool nonShort = false & Probe();
        bool nonShortOr = true | Probe();
        bool parsed = int.TryParse("not-a-number", NumberStyles.None, Inv, out int failedValue);
        var arithmetic = new {
            integerQuotient = five/two, negativeQuotient = -five/two,
            remainder = -five%two, decimalQuotient = (decimal)five/two,
            wrapped = unchecked(maximum+one),
            overflow = Overflow(() => { _ = checked(maximum+one); }),
            narrowed = Overflow(() => { _ = checked((byte)(maximum)); }),
            minDivide = Overflow(() => { _ = min/minusOne; }),
            divide = DivideByZero(() => { _ = five/zero; }),
            decimalExact = 0.1m+0.2m == 0.3m,
            doubleExact = 0.1+0.2 == 0.3,
            floatingInfinity = double.IsPositiveInfinity((double)one/zero),
            floatingNaN = double.IsNaN((double)zero/zero),
            shortAnd, shortOr, nonShort, nonShortOr, calls, parsed, failedValue
        };
        using var document = JsonDocument.Parse(File.ReadAllBytes(args[0]));
        var rows = new List<object>();
        foreach (var row in document.RootElement.EnumerateArray())
            rows.Add(Score(row));
        Console.WriteLine(JsonSerializer.Serialize(new { arithmetic, rows }));
        return 0;
    }
}
'''


class CsharpFundamentalScoringTests(unittest.TestCase):
    def test_native_language_and_synthetic_scoring(self):
        exe = shutil.which("dotnet")
        if not exe:
            if os.environ.get("GITHUB_ACTIONS") == "true":
                self.fail("PREINSTALLED_DOTNET_REQUIRED")
            self.skipTest("native .NET unavailable")
        exe = str(Path(exe).resolve())
        with tempfile.TemporaryDirectory(prefix="csharp-fundamentals-") as tmp:
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
            app = root/"LanguageLab"
            run("new","console","--framework","net10.0","--name","LanguageLab",
                "--output",str(app),"--no-restore")
            program = app/"Program.cs"
            program.write_text(PROGRAM, encoding="utf-8")
            project = str(app/"LanguageLab.csproj")
            run("restore",project,"--configfile",str(config),"--packages",str(root/"packages"),
                "--disable-build-servers","-p:NuGetAudit=false")
            assets = json.loads((app/"obj/project.assets.json").read_text())
            self.assertEqual(assets["libraries"], {})
            self.assertEqual(list((root/"packages").iterdir()), [])
            run("build",project,"--no-restore","--disable-build-servers","-p:UseAppHost=false")
            dll = app/"bin/Debug/net10.0/LanguageLab.dll"
            self.assertTrue(dll.is_file())
            # Exhaust every allowed four-item input, including zero and missing.
            valid_rows = list(product([None,"0","1","2","3","4","5"],repeat=4))
            def oracle(row):
                observed = [int(x) if i in (0,2) else 5-int(x)
                            for i,x in enumerate(row) if x is not None]
                count = len(observed)
                if count < 3:
                    return dict(status="INSUFFICIENT",valid=count,missing=4-count,sum=None,mean=None)
                total = sum(observed)
                avg = (Decimal(total)/Decimal(count)).quantize(Decimal("0.001"),rounding=ROUND_HALF_UP)
                return dict(status="OK",valid=count,missing=4-count,sum=total,mean=str(avg))
            negatives = [
                (None,"SHAPE"), ({},"SHAPE"), (["1"]*3,"SHAPE"), (["1"]*5,"SHAPE"),
                ([0,"1","1","1"],"TYPE"), ([True,"1","1","1"],"TYPE"),
                ([{},"1","1","1"],"TYPE"), ([[],"1","1","1"],"TYPE"),
                (["","1","1","1"],"FORMAT"), ([" 1","1","1","1"],"FORMAT"),
                (["1 ","1","1","1"],"FORMAT"), (["+1","1","1","1"],"FORMAT"),
                (["-1","1","1","1"],"FORMAT"), (["01","1","1","1"],"FORMAT"),
                (["1.0","1","1","1"],"FORMAT"), (["1,0","1","1","1"],"FORMAT"),
                (["1e0","1","1","1"],"FORMAT"), (["１","1","1","1"],"FORMAT"),
                (["1\0","1","1","1"],"FORMAT"), (["6","1","1","1"],"RANGE"),
                (["2147483648","1","1","1"],"RANGE"),
                (["9"*100,"1","1","1"],"RANGE"),
                (["1","1",None,"invalid"],"FORMAT"),
            ]
            expected = [oracle(row) for row in valid_rows]+[{"status":s} for _,s in negatives]
            input_file = root/"sample.json"
            payload = json.dumps(valid_rows+[row for row,_ in negatives],ensure_ascii=False).encode("utf-8")
            input_file.write_bytes(payload)
            first = run(str(dll),str(input_file),"en-US")
            second = run(str(dll),str(input_file),"de-DE")
            self.assertEqual(first,second)
            output = json.loads(first)
            self.assertEqual(output["rows"],expected)
            self.assertEqual(input_file.read_bytes(),payload)
            self.assertEqual(output["arithmetic"],{
                "integerQuotient":2,"negativeQuotient":-2,"remainder":-1,"decimalQuotient":2.5,
                "wrapped":-2147483648,"overflow":True,"narrowed":True,"minDivide":True,"divide":True,
                "decimalExact":True,"doubleExact":False,"floatingInfinity":True,"floatingNaN":True,
                "shortAnd":False,"shortOr":True,"nonShort":False,"nonShortOr":True,
                "calls":2,"parsed":False,"failedValue":0})
            # A real compiler must reject implicit narrowing and unassigned use.
            # Separate output directory avoids mistaking an earlier DLL for success.
            program.write_text("int n = 1000;\nbyte b = n;\nint unassigned;\nConsole.WriteLine(unassigned);\n")
            bad_output = root/"bad-build"
            failure = run("build",project,"--no-restore","--disable-build-servers",
                          "-p:UseAppHost=false","--output",str(bad_output),ok=False)
            self.assertIn("CS0266",failure)
            self.assertIn("CS0165",failure)
            self.assertFalse((bad_output/"LanguageLab.dll").exists())
            print(f"CSHARP-FUNDAMENTALS-PASS sdk={sdk} exhaustive={len(valid_rows)} "
                  f"negative={len(negatives)} culture-identical checked-overflow narrowing "
                  "division-short-circuit numeric-precision compiler-negative=2 empty-feed",flush=True)
