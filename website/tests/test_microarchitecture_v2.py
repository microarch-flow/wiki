"""Check the new reader-facing guides without changing legacy URL coverage."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import unittest
from urllib.parse import urljoin, urlsplit, unquote

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "series/microarchitecture-v2"
SITE = ROOT / ".site-build/site"
PREFIX = "microarchitecture-v2/"
ROUTES = (
    "01-foundations", "02-cpu", "03-parallel-execution", "04-compute-arrays",
    "05-data-movement", "06-resource-cooperation", "07-specialized-compute",
    "08-performance", "09-compute-paradigms",
)


class Body(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.inside = False
        self.links = []
        self.images = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article":
            self.inside = True
        if self.inside and tag == "a":
            self.links.append(attrs.get("href", ""))
        if self.inside and tag == "img":
            self.images.append((attrs.get("src", ""), attrs.get("alt", "")))

    def handle_endtag(self, tag):
        if tag == "article":
            self.inside = False


class MicroarchitectureV2Tests(unittest.TestCase):
    def test_all_guides_match_the_plan_and_do_not_link_unwritten_articles(self):
        plan = (ROOT / "docs/microarchitecture-v2-plan.md").read_text()
        planned = dict(re.findall(r"^\| ([A-I]\d\d) \| ([^|]+?) \|", plan, re.M))
        actual = {}
        for prefix, route in zip("ABCDEFGHI", ROUTES):
            guide = (SOURCE / route / "README.md").read_text()
            self.assertTrue(guide.startswith("# "))
            self.assertIn("assets/knowledge-map.svg", guide)
            for id_, title, status in re.findall(
                r"^\| ([A-I]\d\d) \| ([^|]+?) \| [^|]+? \| ([^|]+?) \|$", guide, re.M
            ):
                self.assertTrue(id_.startswith(prefix))
                self.assertNotIn(id_, actual)
                link = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", title)
                if status == "未发布":
                    self.assertIsNone(link, id_)
                else:
                    self.assertIsNotNone(link, id_)
                    self.assertTrue((SOURCE / route / link.group(2)).is_file(), id_)
                actual[id_] = link.group(1) if link else title
        self.assertEqual(actual, planned)

    def test_guide_navigation_maps_links_and_search(self):
        locations = Counter(item["location"] for item in json.loads(
            (SITE / "search/search_index.json").read_text())["docs"] if "#" not in item["location"])
        landing = (SITE / PREFIX / "index.html").read_text()
        self.assertIn("旧版资料", landing)
        self.assertIn("九个专题的知识关系", landing)
        for route in ("", *ROUTES):
            relative = PREFIX + (route + "/" if route else "")
            path = SITE / relative / "index.html"
            page = path.read_text()
            body = Body(page)
            self.assertEqual(locations[relative], 1, relative)
            self.assertTrue(any("knowledge-map.svg" in src and alt for src, alt in body.images), relative)
            for ref in [*body.links, *(src for src, _ in body.images)]:
                target = urlsplit(urljoin("https://site.invalid/" + relative, ref))
                if target.netloc != "site.invalid":
                    continue
                local = SITE / unquote(target.path).lstrip("/")
                if target.path.endswith("/"):
                    local /= "index.html"
                self.assertTrue(local.is_file(), (relative, ref))
        self.assertIn('href="microarchitecture-v2/"', (SITE / "index.html").read_text())
        legacy = (SITE / "microarchitecture/index.html").read_text()
        self.assertIn("新版计算微架构导读", legacy)
        self.assertIn("../microarchitecture-v2/", legacy)
