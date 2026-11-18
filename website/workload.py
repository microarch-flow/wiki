"""Workload source moves and navigation; public article paths remain stable."""

from pathlib import Path, PurePosixPath
import posixpath
import re
from urllib.parse import unquote, urlsplit

from sources import copy_source

PREFIX = "external/workload-wiki"
MOVES = {
    "learning-objectives/contrastive-learning.md": "01-foundation-model-components/contrastive-learning.md",
    "learning-objectives/jepa-and-self-supervised.md": "01-foundation-model-components/jepa-and-self-supervised.md",
    "generative-models/diffusion-models.md": "01-foundation-model-components/diffusion-models.md",
    "decision-and-policy/robotics-vs-autonomous-driving.md": "04-robotics-and-vla/robotics-vs-autonomous-driving.md",
    "06-chip-workload-analysis/edge-cloud-collaborative-world-model.md": "05-world-model-and-generative/edge-cloud-collaborative-world-model.md",
    "06-chip-workload-analysis/workload-lens.md": "00-overview/workload-lens.md",
    "06-chip-workload-analysis/workload-comparison-table.md": "07-reference/workload-comparison-table.md",
}
CHAPTERS = (
    ("导读与共同基础", "00-overview"),
    ("网络组件与序列建模", "01-foundation-model-components"),
    ("表示学习与训练目标", "learning-objectives"),
    ("生成机制", "generative-models"),
    ("语言与多模态模型", "language-and-multimodal"),
    ("视觉感知与三维场景表示", "02-vision-and-3d-perception"),
    ("决策与策略学习", "decision-and-policy"),
    ("自动驾驶感知、预测与规划", "03-autonomous-driving-algorithms"),
    ("机器人策略与视觉语言动作模型", "04-robotics-and-vla"),
    ("世界模型与环境预测", "05-world-model-and-generative"),
    ("算法工作负载分析", "06-chip-workload-analysis"),
    ("查阅资料", "07-reference"),
)


def public_path(source):
    return f"{PREFIX}/{MOVES.get(str(source), str(source))}"


def stage_workload(source, destination, published):
    """Reuse the public-source boundary checks, then register moved files."""
    source, destination = Path(source), Path(destination)
    copy_source(source, destination, public_only=True)
    originals = [p.relative_to(destination) for p in destination.rglob("*") if p.is_file()]
    for relative in originals:
        mapped = MOVES.get(relative.as_posix(), relative.as_posix())
        staged = destination / mapped
        if mapped != relative.as_posix():
            if staged.exists():
                raise ValueError(f"Workload publication collision: {mapped}")
            staged.parent.mkdir(parents=True, exist_ok=True)
            (destination / relative).rename(staged)
        published.add(source / relative, staged)
    published.add(source, destination)
    for current, old in MOVES.items():
        if (source / current).exists():
            published.add(source / old, destination / old, rewrite_page=False)


def navigation(root):
    """Chapter reading lists own both order and short labels, including moves."""
    root = Path(root)
    home = f"{PREFIX}/README.md"
    seen = {home}
    tree = [home]
    for label, directory in CHAPTERS:
        index = f"{PREFIX}/{directory}/README.md"
        if not (root / index).is_file():
            raise ValueError(f"Workload chapter index missing: {index}")
        seen.add(index)
        entries = [index]
        active = False
        for line in (root / index).read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                active = line[3:].strip() in {"阅读顺序", "原入口"}
                continue
            match = re.match(r"^\d+\. \[([^\]]+)\]\(([^)]+)\)", line) if active else None
            if not match:
                continue
            short, raw = match.groups()
            target = urlsplit(raw)
            path = posixpath.normpath(posixpath.join(posixpath.dirname(index), unquote(target.path)))
            if target.scheme or target.netloc or target.query or target.fragment or not path.startswith(PREFIX + "/") or PurePosixPath(path).suffix != ".md" or not (root / path).is_file():
                raise ValueError(f"Invalid Workload reading target: {raw}")
            if path in seen:
                raise ValueError(f"Duplicate Workload navigation page: {path}")
            seen.add(path)
            entries.append({short: path})
        if len(entries) == 1:
            raise ValueError(f"Empty Workload chapter: {label}")
        tree.append({label: entries})
    expected = {p.relative_to(root).as_posix() for p in (root / PREFIX).rglob("*.md")}
    if seen != expected:
        raise ValueError(f"Workload navigation coverage: missing={sorted(expected-seen)}, extra={sorted(seen-expected)}")
    return tree
