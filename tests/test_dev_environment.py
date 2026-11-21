"""Native POSIX toolchain training, temporary synthetic workspaces only.
No downloads, third-party packages, user config edits, or VS Code GUI claims.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class DevEnvironmentTests(unittest.TestCase):
    def setUp(self):
        if os.name != "posix":
            self.skipTest("POSIX toolchain experiment; Windows not validated")
        tmp = tempfile.TemporaryDirectory(prefix="dev-env-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.python = str(Path(sys.executable).absolute())
        self.node = shutil.which("node")
        self.npm = shutil.which("npm")
        # Preserve only the already-installed tool directories, not host config or secrets.
        folders = [str(Path(p).parent) for p in (self.python, self.node, self.npm) if p]
        self.env = {"PATH":os.pathsep.join(folders+[os.defpath]), "HOME":str(self.home),
                    "LC_ALL":"C", "PYTHONNOUSERSITE":"1", "PIP_NO_INDEX":"1",
                    "NPM_CONFIG_USERCONFIG":str(self.home/".npmrc"),
                    "NPM_CONFIG_GLOBALCONFIG":str(self.home/"global.npmrc"),
                    "NPM_CONFIG_CACHE":str(self.home/"cache"),
                    "NPM_CONFIG_OFFLINE":"true", "NPM_CONFIG_IGNORE_SCRIPTS":"true",
                    "NPM_CONFIG_AUDIT":"false", "NPM_CONFIG_FUND":"false"}

    def run_cmd(self, *args, env=None, cwd=None, success=True):
        p = subprocess.run(args, cwd=cwd or self.root, env=self.env if env is None else env,
                           shell=False, capture_output=True, text=True, timeout=30)
        if success:
            self.assertEqual(p.returncode,0,p.stderr[-1500:])  # synthetic data only
        else:
            self.assertNotEqual(p.returncode,0)
        return p.stdout.strip(),p.stderr

    def require_node(self):
        if not self.node or not self.npm:
            if os.environ.get("GITHUB_ACTIONS")=="true":
                self.fail("native Node/npm required in CI; missing tooling is not a pass")
            self.skipTest("native Node/npm unavailable")
        version=self.run_cmd(self.node,"--version")[0]
        self.assertGreaterEqual(int(version.split(".")[0][1:]),22)
        return version

    def test_python_workspace_interpreter_path_and_import_isolation(self):
        va,vb=self.root/"workspace A"/".venv",self.root/"workspace B"/".venv"
        base_version=self.run_cmd(self.python,"-c","import sys; print(sys.version.split()[0])")[0]
        for v in (va,vb):
            self.run_cmd(self.python,"-m","venv","--without-pip",str(v))
        a,b=str(va/"bin/python"),str(vb/"bin/python")
        inspect="import sys; print(sys.prefix); print(sys.base_prefix); print(sys.version.split()[0])"
        ap=self.run_cmd(a,"-c",inspect)[0].splitlines()
        bp=self.run_cmd(b,"-c",inspect)[0].splitlines()
        self.assertEqual(Path(ap[0]),va)
        self.assertEqual(Path(bp[0]),vb)
        self.assertEqual(ap[1:],bp[1:])
        self.assertNotEqual(ap[0],ap[1])
        self.assertEqual(ap[2],base_version)
        # Two actual environments, not two different Python versions.
        site=Path(self.run_cmd(a,"-c","import sysconfig; print(sysconfig.get_path('purelib'))")[0])
        (site/"lab_version.py").write_text("VALUE='workspace-A'\n")
        query="import lab_version; print(lab_version.VALUE)"
        self.assertEqual(self.run_cmd(a,"-c",query)[0],"workspace-A")
        self.assertIn("ModuleNotFoundError",self.run_cmd(b,"-c",query,success=False)[1])
        wrong={**self.env,"PATH":str(vb/"bin")+os.pathsep+self.env["PATH"],"VIRTUAL_ENV":str(va)}
        self.assertEqual(Path(self.run_cmd("python","-c",inspect,env=wrong)[0].splitlines()[0]),vb)
        self.assertEqual(self.run_cmd(a,"-c",query,env=wrong)[0],"workspace-A")
        contam=self.root/"injected"; contam.mkdir()
        (contam/"lab_version.py").write_text("VALUE='wrong-import'\n")
        polluted={**wrong,"PYTHONPATH":str(contam)}
        self.assertEqual(self.run_cmd(a,"-c",query,env=polluted)[0],"wrong-import")
        self.assertEqual(self.run_cmd(a,"-I","-c",query,env=polluted)[0],"workspace-A")
        # Pin checked against actual runtime, not activation labels or filenames.
        def require_pin(executable, expected):
            observed=self.run_cmd(executable,"-c","import sys; print(sys.version.split()[0])")[0]
            if observed!=expected:
                raise ValueError("PYTHON_VERSION_MISMATCH")
            return observed
        self.assertEqual(require_pin(a,base_version),base_version)
        with self.assertRaisesRegex(ValueError,"PYTHON_VERSION_MISMATCH"):
            require_pin(a,"0.0.0")
        print("DEV-ENV-PYTHON:",base_version,"two venvs; PATH mismatch; PYTHONPATH shadow blocked by -I",flush=True)

    def test_node_env_file_precedence_and_unwanted_preload(self):
        version=self.require_node()
        (self.root/"base.env").write_text("LAB_MODE=base\nLAB_PORT=8000\n")
        (self.root/"workspace.env").write_text("LAB_MODE=workspace\nLAB_PORT=9000\n")
        probe="console.log(JSON.stringify([process.env.LAB_MODE,process.env.LAB_PORT]))"
        args=(self.node,"--env-file=base.env","--env-file=workspace.env","-e",probe)
        self.assertEqual(json.loads(self.run_cmd(*args)[0]),["workspace","9000"])
        self.assertEqual(json.loads(self.run_cmd(*args,env={**self.env,"LAB_MODE":"process"})[0]),["process","9000"])
        self.run_cmd(self.node,"--env-file=absent.env","-e",probe,success=False)
        # Harmless synthetic marker demonstrates that NODE_OPTIONS can execute code.
        (self.root/"preload.cjs").write_text("globalThis.labPreloaded=true;\n")
        probe="console.log(globalThis.labPreloaded===true)"
        polluted={**self.env,"NODE_OPTIONS":"--require=./preload.cjs"}
        self.assertEqual(self.run_cmd(self.node,"-e",probe,env=polluted)[0],"true")
        self.assertEqual(self.run_cmd(self.node,"-e",probe)[0],"false")
        self.assertEqual(self.run_cmd(self.node,"--version")[0],version)
        print("DEV-ENV-NODE:",version,"process > later env file > earlier; preload isolated",flush=True)

    def test_npm_offline_lock_drift_and_lifecycle_suppression(self):
        self.require_node()
        npm_version=self.run_cmd(self.npm,"--version")[0]
        dep=self.root/"dep"; dep.mkdir()
        (dep/"package.json").write_text(json.dumps({"name":"lab-local","version":"1.0.0","main":"index.js"}))
        (dep/"index.js").write_text("module.exports=17;\n")
        package={"name":"lab-app","version":"1.0.0","private":True,
                 "dependencies":{"lab-local":"file:./dep"},
                 "scripts":{"postinstall":"node -e \"require('fs').writeFileSync('lifecycle-marker','ran')\""}}
        manifest=self.root/"package.json"
        manifest.write_text(json.dumps(package))
        flags=("--offline","--ignore-scripts","--no-audit","--no-fund")
        self.run_cmd(self.npm,"install","--package-lock-only",*flags)
        lock=self.root/"package-lock.json"; original=lock.read_bytes()
        self.run_cmd(self.npm,"ci",*flags)
        self.assertEqual(self.run_cmd(self.node,"-e","console.log(require('lab-local'))")[0],"17")
        self.assertFalse((self.root/"lifecycle-marker").exists())
        extra=self.root/"extra"; extra.mkdir()
        (extra/"package.json").write_text('{"name":"lab-extra","version":"1.0.0"}')
        package["dependencies"]["lab-extra"]="file:./extra"
        manifest.write_text(json.dumps(package))
        _,error=self.run_cmd(self.npm,"ci",*flags,success=False)
        self.assertIn("lock",error.lower())
        self.assertEqual(lock.read_bytes(),original)
        self.assertFalse((self.root/"lifecycle-marker").exists())
        del package["dependencies"]["lab-extra"]
        manifest.write_text(json.dumps(package))
        self.run_cmd(self.npm,"ci",*flags)
        self.assertEqual(lock.read_bytes(),original)
        self.assertEqual(self.run_cmd(self.node,"-e","console.log(require('lab-local'))")[0],"17")
        self.assertFalse((self.root/"lifecycle-marker").exists())
        print("DEV-ENV-NPM:",npm_version,"local-only lock drift refused; restore passes; scripts suppressed",flush=True)


if __name__=="__main__":
    unittest.main()
