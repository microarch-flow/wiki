from collections import Counter
from html import unescape
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / ".site-build" / "site"
LEGACY = Path(__file__).with_name("fixtures") / "chip-development-legacy.json"


class ChipDevelopmentRefinementTest(unittest.TestCase):
    def test_published_paths_anchors_and_search(self):
        legacy = json.loads(LEGACY.read_text(encoding="utf-8"))
        index = json.loads((SITE / "search" / "search_index.json").read_text(encoding="utf-8"))
        records = Counter(item["location"] for item in index["docs"] if "#" not in item["location"])

        for path, anchors in legacy.items():
            with self.subTest(path=path):
                html = (SITE / path).read_text(encoding="utf-8")
                article = html.split("<article", 1)[1].split("</article>", 1)[0]
                ids = Counter(unescape(value) for value in re.findall(r'\bid="([^"]+)"', article))
                self.assertEqual([anchor for anchor in anchors if ids[anchor] != 1], [])
                self.assertEqual(records[path.removesuffix("index.html")], 1)

    def test_fab_diagrams_use_full_size_and_preserve_text_alignment(self):
        warpage = "FAB/wiki/06-cross-cutting-engineering/stress-warpage-cte/"
        html = (SITE / warpage / "index.html").read_text(encoding="utf-8")
        self.assertIn('<div class="fab-diagram-scroll" data-top-down>', html)
        self.assertIn("useMaxWidth: false", html)
        self.assertIn('class="fab-text-diagram highlight"', html)

        interposer = SITE / "FAB/wiki/04-back-end-packaging/2.5d-routes/si-interposer-fundamentals/index.html"
        self.assertIn('class="fab-text-diagram fab-diagram-aligned highlight"', interposer.read_text(encoding="utf-8"))

        index = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))
        sections = [item for item in index["docs"] if item["location"].startswith(warpage + "#")]
        self.assertTrue(sections)
        self.assertFalse(any("useMaxWidth" in item["text"] for item in sections))

    def test_grouped_articles_have_no_source_only_ancestor(self):
        cases = {
            "series/chip-development/02_frontend_design_and_verification/05_dft_introduction/":
                "可测性设计、晶圆筛测与终测",
            "FAB/wiki/05-final-test-and-reliability/final-test-methodology/":
                "可测性设计、晶圆筛测与终测",
            "series/chip-development/04_tapeout_and_post_silicon/03_packaging/":
                "封装与多芯粒集成",
            "series/chip-development/04_tapeout_and_post_silicon/06_characterization/":
                "硅后启动、测量与修订",
            "FAB/wiki/06-cross-cutting-engineering/yield-economics-across-stages/":
                "可靠性、良率与量产生命周期",
        }
        for path, topic in cases.items():
            with self.subTest(path=path):
                html = (SITE / path / "index.html").read_text(encoding="utf-8")
                crumb = re.search(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', html, re.S)
                self.assertIsNotNone(crumb)
                labels = [unescape(re.sub(r"<[^>]+>", "", item))
                          for item in re.findall(r"<li>(.*?)</li>", crumb[1], re.S)]
                self.assertEqual(labels[:3], ["首页", "芯片开发与实现", topic])
                self.assertEqual(len(labels), 4)
