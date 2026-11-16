"""Build NoC navigation from its maintained, URL-preserving knowledge map."""

from pathlib import Path, PurePosixPath
import posixpath
import re
from urllib.parse import unquote, urlsplit


NOC_HOME = "NOC/wiki/README.md"
NOC_SUMMARY = "NOC/wiki/SUMMARY.md"
NOC_SECTIONS = (
    ("01 认识 NoC", "01-overview"),
    ("02 路由器与逐跳流控", "02-router-microarchitecture"),
    ("03 拓扑与物理组织", "03-topology"),
    ("04 路由、仲裁与服务保证", "04-routing-and-flow-control"),
    ("05 端点与系统集成", "05-system-integration"),
    ("06 多端通信与调度", "06-ai-noc-specifics"),
    ("07 工作负载与系统案例", "workload-cases"),
    ("08 性能评估与架构探索", "07-evaluation-methodology"),
    ("09 模拟器构建与验证", "08-simulator-construction"),
    ("10 查阅与练习", "09-reference"),
)


def read_noc_sections(root):
    """Return section entries and retained chapter indexes from SUMMARY.md.

    The staged Markdown remains the single source for the visible labels and
    order. Require every NoC page exactly once so new content cannot disappear
    from navigation when its original source directory differs from its group.
    """
    root = Path(root)
    summary = root / NOC_SUMMARY
    sections = []
    seen = set()
    legacy = []
    current = None
    in_legacy = False
    for line in summary.read_text(encoding="utf-8").splitlines():
        heading = re.fullmatch(r"##\s+(.+?)\s+\{#([a-z0-9-]+)\}\s*", line)
        if heading:
            current = (heading.group(1), heading.group(2), [])
            sections.append(current)
            in_legacy = False
            continue
        if line.startswith("### "):
            if line.strip() != "### 原章节入口" or not current or current[0] != NOC_SECTIONS[-1][0] or in_legacy:
                raise ValueError(f"Unexpected NoC knowledge map subsection: {line}")
            in_legacy = True
            continue
        item = re.fullmatch(r"-\s+\[([^\]]+)\]\(([^)]+)\)\s*", line)
        if not item:
            continue
        if current is None:
            raise ValueError("NoC navigation entry appears before its section")
        label, raw_target = item.groups()
        target = urlsplit(raw_target)
        if target.scheme or target.netloc or target.query or target.fragment or not target.path:
            raise ValueError(f"Invalid NoC navigation target: {raw_target}")
        path = posixpath.normpath(posixpath.join("NOC/wiki", unquote(target.path)))
        if not path.startswith("NOC/wiki/") or PurePosixPath(path).suffix != ".md" or not (root / path).is_file():
            raise ValueError(f"NoC navigation target is missing or outside the wiki: {raw_target}")
        if path in seen or path in {NOC_HOME, NOC_SUMMARY}:
            raise ValueError(f"Duplicate NoC navigation target: {path}")
        if (PurePosixPath(path).name == "README.md") != in_legacy:
            raise ValueError(f"NoC chapter indexes belong under 原章节入口: {path}")
        seen.add(path)
        (legacy if in_legacy else current[2]).append((label.strip(), path))

    if tuple((name, anchor) for name, anchor, _ in sections) != NOC_SECTIONS:
        raise ValueError("NoC knowledge map must contain the ten declared sections in order")
    if not legacy or any(not pages for _, _, pages in sections):
        raise ValueError("NoC navigation sections and original chapter entries must not be empty")
    expected = {path.relative_to(root).as_posix() for path in (root / "NOC/wiki").rglob("*.md")}
    expected -= {NOC_HOME, NOC_SUMMARY}
    if seen != expected:
        raise ValueError(f"NoC navigation does not cover pages: missing={sorted(expected - seen)}, extra={sorted(seen - expected)}")
    return sections, legacy


def noc_topic_tree(root):
    root = Path(root)
    if not (root / NOC_SUMMARY).is_file():
        wiki = root / "NOC/wiki"
        pages = {path.relative_to(root).as_posix() for path in wiki.rglob("*.md")}
        if pages == {NOC_HOME}:
            return [NOC_HOME]
        raise ValueError("NoC with multiple pages requires its knowledge map")
    sections, legacy = read_noc_sections(root)
    result = [NOC_HOME, {"知识地图": NOC_SUMMARY}]
    for name, _anchor, pages in sections:
        entries = [{label: path} for label, path in pages]
        if name == NOC_SECTIONS[-1][0]:
            # Wrap each original index separately. Material otherwise treats
            # the first README as the index page for the entire group.
            entries.append({"原章节入口": [{label: [path]} for label, path in legacy]})
        result.append({name: entries})
    return result
