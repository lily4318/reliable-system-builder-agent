"""Native C# typed exchange: synthetic units, no real participant records."""
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
using System.Text.RegularExpressions;

struct Observation
{
    public int Count;
    public int[] Samples;
}
sealed class Buffer
{
    public int Count;
}
static class Lab
{
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;
    static bool Throws<T>(Action a) where T : Exception
    {
        try { a(); return false; }
        catch (T) { return true; }
    }
    static void Change(Buffer b) { b.Count = 9; b = new Buffer { Count = 99 }; }
    static int Increment(int n) { return ++n; }
    static object Probe()
    {
        var a = new Observation { Count = 2, Samples = new[] { 3 } };
        var b = a;
        b.Count = 8; b.Samples[0] = 7;
        var snapshot = new Observation { Count = a.Count, Samples = (int[])a.Samples.Clone() };
        a.Samples[0] = 11;
        var p = new Buffer { Count = 1 };
        var alias = p; Change(alias);
        int n = 5;
        object boxed = n; n = 6;
        int? missing = null, observed = 0;
        object? boxedMissing = missing, boxedObserved = observed;
        long big = 9007199254740993L, outside = (long)int.MaxValue + 1;
        double inf = double.PositiveInfinity, nan = double.NaN, tiny = 1e-100;
        double wide = double.MaxValue;
        decimal exact = 1.9m, half = 2.5m;
        int local = 1;
        { int delta = 3; local += delta; }
        return new {
            valueOriginal=a.Count, valueCopy=b.Count, shallow=b.Samples[0], deep=snapshot.Samples[0],
            referenceAlias=p.Count, sameReference=ReferenceEquals(p,alias),
            byValueReturn=Increment(n), byValueOriginal=n,
            boxedCopy=(int)boxed, wrongUnbox=Throws<InvalidCastException>(() => { _=(long)boxed; }),
            nullBox=boxedMissing is null, nullableBoxType=boxedObserved?.GetType().Name,
            nullableZero=(int?)boxedObserved, nullableDefault=default(int?), intDefault=default(int),
            nullValue=Throws<InvalidOperationException>(() => { _=missing.Value; }),
            nullUnbox=Throws<NullReferenceException>(() => { _=(int)boxedMissing!; }),
            lossyLong=(long)(double)big != big, exactLong=(long)(decimal)big == big,
            checkedNarrow=Throws<OverflowException>(() => { _=checked((int)outside); }),
            uncheckedNarrow=unchecked((int)outside),
            nanToDecimal=Throws<OverflowException>(() => { _=(decimal)nan; }),
            infToDecimal=Throws<OverflowException>(() => { _=(decimal)inf; }),
            wideToDecimal=Throws<OverflowException>(() => { _=(decimal)wide; }),
            tinyToDecimal=(decimal)tiny == 0m,
            decimalTruncate=(int)exact, convertRounded=Convert.ToInt32(exact),
            convertEven=Convert.ToInt32(half), local
        };
    }

    // Explicit synthetic wire contract: id stays a string, count is Int64
    // but exported as text, amount is canonical fixed-scale decimal (not double).
    static object Exchange(JsonElement row)
    {
        object Fail(string code) => new { status=code };
        if (row.ValueKind != JsonValueKind.Object) return Fail("SHAPE");
        var fields = row.EnumerateObject().ToArray();
        if (fields.Length != 4 || fields.Select(f=>f.Name).Distinct().Count()!=4 ||
            !row.TryGetProperty("source",out var src) || !row.TryGetProperty("id",out var id) ||
            !row.TryGetProperty("count",out var count) || !row.TryGetProperty("amount",out var amount))
            return Fail("SHAPE");
        if (src.ValueKind != JsonValueKind.String || id.ValueKind != JsonValueKind.String)
            return Fail("TYPE");
        string? source=src.GetString(), key=id.GetString();
        if (source is not ("text" or "number")) return Fail("SOURCE");
        if (key is null || !Regex.IsMatch(key, @"\A[0-9]{4}\z")) return Fail("ID");
        string? Wire(JsonElement item) =>
            source=="text" && item.ValueKind==JsonValueKind.String ? item.GetString() :
            source=="number" && item.ValueKind==JsonValueKind.Number ? item.GetRawText() : null;
        string? countText=Wire(count);
        if (countText is null) return Fail("TYPE");
        if (!Regex.IsMatch(countText, @"\A(0|[1-9][0-9]{0,18})\z")) return Fail("COUNT_FORMAT");
        if (!long.TryParse(countText,NumberStyles.None,Inv,out long value)) return Fail("COUNT_RANGE");
        decimal? measurement=null;
        if (amount.ValueKind!=JsonValueKind.Null)
        {
            string? t=Wire(amount);
            if (t is null) return Fail("TYPE");
            if (!Regex.IsMatch(t, @"\A(0|[1-9][0-9]{0,5})(\.[0-9]{1,3})?\z"))
                return Fail("AMOUNT_FORMAT");
            if (!decimal.TryParse(t,NumberStyles.AllowDecimalPoint,Inv,out decimal m))
                return Fail("AMOUNT_RANGE");
            measurement=m;
        }
        return new {status="OK", id=key, count=value.ToString(Inv),
                    amount=measurement?.ToString("F3",Inv)};
    }
    static int Main(string[] args)
    {
        CultureInfo.CurrentCulture=CultureInfo.GetCultureInfo(args[1]);
        using var doc=JsonDocument.Parse(File.ReadAllBytes(args[0]));
        Console.WriteLine(JsonSerializer.Serialize(new {
            probe=Probe(), rows=doc.RootElement.EnumerateArray().Select(Exchange).ToArray()
        }));
        return 0;
    }
}
'''

class CsharpTypedExchangeTests(unittest.TestCase):
    def test_native_type_boundaries_and_exchange(self):
        exe = shutil.which("dotnet")
        if not exe:
            if os.environ.get("GITHUB_ACTIONS") == "true":
                self.fail("PREINSTALLED_DOTNET_REQUIRED")
            self.skipTest("native .NET unavailable")
        exe = str(Path(exe).resolve())
        with tempfile.TemporaryDirectory(prefix="csharp-typed-exchange-") as tmp:
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
            app = root/"TypedExchange"
            run("new","console","--framework","net10.0","--name","TypedExchange",
                "--output",str(app),"--no-restore")
            program = app/"Program.cs"
            program.write_text(PROGRAM, encoding="utf-8")
            project = str(app/"TypedExchange.csproj")
            run("restore",project,"--configfile",str(config),"--packages",str(root/"packages"),
                "--disable-build-servers","-p:NuGetAudit=false")
            assets = json.loads((app/"obj/project.assets.json").read_text())
            self.assertEqual(assets["libraries"], {})
            self.assertEqual(list((root/"packages").iterdir()), [])
            run("build",project,"--no-restore","--disable-build-servers","-p:UseAppHost=false")
            dll = app/"bin/Debug/net10.0/TypedExchange.dll"
            self.assertTrue(dll.is_file())
            # Fixed independent expected rows; compare every field, not just totals.
            pairs = [
                ('{"source":"text","id":"0007","count":"9007199254740993","amount":"12.340"}',
                 dict(status="OK",id="0007",count="9007199254740993",amount="12.340")),
                ('{"source":"number","id":"0007","count":9007199254740993,"amount":12.34}',
                 dict(status="OK",id="0007",count="9007199254740993",amount="12.340")),
                ('{"source":"number","id":"0000","count":0,"amount":0}',
                 dict(status="OK",id="0000",count="0",amount="0.000")),
                ('{"source":"text","id":"0000","count":"0","amount":null}',
                 dict(status="OK",id="0000",count="0",amount=None)),
                ('{"source":"number","id":"9999","count":9223372036854775807,"amount":999999.999}',
                 dict(status="OK",id="9999",count="9223372036854775807",amount="999999.999")),
            ]
            def bad(row,code): pairs.append((row,dict(status=code)))
            bad('null',"SHAPE")
            bad('{"source":"text","id":"0007","count":"1"}',"SHAPE")
            bad('{"source":"text","id":"0007","count":"1","amount":null,"id":"0008"}',"SHAPE")
            bad('{"source":"other","id":"0007","count":"1","amount":null}',"SOURCE")
            bad('{"source":"number","id":7,"count":1,"amount":null}',"TYPE")
            bad('{"source":"number","id":"7","count":1,"amount":null}',"ID")
            bad('{"source":"number","id":"0007","count":true,"amount":null}',"TYPE")
            bad('{"source":"text","id":"0007","count":1,"amount":null}',"TYPE")
            bad('{"source":"number","id":"0007","count":1.0,"amount":null}',"COUNT_FORMAT")
            bad('{"source":"number","id":"0007","count":1e0,"amount":null}',"COUNT_FORMAT")
            bad('{"source":"text","id":"0007","count":"01","amount":null}',"COUNT_FORMAT")
            bad('{"source":"number","id":"0007","count":9223372036854775808,"amount":null}',"COUNT_RANGE")
            bad('{"source":"number","id":"0007","count":1,"amount":0.0001}',"AMOUNT_FORMAT")
            bad('{"source":"text","id":"0007","count":"1","amount":"1,25"}',"AMOUNT_FORMAT")
            bad('{"source":"number","id":"0007","count":1,"amount":1e2}',"AMOUNT_FORMAT")
            bad('{"source":"number","id":"0007","count":1,"amount":1000000}',"AMOUNT_FORMAT")
            bad('{"source":"text","id":"0007","count":"1","amount":""}',"AMOUNT_FORMAT")
            bad('{"source":"number","id":"0007","count":1,"amount":"0"}',"TYPE")
            payload=("["+",".join(row for row,_ in pairs)+"]").encode()
            input_file=root/"sample.json"
            input_file.write_bytes(payload)
            first=run(str(dll),str(input_file),"en-US")
            self.assertEqual(first,run(str(dll),str(input_file),"de-DE"))
            output=json.loads(first)
            self.assertEqual(output["rows"],[expected for _,expected in pairs])
            self.assertEqual(input_file.read_bytes(),payload)
            self.assertEqual(output["probe"],dict(
                valueOriginal=2,valueCopy=8,shallow=11,deep=7,referenceAlias=9,sameReference=True,
                byValueReturn=7,byValueOriginal=6,boxedCopy=5,wrongUnbox=True,
                nullBox=True,nullableBoxType="Int32",nullableZero=0,nullableDefault=None,intDefault=0,
                nullValue=True,nullUnbox=True,lossyLong=True,exactLong=True,checkedNarrow=True,
                uncheckedNarrow=-2147483648,nanToDecimal=True,infToDecimal=True,wideToDecimal=True,
                tinyToDecimal=True,decimalTruncate=1,convertRounded=2,convertEven=2,local=4))
            # Separate output targets and independent compiler diagnostics for scope.
            for index,(source,error) in enumerate([
                ("{ int scoped = 1; }\nConsole.WriteLine(scoped);\n","CS0103"),
                ("int outer = 1;\n{ int outer = 2; Console.WriteLine(outer); }\n","CS0136"),
            ]):
                program.write_text(source)
                bad_output=root/f"bad-{index}"
                failure=run("build",project,"--no-restore","--disable-build-servers",
                            "-p:UseAppHost=false","--output",str(bad_output),ok=False)
                self.assertIn(error,failure)
                self.assertFalse((bad_output/"TypedExchange.dll").exists())
            print(f"CSHARP-TYPED-EXCHANGE-PASS sdk={sdk} positive=5 negative=18 "
                  "copy-alias-snapshot nullable-boxing int64-exact decimal-boundaries "
                  "scope-compiler-negative=2 culture-identical empty-feed",flush=True)
