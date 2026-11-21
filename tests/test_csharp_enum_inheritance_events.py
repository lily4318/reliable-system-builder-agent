"""C# real-compiler enum and sealed inheritance event-transition contract.

Synthetic research audit event scenario: explicit noncontiguous enum wire codes,
undefined/default/narrowing refusal, sealed descendants, nonvirtual base safety
gate, staged all-or-nothing in-memory results and independent Python QA oracle.
No third-party packages, real study records, paid services or deployment.
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

// Wire codes are explicit. All other byte values, including default zero,
// are invalid and must be checked after decoding untrusted JSON numbers.
enum StudyPhase : byte { Draft=1, Checked=2, Released=4 }

sealed class LedgerState
{
    public string Subject { get; }
    public StudyPhase Phase { get; set; } = StudyPhase.Draft;
    public int Samples { get; set; }
    public int Valid { get; set; }
    public int Total { get; set; }
    public int Sequence { get; set; }
    public LedgerState(string subject) { Subject=subject; }
    public LedgerState Copy() => new(Subject) {
        Phase=Phase, Samples=Samples, Valid=Valid, Total=Total,
        Sequence=Sequence
    };
}

record View(int phase,int samples,int valid,int total,int sequence);
record Response(string status,View? before,View? after,int? revision,string[]? trace);

// The nonvirtual gate belongs to the base, never to a derived class.
abstract class ResearchEvent
{
    public string Subject { get; }
    public int Sequence { get; }
    public StudyPhase From { get; }
    public StudyPhase To { get; }
    public abstract string Kind { get; }
    protected abstract StudyPhase RequiredFrom { get; }
    protected abstract StudyPhase RequiredTo { get; }
    protected ResearchEvent(string subject,int sequence,StudyPhase from,StudyPhase to)
    {
        if ((subject!="P01" && subject!="P02") ||
            sequence<1 || sequence>6 ||
            !Enum.IsDefined(typeof(StudyPhase),from) ||
            !Enum.IsDefined(typeof(StudyPhase),to))
            throw new ArgumentException("BASE_INVARIANT");
        Subject=subject; Sequence=sequence; From=from; To=to;
    }
    public bool TryExecute(LedgerState stage,out string status)
    {
        if (Subject!=stage.Subject) { status="SUBJECT"; return false; }
        if (Sequence!=stage.Sequence+1) { status="SEQUENCE"; return false; }
        if (stage.Phase!=From) { status="STALE"; return false; }
        if (From!=RequiredFrom || To!=RequiredTo)
            { status="TRANSITION"; return false; }
        if (!ExecutePayload(stage,out status)) return false;
        stage.Phase=To;
        stage.Sequence=Sequence;
        status="OK";
        return true;
    }
    protected abstract bool ExecutePayload(LedgerState stage,out string status);
}

sealed class CollectEvent : ResearchEvent
{
    private readonly int? _value;
    public CollectEvent(string subject,int seq,StudyPhase from,StudyPhase to,int? value)
        : base(subject,seq,from,to)
    {
        if (value is <0 or >5) throw new ArgumentException("SCORE");
        _value=value;
    }
    public override string Kind=>"collect";
    protected override StudyPhase RequiredFrom=>StudyPhase.Draft;
    protected override StudyPhase RequiredTo=>StudyPhase.Draft;
    protected override bool ExecutePayload(LedgerState stage,out string status)
    {
        stage.Samples++;
        if (_value.HasValue) {stage.Valid++;stage.Total=checked(stage.Total+_value.Value);}
        status="OK";return true;
    }
}

sealed class CheckEvent : ResearchEvent
{
    private readonly bool _approved;
    public CheckEvent(string subject,int seq,StudyPhase from,StudyPhase to,bool approved)
        : base(subject,seq,from,to) { _approved=approved; }
    public override string Kind=>"check";
    protected override StudyPhase RequiredFrom=>StudyPhase.Draft;
    protected override StudyPhase RequiredTo=>StudyPhase.Checked;
    protected override bool ExecutePayload(LedgerState stage,out string status)
    {
        if (!_approved) {status="DENIED";return false;}
        if (stage.Valid==0) {status="NO_VALID";return false;}
        status="OK";return true;
    }
}

sealed class ReleaseEvent : ResearchEvent
{
    private readonly string _approver;
    public ReleaseEvent(string subject,int seq,StudyPhase from,StudyPhase to,string approver)
        : base(subject,seq,from,to) {_approver=approver;}
    public override string Kind=>"release";
    protected override StudyPhase RequiredFrom=>StudyPhase.Checked;
    protected override StudyPhase RequiredTo=>StudyPhase.Released;
    protected override bool ExecutePayload(LedgerState stage,out string status)
    {
        if (_approver!="QA") {status="DENIED";return false;}
        status="OK";return true;
    }
}

static class Program
{
    static View ViewOf(LedgerState s)
        =>new((int)s.Phase,s.Samples,s.Valid,s.Total,s.Sequence);
    static Response Bad(string reason)=>new(reason,null,null,null,null);
    static Response Refused(string reason,View initial)
        =>new(reason,initial,initial,0,null);
    static bool Exact(JsonElement obj,params string[] expected)
    {
        if (obj.ValueKind!=JsonValueKind.Object) return false;
        var names=new HashSet<string>(StringComparer.Ordinal);
        foreach(var p in obj.EnumerateObject())
            if(!expected.Contains(p.Name,StringComparer.Ordinal) || !names.Add(p.Name))
                return false;
        return names.Count==expected.Length;
    }
    static bool ValidSubject(string? s) => s=="P01" || s=="P02";
    static bool Phase(JsonElement raw,out StudyPhase phase,out string error)
    {
        phase=default;error="TYPE";
        if(raw.ValueKind!=JsonValueKind.Number || !raw.TryGetInt32(out int value))
            return false;
        error="ENUM";
        // Prevent unchecked narrowing (e.g. 257 -> 1).
        if(value<0 || value>byte.MaxValue) return false;
        phase=(StudyPhase)(byte)value;
        return Enum.IsDefined(typeof(StudyPhase),phase);
    }
    static bool ParseEvent(JsonElement raw,out ResearchEvent ev,out string error)
    {
        ev=null!;error="EVENT";
        if(raw.ValueKind!=JsonValueKind.Object ||
           !raw.TryGetProperty("kind",out var k) || k.ValueKind!=JsonValueKind.String)
            return false;
        string? kind=k.GetString();
        if(kind!="collect" && kind!="check" && kind!="release")
            {error="KIND";return false;}
        string payload=kind=="collect"?"value":kind=="check"?"approved":"approver";
        if(!Exact(raw,"kind","subject","sequence","from","to",payload))
            return false;
        var subject=raw.GetProperty("subject");
        var seq=raw.GetProperty("sequence");
        if(subject.ValueKind!=JsonValueKind.String ||
           seq.ValueKind!=JsonValueKind.Number || !seq.TryGetInt32(out int n))
            {error="TYPE";return false;}
        string? id=subject.GetString();
        if(!ValidSubject(id)) {error="SUBJECT";return false;}
        if(n<1 || n>6) {error="SEQUENCE";return false;}
        if(!Phase(raw.GetProperty("from"),out var from,out error)) return false;
        if(!Phase(raw.GetProperty("to"),out var to,out error)) return false;
        var value=raw.GetProperty(payload);
        error="PAYLOAD";
        try
        {
            if(kind=="collect")
            {
                int? v=null;
                if(value.ValueKind!=JsonValueKind.Null)
                {
                    if(value.ValueKind!=JsonValueKind.Number ||
                       !value.TryGetInt32(out int score) ||
                       score<0 || score>5) return false;
                    v=score;
                }
                ev=new CollectEvent(id!,n,from,to,v);
            }
            else if(kind=="check")
            {
                if(value.ValueKind!=JsonValueKind.True &&
                   value.ValueKind!=JsonValueKind.False) return false;
                ev=new CheckEvent(id!,n,from,to,value.GetBoolean());
            }
            else
            {
                if(value.ValueKind!=JsonValueKind.String) return false;
                ev=new ReleaseEvent(id!,n,from,to,value.GetString()??"");
            }
        }
        catch(ArgumentException) { return false; }
        error="OK";return true;
    }

    static Response Evaluate(JsonElement root)
    {
        if(!Exact(root,"subject","initial","events")) return Bad("SHAPE");
        var id=root.GetProperty("subject");
        if(id.ValueKind!=JsonValueKind.String) return Bad("TYPE");
        string? subject=id.GetString();
        if(!ValidSubject(subject)) return Bad("INIT");
        if(!Phase(root.GetProperty("initial"),out var initial,out string error))
            return Bad(error);
        if(initial!=StudyPhase.Draft) return Bad("INIT");
        var events=root.GetProperty("events");
        if(events.ValueKind!=JsonValueKind.Array) return Bad("SHAPE");
        if(events.GetArrayLength()>6) return Bad("LIMIT");
        var baseline=new LedgerState(subject!);
        var before=ViewOf(baseline);
        if(events.GetArrayLength()==0) return Refused("EMPTY",before);
        var stage=baseline.Copy();
        var trace=new List<string>();
        foreach(var raw in events.EnumerateArray())
        {
            if(!ParseEvent(raw,out var e,out error)) return Refused(error,before);
            if(!e.TryExecute(stage,out error)) return Refused(error,before);
            trace.Add(e.Kind);
        }
        return new Response("OK",before,ViewOf(stage),1,trace.ToArray());
    }

    static object Probe()
    {
        // A cast makes an enum instance, not a validated domain state.
        bool zeroDefined=Enum.IsDefined(typeof(StudyPhase),default(StudyPhase));
        bool gapDefined=Enum.IsDefined(typeof(StudyPhase),(StudyPhase)3);
        bool publishedDefined=Enum.IsDefined(typeof(StudyPhase),StudyPhase.Released);
        bool wrappedCode=unchecked((StudyPhase)257)==StudyPhase.Draft;
        bool nonvirtualGate=!(typeof(ResearchEvent).GetMethod("TryExecute")?.IsVirtual ?? true);
        bool sealedChildren=typeof(CollectEvent).IsSealed &&
                            typeof(CheckEvent).IsSealed &&
                            typeof(ReleaseEvent).IsSealed;
        return new {zeroDefined,gapDefined,publishedDefined,wrappedCode,
                    nonvirtualGate,sealedChildren};
    }
    static int Main(string[] args)
    {
        System.Globalization.CultureInfo.CurrentCulture=
          System.Globalization.CultureInfo.GetCultureInfo(args[1]);
        using var document=JsonDocument.Parse(File.ReadAllBytes(args[0]));
        if(document.RootElement.ValueKind!=JsonValueKind.Array) return 2;
        Console.WriteLine(JsonSerializer.Serialize(new {
            probe=Probe(),cases=document.RootElement.EnumerateArray()
                            .Select(Evaluate).ToArray()
        }));
        return 0;
    }
}
'''

class CsharpEnumInheritanceEventsTests(unittest.TestCase):
    def test_native_enum_inheritance_event_state_machine(self):
        exe = shutil.which("dotnet")
        if not exe:
            if os.environ.get("GITHUB_ACTIONS") == "true":
                self.fail("PREINSTALLED_DOTNET_REQUIRED")
            self.skipTest("native .NET unavailable")
        exe = str(Path(exe).resolve())
        with tempfile.TemporaryDirectory(prefix="csharp-enum-inheritance-") as tmp:
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
            app = root/"EnumInheritance"
            run("new","console","--framework","net10.0","--name","EnumInheritance",
                "--output",str(app),"--no-restore")
            program = app/"Program.cs"
            program.write_text(PROGRAM, encoding="utf-8")
            project = str(app/"EnumInheritance.csproj")
            run("restore",project,"--configfile",str(config),"--packages",str(root/"packages"),
                "--disable-build-servers","-p:NuGetAudit=false")
            assets = json.loads((app/"obj/project.assets.json").read_text())
            self.assertEqual(assets["libraries"], {})
            self.assertEqual(list((root/"packages").iterdir()), [])
            run("build",project,"--no-restore","--disable-build-servers","-p:UseAppHost=false")
            dll = app/"bin/Debug/net10.0/EnumInheritance.dll"
            self.assertTrue(dll.is_file())


            def event(kind,n,from_phase,to_phase,subject="P01",**data):
                return {"kind":kind,"subject":subject,"sequence":n,
                        "from":from_phase,"to":to_phase,**data}
            def collect(n,value,subject="P01"):
                return event("collect",n,1,1,subject,value=value)
            def check(n,approved=True,subject="P01",to_phase=2):
                return event("check",n,1,to_phase,subject,approved=approved)
            def release(n,approver="QA",subject="P01",from_phase=2,to_phase=4):
                return event("release",n,from_phase,to_phase,subject,
                             approver=approver)
            def view(phase=1,samples=0,valid=0,total=0,sequence=0):
                return dict(phase=phase,samples=samples,valid=valid,
                            total=total,sequence=sequence)
            baseline=view()
            def oracle(events,subject="P01"):
                current=1; count=0; valid=0; total=0; sequence=0; trace=[]
                for e in events:
                    kind=e["kind"]
                    if e["subject"]!=subject: return "SUBJECT",None
                    if e["sequence"]!=sequence+1: return "SEQUENCE",None
                    if e["from"] not in (1,2,4) or e["to"] not in (1,2,4):
                        return "ENUM",None
                    if e["from"]!=current: return "STALE",None
                    expected={"collect":(1,1),"check":(1,2),"release":(2,4)}[kind]
                    if (e["from"],e["to"])!=expected:
                        return "TRANSITION",None
                    if kind=="collect":
                        count+=1
                        if e["value"] is not None:
                            valid+=1;total+=e["value"]
                    elif kind=="check":
                        if not e["approved"]: return "DENIED",None
                        if valid==0: return "NO_VALID",None
                    elif kind=="release":
                        if e["approver"]!="QA": return "DENIED",None
                    current=e["to"];sequence=e["sequence"];trace.append(kind)
                return "OK",{"status":"OK","before":baseline,
                             "after":view(current,count,valid,total,sequence),
                             "revision":1,"trace":trace}
            cases=[]
            def make(events,subject="P01"):
                reason,output=oracle(events,subject)
                if reason!="OK":
                    output={"status":reason,"before":baseline,"after":baseline,
                            "revision":0,"trace":None}
                payload={"subject":subject,"initial":1,"events":events}
                cases.append((json.dumps(payload,separators=(",",":")),output))
            def malformed(raw,status,prevalidated=False):
                expected={"status":status,
                          "before":baseline if prevalidated else None,
                          "after":baseline if prevalidated else None,
                          "revision":0 if prevalidated else None,"trace":None}
                cases.append((raw,expected))
            # Fixed successful transitions, including legitimate 0, null, and two actors.
            make([collect(1,0),check(2),release(3)])
            make([collect(1,None),collect(2,5),check(3),release(4)])
            make([collect(1,5),check(2)])
            make([collect(1,None),collect(2,0),check(3)],"P01")
            make([collect(1,2,"P02"),check(2,subject="P02"),
                  release(3,subject="P02")],"P02")
            # Fixed lifecycle refusals, all of which keep initial state intact.
            make([collect(1,None),check(2)])
            make([collect(1,0),check(2,False)])
            make([collect(1,0),check(2),release(3,"OTHER")])
            make([collect(1,0),release(2)])
            make([collect(1,0),collect(1,5)])
            make([collect(1,0),collect(2,2,"P02")])
            make([collect(1,0),check(2,True,to_phase=4)])
            make([collect(1,0),check(2),collect(3,5)])
            make([collect(1,0),check(2),release(3),collect(4,5)])
            make([collect(1,0),event("collect",2,0,1,value=5)])
            make([collect(1,0),event("collect",2,1,3,value=5)])
            malformed("null","SHAPE")
            malformed('{"subject":"P01","initial":1}',"SHAPE")
            malformed('{"subject":"P01","subject":"P02","initial":1,"events":[]}',"SHAPE")
            malformed('{"subject":"P01","initial":0,"events":[]}',"ENUM")
            malformed('{"subject":"P01","initial":3,"events":[]}',"ENUM")
            malformed('{"subject":"P01","initial":257,"events":[]}',"ENUM")
            malformed('{"subject":"P01","initial":2,"events":[]}',"INIT")
            malformed('{"subject":"P01","initial":true,"events":[]}',"TYPE")
            malformed('{"subject":"P01","initial":"1","events":[]}',"TYPE")
            malformed('{"subject":"P03","initial":1,"events":[]}',"INIT")
            malformed('{"subject":"P01","initial":1,"events":{}}',"SHAPE")
            malformed('{"subject":"P01","initial":1,"events":[]}',"EMPTY",True)
            malformed('{"subject":"P01","initial":1,"events":['+
                      ",".join(json.dumps(collect(i,0)) for i in range(1,8))+']}',"LIMIT")
            malformed('{"subject":"P01","initial":1,"events":[0]}',"EVENT",True)
            malformed('{"subject":"P01","initial":1,"events":[{"kind":"other"}]}',"KIND",True)
            malformed('{"subject":"P01","initial":1,"events":[{"kind":"collect"}]}',"EVENT",True)
            malformed('{"subject":"P01","initial":1,"events":[{"kind":"collect","subject":"P01","sequence":1,"from":1,"to":1,"value":0,"value":5}]}',"EVENT",True)
            malformed('{"subject":"P01","initial":1,"events":[{"kind":"collect","subject":"P01","sequence":1,"from":1,"to":1,"value":true}]}',"PAYLOAD",True)
            malformed('{"subject":"P01","initial":1,"events":[{"kind":"collect","subject":"P01","sequence":1,"from":1,"to":1,"value":6}]}',"PAYLOAD",True)
            malformed('{"subject":"P01","initial":1,"events":[{"kind":"check","subject":"P01","sequence":1,"from":1,"to":2,"approved":null}]}',"PAYLOAD",True)
            malformed('{"subject":"P01","initial":1,"events":[{"kind":"release","subject":"P01","sequence":1,"from":2,"to":4,"approver":true}]}',"PAYLOAD",True)
            malformed('{"subject":"P01","initial":1,"events":[{"kind":"collect","subject":"P01","sequence":0,"from":1,"to":1,"value":0}]}',"SEQUENCE",True)
            malformed('{"subject":"P01","initial":1,"events":[{"kind":"collect","subject":"P01","sequence":1,"from":257,"to":1,"value":0}]}',"ENUM",True)
            malformed('{"subject":"P01","initial":1,"events":[{"kind":"collect","subject":false,"sequence":1,"from":1,"to":1,"value":0}]}',"TYPE",True)
            malformed('{"subject":"P01","initial":1,"events":[{"kind":"collect","subject":"P03","sequence":1,"from":1,"to":1,"value":0}]}',"SUBJECT",True)
            malformed('{"subject":"P01","initial":1,"events":[{"kind":"collect","subject":"P01","sequence":1,"from":1,"to":1,"value":0,"extra":0}]}',"EVENT",True)
            oracle_count=0
            for a,b,c in itertools.product((None,0,2,5),repeat=3):
                e1,e2,e3=collect(1,a),collect(2,b),collect(3,c)
                options=[
                  [e1,e2,e3,check(4),release(5)],
                  [e1,e2,e3,check(4,False),release(5)],
                  [e1,e2,e3,check(4),release(5,"UNKNOWN")],
                  [e1,e2,release(3)],
                  [e1,collect(1,b),e3],
                  [e1,collect(2,b,"P02"),e3],
                  [e1,e2,check(3,True,to_phase=4)],
                  [e1,e2,check(3),release(4),collect(5,c)]
                ]
                for candidate in options:
                    make(candidate);oracle_count+=1
            payload=("["+",".join(raw for raw,_ in cases)+"]").encode("utf-8")
            infile=root/"synthetic-events.json"
            infile.write_bytes(payload)
            english=run(str(dll),str(infile),"en-US")
            german=run(str(dll),str(infile),"de-DE")
            self.assertEqual(english,german)
            observed=json.loads(english)
            expected=[val for _,val in cases]
            self.assertEqual(observed["cases"],expected)
            self.assertEqual(infile.read_bytes(),payload)
            self.assertEqual(observed["probe"],{
                "zeroDefined":False,"gapDefined":False,
                "publishedDefined":True,"wrappedCode":True,
                "nonvirtualGate":True,"sealedChildren":True
            })
            compiler_negative=[
              ('enum One { Ready=1 } enum Two { Ready=1 } '+
               'class Program { static void Main() { One x=Two.Ready; } }',
               "CS0266"),
              ('sealed class Base { } class Child:Base { } '+
               'class Program { static void Main(){} }',
               "CS0509"),
              ('class Base { public void Apply() {} } '+
               'class Child : Base { public override void Apply() {} } '+
               'class Program { static void Main(){} }',
               "CS0506")
            ]
            for i,(src,error) in enumerate(compiler_negative):
                program.write_text(src,encoding="utf-8")
                build_dir=root/f"bad-{i}"
                output=run("build",project,"--no-restore","--disable-build-servers",
                           "-p:UseAppHost=false","--output",str(build_dir),ok=False)
                self.assertIn(error,output)
                self.assertFalse((build_dir/"EnumInheritance.dll").exists())
            print(f"CSHARP-ENUM-INHERITANCE-PASS sdk={sdk} "
                  f"fixed={len(cases)-oracle_count} oracle={oracle_count} "
                  "compiler-negative=3 explicit-enum-undefined-narrowing "
                  "sealed-derived-nonvirtual-base-gate staged-reject "
                  "polymorphic-events culture-identical empty-feed",flush=True)
