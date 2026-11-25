"""Check Scaleup source-aligned navigation and legacy reader entry points."""

from html import unescape
import json
from pathlib import Path
import re
import sys
import unittest
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / ".site-build/site"
SOURCE = ROOT / "series/interconnect/SCALEUP"
sys.path.insert(0, str(ROOT / "website"))
from hooks import SCALEUP_PEER_REDIRECT, reading_items  # noqa: E402

PEER_ACCESS_OLD_URL = SCALEUP_PEER_REDIRECT.removesuffix(".md") + "/"


def location(source):
    path = source.relative_to(SOURCE)
    return "SCALEUP/wiki/" + (path.parent.as_posix() + "/" if path.name == "README.md"
                           else path.with_suffix("").as_posix() + "/").removeprefix("./")


class ScaleupNavigationTests(unittest.TestCase):
    def test_source_links_and_figure_resources(self):
        for source in SOURCE.rglob("*.md"):
            for href in re.findall(r'\]\(([^)]+)\)', source.read_text()):
                parsed = urlsplit(href)
                if parsed.scheme or not parsed.path:
                    continue
                self.assertTrue((source.parent / unquote(parsed.path)).resolve().is_file(), (source, href))
            page = (SITE / location(source) / "index.html").read_text()
            article = re.search(r'<article\b[^>]*>(.*?)</article>', page, re.S)[1]
            for tag in re.findall(r'<img\b[^>]*>', article):
                self.assertRegex(tag, r'alt="[^"]+"')
                src = re.search(r'src="([^"]+)"', tag)[1]
                target = urlsplit(urljoin("https://example.test/" + location(source), unescape(src)))
                self.assertTrue((SITE / unquote(target.path).lstrip("/")).is_file(), (source, src))

    def test_reading_lists_cover_all_articles(self):
        chapters = sorted(p for p in SOURCE.iterdir() if (p / "README.md").is_file())
        self.assertEqual(len(chapters), 6)
        self.assertEqual([len(reading_items(p)) for p in chapters], [3, 4, 4, 4, 5, 3])
        for chapter in chapters:
            items = reading_items(chapter)
            actual = [filename for filename, _ in items]
            expected = {p.name for p in chapter.glob("*.md")
                        if p.name != "README.md" and location(p) != PEER_ACCESS_OLD_URL}
            self.assertEqual(set(actual), expected, chapter.name)
            self.assertEqual(len(actual), len(expected))
            self.assertIn(f"]({chapter.name}/README.md)", (SOURCE / "README.md").read_text())

    def test_all_pages_search_breadcrumbs_and_current_navigation(self):
        search = json.loads((SITE / "search/search_index.json").read_text())["docs"]
        indexed = {unquote(row["location"]) for row in search}
        search_titles = {unquote(row["location"]): row["title"] for row in search}
        sources = list(SOURCE.rglob("*.md"))
        self.assertEqual(len(sources), 31)
        for source in sources:
            loc = location(source)
            page = (SITE / loc / "index.html").read_text()
            with self.subTest(page=loc):
                if loc == PEER_ACCESS_OLD_URL:
                    self.assertFalse(any(target.startswith(loc) for target in indexed))
                    continue
                self.assertIn(loc, indexed)
                full = re.search(r"^# (.+)$", source.read_text(), re.M)[1]
                # Chinese tokenization inserts zero-width word separators.
                self.assertEqual(search_titles[loc].replace("\u200b", ""), full)
                document_title = re.search(r"<title>(.*?)</title>", page, re.S)[1]
                self.assertTrue(unescape(document_title).startswith(full + " - "))
                crumb = re.search(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', page, re.S)
                self.assertIsNotNone(crumb)
                self.assertIn("芯片与系统互连", crumb[1])
                if loc != "SCALEUP/wiki/":
                    self.assertIn("加速器互连", crumb[1])
                links = re.findall(r'<a\b(?=[^>]*class="[^"]*md-nav__link--active)(?=[^>]*href="([^"]+)")[^>]*>', page)
                current = urljoin("https://example.test/" + loc, ".")
                self.assertTrue(any(urljoin(current, unescape(link)).split("#")[0] == current for link in links))
        for chapter in (p for p in SOURCE.iterdir() if (p / "README.md").is_file()):
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

    def test_peer_api_bookmarks_land_on_the_matching_sections(self):
        page = (SITE / PEER_ACCESS_OLD_URL / "index.html").read_text()
        menu = re.search(r'<div [^>]*data-article-redirect[^>]*>(.*?)</div>', page, re.S)
        self.assertIsNotNone(menu)
        links = re.findall(r'<li><span id="([^"]+)"></span>\s*<a href="([^"]+)">', menu[1])
        expected = {
            "cuda-与-hip-对端访问先查询能力再建立有效路径": "",
            "建立-a-访问-b-的方向": "peer-access",
            "访问成功以后仍需验证什么": "ready",
            "内核访问与搬运引擎不是同一实验": "copy",
        }
        self.assertEqual([key for key, _ in links], list(expected))
        canonical = "/SCALEUP/wiki/01-access-semantics/address-mapping-and-permissions/"
        for key, href in links:
            target = urlsplit(urljoin("https://example.test/" + PEER_ACCESS_OLD_URL, unescape(href)))
            self.assertEqual((target.path, target.fragment), (canonical, expected[key]))
            self.assertEqual(page.count(f'id="{key}"'), 1)

    def test_legacy_ids_are_unique_and_local_article_links_resolve(self):
        fixture = json.loads((ROOT / "website/tests/fixtures/interconnect-legacy-anchors.json").read_text())
        for loc, expected in fixture.items():
            if not loc.startswith("SCALEUP/"):
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
