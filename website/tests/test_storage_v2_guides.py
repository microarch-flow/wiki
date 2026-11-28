"""Verify the storage reconstruction coexists with the published storage series."""

from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "series/storage-v2"
DOCS = ROOT / ".site-build/docs"
SITE = ROOT / ".site-build/site"
PREFIX = "storage-v2/"
ROUTES = (
    "01-foundations", "02-sram", "03-on-chip-storage", "04-cache",
    "05-address-translation", "06-dram", "07-memory-controller",
    "08-nonvolatile-media", "09-nonvolatile-storage", "10-system-integration",
    "11-reliability", "12-performance",
)


class GuideContent(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.in_article = False
        self.links = []
        self.images = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article":
            self.in_article = True
        elif self.in_article and tag == "a":
            self.links.append(attrs.get("href", ""))
        elif self.in_article and tag == "img":
            self.images.append((attrs.get("src", ""), attrs.get("alt", "")))

    def handle_endtag(self, tag):
        if tag == "article":
            self.in_article = False


class StorageV2GuideTests(unittest.TestCase):
    def test_article_baseline_matches_guides_and_legacy_inventory(self):
        plan = (ROOT / "docs/storage-v2-plan.md").read_text(encoding="utf-8")
        planned = {}
        for match in re.finditer(
                r"^\| ([A-L]\d\d) \| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \| `([^`]+)` \| ([^|]+?) \|$", plan, re.M):
            id_, title, scope, prerequisites, filename, status = match.groups()
            self.assertNotIn(id_, planned)
            planned[id_] = (title, scope, prerequisites, filename, status)

        seen = set()
        for prefix, route in zip("ABCDEFGHIJKL", ROUTES):
            guide = (SOURCE / route / "README.md").read_text(encoding="utf-8")
            for match in re.finditer(
                    r"^\| ([A-L]\d\d) \| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \|$", guide, re.M):
                id_, title, scope, prerequisites, status = match.groups()
                self.assertTrue(id_.startswith(prefix))
                self.assertIn(id_, planned)
                self.assertNotIn(id_, seen)
                seen.add(id_)
                expected_title, expected_scope, expected_prerequisites, filename, expected_status = planned[id_]
                link = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", title)
                if status.startswith("未发布"):
                    self.assertIsNone(link, id_)
                    self.assertFalse((SOURCE / route / filename).exists(), id_)
                else:
                    self.assertIsNotNone(link, id_)
                    self.assertEqual(link.group(2), filename)
                    self.assertTrue((SOURCE / route / filename).is_file(), id_)
                self.assertEqual((link.group(1) if link else title, scope, prerequisites, status),
                                 (expected_title, expected_scope, expected_prerequisites, expected_status), id_)

        self.assertEqual(seen, set(planned))
        self.assertEqual(len(planned), 57)
        self.assertEqual(sum("深化" in status for _, _, _, _, status in planned.values()), 3)

        legacy = ROOT / "series/storage"
        existing = {path.relative_to(legacy).as_posix() for path in legacy.rglob("*.md")
                    if path.name != "README.md"}
        mapped = set(re.findall(r"\]\(\.\./series/storage/([^#)]+\.md)(?:#[^)]*)?\)", plan))
        self.assertEqual(existing - mapped, set())
        self.assertTrue(all((legacy / path).is_file() for path in mapped))

    def test_existing_storage_series_stays_the_primary_entry(self):
        entries = json.loads((ROOT / "website/series.json").read_text())["series"]
        self.assertEqual(len(entries), 8)
        self.assertEqual([entry["page"] for entry in entries if entry.get("page") == "storage.md"], ["storage.md"])
        self.assertNotIn(PREFIX.rstrip("/"), [entry.get("local", {}).get("publish") for entry in entries])

        old = SITE / "storage/index.html"
        page = old.read_text(encoding="utf-8")
        self.assertIn("新版建设中", page)
        self.assertIn("../storage-v2/", GuideContent(page).links)
        self.assertIn('id="first-load"', page)
        self.assertIn('id="topics"', page)
        self.assertTrue((SITE / "RAM/wiki/02-sram-foundations/6t-cell-bistable-storage/index.html").is_file())
        self.assertTrue((SITE / "HBF/wiki/index.html").is_file())
        home = (SITE / "index.html").read_text(encoding="utf-8")
        self.assertIn('<a class="portal-series-card" href="storage/">', home)
        self.assertNotIn('<a class="portal-series-card" href="storage-v2/">', home)

    def test_staged_guides_have_valid_links_assets_and_breadcrumbs(self):
        locations = Counter(entry["location"] for entry in json.loads(
            (SITE / "search/search_index.json").read_text())["docs"] if "#" not in entry["location"])
        for route in ("", *ROUTES):
            relative = PREFIX + (route + "/" if route else "")
            with self.subTest(route=route):
                self.assertTrue((SOURCE / route / "README.md").is_file())
                self.assertTrue((DOCS / relative / "README.md").is_file())
                self.assertTrue((SOURCE / route / "assets/knowledge-map.dot").is_file())
                svg = SOURCE / route / "assets/knowledge-map.svg"
                self.assertEqual(ElementTree.parse(svg).getroot().tag, "{http://www.w3.org/2000/svg}svg")
                page = (SITE / relative / "index.html").read_text(encoding="utf-8")
                self.assertEqual(locations[relative], 1)
                breadcrumbs = re.search(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', page, re.S)
                self.assertIsNotNone(breadcrumbs)
                self.assertIn("存储系统", breadcrumbs.group(1))
                self.assertIn("新版", page)
                body = GuideContent(page)
                self.assertTrue(any("knowledge-map.svg" in src and alt for src, alt in body.images))
                for link in [*body.links, *(src for src, _ in body.images)]:
                    target = urlsplit(urljoin("https://site.invalid/" + relative, link))
                    if target.netloc != "site.invalid":
                        continue
                    path = SITE / unquote(target.path).lstrip("/")
                    if path.is_dir():
                        path /= "index.html"
                    self.assertTrue(path.is_file(), (relative, link))

        landing = GuideContent((SITE / PREFIX / "index.html").read_text(encoding="utf-8"))
        self.assertTrue(set(f"{route}/" for route in ROUTES).issubset(landing.links))


if __name__ == "__main__":
    unittest.main()
