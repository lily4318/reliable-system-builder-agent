"""Controlled POSIX training lab; no network or production deployment."""
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def build(version):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as z:
        z.writestr('lesson.html', '<h1>Teaching handout '+version+'</h1>')
        z.writestr('example.csv', 'item,version\n1,'+version+'\n')
    return out.getvalue()


def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def activate(root, target, expected_current, cut='none'):
    # Trusted pins stored separately by lab controller. Single trusted writer only.
    pins = json.loads((root/'trusted.json').read_text())
    current = root/'current'
    if current.read_text() != expected_current:
        raise ValueError('stale activation')
    if target not in pins or digest((root/(target+'.zip')).read_bytes()) != pins[target]:
        raise ValueError('artifact integrity')
    stage = root/'next'
    with stage.open('w') as f:
        f.write(target)
        f.flush()
        os.fsync(f.fileno())
    if cut == 'before':
        os._exit(71)
    os.replace(stage, current)
    fsync_dir(root)
    if cut == 'after':
        os._exit(72)


@unittest.skipUnless(os.name == 'posix' and hasattr(os, 'O_DIRECTORY'), 'POSIX lab')
class ActivationRecoveryLab(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.payloads = {v:build(v) for v in ('v1','v2')}
        for v, b in self.payloads.items():
            (self.root/(v+'.zip')).write_bytes(b)
        (self.root/'trusted.json').write_text(json.dumps({v:digest(b) for v,b in self.payloads.items()}))
        (self.root/'current').write_text('v1')

    def run_activation(self, target, current, cut='none'):
        return subprocess.run([sys.executable, __file__, 'activate', str(self.root), target, current, cut], capture_output=True, text=True, timeout=10)

    def observe(self, version):
        self.assertEqual((self.root/'current').read_text(), version)
        raw = (self.root/(version+'.zip')).read_bytes()
        self.assertEqual(raw, self.payloads[version])
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            self.assertEqual(z.namelist(), ['lesson.html','example.csv'])
            self.assertEqual(z.read('example.csv'), ('item,version\n1,'+version+'\n').encode())
            self.assertEqual(z.read('lesson.html'), ('<h1>Teaching handout '+version+'</h1>').encode())

    def test_interrupted_before_activation_old_version_remains(self):
        self.assertEqual(self.run_activation('v2','v1','before').returncode, 71)
        self.observe('v1')
        self.assertEqual((self.root/'next').read_text(), 'v2')
        self.assertEqual(self.run_activation('v2','v1').returncode, 0)
        self.observe('v2')

    def test_interrupted_after_commit_reconcile_then_rollback(self):
        self.assertEqual(self.run_activation('v2','v1','after').returncode, 72)
        self.observe('v2')
        stale = self.run_activation('v2','v1')
        self.assertNotEqual(stale.returncode, 0)
        self.assertIn('stale activation', stale.stderr)
        self.observe('v2')
        self.assertEqual(self.run_activation('v1','v2').returncode, 0)
        self.observe('v1')
        self.assertEqual((self.root/'v2.zip').read_bytes(), self.payloads['v2'])

    def test_corrupt_candidate_rejected_before_switch(self):
        (self.root/'v2.zip').write_bytes(self.payloads['v2']+b'bad')
        result = self.run_activation('v2','v1')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('artifact integrity', result.stderr)
        self.observe('v1')
        self.assertFalse((self.root/'next').exists())

    def test_corrupt_rollback_target_cannot_activate(self):
        self.assertEqual(self.run_activation('v2','v1').returncode, 0)
        (self.root/'v1.zip').write_bytes(b'bad')
        result = self.run_activation('v1','v2')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('artifact integrity', result.stderr)
        self.observe('v2')


if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1]=='activate':
        activate(Path(sys.argv[2]), *sys.argv[3:])
    else:
        unittest.main()
