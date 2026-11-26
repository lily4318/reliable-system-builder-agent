"""Native OOP / property snapshots: synthetic mutable research draft boundaries.

Tests constructor/property invariants, defensive deep snapshots, alias/reference
safety, staged revisioned mutations, and independent row-by-row Python oracle.
Fully synthetic; no real research policy, database, third-party packages or deploy.
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

sealed class MutableMeta
{
    public int[] Tags { get; set; }
    public MutableMeta(int[] tags) => Tags = tags;
}

sealed class MutableReading
{
    public string Stage { get; set; }
    public int? Value { get; set; }
    public MutableMeta Meta { get; set; }
    public MutableReading(string stage,int? value,MutableMeta meta)
    { Stage=stage; Value=value; Meta=meta; }
}

// A deliberately encapsulated value object: no exposed mutable fields or
// direct reference to caller-owned nested objects, even on read.
sealed class SafeReading
{
    private readonly int[] _tags;
    public string Stage { get; }
    public int? Value { get; }
    public int[] Tags => (int[])_tags.Clone();
    public int TagSum => _tags.Sum();
    public SafeReading(MutableReading source)
    {
        if (source == null || (source.Stage != "pre" && source.Stage != "post" &&
             source.Stage != "follow") || (source.Value.HasValue &&
             (source.Value.Value < 0 || source.Value.Value > 5)) ||
             source.Meta == null || source.Meta.Tags == null ||
             source.Meta.Tags.Length < 1 || source.Meta.Tags.Length > 3 ||
             source.Meta.Tags.Any(n => n < 0 || n > 9))
            throw new ArgumentException("INVALID_READING");
        Stage=source.Stage;
        Value=source.Value;
        _tags=(int[])source.Meta.Tags.Clone();
    }
    public SafeReading Copy() => new SafeReading(Export());
    public MutableReading Export()
        => new MutableReading(Stage,Value,new MutableMeta((int[])_tags.Clone()));
}

sealed class SafeSession
{
    private List<SafeReading> _rows;
    public string Id { get; }
    public int Revision { get; private set; }
    public bool IsSealed { get; private set; }
    public MutableReading[] Readings => _rows.Select(r => r.Export()).ToArray();

    public SafeSession(string id,IEnumerable<MutableReading> seed)
    {
        if (id != "S1" && id != "S2") throw new ArgumentException("ID");
        Id=id; _rows=new List<SafeReading>();
        foreach (var raw in seed)
        {
            if (_rows.Count>=3) throw new ArgumentException("MAX");
            var entry=new SafeReading(raw);
            if (_rows.Any(x=>x.Stage==entry.Stage))
                throw new ArgumentException("DUPLICATE");
            _rows.Add(entry);
        }
    }

    public bool Apply(JsonElement actions,int expectedRevision,out string status)
    {
        if (expectedRevision!=Revision) { status="REVISION"; return false; }
        if (IsSealed) { status="SEALED"; return false; }
        if (actions.ValueKind!=JsonValueKind.Array) { status="SHAPE"; return false; }
        int count=actions.GetArrayLength();
        if (count==0) { status="EMPTY"; return false; }
        if (count>5) { status="LIMIT"; return false; }

        // No public mutation until every operation succeeds.
        var staged=_rows.Select(x=>x.Copy()).ToList();
        bool close=false;
        for (int i=0; i<count; i++)
        {
            JsonElement action=actions[i];
            if (!Program.Exact(action,"op")
                && !Program.Exact(action,"op","row")
                && !Program.Exact(action,"op","stage"))
                { status="ACTION"; return false; }
            if (!action.TryGetProperty("op",out var o) ||
                 o.ValueKind!=JsonValueKind.String)
                { status="ACTION"; return false; }
            string op=o.GetString()??"";
            if (op=="add" || op=="replace")
            {
                if (!Program.Exact(action,"op","row") ||
                    !Program.Read(action.GetProperty("row"),out MutableReading raw))
                    { status="ROW"; return false; }
                var entry=new SafeReading(raw);
                int index=staged.FindIndex(x=>x.Stage==entry.Stage);
                if (op=="add")
                {
                    if (index>=0) { status="DUPLICATE"; return false; }
                    if (staged.Count>=3) { status="LIMIT"; return false; }
                    staged.Add(entry);
                }
                else
                {
                    if (index<0) { status="MISSING"; return false; }
                    staged[index]=entry;
                }
            }
            else if (op=="remove")
            {
                if (!Program.Exact(action,"op","stage") ||
                    !Program.Stage(action.GetProperty("stage"),out string stage))
                    { status="ROW"; return false; }
                int index=staged.FindIndex(x=>x.Stage==stage);
                if (index<0) { status="MISSING"; return false; }
                staged.RemoveAt(index);
            }
            else if (op=="seal")
            {
                if (!Program.Exact(action,"op"))
                    { status="ACTION"; return false; }
                if (i!=count-1) { status="ORDER"; return false; }
                if (staged.Count==0) { status="EMPTY"; return false; }
                close=true;
            }
            else { status="ACTION"; return false; }
        }
        _rows=staged;
        Revision++;
        IsSealed=close;
        status="OK";
        return true;
    }
}

record RowOutput(string stage,int? value,int[] tags,int tagSum);
record CaseOutput(string status,int? revision,bool? @sealed,
                  RowOutput[]? before,RowOutput[]? after);

static class Program
{
    public static bool Exact(JsonElement e,params string[] fields)
    {
        if (e.ValueKind!=JsonValueKind.Object) return false;
        var names=new HashSet<string>(StringComparer.Ordinal);
        foreach (var p in e.EnumerateObject())
            if (!fields.Contains(p.Name,StringComparer.Ordinal) ||
                !names.Add(p.Name)) return false;
        return names.Count==fields.Length;
    }
    public static bool Stage(JsonElement e,out string stage)
    {
        stage="";
        if (e.ValueKind!=JsonValueKind.String) return false;
        stage=e.GetString()??"";
        return stage=="pre" || stage=="post" || stage=="follow";
    }
    public static bool Read(JsonElement e,out MutableReading row)
    {
        row=null!;
        if (!Exact(e,"stage","value","meta") ||
            !Stage(e.GetProperty("stage"),out string stage)) return false;
        JsonElement value=e.GetProperty("value");
        int? score=null;
        if (value.ValueKind!=JsonValueKind.Null)
        {
            if (value.ValueKind!=JsonValueKind.Number ||
                !value.TryGetInt32(out int number) || number<0 || number>5)
                return false;
            score=number;
        }
        JsonElement meta=e.GetProperty("meta");
        if (!Exact(meta,"tags")) return false;
        JsonElement tags=meta.GetProperty("tags");
        if (tags.ValueKind!=JsonValueKind.Array ||
            tags.GetArrayLength()<1 || tags.GetArrayLength()>3)
            return false;
        var values=new List<int>();
        foreach (var t in tags.EnumerateArray())
        {
            if (t.ValueKind!=JsonValueKind.Number ||
                !t.TryGetInt32(out int n) || n<0 || n>9) return false;
            values.Add(n);
        }
        row=new MutableReading(stage,score,new MutableMeta(values.ToArray()));
        return true;
    }
    static RowOutput[] Output(SafeSession s)
        => s.Readings.Select(x=>new RowOutput(x.Stage,x.Value,
                   (int[])x.Meta.Tags.Clone(),x.Meta.Tags.Sum()))
             .OrderBy(x=>x.stage=="pre"?0:x.stage=="post"?1:2).ToArray();
    static CaseOutput Error(string status) => new(status,null,null,null,null);
    static CaseOutput Evaluate(JsonElement request)
    {
        if (!Exact(request,"id","seed","expectedRevision","actions"))
            return Error("SHAPE");
        JsonElement id=request.GetProperty("id");
        JsonElement seed=request.GetProperty("seed");
        JsonElement revision=request.GetProperty("expectedRevision");
        JsonElement actions=request.GetProperty("actions");
        if (id.ValueKind!=JsonValueKind.String ||
            revision.ValueKind!=JsonValueKind.Number ||
            !revision.TryGetInt32(out int expected))
            return Error("TYPE");
        if (seed.ValueKind!=JsonValueKind.Array) return Error("SHAPE");
        var parsed=new List<MutableReading>();
        if (seed.GetArrayLength()>3) return Error("INIT");
        foreach (var item in seed.EnumerateArray())
        {
            if (!Read(item,out MutableReading reading)) return Error("INIT");
            parsed.Add(reading);
        }
        SafeSession session;
        try { session=new SafeSession(id.GetString()??"",parsed); }
        catch (ArgumentException) { return Error("INIT"); }
        RowOutput[] before=Output(session);
        session.Apply(actions,expected,out string status);
        return new CaseOutput(status,session.Revision,session.IsSealed,
                              before,Output(session));
    }

    static object Probe()
    {
        int[] sourceTags={1,2};
        var source=new MutableReading("pre",0,new MutableMeta(sourceTags));
        var session=new SafeSession("S1",new[]{source});
        bool sourceTagsAliased=ReferenceEquals(sourceTags,session.Readings[0].Meta.Tags);
        sourceTags[0]=9; source.Meta.Tags=new[]{8}; source.Value=5;
        source.Stage="post";
        MutableReading[] first=session.Readings;
        first[0].Meta.Tags[1]=8;
        first[0].Stage="follow"; first[0].Value=null;
        var safe=session.Readings[0];
        using var fail=JsonDocument.Parse(
            "[{\"op\":\"add\",\"row\":{\"stage\":\"post\",\"value\":0,\"meta\":{\"tags\":[3]}}},"+
            "{\"op\":\"add\",\"row\":{\"stage\":\"post\",\"value\":5,\"meta\":{\"tags\":[1]}}}]");
        bool rejected=session.Apply(fail.RootElement,0,out string failCode);
        var afterReject=session.Readings[0];
        using var done=JsonDocument.Parse(
            "[{\"op\":\"replace\",\"row\":{\"stage\":\"pre\",\"value\":null,\"meta\":{\"tags\":[4,5]}}},"+
            "{\"op\":\"seal\"}]");
        bool accepted=session.Apply(done.RootElement,0,out string doneCode);
        var afterDone=session.Readings[0];
        using var later=JsonDocument.Parse("[{\"op\":\"remove\",\"stage\":\"pre\"}]");
        bool afterSeal=session.Apply(later.RootElement,1,out string sealedCode);
        bool wrongRev=session.Apply(later.RootElement,0,out string revisionCode);
        return new {
            sourceTagsAliased,
            safeStage=safe.Stage,safeValue=safe.Value,safeTags=safe.Meta.Tags,
            rejected,failCode,rejectRevision=session.Revision,
            afterRejectStage=afterReject.Stage,afterRejectTags=afterReject.Meta.Tags,
            accepted,doneCode,afterDoneStage=afterDone.Stage,
            afterDoneValue=afterDone.Value,afterDoneTags=afterDone.Meta.Tags,
            afterSeal,sealedCode,wrongRev,revisionCode,
            finalRevision=session.Revision,finalSealed=session.IsSealed
        };
    }

    static int Main(string[] args)
    {
        System.Globalization.CultureInfo.CurrentCulture =
            System.Globalization.CultureInfo.GetCultureInfo(args[1]);
        using var doc=JsonDocument.Parse(File.ReadAllBytes(args[0]));
        if (doc.RootElement.ValueKind!=JsonValueKind.Array) return 2;
        Console.WriteLine(JsonSerializer.Serialize(new {
            probe=Probe(),
            cases=doc.RootElement.EnumerateArray().Select(Evaluate).ToArray()
        }));
        return 0;
    }
}
'''

class CsharpOopPropertySnapshotTests(unittest.TestCase):
    def test_native_oop_encapsulation_deep_copy_and_invariants(self):
        exe = shutil.which("dotnet")
        if not exe:
            if os.environ.get("GITHUB_ACTIONS") == "true":
                self.fail("PREINSTALLED_DOTNET_REQUIRED")
            self.skipTest("native .NET unavailable")
        exe = str(Path(exe).resolve())
        with tempfile.TemporaryDirectory(prefix="csharp-oop-snapshots-") as tmp:
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
            app = root/"OopSnapshots"
            run("new","console","--framework","net10.0","--name","OopSnapshots",
                "--output",str(app),"--no-restore")
            program = app/"Program.cs"
            program.write_text(PROGRAM, encoding="utf-8")
            project = str(app/"OopSnapshots.csproj")
            run("restore",project,"--configfile",str(config),"--packages",str(root/"packages"),
                "--disable-build-servers","-p:NuGetAudit=false")
            assets = json.loads((app/"obj/project.assets.json").read_text())
            self.assertEqual(assets["libraries"], {})
            self.assertEqual(list((root/"packages").iterdir()), [])
            run("build",project,"--no-restore","--disable-build-servers","-p:UseAppHost=false")
            dll = app/"bin/Debug/net10.0/OopSnapshots.dll"
            self.assertTrue(dll.is_file())

            stages=("pre","post","follow")
            def reading(stage,value,tags):
                return {"stage":stage,"value":value,"meta":{"tags":tags}}
            def add(item): return {"op":"add","row":item}
            def replace(item): return {"op":"replace","row":item}
            def remove(stage): return {"op":"remove","stage":stage}
            def seal(): return {"op":"seal"}
            def view(items):
                return [{"stage":x["stage"],"value":x["value"],
                         "tags":x["meta"]["tags"][:],
                         "tagSum":sum(x["meta"]["tags"])}
                         for x in sorted(items,key=lambda x:stages.index(x["stage"]))]
            def independent_oracle(seed,actions,revision):
                before=view(seed)
                if revision!=0:
                    return {"status":"REVISION","revision":0,"sealed":False,
                            "before":before,"after":before}
                if not actions:
                    return {"status":"EMPTY","revision":0,"sealed":False,
                            "before":before,"after":before}
                if len(actions)>5:
                    return {"status":"LIMIT","revision":0,"sealed":False,
                            "before":before,"after":before}
                state={x["stage"]:json.loads(json.dumps(x)) for x in seed}
                status="OK"
                closed=False
                for i,cmd in enumerate(actions):
                    op=cmd["op"]
                    if op=="add":
                        entry=cmd["row"]
                        if entry["stage"] in state: status="DUPLICATE"; break
                        if len(state)>=3: status="LIMIT"; break
                        state[entry["stage"]]=json.loads(json.dumps(entry))
                    elif op=="replace":
                        entry=cmd["row"]
                        if entry["stage"] not in state: status="MISSING"; break
                        state[entry["stage"]]=json.loads(json.dumps(entry))
                    elif op=="remove":
                        if cmd["stage"] not in state: status="MISSING"; break
                        del state[cmd["stage"]]
                    elif op=="seal":
                        if i!=len(actions)-1: status="ORDER";break
                        if not state: status="EMPTY";break
                        closed=True
                    else:
                        raise AssertionError("unknown generator")
                if status=="OK":
                    return {"status":"OK","revision":1,"sealed":closed,
                            "before":before,"after":view(state.values())}
                return {"status":status,"revision":0,"sealed":False,
                        "before":before,"after":before}

            cases=[]
            def make(seed,actions,revision=0,id="S1"):
                data={"id":id,"seed":seed,"expectedRevision":revision,"actions":actions}
                cases.append((json.dumps(data,separators=(",",":")),
                              independent_oracle(seed,actions,revision)))
            def invalid(raw,status,initial=None):
                expected={"status":status,"revision":None,"sealed":None,
                          "before":None,"after":None}
                if initial is not None:
                    expected={"status":status,"revision":0,"sealed":False,
                              "before":view(initial),"after":view(initial)}
                cases.append((raw,expected))

            a=reading("pre",0,[1,2])
            b=reading("post",None,[3])
            c=reading("follow",5,[4,5,6])
            make([], [add(a)])
            make([a],[replace(reading("pre",None,[0]))])
            make([a,b],[replace(reading("post",0,[9])),seal()])
            make([a,b,c],[remove("post"),replace(reading("pre",5,[1]))])
            make([a],[seal()])
            make([a],[add(b),remove("pre"),add(c)])
            make([a],[add(a)])
            make([a,b,c],[add(reading("pre",5,[0]))])
            make([a],[replace(b)])
            make([a],[remove("post")])
            make([],[seal()])
            make([a],[seal(),remove("pre")])
            make([a],[add(b)],revision=1)
            make([a],[])
            make([a],[add(b),add(c),remove("pre"),replace(reading("post",5,[1])),seal()])
            make([a],[add(b),add(c),remove("pre"),add(a)])
            make([a,b],[remove("pre"),remove("post"),seal()])
            invalid("null","SHAPE")
            invalid('{"id":"S1","seed":[],"expectedRevision":0}',"SHAPE")
            invalid('{"id":"S1","seed":[],"expectedRevision":0,"actions":[],"id":"S2"}',"SHAPE")
            invalid('{"id":"S1","seed":[],"expectedRevision":true,"actions":[]}',"TYPE")
            invalid('{"id":"S1","seed":{},"expectedRevision":0,"actions":[]}',"SHAPE")
            invalid('{"id":"S3","seed":[],"expectedRevision":0,"actions":[]}',"INIT")
            invalid('{"id":"S1","seed":[{"stage":"pre","value":5,"meta":{"tags":[]}}],"expectedRevision":0,"actions":[]}',"INIT")
            invalid('{"id":"S1","seed":[{"stage":"pre","value":true,"meta":{"tags":[1]}}],"expectedRevision":0,"actions":[]}',"INIT")
            invalid('{"id":"S1","seed":[{"stage":"pre","value":0,"meta":{"tags":[1]}},{"stage":"pre","value":5,"meta":{"tags":[2]}}],"expectedRevision":0,"actions":[]}',"INIT")
            invalid('{"id":"S1","seed":[{"stage":"pre","value":0,"meta":{"tags":[1,10]}}],"expectedRevision":0,"actions":[]}',"INIT")
            invalid('{"id":"S1","seed":[{"stage":"pre","value":0,"meta":{"tags":[1],"tags":[2]}}],"expectedRevision":0,"actions":[]}',"INIT")
            invalid('{"id":"S1","seed":[{"stage":"pre","value":0,"value":1,"meta":{"tags":[1]}}],"expectedRevision":0,"actions":[]}',"INIT")
            invalid('{"id":"S1","seed":[],"expectedRevision":0,"actions":{}}',"SHAPE",[])
            invalid('{"id":"S1","seed":[],"expectedRevision":0,"actions":[{"op":"bogus"}]}',"ACTION",[])
            invalid('{"id":"S1","seed":[],"expectedRevision":0,"actions":[{"op":"add"}]}',"ROW",[])
            invalid('{"id":"S1","seed":[],"expectedRevision":0,"actions":[{"op":"add","row":null}]}',"ROW",[])
            invalid('{"id":"S1","seed":[],"expectedRevision":0,"actions":[{"op":"add","row":{"stage":"pre","value":6,"meta":{"tags":[1]}}}]}',"ROW",[])
            invalid('{"id":"S1","seed":[],"expectedRevision":0,"actions":[{"op":"remove","stage":false}]}',"ROW",[])
            invalid('{"id":"S1","seed":[],"expectedRevision":0,"actions":[{"op":1}]}',"ACTION",[])
            invalid('{"id":"S1","seed":[],"expectedRevision":0,"actions":[{"op":"seal","unexpected":0}]}',"ACTION",[])
            invalid('{"id":"S1","seed":[],"expectedRevision":0,"actions":[{"op":"add","row":{"stage":"pre","value":0,"meta":{"tags":[1]}},"row":{"stage":"post","value":1,"meta":{"tags":[2]}}}]}',"ACTION",[])
            invalid('{"id":"S1","seed":[],"expectedRevision":0,"actions":['+
                    ','.join('{"op":"seal"}' for _ in range(6))+']}',"LIMIT",[])

            oracle_count=0
            for first,second,third in itertools.product((None,0,2,5),repeat=3):
                aa=reading("pre",first,[1,0])
                bb=reading("post",second,[2])
                cc=reading("follow",third,[3,4])
                options=[
                    ([],[add(aa),add(bb),seal()],0),
                    ([aa],[replace(reading("pre",second,[5]))],0),
                    ([aa,bb],[replace(cc)],0),
                    ([aa,bb],[remove("pre"),add(cc)],0),
                    ([aa,bb,cc],[remove("post"),add(bb)],0),
                    ([aa],[add(bb),add(cc),seal(),remove("pre")],0),
                    ([aa],[remove("pre"),seal()],0),
                    ([aa],[add(bb)],2),
                ]
                for seed,actions,revision in options:
                    make(seed,actions,revision)
                    oracle_count+=1
            payload=("["+",".join(raw for raw,_ in cases)+"]").encode("utf-8")
            batch=root/"synthetic-sessions.json"
            batch.write_bytes(payload)
            first=run(str(dll),str(batch),"en-US")
            second=run(str(dll),str(batch),"de-DE")
            self.assertEqual(first,second)
            actual=json.loads(first)
            self.assertEqual(actual["cases"],[expected for _,expected in cases])
            self.assertEqual(batch.read_bytes(),payload)
            self.assertEqual(actual["probe"],{
                "sourceTagsAliased":False,
                "safeStage":"pre","safeValue":0,"safeTags":[1,2],
                "rejected":False,"failCode":"DUPLICATE","rejectRevision":1,
                "afterRejectStage":"pre","afterRejectTags":[1,2],
                "accepted":True,"doneCode":"OK","afterDoneStage":"pre",
                "afterDoneValue":None,"afterDoneTags":[4,5],
                "afterSeal":False,"sealedCode":"SEALED",
                "wrongRev":False,"revisionCode":"REVISION",
                "finalRevision":1,"finalSealed":True
            })
            # Actual compiler, not textual prediction: property setter/field access.
            compiler_negative=[
                ('class Bound { public int Revision { get; private set; } } '+
                 'class Program { static void Main() { new Bound().Revision=3; } }',
                 'CS0272'),
                ('class Bound { public string Id { get; } = "S1"; } '+
                 'class Program { static void Main() { new Bound().Id="S2"; } }',
                 'CS0200'),
                ('class Bound { private int _state; } '+
                 'class Program { static void Main() { var x = new Bound(); '+
                 'System.Console.WriteLine(x._state); } }',
                 'CS0122')
            ]
            for i,(source,code) in enumerate(compiler_negative):
                program.write_text(source,encoding="utf-8")
                failure_dir=root/f"negative-{i}"
                failure=run("build",project,"--no-restore","--disable-build-servers",
                            "-p:UseAppHost=false","--output",str(failure_dir),ok=False)
                self.assertIn(code,failure)
                self.assertFalse((failure_dir/"OopSnapshots.dll").exists())
            print(f"CSHARP-OOP-PROPERTY-SNAPSHOT-PASS sdk={sdk} "
                  f"fixed={len(cases)-oracle_count} oracle={oracle_count} "
                  "compiler-negative=3 constructor-property-invariants "
                  "defensive-deep-copy alias-separation revisioned-staging "
                  "no-partial-state private-set-readonly culture-identical empty-feed",
                  flush=True)
