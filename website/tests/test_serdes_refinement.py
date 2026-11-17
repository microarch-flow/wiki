"""Check SerDes reader entries after the site is built."""

from html import unescape
import json
from pathlib import Path
import re
import sys
import unittest
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / ".site-build/site"
SOURCE = ROOT / "series/interconnect/SERDES"
sys.path.insert(0, str(ROOT / "website"))
from hooks import grouped_original_topics, reading_items  # noqa: E402
from ownership import INTERCONNECT  # noqa: E402


def location(source):
    path = source.relative_to(SOURCE)
    relative = path.parent.as_posix() if path.name == "README.md" else path.with_suffix("").as_posix()
    return "SERDES/wiki/" + ("" if relative == "." else relative + "/")


class SerdesReaderTests(unittest.TestCase):
    def test_reading_lists_cover_all_articles(self):
        chapters = sorted(path for path in SOURCE.iterdir()
                          if path.is_dir() and re.match(r"^\d\d-", path.name))
        self.assertEqual(len(chapters), 10)
        counts = []
        for chapter in chapters:
            items = reading_items(chapter)
            expected = {path.name for path in chapter.glob("*.md") if path.name != "README.md"}
            self.assertEqual({name for name, _ in items}, expected, chapter.name)
            self.assertEqual(len(items), len(expected), chapter.name)
            counts.append(len(items))
        self.assertEqual(sum(counts[:-1]), 48)
        self.assertEqual(counts[-1], 10)

        # These section labels are also the titles inside Material's mobile drawer.
        groups = grouped_original_topics(SITE.parent / "docs", INTERCONNECT)
        topic = next(group["高速电链路（SerDes）"] for group in groups if "高速电链路（SerDes）" in group)
        self.assertEqual([next(iter(section)) for section in topic[1:]], [
            "01 全局链路", "02 电信号与通道", "03 发送端", "04 接收端", "05 信号与指标",
            "06 初始化与训练", "07 设计与验证", "08 系统应用", "09 系统建模", "10 查阅与自测",
        ])

    def test_pages_keep_search_title_breadcrumb_and_current_navigation(self):
        search = json.loads((SITE / "search/search_index.json").read_text())["docs"]
        titles = {unquote(row["location"]): row["title"].replace("\u200b", "") for row in search}
        sources = list(SOURCE.rglob("*.md"))
        self.assertEqual(len(sources), 69)
        for source in sources:
            loc = location(source)
            page = (SITE / loc / "index.html").read_text()
            full = re.search(r"^# (.+)$", source.read_text(), re.M)[1]
            with self.subTest(page=loc):
                self.assertEqual(titles.get(loc), full)
                document_title = unescape(re.search(r"<title>(.*?)</title>", page, re.S)[1])
                self.assertTrue(document_title.startswith(full + " - "))
                breadcrumb = re.search(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', page, re.S)
                self.assertIsNotNone(breadcrumb)
                self.assertIn("芯片与系统互连", breadcrumb[1])
                self.assertIn(full, unescape(breadcrumb[1]))
                active = re.findall(r'<a\b(?=[^>]*class="[^\"]*md-nav__link--active)'
                                    r'(?=[^>]*href="([^\"]+)")[^>]*>', page)
                current = "https://example.test/" + loc
                self.assertTrue(any(urljoin(current, unescape(link)).split("#")[0] == current
                                    for link in active))

    def test_legacy_anchors_and_generated_links(self):
        fixture = json.loads((ROOT / "website/tests/fixtures/interconnect-legacy-anchors.json").read_text())
        legacy = {loc: anchors for loc, anchors in fixture.items() if loc.startswith("SERDES/")}
        self.assertEqual(len(legacy), 69)
        for loc, anchors in legacy.items():
            page = (SITE / loc / "index.html").read_text()
            article = re.search(r"<article\b[^>]*>(.*?)</article>", page, re.S)[1]
            ids = re.findall(r'\bid="([^\"]+)"', article)
            for anchor in anchors:
                self.assertEqual(ids.count(anchor), 1, (loc, anchor))

        for source in SOURCE.rglob("*.md"):
            loc = location(source)
            page = (SITE / loc / "index.html").read_text()
            article = re.search(r"<article\b[^>]*>(.*?)</article>", page, re.S)[1]
            for href in re.findall(r'href="([^\"]+)"', article):
                target = urlsplit(urljoin("https://example.test/" + loc, unescape(href)))
                if target.netloc != "example.test":
                    continue
                path = SITE / unquote(target.path).lstrip("/")
                if target.path.endswith("/") or path.is_dir():
                    path /= "index.html"
                with self.subTest(page=loc, href=href):
                    self.assertTrue(path.is_file(), path)
                    if target.fragment and path.suffix == ".html":
                        ids = re.findall(r'\bid="([^\"]+)"', path.read_text())
                        self.assertIn(unquote(target.fragment), ids)
