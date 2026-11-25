"""Publish section links from the old GitHub reading guides at their original URLs."""

from html import escape
import posixpath
import re
from string import Template
from urllib.parse import urlsplit

from stage_links import page_directory


FOUNDATION_SPLIT_ARTICLES = ("silicon-to-logic", "inverter-to-package", "voltage-to-clock")
SILICON_TO_LOGIC_LEGACY_SECTIONS = {
    "circuit-quantities": "用电压电流电阻和电容描述一个节点",
    "silicon-and-doping": "从硅的四个价电子理解-p-型和-n-型掺杂",
    "pn-junction": "pn-结如何形成势垒二极管如何整流",
    "bipolar-transistor": "三极管怎样放大电流并作为开关",
    "mosfet": "mosfet-如何用栅极电压控制沟道电流",
    "cmos-logic": "cmos-门怎样用充放电实现逻辑运算",
}


def read_sections(readme, published):
    """Each bullet groups the bookmarks which now share its Markdown link."""
    lines = readme.read_text(encoding="utf-8").splitlines()
    sections = []
    for line in lines:
        if not line.startswith("- "):
            continue
        entry = re.fullmatch(r'- ((?:<span id="[^"]+"></span>)+)\[([^\]]+)\]\(([^)]+)\)', line)
        if not entry:
            raise ValueError(f"Invalid section link in {readme}: {line}")
        markers, label, href = entry.groups()
        fragments = re.findall(r'id="([^"]+)"', markers)
        link = urlsplit(href)
        source = (readme.parent / link.path).resolve().relative_to(published.root).as_posix()
        destination = page_directory(published.paths[source])
        sections.append((fragments, label, destination, link.fragment))
    if not sections:
        raise ValueError(f"Missing section links in {readme}")
    return lines[0].removeprefix("# "), sections


def write_redirect(directory, docs, template, title, sections, default_fragment=None):
    rows = []
    default_href = None
    for fragments, label, destination, fragment in sections:
        relative = posixpath.relpath(destination, directory.relative_to(docs).as_posix())
        href = escape(f"{relative}/#{fragment}", quote=True)
        link = f'<a href="{href}">{escape(label)}</a>'
        markers = "".join(f'<span id="{escape(key, quote=True)}"></span>' for key in fragments)
        if (default_fragment is None and not rows) or default_fragment in fragments:
            default_href, default_label = href, escape(label)
        rows.append(f"      <li>{markers}{link}</li>")
    if default_href is None:
        raise ValueError(f"Unknown default bookmark for {directory.name}: {default_fragment}")
    directory.mkdir(exist_ok=True, parents=True)
    page = template.substitute(title=escape(title), default_href=default_href,
                               default_label=default_label, sections="\n".join(rows))
    (directory / "index.html").write_text(page, encoding="utf-8")


def stage_split_guides(root, docs, published):
    for slug in FOUNDATION_SPLIT_ARTICLES:
        source = root / "series/semiconductor-foundations" / slug / "README.md"
        directory = docs / "foundations" / slug
        # Builds with a reduced series registry do not include these guides.
        if source.relative_to(root).as_posix() not in published.paths:
            continue
        template = Template((root / "website/foundation-section-redirect.html").read_text(encoding="utf-8"))
        title, sections = read_sections(source, published)
        write_redirect(directory, docs, template, title, sections)
        if slug == "silicon-to-logic":
            for subpath, default in SILICON_TO_LOGIC_LEGACY_SECTIONS.items():
                write_redirect(directory / subpath, docs, template, title, sections, default)
