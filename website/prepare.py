#!/usr/bin/env python3
"""Stage the published sources without changing the existing wiki files."""

import argparse
import json
import os
from pathlib import Path
from pathlib import PurePosixPath
import shutil
import tempfile

from ownership import GROUPS, MICRO, STORAGE, owner
from microarchitecture_navigation import MICRO_TOPICS
from sources import copy_source, fetch_checkout, load_series, source_directory, validate_output_paths
from stage_links import PublishedPaths
from workload import stage_workload
from inference import stage_inference
from storage_navigation import INTEGRATION_PAGE_SECTION, MEMORY_HOME, MEMORY_PAGE_SECTION, RESOURCE_HOME, RESOURCE_PAGE_SECTION, STORAGE_RESOURCES


ROOT = Path(__file__).resolve().parent.parent
TOPICS = ("RAM", "COMPUTE", "BUS", "NOC", "D2D", "DMA", "PCIE", "COHERENCE",
          "SCALEUP", "NETWORK", "CIM", "CPO", "FAB", "SERDES", "HBF")
SOURCE_TOPICS = tuple(name for name in TOPICS if name not in {"RAM", "HBF", "COMPUTE", "DMA", "CIM"})
INTERCONNECT_TOPICS = frozenset({"BUS", "NOC", "D2D", "PCIE", "COHERENCE",
                                "SCALEUP", "NETWORK", "SERDES", "CPO"})
BUS_LEGACY_INDEX = "docs/archive/interconnect/BUS/README.md"
STORAGE_TOPICS = dict(zip((
    "01-memory-hierarchy", "02-sram", "03-dram", "04-dram-controller", "05-hbf", "06-system-integration",
), GROUPS[STORAGE]))
STORAGE_TOPICS["reading-and-reference"] = STORAGE_RESOURCES


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
    if not isinstance(data, dict) or set(data) != {"topics", "foundations", "storage", "microarchitecture"}:
        raise ValueError("Source layout needs topics, foundations, storage and microarchitecture")
    if not isinstance(data["topics"], dict) or set(data["topics"]) != set(SOURCE_TOPICS):
        raise ValueError("Source layout must map each non-storage topic exactly once")
    if not isinstance(data["foundations"], dict) or set(data["foundations"]) != {"article", "images"}:
        raise ValueError("Source layout needs a foundations article and images directory")
    storage = data["storage"]
    if not isinstance(storage, dict) or set(storage) != {"homepage", "roots", "mappings", "aliases"}:
        raise ValueError("Storage layout needs homepage, roots, mappings and aliases")
    if not isinstance(storage["roots"], list) or not storage["roots"]:
        raise ValueError("Storage layout needs source roots")
    if not isinstance(storage["mappings"], list) or not storage["mappings"]:
        raise ValueError("Storage layout needs source mappings")
    if not isinstance(storage["aliases"], list):
        raise ValueError("Storage aliases must be a list")
    for item in storage["mappings"]:
        if not isinstance(item, dict) or set(item) != {"kind", "source", "target"} or item["kind"] not in {"file", "directory"}:
            raise ValueError("Each storage mapping needs kind, source and target")
    for item in storage["aliases"]:
        if not isinstance(item, dict) or set(item) != {"source", "target"}:
            raise ValueError("Each storage alias needs source and target")
    micro = data["microarchitecture"]
    if not isinstance(micro, dict) or set(micro) != {"homepage", "mappings", "aliases"}:
        raise ValueError("Microarchitecture layout needs homepage, mappings and aliases")
    for key in ("mappings", "aliases"):
        if not isinstance(micro[key], list):
            raise ValueError(f"Microarchitecture {key} must be a list")
        for item in micro[key]:
            if not isinstance(item, dict) or set(item) != {"source", "target"}:
                raise ValueError("Microarchitecture entries need source and target")
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


def _storage_source(root, value, is_directory):
    path = _path_inside(root, value, is_directory)
    storage = Path(root) / "series" / "storage"
    if path == storage or storage not in path.parents:
        raise ValueError(f"Storage source must be inside series/storage: {value!r}")
    return path


def _storage_target(docs, value):
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"Invalid storage target: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in {".", "..", ".git"} for part in path.parts):
        raise ValueError(f"Storage target must stay inside the staged docs: {value!r}")
    allowed = (PurePosixPath("RAM/wiki"), PurePosixPath("HBF/wiki"),
               PurePosixPath("COMPUTE/wiki/06-memory-discipline"))
    if path != PurePosixPath("RAM/self-test-questions.md") and not any(path == prefix or prefix in path.parents for prefix in allowed):
        raise ValueError(f"Storage target is outside the preserved publication paths: {value!r}")
    return Path(docs).joinpath(*path.parts)


def _storage_files(source):
    """List publishable files without exposing source maintenance material."""
    _assert_no_symlinks(source)
    files = []
    for parent, directories, names in os.walk(source, followlinks=False):
        ignored = _ignore_topic_maintenance(parent, directories + names)
        directories[:] = [name for name in directories if name not in ignored]
        files.extend(Path(parent) / name for name in names if name not in ignored)
    return files


def _storage_layout(root, storage):
    roots = [_storage_source(root, item, True) for item in storage["roots"]]
    for index, source in enumerate(roots):
        if any(source == other or source in other.parents or other in source.parents for other in roots[:index]):
            raise ValueError(f"Storage source roots overlap: {source}")
    mappings = []
    covered = set()
    source_paths = []
    for item in storage["mappings"]:
        is_directory = item["kind"] == "directory"
        source = _storage_source(root, item["source"], is_directory)
        if not any(source == parent or parent in source.parents for parent in roots):
            raise ValueError(f"Storage source is not in a declared root: {source}")
        if any(source == other or source in other.parents or other in source.parents for other in source_paths):
            raise ValueError(f"Storage source mappings overlap: {source}")
        source_paths.append(source)
        files = _storage_files(source) if is_directory else [source]
        if not is_directory and source.name in _ignore_topic_maintenance(source.parent, [source.name]):
            raise ValueError(f"Storage maintenance file cannot be published: {source}")
        covered.update(files)
        mappings.append((source, item["target"], is_directory, files))
    homepage = _storage_source(root, storage["homepage"], False)
    # Check the entire storage source tree, not only the declared roots. This
    # catches new files or directories that were never added to the layout.
    available = set(_storage_files(Path(root) / "series" / "storage"))
    if homepage not in available:
        raise ValueError(f"Storage homepage is not publishable: {homepage}")
    available.remove(homepage)
    if covered != available:
        missing = sorted(str(path) for path in available - covered)
        extra = sorted(str(path) for path in covered - available)
        raise ValueError(f"Storage mappings do not cover source files: missing={missing}, extra={extra}")
    return homepage, roots, mappings


def _check_storage_topic(root, docs, source, destination):
    """Ensure source placement and published navigation agree for each page."""
    if source.suffix != ".md":
        return
    parts = source.relative_to(Path(root) / "series" / "storage").parts
    top = parts[0]
    if top == "assets":
        return
    expected = STORAGE_TOPICS.get(top)
    if expected is None:
        raise ValueError(f"Storage source has no navigation topic: {source}")
    actual = owner(destination.relative_to(docs).as_posix())
    if actual != (STORAGE, expected):
        raise ValueError(f"Storage source and published navigation differ: {source} -> {destination} ({actual})")
    staged = destination.relative_to(docs).as_posix()
    if top == "01-memory-hierarchy":
        is_home = len(parts) == 2 and parts[1] == "README.md"
        if ((is_home and staged != MEMORY_HOME) or
                (not is_home and (len(parts) < 3 or
                                  parts[1] != MEMORY_PAGE_SECTION.get(staged)))):
            raise ValueError(f"Storage source and navigation section differ: {source} -> {destination}")
    elif top == "reading-and-reference":
        is_home = len(parts) == 2 and parts[1] == "README.md"
        if ((is_home and staged != RESOURCE_HOME) or
                (not is_home and (len(parts) < 3 or parts[1] != RESOURCE_PAGE_SECTION.get(staged)))):
            raise ValueError(f"Storage reference source and navigation section differ: {source} -> {destination}")
    elif top == "06-system-integration":
        section = "" if len(parts) == 2 else parts[1] if len(parts) == 3 else None
        if section is None or staged not in INTEGRATION_PAGE_SECTION or section != INTEGRATION_PAGE_SECTION[staged]:
            raise ValueError(f"Storage integration source and navigation section differ: {source} -> {destination}")


def _copy_storage(docs, published, mappings, aliases, root, roots):
    for source, target_value, is_directory, files in mappings:
        target = _storage_target(docs, target_value)
        if is_directory:
            target.mkdir(parents=True, exist_ok=True)
            published.add(source, target)
            for path in files:
                relative = path.relative_to(source)
                destination = target / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                # Register actual source directories only, even when multiple
                # source trees are merged into one published directory.
                parent = path.parent
                while parent != source:
                    published.add(parent, target / parent.relative_to(source))
                    parent = parent.parent
                if destination.exists():
                    raise ValueError(f"Storage output path collision: {destination}")
                _check_storage_topic(root, docs, path, destination)
                shutil.copy2(path, destination)
                published.add(path, destination)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                raise ValueError(f"Storage output path collision: {target}")
            _check_storage_topic(root, docs, source, target)
            shutil.copy2(source, target)
            published.add(source, target)
    for alias in aliases:
        source = _storage_source(root, alias["source"], True)
        if not any(source == parent or parent in source.parents for parent in roots):
            raise ValueError(f"Storage alias is not in a declared root: {source}")
        destination = _storage_target(docs, alias["target"])
        if not destination.is_dir():
            raise ValueError(f"Storage alias target is not a staged directory: {destination}")
        published.add(source, destination, rewrite_page=False)


def _copy_microarchitecture(root, docs, published, data, article, images):
    """Cover the source tree exactly once and retain explicit legacy targets."""
    base = root / "series/microarchitecture"
    homepage = _path_inside(root, data["homepage"], False)
    if homepage != base / "README.md":
        raise ValueError("Microarchitecture homepage must be series/microarchitecture/README.md")
    foundation_files = {article, *_storage_files(images)}
    covered = {homepage, *foundation_files}
    metadata = {}
    targets = set()
    for item in data["mappings"]:
        source = _path_inside(root, item["source"], False)
        if base not in source.parents or source in covered:
            raise ValueError(f"Invalid or repeated microarchitecture source: {source}")
        target_path = PurePosixPath(item["target"])
        if (target_path.is_absolute() or any(p in {".", "..", ".git"} for p in target_path.parts)
                or "\\" in item["target"] or not target_path.parts
                or target_path.parts[0] not in {"COMPUTE", "DMA", "CIM", "microarchitecture"}
                or item["target"].startswith("COMPUTE/wiki/06-memory-discipline/")):
            raise ValueError(f"Invalid microarchitecture publication target: {target_path}")
        destination = docs / target_path
        if destination.exists() or item["target"] in targets:
            raise ValueError(f"Microarchitecture output collision: {destination}")
        relative = source.relative_to(base).as_posix()
        if source.suffix == ".md":
            group = MICRO_TOPICS.get(relative.split("/")[0])
            if group is None or owner(item["target"]) != (MICRO, group):
                raise ValueError(f"Microarchitecture source and navigation differ: {source} -> {destination}")
            metadata[relative] = item["target"]
        covered.add(source)
        targets.add(item["target"])
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        published.add(source, destination)
        if source.name == "README.md":
            published.add(source.parent, destination.parent, rewrite_page=False)
    available = set(_storage_files(base))
    if covered - foundation_files != available - foundation_files:
        missing = sorted(str(p) for p in available - covered)
        extra = sorted(str(p) for p in covered - available - foundation_files)
        raise ValueError(f"Microarchitecture mappings do not cover source files: missing={missing}, extra={extra}")
    metadata["02-pipeline/electrical-timing-foundations.md"] = "electrical-timing-foundations.md"
    for item in data["aliases"]:
        path = PurePosixPath(item["source"])
        target = PurePosixPath(item["target"])
        if (not path.parts or not target.parts or path.is_absolute() or target.is_absolute()
                or ".." in path.parts or ".." in target.parts or ".git" in path.parts or ".git" in target.parts
                or "\\" in item["source"] or "\\" in item["target"]):
            raise ValueError("Microarchitecture alias escapes the checkout")
        # Foundation targets are copied later in stage_site.
        if not (docs / target).exists() and str(target) != "electrical-timing-foundations.md" and target.parts[0] != "img":
            raise ValueError(f"Missing microarchitecture alias target: {target}")
        published.add(root / path, docs / target, rewrite_page=False)
    shutil.copy2(homepage, docs / "microarchitecture.md")
    published.add(homepage, docs / "microarchitecture.md")
    (docs.parent / "microarchitecture-navigation.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")


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
    topics = {name: _path_inside(root, layout_data["topics"][name], True) for name in SOURCE_TOPICS}
    if len(set(topics.values())) != len(topics):
        raise ValueError("A topic source is staged to multiple paths")
    bus_legacy_index = _path_inside(root, BUS_LEGACY_INDEX, False)
    storage_home, storage_roots, storage_mappings = _storage_layout(root, layout_data["storage"])
    article = _path_inside(root, layout_data["foundations"]["article"], False)
    images = _path_inside(root, layout_data["foundations"]["images"], True)
    reviews = _path_inside(root, "docs/reviews", True)
    local_sources = [source_directory(root, item["local"]["directory"]) for item in entries if "local" in item]
    micro_source = root / "series/microarchitecture"
    for local in local_sources:
        if local == micro_source or local in micro_source.parents or micro_source in local.parents:
            raise ValueError(f"Microarchitecture overlaps a local series source: {local}")
    # An explicitly staged topic must never also be included recursively in a
    # local series: this could duplicate published pages or expose wiki.old.
    for topic, source in topics.items():
        for local in local_sources:
            if source == local or source in local.parents or local in source.parents:
                raise ValueError(f"Topic {topic} overlaps a local series source: {source} and {local}")
    for source in [storage_home, *storage_roots]:
        for local in local_sources:
            if source == local or source in local.parents or local in source.parents:
                raise ValueError(f"Storage overlaps a local series source: {source} and {local}")
    build_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=".stage-", dir=build_root) as temporary:
        staging = Path(temporary)
        docs = staging / "docs"
        docs.mkdir()
        published = PublishedPaths(root, docs)

        for name in SOURCE_TOPICS:
            source = topics[name]
            target = docs / name
            if name in INTERCONNECT_TOPICS:
                # Source topics are flat; retain the historical /TOPIC/wiki/
                # paths in the staged site. Register old source paths as link
                # aliases so published historical reviews still resolve.
                if (source / "wiki").exists():
                    raise ValueError(f"Interconnect topic contains a wiki directory: {source}")
                _assert_no_symlinks(source)
                shutil.copytree(source, target / "wiki", ignore=_ignore_topic_maintenance)
                published.add_tree(source, target / "wiki")
                published.add(source / "wiki", target / "wiki", rewrite_page=False)
                for staged in (target / "wiki").rglob("*"):
                    published.add(source / "wiki" / staged.relative_to(target / "wiki"), staged,
                                  rewrite_page=False)
                if name == "BUS":
                    shutil.copy2(bus_legacy_index, target / "README.md")
                    published.add(bus_legacy_index, target / "README.md")
                continue
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

        _copy_storage(docs, published, storage_mappings, layout_data["storage"]["aliases"], root, storage_roots)
        _copy_microarchitecture(root, docs, published, layout_data["microarchitecture"], article, images)

        for index in sorted((root / "foundations").glob("*/README.md")):
            source = source_directory(root, index.parent.relative_to(root).as_posix())
            target = docs / "foundations" / source.name
            copy_source(source, target, public_only=True)
            published.add_tree(source, target)

        # Keep the published URLs stable when the review sources move.
        _assert_no_symlinks(reviews)
        shutil.copytree(reviews, docs / "reviews")
        published.add_tree(reviews, docs / "reviews")
        _assert_no_symlinks(images)
        shutil.copytree(images, docs / "img")
        published.add_tree(images, docs / "img")
        shutil.copy2(article, docs / "electrical-timing-foundations.md")
        published.add(article, docs / "electrical-timing-foundations.md")
        shutil.copy2(root / "website" / "home.md", docs / "README.md")
        # Source links to the repository overview lead to the published home.
        # The copied website template is already written in site paths and must
        # not be treated as source Markdown for link rewriting.
        published.add(root / "README.md", docs / "README.md", rewrite_page=False)
        shutil.copy2(root / "website" / "series.md", docs / "series.md")
        shutil.copy2(storage_home, docs / "storage.md")
        published.add(storage_home, docs / "storage.md")
        shutil.copy2(root / "website" / "interconnect.md", docs / "interconnect.md")
        published.add(root / "series/interconnect/README.md", docs / "interconnect.md", rewrite_page=False)
        shutil.copy2(root / "website" / "articles.md", docs / "articles.md")
        shutil.copy2(root / "website" / "visuals.md", docs / "visuals.md")
        shutil.copytree(root / "website" / "assets", docs / "assets")

        checkouts = {}
        for item in entries:
            if "local" in item:
                local = item["local"]
                selected = source_directory(root, local["directory"])
                if local["publish"] == "external/workload-wiki":
                    stage_workload(selected, docs / local["publish"], published)
                elif local["publish"] == "series/inference-runtime":
                    stage_inference(selected, docs / local["publish"], published)
                else:
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
        (staging / "microarchitecture-navigation.json").replace(build_root / "microarchitecture-navigation.json")
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
