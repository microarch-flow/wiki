"""Build D2D reading groups without changing existing public paths."""

from pathlib import Path, PurePosixPath
import posixpath
import re
from urllib.parse import unquote, urlsplit


D2D_HOME = "D2D/wiki/README.md"
D2D_SUMMARY = "D2D/wiki/SUMMARY.md"


def read_d2d_sections(root):
    """Read groups from the knowledge map and require every article exactly once."""
    root = Path(root)
    sections = []
    seen_pages = set()
    seen_names = set()
    seen_anchors = set()
    current = None
    for line in (root / D2D_SUMMARY).read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            heading = re.fullmatch(r"##\s+(.+?)\s+\{#([a-z0-9-]+)\}\s*", line)
            if not heading:
                raise ValueError(f"Invalid D2D knowledge map heading: {line}")
            name, anchor = heading.groups()
            if name in seen_names or anchor in seen_anchors:
                raise ValueError(f"Duplicate D2D navigation section: {name}")
            seen_names.add(name)
            seen_anchors.add(anchor)
            current = (name, anchor, [])
            sections.append(current)
            continue
        item = re.fullmatch(r"-\s+\[([^\]]+)\]\(([^)]+)\)\s*", line)
        if not item:
            continue
        if current is None:
            raise ValueError("D2D navigation entry appears before its section")
        label, raw_target = item.groups()
        target = urlsplit(raw_target)
        if target.scheme or target.netloc or target.query or target.fragment or not target.path:
            raise ValueError(f"Invalid D2D navigation target: {raw_target}")
        path = posixpath.normpath(posixpath.join("D2D/wiki", unquote(target.path)))
        if not path.startswith("D2D/wiki/") or PurePosixPath(path).suffix != ".md" or not (root / path).is_file():
            raise ValueError(f"D2D navigation target is missing or outside the wiki: {raw_target}")
        if path in seen_pages or path in {D2D_HOME, D2D_SUMMARY}:
            raise ValueError(f"Duplicate D2D navigation target: {path}")
        seen_pages.add(path)
        current[2].append((label.strip(), path))

    if not sections or any(not pages for _, _, pages in sections):
        raise ValueError("D2D navigation sections must not be empty")
    expected = {path.relative_to(root).as_posix() for path in (root / "D2D/wiki").rglob("*.md")}
    expected -= {D2D_HOME, D2D_SUMMARY}
    if seen_pages != expected:
        raise ValueError(f"D2D navigation does not cover pages: missing={sorted(expected - seen_pages)}, extra={sorted(seen_pages - expected)}")
    return sections


def d2d_topic_tree(root):
    root = Path(root)
    if not (root / D2D_HOME).is_file():
        return []
    if not (root / D2D_SUMMARY).is_file():
        pages = {path.relative_to(root).as_posix() for path in (root / "D2D/wiki").rglob("*.md")}
        if pages == {D2D_HOME}:
            return [D2D_HOME]
        raise ValueError("D2D with multiple pages requires its knowledge map")
    sections = read_d2d_sections(root)
    return [D2D_HOME, {"知识地图": D2D_SUMMARY}] + [
        {name: [path for _label, path in pages]}
        for name, _anchor, pages in sections
    ]
