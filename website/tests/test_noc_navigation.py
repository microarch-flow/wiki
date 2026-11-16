"""Check the NoC reading groups and preserved public pages after a site build."""

from html import unescape
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
from urllib.parse import unquote, urljoin


SITE = Path(__file__).resolve().parents[2] / ".site-build" / "site"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hooks import grouped_original_topics  # noqa: E402
from noc_navigation import NOC_SECTIONS, read_noc_sections  # noqa: E402
from ownership import INTERCONNECT  # noqa: E402


def pages(item):
    if isinstance(item, str):
        return [item] if item.endswith(".md") else []
    if isinstance(item, dict):
        return [page for child in item.values() for page in pages(child)]
    if isinstance(item, list):
        return [page for child in item for page in pages(child)]
    return []


class NocNavigationTests(unittest.TestCase):
    def test_groups_cover_existing_pages_once_and_match_breadcrumbs(self):
        docs = SITE.parent / "docs"
        sections, legacy = read_noc_sections(docs)
        self.assertEqual([(name, anchor) for name, anchor, _ in sections], list(NOC_SECTIONS))
        self.assertEqual(len(legacy), 9)

        interconnect = grouped_original_topics(docs, INTERCONNECT)
        topic = interconnect[1]["片上网络（NoC）"]
        groups = topic[2:]
        self.assertEqual([next(iter(group)) for group in groups], [name for name, _ in NOC_SECTIONS])
        actual = pages(topic)
        expected = {path.relative_to(docs).as_posix() for path in (docs / "NOC/wiki").rglob("*.md")}
        self.assertEqual(sum(len(entries) for _, _, entries in sections), len(expected) - len(legacy) - 2)
        self.assertEqual(set(actual), expected)
        self.assertEqual(len(actual), len(expected))

        representative = {
            "NOC/wiki/06-ai-noc-specifics/chiplet-and-die-to-die-interconnect.md": "05 端点与系统集成",
            "NOC/wiki/06-ai-noc-specifics/broadcast-multicast-tree.md": "06 多端通信与调度",
            "NOC/wiki/06-ai-noc-specifics/workload-gemm-on-noc.md": "07 工作负载与系统案例",
            "NOC/wiki/05-system-integration/traffic-patterns-and-characterization.md": "08 性能评估与架构探索",
            "NOC/wiki/08-simulator-construction/router-pipeline-pseudocode.md": "09 模拟器构建与验证",
        }
        for path, group in representative.items():
            with self.subTest(path=path):
                self.assertIn(path, pages(next(item[group] for item in groups if group in item)))
                directory = Path(path).with_suffix("")
                html = (SITE / directory / "index.html").read_text(encoding="utf-8")
                breadcrumb = re.search(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', html, re.DOTALL)
                self.assertIsNotNone(breadcrumb)
                self.assertIn(group, breadcrumb.group(1))
                self.assertIn("原章节：", html)

        intro = SITE / "NOC/wiki/06-ai-noc-specifics/collective-communication-basics/index.html"
        intro_html = intro.read_text(encoding="utf-8")
        for slug in ("broadcast-multicast-tree", "reduction-and-collective-networks",
                     "deterministic-noc-and-static-scheduling", "compiler-noc-co-design"):
            with self.subTest(navigation_title=slug):
                links = re.findall(r'<a\b(?=[^>]*\bmd-nav__link\b)(?=[^>]*href="\.\./' + re.escape(slug) + r'/")[^>]*>', intro_html)
                self.assertEqual(len(links), 1)
                self.assertNotIn("{#", links[0])

    def test_all_old_urls_anchors_search_and_active_navigation(self):
        legacy = json.loads((Path(__file__).parent / "fixtures/noc-legacy-anchors.json").read_text(encoding="utf-8"))
        search = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))["docs"]
        locations = {unquote(entry["location"]) for entry in search}
        for slug in ("collective-communication-basics", "all-to-all-and-traffic-matrix"):
            self.assertIn(f"NOC/wiki/06-ai-noc-specifics/{slug}/", locations)
        self.assertIn("NOC/wiki/07-workload-cases/coherent-access-and-noc/", locations)
        for slug in ("performance-bounds-and-bottlenecks", "trace-generation-worked-example"):
            self.assertIn(f"NOC/wiki/07-evaluation-methodology/{slug}/", locations)
        for slug in ("workload-endpoint-execution", "minimal-cycle-simulator"):
            self.assertIn(f"NOC/wiki/08-simulator-construction/{slug}/", locations)
        for path, anchors in legacy.items():
            with self.subTest(page=path):
                html = (SITE / path / "index.html").read_text(encoding="utf-8")
                article = re.search(r'<article\b[^>]*>(.*?)</article>', html, re.DOTALL)
                self.assertIsNotNone(article)
                ids = re.findall(r'\bid="([^"]+)"', article.group(1))
                for anchor in anchors:
                    self.assertEqual(ids.count(anchor), 1, (path, anchor))
                self.assertIn(path + "/", locations)
                active = re.search(r'<a\s+href="([^"]+)"\s+class="[^"]*\bmd-nav__link--active\b[^"]*"[^>]*>', html)
                self.assertIsNotNone(active)
                current = "https://example.test/" + path + "/"
                self.assertEqual(urljoin(current, unescape(active.group(1))), current)

    def test_unassigned_or_duplicate_page_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(SITE.parent / "docs/NOC/wiki", root / "NOC/wiki")
            extra = root / "NOC/wiki/extra.md"
            extra.write_text("# Extra\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "does not cover pages"):
                read_noc_sections(root)
            extra.unlink()
            summary = root / "NOC/wiki/SUMMARY.md"
            with summary.open("a", encoding="utf-8") as out:
                out.write("\n- [重复](./01-overview/problem-statement.md)\n")
            with self.assertRaisesRegex(ValueError, "Duplicate NoC navigation target"):
                read_noc_sections(root)


if __name__ == "__main__":
    unittest.main()
