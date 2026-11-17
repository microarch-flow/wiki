"""Validate the six coherence chapters, their preserved entry points and search."""
from html import unescape
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / '.site-build/site'
DOCS = ROOT / '.site-build/docs'
SOURCE = ROOT / 'series/interconnect/COHERENCE'
sys.path.insert(0, str(ROOT / 'website'))
from hooks import coherence_sections, coherence_topic_tree


def location(source):
    path = source.relative_to(SOURCE)
    return 'COHERENCE/wiki/' + (path.parent.as_posix() + '/' if path.name == 'README.md'
                               else path.with_suffix('').as_posix() + '/').removeprefix('./')


class CoherenceNavigationTests(unittest.TestCase):
    def test_chapter_coverage_and_legacy_cxl_parent(self):
        sections = coherence_sections(DOCS)
        self.assertEqual(len(sections), 6)
        self.assertEqual([len(pages) - 1 for _, pages in sections], [3, 5, 3, 4, 3, 3])
        self.assertEqual(sections[3][1][0][1], 'COHERENCE/wiki/cxl-host-memory.md')
        self.assertTrue(all(p.startswith('COHERENCE/wiki/04-cxl/') for _, p in sections[3][1][1:]))
        self.assertEqual(len(list(SOURCE.rglob('*.md'))), 28)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(SOURCE, root / 'COHERENCE/wiki')
            (root / 'COHERENCE/wiki/04-cxl/unlisted.md').write_text('# New article\n')
            with self.assertRaisesRegex(ValueError, 'coverage'):
                coherence_topic_tree(root)

    def test_titles_search_order_and_breadcrumbs(self):
        entries = json.loads((SITE / 'search/search_index.json').read_text())['docs']
        titles = {unquote(e['location']): e['title'].replace('\u200b', '') for e in entries}
        for source in SOURCE.rglob('*.md'):
            loc = location(source)
            page = (SITE / loc / 'index.html').read_text()
            full = re.search(r'^# (.+)$', source.read_text(), re.M)[1]
            with self.subTest(page=loc):
                self.assertEqual(titles[loc], full)
                self.assertTrue(unescape(re.search(r'<title>(.*?)</title>', page, re.S)[1]).startswith(full + ' - '))
                self.assertIn(f'<link rel="canonical" href="https://microarch-flow.github.io/wiki/{loc}">', page)
                crumb = re.search(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', page, re.S)[1]
                self.assertIn('芯片与系统互连', crumb)
                if source.parent.name == '04-cxl':
                    self.assertIn('04 CXL 内存访问', crumb)
                    self.assertIn('cxl-host-memory/', crumb)
        for _, pages in coherence_sections(DOCS):
            guide = SOURCE / Path(pages[0][1]).relative_to('COHERENCE/wiki')
            loc = location(guide)
            page = (SITE / loc / 'index.html').read_text()
            start = page.index('<div class="md-sidebar md-sidebar--primary"')
            end = page.index('<div class="md-sidebar md-sidebar--secondary"', start)
            primary = page[start:end]
            positions = []
            for short, path in pages[1:]:
                target = '/' + path.removesuffix('.md') + '/'
                found = [(m.start(), m[2]) for m in re.finditer(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', primary, re.S)
                         if urlsplit(urljoin('https://example.test/' + loc, unescape(m[1]))).path == target]
                self.assertEqual(len(found), 1, path)
                self.assertIn(short, unescape(found[0][1]))
                positions.append(found[0][0])
            self.assertEqual(positions, sorted(positions))

    def test_legacy_anchors_and_internal_article_links(self):
        fixture = json.loads((ROOT / 'website/tests/fixtures/interconnect-legacy-anchors.json').read_text())
        for source in SOURCE.rglob('*.md'):
            loc = location(source)
            page = (SITE / loc / 'index.html').read_text()
            article = re.search(r'<article\b[^>]*>(.*?)</article>', page, re.S)[1]
            ids = re.findall(r'\bid="([^"]+)"', article)
            for anchor in fixture.get(loc.rstrip('/'), []):
                self.assertEqual(ids.count(anchor), 1, (loc, anchor))
            for alt, src in re.findall(r'<img\b[^>]*alt="([^"]*)"[^>]*src="([^"]+)"', article):
                self.assertTrue(alt)
                target = urlsplit(urljoin('https://example.test/' + loc, unescape(src)))
                self.assertTrue((SITE / unquote(target.path).lstrip('/')).is_file(), (loc, src))
            for href in re.findall(r'href="([^"]+)"', article):
                url = urlsplit(urljoin('https://example.test/' + loc, unescape(href)))
                if url.netloc != 'example.test':
                    continue
                target = SITE / unquote(url.path).lstrip('/')
                if target.is_dir():
                    target /= 'index.html'
                self.assertTrue(target.is_file(), (loc, href))
                if url.fragment:
                    self.assertIn(unquote(url.fragment), re.findall(r'\bid="([^"]+)"', target.read_text()), (loc, href))


if __name__ == '__main__':
    unittest.main()
