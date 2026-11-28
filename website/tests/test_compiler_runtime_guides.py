"""Verify the new software guides coexist with the published runtime series."""

from collections import Counter
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "series/compiler-runtime"
DOCS = ROOT / ".site-build/docs"
SITE = ROOT / ".site-build/site"
PREFIX = "series/compiler-runtime/"
ROUTES = (
    "01-foundations", "02-frontend-and-optimization", "03-mapping-and-planning",
    "04-code-generation", "05-device-driver", "06-execution-runtime",
    "07-model-execution", "08-request-scheduling", "09-distributed-execution",
    "10-serving", "11-performance",
)


class GuideContent(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.in_article = False
        self.links = []
        self.images = []
        self.ids = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "article":
            self.in_article = True
        elif self.in_article and tag == "a":
            self.links.append(attrs.get("href", ""))
        elif self.in_article and tag == "img":
            self.images.append((attrs.get("src", ""), attrs.get("alt", "")))

    def handle_endtag(self, tag):
        if tag == "article":
            self.in_article = False


class CompilerRuntimeGuideTests(unittest.TestCase):
    def test_article_baseline_matches_guides_and_legacy_inventory(self):
        plan = (ROOT / "docs/compiler-runtime-plan.md").read_text()
        planned = {}
        for match in re.finditer(
                r"^\| ([A-K]\d\d) \| ([^|]+?) \| [^|]+? \| [^|]+? \| `([^`]+)` \| ([^|]+?) \|$", plan, re.M):
            id_, title, filename, status = match.groups()
            self.assertNotIn(id_, planned)
            planned[id_] = (title, filename, status)
        actual = {}
        for prefix, route in zip("ABCDEFGHIJK", ROUTES):
            guide = (SOURCE / route / "README.md").read_text()
            for match in re.finditer(r"^\| ([A-K]\d\d) \| ([^|]+?) \| [^|]+? \| [^|]+? \| ([^|]+?) \|$", guide, re.M):
                id_, title, status = match.groups()
                self.assertTrue(id_.startswith(prefix))
                self.assertNotIn(id_, actual)
                link = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", title)
                if status == "未发布":
                    self.assertIsNone(link, id_)
                else:
                    self.assertIsNotNone(link, id_)
                    self.assertTrue((SOURCE / route / link.group(2)).is_file(), id_)
                actual[id_] = link.group(1) if link else title
        self.assertEqual({id_: title for id_, (title, _, _) in planned.items()}, actual)
        self.assertEqual(len(planned), 59)
        self.assertEqual(sum("深化" in status for _, _, status in planned.values()), 6)
        legacy = ROOT / "series/inference-runtime"
        existing = {path.relative_to(legacy).as_posix() for path in legacy.rglob("*.md")
                    if path.name not in {"README.md", "_conventions.md", "glossary.md"}}
        mapped = set(re.findall(r"^\| \[[^\]]+\]\(\.\./series/inference-runtime/([^)]*)\) \|", plan, re.M))
        self.assertEqual(existing, mapped)
        self.assertEqual(len(mapped), 29)

    def test_existing_series_stays_the_primary_entry(self):
        entries = json.loads((ROOT / "website/series.json").read_text())["series"]
        self.assertEqual(len(entries), 8)
        self.assertEqual([entry["local"]["publish"] for entry in entries
                          if entry.get("local", {}).get("publish") == "series/inference-runtime"],
                         ["series/inference-runtime"])
        self.assertNotIn(PREFIX.rstrip("/"), [entry.get("local", {}).get("publish") for entry in entries])

        legacy = SITE / "series/inference-runtime/index.html"
        self.assertTrue(legacy.is_file())
        page = legacy.read_text()
        self.assertIn("新版建设中", page)
        links = GuideContent(page).links
        self.assertIn("../compiler-runtime/", links)
        self.assertTrue((SITE / PREFIX / "index.html").is_file())

    def test_staged_guides_are_searchable_with_valid_links(self):
        locations = Counter(entry["location"] for entry in json.loads(
            (SITE / "search/search_index.json").read_text())["docs"] if "#" not in entry["location"])
        for route in ("", *ROUTES):
            relative = PREFIX + (route + "/" if route else "")
            with self.subTest(route=route):
                self.assertTrue((SOURCE / route / "README.md").is_file())
                self.assertTrue((DOCS / relative / "README.md").is_file())
                page = (SITE / relative / "index.html").read_text()
                self.assertEqual(locations[relative], 1)
                breadcrumbs = re.search(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', page, re.S)
                self.assertIsNotNone(breadcrumbs)
                self.assertIn("编译器与运行时系统", breadcrumbs.group(1))
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

    def test_a01_article_navigation_search_and_diagrams(self):
        route = "01-foundations"
        slug = "a01-program-semantics"
        title = "同一段计算，软件究竟要求计算机做什么？"
        relative = f"{PREFIX}{route}/{slug}/"
        url = "https://site.invalid/" + relative
        source = SOURCE / route / f"{slug}.md"
        staged = DOCS / PREFIX / route / source.name
        self.assertRegex(source.read_text(), rf"(?m)^# {re.escape(title)}$")
        self.assertTrue(staged.is_file())

        page = (SITE / relative / "index.html").read_text()
        body = re.search(r"<article\b[^>]*>(.*?)</article>", page, re.S)[1]
        headings = re.findall(r"<h1\b[^>]*>(.*?)</h1>", body, re.S)
        self.assertEqual(len(headings), 1)
        heading = re.sub(r'<a\b[^>]*class="headerlink"[^>]*>.*?</a>', "", headings[0], flags=re.S)
        self.assertEqual(unescape(re.sub(r"<[^>]+>", "", heading)).strip(), title)
        self.assertIn(f'<link rel="canonical" href="https://microarch-flow.github.io/wiki/{relative}">', page)

        entries = json.loads((SITE / "search/search_index.json").read_text())["docs"]
        indexed = [item for item in entries if unquote(item["location"]) == relative]
        self.assertEqual(len(indexed), 1)
        self.assertEqual(indexed[0]["title"].replace("\u200b", ""), title)

        primary = page.split('<div class="md-sidebar md-sidebar--primary"', 1)[1].split(
            '<div class="md-sidebar md-sidebar--secondary"', 1)[0]
        active = re.findall(r'<a\b[^>]*class="[^"]*\bmd-nav__link--active\b[^"]*"[^>]*>', primary)
        self.assertEqual(len(active), 1)
        self.assertIn('aria-current="page"', active[0])
        href = re.search(r'href="([^"]+)"', active[0])[1]
        self.assertEqual(urljoin(url, unescape(href)), url)

        crumb = re.search(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', page, re.S)[1]
        self.assertIn(f'<span aria-current="page">{title}</span>', crumb)
        crumb_targets = {unescape(label): urljoin(url, unescape(href)) for href, label in
                         re.findall(r'<a href="([^"]+)">([^<]+)</a>', crumb)}
        self.assertEqual(crumb_targets["新版：编译器与运行时系统"], "https://site.invalid/" + PREFIX)
        self.assertEqual(crumb_targets["软件执行共同基础"], "https://site.invalid/" + PREFIX + route + "/")
        guide_url = "https://site.invalid/" + PREFIX + route + "/"
        guide = GuideContent((SITE / PREFIX / route / "index.html").read_text())
        self.assertIn(url, [urljoin(guide_url, link) for link in guide.links])

        content = GuideContent(page)
        for filename in ("a01-values-and-state.svg", "a01-observable-behavior.svg"):
            original = SOURCE / route / "assets" / filename
            published = SITE / PREFIX / route / "assets" / filename
            self.assertTrue(original.is_file())
            self.assertTrue(published.is_file())
            self.assertEqual(ElementTree.parse(published).getroot().tag, "{http://www.w3.org/2000/svg}svg")
            self.assertTrue(any(src.endswith("/" + filename) and alt for src, alt in content.images), filename)

        for ref in [*content.links, *(src for src, _ in content.images)]:
            target = urlsplit(urljoin(url, ref))
            if target.netloc != "site.invalid":
                continue
            path = SITE / unquote(target.path).lstrip("/")
            if path.is_dir():
                path /= "index.html"
            self.assertTrue(path.is_file(), (relative, ref))
            if target.fragment and path.suffix == ".html":
                self.assertIn(unquote(target.fragment), GuideContent(path.read_text()).ids, (relative, ref))


if __name__ == "__main__":
    unittest.main()
