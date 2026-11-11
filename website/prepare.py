#!/usr/bin/env python3
"""Stage the published sources without changing the existing wiki files."""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / ".site-build" / "docs"
TOPICS = ("RAM", "COMPUTE", "BUS", "NOC", "DMA", "PCIE", "CIM", "CPO", "FAB")


def main():
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True)

    for name in TOPICS:
        source = ROOT / name
        target = DOCS / name
        shutil.copytree(source / "wiki", target / "wiki")
        for filename in ("README.md", "self-test-questions.md"):
            if (source / filename).is_file():
                shutil.copy2(source / filename, target / filename)

    shutil.copytree(ROOT / "reviews", DOCS / "reviews")
    shutil.copy2(ROOT / "electrical-timing-foundations.md", DOCS)
    shutil.copy2(ROOT / "website" / "home.md", DOCS / "README.md")
    shutil.copy2(ROOT / "website" / "series.md", DOCS / "series.md")
    shutil.copy2(ROOT / "website" / "microarchitecture.md", DOCS / "microarchitecture.md")
    shutil.copy2(ROOT / "website" / "articles.md", DOCS / "articles.md")
    shutil.copy2(ROOT / "website" / "visuals.md", DOCS / "visuals.md")
    shutil.copytree(ROOT / "website" / "assets", DOCS / "assets")
    print(f"Staged source documents in {DOCS}")


if __name__ == "__main__":
    main()
