"""Owned template fixture; native CLI only with a provisioned Linux .NET 10 SDK."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

SHORT = "rsb-study-fixture"
PROGRAM = 'namespace SeedProject;\npublic static class Program { public static void Main() => System.Console.WriteLine("SeedProject:MODE_TOKEN"); }\n'
PROJECT = '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><UseAppHost>false</UseAppHost></PropertyGroup></Project>\n'
SCRIPT = 'from pathlib import Path\nPath("post-marker.txt").write_text("approved synthetic action\\n")\n'


def manifest():
    return {"author": "Training", "identity": "RSB.Owned.Study.V1", "name": "Owned study fixture",
            "shortName": SHORT, "sourceName": "SeedProject", "preferNameDirectory": True,
            "tags": {"language": "C#", "type": "project"},
            "symbols": {"mode": {"type": "parameter", "datatype": "choice", "defaultValue": "basic",
                                 "choices": [{"choice": "basic"}, {"choice": "extended"}], "replaces": "MODE_TOKEN"},
                        "includeNotes": {"type": "parameter", "datatype": "bool", "defaultValue": "false"}},
            "sources": [{"source": "./", "target": "./", "exclude": [".template.config/**/*", "private.txt", "**/bin/**", "**/obj/**"],
                         "copyOnly": ["literal.txt"], "modifiers": [{"condition": "(!includeNotes)", "exclude": ["Notes.txt"]}]}],
            "postActions": [{"actionId": "3A7C4B45-1F5D-4A30-959A-51B88E82B5D2", "description": "Owned marker only",
                             "manualInstructions": [{"text": "Optional owned marker; no manual execution needed."}],
                             "args": {"executable": sys.executable, "args": "post.py"}, "continueOnError": True}]}


def files():
    return {".template.config/template.json": json.dumps(manifest(), sort_keys=True), "SeedProject.csproj": PROJECT,
            "Program.cs": PROGRAM, "README.txt": "SeedProject MODE_TOKEN\n", "literal.txt": "SeedProject MODE_TOKEN\n",
            "Notes.txt": "optional note\n", "private.txt": "SYNTHETIC_EXCLUDED_CANARY\n", "obj/stale.txt": "old output\n", "post.py": SCRIPT}


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def make_template(root):
    for name, data in files().items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding="utf-8")


def check_owned(root):
    # Exact fixture allowlist; not a general template scanner or sandbox.
    if any(p.is_symlink() for p in root.rglob("*")) or snapshot(root) != {k: v.encode() for k, v in files().items()}:
        raise ValueError("TEMPLATE_DRIFT")


def expected(name, mode, notes=False, marker=False):
    result = {name + ".csproj": PROJECT, "Program.cs": PROGRAM.replace("SeedProject", name).replace("MODE_TOKEN", mode),
              "README.txt": name + " " + mode + "\n", "literal.txt": "SeedProject MODE_TOKEN\n", "post.py": SCRIPT}
    if notes:
        result["Notes.txt"] = "optional note\n"
    if marker:
        result["post-marker.txt"] = "approved synthetic action\n"
    return {k: v.encode() for k, v in result.items()}


class DotnetTemplateTests(unittest.TestCase):
    def test_owned_fixture_rejects_modified_action_and_extra_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_template(root)
            check_owned(root)
            config = root / ".template.config/template.json"
            changed = manifest()
            changed["postActions"][0]["args"]["args"] = "unexpected.py"
            config.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, "TEMPLATE_DRIFT"):
                check_owned(root)
            make_template(root)
            (root / "extra.txt").write_text("unexpected")
            with self.assertRaisesRegex(ValueError, "TEMPLATE_DRIFT"):
                check_owned(root)
            self.assertFalse((root / "post-marker.txt").exists())

    def test_native_template_generation_and_script_consent(self):
        dotnet = shutil.which("dotnet")
        if not dotnet or sys.platform != "linux":
            self.skipTest("NO_PREINSTALLED_LINUX_DOTNET")
        dotnet = str(Path(dotnet).resolve())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            for name in ("home", "feed", "packages", "hive", "template"):
                (root / name).mkdir()
            env = {"PATH": os.defpath, "HOME": str(root / "home"), "DOTNET_CLI_HOME": str(root / "home"),
                   "NUGET_PACKAGES": str(root / "packages"), "NUGET_HTTP_CACHE_PATH": str(root / "http-cache"),
                   "DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE": "true",
                   "DOTNET_NOLOGO": "1", "DOTNET_GENERATE_ASPNET_CERTIFICATE": "false", "MSBUILDDISABLENODEREUSE": "1", "LC_ALL": "C.UTF-8"}
            def run(*args, success=True, cwd=root):
                p = subprocess.run([dotnet, *args], cwd=cwd, env=env, capture_output=True, text=True, timeout=45)
                output = p.stdout + p.stderr
                self.assertEqual(p.returncode == 0, success, output[-3000:])
                return output
            versions = []
            for line in run("--list-sdks").splitlines():
                m = re.fullmatch(r"(10\.0\.\d+) \[(.+)\]", line.strip())
                if m:
                    v, sdkdir = m.groups()
                    base = Path(sdkdir).parent
                    if any((base / "packs/Microsoft.NETCore.App.Ref").glob("10.0.*")) and any((base / "shared/Microsoft.NETCore.App").glob("10.0.*")):
                        versions.append(v)
            if not versions:
                self.skipTest("NO_MATCHING_PREINSTALLED_DOTNET10")
            sdk = max(versions, key=lambda v: tuple(map(int, v.split('.'))))
            (root / "global.json").write_text(json.dumps({"sdk": {"version": sdk, "rollForward": "disable", "allowPrerelease": False}}))
            for name in ("Directory.Build.props", "Directory.Build.targets"):
                (root / name).write_text("<Project />")
            (root / "Directory.Build.rsp").write_text("")
            config = root / "NuGet.Config"
            config.write_text('<configuration><packageSources><clear/><add key="local" value="feed"/></packageSources></configuration>')
            self.assertEqual(run("--version").strip(), sdk)
            template = root / "template"
            make_template(template)
            check_owned(template)
            original = snapshot(template)
            def new(*args, success=True):
                return run("new", *args, "--debug:custom-hive", str(root / "hive"), success=success)
            new("install", str(template))
            self.assertIn(SHORT, new("list", SHORT))
            def generate(output, *args, success=True):
                return new(SHORT, "--name", "StudySite", "--output", str(output), "--no-update-check", *args, success=success)
            preview = root / "preview"
            generate(preview, "--allow-scripts", "yes", "--dry-run")
            self.assertEqual(snapshot(preview), {})
            invalid = root / "invalid"
            generate(invalid, "--mode", "unknown", "--allow-scripts", "no", success=False)
            self.assertEqual(snapshot(invalid), {})
            basic = root / "basic"
            generate(basic, "--allow-scripts", "no")
            self.assertEqual(snapshot(basic), expected("StudySite", "basic"))
            extended = root / "extended"
            generate(extended, "--mode", "extended", "--includeNotes", "true", "--allow-scripts", "yes")
            self.assertEqual(snapshot(extended), expected("StudySite", "extended", notes=True, marker=True))
            duplicate = root / "duplicate"
            generate(duplicate, "--mode", "extended", "--includeNotes", "true", "--allow-scripts", "yes")
            self.assertEqual(snapshot(duplicate), snapshot(extended))
            collision = root / "collision"
            collision.mkdir()
            (collision / "README.txt").write_text("existing content\n")
            before = snapshot(collision)
            generate(collision, "--allow-scripts", "yes", success=False)
            self.assertEqual(snapshot(collision), before)
            project = extended / "StudySite.csproj"
            run("restore", str(project), "--configfile", str(config), "--packages", str(root / "packages"), "--disable-build-servers", "-p:NuGetAudit=false")
            run("build", str(project), "--no-restore", "--disable-build-servers")
            self.assertEqual(run(str(extended / "bin/Debug/net10.0/StudySite.dll")).strip(), "StudySite:extended")
            self.assertEqual(snapshot(template), original)
            new("uninstall", str(template))
            self.assertNotIn(str(template), new("uninstall"))
            print(f"DOTNET-TEMPLATE-NATIVE-PASS: sdk={sdk} dry-run choice exclude copyOnly consent conflict repeat build uninstall", flush=True)


if __name__ == "__main__":
    unittest.main()
