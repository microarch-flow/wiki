"""Enable Arithmatex only for the inference drafts during Markdown parsing."""

from html import escape
import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from pymdownx.arithmatex import ArithmatexExtension


MARKER = "<!-- site-inference-math -->"


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
