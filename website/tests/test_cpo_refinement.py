"""Check CPO reading order, published paths, search, and legacy anchors."""

from collections import Counter
from functools import lru_cache
from html import unescape
import json
from pathlib import Path
import re
import sys
import unittest
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / ".site-build/site"
DOCS = ROOT / ".site-build/docs"
SOURCE = ROOT / "series/interconnect/CPO"
sys.path.insert(0, str(ROOT / "website"))
from hooks import grouped_original_topics, make_tree, reading_items  # noqa: E402
from ownership import INTERCONNECT  # noqa: E402

OLD_DEVICES = "CPO/wiki/04-optical-engine/laser-modulator-detector.md"
OLD_ROADMAP = "CPO/wiki/01-overview/learning-roadmap.md"
REDIRECTS = {OLD_DEVICES, OLD_ROADMAP}


def location(source):
    path = source.relative_to(SOURCE)
    relative = path.parent.as_posix() if path.name == "README.md" else path.with_suffix("").as_posix()
    return "CPO/wiki/" + ("" if relative == "." else relative + "/")


@lru_cache(maxsize=None)
def read_page(path):
    return path.read_text(encoding="utf-8")


def article(page):
    return re.search(r"<article\b[^>]*>(.*?)</article>", page, re.S)[1]


def all_paths(tree):
    if isinstance(tree, str):
        return [tree]
    if isinstance(tree, dict):
        return [path for value in tree.values() for path in all_paths(value)]
    return [path for value in tree for path in all_paths(value)]


class CpoRefinementTests(unittest.TestCase):
    def test_groups_cover_every_page_once_and_lists_set_order(self):
        sources = list(SOURCE.rglob("*.md"))
        self.assertEqual(len(sources), 101)
        groups = grouped_original_topics(DOCS, INTERCONNECT)
        topic = next(group["共封装光学（CPO）"] for group in groups if "共封装光学（CPO）" in group)
        self.assertEqual([next(iter(section)) for section in topic[2:]],
                         ["技术与工程", "产业与公司", "学习与查阅", "维护与模板"])
        paths = all_paths(topic)
        expected = {p.relative_to(DOCS).as_posix() for p in (DOCS / "CPO/wiki").rglob("*.md")}
        expected -= REDIRECTS
        self.assertEqual(set(paths), expected)
        self.assertEqual(len(paths), len(expected))

        chapters = [p.parent for p in SOURCE.rglob("README.md") if p.parent != SOURCE]
        self.assertEqual(len(chapters), 24)
        for chapter in chapters:
            listed = [name for name, _ in reading_items(chapter, include_subdirs=True)]
            siblings = {p.name for p in chapter.glob("*.md")
                        if p.name != "README.md" and f"CPO/wiki/{p.relative_to(SOURCE)}" not in REDIRECTS}
            children = {p.name for p in chapter.iterdir() if p.is_dir() and (p / "README.md").is_file()}
            self.assertEqual(set(listed), siblings | children, chapter)
            self.assertEqual(len(listed), len(siblings | children), chapter)
            staged = DOCS / "CPO/wiki" / chapter.relative_to(SOURCE)
            tree = make_tree(staged, DOCS, include=lambda p: p.relative_to(DOCS).as_posix() not in REDIRECTS)[1:]
            displayed = []
            for item in tree:
                if isinstance(item, str):
                    displayed.append(Path(item).name)
                else:
                    displayed.append(Path(all_paths(item)[0]).parent.name)
            self.assertEqual(displayed, listed, chapter)

        research = SOURCE / "08-research"
        self.assertEqual([name for name, _ in reading_items(research, include_subdirs=True)][4:6],
                         ["paper-cards", "detailed-cards"])

    def test_pages_have_search_title_breadcrumb_and_current_navigation(self):
        search = json.loads((SITE / "search/search_index.json").read_text())["docs"]
        titles = {unquote(row["location"]): row["title"].replace("\u200b", "") for row in search}
        by_location = {unquote(row["location"]): row for row in search}
        # Breadcrumbs are present in the page, but must not occupy its search excerpt.
        excerpt = by_location["CPO/wiki/"]["text"].replace("\u200b", "")
        self.assertIn("光引擎", excerpt)
        self.assertNotIn("<ol>", excerpt)
        for source in SOURCE.rglob("*.md"):
            loc = location(source)
            page = read_page(SITE / loc / "index.html")
            full = re.search(r"^# (.+)$", source.read_text(), re.M)[1]
            with self.subTest(page=loc):
                if f"CPO/wiki/{source.relative_to(SOURCE)}" in REDIRECTS:
                    self.assertFalse(any(key.startswith(loc) for key in titles))
                    continue
                self.assertEqual(titles.get(loc), full)
                self.assertTrue(unescape(re.search(r"<title>(.*?)</title>", page, re.S)[1]).startswith(full + " - "))
                crumb = re.search(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', page, re.S)
                self.assertIsNotNone(crumb)
                self.assertIn("芯片与系统互连", crumb[1])
                self.assertIn(full, unescape(crumb[1]))
                active = re.findall(r'<a\b(?=[^>]*class="[^"]*md-nav__link--active)'
                                    r'(?=[^>]*href="([^"]+)")[^>]*>', page)
                current = "https://example.test/" + loc
                self.assertTrue(any(urljoin(current, unescape(link)).split("#")[0] == current for link in active))

        manufacturing = read_page(SITE / "CPO/wiki/06-manufacturing/index.html")
        self.assertIn('<span class="md-ellipsis">KGD 与良率</span>', manufacturing)
        self.assertIn('title="KGD、装配良率与系统良率"', manufacturing)

    def test_redirect_each_old_section_to_the_part_that_replaces_it(self):
        fixture = json.loads((ROOT / "website/tests/fixtures/interconnect-legacy-anchors.json").read_text())
        targets = {
            OLD_DEVICES: ("CPO/wiki/04-optical-engine/optical-link-basics/",
                          ["electrical", "modulation", "modulation", "receiver", "receiver", "tradeoffs"]),
            OLD_ROADMAP: ("CPO/wiki/16-learning-navigation/study-navigation/",
                          ["start", "first", "first", "first", "engineering", "engineering", "engineering",
                           "industry", "boundaries", "boundaries", "boundaries", "boundaries", "boundaries"]),
        }
        for path, (destination, sections) in targets.items():
            loc = path.removesuffix(".md")
            page = read_page(SITE / loc / "index.html")
            menu = re.search(r'<div [^>]*data-article-redirect[^>]*>(.*?)</div>', page, re.S)[1]
            links = re.findall(r'<li><span id="([^"]+)"></span>\s*<a href="([^"]+)">', menu)
            self.assertEqual([anchor for anchor, _ in links], fixture[loc])
            for (_anchor, url), section in zip(links, sections, strict=True):
                self.assertEqual(urljoin(f"https://example.test/{loc}/", unescape(url)),
                                 f"https://example.test/{destination}#{section}")

    def test_old_anchors_and_generated_article_links(self):
        fixture = json.loads((ROOT / "website/tests/fixtures/interconnect-legacy-anchors.json").read_text())
        legacy = {loc: anchors for loc, anchors in fixture.items() if loc.startswith("CPO/")}
        self.assertEqual(len(legacy), 101)
        for loc, anchors in legacy.items():
            ids = Counter(re.findall(r'\bid="([^"]+)"', article(read_page(SITE / loc / "index.html"))))
            for anchor in anchors:
                self.assertEqual(ids[anchor], 1, (loc, anchor))

        for source in SOURCE.rglob("*.md"):
            loc = location(source)
            body = article(read_page(SITE / loc / "index.html"))
            for href in re.findall(r'href="([^"]+)"', body):
                target = urlsplit(urljoin("https://example.test/" + loc, unescape(href)))
                if target.netloc != "example.test":
                    continue
                path = SITE / unquote(target.path).lstrip("/")
                if target.path.endswith("/") or path.is_dir():
                    path /= "index.html"
                self.assertTrue(path.is_file(), (loc, href))
                if target.fragment and path.suffix == ".html":
                    self.assertIn(unquote(target.fragment),
                                  re.findall(r'\bid="([^"]+)"', read_page(path)), (loc, href))


if __name__ == "__main__":
    unittest.main()
