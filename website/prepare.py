#!/usr/bin/env python3
"""Stage the published sources without changing the existing wiki files."""

import argparse
import json
import os
from pathlib import Path
from pathlib import PurePosixPath
import shutil
import tempfile

from sources import copy_source, fetch_checkout, load_series, source_directory, validate_output_paths
from stage_links import PublishedPaths


ROOT = Path(__file__).resolve().parent.parent
TOPICS = ("RAM", "COMPUTE", "BUS", "NOC", "DMA", "PCIE", "CIM", "CPO", "FAB", "SERDES", "HBF")


def _path_inside(root, value, is_directory):
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"Invalid source layout path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in {".", "..", ".git"} for part in path.parts):
        raise ValueError(f"Source layout path must stay inside the checkout: {value!r}")
    current = Path(root)
    for part in path.parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f"Source layout path contains a symlink: {current}")
    if not (current.is_dir() if is_directory else current.is_file()):
        raise ValueError(f"Source layout path does not exist: {current}")
    return current


def load_layout(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"topics", "foundations"}:
        raise ValueError("Source layout needs topics and foundations")
    if not isinstance(data["topics"], dict) or set(data["topics"]) != set(TOPICS):
        raise ValueError("Source layout must map each existing topic exactly once")
    if not isinstance(data["foundations"], dict) or set(data["foundations"]) != {"article", "images"}:
        raise ValueError("Source layout needs a foundations article and images directory")
    return data


def _assert_no_symlinks(source):
    for parent, directories, files in os.walk(source, followlinks=False):
        for name in directories + files:
            path = Path(parent) / name
            if path.is_symlink():
                raise ValueError(f"Source contains a symlink: {path}")


def _ignore_topic_maintenance(_directory, names):
    excluded_dirs = {".git", "wiki.old", "raw", "seed", "__pycache__"}
    excluded_files = {"agents.md", "skill.md", "task.md", "wiki-plan.md"}
    return {name for name in names if name in excluded_dirs or name.lower() in excluded_files}


def stage_site(root=ROOT, build_root=None, registry=None, source_root=None, layout=None):
    """Build a complete staging tree before replacing the previous one.

    With source_root, each external series uses the checkout named by its slug.
    Otherwise configured GitHub repositories are fetched at their selected refs.
    """
    root = Path(root)
    build_root = Path(build_root) if build_root is not None else root / ".site-build"
    registry = Path(registry) if registry is not None else root / "website" / "series.json"
    layout = Path(layout) if layout is not None else root / "website" / "source-layout.json"
    source_root = Path(source_root) if source_root is not None else None
    entries = load_series(registry)
    layout_data = load_layout(layout)
    topics = {name: _path_inside(root, layout_data["topics"][name], True) for name in TOPICS}
    article = _path_inside(root, layout_data["foundations"]["article"], False)
    images = _path_inside(root, layout_data["foundations"]["images"], True)
    local_sources = [source_directory(root, item["local"]["directory"]) for item in entries if "local" in item]
    # An explicitly staged topic must never also be included recursively in a
    # local series: this could duplicate published pages or expose wiki.old.
    for topic, source in topics.items():
        for local in local_sources:
            if source == local or source in local.parents or local in source.parents:
                raise ValueError(f"Topic {topic} overlaps a local series source: {source} and {local}")
    build_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=".stage-", dir=build_root) as temporary:
        staging = Path(temporary)
        docs = staging / "docs"
        docs.mkdir()
        published = PublishedPaths(root, docs)

        for name in TOPICS:
            source = topics[name]
            target = docs / name
            _assert_no_symlinks(source / "wiki")
            shutil.copytree(source / "wiki", target / "wiki", ignore=_ignore_topic_maintenance)
            published.add(source, target)
            published.add_tree(source / "wiki", target / "wiki")
            for filename in ("README.md", "self-test-questions.md"):
                if (source / filename).is_file():
                    if (source / filename).is_symlink():
                        raise ValueError(f"Source contains a symlink: {source / filename}")
                    shutil.copy2(source / filename, target / filename)
                    published.add(source / filename, target / filename)

        shutil.copytree(root / "reviews", docs / "reviews")
        published.add_tree(root / "reviews", docs / "reviews")
        _assert_no_symlinks(images)
        shutil.copytree(images, docs / "img")
        published.add_tree(images, docs / "img")
        shutil.copy2(article, docs / "electrical-timing-foundations.md")
        published.add(article, docs / "electrical-timing-foundations.md")
        shutil.copy2(root / "website" / "home.md", docs / "README.md")
        shutil.copy2(root / "website" / "series.md", docs / "series.md")
        shutil.copy2(root / "website" / "microarchitecture.md", docs / "microarchitecture.md")
        shutil.copy2(root / "website" / "storage.md", docs / "storage.md")
        shutil.copy2(root / "website" / "interconnect.md", docs / "interconnect.md")
        shutil.copy2(root / "website" / "articles.md", docs / "articles.md")
        shutil.copy2(root / "website" / "visuals.md", docs / "visuals.md")
        shutil.copytree(root / "website" / "assets", docs / "assets")

        checkouts = {}
        for item in entries:
            if "local" in item:
                local = item["local"]
                selected = source_directory(root, local["directory"])
                copy_source(selected, docs / local["publish"], public_only=True)
                published.add_tree(selected, docs / local["publish"])
                print(f"Staged series {item['title']} from local {local['directory']}")
                continue
            if "source" not in item:
                continue
            source = item["source"]
            slug = source["slug"]
            if source_root is not None:
                checkout = source_root / slug
                if not checkout.is_dir():
                    raise ValueError(f"Missing local checkout for {slug}: {checkout}")
            else:
                key = (source["repository"], source["ref"])
                if key not in checkouts:
                    checkout = staging / "checkouts" / str(len(checkouts))
                    fetch_checkout(source, checkout)
                    checkouts[key] = checkout
                checkout = checkouts[key]
            selected = source_directory(checkout, source["directory"])
            copy_source(selected, docs / "external" / slug)
            print(f"Staged series {item['title']} from {source['repository']}:{source['directory']}")

        published.rewrite()
        validate_output_paths(docs)

        # Keep the registry outside docs: it is build metadata, not a site asset.
        (staging / "series.json").write_text(
            json.dumps({"series": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
        )
        destination = build_root / "docs"
        if destination.exists():
            shutil.rmtree(destination)
        docs.rename(destination)
        (staging / "series.json").replace(build_root / "series.json")
    print(f"Staged source documents in {destination}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root", type=Path,
        help="Use local checkouts in SOURCE_ROOT/<series-slug> instead of fetching GitHub",
    )
    args = parser.parse_args()
    stage_site(source_root=args.source_root)


if __name__ == "__main__":
    main()
