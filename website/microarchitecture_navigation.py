"""Source-aligned microarchitecture navigation over preserved publication URLs."""

from html import unescape
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
from urllib.parse import unquote, urlsplit


MICRO_TOPICS = {
    "00-overview": "系列导读",
    "01-datapath": "数值格式与运算数据通路",
    "02-pipeline": "流水线、时序与时钟域",
    "03-instruction-execution": "指令执行与处理器控制",
    "04-parallel-execution": "并行执行与计算阵列",
    "05-dma": "DMA 与异步数据搬运",
    "06-task-control": "任务控制、同步与资源管理",
    "07-chip-organization": "处理单元与片上组织",
    "08-in-memory-computing": "存内与近存计算",
    "09-power-implementation": "功耗管理与实现权衡",
    "reading-and-reference": "分析方法与查阅练习",
}


def micro_navigation(root):
    """Read staged source metadata; chapter reading lists own order and labels.

    Resolve reading targets against staged paths, then group by source paths.
    This avoids inferring the new source hierarchy from legacy URLs.
    """
    root = Path(root)
    mapping = json.loads((root.parent / "microarchitecture-navigation.json").read_text())
    if len(set(mapping.values())) != len(mapping):
        raise ValueError("Duplicate microarchitecture publication target")
    reverse = {target: source for source, target in mapping.items()}
    labels = {}
    assigned = set()

    def page_title(path):
        text = (root / path).read_text(encoding="utf-8")
        heading = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        metadata = re.search(r"^<!--\s*nav-title:\s*(.+?)\s*-->\s*$", text, re.MULTILINE)
        full = heading.group(1) if heading else Path(path).stem
        return (metadata.group(1) if metadata else full), full

    def tree(directory, group_label=None):
        direct = {PurePosixPath(source).name: source for source in mapping
                  if str(PurePosixPath(source).parent) == directory}
        subdirs = {source[len(directory) + 1:].split("/")[0] for source in mapping
                   if source.startswith(directory + "/") and "/" in source[len(directory) + 1:]}
        index = direct.pop("README.md", None)
        priorities = {}
        short_names = {}
        if index:
            staged = mapping[index]
            in_order = False
            for line in (root / staged).read_text(encoding="utf-8").splitlines():
                if line.startswith("## "):
                    in_order = bool(re.match(r"## (?:推荐)?阅读顺序|## 接下来怎么读", line))
                item = re.match(r"\s*\d+\.\s+\[([^\]]+)\]\(([^)]+)\)", line) if in_order else None
                if not item:
                    continue
                target = urlsplit(item.group(2))
                if target.scheme or target.netloc or target.fragment or target.query:
                    raise ValueError(f"Invalid microarchitecture reading target in {staged}: {item.group(2)}")
                resolved = posixpath.normpath(posixpath.join(posixpath.dirname(staged), unquote(target.path)))
                source = reverse.get(resolved)
                if source is None:
                    raise ValueError(f"Unpublished microarchitecture reading target: {staged} -> {resolved}")
                if PurePosixPath(source).parent.as_posix() == directory:
                    name = PurePosixPath(source).name
                elif source.endswith("/README.md") and PurePosixPath(source).parent.parent.as_posix() == directory:
                    name = PurePosixPath(source).parent.name
                else:
                    raise ValueError(f"Reading target does not belong to source section {directory}: {source}")
                if name in priorities:
                    raise ValueError(f"Duplicate microarchitecture reading target: {source}")
                priorities[name] = len(priorities)
                short_names[source] = unescape(item.group(1)).strip()
            required = set(direct) - {"SUMMARY.md"} | subdirs
            if set(priorities) != required:
                raise ValueError(f"Microarchitecture reading coverage in {directory}: missing={sorted(required - set(priorities))}, extra={sorted(set(priorities) - required)}")
        elif direct or subdirs:
            raise ValueError(f"Microarchitecture section has no guide: {directory}")

        def entry(source, short=None):
            path = mapping[source]
            label, full = page_title(path)
            label = short or short_names.get(source, label)
            labels[path] = (label, full)
            assigned.add(path)
            return path

        result = [entry(index, group_label)] if index else []
        if "SUMMARY.md" in direct:
            result.append(entry(direct.pop("SUMMARY.md"), "知识地图"))
        for name in sorted(set(direct) | subdirs, key=lambda name: (priorities.get(name, len(priorities)), name)):
            if name in subdirs:
                child = directory + "/" + name
                child_index = child + "/README.md"
                label = short_names.get(child_index) or page_title(mapping[child_index])[0]
                result.append({label: tree(child, label)})
            else:
                result.append(entry(direct[name]))
        return result

    result = []
    for directory, label in MICRO_TOPICS.items():
        if any(source.startswith(directory + "/") for source in mapping):
            result.append({label: tree(directory, label)})
    if assigned != set(mapping.values()):
        raise ValueError(f"Microarchitecture navigation coverage: missing={sorted(set(mapping.values()) - assigned)}")
    return result, labels
