"""Build navigation and breadcrumbs from the wiki's chapter directories."""

from html import escape, unescape
from hashlib import sha256
from pathlib import Path, PurePosixPath
import posixpath
import re
import sys
from urllib.parse import quote, unquote, urljoin, urlsplit

from markdown.extensions.toc import slugify_unicode
from mkdocs.utils import get_relative_url
from mkdocs.structure.pages import Page

_WEBSITE = str(Path(__file__).resolve().parent)
if _WEBSITE not in sys.path:
    sys.path.insert(0, _WEBSITE)
from sources import load_series, series_landing  # noqa: E402
from ownership import GROUPS, MICRO, STORAGE, INTERCONNECT, DEVELOPMENT, owner, development_owner  # noqa: E402
from inference import navigation as inference_navigation  # noqa: E402
from workload import navigation as workload_navigation  # noqa: E402
from storage_navigation import (INTEGRATION_AFTER, INTEGRATION_HOME, INTEGRATION_PACKAGING,
                                INTEGRATION_TOPIC, MEMORY_HOME, MEMORY_SECTIONS, MEMORY_TOPIC,
                                RESOURCE_HOME, RESOURCE_SECTIONS, STORAGE_RESOURCES, SYSTEM_SELECTION)  # noqa: E402
from microarchitecture_navigation import micro_navigation  # noqa: E402
from noc_navigation import NOC_SUMMARY, noc_topic_tree, read_noc_sections  # noqa: E402
from d2d_navigation import D2D_SUMMARY, d2d_topic_tree, read_d2d_sections  # noqa: E402


COMMON_FOUNDATIONS = "共同基础"
CHIP_ARCHITECTURES = "series/chip-architectures"
CHIP_ARCHITECTURES_HOME = f"{CHIP_ARCHITECTURES}/README.md"

TOPICS = (
    ("RAM", "RAM · 存储系统"),
    ("COMPUTE", "COMPUTE · 计算"),
    ("BUS", "BUS · 片上总线"),
    ("NOC", "NoC · 片上网络"),
    ("D2D", "芯粒间连接"),
    ("DMA", "DMA · 数据搬运"),
    ("PCIE", "PCIe · 主机互连"),
    ("COHERENCE", "一致性与内存互连"),
    ("SCALEUP", "加速器间通信"),
    ("NETWORK", "服务器与集群网络"),
    ("CIM", "CIM · 存内计算"),
    ("CPO", "CPO · 光互连"),
    ("FAB", "FAB · 制造与封装"),
    ("SERDES", "SerDes · 高速串行链路"),
    ("HBF", "HBF · 高带宽闪存"),
)

# Illustrations belong to series landing pages; article sources remain usable
# outside the site and retain their original headings and links.
SERIES_COVERS = {
    "microarchitecture.md": (
        "microarchitecture.svg", "微架构 / 系列首页", "执行、搬运、同步与资源",
        "计算、存储、互连与外部存储构成芯片的数据路径。", "",
    ),
    "storage.md": (
        "storage.svg", "存储系统 / 系列首页", "计算、缓存、控制器与 DRAM",
        "计算请求经过 cache 和控制器访问 DRAM，数据沿路径返回。", "",
    ),
    "interconnect.md": (
        "interconnect.svg", "芯片与系统互连 / 系列首页", "端点、片上网络与链路",
        "请求从一个端点经过片上互连与链路，到达另一个端点。", "",
    ),
    "external/workload-wiki/README.md": (
        "workload.svg", "算法与模型 / 系列首页", "输入、模型、输出与计算需求",
        "输入经过模型得到输出，并可进一步分析计算和数据需求。", "",
    ),
    "series/inference-runtime/README.md": (
        "inference.svg", "推理运行时 / 系列首页", "请求、调度、Prefill、Decode 与 KV cache",
        "推理请求经过调度、预填充和解码，执行时使用 KV cache。",
        "从推理阶段、请求调度和 KV cache 出发，理解模型如何提供服务。",
    ),
    "series/chip-architectures/README.md": (
        "architectures.svg", "芯片架构实例 / 系列首页", "计算、存储和互连的不同组织",
        "三个抽象示意展示计算阵列、片上存储与互连的不同组织。", "",
    ),
    "series/chip-development/README.md": (
        "development.svg", "芯片开发与实现 / 系列首页", "定义、设计、验证、制造与测试",
        "芯片开发从产品定义、设计和验证，延伸到制造、测试和交付。", "",
    ),
}


def render_series_cover(html, page, docs):
    """Frame the existing first heading and introduction with a themed figure."""
    cover = SERIES_COVERS.get(page.file.src_uri)
    if cover is None:
        return html
    match = re.match(r"\s*(<h1\b[^>]*>.*?</h1>)\s*(<p(?:\s[^>]*)?>.*?</p>)?", html, re.DOTALL)
    if not match:
        return html
    asset, label, caption, alt, fallback = cover
    heading, lead = match.group(1), match.group(2)
    intro = lead or (f"<p>{escape(fallback)}</p>" if fallback else "")
    source = get_relative_url(f"assets/images/series-covers/{asset}", page.url)
    version = sha256((docs / "assets" / "images" / "series-covers" / asset).read_bytes()).hexdigest()[:12]
    source = f"{source}?v={version}"
    return (
        '<section class="series-cover">'
        '<div class="series-cover-copy">'
        f'<p class="series-cover-label"><span aria-hidden="true"></span>{escape(label)}</p>'
        f'{heading}{intro}'
        '<a class="series-cover-action" href="#series-home-content">浏览系列内容 <span aria-hidden="true">↘</span></a>'
        '</div><figure class="series-cover-art">'
        f'<img src="{escape(source, quote=True)}" alt="{escape(alt, quote=True)}">'
        f'<figcaption><span>FIG. 01</span> {escape(caption)} · 概念示意</figcaption>'
        '</figure></section>'
        f'<div class="series-home-content" id="series-home-content">{html[match.end():]}</div>'
    )


def read_series(root, registry=None):
    """Read the registry staged together with the site's source documents."""
    registry = registry or root.parent / "series.json"
    entries = load_series(registry)
    result = []
    for item in entries:
        name = item["title"].strip()
        description = item["description"].strip()
        source = item.get("source")
        local = item.get("local")
        page, url = item.get("page"), item.get("url")
        if source:
            landing = series_landing(root / "external" / source["slug"])
            page = landing.relative_to(root).as_posix()
        elif local:
            landing = series_landing(root / local["publish"])
            page = landing.relative_to(root).as_posix()
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
        result.append({"title": name, "description": description, "href": href, "target": target, "source": source, "local": local})
    return result


def render_series(entries):
    """Render public links; the empty future tile is presentational only."""
    cards = []
    for index, entry in enumerate(entries, 1):
        cards.append(
            '<a class="portal-series-card" href="{}">'
            '<span class="portal-card-number">SERIES / {:02d}</span>'
            '<span class="portal-card-arrow" aria-hidden="true">↗</span>'
            '<h3>{}</h3><p>{}</p><span class="portal-card-link">进入系列 →</span></a>'.format(
                escape(entry["href"], quote=True), index,
                escape(entry["title"]), escape(entry["description"]),
            )
        )
    return "\n".join(cards)


def title(path):
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^#\s+(.+?)\s*$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else path.stem.replace("-", " ")


def reading_items(directory, index_name="README.md", article_directory=None, include_subdirs=False):
    """Read labels and targets from an index's numbered reading list.

    CPO also orders immediate child sections by linking to their README.
    Other topics retain the original sibling-article behavior.
    """
    index = directory / index_name
    article_directory = article_directory or directory
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
        name = None
        if path.is_file() and path.suffix.lower() == ".md":
            if path.parent == article_directory.resolve() and path.name not in {index_name, "README.md", "SUMMARY.md"}:
                name = path.name
            elif include_subdirs and path.name == "README.md" and path.parent.parent == article_directory.resolve():
                name = path.parent.name
        if name and all(existing != name for existing, _ in items):
            items.append((name, unescape(item.group(1)).strip()))
    return items


def reading_order(directory, index_name="README.md"):
    """Use an index's explicit numbered reading list for sibling articles."""
    return [name for name, _ in reading_items(directory, index_name)]


def storage_sidebar_labels(root):
    """Use storage reading-list labels as concise sidebar names."""
    labels = {}
    wiki = root / "RAM" / "wiki"
    chapters = sorted(path for path in wiki.iterdir() if path.is_dir())
    hbf = root / "HBF" / "wiki"
    if hbf.is_dir():
        chapters.append(hbf)
    for chapter in chapters:
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


def make_tree(directory, root, index_names=("README.md",), include=None, *, order_subdirs=False):
    items = []
    include = include or (lambda path: True)
    indexes = [directory / name for name in index_names if (directory / name).is_file()]
    if len(indexes) > 1:
        raise ValueError(f"Directory has more than one index page: {directory}")
    index = indexes[0] if indexes else None
    if index and include(index):
        items.append(index.relative_to(root).as_posix())
    summary = directory / "SUMMARY.md"
    if summary.is_file() and include(summary):
        items.append({"知识地图": summary.relative_to(root).as_posix()})
    is_cpo = directory.relative_to(root).parts[:2] == ("CPO", "wiki")
    ordered = reading_items(directory, index.name if index else "README.md",
                            include_subdirs=is_cpo or order_subdirs)
    priority = {name: number for number, (name, _label) in enumerate(ordered)}
    for path in sorted(directory.iterdir(), key=lambda p: (priority.get(p.name, len(priority)), p.name.lower())):
        if path.is_dir():
            if not any(path.rglob("*.md")):
                continue
            section_index = next((path / name for name in index_names if (path / name).is_file()), None)
            label = title(section_index) if section_index else path.name
            # Material also uses the section label as the mobile drawer title;
            # changing only the chapter link leaves that title unshortened.
            if section_index and section_index.relative_to(root).parts[:2] in (("SERDES", "wiki"), ("CPO", "wiki")):
                metadata = re.search(r"^<!--\s*nav-title:\s*(.+?)\s*-->\s*$", section_index.read_text(encoding="utf-8"), re.MULTILINE)
                if metadata:
                    label = metadata.group(1)
            children = make_tree(path, root, index_names, include, order_subdirs=order_subdirs)
            if children:
                items.append({label: children})
        elif path.is_file() and path.suffix.lower() == ".md" and path.name not in {*index_names, "SUMMARY.md"} and include(path):
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


COHERENCE_CHAPTERS = (
    ("01-foundations", "01-foundations/README.md"),
    ("02-protocols", "02-protocols/README.md"),
    ("03-chi", "03-chi/README.md"),
    ("04-cxl", "cxl-host-memory.md"),
    ("05-performance-reliability", "05-performance-reliability/README.md"),
    ("06-reference", "06-reference/README.md"),
)


def coherence_sections(root):
    """Chapter reading lists own order; the CXL guide keeps its public path."""
    wiki = root / "COHERENCE/wiki"
    if not wiki.is_dir():
        return []
    # Minimal staging fixtures may contain only the topic landing page.
    if {path.relative_to(wiki).as_posix() for path in wiki.rglob("*.md")} == {"README.md"}:
        return []
    sections = []
    assigned = {"COHERENCE/wiki/README.md"}
    for directory, guide in COHERENCE_CHAPTERS:
        index = wiki / guide
        text = index.read_text(encoding="utf-8")
        metadata = re.search(r"^<!--\s*nav-title:\s*(.+?)\s*-->\s*$", text, re.MULTILINE)
        label = metadata.group(1) if metadata else title(index)
        pages = [(label, index.relative_to(root).as_posix())]
        pages.extend((short, (wiki / directory / name).relative_to(root).as_posix())
                     for name, short in reading_items(index.parent, index.name, wiki / directory))
        for _short, path in pages:
            if path in assigned:
                raise ValueError(f"Duplicate coherence navigation page: {path}")
            assigned.add(path)
        sections.append((label, pages))
    expected = {path.relative_to(root).as_posix() for path in wiki.rglob("*.md")}
    if assigned != expected:
        raise ValueError(f"Coherence navigation coverage: missing={sorted(expected - assigned)}, extra={sorted(assigned - expected)}")
    return sections


def coherence_topic_tree(root):
    sections = coherence_sections(root)
    if not sections:
        return ["COHERENCE/wiki/README.md"] if (root / "COHERENCE/wiki/README.md").is_file() else []
    return ["COHERENCE/wiki/README.md", *({label: [path for _, path in pages]} for label, pages in sections)]


def owned_topic_tree(root, name, series, group, exclude=()):
    """Keep each original page in its one designated main topic."""
    include = lambda path: (path.relative_to(root).as_posix() not in exclude
                            and owner(path.relative_to(root).as_posix()) == (series, group))
    if not (root / name / "wiki").is_dir():
        return []
    items = make_tree(root / name / "wiki", root, include=include)
    for filename, label in (("self-test-questions.md", "自测问题"), ("README.md", "专题仓库说明")):
        path = root / name / filename
        if path.is_file() and include(path):
            items.append({label: path.relative_to(root).as_posix()})
    return items


def compact_storage_sections(items):
    """Omit source-directory sections that contain only one retained page."""
    compact = []
    for item in items:
        if isinstance(item, dict) and len(item) == 1:
            label, children = next(iter(item.items()))
            if isinstance(children, list):
                children = compact_storage_sections(children)
                compact.append(children[0] if len(children) == 1 else {label: children})
                continue
        compact.append(item)
    return compact


def storage_sections(root, sections):
    """Build ordered sections from pages that exist in this staging tree."""
    result = []
    for label, _directory, pages in sections:
        entries = [{short: page} for short, page in pages if (root / page).is_file()]
        if entries:
            result.append({label: entries})
    return result


def storage_memory_tree(root):
    entries = [{"专题首页": MEMORY_HOME}] if (root / MEMORY_HOME).is_file() else []
    return entries + storage_sections(root, MEMORY_SECTIONS)


def storage_integration_tree(root):
    """Present source-aligned integration sections while retaining published URLs."""
    entries = [{INTEGRATION_TOPIC: INTEGRATION_HOME}] if (root / INTEGRATION_HOME).is_file() else []
    if (root / SYSTEM_SELECTION).is_file():
        entries.append({"不同系统的存储选型": SYSTEM_SELECTION})
    packaging = [{label: path} for label, path in INTEGRATION_PACKAGING if (root / path).is_file()]
    if packaging:
        entries.append({"封装与集成": packaging})
    entries.extend({label: path} for label, path in INTEGRATION_AFTER if (root / path).is_file())
    return entries


def storage_resources_tree(root):
    entries = [{STORAGE_RESOURCES: RESOURCE_HOME}] if (root / RESOURCE_HOME).is_file() else []
    sections = storage_sections(root, RESOURCE_SECTIONS)
    return [{STORAGE_RESOURCES: entries + sections}] if entries or sections else []


CPO_SECTIONS = (
    ("技术与工程", ("01-overview", "03-architecture-platform", "04-optical-engine",
                    "05-electrical-thermal-reliability", "06-manufacturing", "07-applications-economics")),
    ("产业与公司", ("02-industry", "09-supply-chain-geography", "10-company-ecosystem",
                    "11-deep-company-cards", "12-conclusions-competition", "15-china-opportunities",
                    "18-sources-and-updates")),
    ("学习与查阅", ("08-research", "13-one-page-summary", "14-indexes", "16-learning-navigation")),
    ("维护与模板", ("17-report-template", "19-versioning-and-usage", "20-editorial-style")),
)


def cpo_topic_tree(root, group):
    """Group CPO chapters without moving or excluding any existing pages."""
    tree = owned_topic_tree(root, "CPO", INTERCONNECT, group)
    section_for_title = {}
    for label, directories in CPO_SECTIONS:
        for directory in directories:
            index = root / "CPO" / "wiki" / directory / "README.md"
            if index.is_file():
                metadata = re.search(r"^<!--\s*nav-title:\s*(.+?)\s*-->\s*$", index.read_text(encoding="utf-8"), re.MULTILINE)
                section_for_title[metadata.group(1) if metadata else title(index)] = label
    grouped = {label: [] for label, _ in CPO_SECTIONS}
    ungrouped = []
    for item in tree:
        label = next(iter(item)) if isinstance(item, dict) and len(item) == 1 else None
        if label in section_for_title and isinstance(item[label], list):
            grouped[section_for_title[label]].append(item)
        else:
            ungrouped.append(item)
    return ungrouped + [{label: grouped[label]} for label, _ in CPO_SECTIONS if grouped[label]]


def grouped_original_topics(root, series):
    result = []
    for group in GROUPS[series]:
        if series == STORAGE and group == MEMORY_TOPIC:
            entries = storage_memory_tree(root)
            if entries:
                result.append({group: entries})
            continue
        if series == STORAGE and group == INTEGRATION_TOPIC:
            entries = storage_integration_tree(root)
            if entries:
                result.append({group: entries})
            continue
        entries = []
        if (series, group) == owner("electrical-timing-foundations.md"):
            entries.append("electrical-timing-foundations.md")
        for name, label in TOPICS:
            if series == INTERCONNECT and group == "片上网络（NoC）" and name == "NOC":
                tree = noc_topic_tree(root)
            elif series == INTERCONNECT and group == "封装内芯粒互连" and name == "D2D":
                tree = d2d_topic_tree(root)
            elif series == INTERCONNECT and group == "一致性与内存互连" and name == "COHERENCE":
                tree = coherence_topic_tree(root)
            elif series == INTERCONNECT and group == "共封装光学（CPO）" and name == "CPO":
                tree = cpo_topic_tree(root, group)
            else:
                tree = owned_topic_tree(root, name, series, group)
            if tree:
                if series == STORAGE:
                    entries.extend(compact_storage_sections(tree))
                elif series == INTERCONNECT:
                    entries.extend(tree)
                else:
                    entries.append({label: tree})
        # A sole directory around a whole storage topic repeats the topic's
        # label (for example, DRAM controller / Memory Controller).
        if series == STORAGE and len(entries) == 1 and isinstance(entries[0], dict):
            children = next(iter(entries[0].values()))
            if isinstance(children, list):
                entries = children
        if entries:
            result.append({group: entries})
    return result


def workload_tree(root, directory, labels=None):
    tree = workload_navigation(root)
    result = [tree[0]]

    def sidebar_pages(entries):
        pages = []
        for entry in entries:
            short, target = next(iter(entry.items()))
            if isinstance(target, list):
                pages.append({short: sidebar_pages(target)})
            else:
                if labels is not None:
                    labels[target] = (short, title(root / target))
                pages.append(target)
        return pages

    for group in tree[1:]:
        label, entries = next(iter(group.items()))
        if labels is not None:
            labels[entries[0]] = (label, title(root / entries[0]))
        result.append({label: [entries[0], *sidebar_pages(entries[1:])]})
    return result


def compact_development_sections(items, labels):
    """Keep source chapters with a guide in this topic, and lift moved pages."""
    compact = []
    for item in items:
        if isinstance(item, str):
            compact.append(item)
            continue
        label, children = next(iter(item.items()))
        if isinstance(children, str):
            compact.append(item)
            continue
        guide = children[0]
        contents = compact_development_sections(children, labels)
        if (len(contents) > 1 and isinstance(guide, str)
                and PurePosixPath(guide).name in {"README.md", "index.md"}):
            compact.append({labels.get(guide, (label,))[0]: contents})
        else:
            compact.extend(contents)
    return compact


def development_tree(root, directory, labels):
    landing = series_landing(directory)
    fab = root / "FAB" / "wiki"
    for source in (directory, fab):
        for index in sorted(source.rglob("README.md")):
            for name, short in reading_items(index.parent, include_subdirs=True):
                path = index.parent / name
                if path.is_dir():
                    path = path / "README.md"
                labels[path.relative_to(root).as_posix()] = (short, title(path))

    result = [landing.relative_to(root).as_posix()]
    for group in GROUPS[DEVELOPMENT]:
        include = lambda path, g=group: path != landing and development_owner(path.relative_to(directory).as_posix()) == g
        entries = make_tree(directory, root, ("README.md", "index.md"), include, order_subdirs=True)
        if fab.is_dir():
            entries.extend(make_tree(
                fab, root,
                include=lambda path: owner(path.relative_to(root).as_posix()) == (DEVELOPMENT, group),
                order_subdirs=True,
            ))
        entries = compact_development_sections(entries, labels)
        if len(entries) == 1 and isinstance(entries[0], dict) and group in entries[0]:
            entries = entries[0][group]
        if entries:
            result.append({group: entries})
    expected = {
        path.relative_to(root).as_posix()
        for source in (directory, fab)
        for path in source.rglob("*.md")
    }
    assigned = validate_unique_navigation(result)
    if assigned != expected:
        raise ValueError(f"Chip development navigation mismatch: missing={sorted(expected - assigned)}, "
                         f"extra={sorted(assigned - expected)}")
    return result


def inference_tree(root, directory, labels):
    tree = inference_navigation(root)
    result = [tree[0]]
    for section in tree[1:]:
        label, entries = next(iter(section.items()))
        pages = []
        for entry in entries:
            short, path = next(iter(entry.items())) if isinstance(entry, dict) else (label, entry)
            if isinstance(entry, dict) or path.endswith("/README.md"):
                labels[path] = (short, title(root / path))
            pages.append(path)
        result.append({label: pages})
    return result


def chip_architecture_tree(root, directory, labels):
    """Use the series guide's numbered lists as the product navigation."""
    landing = directory / "README.md"
    remaining = {path.relative_to(directory).as_posix() for path in directory.rglob("*.md") if path != landing}
    groups = {}
    group = None
    for line in landing.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            group = line[3:].strip()
            continue
        item = re.match(r"^\d+\. \[([^\]]+)\]\(([^)]+)\)", line)
        if not item:
            continue
        short, target = item.groups()
        if not group or target not in remaining:
            raise ValueError(f"Invalid or repeated chip architecture entry: {target}")
        remaining.remove(target)
        path = (directory / target).relative_to(root).as_posix()
        groups.setdefault(group, []).append(path)
        labels[path] = (short, title(root / path))
    if remaining:
        raise ValueError(f"Chip architecture guide omits articles: {sorted(remaining)}")
    return [landing.relative_to(root).as_posix(), *({name: pages} for name, pages in groups.items())]


def breadcrumb_ancestors(page):
    """Find ancestor sections and their landing pages, when available."""
    ancestors = []
    parent = page.parent
    while parent:
        index = next((item for item in parent.children if item.is_page and item.is_index), None)
        landing = {"微架构": "microarchitecture.md", "存储系统": "storage.md", "芯片与系统互连": "interconnect.md"}.get(parent.title)
        if landing:
            index = next((item for item in parent.children if item.is_page and item.file.src_uri == landing), None)
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
            if path not in ancestors and (root / path).is_file() and not target.query and not target.fragment:
                lines[number] = line.replace(match.group(1), target.path.rstrip("/") + "/README.md")
        if path in ancestors:
            del lines[number]
        break
    return "".join(lines)


def label_noc_original_parent(markdown, page, root, legacy_pages):
    """Keep old source links, while distinguishing them from the new group."""
    if not page.file.src_uri.startswith("NOC/wiki/"):
        return markdown
    lines = markdown.splitlines(keepends=True)
    for number, line in enumerate(lines[:8]):
        match = re.match(r"^(\s*)上级[：:]\s*\[[^\]]+\]\(([^)]+)\)\s*$", line)
        if not match:
            continue
        target = urlsplit(unescape(match.group(2)))
        if target.scheme or target.netloc or not target.path:
            break
        path = posixpath.normpath(posixpath.join(str(PurePosixPath(page.file.src_uri).parent), unquote(target.path)))
        if (root / path).is_dir():
            path = posixpath.join(path, "README.md")
        if path in legacy_pages:
            lines[number] = re.sub(r"^(\s*)上级[：:]", r"\1原章节：", line, count=1)
        break
    return "".join(lines)


def render_breadcrumbs(page, root, sidebar_labels=None):
    """Render links to real ancestor pages and the current article title."""
    items = [("首页", "/")]
    sidebar_labels = sidebar_labels or {}
    storage_groups = {MEMORY_TOPIC, STORAGE_RESOURCES, *(name for name, _, _ in MEMORY_SECTIONS),
                      *(name for name, _, _ in RESOURCE_SECTIONS)}
    for label, index in breadcrumb_ancestors(page):
        if index is None:
            url = "/#common-foundations" if label == COMMON_FOUNDATIONS else None
            if page.file.src_uri.startswith(f"{CHIP_ARCHITECTURES}/"):
                url = f"{CHIP_ARCHITECTURES}/#{quote(slugify_unicode(label, '-'))}"
        else:
            path = index.file.src_uri
            if path == "README.md":
                continue
            url = index.url
            if label not in storage_groups:
                label = sidebar_labels.get(path, (label,))[0]
        items.append((label, url))
    links = [
        ('<li><a href="{}">{}</a></li>'.format(escape(get_relative_url(url, page.url), quote=True), escape(label))
         if url is not None else '<li><span>{}</span></li>'.format(escape(label)))
        for label, url in items
    ]
    links.append('<li><span aria-current="page">{}</span></li>'.format(escape(title(root / page.file.src_uri))))
    return '<nav class="site-breadcrumbs" aria-label="面包屑导航"><ol>{}</ol></nav>'.format("".join(links))


def has_breadcrumbs(page):
    return page.file.src_uri not in {"README.md", "microarchitecture.md", "storage.md", "interconnect.md", "articles.md", "visuals.md"}


def validate_unique_navigation(entries):
    """A page may have many reading links but only one main navigation entry."""
    seen = set()
    def visit(item):
        if isinstance(item, list):
            for child in item:
                visit(child)
        elif isinstance(item, dict):
            for child in item.values():
                visit(child)
        elif isinstance(item, str) and item.endswith(".md"):
            if item in seen:
                raise ValueError(f"Page has more than one main navigation entry: {item}")
            seen.add(item)
    visit(entries)
    return seen


def validate_storage_navigation(root, entries):
    """Do not silently publish a storage page without its main navigation."""
    assigned = set()

    def collect(item):
        if isinstance(item, str) and item.endswith(".md"):
            assigned.add(item)
        elif isinstance(item, dict):
            for value in item.values():
                collect(value)
        elif isinstance(item, list):
            for value in item:
                collect(value)

    collect(entries)
    expected = {
        path.relative_to(root).as_posix()
        for directory in ("RAM/wiki", "HBF/wiki", "COMPUTE/wiki/06-memory-discipline")
        for path in (root / directory).rglob("*.md")
    }
    for name in ("RAM", "HBF"):
        for filename in ("README.md", "self-test-questions.md"):
            path = root / name / filename
            if path.is_file():
                expected.add(path.relative_to(root).as_posix())
    if assigned != expected:
        raise ValueError(f"Storage navigation does not cover pages: missing={sorted(expected - assigned)}, extra={sorted(assigned - expected)}")


def on_config(config, **kwargs):
    root = Path(config.docs_dir)
    series = read_series(root)
    config.extra["storage_sidebar_labels"] = storage_sidebar_labels(root)
    # The storage source groups may merge several preserved URL directories.
    # Use their declared order and labels rather than the old chapter indexes.
    for _name, _directory, pages in (*MEMORY_SECTIONS, *RESOURCE_SECTIONS):
        for short, path in pages:
            if (root / path).is_file():
                config.extra["storage_sidebar_labels"][path] = (short, title(root / path))
    if (root / MEMORY_HOME).is_file():
        # Material uses the topic's index page as its clickable section title.
        config.extra["storage_sidebar_labels"][MEMORY_HOME] = (MEMORY_TOPIC, title(root / MEMORY_HOME))
    if (root / RESOURCE_HOME).is_file():
        config.extra["storage_sidebar_labels"][RESOURCE_HOME] = (STORAGE_RESOURCES, title(root / RESOURCE_HOME))
    for short, path in (("不同系统的存储选型", SYSTEM_SELECTION), *INTEGRATION_PACKAGING, *INTEGRATION_AFTER):
        if (root / path).is_file():
            config.extra["storage_sidebar_labels"][path] = (short, title(root / path))
    if (root / INTEGRATION_HOME).is_file():
        config.extra["storage_sidebar_labels"][INTEGRATION_HOME] = (INTEGRATION_TOPIC, title(root / INTEGRATION_HOME))
    for name, _label in TOPICS:
        path = f"{name}/wiki/README.md"
        if owner(path)[0] == INTERCONNECT and (root / path).is_file():
            config.extra["storage_sidebar_labels"][path] = (owner(path)[1], title(root / path))
    for _label, pages in coherence_sections(root):
        for short, path in pages:
            config.extra["storage_sidebar_labels"][path] = (short, title(root / path))
    # Source-aligned topics use their reading lists for article short labels.
    for topic in ("PCIE", "SCALEUP", "NETWORK", "SERDES"):
        for chapter in sorted((root / topic / "wiki").glob("*/")):
            if topic == "SERDES":
                index = chapter / "README.md"
                if index.is_file():
                    metadata = re.search(r"^<!--\s*nav-title:\s*(.+?)\s*-->\s*$", index.read_text(encoding="utf-8"), re.MULTILINE)
                    if metadata:
                        config.extra["storage_sidebar_labels"][index.relative_to(root).as_posix()] = (metadata.group(1), title(index))
            for filename, short in reading_items(chapter):
                path = chapter / filename
                config.extra["storage_sidebar_labels"][path.relative_to(root).as_posix()] = (short, title(path))
    # CPO reading lists may also contain immediate child-section indexes.
    cpo_root = root / "CPO" / "wiki"
    for index in sorted(cpo_root.rglob("README.md")):
        if index.parent == cpo_root:
            continue
        metadata = re.search(r"^<!--\s*nav-title:\s*(.+?)\s*-->\s*$", index.read_text(encoding="utf-8"), re.MULTILINE)
        if metadata:
            config.extra["storage_sidebar_labels"][index.relative_to(root).as_posix()] = (metadata.group(1), title(index))
        for name, short in reading_items(index.parent, include_subdirs=True):
            path = index.parent / name
            if path.is_dir():
                path = path / "README.md"
            config.extra["storage_sidebar_labels"][path.relative_to(root).as_posix()] = (short, title(path))
    if (root / D2D_SUMMARY).is_file():
        for _name, _anchor, pages in read_d2d_sections(root):
            for short, path in pages:
                config.extra["storage_sidebar_labels"][path] = (short, title(root / path))
    if (root / NOC_SUMMARY).is_file():
        sections, legacy = read_noc_sections(root)
        config.extra["noc_legacy_pages"] = {path for _, path in legacy}
        for _name, _anchor, pages in sections:
            for short, path in pages:
                config.extra["storage_sidebar_labels"][path] = (short, title(root / path))
        for short, path in legacy:
            config.extra["storage_sidebar_labels"][path] = (short, title(root / path))
    micro_topics, micro_labels = micro_navigation(root)
    config.extra["storage_sidebar_labels"].update(micro_labels)
    home = "README.md"
    foundations = root / "foundations"
    if foundations.is_dir():
        home = [home, {COMMON_FOUNDATIONS: make_tree(foundations, root)}]
        for directory in sorted(foundations.glob("*/")):
            for name, short in reading_items(directory):
                path = directory / name
                config.extra["storage_sidebar_labels"][path.relative_to(root).as_posix()] = (short, title(path))
    storage_topics = grouped_original_topics(root, STORAGE)
    storage_resources = storage_resources_tree(root)
    validate_storage_navigation(root, [*storage_topics, *storage_resources])
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
        {"首页": home},
        {"微架构": [
            {"微架构首页": "microarchitecture.md"},
            {"精选文章": "articles.md"},
            {"互动图解": "visuals.md"},
            *micro_topics,
        ]},
        {STORAGE: [{"系列首页": "storage.md"}, *storage_topics, *storage_resources]},
        {INTERCONNECT: [{"系列首页": "interconnect.md"}, *grouped_original_topics(root, INTERCONNECT)]},
    ]
    for entry in series:
        if entry["source"]:
            directory = root / "external" / entry["source"]["slug"]
            config.nav.append({entry["title"]: make_tree(directory, root, ("README.md", "index.md"))})
        elif entry["local"]:
            directory = root / entry["local"]["publish"]
            if entry["local"]["publish"] == "external/workload-wiki":
                tree = workload_tree(root, directory, config.extra["storage_sidebar_labels"])
            elif entry["local"]["publish"] == "series/chip-development":
                tree = development_tree(root, directory, config.extra["storage_sidebar_labels"])
            elif entry["local"]["publish"] == "series/inference-runtime":
                tree = inference_tree(root, directory, config.extra["storage_sidebar_labels"])
            elif entry["local"]["publish"] == CHIP_ARCHITECTURES:
                tree = chip_architecture_tree(root, directory, config.extra["storage_sidebar_labels"])
            else:
                tree = make_tree(directory, root, ("README.md", "index.md"))
            config.nav.append({entry["title"]: tree})
    validate_unique_navigation(config.nav)
    return config


class CoherenceChapterPage(Page):
    """Use the preserved CXL article as a section index without changing its URL."""

    @property
    def is_index(self):
        return True


class ChipArchitectureArticle(Page):
    """Keep product README pages visible as articles within a reading group."""

    @property
    def is_index(self):
        return False


def on_files(files, config, **kwargs):
    # MkDocs navigation reuses pre-created Page instances. Keep the File's name,
    # destination and canonical URL unchanged; only its navigation role differs.
    file = files.get_file_from_path("COHERENCE/wiki/cxl-host-memory.md")
    if file is not None:
        CoherenceChapterPage(None, file, config)
    for file in files.documentation_pages():
        path = file.src_uri
        if (path.startswith(f"{CHIP_ARCHITECTURES}/") and path.endswith("/README.md")
                and path != CHIP_ARCHITECTURES_HOME):
            ChipArchitectureArticle(None, file, config)
    return files


def on_nav(nav, config, files, **kwargs):
    """Resolve source paths to generated URLs for sidebar labels."""
    labels = config.extra.get("storage_sidebar_labels", {})
    config.extra["storage_sidebar_urls"] = {
        unquote(file.url).lstrip("/"): labels[path]
        for path in labels
        if (file := files.get_file_from_path(path)) is not None
    }
    return nav


def on_page_markdown(markdown, page, **kwargs):
    """Add website interactions while keeping Markdown usable on GitHub."""
    if page.file.src_uri.startswith("FAB/wiki/"):
        markdown = re.sub(r"^```text[ \t]*$", "``` {.text .fab-text-diagram}", markdown, flags=re.MULTILINE)
    if page.file.src_uri.startswith("reviews/"):
        # Keep the archived page reachable by URL without indexing it for readers.
        search = page.meta.get("search")
        page.meta["search"] = {**(search if isinstance(search, dict) else {}), "exclude": True}
    if has_breadcrumbs(page):
        markdown = strip_duplicate_parent(markdown, page, Path(kwargs["config"].docs_dir))
        markdown = label_noc_original_parent(markdown, page, Path(kwargs["config"].docs_dir),
                                             kwargs["config"].extra.get("noc_legacy_pages", set()))
    if page.file.src_uri == "README.md":
        config = kwargs["config"]
        markdown = markdown.replace("__SITE_NAME__", escape(config.site_name))
        markdown = markdown.replace("<!-- site-series -->", render_series(read_series(Path(config.docs_dir))))

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
    html = render_series_cover(html, page, Path(kwargs["config"].docs_dir))
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
        "RAM/wiki/02-sram-foundations/README.md",
        "RAM/wiki/02-sram-foundations/6t-cell-bistable-storage.md",
        "RAM/wiki/02-sram-foundations/wordline-bitline-sense-amp.md",
        "RAM/wiki/02-sram-foundations/read-write-cycle-timing.md",
        "RAM/wiki/02-sram-foundations/sram-macro-interface-and-semantics.md",
        "RAM/wiki/02-sram-foundations/single-port-dual-port-multi-port.md",
        "RAM/wiki/02-sram-foundations/sram-array-organization.md",
        "RAM/wiki/02-sram-foundations/sram-bank-address-mapping-conflicts.md",
        "RAM/wiki/02-sram-foundations/sram-process-scaling-challenge.md",
        "RAM/wiki/02-sram-foundations/sram-power-leakage-retention.md",
        "RAM/wiki/02-sram-foundations/sram-reliability-ecc-mbist-repair.md",
    }:
        html = f'<div class="ram-problem-article">\n{html}\n</div>'
    elif page.file.src_uri.startswith("RAM/wiki/03-sram-applications/"):
        html = f'<div class="sram-application-article">\n{html}\n</div>'
    # CPO and Workload breadcrumbs are inserted after indexing so results start with
    # article content, rather than an ordered list of navigation ancestors.
    if has_breadcrumbs(page) and not page.file.src_uri.startswith(("CPO/wiki/", "external/workload-wiki/")):
        config = kwargs["config"]
        html = render_breadcrumbs(page, Path(config.docs_dir), config.extra.get("storage_sidebar_labels")) + "\n" + html
    return html


def render_fab_flowchart(match):
    # Use the intrinsic SVG dimensions so a wide graph stays legible inside the scroll region.
    settings = "---\nconfig:\n  flowchart:\n    useMaxWidth: false\n    nodeSpacing: 28\n---\n"
    top_down = ' data-top-down' if re.match(r"(?:flowchart|graph)[ \t]+(?:TB|TD)\b", match[2]) else ""
    return (
        f'<div class="fab-diagram-scroll"{top_down}><div class="fab-diagram-inner">'
        f'{match[1]}{settings}{match[2]}{match[3]}</div></div>'
    )


def on_post_page(output, page, **kwargs):
    """Shorten configured sidebar labels and expose the current page accessibly."""
    if page.file.src_uri.startswith("FAB/wiki/"):
        # Apply display settings after searching has indexed the original content.
        output = re.sub(r'(<pre class="mermaid"><code>)((?:flowchart|graph)[ \t].*?)(</code></pre>)',
                        render_fab_flowchart, output, flags=re.DOTALL)
    if page.file.src_uri.startswith(("CPO/wiki/", "external/workload-wiki/")) and has_breadcrumbs(page):
        config = kwargs["config"]
        crumb = render_breadcrumbs(page, Path(config.docs_dir), config.extra.get("storage_sidebar_labels"))
        output, count = re.subn(r'(<article class="md-content__inner md-typeset">)',
                                lambda match: match.group(1) + "\n" + crumb, output, count=1)
        if count != 1:
            raise ValueError(f"Article container not found: {page.file.src_uri}")
    labels = kwargs["config"].extra.get("storage_sidebar_urls", {})
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

        primary = link.sub(shorten, output[start:end])
        # Material renders the active page twice: an anchor for wide screens
        # and a TOC label for the mobile drawer. Give both the same short name.
        current = labels.get(unquote(page.url).lstrip("/"))
        if current and current[0] != current[1]:
            short, full = current
            toc_label = re.compile(
                r'(<label\b(?=[^>]*\bclass="[^"]*\bmd-nav__link--active\b[^"]*")'
                r'(?=[^>]*\bfor="__toc")[^>]*)(>\s*<span class="md-ellipsis">)'
                r'(.*?)(</span>)', re.DOTALL,
            )

            def shorten_active_label(match):
                attrs = match.group(1)
                if not re.search(r'\btitle\s*=', attrs):
                    attrs += ' title="{}"'.format(escape(full, quote=True))
                if not re.search(r'\baria-label\s*=', attrs):
                    attrs += ' aria-label="{}"'.format(escape(full, quote=True))
                return attrs + match.group(2) + escape(short) + match.group(4)

            primary = toc_label.sub(shorten_active_label, primary)
        output = output[:start] + primary + output[end:]
    active_link = r'(<a\b[^>]*\bclass="[^"]*\bmd-nav__link--active\b[^"]*"[^>]*)(>)'
    return re.sub(active_link, lambda match: match.group(0) if "aria-current=" in match.group(1) else match.group(1) + ' aria-current="page"' + match.group(2), output)
