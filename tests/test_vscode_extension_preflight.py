"""TD004 controlled prerequisites, not VS Code/Emmet or a VSIX installer."""
import hashlib
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
import warnings
import zipfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


class FormTokens(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.ids, self.labels, self.fields = [], [], []
        self.feed(markup)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "label":
            self.labels.append(attrs.get("for"))
        if tag == "input":
            self.fields.append((attrs.get("id"), attrs.get("name")))

    handle_startendtag = handle_starttag


def accept_form(markup):
    # Bounded fixture oracle, not a general HTML accessibility/security checker.
    p = FormTokens(markup)
    expected = ["visit1", "visit2", "visit3"]
    if (len(p.ids) != len(set(p.ids)) or p.labels != expected
            or p.fields != [(x, x) for x in expected]):
        raise ValueError("FORM_CONTRACT")
    return p.fields


def format_on_save(user_file, workspace_file, language):
    # Only the documented single-language boolean subset, strict JSON, no JSONC.
    scopes = [json.loads(p.read_bytes()) for p in (user_file, workspace_file)]
    values = [False]
    for scope in scopes + [x.get("[" + language + "]", {}) for x in scopes]:
        if "editor.formatOnSave" in scope:
            value = scope["editor.formatOnSave"]
            if type(value) is not bool:
                raise ValueError("SETTING_TYPE")
            values.append(value)
    return values[-1]


MANIFEST = {"publisher": "synthetic", "name": "study-snippets", "version": "1.0.0",
            "engines": {"vscode": "^1.90.0"},
            "contributes": {"snippets": [{"language": "html", "path": "./snippets/html.json"}]}}
PAYLOAD = {"Study label": {"prefix": "study-label", "body": ["<label for=\"$1\">$2</label>"]}}
FILES = {"extension/package.json", "extension/snippets/html.json"}


def fixture(manifest=MANIFEST, extra=None):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as z:
        z.writestr("extension/package.json", json.dumps(manifest))
        z.writestr("extension/snippets/html.json", json.dumps(PAYLOAD))
        if extra:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                z.writestr(extra, "synthetic")
    return stream.getvalue()


def inspect_fixture(data, approved_digest):
    # Strict allowlist for this one nonexecutable synthetic archive only.
    # Not Marketplace attestation, a general VSIX scanner, or install permission.
    if len(data) > 65536 or digest(data) != approved_digest:
        raise ValueError("ARCHIVE_PIN")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        infos = z.infolist()
        if (len(infos) != 2 or {i.filename for i in infos} != FILES
                or any(i.file_size > 8192 or i.flag_bits & 1 or
                       stat.S_IFMT(i.external_attr >> 16) not in (0, stat.S_IFREG)
                       for i in infos)):
            raise ValueError("ARCHIVE_ENTRIES")
        if json.loads(z.read("extension/package.json")) != MANIFEST:
            raise ValueError("MANIFEST_CONTRACT")
        if json.loads(z.read("extension/snippets/html.json")) != PAYLOAD:
            raise ValueError("SNIPPET_CONTRACT")
    return "synthetic.study-snippets@1.0.0"


def restore_owned_file(path, expected_current, original):
    # One trusted writer in a new temp directory; not concurrent CAS or PC repair.
    if path.read_bytes() != expected_current:
        raise ValueError("DRIFT_STOP")
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
        staged = Path(f.name)
        f.write(original)
        f.flush()
        os.fsync(f.fileno())
    try:
        os.replace(staged, path)
    finally:
        staged.unlink(missing_ok=True)


class VSCodePrerequisites(unittest.TestCase):
    def test_form_expansion_output_contract(self):
        # Hand-authored equivalent of a numbered markup expansion, never engine output.
        good = "<form>" + "".join(
            f'<label for="visit{i}">Visit {i}</label><input id="visit{i}" name="visit{i}">'
            for i in range(1, 4)) + "</form>"
        self.assertEqual(accept_form(good), [(f"visit{i}", f"visit{i}") for i in range(1, 4)])
        for bad in (good.replace('id="visit2"', 'id="visit1"'),
                    good.replace('for="visit2"', 'for="missing"'),
                    good.replace('name="visit3"', 'name="visit2"')):
            with self.assertRaisesRegex(ValueError, "FORM_CONTRACT"):
                accept_form(bad)

    def test_settings_scope_from_real_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            user = Path(tmp) / "user.json"
            workspace = Path(tmp) / ".vscode" / "settings.json"
            workspace.parent.mkdir()
            user.write_text(json.dumps({"editor.formatOnSave": False,
                                        "[html]": {"editor.formatOnSave": True}}))
            workspace.write_text(json.dumps({"editor.formatOnSave": False}))
            self.assertTrue(format_on_save(user, workspace, "html"))
            self.assertFalse(format_on_save(user, workspace, "python"))
            workspace.write_text(json.dumps({"editor.formatOnSave": True,
                                             "[html]": {"editor.formatOnSave": False}}))
            self.assertFalse(format_on_save(user, workspace, "html"))
            self.assertTrue(format_on_save(user, workspace, "python"))
            workspace.write_text('{"editor.formatOnSave":"false"}')
            with self.assertRaisesRegex(ValueError, "SETTING_TYPE"):
                format_on_save(user, workspace, "html")

    def test_pinned_archive_identity_and_repacked_negative_cases(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.vsix"
            good = fixture()
            path.write_bytes(good)
            pin = digest(good)
            self.assertEqual(inspect_fixture(path.read_bytes(), pin), "synthetic.study-snippets@1.0.0")
            changed = fixture({**MANIFEST, "version": "2.0.0"})
            path.write_bytes(changed)
            with self.assertRaisesRegex(ValueError, "ARCHIVE_PIN"):
                inspect_fixture(path.read_bytes(), pin)
            # Even if a changed archive were re-pinned, its narrow contract must reject it.
            for manifest in ({**MANIFEST, "publisher": "other"},
                             {**MANIFEST, "version": "2.0.0"},
                             {**MANIFEST, "main": "./entry.js"},
                             {**MANIFEST, "extensionDependencies": ["other.demo"]},
                             {**MANIFEST, "capabilities": {"untrustedWorkspaces": {"supported": True}}}):
                data = fixture(manifest)
                with self.assertRaisesRegex(ValueError, "MANIFEST_CONTRACT"):
                    inspect_fixture(data, digest(data))
            for name in ("../escape.txt", "extension/package.json", "extension/entry.js"):
                data = fixture(extra=name)
                with self.assertRaisesRegex(ValueError, "ARCHIVE_ENTRIES"):
                    inspect_fixture(data, digest(data))
            self.assertEqual(list(Path(tmp).iterdir()), [path])  # nothing extracted

    def test_disable_is_not_rollback_and_drift_stops_restore(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            settings = root / "settings.json"
            extension = root / "synthetic-extension.zip"
            original = b'{"editor.formatOnSave": false}\n'
            changed = b'{"editor.formatOnSave": true}\n'
            settings.write_bytes(original)
            extension.write_bytes(fixture())
            # Explicit synthetic side effect, not actual extension activation.
            settings.write_bytes(changed)
            extension.unlink()  # removal of package does not restore settings
            self.assertFalse(extension.exists())
            self.assertEqual(settings.read_bytes(), changed)
            drift = b'{"editor.formatOnSave": true, "editor.tabSize": 2}\n'
            settings.write_bytes(drift)
            with self.assertRaisesRegex(ValueError, "DRIFT_STOP"):
                restore_owned_file(settings, changed, original)
            self.assertEqual(settings.read_bytes(), drift)
            # Simulate an explicitly reconciled, owned after-image, then restore bytes.
            settings.write_bytes(changed)
            restore_owned_file(settings, changed, original)
            self.assertEqual(settings.read_bytes(), original)
            self.assertEqual(list(root.iterdir()), [settings])


if __name__ == "__main__":
    unittest.main()
