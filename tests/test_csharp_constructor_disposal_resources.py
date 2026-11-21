"""Native C# constructor/finalizer and deterministic temporary-file ownership.

Real FileStream handles with DeleteOnClose, constructor failure injection at
three acquisition boundaries, IDisposable/using idempotence, independently
modeled exception cleanup. Finalizer verified by syntax/reflection ONLY:
no GC timing, collection or finalizer execution assertion. Synthetic data.
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
using System.Reflection;
using System.Linq;
using System.Collections.Generic;
using System.IO;

sealed class Audit
{
    public int Acquired;
    public int Released;
    public int CloseErrors;
    public int Writes;
    public int ByteTotal;
    public int DisposeCalls;
    public int Active => Acquired-Released;
}

sealed class SyntheticConstructorFailure : Exception { }
sealed class SyntheticWorkFailure : Exception { }

// Actual on-disk FileStream with DeleteOnClose: owned and released exactly once.
sealed class TrackedTempLease : IDisposable
{
    private readonly FileStream _stream;
    private readonly Audit _audit;
    private readonly bool _injectCloseFailure;
    private bool _closed;
    public TrackedTempLease(string path,Audit audit,bool injectCloseFailure)
    {
        _stream=new FileStream(path,FileMode.CreateNew,FileAccess.ReadWrite,
                               FileShare.None,4096,FileOptions.DeleteOnClose);
        _audit=audit;
        _injectCloseFailure=injectCloseFailure;
        audit.Acquired++;
    }
    public void Write(int count)
    {
        if(_closed)throw new ObjectDisposedException(nameof(TrackedTempLease));
        _stream.Write(new byte[count],0,count);
        _audit.Writes++;
        _audit.ByteTotal+=count;
    }
    public void Dispose()
    {
        if(_closed)return;
        _closed=true;
        _stream.Dispose(); // Real operating-system file handle closure.
        _audit.Released++;
        if(_injectCloseFailure)
        {
            _audit.CloseErrors++;
            throw new IOException("SYNTHETIC_CLOSE_FAULT");
        }
    }
}

sealed class ResearchTempOwner : IDisposable
{
    private TrackedTempLease? _source;
    private TrackedTempLease? _work;
    private readonly Audit _audit;
    private bool _disposed;
    public bool Disposed=>_disposed;
    public ResearchTempOwner(string folder,int failAt,int closeFault,Audit audit)
    {
        _audit=audit;
        try
        {
            if(failAt==1)throw new SyntheticConstructorFailure();
            _source=new TrackedTempLease(Path.Combine(folder,"source.tmp"),audit,
                                         closeFault==1);
            if(failAt==2)throw new SyntheticConstructorFailure();
            _work=new TrackedTempLease(Path.Combine(folder,"working.tmp"),audit,
                                       closeFault==2);
            if(failAt==3)throw new SyntheticConstructorFailure();
        }
        catch
        {
            // Constructor did not publish an owner: release partial acquisitions.
            try { Dispose(); }
            catch(IOException) { /* preserves the primary constructor failure */ }
            throw;
        }
    }
    public void Write(int which,int count)
    {
        if(_disposed)throw new ObjectDisposedException(nameof(ResearchTempOwner));
        TrackedTempLease selected=which==1?_source!:_work!;
        selected.Write(count);
    }
    public void Dispose()
    {
        _audit.DisposeCalls++;
        if(_disposed)return;
        _disposed=true;
        IOException? first=null;
        // Both owned leases are always attempted, even after one close fails.
        foreach(TrackedTempLease? resource in new[]{_work,_source})
        {
            try {resource?.Dispose();}
            catch(IOException ex){first??=ex;}
        }
        if(first!=null)throw first;
    }
}

// Deliberately separated syntax probe. Never asked to close a managed file.
// No GC.Collect, GC.WaitForPendingFinalizers, or finalizer timing assertion.
sealed class FinalizerSyntaxProbe : IDisposable
{
    private bool _disposed;
    public int DisposeTransitions {get;private set;}
    ~FinalizerSyntaxProbe()
    {
        // Not used as the lifecycle/cleanup oracle.
        System.Threading.Interlocked.Increment(ref _unobservedCount);
    }
    private static int _unobservedCount;
    public void Dispose()
    {
        if(_disposed)return;
        _disposed=true;
        DisposeTransitions++;
        GC.SuppressFinalize(this);
    }
}

record Instruction(string Op,int Which,int Count);
record Outcome(string status,bool? constructed,int? acquired,int? released,
               int? active,int? closeErrors,int? writes,int? byteTotal,
               int? disposeCalls,int? remainingFiles,bool? ownerDisposed);
static class Program
{
    static bool Exact(JsonElement obj,params string[] keys)
    {
        if(obj.ValueKind!=JsonValueKind.Object)return false;
        var found=new HashSet<string>(StringComparer.Ordinal);
        foreach(var p in obj.EnumerateObject())
            if(!keys.Contains(p.Name,StringComparer.Ordinal)||!found.Add(p.Name))
                return false;
        return found.Count==keys.Length;
    }
    static Outcome Bad(string status)
        =>new(status,null,null,null,null,null,null,null,null,null,null);

    static bool Instructions(JsonElement raw,out List<Instruction> actions)
    {
        actions=new();
        if(raw.ValueKind!=JsonValueKind.Array)return false;
        foreach(var item in raw.EnumerateArray())
        {
            if(item.ValueKind!=JsonValueKind.Object ||
               !item.TryGetProperty("op",out var op) ||
               op.ValueKind!=JsonValueKind.String)return false;
            string type=op.GetString()??"";
            if(type=="write")
            {
                if(!Exact(item,"op","which","count"))return false;
                var which=item.GetProperty("which");var count=item.GetProperty("count");
                if(which.ValueKind!=JsonValueKind.Number||!which.TryGetInt32(out int w)||
                   (w!=1&&w!=2)||count.ValueKind!=JsonValueKind.Number||
                   !count.TryGetInt32(out int n)||n<0||n>5)return false;
                actions.Add(new(type,w,n));
            }
            else if(type=="fault"||type=="dispose")
            {
                if(!Exact(item,"op"))return false;
                actions.Add(new(type,0,0));
            }
            else return false;
        }
        return true;
    }
    static string Work(ResearchTempOwner owner,List<Instruction> actions)
    {
        try
        {
            foreach(var action in actions)
            {
                if(action.Op=="fault")throw new SyntheticWorkFailure();
                if(action.Op=="dispose")
                {
                    try{owner.Dispose();}
                    catch(IOException){return "CLOSE_ERROR";}
                }
                else owner.Write(action.Which,action.Count);
            }
            return "OK";
        }
        catch(ObjectDisposedException){return "DISPOSED";}
        catch(SyntheticWorkFailure){return "WORK_ERROR";}
    }
    static Outcome Evaluate(JsonElement root,string parent,int index)
    {
        if(!Exact(root,"id","failAt","closeFault","mode","actions"))
            return Bad("SHAPE");
        var id=root.GetProperty("id");var fa=root.GetProperty("failAt");
        var cf=root.GetProperty("closeFault");var mode=root.GetProperty("mode");
        if(id.ValueKind!=JsonValueKind.String ||
           (id.GetString()!="R1"&&id.GetString()!="R2")||
           fa.ValueKind!=JsonValueKind.Number||!fa.TryGetInt32(out int failAt)||
           failAt<0||failAt>3||
           cf.ValueKind!=JsonValueKind.Number||!cf.TryGetInt32(out int closeFault)||
           closeFault<0||closeFault>2||
           mode.ValueKind!=JsonValueKind.String ||
           (mode.GetString()!="using"&&mode.GetString()!="manual"))
            return Bad("CONFIG");
        var raw=root.GetProperty("actions");
        if(raw.ValueKind!=JsonValueKind.Array)return Bad("ACTION");
        if(raw.GetArrayLength()>6)return Bad("LIMIT");
        if(!Instructions(raw,out var actions))return Bad("ACTION");

        var folder=Path.Combine(parent,"case-"+index.ToString("D4"));
        Directory.CreateDirectory(folder);
        var audit=new Audit();
        ResearchTempOwner? owner=null;
        bool constructed=false;
        string status="OK";
        try
        {
            owner=new ResearchTempOwner(folder,failAt,closeFault,audit);
            constructed=true;
            if(mode.GetString()=="using")
            {
                try
                {
                    using(owner){status=Work(owner,actions);}
                }
                catch(IOException){if(status=="OK")status="CLOSE_ERROR";}
            }
            else
            {
                try {status=Work(owner,actions);}
                finally
                {
                    try{owner.Dispose();}
                    catch(IOException){if(status=="OK")status="CLOSE_ERROR";}
                }
            }
        }
        catch(SyntheticConstructorFailure){status="CTOR_FAIL";}

        // Real directory inventory verifies that OS-level temp handles are gone.
        int remaining=Directory.GetFiles(folder).Length;
        return new(status,constructed,audit.Acquired,audit.Released,
                   audit.Active,audit.CloseErrors,audit.Writes,audit.ByteTotal,
                   audit.DisposeCalls,remaining,constructed?owner!.Disposed:null);
    }
    static object Probe()
    {
        using var marker=new FinalizerSyntaxProbe();
        marker.Dispose();
        return new {
            declaredClassFinalizer=typeof(FinalizerSyntaxProbe).GetMethod(
                "Finalize",BindingFlags.Instance|BindingFlags.NonPublic|
                BindingFlags.DeclaredOnly)!=null,
            ownerHasNoCustomFinalizer=typeof(ResearchTempOwner).GetMethod(
                "Finalize",BindingFlags.Instance|BindingFlags.NonPublic|
                BindingFlags.DeclaredOnly)==null,
            probeDisposeTransitions=marker.DisposeTransitions,
            ownerIDisposable=typeof(IDisposable).IsAssignableFrom(
                typeof(ResearchTempOwner))
        };
    }
    static int Main(string[] args)
    {
        System.Globalization.CultureInfo.CurrentCulture=
            System.Globalization.CultureInfo.GetCultureInfo(args[1]);
        var baseDir=args[2];
        Directory.CreateDirectory(baseDir);
        using var doc=JsonDocument.Parse(File.ReadAllBytes(args[0]));
        if(doc.RootElement.ValueKind!=JsonValueKind.Array)return 2;
        var results=new List<Outcome>();
        int i=0;
        foreach(var item in doc.RootElement.EnumerateArray())
            results.Add(Evaluate(item,baseDir,i++));
        Console.WriteLine(JsonSerializer.Serialize(new {probe=Probe(),cases=results}));
        return 0;
    }
}
'''

class CsharpConstructorDisposalResourcesTests(unittest.TestCase):
    def test_native_constructor_cleanup_finalizer_non_determinism(self):
        exe = shutil.which("dotnet")
        if not exe:
            if os.environ.get("GITHUB_ACTIONS") == "true":
                self.fail("PREINSTALLED_DOTNET_REQUIRED")
            self.skipTest("native .NET unavailable")
        exe = str(Path(exe).resolve())
        with tempfile.TemporaryDirectory(prefix="csharp-resource-lifecycle-") as tmp:
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
            app = root/"ResourceLifecycle"
            run("new","console","--framework","net10.0","--name","ResourceLifecycle",
                "--output",str(app),"--no-restore")
            program = app/"Program.cs"
            program.write_text(PROGRAM, encoding="utf-8")
            project = str(app/"ResourceLifecycle.csproj")
            run("restore",project,"--configfile",str(config),"--packages",str(root/"packages"),
                "--disable-build-servers","-p:NuGetAudit=false")
            assets = json.loads((app/"obj/project.assets.json").read_text())
            self.assertEqual(assets["libraries"], {})
            self.assertEqual(list((root/"packages").iterdir()), [])
            run("build",project,"--no-restore","--disable-build-servers","-p:UseAppHost=false")
            dll = app/"bin/Debug/net10.0/ResourceLifecycle.dll"
            self.assertTrue(dll.is_file())




            def write(which,n):
                return {"op":"write","which":which,"count":n}
            def dispose():return {"op":"dispose"}
            def fault():return {"op":"fault"}
            def independent_model(config):
                acquired={0:2,1:0,2:1,3:2}[config["failAt"]]
                released=acquired
                close_errors=int(0<config["closeFault"]<=acquired)
                status="CTOR_FAIL" if config["failAt"] else "OK"
                writes=byte_total=0
                disposed=False
                explicit_calls=0
                if config["failAt"]==0:
                    for act in config["actions"]:
                        if act["op"]=="fault":
                            status="WORK_ERROR"
                            break
                        if act["op"]=="dispose":
                            explicit_calls+=1
                            if not disposed:
                                disposed=True
                                if close_errors:
                                    status="CLOSE_ERROR"
                                    break
                        elif disposed:
                            status="DISPOSED"
                            break
                        else:
                            writes+=1
                            byte_total+=act["count"]
                    if status=="OK" and close_errors:
                        status="CLOSE_ERROR"
                return {
                    "status":status,
                    "constructed":config["failAt"]==0,
                    "acquired":acquired,
                    "released":released,
                    "active":0,
                    "closeErrors":close_errors,
                    "writes":writes,
                    "byteTotal":byte_total,
                    "disposeCalls":1+explicit_calls,
                    "remainingFiles":0,
                    "ownerDisposed":True if config["failAt"]==0 else None
                }

            cases=[]
            def add(failAt=0,closeFault=0,mode="using",actions=None,id="R1"):
                if actions is None:actions=[]
                obj={"id":id,"failAt":failAt,"closeFault":closeFault,
                     "mode":mode,"actions":actions}
                cases.append((json.dumps(obj,separators=(",",":")),
                              independent_model(obj)))
            def bad(raw,status):
                cases.append((raw,{"status":status,"constructed":None,
                                   "acquired":None,"released":None,"active":None,
                                   "closeErrors":None,"writes":None,
                                   "byteTotal":None,"disposeCalls":None,
                                   "remainingFiles":None,"ownerDisposed":None}))
            add()
            add(mode="manual")
            add(actions=[write(1,0),write(2,5)])
            add(actions=[write(1,1),write(2,2),fault()])
            add(actions=[write(1,3),dispose(),write(2,1)])
            add(actions=[write(2,4),dispose(),dispose()])
            add(actions=[dispose(),dispose()])
            add(actions=[fault(),write(1,1)])
            add(closeFault=1,actions=[write(1,1)])
            add(closeFault=2,actions=[write(2,1)])
            add(closeFault=1,actions=[write(1,3),fault()])
            add(closeFault=2,actions=[dispose(),write(1,3)])
            add(failAt=1,closeFault=1)
            add(failAt=2,closeFault=1)
            add(failAt=2,closeFault=2)
            add(failAt=3,closeFault=2)
            add(failAt=3,closeFault=1)
            add(failAt=2,closeFault=0,mode="manual")
            add(id="R2",actions=[write(1,1)])
            add(id="R2",mode="manual",actions=[write(2,0),fault()])
            add(mode="manual",closeFault=2,actions=[write(1,5),write(2,2)])
            add(mode="manual",actions=[dispose(),write(2,2)])
            bad("null","SHAPE")
            bad('{"id":"R1","failAt":0,"closeFault":0,"mode":"using"}',"SHAPE")
            bad('{"id":"R1","id":"R2","failAt":0,"closeFault":0,"mode":"using","actions":[]}',"SHAPE")
            bad(json.dumps({"id":"../escape","failAt":0,"closeFault":0,"mode":"using","actions":[]}),"CONFIG")
            bad(json.dumps({"id":"R1","failAt":-1,"closeFault":0,"mode":"using","actions":[]}),"CONFIG")
            bad(json.dumps({"id":"R1","failAt":4,"closeFault":0,"mode":"using","actions":[]}),"CONFIG")
            bad(json.dumps({"id":"R1","failAt":True,"closeFault":0,"mode":"using","actions":[]}),"CONFIG")
            bad(json.dumps({"id":"R1","failAt":0,"closeFault":3,"mode":"using","actions":[]}),"CONFIG")
            bad(json.dumps({"id":"R1","failAt":0,"closeFault":0,"mode":"unknown","actions":[]}),"CONFIG")
            bad(json.dumps({"id":"R1","failAt":0,"closeFault":0,"mode":"using","actions":{}}),"ACTION")
            bad(json.dumps({"id":"R1","failAt":0,"closeFault":0,"mode":"using","actions":[{"op":"other"}]}),"ACTION")
            bad(json.dumps({"id":"R1","failAt":0,"closeFault":0,"mode":"using","actions":[{"op":"write","which":0,"count":1}]}),"ACTION")
            bad(json.dumps({"id":"R1","failAt":0,"closeFault":0,"mode":"using","actions":[{"op":"write","which":1,"count":6}]}),"ACTION")
            bad(json.dumps({"id":"R1","failAt":0,"closeFault":0,"mode":"using","actions":[{"op":"write","which":1,"count":True}]}),"ACTION")
            bad(json.dumps({"id":"R1","failAt":0,"closeFault":0,"mode":"using","actions":[{"op":"dispose","extra":0}]}),"ACTION")
            bad('{"id":"R1","failAt":0,"closeFault":0,"mode":"using","actions":[{"op":"write","which":1,"count":1,"count":2}]}',"ACTION")
            bad(json.dumps({"id":"R1","failAt":0,"closeFault":0,"mode":"using","actions":[write(1,0)]*7}),"LIMIT")

            oracle_count=0
            for failAt,closeFault,n,mode in itertools.product(
                range(4),(0,1,2),(0,1,3,5),("using","manual")):
                patterns=(
                    [write(1,n)],
                    [write(1,n),write(2,5-n),fault()],
                    [write(1,n),dispose(),write(2,1)],
                    [write(2,n),dispose(),dispose()],
                    [fault(),write(1,n)],
                    [write(1,n),write(2,n)]
                )
                for actions in patterns:
                    add(failAt,closeFault,mode,actions)
                    oracle_count+=1
            payload=("["+",".join(raw for raw,_ in cases)+"]").encode("utf-8")
            infile=root/"synthetic-resources.json"
            infile.write_bytes(payload)
            data_root=root/"real-temp-files"
            data_root.mkdir()
            english=run(str(dll),str(infile),"en-US",str(data_root))
            german=run(str(dll),str(infile),"de-DE",str(data_root))
            self.assertEqual(english,german)
            observed=json.loads(english)
            self.assertEqual(observed["cases"],[want for _,want in cases])
            self.assertEqual(infile.read_bytes(),payload)
            self.assertEqual(list(data_root.rglob("*.tmp")),[])
            self.assertEqual(observed["probe"],{
                "declaredClassFinalizer":True,
                "ownerHasNoCustomFinalizer":True,
                "probeDisposeTransitions":1,
                "ownerIDisposable":True
            })
            compiler_negative=[
                ('struct Lease { ~Lease() {} } '+
                 'class Program { static void Main(){} }',"CS0575"),
                ('class Lease { private Lease(){} } '+
                 'class Program { static void Main(){new Lease();} }',"CS0122"),
                ('class Lease { public Lease(int required){} } '+
                 'class Program { static void Main(){new Lease();} }',"CS7036")
            ]
            for i,(source,error) in enumerate(compiler_negative):
                program.write_text(source,encoding="utf-8")
                failure=root/f"negative-{i}"
                output=run("build",project,"--no-restore","--disable-build-servers",
                           "-p:UseAppHost=false","--output",str(failure),ok=False)
                self.assertIn(error,output)
                self.assertFalse((failure/"ResourceLifecycle.dll").exists())
            print(f"CSHARP-CONSTRUCTOR-DISPOSAL-PASS sdk={sdk} "
                  f"fixed={len(cases)-oracle_count} oracle={oracle_count} "
                  "compiler-negative=3 real-file-handles-delete-on-close "
                  "constructor-partial-rollback owned-leases using-finally "
                  "dispose-idempotent-close-fault-best-effort "
                  "finalizer-nondeterministic-not-awaited culture-identical empty-feed",
                  flush=True)
