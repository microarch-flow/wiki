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
from d2d_navigation import D2D_HOME, D2D_SUMMARY, d2d_topic_tree, read_d2d_sections  # noqa: E402


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
        ])
        topic = d2d_topic_tree(docs)
        expected = {path.relative_to(docs).as_posix() for path in (docs / "D2D/wiki").rglob("*.md")}
        actual = pages(topic)
        self.assertEqual(set(actual), expected)
        self.assertEqual(len(actual), len(expected))
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
                    self.assertEqual(unescape(page_title.group(1)), source.splitlines()[0][2:] + " - 技术笔记")
                    breadcrumb = re.search(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', html, re.DOTALL)
                    self.assertIsNotNone(breadcrumb)
                    self.assertIn(group, breadcrumb.group(1))
                    active = re.search(r'<a\s+href="([^"]+)"\s+class="[^"]*\bmd-nav__link--active\b[^"]*"[^>]*>', html)
                    self.assertIsNotNone(active)
                    current = "https://example.test/" + page + "/"
                    self.assertEqual(urljoin(current, unescape(active.group(1))), current)
                    self.assertIn(page + "/", locations)
                    self.assertIn(label, html)

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
