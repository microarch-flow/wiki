#!/usr/bin/env python3
"""Stage the published sources without changing the existing wiki files."""

import argparse
import json
from pathlib import Path
import shutil
import tempfile

from sources import copy_source, fetch_checkout, load_series, source_directory


ROOT = Path(__file__).resolve().parent.parent
TOPICS = ("RAM", "COMPUTE", "BUS", "NOC", "DMA", "PCIE", "CIM", "CPO", "FAB", "SERDES", "HBF")


def stage_site(root=ROOT, build_root=None, registry=None, source_root=None):
    """Build a complete staging tree before replacing the previous one.

    With source_root, each external series uses the checkout named by its slug.
    Otherwise configured GitHub repositories are fetched at their selected refs.
    """
    root = Path(root)
    build_root = Path(build_root) if build_root is not None else root / ".site-build"
    registry = Path(registry) if registry is not None else root / "website" / "series.json"
    source_root = Path(source_root) if source_root is not None else None
    entries = load_series(registry)
    build_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=".stage-", dir=build_root) as temporary:
        staging = Path(temporary)
        docs = staging / "docs"
        docs.mkdir()

        for name in TOPICS:
            source = root / name
            target = docs / name
            shutil.copytree(source / "wiki", target / "wiki")
            for filename in ("README.md", "self-test-questions.md"):
                if (source / filename).is_file():
                    shutil.copy2(source / filename, target / filename)

        shutil.copytree(root / "reviews", docs / "reviews")
        shutil.copytree(root / "img", docs / "img")
        shutil.copy2(root / "electrical-timing-foundations.md", docs)
        shutil.copy2(root / "website" / "home.md", docs / "README.md")
        shutil.copy2(root / "website" / "series.md", docs / "series.md")
        shutil.copy2(root / "website" / "microarchitecture.md", docs / "microarchitecture.md")
        shutil.copy2(root / "website" / "articles.md", docs / "articles.md")
        shutil.copy2(root / "website" / "visuals.md", docs / "visuals.md")
        shutil.copytree(root / "website" / "assets", docs / "assets")

        checkouts = {}
        for item in entries:
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
