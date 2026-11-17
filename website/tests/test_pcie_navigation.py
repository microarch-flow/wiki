"""Check PCIe source-aligned navigation and legacy reader entry points."""

from html import unescape
import json
from pathlib import Path
import re
import sys
import unittest
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / ".site-build/site"
SOURCE = ROOT / "series/interconnect/PCIE"
sys.path.insert(0, str(ROOT / "website"))
from hooks import reading_items  # noqa: E402


def location(source):
    path = source.relative_to(SOURCE)
    return "PCIE/wiki/" + (path.parent.as_posix() + "/" if path.name == "README.md"
                           else path.with_suffix("").as_posix() + "/").removeprefix("./")


class PCIeNavigationTests(unittest.TestCase):
    def test_reading_lists_and_map_cover_all_articles(self):
        chapters = sorted(p for p in SOURCE.iterdir() if p.is_dir())
        self.assertEqual(len(chapters), 8)
        summary = (SOURCE / "SUMMARY.md").read_text()
        for chapter in chapters:
            items = reading_items(chapter)
            actual = [filename for filename, _ in items]
            expected = {p.name for p in chapter.glob("*.md") if p.name != "README.md"}
            self.assertEqual(set(actual), expected, chapter.name)
            self.assertEqual(len(actual), len(expected))
            for filename in actual:
                self.assertIn(f"]({chapter.name}/{filename})", summary)
        self.assertEqual(reading_items(SOURCE / "04-data-path-dma-interrupts")[0][0],
                         "host-memory-pinned-buffer-visibility.md")
        self.assertEqual(reading_items(SOURCE / "02-link-transaction-basics")[3][0],
                         "credit-flow-control-and-replay.md")

    def test_all_pages_search_breadcrumbs_and_current_navigation(self):
        search = json.loads((SITE / "search/search_index.json").read_text())["docs"]
        indexed = {unquote(row["location"]) for row in search}
        search_titles = {unquote(row["location"]): row["title"] for row in search}
        sources = list(SOURCE.rglob("*.md"))
        self.assertEqual(len(sources), 48)
        for source in sources:
            loc = location(source)
            page = (SITE / loc / "index.html").read_text()
            with self.subTest(page=loc):
                self.assertIn(loc, indexed)
                full = re.search(r"^# (.+)$", source.read_text(), re.M)[1]
                # Chinese tokenization inserts zero-width word separators.
                self.assertEqual(search_titles[loc].replace("\u200b", ""), full)
                document_title = re.search(r"<title>(.*?)</title>", page, re.S)[1]
                self.assertTrue(unescape(document_title).startswith(full + " - "))
                crumb = re.search(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', page, re.S)
                self.assertIsNotNone(crumb)
                self.assertIn("芯片与系统互连", crumb[1])
                if loc != "PCIE/wiki/":
                    self.assertIn("系统 I/O 互连（PCIe）", crumb[1])
                links = re.findall(r'<a\b(?=[^>]*class="[^"]*md-nav__link--active)(?=[^>]*href="([^"]+)")[^>]*>', page)
                current = urljoin("https://example.test/" + loc, ".")
                self.assertTrue(any(urljoin(current, unescape(link)).split("#")[0] == current for link in links))
        for chapter in (p for p in SOURCE.iterdir() if p.is_dir()):
            page = (SITE / location(chapter / "README.md") / "index.html").read_text()
            positions = []
            for filename, short in reading_items(chapter):
                full = re.search(r"^# (.+)$", (chapter / filename).read_text(), re.M)[1]
                # Labels have both a compact visible form and full-title tooltip.
                self.assertIn(f'title="{full}"', unescape(page))
                link = re.search(r'<a\b(?=[^>]*\bmd-nav__link\b)(?=[^>]*href="' +
                                 re.escape(Path(filename).stem) + r'/")[^>]*>(.*?)</a>', page, re.S)
                self.assertIsNotNone(link, (chapter.name, filename))
                self.assertIn(short, unescape(link[1]))
                positions.append(link.start())
            self.assertEqual(positions, sorted(positions), chapter.name)

    def test_legacy_ids_are_unique_and_local_article_links_resolve(self):
        fixture = json.loads((ROOT / "website/tests/fixtures/interconnect-legacy-anchors.json").read_text())
        for loc, expected in fixture.items():
            if not loc.startswith("PCIE/"):
                continue
            page = (SITE / loc / "index.html").read_text()
            article = re.search(r'<article\b[^>]*>(.*?)</article>', page, re.S)[1]
            ids = re.findall(r'\bid="([^"]+)"', article)
            for anchor in expected:
                self.assertEqual(ids.count(anchor), 1, (loc, anchor))
        for source in SOURCE.rglob("*.md"):
            loc = location(source)
            page = (SITE / loc / "index.html").read_text()
            article = re.search(r'<article\b[^>]*>(.*?)</article>', page, re.S)[1]
            for href in re.findall(r'href="([^"]+)"', article):
                parsed = urlsplit(urljoin("https://example.test/" + loc, unescape(href)))
                if parsed.netloc != "example.test":
                    continue
                target = SITE / unquote(parsed.path).lstrip("/")
                if parsed.path.endswith("/"):
                    target /= "index.html"
                self.assertTrue(target.is_file(), (loc, href))
                if parsed.fragment and target.suffix == ".html":
                    ids = re.findall(r'\bid="([^"]+)"', target.read_text())
                    self.assertIn(unquote(parsed.fragment), ids, (loc, href))


if __name__ == "__main__":
    unittest.main()
