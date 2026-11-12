"""Keep mathematics scoped to inference and preserve ordinary Markdown code."""

from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

import markdown

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from website.inference_math import MARKER, on_config, on_page_markdown  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
