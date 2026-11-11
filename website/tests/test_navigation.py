"""Check navigation and breadcrumbs in the generated static site.

Run after `python website/prepare.py && mkdocs build`.
"""

from html import unescape
from pathlib import Path
import re
import sys
import tempfile
import unittest
from urllib.parse import unquote, urljoin, urlsplit


SITE = Path(__file__).resolve().parents[2] / ".site-build" / "site"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hooks import make_tree  # noqa: E402

LANDING_PAGES = {
    "index.html", "series/index.html", "microarchitecture/index.html",
    "articles/index.html", "visuals/index.html",
}
ACTIVE_LINK = re.compile(r'<a\s+href="([^"]+)"\s+class="[^"]*\bmd-nav__link--active\b[^"]*"[^>]*>')
BREADCRUMB = re.compile(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', re.DOTALL)


def page_url(relative):
    directory = relative.parent.as_posix()
    return "https://example.test/" + ("" if directory == "." else directory + "/")


class GeneratedNavigationTests(unittest.TestCase):
    def test_ram_chapter_reading_lists_match_navigation(self):
        chapters = sorted((SITE / "RAM/wiki").glob("[0-9][0-9]-*/index.html"))
        self.assertGreater(len(chapters), 0)
        clean = lambda items: [(unescape(url), unescape(" ".join(label.split()))) for url, label in items]
        for chapter in chapters:
            with self.subTest(chapter=chapter.parent.name):
                html = chapter.read_text(encoding="utf-8")
                start = html.index('<div class="md-sidebar md-sidebar--primary"')
                end = html.index('<div class="md-sidebar md-sidebar--secondary"', start)
                primary = html[start:end]
                active = ACTIVE_LINK.search(primary)
                self.assertIsNotNone(active)
                section = re.search(r'<nav class="md-nav"[^>]*>.*?<ul class="md-nav__list"[^>]*>(.*?)</ul>', primary[active.end():], re.DOTALL)
                self.assertIsNotNone(section)
                nav_items = re.findall(r'<a\s+href="([^"]+)"[^>]*>\s*<span class="md-ellipsis">(.*?)</span>\s*</a>', section.group(1), re.DOTALL)
                reading_section = re.search(r'<h2\b[^>]*>[^<]*(?:阅读顺序|接下来怎么读).*?</h2>.*?<ol>(.*?)</ol>', html, re.DOTALL)
                self.assertIsNotNone(reading_section)
                reading_items = re.findall(r'<li>\s*<a href="([^"]+)">(.*?)</a>', reading_section.group(1), re.DOTALL)
                self.assertGreater(len(reading_items), 0)
                self.assertEqual(clean(nav_items), clean(reading_items))

        overview = (SITE / "RAM/wiki/01-overview/index.html").read_text(encoding="utf-8")
        self.assertIn('class="ram-calculation"', overview)
        self.assertIn('class="ram-event-sequence"', overview)

    def test_ram_sidebar_short_names_keep_full_article_titles(self):
        relative = Path("RAM/wiki/01-overview/problem-statement/index.html")
        html = (SITE / relative).read_text(encoding="utf-8")
        self.assertIn('title="为什么存储系统难设计？从一次读取看跨层约束"', html)
        self.assertIn('<span class="md-ellipsis">存储系统为何难设计</span>', html)
        self.assertIn('<h1 id="为什么存储系统难设计从一次读取看跨层约束">为什么存储系统难设计？从一次读取看跨层约束', html)

        start = html.index('<div class="md-sidebar md-sidebar--primary"')
        end = html.index('<div class="md-sidebar md-sidebar--secondary"', start)
        nav = re.findall(r'<a\s+href="([^"]+)"[^>]*>\s*<span class="md-ellipsis">(.*?)</span>\s*</a>', html[start:end], re.DOTALL)
        names = {urljoin(page_url(relative), unescape(href)): unescape(" ".join(label.split())) for href, label in nav}
        section = re.search(r'<h2 id="接下来怎么读".*?</h2>\s*<ul>(.*?)</ul>', html, re.DOTALL)
        self.assertIsNotNone(section)
        links = re.findall(r'<li>\s*<a href="([^"]+)">(.*?)</a>', section.group(1), re.DOTALL)
        self.assertGreater(len(links), 0)
        for href, label in links:
            self.assertEqual(names.get(urljoin(page_url(relative), unescape(href))), unescape(label))

    def test_numbered_reading_order_ignores_non_sibling_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chapter = root / "chapter"
            chapter.mkdir()
            for name in ("a.md", "b.md", "c.md"):
                (chapter / name).write_text("# Article\n", encoding="utf-8")
            (root / "outside.md").write_text("# Outside\n", encoding="utf-8")
            (chapter / "README.md").write_text(
                "# Chapter\n\n```md\n## 阅读顺序\n1. [ignored](./c.md)\n```\n\n"
                "## 阅读顺序\n\n1. [B](./b.md)\n2. [Outside](../outside.md)\n"
                "3. [A](./a.md)\n4. [B again](./b.md)\n5. [Missing](./missing.md)\n",
                encoding="utf-8",
            )
            self.assertEqual(
                make_tree(chapter, root),
                ["chapter/README.md", "chapter/b.md", "chapter/a.md", "chapter/c.md"],
            )

    def test_article_paths_and_distinct_parent_links(self):
        cases = {
            "RAM/wiki/01-overview/problem-statement/index.html": [
                "首页", "微架构", "专题", "RAM · 存储系统", "存储系统概览",
                "为什么存储系统难设计？从一次读取看跨层约束",
            ],
            "RAM/wiki/02-sram-foundations/6t-cell-bistable-storage/index.html": [
                "首页", "微架构", "专题", "RAM · 存储系统", "SRAM 基础",
                "6T SRAM cell：它如何保存、读取和写入 1 bit",
            ],
            "CPO/wiki/08-research/detailed-cards/cpo-status-challenges-solutions/index.html": [
                "首页", "微架构", "专题", "CPO · 光互连", "08 研究模板与术语",
                "完整论文卡", "完整卡：CPO status, challenges, and solutions",
            ],
            "electrical-timing-foundations/index.html": [
                "首页", "微架构", "基础", "从电荷到芯片时序：一条可手算的路径",
            ],
        }
        for filename, expected in cases.items():
            html = (SITE / filename).read_text(encoding="utf-8")
            breadcrumb = BREADCRUMB.search(html)
            self.assertIsNotNone(breadcrumb, filename)
            labels = re.findall(r'<(?:a\s[^>]*|span(?:\s[^>]*)?)>(.*?)</(?:a|span)>', breadcrumb.group(1))
            self.assertEqual([unescape(label) for label in labels], expected, filename)

        ram = (SITE / "RAM/wiki/02-sram-foundations/index.html").read_text(encoding="utf-8")
        fab = (SITE / "FAB/wiki/07-industry-map/index.html").read_text(encoding="utf-8")
        self.assertNotIn("<p>上级：", ram)
        self.assertIn("<p>上级:", fab)

    def test_current_navigation_and_breadcrumb_links(self):
        self.assertTrue(SITE.is_dir(), "Build the site before running this test")
        pages = sorted(p for p in SITE.rglob("*.html") if p.name != "404.html")
        self.assertGreater(len(pages), 1)
        errors = []
        for path in pages:
            relative = path.relative_to(SITE)
            html = path.read_text(encoding="utf-8")
            start = html.find('<div class="md-sidebar md-sidebar--primary"')
            end = html.find('<div class="md-sidebar md-sidebar--secondary"', start)
            primary = html[start:end] if start >= 0 and end >= 0 else ""
            active = list(ACTIVE_LINK.finditer(primary))
            if len(active) != 1 or 'aria-current="page"' not in active[0].group():
                errors.append(f"{relative}: expected one accessible current navigation link")
                continue
            current = urlsplit(urljoin(page_url(relative), unescape(active[0].group(1)))).path
            if current.rstrip("/") != urlsplit(page_url(relative)).path.rstrip("/"):
                errors.append(f"{relative}: current navigation link points to {current}")

            breadcrumbs = BREADCRUMB.findall(html)
            if relative.as_posix() in LANDING_PAGES:
                continue
            if len(breadcrumbs) != 1 or breadcrumbs[0].count('aria-current="page"') != 1:
                errors.append(f"{relative}: expected one breadcrumb with a current page")
                continue
            for href in re.findall(r'<a href="([^"]+)">', breadcrumbs[0]):
                target = urlsplit(urljoin(page_url(relative), unescape(href)))
                destination = SITE / unquote(target.path).lstrip("/")
                if destination.is_dir():
                    destination /= "index.html"
                if target.netloc != "example.test" or not destination.is_file():
                    errors.append(f"{relative}: broken breadcrumb link {href}")

        self.assertFalse(errors, "\n".join(errors[:30]))


if __name__ == "__main__":
    unittest.main()
