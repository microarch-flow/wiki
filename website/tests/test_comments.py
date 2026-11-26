"""Check comments are attached to articles, not the navigation or search text."""

import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / ".site-build" / "site"
sys.path.insert(0, str(ROOT / "website"))
from comments import comment_settings, comment_term, is_concrete_article, on_nav, on_post_page  # noqa: E402


def page(path, index=False, canonical_url="https://example.test/wiki/article/", meta=None):
    return SimpleNamespace(file=SimpleNamespace(src_uri=path), is_index=index,
                           canonical_url=canonical_url, meta=meta or {})


def config(enabled=True, **overrides):
    # Fixture values only; tests do not contact Giscus or create Discussions.
    values = dict(enabled=enabled, repo="fixture/repository", repo_id="fixture-repo-id",
                  category="文章评论", category_id="fixture-category-id")
    values.update(overrides)
    return SimpleNamespace(extra={"comments": values}, site_url="https://example.test/wiki/")


class CommentsTests(unittest.TestCase):
    def test_configuration_can_be_disabled_but_enabled_configuration_must_be_complete(self):
        self.assertIsNone(comment_settings(config(enabled=False, category_id="")))
        with self.assertRaisesRegex(ValueError, "category_id"):
            comment_settings(config(category_id=""))
        with self.assertRaisesRegex(ValueError, "owner/repository"):
            comment_settings(config(repo="https://evil.example/"))
        with self.assertRaisesRegex(ValueError, "true or false"):
            comment_settings(config(enabled="true"))
        self.assertEqual(comment_settings(config())["category"], "文章评论")

    def test_article_selection_uses_the_primary_navigation_and_index_role(self):
        articles = [page("electrical-timing-foundations.md"),
                    page("microarchitecture-v2/01-foundations/a01.md"),
                    page("foundations/electrons-to-diode/README.md"),
                    page("series/chip-architectures/nvidia-h100-sxm/README.md")]
        guides = [page("README.md", index=True), page("storage.md"),
                  page("microarchitecture.md"), page("interconnect.md"),
                  page("foundations/README.md", index=True),
                  page("microarchitecture-v2/01-foundations/README.md", index=True),
                  page("COHERENCE/wiki/cxl-host-memory.md", index=True),
                  page("CPO/wiki/SUMMARY.md"), page("BUS/wiki/01-overview/learning-roadmap.md"),
                  page("reviews/old.md"), page("wiki.old/test.md")]
        self.assertTrue(all(is_concrete_article(p) for p in articles))
        self.assertFalse(any(is_concrete_article(p) for p in guides))
        cfg = config()
        nav = SimpleNamespace(pages=articles + guides)
        on_nav(nav, cfg)
        self.assertEqual(cfg.extra["comment_article_paths"], {p.file.src_uri for p in articles})
        markup = "<html><head></head><body><article>Article body</article></body></html>"
        unlisted = page("RAM/wiki/old-unlisted-redirect.md")
        self.assertEqual(on_post_page(markup, unlisted, cfg), markup)
        self.assertEqual(on_post_page(markup, guides[0], cfg), markup)
        articles[0].meta["comments"] = False
        self.assertEqual(on_post_page(markup, articles[0], cfg), markup)

    def test_comments_use_a_canonical_published_path_and_load_lazily(self):
        p = page("foundations/electrons-to-diode/README.md", canonical_url="https://example.test/wiki/中文/")
        cfg = config()
        on_nav(SimpleNamespace(pages=[p]), cfg)
        markup = "<html><head></head><body><article>Article body</article></body></html>"
        rendered = on_post_page(markup, p, cfg)
        self.assertIn('content="https://example.test/wiki/中文/"', rendered)
        self.assertIn('data-mapping="specific"', rendered)
        self.assertIn('data-term="/wiki/中文/"', rendered)
        self.assertIn('data-strict="1"', rendered)
        self.assertIn('data-loading="lazy"', rendered)
        self.assertIn('data-lang="zh-CN"', rendered)
        self.assertIn('data-reactions-enabled="1"', rendered)
        self.assertIn('data-emit-metadata="0"', rendered)
        self.assertIn('href="https://github.com/fixture/repository/discussions"', rendered)
        self.assertIn('href="https://github.com/fixture/repository/issues"', rendered)
        self.assertLess(rendered.index("Article body"), rendered.index('class="site-comments"'))
        self.assertLess(rendered.index('class="site-comments"'), rendered.index("</article>"))
        self.assertEqual(rendered.count('src="https://giscus.app/client.js"'), 1)
        self.assertEqual(comment_term(p), comment_term(page("renamed/README.md", canonical_url=p.canonical_url)))
        disabled = config(enabled=False)
        on_nav(SimpleNamespace(pages=[p]), disabled)
        self.assertEqual(on_post_page(markup, p, disabled), markup)


class GeneratedCommentsTests(unittest.TestCase):
    def test_generated_comments_and_search(self):
        # Full-site validation uses the actual enabled state, while the unit tests
        # above exercise both states without depending on GitHub or local access.
        self.assertTrue(SITE.is_dir(), "Build the site before running this test")
        cfg = yaml.load((ROOT / "mkdocs.yml").read_text(), Loader=yaml.BaseLoader)
        enabled = cfg["extra"]["comments"]["enabled"].lower() == "true"
        article_urls = [
            "foundations/electrons-to-diode/",
            "series/chip-architectures/nvidia-h100-sxm/",
            "RAM/wiki/02-sram-foundations/6t-cell-bistable-storage/",
            "electrical-timing-foundations/",
        ]
        for url in article_urls:
            with self.subTest(article=url):
                html = (SITE / url / "index.html").read_text()
                self.assertEqual('src="https://giscus.app/client.js"' in html, enabled)
                if enabled:
                    self.assertIn(f'data-term="/wiki/{url}"', html)
                    self.assertIn(f'data-repo-id="{cfg["extra"]["comments"]["repo_id"]}"', html)
                    self.assertIn(f'data-category-id="{cfg["extra"]["comments"]["category_id"]}"', html)
        for url in ["", "storage/", "foundations/", "microarchitecture-v2/",
                    "microarchitecture-v2/01-foundations/", "series/chip-architectures/",
                    "RAM/wiki/02-sram-foundations/", "COHERENCE/wiki/cxl-host-memory/",
                    "D2D/wiki/SUMMARY/", "reviews/2026-11-09-topic-review/"]:
            with self.subTest(guide=url):
                html = (SITE / url / "index.html").read_text()
                self.assertNotIn('src="https://giscus.app/client.js"', html)
        search = json.loads((SITE / "search/search_index.json").read_text())
        self.assertFalse(any("评论公开保存在GitHubDiscussions" in
                             "".join(doc.get("text", "").replace("\u200b", "").split()) for doc in search["docs"]))


if __name__ == "__main__":
    unittest.main()
