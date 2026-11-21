"""Native C# Array/List batch integrity: fixed-capacity vs dynamic collection.

Synthetic research observations only, not a verified clinical policy. Independent
Python row-by-row oracle checks composite identity, legitimate repeated values,
copy/alias behavior, rollback output, sorting, capacity and source byte integrity.
No third-party dependencies, external API or deployment.
"""
import itertools
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
using System.Collections.Generic;

sealed record Sample(string Study, string Person, int Visit, int Attempt, int? Value);
sealed class Cell
{
    public int Value;
    public Cell(int value) { Value = value; }
}

static class ArrayListBatch
{
    // Synthetic batch contract, not a real study dictionary.
    const int MaxRows = 6;
    const int MaxActions = 8;

    static bool Exactly(JsonElement e, params string[] required)
    {
        if (e.ValueKind != JsonValueKind.Object) return false;
        var seen = new HashSet<string>(StringComparer.Ordinal);
        foreach (var p in e.EnumerateObject())
        {
            if (!required.Contains(p.Name, StringComparer.Ordinal) || !seen.Add(p.Name))
                return false;
        }
        return seen.Count == required.Length;
    }

    static bool Identity(JsonElement e, out string study, out string person,
                         out int visit, out int attempt)
    {
        study = ""; person = ""; visit = 0; attempt = 0;
        if (!e.TryGetProperty("study", out var s) || s.ValueKind != JsonValueKind.String
            || !e.TryGetProperty("person", out var p) || p.ValueKind != JsonValueKind.String
            || !e.TryGetProperty("visit", out var v) || v.ValueKind != JsonValueKind.Number
            || !e.TryGetProperty("attempt", out var a) || a.ValueKind != JsonValueKind.Number
            || !v.TryGetInt32(out visit) || !a.TryGetInt32(out attempt))
            return false;
        study = s.GetString() ?? ""; person = p.GetString() ?? "";
        return (study == "A" || study == "B")
            && person.Length == 2 && person[0] == '0'
            && person[1] >= '1' && person[1] <= '4'
            && visit is >= 1 and <= 2 && attempt is >= 1 and <= 2;
    }

    static bool ReadRow(JsonElement e, out Sample row)
    {
        row = null!;
        if (!Exactly(e, "study", "person", "visit", "attempt", "value")
            || !Identity(e, out var study, out var person, out int visit, out int attempt)
            || !e.TryGetProperty("value", out var value))
            return false;
        int? score = null;
        if (value.ValueKind != JsonValueKind.Null)
        {
            if (value.ValueKind != JsonValueKind.Number
                || !value.TryGetInt32(out int n) || n < 0 || n > 5)
                return false;
            score = n;
        }
        row = new Sample(study, person, visit, attempt, score);
        return true;
    }

    static bool SameIdentity(Sample x, Sample y)
        => x.Study == y.Study && x.Person == y.Person
            && x.Visit == y.Visit && x.Attempt == y.Attempt;

    static int Compare(Sample x, Sample y)
    {
        int result = string.CompareOrdinal(x.Study, y.Study);
        if (result != 0) return result;
        result = string.CompareOrdinal(x.Person, y.Person);
        if (result != 0) return result;
        result = x.Visit.CompareTo(y.Visit);
        if (result != 0) return result;
        return x.Attempt.CompareTo(y.Attempt);
    }

    static object Reject(string reason) => new {
        status = reason, count = (int?)null, rows = (object?)null,
        arraySlots = (int?)null, listCapacity = (int?)null
    };

    static object Batch(JsonElement input)
    {
        if (!Exactly(input, "maxRows", "seed", "actions")) return Reject("SHAPE");
        var max = input.GetProperty("maxRows");
        var seed = input.GetProperty("seed");
        var actions = input.GetProperty("actions");
        if (max.ValueKind != JsonValueKind.Number || !max.TryGetInt32(out int maxRows))
            return Reject("TYPE");
        if (maxRows < 1 || maxRows > MaxRows) return Reject("LIMIT");
        if (seed.ValueKind != JsonValueKind.Array || actions.ValueKind != JsonValueKind.Array)
            return Reject("SHAPE");
        if (actions.GetArrayLength() > MaxActions) return Reject("LIMIT");
        if (seed.GetArrayLength() > maxRows) return Reject("CAPACITY");

        var baseline = new Sample[seed.GetArrayLength()];
        int originalCount = 0;
        foreach (var item in seed.EnumerateArray())
        {
            if (!ReadRow(item, out Sample row)) return Reject("ROW");
            if (baseline.Take(originalCount).Any(x => SameIdentity(x, row)))
                return Reject("DUPLICATE");
            baseline[originalCount++] = row;
        }

        // Array fixed physical storage vs List dynamic backing capacity.
        // All operations are performed on staged copies only.
        Sample?[] slots = new Sample?[maxRows];
        Array.Copy(baseline, slots, originalCount);
        int used = originalCount;
        var stage = new List<Sample>(baseline);

        void AssertEquivalent()
        {
            if (used != stage.Count || used > maxRows || stage.Capacity < used)
                throw new InvalidOperationException("MIRROR_COUNT");
            for (int i = 0; i < used; ++i)
            {
                if (slots[i] != stage[i]) throw new InvalidOperationException("MIRROR_ROW");
            }
            for (int i = used; i < slots.Length; ++i)
            {
                if (slots[i] != null) throw new InvalidOperationException("UNUSED_SLOT");
            }
        }
        AssertEquivalent();

        foreach (var action in actions.EnumerateArray())
        {
            if (action.ValueKind != JsonValueKind.Object
                || !action.TryGetProperty("op", out var op)
                || op.ValueKind != JsonValueKind.String)
                return Reject("ACTION");
            string? kind = op.GetString();
            if (kind == "add")
            {
                if (!Exactly(action,"op","row") ||
                    !ReadRow(action.GetProperty("row"), out Sample row))
                    return Reject("ROW");
                if (stage.Any(x => SameIdentity(x,row))) return Reject("DUPLICATE");
                if (used >= maxRows) return Reject("CAPACITY");
                slots[used++] = row;
                stage.Add(row);
            }
            else if (kind == "remove")
            {
                if (!Exactly(action,"op","study","person","visit","attempt")
                    || !Identity(action, out string study, out string person,
                                 out int visit, out int attempt))
                    return Reject("ROW");
                var needle = new Sample(study,person,visit,attempt,null);
                int i = -1;
                for (int k = 0; k < used; k++)
                    if (SameIdentity(slots[k]!,needle)) { i = k; break; }
                if (i < 0) return Reject("NOT_FOUND");
                int indexInList = stage.FindIndex(x => SameIdentity(x,needle));
                if (indexInList != i) throw new InvalidOperationException("MIRROR_INDEX");
                Array.Copy(slots,i+1,slots,i,used-i-1);
                slots[--used] = null;
                stage.RemoveAt(i);
            }
            else return Reject("ACTION");
            AssertEquivalent();
        }

        var arraySorted = new Sample[used];
        for (int i=0; i<used; i++) arraySorted[i] = slots[i]!;
        Array.Sort(arraySorted, Compare);
        stage.Sort(Compare);
        if (!arraySorted.SequenceEqual(stage))
            throw new InvalidOperationException("SORT_DIVERGED");
        var result = arraySorted.Select(x => new {
            study=x.Study, person=x.Person, visit=x.Visit,
            attempt=x.Attempt, value=x.Value
        }).ToArray();
        return new {
            status="OK", count=(int?)used, rows=(object?)result,
            arraySlots=(int?)maxRows, listCapacity=(int?)stage.Capacity
        };
    }

    static object Probe()
    {
        int[] original = { 2, 4 };
        int[] externalAlias = original;
        Array.Resize(ref original, 4); // creates new array rather than resizing external alias
        original[2] = 7;

        var reference = new Cell[] { new(1) };
        Cell[] arrayShallow = (Cell[])reference.Clone();
        Cell[] viaArrayCopy = new Cell[1];
        Array.Copy(reference,viaArrayCopy,1);
        var deep = reference.Select(x=>new Cell(x.Value)).ToArray();
        var listShallow = new List<Cell>(reference);
        reference[0].Value = 9;

        var list = new List<int>(1);
        int capacityBefore = list.Capacity;
        list.Add(7); list.Add(8);   // dynamic growth
        int capacityAfterGrow = list.Capacity;
        list.RemoveAt(0);          // physical capacity does not automatically shrink
        int capacityAfterRemove = list.Capacity;
        list.Insert(0,3);
        int afterInsertFirst = list[0];
        int afterInsertCount = list.Count;
        return new {
            oldArrayLength=externalAlias.Length,
            resizedArrayLength=original.Length,
            originalOldFirst=externalAlias[0],
            resizedNewValue=original[2],
            shallowArrayValue=arrayShallow[0].Value,
            arrayCopyValue=viaArrayCopy[0].Value,
            shallowListValue=listShallow[0].Value,
            deepValue=deep[0].Value,
            capacityBefore, capacityAfterGrow, capacityAfterRemove,
            countAfterRemove=1,
            afterInsertFirst, afterInsertCount
        };
    }

    static int Main(string[] args)
    {
        System.Globalization.CultureInfo.CurrentCulture =
            System.Globalization.CultureInfo.GetCultureInfo(args[1]);
        using var doc = JsonDocument.Parse(File.ReadAllBytes(args[0]));
        if (doc.RootElement.ValueKind != JsonValueKind.Array) return 2;
        Console.WriteLine(JsonSerializer.Serialize(new {
            probe=Probe(),
            rows=doc.RootElement.EnumerateArray().Select(Batch).ToArray()
        }));
        return 0;
    }
}
'''

class CsharpArrayListBatchTests(unittest.TestCase):
    def test_native_array_list_batch_integrity(self):
        exe = shutil.which("dotnet")
        if not exe:
            if os.environ.get("GITHUB_ACTIONS") == "true":
                self.fail("PREINSTALLED_DOTNET_REQUIRED")
            self.skipTest("native .NET unavailable")
        exe = str(Path(exe).resolve())
        with tempfile.TemporaryDirectory(prefix="csharp-array-list-batch-") as tmp:
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
            app = root/"ArrayListBatch"
            run("new","console","--framework","net10.0","--name","ArrayListBatch",
                "--output",str(app),"--no-restore")
            program = app/"Program.cs"
            program.write_text(PROGRAM, encoding="utf-8")
            project = str(app/"ArrayListBatch.csproj")
            run("restore",project,"--configfile",str(config),"--packages",str(root/"packages"),
                "--disable-build-servers","-p:NuGetAudit=false")
            assets = json.loads((app/"obj/project.assets.json").read_text())
            self.assertEqual(assets["libraries"], {})
            self.assertEqual(list((root/"packages").iterdir()), [])
            run("build",project,"--no-restore","--disable-build-servers","-p:UseAppHost=false")
            dll = app/"bin/Debug/net10.0/ArrayListBatch.dll"
            self.assertTrue(dll.is_file())
            def row(study,person,visit,attempt,value):
                return dict(study=study,person=person,visit=visit,
                            attempt=attempt,value=value)
            def add(item): return {"op":"add","row":item}
            def remove(item): return {"op":"remove",**{k:item[k] for k in
                                        ("study","person","visit","attempt")}}
            def key(item): return (item["study"],item["person"],
                                   item["visit"],item["attempt"])
            def expected_batch(max_rows, seed, actions):
                # Independent small Python model, not C# array/list implementation.
                state = {key(x):dict(x) for x in seed}
                assert len(state) == len(seed)
                for action in actions:
                    if action["op"] == "add":
                        item = action["row"]
                        if key(item) in state: return "DUPLICATE",None
                        if len(state) >= max_rows: return "CAPACITY",None
                        state[key(item)] = dict(item)
                    else:
                        identity=key(action)
                        if identity not in state: return "NOT_FOUND",None
                        del state[identity]
                return "OK",[state[k] for k in sorted(state)]
            cases = []
            def success(max_rows,seed,actions):
                status,values=expected_batch(max_rows,seed,actions)
                assert status=="OK"
                cases.append((json.dumps(dict(maxRows=max_rows,seed=seed,actions=actions),
                                         separators=(",",":")),status,values,max_rows))
            def auto_case(max_rows,seed,actions):
                status,values=expected_batch(max_rows,seed,actions)
                cases.append((json.dumps(dict(maxRows=max_rows,seed=seed,actions=actions),
                                         separators=(",",":")),status,values,max_rows))
            def rejection(raw,status):
                cases.append((raw,status,None,None))

            success(2,[],[])
            success(1,[row("A","01",1,1,0)],[])
            success(4,[row("B","02",2,1,None),row("A","01",1,2,0)],[])
            success(3,[row("A","01",1,1,1),row("A","01",1,2,1)],[])
            success(4,[row("B","03",1,1,5)], [add(row("A","01",2,1,0))])
            success(4,[row("A","01",1,1,0),row("B","02",2,2,None)],
                    [remove(row("A","01",1,1,0))])
            success(3,[row("A","01",1,1,0),row("A","01",1,2,0)],
                    [remove(row("A","01",1,1,0)),add(row("A","01",1,1,5))])
            success(1,[row("B","03",1,1,None)],[remove(row("B","03",1,1,None))])

            auto_case(1,[row("A","01",1,1,0)], [add(row("B","01",1,1,5))])
            auto_case(3,[row("A","01",1,1,0)], [add(row("A","01",1,1,5))])
            auto_case(3,[row("A","01",1,1,None)],
                      [remove(row("B","01",1,1,0))])
            auto_case(1,[],[add(row("B","04",2,2,5)),add(row("A","01",1,1,0))])
            auto_case(2,[row("A","01",1,1,0)],
                      [add(row("B","02",1,1,5)),remove(row("A","01",1,1,0))])
            rejection("null","SHAPE")
            rejection('{"maxRows":1,"seed":[]}',"SHAPE")
            rejection('{"maxRows":1,"seed":[],"actions":[],"maxRows":2}',"SHAPE")
            rejection('{"maxRows":true,"seed":[],"actions":[]}',"TYPE")
            rejection('{"maxRows":0,"seed":[],"actions":[]}',"LIMIT")
            rejection('{"maxRows":7,"seed":[],"actions":[]}',"LIMIT")
            rejection('{"maxRows":1,"seed":{},"actions":[]}',"SHAPE")
            rejection('{"maxRows":1,"seed":[],"actions":null}',"SHAPE")
            rejection('{"maxRows":1,"seed":[{"study":"A","person":"01","visit":1,"attempt":1,"value":0},{"study":"A","person":"02","visit":1,"attempt":1,"value":0}],"actions":[]}',"CAPACITY")
            rejection('{"maxRows":2,"seed":[{"study":"A","person":"01","visit":1,"attempt":1,"value":0},{"study":"A","person":"01","visit":1,"attempt":1,"value":5}],"actions":[]}',"DUPLICATE")
            rejection('{"maxRows":1,"seed":[{"study":"A","person":"01","visit":1,"attempt":1,"value":1.5}],"actions":[]}',"ROW")
            rejection('{"maxRows":1,"seed":[{"study":"A","person":"01","visit":1,"attempt":1,"value":true}],"actions":[]}',"ROW")
            rejection('{"maxRows":1,"seed":[{"study":"A","person":"01","visit":1,"attempt":1,"value":0,"value":5}],"actions":[]}',"ROW")
            rejection('{"maxRows":1,"seed":[{"study":"A","person":"01","visit":1,"attempt":1,"value":6}],"actions":[]}',"ROW")
            rejection('{"maxRows":1,"seed":[],"actions":[{"op":"noop"}]}',"ACTION")
            rejection('{"maxRows":1,"seed":[],"actions":[{"op":"add","row":{"study":"A","person":"04","visit":1,"attempt":1,"value":"0"}}]}',"ROW")
            rejection('{"maxRows":1,"seed":[],"actions":[{"op":"remove","study":"A","person":"01","visit":1,"attempt":1}]}',"NOT_FOUND")
            rejection('{"maxRows":1,"seed":[],"actions":[{"op":"remove","study":"A","person":"01","visit":1,"attempt":1,"attempt":2}]}',"ROW")
            rejection('{"maxRows":1,"seed":[],"actions":[{"op":"add","row":{"study":"A","person":"01","visit":1,"attempt":1,"value":0},"row":{"study":"A","person":"02","visit":1,"attempt":1,"value":0}}]}',"ROW")
            rejection('{"maxRows":1,"seed":[],"actions":[{"op":"remove","study":"Z","person":"01","visit":1,"attempt":1}]}',"ROW")
            rejection('{"maxRows":1,"seed":[],"actions":[0]}',"ACTION")
            rejection('{"maxRows":1,"seed":[],"actions":[{"op":1}]}',"ACTION")
            rejection('{"maxRows":1,"seed":[],"actions":[{"op":"add"}]}',"ROW")
            rejection('{"maxRows":1,"seed":[],"actions":[{"op":"add","row":null}]}',"ROW")
            rejection('{"maxRows":1,"seed":[],"actions":[{"op":"add","row":{"study":"A","person":"01","visit":1,"attempt":1,"value":0},"extra":0}]}',"ROW")
            rejection('{"maxRows":1,"seed":[],"actions":[{"op":"remove","study":"A","person":"01","visit":1,"attempt":1,"extra":0}]}',"ROW")
            rejection('{"maxRows":1,"seed":[],"actions":['+
                      ','.join('{"op":"noop"}' for _ in range(9))+']}',"LIMIT")

            oracle_cases=0
            for score1,score2,score3 in itertools.product((None,0,5),repeat=3):
                first = row("A","01",1,1,score1)
                second = row("B","02",1,1,score2)
                third = row("A","01",1,2,score3)
                scenarios = [
                    (3,[first,second],[add(third)]),
                    (3,[first,second],[remove(first)]),
                    (3,[first,second],[remove(first),add(third)]),
                    (3,[first,second],[add(row("A","01",1,1,score3))]),
                    (2,[first,second],[add(third)]),
                    (3,[first,second],[remove(third)]),
                    (3,[first,second],[remove(second),add(third)]),
                    (3,[first,second],[add(third),remove(first)])
                ]
                for max_rows,seed,actions in scenarios:
                    auto_case(max_rows,seed,actions)
                    oracle_cases+=1
            payload=("["+",".join(raw for raw,*_ in cases)+"]").encode("utf-8")
            input_file=root/"synthetic-batches.json"
            input_file.write_bytes(payload)
            first = run(str(dll),str(input_file),"en-US")
            second = run(str(dll),str(input_file),"de-DE")
            self.assertEqual(first,second)
            observed=json.loads(first)
            self.assertEqual(len(observed["rows"]),len(cases))
            for idx,((raw,status,rows,max_rows),actual) in enumerate(zip(cases,observed["rows"])):
                self.assertEqual(actual["status"],status,(idx,raw,actual))
                if status=="OK":
                    self.assertEqual(actual["rows"],rows,(idx,raw,actual))
                    self.assertEqual(actual["count"],len(rows))
                    self.assertEqual(actual["arraySlots"],max_rows)
                    self.assertIsInstance(actual["listCapacity"],int)
                    self.assertGreaterEqual(actual["listCapacity"],len(rows))
                else:
                    self.assertEqual(actual,{"status":status,"count":None,"rows":None,
                                             "arraySlots":None,"listCapacity":None},(idx,raw))
            self.assertEqual(input_file.read_bytes(),payload)
            probe=observed["probe"]
            self.assertEqual({k:probe[k] for k in (
                "oldArrayLength","resizedArrayLength","originalOldFirst",
                "resizedNewValue","shallowArrayValue","arrayCopyValue",
                "shallowListValue","deepValue","capacityBefore",
                "countAfterRemove","afterInsertFirst","afterInsertCount")},
                {"oldArrayLength":2,"resizedArrayLength":4,"originalOldFirst":2,
                 "resizedNewValue":7,"shallowArrayValue":9,"arrayCopyValue":9,
                 "shallowListValue":9,"deepValue":1,"capacityBefore":1,
                 "countAfterRemove":1,"afterInsertFirst":3,"afterInsertCount":2})
            self.assertGreaterEqual(probe["capacityAfterGrow"],2)
            self.assertEqual(probe["capacityAfterRemove"],probe["capacityAfterGrow"])
            print(f"CSHARP-ARRAY-LIST-BATCH-PASS sdk={sdk} fixed={len(cases)-oracle_cases} "
                  f"oracle={oracle_cases} duplicate-capacity-atomic-reject "
                  "array-copy-resize-alias list-add-remove-sort "
                  "composite-key-legitimate-repeat culture-identical empty-feed",flush=True)
