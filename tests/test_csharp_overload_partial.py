"""Native C# overload resolution and partial declarations in an offline lab."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


SOURCES = {
    "ScoreApi.Numeric.cs": '''\
namespace SyntheticScoring;

public static partial class ScoreApi
{
    private static string Route(string kind) => "score:" + kind;

    public static string FromNumber(int value) => Route("int");
    public static string FromNumber(long value) => Route("long");
    public static string FromNumber(decimal value) => Route("decimal");
}
''',
    "ScoreApi.Token.cs": '''\
namespace SyntheticScoring;

public static partial class ScoreApi
{
    public static string FromToken(string? value) =>
        Route(value is null ? "missing-text" : "text");

    public static string FromToken(byte[]? value) =>
        Route(value is null ? "missing-bytes" : "bytes");
}
''',
    "Program.cs": '''\
using SyntheticScoring;

System.Console.WriteLine(string.Join("|",
    ScoreApi.FromNumber((short)7),
    ScoreApi.FromNumber(7),
    ScoreApi.FromNumber(7L),
    ScoreApi.FromNumber(7m),
    ScoreApi.FromToken((string?)null),
    ScoreApi.FromToken((byte[]?)null),
    ScoreApi.FromToken("sample"),
    ScoreApi.FromToken(new byte[] { 7 })));
''',
}
EXPECTED_ROUTES = (
    "score:int|score:int|score:long|score:decimal|"
    "score:missing-text|score:missing-bytes|score:text|score:bytes"
)


class CsharpOverloadPartialTests(unittest.TestCase):
    def test_native_caller_binding_and_partial_declaration_contract(self):
        exe = shutil.which("dotnet")
        in_ci = os.environ.get("GITHUB_ACTIONS") == "true"
        if not exe:
            if in_ci:
                self.fail("PREINSTALLED_DOTNET_REQUIRED")
            self.skipTest("native .NET unavailable")

        with tempfile.TemporaryDirectory(prefix="csharp-score-overloads-") as tmp:
            root = Path(tmp)
            feed = root / "feed"
            feed.mkdir()
            env = {
                key: os.environ[key] for key in ("SystemRoot", "WINDIR", "TMP", "TEMP", "ProgramData",
                                                   "ProgramFiles", "ProgramFiles(x86)")
                if key in os.environ
            }
            env.update({
                "PATH": os.defpath,
                "HOME": str(root),
                "DOTNET_CLI_HOME": str(root),
                "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
                "DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE": "true",
                "DOTNET_NOLOGO": "1",
                "DOTNET_GENERATE_ASPNET_CERTIFICATE": "false",
                "MSBUILDDISABLENODEREUSE": "1",
                "NUGET_PACKAGES": str(root / "packages"),
                "NUGET_HTTP_CACHE_PATH": str(root / "http-cache"),
            })

            if os.name == "nt":
                for key in ("USERPROFILE", "APPDATA", "LOCALAPPDATA"):
                    folder = root / key.lower()
                    folder.mkdir()
                    env[key] = str(folder)

            def run(*args):
                return subprocess.run(
                    [exe, *args], cwd=root, env=env, capture_output=True,
                    text=True, encoding="utf-8", errors="replace", timeout=60,
                )

            def require_success(result):
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return result.stdout.strip()

            sdks = []
            for line in require_success(run("--list-sdks")).splitlines():
                match = re.match(r"^((?:9|10)\.0\.\d+) \[", line)
                if match:
                    sdks.append(tuple(map(int, match[1].split("."))))
            if in_ci:
                sdks = [version for version in sdks if version[0] == 10]
                self.assertTrue(sdks, "preinstalled .NET 10 required in CI")
            elif not sdks:
                self.skipTest("native .NET 9 or 10 SDK unavailable")
            sdk = max(sdks)
            target = f"net{sdk[0]}.0"
            (root / "global.json").write_text(json.dumps({
                "sdk": {"version": ".".join(map(str, sdk)), "rollForward": "disable"}
            }), encoding="utf-8")
            (root / "Probe.csproj").write_text(f"""\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>{target}</TargetFramework>
    <Nullable>enable</Nullable>
    <NuGetAudit>false</NuGetAudit>
  </PropertyGroup>
</Project>
""", encoding="utf-8")
            for path, contents in SOURCES.items():
                (root / path).write_text(contents, encoding="utf-8")

            require_success(run("restore", "Probe.csproj", "--source", str(feed)))
            build = ("build", "Probe.csproj", "--no-restore", "--nologo", "-v", "quiet")
            executable = str(root / "bin" / "Debug" / target / "Probe.dll")
            require_success(run(*build))
            self.assertEqual(require_success(run(executable)), EXPECTED_ROUTES)

            invalid_sources = (
                ("ambiguous null", "Program.cs",
                 "SyntheticScoring.ScoreApi.FromToken(null);\n", "CS0121"),
                ("double needs an explicit conversion", "Program.cs",
                 "SyntheticScoring.ScoreApi.FromNumber(7d);\n", "CS1503"),
                ("partial accessibility mismatch", "ScoreApi.Token.cs",
                 SOURCES["ScoreApi.Token.cs"].replace(
                     "public static partial", "internal static partial", 1
                 ), "CS0262"),
                ("missing partial modifier", "ScoreApi.Token.cs",
                 SOURCES["ScoreApi.Token.cs"].replace(
                     "public static partial", "public static", 1
                 ), "CS0260"),
            )
            for name, file, contents, expected_error in invalid_sources:
                with self.subTest(case=name):
                    path = root / file
                    path.write_text(contents, encoding="utf-8")
                    try:
                        result = run(*build)
                        output = result.stdout + result.stderr
                        self.assertNotEqual(result.returncode, 0, output)
                        self.assertEqual(
                            set(re.findall(r"\b(CS\d{4}):", output)), {expected_error}, output
                        )
                    finally:
                        path.write_text(SOURCES[file], encoding="utf-8")
            require_success(run(*build))
            self.assertEqual(require_success(run(executable)), EXPECTED_ROUTES)
            print("CSHARP_OVERLOAD_PARTIAL_PASS runtime=8 compiler_rejections=4 restored=1")
