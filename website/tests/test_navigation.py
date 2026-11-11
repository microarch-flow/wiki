"""Check navigation and breadcrumbs in the generated static site.

Run after `python website/prepare.py && mkdocs build`.
"""

from html import unescape
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urljoin, urlsplit


SITE = Path(__file__).resolve().parents[2] / ".site-build" / "site"
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
    def test_article_paths_and_distinct_parent_links(self):
        cases = {
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
