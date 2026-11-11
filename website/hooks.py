"""Build navigation and breadcrumbs from the wiki's chapter directories."""

from html import escape, unescape
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
from urllib.parse import quote, unquote, urljoin, urlsplit

from mkdocs.utils import get_relative_url


TOPICS = (
    ("RAM", "RAM · 存储系统"),
    ("COMPUTE", "COMPUTE · 计算"),
    ("BUS", "BUS · 片上总线"),
    ("NOC", "NoC · 片上网络"),
    ("DMA", "DMA · 数据搬运"),
    ("PCIE", "PCIe · 主机互连"),
    ("CIM", "CIM · 存内计算"),
    ("CPO", "CPO · 光互连"),
    ("FAB", "FAB · 制造与封装"),
)


def read_series(root, registry=None):
    """Read a list of local pages or independently hosted HTTPS series."""
    registry = registry or Path(__file__).parent / "series.json"
    entries = json.loads(registry.read_text(encoding="utf-8"))["series"]
    if not isinstance(entries, list) or not entries:
        raise ValueError("website/series.json must contain at least one series")
    result = []
    for item in entries:
        name = item.get("title", "").strip()
        description = item.get("description", "").strip()
        page, url = item.get("page"), item.get("url")
        if not name or not description or bool(page) == bool(url):
            raise ValueError("Each series needs a title, description, and exactly one page or url")
        if page:
            path = PurePosixPath(page)
            if path.is_absolute() or ".." in path.parts or path.suffix.lower() != ".md" or not (root / page).is_file():
                raise ValueError(f"Series page does not exist inside the staged docs: {page}")
            relative = path.parent if path.name.lower() in {"index.md", "readme.md"} else path.with_suffix("")
            href = quote(relative.as_posix(), safe="/") + "/"
            target = page
        else:
            parsed = urlsplit(url)
            if parsed.scheme != "https" or not parsed.netloc:
                raise ValueError(f"Series URL must be an absolute HTTPS URL: {url}")
            href = target = url
        result.append({"title": name, "description": description, "href": href, "target": target})
    return result


def render_series(entries, relative_root=""):
    """Render public links; the empty future tile is presentational only."""
    cards = []
    for index, entry in enumerate(entries, 1):
        href = entry["href"] if urlsplit(entry["href"]).scheme else relative_root + entry["href"]
        cards.append(
            '<a class="portal-series-card" href="{}">'
            '<span class="portal-card-number">SERIES / {:02d}</span>'
            '<span class="portal-card-arrow" aria-hidden="true">↗</span>'
            '<h3>{}</h3><p>{}</p><span class="portal-card-link">进入系列 →</span></a>'.format(
                escape(href, quote=True), index,
                escape(entry["title"]), escape(entry["description"]),
            )
        )
    return "\n".join(cards)


def title(path):
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^#\s+(.+?)\s*$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else path.stem.replace("-", " ")


def reading_items(directory):
    """Read labels and targets from an index's numbered sibling reading list."""
    index = directory / "README.md"
    if not index.is_file():
        return []
    items = []
    section_level = None
    fence = None
    for line in index.read_text(encoding="utf-8").splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence) and not marker.group(2).strip():
                fence = None
            continue
        if marker:
            fence = marker.group(1)
            continue
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            level = len(heading.group(1))
            if section_level is not None and level <= section_level:
                if items:
                    break
                section_level = None
            label = re.sub(r"^\d+[.、．]?\s*", "", heading.group(2)).strip()
            if re.fullmatch(r"(?:(?:推荐|建议|本章|本目录|这章的)?阅读顺序|接下来怎么读)[？?]?", label):
                section_level = level
            continue
        if section_level is None:
            continue
        item = re.match(r"^\s*\d+[.)、]\s+\[([^\]]+)\]\(([^)]+)\)", line)
        if not item:
            continue
        target = urlsplit(unescape(item.group(2)))
        if target.scheme or target.netloc or not target.path:
            continue
        path = (directory / unquote(target.path)).resolve()
        if path.parent == directory.resolve() and path.is_file() and path.suffix.lower() == ".md" and path.name not in {"README.md", "SUMMARY.md"} and all(name != path.name for name, _ in items):
            items.append((path.name, unescape(item.group(1)).strip()))
    return items


def reading_order(directory):
    """Use an index's explicit numbered reading list for sibling articles."""
    return [name for name, _ in reading_items(directory)]


def ram_sidebar_labels(root):
    """Use RAM chapter reading-list labels as concise sidebar names."""
    labels = {}
    wiki = root / "RAM" / "wiki"
    for chapter in sorted(path for path in wiki.iterdir() if path.is_dir()):
        index = chapter / "README.md"
        if not index.is_file():
            continue
        metadata = re.search(r"^<!--\s*nav-title:\s*(.+?)\s*-->\s*$", index.read_text(encoding="utf-8"), re.MULTILINE)
        if metadata:
            labels[index.relative_to(root).as_posix()] = (metadata.group(1), title(index))
        for filename, label in reading_items(chapter):
            path = chapter / filename
            labels[path.relative_to(root).as_posix()] = (label, title(path))
    return labels


def make_tree(directory, root):
    items = []
    index = directory / "README.md"
    if index.is_file():
        items.append(index.relative_to(root).as_posix())
    summary = directory / "SUMMARY.md"
    if summary.is_file():
        items.append({"知识地图": summary.relative_to(root).as_posix()})
    priority = {name: number for number, name in enumerate(reading_order(directory))}
    for path in sorted(directory.iterdir(), key=lambda p: (priority.get(p.name, len(priority)), p.name.lower())):
        if path.is_dir():
            if not any(path.rglob("*.md")):
                continue
            section_index = path / "README.md"
            label = title(section_index) if section_index.exists() else path.name
            items.append({label: make_tree(path, root)})
        elif path.is_file() and path.suffix.lower() == ".md" and path.name not in {"README.md", "SUMMARY.md"}:
            items.append(path.relative_to(root).as_posix())
    return items


def topic_tree(root, name):
    """Include the topic's wiki and any published companion documents."""
    items = make_tree(root / name / "wiki", root)
    for filename, label in (("self-test-questions.md", "自测问题"), ("README.md", "专题仓库说明")):
        path = root / name / filename
        if path.is_file():
            items.append({label: path.relative_to(root).as_posix()})
    return items


def breadcrumb_ancestors(page):
    """Find ancestor sections and their landing pages, when available."""
    ancestors = []
    parent = page.parent
    while parent:
        index = next((item for item in parent.children if item.is_page and item.is_index), None)
        if parent.title == "微架构":
            index = next((item for item in parent.children if item.is_page and item.file.src_uri == "microarchitecture.md"), None)
        if index is None or index.file.src_uri != page.file.src_uri:
            ancestors.append((parent.title, index))
        parent = parent.parent
    return list(reversed(ancestors))


def strip_duplicate_parent(markdown, page, root):
    """Hide an introductory parent link only when breadcrumbs already contain it."""
    ancestors = {index.file.src_uri for _, index in breadcrumb_ancestors(page) if index is not None}
    lines = markdown.splitlines(keepends=True)
    for number, line in enumerate(lines[:8]):
        match = re.match(r"^\s*上级[：:]\s*\[[^\]]+\]\(([^)]+)\)\s*$", line)
        if not match:
            continue
        target = urlsplit(unescape(match.group(1)))
        if target.scheme or target.netloc or not target.path:
            continue
        path = posixpath.normpath(posixpath.join(str(PurePosixPath(page.file.src_uri).parent), unquote(target.path)))
        if (root / path).is_dir():
            path = posixpath.join(path, "README.md")
        if path in ancestors:
            del lines[number]
        break
    return "".join(lines)


def render_breadcrumbs(page, root, sidebar_labels=None):
    """Render links to real ancestor pages and the current article title."""
    items = [("首页", "/")]
    sidebar_labels = sidebar_labels or {}
    items.extend((sidebar_labels.get(index.file.src_uri, (label,))[0] if index is not None else label,
                  index.url if index is not None else None) for label, index in breadcrumb_ancestors(page))
    links = [
        ('<li><a href="{}">{}</a></li>'.format(escape(get_relative_url(url, page.url), quote=True), escape(label))
         if url is not None else '<li><span>{}</span></li>'.format(escape(label)))
        for label, url in items
    ]
    links.append('<li><span aria-current="page">{}</span></li>'.format(escape(title(root / page.file.src_uri))))
    return '<nav class="site-breadcrumbs" aria-label="面包屑导航"><ol>{}</ol></nav>'.format("".join(links))


def has_breadcrumbs(page):
    return page.file.src_uri not in {"README.md", "series.md", "microarchitecture.md", "articles.md", "visuals.md"}


def on_config(config, **kwargs):
    root = Path(config.docs_dir)
    read_series(root)
    config.extra["ram_sidebar_labels"] = ram_sidebar_labels(root)
    # These files use stable paths. A content-derived query prevents browsers
    # from combining freshly deployed HTML with a cached older CSS/JS file.
    for setting in ("extra_css", "extra_javascript"):
        paths = []
        for asset in getattr(config, setting):
            asset_path, _, query = asset.partition("?")
            path = root / asset_path
            if path.is_file():
                version = sha256(path.read_bytes()).hexdigest()[:12]
                params = [part for part in query.split("&") if part and not part.startswith("v=")]
                paths.append(f"{asset_path}?{'&'.join(params + [f'v={version}'])}")
            else:
                paths.append(asset)
        setattr(config, setting, paths)
    config.nav = [
        {"首页": "README.md"},
        {"系列": "series.md"},
        {"微架构": [
            {"微架构首页": "microarchitecture.md"},
            {"精选文章": "articles.md"},
            {"互动图解": "visuals.md"},
            {"基础": ["electrical-timing-foundations.md"]},
            {"专题": [{label: topic_tree(root, name)} for name, label in TOPICS]},
            {"评审记录": [
                {"九专题基线问题": "reviews/2026-11-09-topic-review.md"},
                {"第二轮逐篇评审": make_tree(root / "reviews" / "round-2", root)},
                {"第三轮有限资源盲测": make_tree(root / "reviews" / "round-3", root)},
            ]},
        ]},
    ]
    return config


def on_nav(nav, config, files, **kwargs):
    """Resolve source paths to generated URLs for sidebar labels."""
    labels = config.extra.get("ram_sidebar_labels", {})
    config.extra["ram_sidebar_urls"] = {
        file.url: labels[path]
        for path in labels
        if (file := files.get_file_from_path(path)) is not None
    }
    return nav


def on_page_markdown(markdown, page, **kwargs):
    """Add website interactions while keeping Markdown usable on GitHub."""
    if has_breadcrumbs(page):
        markdown = strip_duplicate_parent(markdown, page, Path(kwargs["config"].docs_dir))
    if page.file.src_uri == "README.md":
        config = kwargs["config"]
        markdown = markdown.replace("__SITE_NAME__", escape(config.site_name))
        markdown = markdown.replace("<!-- site-series -->", render_series(read_series(Path(config.docs_dir))))
    elif page.file.src_uri == "series.md":
        config = kwargs["config"]
        markdown = markdown.replace("<!-- site-series -->", render_series(read_series(Path(config.docs_dir)), "../"))

    if page.file.src_uri == "RAM/wiki/01-overview/README.md":
        template = (Path(__file__).parent / "partials" / "ram-overview-demo.html").read_text(encoding="utf-8")
        markdown = markdown.replace("<!-- ram-overview-demo -->", template)

    if page.file.src_uri == "RAM/wiki/02-sram-foundations/6t-cell-bistable-storage.md":
        template = (Path(__file__).parent / "partials" / "sram-demo.html").read_text(encoding="utf-8")
        for mode, number, heading, intro, label in (
            ("read", "01", "一次读操作", "初始状态：Q = 1，QB = 0。观察位线预充、差分形成和感测。", "读：Q = 1"),
            ("write", "02", "把 Q 从 1 写成 0", "初始状态：Q = 1，QB = 0。观察写驱动如何推动 cell 翻转。", "写：Q 1 → 0"),
        ):
            demo = template
            for key, value in (("MODE", mode), ("NUMBER", number), ("TITLE", heading), ("INTRO", intro), ("LABEL", label)):
                demo = demo.replace(f"__{key}__", value)
            markdown = markdown.replace(f"<!-- sram-{mode}-demo -->", demo)

    visual_links = {
        "RAM/wiki/05-dram-protocol-families/commands-act-rd-wr-pre.md": (
            "观察 DRAM 的 ACT、RD 和显式 PRE 阶段", "dram"
        ),
        "DMA/wiki/04-programming-model/tiling-double-buffering.md": (
            "观察双缓冲中搬运与计算重叠的时间线", "double-buffer"
        ),
    }
    selected = visual_links.get(page.file.src_uri)
    if not selected:
        return markdown
    label, anchor = selected
    lines = markdown.splitlines(keepends=True)
    link = f"\n> 互动图解：[{label}](../../../visuals.md#{anchor})。\n\n"
    return lines[0] + link + "".join(lines[1:]) if lines else markdown


def on_page_content(html, page, **kwargs):
    """Add article breadcrumbs and scope customized article layouts."""
    if page.file.src_uri == "electrical-timing-foundations.md":
        html = f'<div class="timing-article">\n{html}\n</div>'
    elif page.file.src_uri == "RAM/wiki/01-overview/README.md":
        html = f'<div class="ram-overview-article">\n{html}\n</div>'
    elif page.file.src_uri in {
        "RAM/wiki/01-overview/problem-statement.md",
        "RAM/wiki/01-overview/memory-hierarchy-tension.md",
        "RAM/wiki/01-overview/taxonomy.md",
        "RAM/wiki/01-overview/locality-working-set-data-movement.md",
        "RAM/wiki/01-overview/sram-dram-divergence.md",
        "RAM/wiki/01-overview/learning-roadmap.md",
    }:
        html = f'<div class="ram-problem-article">\n{html}\n</div>'
    if has_breadcrumbs(page):
        config = kwargs["config"]
        html = render_breadcrumbs(page, Path(config.docs_dir), config.extra.get("ram_sidebar_labels")) + "\n" + html
    return html


def on_post_page(output, page, **kwargs):
    """Shorten RAM sidebar labels and expose the current page accessibly."""
    labels = kwargs["config"].extra.get("ram_sidebar_urls", {})
    start = output.find('<div class="md-sidebar md-sidebar--primary"')
    end = output.find('<div class="md-sidebar md-sidebar--secondary"', start)
    if labels and start >= 0 and end >= 0:
        link = re.compile(r'(<a\s+href="([^"]+)"\s+class="[^"]*\bmd-nav__link\b[^"]*"[^>]*)(>\s*<span class="md-ellipsis">)(.*?)(</span>\s*</a>)', re.DOTALL)

        def shorten(match):
            target = urlsplit(urljoin("https://navigation.invalid/" + page.url, unescape(match.group(2))))
            if target.netloc != "navigation.invalid" or target.fragment:
                return match.group(0)
            label = labels.get(unquote(target.path).lstrip("/"))
            if not label or label[0] == label[1]:
                return match.group(0)
            short, full = label
            return '{} title="{}" aria-label="{}"{}{}{}'.format(
                match.group(1), escape(full, quote=True), escape(full, quote=True),
                match.group(3), escape(short), match.group(5),
            )

        output = output[:start] + link.sub(shorten, output[start:end]) + output[end:]
    active_link = r'(<a\b[^>]*\bclass="[^"]*\bmd-nav__link--active\b[^"]*"[^>]*)(>)'
    return re.sub(active_link, lambda match: match.group(0) if "aria-current=" in match.group(1) else match.group(1) + ' aria-current="page"' + match.group(2), output)
