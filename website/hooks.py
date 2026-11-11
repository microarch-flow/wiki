"""Build a compact navigation from the wiki's real chapter directories."""

from pathlib import Path
import re


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


def title(path):
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^#\s+(.+?)\s*$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else path.stem.replace("-", " ")


def make_tree(directory, root):
    items = []
    index = directory / "README.md"
    if index.is_file():
        items.append(index.relative_to(root).as_posix())
    summary = directory / "SUMMARY.md"
    if summary.is_file():
        items.append({"知识地图": summary.relative_to(root).as_posix()})
    for path in sorted(directory.iterdir(), key=lambda p: p.name.lower()):
        if path.is_dir():
            if not any(path.rglob("*.md")):
                continue
            section_index = path / "README.md"
            label = title(section_index) if section_index.exists() else path.name
            items.append({label: make_tree(path, root)})
    return items


def on_config(config, **kwargs):
    root = Path(config.docs_dir)
    config.nav = [
        {"首页": "README.md"},
        {"精选文章": "articles.md"},
        {"互动图解": "visuals.md"},
        {"基础": "electrical-timing-foundations.md"},
        {"专题": [{label: make_tree(root / name / "wiki", root)} for name, label in TOPICS]},
        {"评审记录": [
            {"九专题基线问题": "reviews/2026-11-09-topic-review.md"},
            {"第二轮逐篇评审": "reviews/round-2/README.md"},
            {"第三轮有限资源盲测": "reviews/round-3/README.md"},
        ]},
    ]
    return config


def on_page_markdown(markdown, page, **kwargs):
    """Add website interactions while keeping Markdown usable on GitHub."""
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
