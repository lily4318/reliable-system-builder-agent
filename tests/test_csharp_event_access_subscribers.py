"""Native C# event publishing and access modifier evidence.

Original synthetic subscription audit: stable handler identity, snapshot delivery,
attach/detach in callbacks, guarded reentry, exception isolation with preserved
side effects, and actual compiler access failures. Independent Python event model.
No real study data or deployment, no third-party dependencies.
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
using System.Reflection;

// Synthetic notification, NOT any real research subject data or authorization.
sealed class NoticeArgs : EventArgs
{
    public int Value { get; }
    public NoticeArgs(int value) => Value=value;
}

class AccessBase
{
    private readonly int _secret=7;
    internal int AssemblyOnly=>6;
    protected int ForDerived=>5;
    public int Everyone=>4;
    public int OwnerSecret()=>_secret;
}
sealed class AccessChild : AccessBase
{
    public int DerivedValue()=>ForDerived;
}

sealed class EventBroker
{
    private EventHandler<NoticeArgs>? _notice;
    private bool _dispatching;
    internal readonly List<string> Trace=new();
    internal int Accepted { get; private set; }
    internal int Failures { get; private set; }
    internal int NestedRejected { get; private set; }

    // Event accessors, unlike a public delegate field, do not expose Invoke.
    public event EventHandler<NoticeArgs> Notice
    {
        add { _notice += value; }
        remove { _notice -= value; }
    }

    internal bool TryEmit(int value,out string status)
    {
        if(_dispatching)
        {
            NestedRejected++;
            status="REENTRANT";
            return false;
        }
        if(value<0 || value>5) {status="VALUE";return false;}
        Accepted++;
        Trace.Add("emit:"+value);
        // Snapshot: add/remove during callback affects future dispatch, not this one.
        var handlers=_notice?.GetInvocationList() ?? Array.Empty<Delegate>();
        _dispatching=true;
        try
        {
            var args=new NoticeArgs(value);
            foreach(var item in handlers)
            {
                try { ((EventHandler<NoticeArgs>)item)(this,args); }
                catch(Exception)
                {
                    Failures++;
                    Trace.Add("error");
                }
            }
        }
        finally { _dispatching=false; }
        status="OK";
        return true;
    }
}

record Configuration(string Name,string Mode,string? Target);
record Command(string Op,string? Name,int Value);
record ListenerView(string name,bool active,int calls,int sum);
record Result(string status,int? accepted,int? failures,int? nestedRejected,
              string[]? trace,ListenerView[]? listeners);

sealed class Listener
{
    private readonly EventBroker _bus;
    private readonly Dictionary<string,Listener> _all;
    private readonly string _mode;
    private readonly string? _target;
    private EventHandler<NoticeArgs> _handler;
    public string Name { get; }
    public bool Active { get; private set; }
    public int Calls { get; private set; }
    public int Sum { get; private set; }

    public Listener(Configuration conf,EventBroker bus,Dictionary<string,Listener> all)
    {
        Name=conf.Name;_mode=conf.Mode;_target=conf.Target;
        _bus=bus;_all=all;
        _handler=Receive;
    }
    public bool Subscribe()
    {
        if(Active)return false;
        _bus.Notice+=_handler;Active=true;return true;
    }
    public bool Unsubscribe()
    {
        if(!Active)return false;
        _bus.Notice-=_handler;Active=false;return true;
    }
    private void Receive(object? sender,NoticeArgs msg)
    {
        Calls++;
        Sum+=msg.Value;
        _bus.Trace.Add(Name+":"+msg.Value);
        if(_mode=="throw")throw new InvalidOperationException("SYNTHETIC");
        if(_mode=="reenter")
        {
            // A callback must not recursively publish to the same broker.
            _bus.TryEmit(5,out _);
        }
        else if(_mode=="attach" && _target is not null)
        {
            if(_all[_target].Subscribe())
                _bus.Trace.Add("auto:on:"+_target);
        }
        else if(_mode=="detach" && _target is not null)
        {
            if(_all[_target].Unsubscribe())
                _bus.Trace.Add("auto:off:"+_target);
        }
    }
    public ListenerView View() => new(Name,Active,Calls,Sum);
}

static class Program
{
    static bool Exact(JsonElement obj,params string[] fields)
    {
        if(obj.ValueKind!=JsonValueKind.Object)return false;
        var keys=new HashSet<string>(StringComparer.Ordinal);
        foreach(var p in obj.EnumerateObject())
            if(!fields.Contains(p.Name,StringComparer.Ordinal)||!keys.Add(p.Name))
                return false;
        return keys.Count==fields.Length;
    }
    static Result Bad(string code)=>new(code,null,null,null,null,null);
    static bool ReadConfigs(JsonElement configs,out List<Configuration> list)
    {
        list=new();
        if(configs.ValueKind!=JsonValueKind.Array||configs.GetArrayLength()!=3)
            return false;
        var names=new HashSet<string>(StringComparer.Ordinal);
        foreach(var item in configs.EnumerateArray())
        {
            if(!Exact(item,"name","mode","target"))return false;
            var name=item.GetProperty("name");var mode=item.GetProperty("mode");
            var target=item.GetProperty("target");
            if(name.ValueKind!=JsonValueKind.String || mode.ValueKind!=JsonValueKind.String ||
               (target.ValueKind!=JsonValueKind.Null && target.ValueKind!=JsonValueKind.String))
                return false;
            string id=name.GetString()??"";
            string m=mode.GetString()??"";
            string? t=target.ValueKind==JsonValueKind.Null?null:target.GetString();
            if((id!="A"&&id!="B"&&id!="C")||!names.Add(id)||
               (m!="normal"&&m!="throw"&&m!="reenter"&&m!="attach"&&m!="detach"))
                return false;
            if(m=="attach"||m=="detach")
            {
                if(t is null || (t!="A"&&t!="B"&&t!="C")||t==id)return false;
            }
            else if(t is not null)return false;
            list.Add(new(id,m,t));
        }
        return names.Count==3;
    }
    static bool ParseActions(JsonElement raw,out List<Command> actions)
    {
        actions=new();
        if(raw.ValueKind!=JsonValueKind.Array)return false;
        foreach(var item in raw.EnumerateArray())
        {
            if(item.ValueKind!=JsonValueKind.Object ||
               !item.TryGetProperty("op",out var op)||op.ValueKind!=JsonValueKind.String)
                return false;
            string action=op.GetString()??"";
            if(action=="on"||action=="off")
            {
                if(!Exact(item,"op","name"))return false;
                var id=item.GetProperty("name");
                if(id.ValueKind!=JsonValueKind.String)return false;
                string name=id.GetString()??"";
                if(name!="A"&&name!="B"&&name!="C")return false;
                actions.Add(new(action,name,0));
            }
            else if(action=="emit")
            {
                if(!Exact(item,"op","value"))return false;
                var value=item.GetProperty("value");
                if(value.ValueKind!=JsonValueKind.Number||!value.TryGetInt32(out int n))
                    return false;
                actions.Add(new(action,null,n));
            }
            else return false;
        }
        return true;
    }
    static Result Evaluate(JsonElement root)
    {
        if(!Exact(root,"listeners","actions"))return Bad("SHAPE");
        if(!ReadConfigs(root.GetProperty("listeners"),out var configs))
            return Bad("CONFIG");
        var raw=root.GetProperty("actions");
        if(raw.ValueKind!=JsonValueKind.Array)return Bad("ACTION");
        if(raw.GetArrayLength()>8)return Bad("LIMIT");
        if(!ParseActions(raw,out var commands))return Bad("ACTION");

        var bus=new EventBroker();
        var all=new Dictionary<string,Listener>(StringComparer.Ordinal);
        foreach(var config in configs)
            all[config.Name]=new Listener(config,bus,all);
        string status="OK";
        foreach(var cmd in commands)
        {
            if(cmd.Op=="on")
            {
                if(!all[cmd.Name!].Subscribe()) {status="ALREADY_ON";break;}
                bus.Trace.Add("on:"+cmd.Name);
            }
            else if(cmd.Op=="off")
            {
                if(!all[cmd.Name!].Unsubscribe()) {status="NOT_ON";break;}
                bus.Trace.Add("off:"+cmd.Name);
            }
            else if(!bus.TryEmit(cmd.Value,out status))break;
        }
        return new Result(status,bus.Accepted,bus.Failures,bus.NestedRejected,
                          bus.Trace.ToArray(),
                          all.Values.OrderBy(v=>v.Name,StringComparer.Ordinal)
                                    .Select(v=>v.View()).ToArray());
    }
    static object Probe()
    {
        var child=new AccessChild();
        var flags=BindingFlags.Instance|BindingFlags.NonPublic;
        var privField=typeof(AccessBase).GetField("_secret",flags);
        var eventInfo=typeof(EventBroker).GetEvent("Notice");
        return new {
            publicValue=child.Everyone,assemblyValue=child.AssemblyOnly,
            protectedThroughDerived=child.DerivedValue(),privateThroughOwner=child.OwnerSecret(),
            privateReflected=privField?.IsPrivate==true,
            publicEventAdd=eventInfo?.AddMethod?.IsPublic==true,
            publicEventRemove=eventInfo?.RemoveMethod?.IsPublic==true,
            rawDelegatePrivate=typeof(EventBroker).GetField("_notice",flags)?.IsPrivate==true
        };
    }
    static int Main(string[] args)
    {
        System.Globalization.CultureInfo.CurrentCulture=
          System.Globalization.CultureInfo.GetCultureInfo(args[1]);
        using var doc=JsonDocument.Parse(File.ReadAllBytes(args[0]));
        if(doc.RootElement.ValueKind!=JsonValueKind.Array)return 2;
        Console.WriteLine(JsonSerializer.Serialize(new{
            probe=Probe(),cases=doc.RootElement.EnumerateArray().Select(Evaluate).ToArray()
        }));
        return 0;
    }
}
'''

class CsharpEventAccessSubscribersTests(unittest.TestCase):
    def test_native_event_handlers_access_and_side_effect_boundaries(self):
        exe = shutil.which("dotnet")
        if not exe:
            if os.environ.get("GITHUB_ACTIONS") == "true":
                self.fail("PREINSTALLED_DOTNET_REQUIRED")
            self.skipTest("native .NET unavailable")
        exe = str(Path(exe).resolve())
        with tempfile.TemporaryDirectory(prefix="csharp-event-access-") as tmp:
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
            app = root/"EventAccess"
            run("new","console","--framework","net10.0","--name","EventAccess",
                "--output",str(app),"--no-restore")
            program = app/"Program.cs"
            program.write_text(PROGRAM, encoding="utf-8")
            project = str(app/"EventAccess.csproj")
            run("restore",project,"--configfile",str(config),"--packages",str(root/"packages"),
                "--disable-build-servers","-p:NuGetAudit=false")
            assets = json.loads((app/"obj/project.assets.json").read_text())
            self.assertEqual(assets["libraries"], {})
            self.assertEqual(list((root/"packages").iterdir()), [])
            run("build",project,"--no-restore","--disable-build-servers","-p:UseAppHost=false")
            dll = app/"bin/Debug/net10.0/EventAccess.dll"
            self.assertTrue(dll.is_file())



            names=("A","B","C")
            def conf(name,mode="normal",target=None):
                return {"name":name,"mode":mode,"target":target}
            def cfg(a="normal",b="normal",c="normal",at=None,bt=None,ct=None):
                return [conf("A",a,at),conf("B",b,bt),conf("C",c,ct)]
            def on(name):return {"op":"on","name":name}
            def off(name):return {"op":"off","name":name}
            def emit(value):return {"op":"emit","value":value}
            def independent_oracle(configs,actions):
                specs={c["name"]:c for c in configs}
                # Python map/order simulator; no C# delegates, events, reflection.
                active=[]
                calls={n:0 for n in names}
                sums={n:0 for n in names}
                trace=[]
                accepted=failures=nested=0
                status="OK"
                for step in actions:
                    op=step["op"]
                    if op=="on":
                        n=step["name"]
                        if n in active:status="ALREADY_ON";break
                        active.append(n);trace.append("on:"+n)
                    elif op=="off":
                        n=step["name"]
                        if n not in active:status="NOT_ON";break
                        active.remove(n);trace.append("off:"+n)
                    else:
                        value=step["value"]
                        if value<0 or value>5:status="VALUE";break
                        accepted+=1;trace.append("emit:"+str(value))
                        # Copy models the snapshot of invoked handlers.
                        for n in list(active):
                            calls[n]+=1;sums[n]+=value
                            trace.append(n+":"+str(value))
                            spec=specs[n]
                            mode=spec["mode"]
                            if mode=="throw":
                                failures+=1
                                trace.append("error")
                            elif mode=="reenter":
                                nested+=1
                            elif mode=="attach":
                                target=spec["target"]
                                if target not in active:
                                    active.append(target);trace.append("auto:on:"+target)
                            elif mode=="detach":
                                target=spec["target"]
                                if target in active:
                                    active.remove(target);trace.append("auto:off:"+target)
                return {"status":status,"accepted":accepted,
                        "failures":failures,"nestedRejected":nested,
                        "trace":trace,
                        "listeners":[{"name":n,"active":n in active,
                                      "calls":calls[n],"sum":sums[n]} for n in names]}
            cases=[]
            def add(configs,actions):
                raw=json.dumps({"listeners":configs,"actions":actions},
                               separators=(",",":"))
                cases.append((raw,independent_oracle(configs,actions)))
            def bad(raw,status):
                cases.append((raw,{"status":status,"accepted":None,"failures":None,
                                   "nestedRejected":None,"trace":None,"listeners":None}))
            add(cfg(),[])
            add(cfg(),[emit(0)])
            add(cfg(),[on("A"),emit(0),off("A"),emit(1)])
            add(cfg(),[on("A"),on("B"),on("C"),emit(2)])
            add(cfg(b="throw"),[on("A"),on("B"),on("C"),emit(3)])
            add(cfg(a="detach",at="B"),[on("A"),on("B"),on("C"),emit(1),emit(2)])
            add(cfg(a="attach",at="C"),[on("A"),on("B"),emit(2),emit(5)])
            add(cfg(a="reenter"),[on("A"),on("B"),emit(1)])
            add(cfg(b="throw"),[on("B"),on("C"),emit(5),off("B"),emit(0)])
            add(cfg(),[on("A"),emit(0),on("A"),emit(5)])
            add(cfg(),[on("A"),emit(0),off("B"),emit(2)])
            add(cfg(),[on("A"),emit(0),emit(6),emit(2)])
            add(cfg(),[on("A"),emit(-1)])
            add(cfg(),[off("A")])
            add(cfg(),[on("A"),off("A"),off("A")])
            add(cfg(a="detach",at="C"),[on("A"),on("B"),emit(1)])
            add(cfg(a="attach",at="B"),[on("A"),emit(4),emit(1)])
            add(cfg(a="attach",at="B"),[on("A"),on("B"),emit(1)])
            add(cfg(a="detach",at="C"),[on("B"),emit(4)])
            add(cfg(a="reenter",b="throw"),[on("B"),on("A"),emit(4)])
            add(cfg(c="throw"),[on("C"),on("A"),emit(0),emit(5)])
            add(cfg(),[on("B"),off("B"),on("B"),emit(2)])
            bad("null","SHAPE")
            bad('{"listeners":[]}',"SHAPE")
            bad('{"listeners":[],"actions":[],"actions":[]}',"SHAPE")
            bad('{"listeners":null,"actions":[]}',"CONFIG")
            bad('{"listeners":[],"actions":[]}',"CONFIG")
            bad(json.dumps({"listeners":[conf("A"),conf("B"),conf("B")],
                            "actions":[]}),"CONFIG")
            bad(json.dumps({"listeners":[conf("A","unknown"),conf("B"),conf("C")],
                            "actions":[]}),"CONFIG")
            bad(json.dumps({"listeners":[conf("A","attach"),conf("B"),conf("C")],
                            "actions":[]}),"CONFIG")
            bad(json.dumps({"listeners":[conf("A","attach","A"),conf("B"),conf("C")],
                            "actions":[]}),"CONFIG")
            bad(json.dumps({"listeners":[conf("A","detach","Z"),conf("B"),conf("C")],
                            "actions":[]}),"CONFIG")
            bad(json.dumps({"listeners":[conf("A","normal","B"),conf("B"),conf("C")],
                            "actions":[]}),"CONFIG")
            bad('{"listeners":[{"name":"A","mode":"normal","target":null,"mode":"throw"},{"name":"B","mode":"normal","target":null},{"name":"C","mode":"normal","target":null}],"actions":[]}',"CONFIG")
            bad(json.dumps({"listeners":cfg(),"actions":{}}),"ACTION")
            bad(json.dumps({"listeners":cfg(),"actions":[{"op":"other"}]}),"ACTION")
            bad(json.dumps({"listeners":cfg(),"actions":[{"op":"emit","value":True}]}),"ACTION")
            bad(json.dumps({"listeners":cfg(),"actions":[{"op":"emit","value":None}]}),"ACTION")
            bad(json.dumps({"listeners":cfg(),"actions":[{"op":"on","name":"Z"}]}),"ACTION")
            bad(json.dumps({"listeners":cfg(),"actions":[{"op":"off","name":4}]}),"ACTION")
            bad(json.dumps({"listeners":cfg(),"actions":[{"op":"emit","value":1,"extra":0}]}),"ACTION")
            bad('{"listeners":[{"name":"A","mode":"normal","target":null},{"name":"B","mode":"normal","target":null},{"name":"C","mode":"normal","target":null}],"actions":[{"op":"emit","value":1,"value":2}]}',"ACTION")
            bad(json.dumps({"listeners":cfg(),"actions":[on("A")]*9}),"LIMIT")

            oracle_count=0
            for a,b,c in itertools.product((0,1,2,5),repeat=3):
                candidates=[
                    (cfg(),[on("A"),on("B"),on("C"),emit(a)]),
                    (cfg(b="throw"),[on("A"),on("B"),on("C"),emit(a),emit(b)]),
                    (cfg(a="detach",at="B"),[on("A"),on("B"),on("C"),emit(a),emit(b)]),
                    (cfg(a="attach",at="C"),[on("A"),on("B"),emit(a),emit(b)]),
                    (cfg(a="reenter"),[on("A"),on("B"),emit(a),emit(c)]),
                    (cfg(b="throw"),[on("B"),on("C"),emit(a),off("B"),emit(c)]),
                    (cfg(),[on("A"),emit(a),on("A"),emit(c)]),
                    (cfg(),[on("A"),emit(a),emit(6),emit(c)])
                ]
                for listeners,actions in candidates:
                    add(listeners,actions)
                    oracle_count+=1
            payload=("["+",".join(raw for raw,_ in cases)+"]").encode("utf-8")
            batch=root/"synthetic-subscriptions.json"
            batch.write_bytes(payload)
            first=run(str(dll),str(batch),"en-US")
            second=run(str(dll),str(batch),"de-DE")
            self.assertEqual(first,second)
            data=json.loads(first)
            self.assertEqual(data["cases"],[expected for _,expected in cases])
            self.assertEqual(batch.read_bytes(),payload)
            self.assertEqual(data["probe"],{
                "publicValue":4,"assemblyValue":6,
                "protectedThroughDerived":5,"privateThroughOwner":7,
                "privateReflected":True,"publicEventAdd":True,
                "publicEventRemove":True,"rawDelegatePrivate":True
            })
            compiler_negative=[
                ('class Bus { public event System.EventHandler? Changed; } '+
                 'class Program { static void Main() { var b=new Bus(); '+
                 'b.Changed?.Invoke(null,System.EventArgs.Empty); } }',"CS0070"),
                ('class Bus { private int hidden=7; } '+
                 'class Program { static void Main() { '+
                 'System.Console.WriteLine(new Bus().hidden); } }',"CS0122"),
                ('class Base { protected void Raise(){} } '+
                 'class Program { static void Main() { new Base().Raise(); } }',"CS0122")
            ]
            for i,(source,error) in enumerate(compiler_negative):
                program.write_text(source,encoding="utf-8")
                outputdir=root/f"negative-{i}"
                output=run("build",project,"--no-restore","--disable-build-servers",
                           "-p:UseAppHost=false","--output",str(outputdir),ok=False)
                self.assertIn(error,output)
                self.assertFalse((outputdir/"EventAccess.dll").exists())
            print(f"CSHARP-EVENT-ACCESS-PASS sdk={sdk} "
                  f"fixed={len(cases)-oracle_count} oracle={oracle_count} "
                  "compiler-negative=3 handler-unsubscribe-attach-detach "
                  "snapshot-dispatch reentry-guard exception-isolation "
                  "nonrollback-side-effects event-only-raise "
                  "private-protected-internal culture-identical empty-feed",
                  flush=True)
