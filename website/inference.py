"""Inference source chapters, stable publication paths, and guide-owned order."""

from pathlib import Path, PurePosixPath
import posixpath
import re
from urllib.parse import unquote, urlsplit

from sources import copy_source

PREFIX = "series/inference-runtime"
CHAPTERS = (
    ("请求路径与服务指标", "01-request-and-metrics"),
    ("模型加载与执行计划", "02-model-execution"),
    ("算子内核与低精度执行", "03-kernels-and-precision"),
    ("运行时状态与 KV 管理", "04-state-and-memory"),
    ("批处理与请求调度", "05-batching-and-scheduling"),
    ("采样与解码控制", "06-sampling-and-decoding"),
    ("分布式执行与阶段分离", "07-distributed-execution"),
    ("服务生命周期与副本管理", "08-serving-lifecycle"),
    ("测量、建模与框架案例", "09-measurement-and-cases"),
)
MOVES = {
    "01-request-and-metrics/01-prefill-decode.md": "topics/01-prefill-decode.md",
    "01-request-and-metrics/02-metrics-slo.md": "topics/02-metrics-slo.md",
    "01-request-and-metrics/03-naive-bottlenecks.md": "topics/03-naive-bottlenecks.md",
    "05-batching-and-scheduling/04-dynamic-shape-batching.md": "topics/04-dynamic-shape-batching.md",
    "03-kernels-and-precision/05-attention-kernels.md": "topics/05-attention-kernels.md",
    "04-state-and-memory/06-paged-kv-cache.md": "topics/06-paged-kv-cache.md",
    "04-state-and-memory/07-radix-prefix-reuse.md": "topics/07-radix-prefix-reuse.md",
    "05-batching-and-scheduling/08-scheduling.md": "topics/08-scheduling.md",
    "06-sampling-and-decoding/09-speculative-decoding.md": "topics/09-speculative-decoding.md",
    "03-kernels-and-precision/10-quantization.md": "topics/10-quantization.md",
    "07-distributed-execution/11-cluster-parallelism.md": "topics/11-cluster-parallelism.md",
    "07-distributed-execution/12-pd-disaggregation.md": "topics/12-pd-disaggregation.md",
    "06-sampling-and-decoding/13-constrained-decoding.md": "topics/13-constrained-decoding.md",
    "09-measurement-and-cases/14-framework-comparison.md": "topics/14-framework-comparison.md",
    "09-measurement-and-cases/15-quantitative-estimation.md": "topics/15-quantitative-estimation.md",
}


def public_path(source):
    return f"{PREFIX}/{MOVES.get(str(source), str(source))}"


def stage_inference(source, destination, published):
    """Register each real source and an alias for every preserved source path."""
    source, destination = Path(source), Path(destination)
    copy_source(source, destination, public_only=True)
    originals = [p.relative_to(destination) for p in destination.rglob("*") if p.is_file()]
    for relative in originals:
        mapped = MOVES.get(relative.as_posix(), relative.as_posix())
        staged = destination / mapped
        if mapped != relative.as_posix():
            if staged.exists():
                raise ValueError(f"Inference publication collision: {mapped}")
            staged.parent.mkdir(parents=True, exist_ok=True)
            (destination / relative).rename(staged)
        published.add(source / relative, staged)
    published.add(source, destination)
    for current, old in MOVES.items():
        if not (source / current).is_file():
            raise ValueError(f"Inference moved source missing: {current}")
        published.add(source / old, destination / old, rewrite_page=False)


def navigation(root):
    """Use each chapter guide's ordered list, after source links are staged."""
    root = Path(root)
    home = f"{PREFIX}/README.md"
    seen = {home}
    tree = [home]
    for label, directory in CHAPTERS:
        index = f"{PREFIX}/{directory}/README.md"
        if not (root / index).is_file():
            raise ValueError(f"Inference chapter index missing: {index}")
        seen.add(index)
        entries = [index]
        active = False
        for line in (root / index).read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                active = line[3:].strip() == "阅读顺序"
                continue
            match = re.match(r"^\d+\. \[([^\]]+)\]\(([^)]+)\)", line) if active else None
            if not match:
                continue
            short, raw = match.groups()
            target = urlsplit(raw)
            path = posixpath.normpath(posixpath.join(posixpath.dirname(index), unquote(target.path)))
            if (target.scheme or target.netloc or target.query or target.fragment
                    or not path.startswith(PREFIX + "/")
                    or PurePosixPath(path).suffix != ".md" or not (root / path).is_file()):
                raise ValueError(f"Invalid inference reading target: {raw}")
            relative = path.removeprefix(PREFIX + "/")
            source = next((current for current, old in MOVES.items() if old == relative), relative)
            if PurePosixPath(source).parent.as_posix() != directory:
                raise ValueError(f"Inference reading target outside chapter: {raw}")
            if path in seen:
                raise ValueError(f"Duplicate inference navigation page: {path}")
            seen.add(path)
            entries.append({short: path})
        if len(entries) == 1:
            raise ValueError(f"Empty inference chapter: {label}")
        tree.append({label: entries})
    references = [f"{PREFIX}/glossary.md", f"{PREFIX}/_conventions.md"]
    tree.append({"术语与约定": references})
    seen.update(references)
    expected = {p.relative_to(root).as_posix() for p in (root / PREFIX).rglob("*.md")}
    if seen != expected:
        raise ValueError(f"Inference navigation coverage: missing={sorted(expected-seen)}, extra={sorted(seen-expected)}")
    return tree
