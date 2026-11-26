"""Check the normal training entrances and the shared working structure."""
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "docs/AGENT_CAPABILITY_TRAINING.md"
WORKSPACE = ROOT / "docs/training/工作區"
BRIEFS = ROOT / "docs/training/任務書"
LINK = re.compile(r"\[[^\]\n]+\]\(([^)\s]+)\)")


def local_targets(page, markdown):
    for href in LINK.findall(markdown):
        url = urlsplit(href)
        if not url.scheme and not url.netloc and url.path:
            yield (page.parent / unquote(url.path)).resolve()


class TrainingNavigationTests(unittest.TestCase):
    def test_both_entrances_open_the_canonical_training_manual(self):
        for filename in ("START_HERE.md", "AGENTS.md"):
            page = ROOT / filename
            with self.subTest(page=filename):
                first_link = next(local_targets(page, page.read_text(encoding="utf-8")))
                self.assertEqual(first_link, MASTER)

    def test_current_work_points_to_one_existing_brief(self):
        manual = MASTER.read_text(encoding="utf-8")
        current_sections = re.findall(
            r"^## 目前工作\s*\n(.*?)(?=^## |\Z)", manual, re.M | re.S
        )
        self.assertEqual(len(current_sections), 1)
        briefs = {path for path in local_targets(MASTER, current_sections[0])
                  if path.is_relative_to(BRIEFS)}
        self.assertEqual(len(briefs), 1)
        brief = briefs.pop()
        self.assertTrue(brief.is_file())
        for target in local_targets(brief, brief.read_text(encoding="utf-8")):
            self.assertTrue(target.exists(), target)

    def test_ten_work_areas_are_reachable_and_point_to_existing_sources(self):
        areas = sorted(path for path in WORKSPACE.iterdir() if path.is_dir())
        self.assertEqual([area.name.split("_", 1)[0] for area in areas],
                         [f"{n:02}" for n in range(1, 11)])
        targets = set(local_targets(MASTER, MASTER.read_text(encoding="utf-8")))
        for area in areas:
            page = area / "README.md"
            with self.subTest(area=area.name):
                self.assertIn(page, targets)
                sources = list(local_targets(page, page.read_text(encoding="utf-8")))
                self.assertTrue(sources)
                for source in sources:
                    self.assertTrue(source.exists(), source)
