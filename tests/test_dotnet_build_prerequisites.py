"""Owned synthetic build fixture; native .NET only if already provisioned."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile


def project(tfm, app=False, version="1.0.0"):
    props = f"<TargetFramework>{tfm}</TargetFramework>"
    if app:
        props += "<OutputType>Exe</OutputType><UseAppHost>false</UseAppHost>"
    items = ('<ItemGroup><ProjectReference Include="../Lib/Lib.csproj" />'
             f'<PackageReference Include="Synthetic.Marker" Version="[{version}]" />'
             '</ItemGroup>') if app else ""
    return '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>' + props + '</PropertyGroup>' + items + '</Project>'


def fixture(root, tfm, sdk):
    for name in ("App", "Lib", "feed", "packages", "home"):
        (root / name).mkdir(exist_ok=True)
    (root / "global.json").write_text(json.dumps({"sdk": {"version": sdk, "rollForward": "disable", "allowPrerelease": False}}))
    for name in ("Directory.Build.props", "Directory.Build.targets"):
        (root / name).write_text("<Project />")
    (root / "Directory.Build.rsp").write_text("")
    (root / "NuGet.Config").write_text('<configuration><packageSources><clear/><add key="local" value="feed"/></packageSources><packageSourceMapping><packageSource key="local"><package pattern="Synthetic.Marker"/></packageSource></packageSourceMapping></configuration>')
    (root / "Lib/Lib.csproj").write_text(project(tfm))
    (root / "App/App.csproj").write_text(project(tfm, True))
    (root / "Lib/Score.cs").write_text('public static class Score { public static int Value() => 17; }')
    (root / "App/Program.cs").write_text('System.Console.WriteLine(Score.Value());')
    for v in ("1.0.0", "1.0.1"):
        with zipfile.ZipFile(root / f"feed/Synthetic.Marker.{v}.nupkg", "w") as z:
            z.writestr("Synthetic.Marker.nuspec", f'<package><metadata><id>Synthetic.Marker</id><version>{v}</version><authors>Training</authors><description>Nonexecutable marker</description></metadata></package>')
            z.writestr(f"lib/{tfm}/_._", "")


def inspect_owned_fixture(root, tfm, sdk):
    # Exact narrow authored contract, not MSBuild evaluation or generic scanner.
    expected = {"App/App.csproj": project(tfm, True), "Lib/Lib.csproj": project(tfm)}
    for name, text in expected.items():
        path = root / name
        if path.resolve() != path or ET.tostring(ET.parse(path).getroot()) != ET.tostring(ET.fromstring(text)):
            raise ValueError("PROJECT_CONTRACT")
    if json.loads((root / "global.json").read_text()) != {"sdk": {"version": sdk, "rollForward": "disable", "allowPrerelease": False}}:
        raise ValueError("SDK_CONTRACT")
    return ("Lib/Lib.csproj", "App/App.csproj")


class DotnetBuildPrerequisites(unittest.TestCase):
    def test_owned_project_fixture_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fixture(root, "net8.0", "8.0.100")
            self.assertEqual(inspect_owned_fixture(root, "net8.0", "8.0.100"), ("Lib/Lib.csproj", "App/App.csproj"))
            app = root / "App/App.csproj"
            for bad in (project("net9.0", True), project("net8.0", True).replace("../Lib/Lib.csproj", "../../Other.csproj"), project("net8.0", True).replace("</Project>", '<Target Name="Unexpected"><Exec Command="never-run"/></Target></Project>')):
                app.write_text(bad)
                with self.assertRaisesRegex(ValueError, "PROJECT_CONTRACT"):
                    inspect_owned_fixture(root, "net8.0", "8.0.100")
            app.write_text(project("net8.0", True))
            (root / "global.json").write_text('{"sdk":{"version":"8.0.100","rollForward":"latestMajor"}}')
            with self.assertRaisesRegex(ValueError, "SDK_CONTRACT"):
                inspect_owned_fixture(root, "net8.0", "8.0.100")
            self.assertFalse((root / "App/obj").exists())
            self.assertEqual(list((root / "packages").iterdir()), [])

    def test_native_sdk_restore_and_build_if_preinstalled(self):
        dotnet = shutil.which("dotnet")
        if not dotnet:
            self.skipTest("DOTNET_NOT_PREINSTALLED")
        dotnet = str(Path(dotnet).resolve())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            env = {"PATH": os.defpath, "HOME": str(root / "home"), "DOTNET_CLI_HOME": str(root / "home"),
                   "NUGET_PACKAGES": str(root / "packages"), "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
                   "DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE": "true", "DOTNET_NOLOGO": "1",
                   "DOTNET_GENERATE_ASPNET_CERTIFICATE": "false", "NUGET_HTTP_CACHE_PATH": str(root / "http-cache"),
                   "MSBUILDDISABLENODEREUSE": "1", "LC_ALL": "C.UTF-8"}
            def run(*args, cwd=root, expected=True):
                p = subprocess.run([dotnet, *args], cwd=cwd, env=env, capture_output=True, text=True, timeout=45)
                output = p.stdout + p.stderr
                self.assertEqual(p.returncode == 0, expected, output[-2500:])
                return output
            sdk_list = run("--list-sdks")
            versions = []
            for line in sdk_list.splitlines():
                m = re.fullmatch(r"(\d+\.\d+\.\d+) \[(.+)\]", line.strip())
                if m:
                    v, sdk_dir = m.groups()
                    major = int(v.split(".")[0]); base = Path(sdk_dir).parent
                    if 8 <= major <= 10 and any((base / "packs/Microsoft.NETCore.App.Ref").glob(f"{major}.0.*")) and any((base / "shared/Microsoft.NETCore.App").glob(f"{major}.0.*")):
                        versions.append((tuple(map(int, v.split("."))), v, major))
            if not versions:
                self.skipTest("NO_PREINSTALLED_SDK_WITH_MATCHING_PACK_AND_RUNTIME")
            _, sdk, major = max(versions)
            tfm = f"net{major}.0"
            fixture(root, tfm, sdk)
            self.assertEqual(inspect_owned_fixture(root, tfm, sdk), ("Lib/Lib.csproj", "App/App.csproj"))
            self.assertEqual(run("--version", cwd=root / "App").strip(), sdk)
            print(f"DOTNET-NATIVE-SDK: {sdk} target={tfm}", flush=True)
            pin = root / "global.json"; old_pin = pin.read_bytes()
            pin.write_text('{"sdk":{"version":"999.0.100","rollForward":"disable","allowPrerelease":false}}')
            run("--version", cwd=root / "App", expected=False)
            pin.write_bytes(old_pin)
            app = root / "App/App.csproj"
            restore = ("restore", str(app), "--configfile", str(root / "NuGet.Config"), "--packages", str(root / "packages"), "--disable-build-servers", "-p:NuGetAudit=false")
            build = ("build", str(app), "--no-restore", "--disable-build-servers")
            self.assertIn("NETSDK1004", run(*build, expected=False))
            run(*restore, "--use-lock-file")
            lock = root / "App/packages.lock.json"; old_lock = lock.read_bytes()
            self.assertEqual(json.loads(old_lock)["dependencies"][tfm]["Synthetic.Marker"]["resolved"], "1.0.0")
            run(*restore, "--locked-mode")
            self.assertEqual(lock.read_bytes(), old_lock)
            app.write_text(project(tfm, True, "1.0.1"))
            self.assertIn("NU1004", run(*restore, "--locked-mode", expected=False))
            self.assertEqual(lock.read_bytes(), old_lock)
            app.write_text(project(tfm, True))
            run(*restore, "--locked-mode")
            run(*build)
            dll = root / f"App/bin/Debug/{tfm}/App.dll"
            self.assertEqual(run(str(dll)).strip(), "17")
            (root / "Lib/Score.cs").write_text('public static class Score { public static int Value() => 23; }')
            run(*build)
            self.assertEqual(run(str(dll)).strip(), "23")
            self.assertEqual(lock.read_bytes(), old_lock)
            print("DOTNET-NATIVE-PASS: exact SDK, missing SDK, no restore, locked drift, dependency rebuild", flush=True)


if __name__ == "__main__":
    unittest.main()
