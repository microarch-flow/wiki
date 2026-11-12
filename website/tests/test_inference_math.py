"""Keep mathematics scoped to inference and preserve ordinary Markdown code."""

from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

import markdown

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from website.inference_math import MARKER, on_config, on_page_content, on_page_markdown, plain_toc_math  # noqa: E402


class InferenceMathTests(unittest.TestCase):
    def test_hook_registers_extension_only_once(self):
        config = SimpleNamespace(markdown_extensions=[])
        on_config(config)
        on_config(config)
        self.assertEqual(len(config.markdown_extensions), 1)

    def test_scoped_math_and_code(self):
        source = "Inline $x_1$ and `price $1`.\n\n$$y=2x$$\n"
        render = lambda text: markdown.markdown(text, extensions=["website.inference_math"])
        self.assertNotIn('class="arithmatex"', render(source))
        html = render(MARKER + "\n" + source)
        self.assertIn('<span class="arithmatex">\\(x_1\\)</span>', html)
        self.assertIn('<span class="arithmatex arithmatex-inline-display">\\[y=2x\\]</span>', html)
        self.assertIn('<code>price $1</code>', html)
        list_html = render(MARKER + "\n" + "- Item:\n  $$z=a+b$$\n  text\n")
        self.assertIn('<span class="arithmatex arithmatex-inline-display">\\[z=a+b\\]</span>', list_html)

    def test_only_inference_paths_receive_the_marker(self):
        inference = SimpleNamespace(file=SimpleNamespace(src_uri="series/inference-runtime/topics/01.md"))
        other = SimpleNamespace(file=SimpleNamespace(src_uri="RAM/wiki/01.md"))
        self.assertTrue(on_page_markdown("source", inference).startswith(MARKER))
        self.assertEqual(on_page_markdown("source", other), "source")

    def test_toc_has_accessible_fallback_without_changing_anchor(self):
        self.assertEqual(plain_toc_math(r"\eta_\text{mem}"), "η_mem")
        self.assertEqual(plain_toc_math(r"\text{KV}_\text{tok}^{\text{fp16}}=320"), "KV_tok^fp16=320")
        heading = SimpleNamespace(title=r"(1) \(\eta_\text{mem}\):从预留到分页", id="stable-anchor", children=[])
        page = SimpleNamespace(file=SimpleNamespace(src_uri="series/inference-runtime/topics/06.md"), toc=[heading])
        self.assertEqual(on_page_content("body", page), "body")
        self.assertEqual(heading.id, "stable-anchor")
        self.assertIn('data-tex="\\eta_\\text{mem}"', str(heading.title))
        self.assertIn('>η_mem</span>', str(heading.title))
        other = SimpleNamespace(file=SimpleNamespace(src_uri="RAM/wiki/01.md"), toc=[heading])
        before = heading.title
        on_page_content("body", other)
        self.assertEqual(heading.title, before)

        escaped = SimpleNamespace(title=r"<unsafe> \(a<b\) &amp;", id="x", children=[])
        page.toc = [escaped]
        on_page_content("body", page)
        self.assertIn("&lt;unsafe&gt;", str(escaped.title))
        self.assertIn('data-tex="a&lt;b"', str(escaped.title))
        self.assertIn("&amp;", str(escaped.title))

    def test_all_inference_math_headings_keep_their_toc_ids(self):
        root = Path(__file__).resolve().parents[2] / "series/inference-runtime/topics"
        files = ("03-naive-bottlenecks", "05-attention-kernels", "06-paged-kv-cache", "10-quantization")
        headings = []

        def convert(items):
            return [SimpleNamespace(title=item["name"], id=item["id"], children=convert(item["children"])) for item in items]

        def flatten(items):
            for item in items:
                yield item
                yield from flatten(item.children)

        for name in files:
            parser = markdown.Markdown(extensions=["toc", "tables", "website.inference_math"])
            parser.convert(MARKER + "\n" + (root / f"{name}.md").read_text(encoding="utf-8"))
            toc = convert(parser.toc_tokens)
            before = [(item.id, item.title) for item in flatten(toc)]
            page = SimpleNamespace(file=SimpleNamespace(src_uri=f"series/inference-runtime/topics/{name}.md"), toc=toc)
            on_page_content("", page)
            after = list(flatten(toc))
            self.assertEqual([item.id for item in after], [item[0] for item in before])
            headings.extend(str(item.title) for item in after if "inference-toc-math" in str(item.title))
        self.assertEqual(len(headings), 8)
        self.assertEqual(sum(item.count('class="inference-toc-math"') for item in headings), 9)
        self.assertTrue(all(r"\(" not in title and r"\)" not in title for title in headings))
        self.assertTrue(any("η_mem" in title for title in headings))
        self.assertTrue(any("KV_tok^fp16=320" in title for title in headings))


if __name__ == "__main__":
    unittest.main()
