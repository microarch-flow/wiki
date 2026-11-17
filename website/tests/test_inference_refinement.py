"""Validate the complete inference publication and legacy compatibility contract."""

from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "website"))
from inference import CHAPTERS, MOVES, PREFIX, navigation, public_path

SOURCE = ROOT / PREFIX
SITE = ROOT / ".site-build/site"
DOCS = ROOT / ".site-build/docs"
BASE = json.loads((ROOT / "website/tests/fixtures/inference-legacy.json").read_text())["pages"]


class Elements(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = []
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == "id":
                self.ids.append(value)
            if tag == "a" and key == "href":
                self.links.append(value)


def article(path):
    return re.search(r"<article\b[^>]*>(.*?)</article>", path.read_text(), re.S)[1]


def location(source):
    path = Path(public_path(source))
    return (path.parent.as_posix() if path.name == "README.md" else path.with_suffix("").as_posix()) + "/"


class InferenceRefinementTests(unittest.TestCase):
    def test_all_legacy_urls_and_277_dom_anchors_survive_once(self):
        self.assertEqual(len(BASE), 18)
        self.assertEqual(sum(len(page["ids"]) for page in BASE.values()), 277)
        for old, page in BASE.items():
            with self.subTest(source=old):
                target = SITE / page["path"] / "index.html"
                self.assertTrue(target.is_file())
                ids = Elements(article(target)).ids
                for anchor in page["ids"]:
                    self.assertEqual(ids.count(anchor), 1, (old, anchor))

    def test_guides_own_order_labels_and_complete_navigation(self):
        tree = navigation(DOCS)
        self.assertEqual(len(tree), 11)
        self.assertEqual([next(iter(group)) for group in tree[1:-1]], [label for label, _ in CHAPTERS])
        pages = [tree[0]]
        for label, directory in CHAPTERS:
            guide = SOURCE / directory / "README.md"
            links = re.findall(r"^\d+\. \[([^]]+)\]\(([^)]+)\)", guide.read_text(), re.M)
            entries = next(group[label] for group in tree[1:] if label in group)
            self.assertEqual(len(entries), len(links)+1)
            pages.append(entries[0])
            for entry, (short, target) in zip(entries[1:], links):
                self.assertEqual(entry, {short: public_path(f"{directory}/{target}")})
                pages.extend(entry.values())
        pages.extend(tree[-1]["术语与约定"])
        self.assertEqual(len(pages), 41)
        self.assertEqual(len(set(pages)), 41)
        self.assertEqual(len(list(SOURCE.rglob("*.md"))), 41)

    def test_every_page_search_canonical_breadcrumbs_and_internal_links(self):
        entries = json.loads((SITE / "search/search_index.json").read_text())["docs"]
        indexed = {unquote(e["location"]): e["title"].replace("\u200b", "") for e in entries}
        for source in SOURCE.rglob("*.md"):
            relative = source.relative_to(SOURCE).as_posix()
            loc = location(relative)
            path = SITE / loc / "index.html"
            full = re.search(r"^# (.+)$", source.read_text(), re.M)[1]
            with self.subTest(source=relative):
                html = path.read_text()
                self.assertEqual(indexed[loc], full)
                self.assertIn(f'<link rel="canonical" href="https://microarch-flow.github.io/wiki/{loc}">', html)
                crumb = re.search(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', html, re.S)[1]
                self.assertIn("推理运行时", unescape(crumb))
                if "/" in relative:
                    label = dict((directory, label) for label, directory in CHAPTERS)[relative.split("/")[0]]
                    self.assertIn(label, unescape(crumb))
                body = article(path)
                elements = Elements(body)
                self.assertEqual(len(elements.ids), len(set(elements.ids)), relative)
                self.assertNotIn("上级：", body)
                for href in elements.links:
                    url = urlsplit(urljoin("https://example.test/"+loc, href))
                    if url.netloc != "example.test":
                        continue
                    target = SITE / unquote(url.path).lstrip("/")
                    if target.is_dir():
                        target /= "index.html"
                    self.assertTrue(target.is_file(), (loc, href))
                    if url.fragment:
                        self.assertIn(unquote(url.fragment), Elements(target.read_text()).ids, (loc, href))

    def test_source_links_and_single_public_location(self):
        for source in SOURCE.rglob("*.md"):
            text = re.sub(r"~~~.*?~~~|```.*?```", "", source.read_text(), flags=re.S)
            for raw in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
                url = urlsplit(raw)
                if not url.scheme and not url.netloc and url.path:
                    self.assertTrue((source.parent / unquote(url.path)).resolve().exists(), (source, raw))
        for current, old in MOVES.items():
            self.assertTrue((SOURCE / current).is_file())
            self.assertFalse((SOURCE / old).exists())
            self.assertTrue((DOCS / PREFIX / old).is_file())
            self.assertFalse((DOCS / PREFIX / current).exists())

    def test_navigation_rejects_unlisted_duplicate_and_wrong_chapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(DOCS / PREFIX, root / PREFIX)
            extra = root / PREFIX / "unlisted.md"
            extra.write_text("# Unlisted")
            with self.assertRaisesRegex(ValueError, "coverage"):
                navigation(root)
            extra.unlink()
            guide = root / PREFIX / CHAPTERS[0][1] / "README.md"
            original = guide.read_text()
            guide.write_text(original+"\n## 阅读顺序\n\n1. [重复](../topics/01-prefill-decode.md)\n")
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                navigation(root)
            guide.write_text(original+"\n## 阅读顺序\n\n1. [错误归属](../topics/06-paged-kv-cache.md)\n")
            with self.assertRaisesRegex(ValueError, "outside chapter"):
                navigation(root)

    def test_numerical_and_event_examples(self):
        result = subprocess.run(
            [sys.executable, str(SOURCE / "examples/verify_examples.py")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertIn("Ran 9 tests", result.stderr)


if __name__ == "__main__":
    unittest.main()
