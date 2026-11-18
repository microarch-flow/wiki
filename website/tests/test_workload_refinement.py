"""Verify Workload source moves, all legacy anchors, navigation and search."""

from html import unescape
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from urllib.parse import unquote, urljoin, urlsplit

import markdown

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "website"))
from workload import CHAPTERS, MOVES, PREFIX, navigation, public_path, stage_workload
from ownership import workload_owner
from stage_links import PublishedPaths
from inference_math import on_page_markdown, InferenceMathExtension

SOURCE = ROOT / "series/workload"
SITE = ROOT / ".site-build/site"
DOCS = ROOT / ".site-build/docs"
BASE = json.loads((ROOT / "website/tests/fixtures/workload-legacy.json").read_text())["pages"]
PRIOR_IDS = json.loads((ROOT / "website/tests/fixtures/workload-foundation-anchors.json").read_text())["additional_ids"]


def location(path):
    path = Path(public_path(path))
    return (path.parent.as_posix() if path.name == "README.md" else path.with_suffix("").as_posix()) + "/"


def content(path):
    return re.search(r"<article\b[^>]*>(.*?)</article>", path.read_text(), re.S)[1]


class WorkloadRefinementTests(unittest.TestCase):
    def test_all_legacy_paths_and_anchors_survive_once(self):
        self.assertEqual(len(BASE), 70)
        self.assertEqual(sum(len(page["ids"]) for page in BASE.values()), 610)
        for old, page in BASE.items():
            with self.subTest(source=old):
                target = SITE / page["path"] / "index.html"
                self.assertTrue(target.is_file())
                ids = re.findall(r'\bid="([^"]+)"', content(target))
                for anchor in page["ids"]:
                    self.assertEqual(ids.count(anchor), 1, (old, anchor))

    def test_navigation_matches_all_twelve_source_guides(self):
        tree = navigation(DOCS)
        self.assertEqual(len(tree), 13)
        self.assertEqual([next(iter(group)) for group in tree[1:]], [label for label, _ in CHAPTERS])
        self.assertEqual(len(list(SOURCE.rglob("*.md"))), 86)
        series_map = re.findall(r"^\| \[([^]]+)\]\(([^/]+)/README.md\)", (SOURCE / "README.md").read_text(), re.M)
        self.assertEqual(series_map, list(CHAPTERS))
        for label, directory in CHAPTERS:
            guide = SOURCE / directory / "README.md"
            regular, _, archive = guide.read_text().partition("## 历史入口")
            pattern = r"^\d+\. \[([^]]+)\]\(([^)]+)\)"
            reading = re.findall(pattern, regular, re.M)
            history = re.findall(pattern, archive, re.M)
            links = reading + history
            entries = next(group[label] for group in tree[1:] if label in group)
            expected = [{short: public_path(f"{directory}/{target}")} for short, target in reading]
            if history:
                expected.append({"历史入口": [
                    {short: public_path(f"{directory}/{target}")} for short, target in history
                ]})
            self.assertEqual(entries[1:], expected)
            for short, target in links:
                self.assertEqual((short, target) in history, "exclude: true" in (guide.parent / target).read_text())
            page = (SITE / location(guide.relative_to(SOURCE)) / "index.html").read_text()
            primary = page.split('<div class="md-sidebar md-sidebar--primary"', 1)[1].split('<div class="md-sidebar md-sidebar--secondary"', 1)[0]
            positions = []
            for short, target in links:
                loc = location(f"{directory}/{target}")
                matches = [(m.start(), unescape(m[2])) for m in re.finditer(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', primary, re.S)
                           if urlsplit(urljoin("https://example.test/" + location(guide.relative_to(SOURCE)), unescape(m[1]))).path == "/" + loc]
                self.assertEqual(len(matches), 1, loc)
                self.assertIn(short, matches[0][1])
                positions.append(matches[0][0])
            self.assertEqual(positions, sorted(positions))

    def test_headings_published_after_the_first_reconstruction(self):
        self.assertEqual(len(PRIOR_IDS), 86)
        self.assertEqual(sum(map(len, PRIOR_IDS.values())), 451)
        for path, anchors in PRIOR_IDS.items():
            with self.subTest(page=path):
                ids = re.findall(r'\bid="([^"]+)"', content(SITE / PREFIX / path / "index.html"))
                for anchor in anchors:
                    self.assertEqual(ids.count(anchor), 1, (path, anchor))

    def test_search_titles_breadcrumbs_and_article_links(self):
        entries = json.loads((SITE / "search/search_index.json").read_text())["docs"]
        indexed = {unquote(e["location"]): e["title"].replace("\u200b", "") for e in entries}
        excluded = 0
        for source in SOURCE.rglob("*.md"):
            relative = source.relative_to(SOURCE).as_posix()
            text = source.read_text()
            loc = location(relative)
            path = SITE / loc / "index.html"
            html = path.read_text()
            full = re.search(r"^# (.+)$", text, re.M)[1]
            with self.subTest(page=relative):
                if "exclude: true" in text:
                    excluded += 1
                    self.assertFalse(any(key == loc or key.startswith(loc + "#") for key in indexed), loc)
                else:
                    self.assertEqual(indexed[loc], full)
                self.assertIn(f'<link rel="canonical" href="https://microarch-flow.github.io/wiki/{loc}">', html)
                crumb = re.search(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', html, re.S)[1]
                if relative != "README.md":
                    self.assertIn(workload_owner(relative), unescape(crumb))
                self.assertEqual("历史入口</span>" in crumb, "exclude: true" in text)
                article = content(path)
                self.assertNotIn("上级：", article)
                ids = re.findall(r'\bid="([^"]+)"', article)
                self.assertEqual(len(ids), len(set(ids)), loc)
                self.assertNotIn("</invoke>", article)
                for href in re.findall(r'href="([^"]+)"', article):
                    url = urlsplit(urljoin("https://example.test/" + loc, unescape(href)))
                    if url.netloc != "example.test":
                        continue
                    target = SITE / unquote(url.path).lstrip("/")
                    if target.is_dir():
                        target /= "index.html"
                    self.assertTrue(target.is_file(), (loc, href))
                    if url.fragment:
                        self.assertIn(unquote(url.fragment), re.findall(r'\bid="([^"]+)"', target.read_text()), (loc, href))
        self.assertEqual(excluded, 7)

    def test_source_links_and_mapped_pages_have_single_public_location(self):
        for source in SOURCE.rglob("*.md"):
            text = re.sub(r"```.*?```", "", source.read_text(), flags=re.S)
            for raw in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
                url = urlsplit(raw)
                if not url.scheme and not url.netloc and url.path:
                    self.assertTrue((source.parent / unquote(url.path)).resolve().exists(), (source, raw))
        for current, old in MOVES.items():
            self.assertTrue((SOURCE / current).is_file())
            self.assertFalse((SOURCE / old).exists())
            self.assertEqual(workload_owner(current), workload_owner(old))
            self.assertTrue((DOCS / PREFIX / old).is_file())
            self.assertFalse((DOCS / PREFIX / current).exists())

    def test_moves_rewrite_new_and_old_source_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "series/workload"
            source.mkdir(parents=True)
            (source / "README.md").write_text("# Home\n[old](01-foundation-model-components/contrastive-learning.md)\n[new](learning-objectives/contrastive-learning.md)\n")
            moved = source / "learning-objectives/contrastive-learning.md"
            moved.parent.mkdir()
            moved.write_text("# Contrastive\n[home](../README.md)\n")
            docs = root / "docs"
            published = PublishedPaths(root, docs)
            stage_workload(source, docs / PREFIX, published)
            published.rewrite()
            home = (docs / PREFIX / "README.md").read_text()
            self.assertEqual(home.count("(01-foundation-model-components/contrastive-learning.md)"), 2)
            self.assertIn("(../README.md)", (docs / PREFIX / MOVES["learning-objectives/contrastive-learning.md"]).read_text())
            # An accidental second source for a preserved URL must fail.
            collision = source / MOVES["learning-objectives/contrastive-learning.md"]
            collision.parent.mkdir()
            collision.write_text("# Collision")
            with self.assertRaisesRegex(ValueError, "collision"):
                stage_workload(source, root / "other", PublishedPaths(root, root / "other"))

    def test_navigation_rejects_unlisted_and_duplicate_articles(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(DOCS / PREFIX, root / PREFIX)
            extra = root / PREFIX / "unlisted.md"
            extra.write_text("# Unlisted")
            with self.assertRaisesRegex(ValueError, "coverage"):
                navigation(root)
            extra.unlink()
            guide = root / PREFIX / "00-overview/README.md"
            guide.write_text(guide.read_text() + "\n## 阅读顺序\n\n1. [重复](glossary.md)\n")
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                navigation(root)

    def test_workload_math_is_scoped_and_uses_rendered_formulas(self):
        page = SimpleNamespace(file=SimpleNamespace(src_uri=PREFIX + "/00-overview/tensor-shapes-and-cost.md"))
        text = on_page_markdown("Example $2MKN$ and `x$1`.", page)
        rendered = markdown.markdown(text, extensions=[InferenceMathExtension()])
        self.assertIn('class="arithmatex"', rendered)
        self.assertIn("<code>x$1</code>", rendered)
        html = content(SITE / location("00-overview/tensor-shapes-and-cost.md") / "index.html")
        self.assertIn('class="arithmatex"', html)
        self.assertIn(r"\[", html)


if __name__ == "__main__":
    unittest.main()
