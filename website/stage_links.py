"""Translate source-relative links to paths in the staged site tree.

The source files remain untouched. Only targets actually copied into the site
are translated; unresolved paths and links to non-published material are left
as written. Website page templates use site URLs and are not passed here.
"""

from pathlib import Path, PurePosixPath
import posixpath
import re
from urllib.parse import quote, unquote, urlsplit, urlunsplit


FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
REFERENCE = re.compile(r"^ {0,3}\[[^]\n]+\]:[ \t]*(?:<([^>\n]+)>|([^ \t\n]+))")
HTML_TAG = re.compile(r"<[A-Za-z][^>]*>")
HTML_ATTR = re.compile(r"\b(?:href|src)\s*=\s*(?:([\"'])(.*?)\1|([^\s>]+))", re.IGNORECASE)


class PublishedPaths:
    """Record the actual source and destination of each copied file/directory."""

    def __init__(self, root, docs):
        self.root = Path(root).absolute()
        self.docs = Path(docs).absolute()
        self.paths = {}
        self.pages = {}

    def add(self, source, destination, *, rewrite_page=True):
        source = Path(source).absolute().relative_to(self.root).as_posix()
        destination_path = Path(destination).absolute()
        destination = destination_path.relative_to(self.docs).as_posix()
        previous = self.paths.get(source)
        if previous is not None and previous != destination:
            raise ValueError(f"Source is staged to multiple paths: {source}")
        self.paths[source] = destination
        if rewrite_page and destination_path.is_file() and destination_path.suffix == ".md":
            other = self.pages.get(destination)
            if other is not None and other != source:
                raise ValueError(f"Multiple sources stage to {destination}")
            self.pages[destination] = source

    def add_tree(self, source, destination):
        source, destination = Path(source), Path(destination)
        self.add(source, destination)
        for staged in destination.rglob("*"):
            self.add(source / staged.relative_to(destination), staged)

    def destination(self, raw, source, staged, html=False):
        try:
            parts = urlsplit(raw)
        except ValueError:
            return raw
        path = parts.path
        if not path or parts.scheme or parts.netloc or path.startswith(("/", "\\")) or "\\" in path:
            return raw
        target = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(path)))
        if target == ".." or target.startswith("../"):
            return raw
        mapped = self.paths.get(target)
        if mapped is None:
            return raw
        # Preserve spelling where the source and destination have the same
        # relative topology, even if both were relocated together.
        ordinary = posixpath.relpath(mapped, posixpath.dirname(staged) or ".")
        if posixpath.normpath(ordinary) == posixpath.normpath(unquote(path)):
            return raw
        if html:
            base = _page_directory(staged)
            target_path = _page_directory(mapped) if mapped.endswith(".md") else mapped
        else:
            base = posixpath.dirname(staged) or "."
            target_path = mapped
        relative = posixpath.relpath(target_path, base)
        if (path.endswith("/") or (html and mapped.endswith(".md"))) and not relative.endswith("/"):
            relative += "/"
        if path.startswith("./") and not relative.startswith((".", "/")):
            relative = "./" + relative
        if "%" in path:
            relative = quote(relative, safe="/-._~!$&'()*+,;=:@")
        return urlunsplit(("", "", relative, parts.query, parts.fragment))

    def rewrite(self):
        for staged, source in self.pages.items():
            page = self.docs / staged
            original = page.read_text(encoding="utf-8")
            updated = rewrite_document(original, lambda value, html: self.destination(value, source, staged, html))
            if updated != original:
                page.write_text(updated, encoding="utf-8")


def _page_directory(path):
    path = PurePosixPath(path)
    if path.name in {"README.md", "index.md"}:
        return str(path.parent)
    if path.suffix == ".md":
        return str(path.parent / path.stem)
    return str(path)


def _mask_line(line, in_comment, inline_ticks, raw_block):
    """Mask comments, code spans and HTML pre/code blocks before finding links."""
    mask = [True] * len(line)
    i = 0
    while i < len(line):
        if in_comment:
            end = line.find("-->", i)
            stop = len(line) if end < 0 else end + 3
            mask[i:stop] = [False] * (stop - i)
            i, in_comment = stop, end < 0
            continue
        if raw_block:
            match = re.search(r"</\s*" + raw_block + r"\s*>", line[i:], re.IGNORECASE)
            stop = len(line) if match is None else i + match.end()
            mask[i:stop] = [False] * (stop - i)
            i, raw_block = stop, raw_block if match is None else None
            continue
        if inline_ticks:
            end = line.find(inline_ticks, i)
            stop = len(line) if end < 0 else end + len(inline_ticks)
            mask[i:stop] = [False] * (stop - i)
            i, inline_ticks = stop, inline_ticks if end < 0 else None
            continue
        if line.startswith("<!--", i):
            in_comment = True
            continue
        opening = re.match(r"<(pre|code)(?:\s[^>]*)?>", line[i:], re.IGNORECASE)
        if opening:
            raw_block = opening.group(1)
            continue
        if line[i] == "`" and (i == 0 or line[i - 1] != "\\"):
            end = i + 1
            while end < len(line) and line[end] == "`":
                end += 1
            inline_ticks = line[i:end]
            mask[i:end] = [False] * (end - i)
            i = end
            continue
        i += 1
    return mask, in_comment, inline_ticks, raw_block


def _destinations(line, mask):
    found = []
    reference = REFERENCE.match(line)
    if reference:
        group = 1 if reference.group(1) is not None else 2
        start, end = reference.span(group)
        if all(mask[start:end]):
            found.append((start, end, False))
    for tag in HTML_TAG.finditer(line):
        if not all(mask[tag.start():tag.end()]):
            continue
        for attribute in HTML_ATTR.finditer(tag.group()):
            group = 2 if attribute.group(2) is not None else 3
            start, end = attribute.span(group)
            found.append((tag.start() + start, tag.start() + end, True))
    cursor = 0
    while cursor < len(line) - 1:
        opening = line.find("](", cursor)
        if opening < 0:
            break
        cursor = opening + 2
        if not (mask[opening] and mask[opening + 1]):
            continue
        start = cursor
        while start < len(line) and line[start] in " \t":
            start += 1
        if start >= len(line):
            continue
        if line[start] == "<":
            end = line.find(">", start + 1)
            if end < 0:
                continue
            start += 1
        else:
            end, depth, escaped = start, 0, False
            while end < len(line):
                ch = line[end]
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    if depth == 0:
                        break
                    depth -= 1
                elif ch.isspace() and depth == 0:
                    break
                end += 1
            if end == start or end >= len(line):
                continue
        if all(mask[start:end]):
            found.append((start, end, False))
    return sorted(set(found))


def rewrite_document(text, convert):
    """Rewrite links outside code and comments without changing other text."""
    output = []
    fence = None
    comment = False
    ticks = None
    raw_block = None
    for line in text.splitlines(keepends=True):
        marker = FENCE.match(line)
        if marker and not comment and not ticks and not raw_block:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            output.append(line)
            continue
        if fence is not None:
            output.append(line)
            continue
        # Indented blocks are code in the tracked Markdown corpus. Nested list
        # continuations with links are not currently used; keep them untouched.
        if line.startswith(("    ", "\t")) and not comment and not ticks and not raw_block:
            output.append(line)
            continue
        mask, comment, ticks, raw_block = _mask_line(line, comment, ticks, raw_block)
        for start, end, html in reversed(_destinations(line, mask)):
            value = convert(line[start:end], html)
            line = line[:start] + value + line[end:]
        output.append(line)
    return "".join(output)
