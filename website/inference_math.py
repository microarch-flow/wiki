"""Enable Arithmatex only for the inference drafts during Markdown parsing."""

from html import escape, unescape
import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markupsafe import Markup
from pymdownx.arithmatex import ArithmatexExtension


MARKER = "<!-- site-inference-math -->"
INLINE_TEX = re.compile(r"\\\((.+?)\\\)")
GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "eta": "η",
    "lambda": "λ", "mu": "μ", "sigma": "σ", "tau": "τ", "theta": "θ",
}


def on_config(config, **kwargs):
    """Register the local extension after MkDocs has loaded this hook by path."""
    if not any(isinstance(item, InferenceMathExtension) for item in config.markdown_extensions):
        config.markdown_extensions.append(InferenceMathExtension())
    return config


def on_page_markdown(markdown, page, **kwargs):
    """Mark inference pages; leave every other source untouched."""
    if page.file.src_uri.startswith("series/inference-runtime/"):
        return MARKER + "\n" + markdown
    return markdown


def plain_toc_math(tex):
    """Provide a useful text label when JavaScript or KaTeX is unavailable."""
    value = re.sub(r"\\(?:text|mathrm)\{([^{}]*)\}", r"\1", tex)
    value = re.sub(r"\\([A-Za-z]+)", lambda m: GREEK.get(m.group(1), m.group(1)), value)
    value = re.sub(r"(?<=[_^])\{([^{}]*)\}", r"\1", value)
    return value.replace(r"\_", "_").replace(r"\*", "*")


def toc_title_with_math(title):
    """Wrap inline TeX without altering any of the heading's anchor IDs."""
    result = Markup("")
    end = 0
    for match in INLINE_TEX.finditer(title):
        tex = match.group(1)
        result += Markup(escape(unescape(title[end:match.start()])))
        result += Markup('<span class="inference-toc-math" data-tex="{}">{}</span>').format(tex, plain_toc_math(tex))
        end = match.end()
    return result + Markup(escape(unescape(title[end:]))) if end else title


def on_page_content(html, page, **kwargs):
    """Replace raw TeX in the inference TOC, preserving links and headings."""
    if not page.file.src_uri.startswith("series/inference-runtime/"):
        return html

    def update(items):
        for item in items:
            item.title = toc_title_with_math(item.title)
            update(item.children)

    update(page.toc)
    return html


class SelectiveMath(Preprocessor):
    def run(self, lines):
        if lines and lines[0] == MARKER:
            ArithmatexExtension(generic=True).extendMarkdown(self.md)
            result = []
            for line in lines[1:]:
                # A display formula without surrounding blank lines, or one
                # inside a list, is not block math to Python-Markdown. Stash an
                # equivalent wrapper while preserving the surrounding structure.
                match = re.fullmatch(r"( {0,3})\$\$(.+)\$\$[ \t]*", line)
                if match:
                    wrapped = '<span class="arithmatex arithmatex-inline-display">\\[' + escape(match.group(2)) + '\\]</span>'
                    line = match.group(1) + self.md.htmlStash.store(wrapped)
                result.append(line)
            return result
        return lines


class InferenceMathExtension(Extension):
    def extendMarkdown(self, md):
        md.registerExtension(self)
        # Markdown normalizes control characters at priority 30. Stash after
        # that step so its placeholders survive until post-processing.
        md.preprocessors.register(SelectiveMath(md), "selective-inference-math", 25)


def makeExtension(**kwargs):
    return InferenceMathExtension(**kwargs)
