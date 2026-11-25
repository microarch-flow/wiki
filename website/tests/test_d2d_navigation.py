"""Check D2D knowledge-map coverage, navigation and existing page locations."""

from html import unescape
import json
from pathlib import Path
import posixpath
import re
import shutil
import sys
import tempfile
import unittest
from urllib.parse import unquote, urljoin


SITE = Path(__file__).resolve().parents[2] / ".site-build" / "site"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from d2d_navigation import D2D_HOME, D2D_READ_REDIRECT, D2D_SUMMARY, d2d_topic_tree, read_d2d_sections  # noqa: E402


def pages(item):
    if isinstance(item, str):
        return [item] if item.endswith(".md") else []
    if isinstance(item, dict):
        return [page for child in item.values() for page in pages(child)]
    if isinstance(item, list):
        return [page for child in item for page in pages(child)]
    return []


class D2dNavigationTests(unittest.TestCase):
    def test_groups_cover_pages_and_match_breadcrumbs_and_search(self):
        docs = SITE.parent / "docs"
        sections = read_d2d_sections(docs)
        self.assertEqual([(name, anchor) for name, anchor, _ in sections], [
            ("01 芯粒与连接基础", "foundations"), ("02 接口与案例", "interfaces"),
            ("03 系统集成与验证", "system-integration"),
            ("04 产品与系统案例", "product-cases"),
        ])
        topic = d2d_topic_tree(docs)
        expected = {path.relative_to(docs).as_posix() for path in (docs / "D2D/wiki").rglob("*.md")}
        actual = pages(topic)
        self.assertNotIn(D2D_READ_REDIRECT, actual)
        self.assertEqual(set(actual), expected - {D2D_READ_REDIRECT})
        self.assertEqual(len(actual), len(set(actual)))
        self.assertEqual(actual[:2], [D2D_HOME, D2D_SUMMARY])
        home = (docs / D2D_HOME).read_text(encoding="utf-8")
        reading = re.search(r"^## 阅读顺序\s*\n(.*?)(?=^## |\Z)", home, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(reading)
        home_items = re.findall(r"^\d+\.\s+\[([^\]]+)\]\(([^)]+)\)", reading.group(1), re.MULTILINE)
        home_items = [(label, posixpath.normpath(posixpath.join("D2D/wiki", path)))
                      for label, path in home_items]
        self.assertEqual(home_items, [entry for _name, _anchor, entries in sections for entry in entries])

        search = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))["docs"]
        locations = {unquote(entry["location"]) for entry in search}
        for group, anchor, entries in sections:
            for label, path in entries:
                with self.subTest(page=path):
                    source = (docs / path).read_text(encoding="utf-8")
                    up = re.search(r"^上级：([^\n]+)$", source, re.MULTILINE)
                    self.assertIsNotNone(up)
                    self.assertIn(f"#{anchor})", up.group(1))
                    page = Path(path).with_suffix("").as_posix()
                    html = (SITE / page / "index.html").read_text(encoding="utf-8")
                    page_title = re.search(r"<title>(.*?)</title>", html, re.DOTALL)
                    self.assertIsNotNone(page_title)
                    self.assertEqual(unescape(page_title.group(1)), source.splitlines()[0][2:] + " - 从硅到系统")
                    breadcrumb = re.search(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', html, re.DOTALL)
                    self.assertIsNotNone(breadcrumb)
                    self.assertIn(group, breadcrumb.group(1))
                    active = re.search(r'<a\s+href="([^"]+)"\s+class="[^"]*\bmd-nav__link--active\b[^"]*"[^>]*>', html)
                    self.assertIsNotNone(active)
                    current = "https://example.test/" + page + "/"
                    self.assertEqual(urljoin(current, unescape(active.group(1))), current)
                    self.assertIn(page + "/", locations)
                    self.assertIn(label, html)

    def test_merged_intro_preserves_old_section_links(self):
        page = Path(D2D_READ_REDIRECT).with_suffix("")
        old = (SITE / page / "index.html").read_text(encoding="utf-8")
        landing = re.search(r'<div [^>]*data-article-redirect[^>]*>(.*?)</div>', old, re.DOTALL)
        self.assertIsNotNone(landing)
        expected = {
            "一次跨芯粒通信怎样完成": "", "先约定一个读取": "先约定一次读取",
            "请求经过哪些边界": "read-path", "怎样判断已经完成": "return-wait",
            "为什么连接线接通还不够": "ready", "接下来怎么读": "next",
        }
        canonical = "https://example.test/D2D/wiki/ucie-pcie-read/"
        base = f"https://example.test/{page}/"
        new = (SITE / "D2D/wiki/ucie-pcie-read/index.html").read_text(encoding="utf-8")
        first = re.search(r'<a href="([^"]+)">', landing.group(1))
        self.assertEqual(urljoin(base, first.group(1)), canonical)
        routes = dict(re.findall(r'<li><span id="([^"]+)"></span>\s*<a href="([^"]+)">', landing.group(1)))
        self.assertEqual(routes.keys(), expected.keys())
        for old_id, target_id in expected.items():
            self.assertEqual(old.count(f'id="{old_id}"'), 1)
            if target_id:
                self.assertEqual(new.count(f'id="{target_id}"'), 1)
            self.assertEqual(unquote(urljoin(base, routes[old_id])), canonical + ("#" + target_id if target_id else ""))
        index = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))
        self.assertFalse(any(entry["location"].startswith(f"{page}/") for entry in index["docs"]))

    def test_unassigned_or_duplicate_article_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(SITE.parent / "docs/D2D/wiki", root / "D2D/wiki")
            extra = root / "D2D/wiki/extra.md"
            extra.write_text("# Extra\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "does not cover pages"):
                read_d2d_sections(root)
            extra.unlink()
            summary = root / D2D_SUMMARY
            with summary.open("a", encoding="utf-8") as out:
                out.write("\n- [重复](./ucie-pcie-read.md)\n")
            with self.assertRaisesRegex(ValueError, "Duplicate D2D navigation target"):
                read_d2d_sections(root)


if __name__ == "__main__":
    unittest.main()
