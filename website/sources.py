"""Validate and stage explicitly configured external series."""

import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess


SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
REPOSITORY = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*\Z")
REF = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]*\Z")


def load_series(registry):
    """Read the series registry and reject ambiguous source definitions."""
    data = json.loads(Path(registry).read_text(encoding="utf-8"))
    entries = data.get("series") if isinstance(data, dict) else None
    if not isinstance(entries, list) or not entries:
        raise ValueError("Series registry must contain a non-empty series list")

    slugs = set()
    titles = set()
    for item in entries:
        if not isinstance(item, dict):
            raise ValueError("Each series must be an object")
        name = item.get("title")
        description = item.get("description")
        if not isinstance(name, str) or not name.strip() or not isinstance(description, str) or not description.strip():
            raise ValueError("Each series needs a non-empty title and description")
        if name.strip() in titles:
            raise ValueError(f"Duplicate series title: {name.strip()}")
        titles.add(name.strip())
        kinds = [kind for kind in ("page", "url", "source") if kind in item]
        if len(kinds) != 1:
            raise ValueError("Each series needs exactly one of page, url, or source")
        if kinds[0] != "source":
            if not isinstance(item[kinds[0]], str) or not item[kinds[0]].strip():
                raise ValueError(f"Series {name!r} has an empty {kinds[0]}")
            continue

        source = item["source"]
        if name.strip() in {"首页", "系列", "微架构"}:
            raise ValueError(f"Source series title conflicts with an existing navigation label: {name.strip()}")
        if not isinstance(source, dict) or set(source) != {"slug", "repository", "ref", "directory"}:
            raise ValueError(f"Series {name!r} needs source slug, repository, ref, and directory")
        slug, repository, ref, directory = (source[key] for key in ("slug", "repository", "ref", "directory"))
        if not isinstance(slug, str) or not SLUG.fullmatch(slug):
            raise ValueError(f"Invalid source slug: {slug!r}")
        if slug in slugs:
            raise ValueError(f"Duplicate source slug: {slug}")
        slugs.add(slug)
        if not isinstance(repository, str) or not REPOSITORY.fullmatch(repository):
            raise ValueError(f"Invalid GitHub repository: {repository!r}")
        if not isinstance(ref, str) or not REF.fullmatch(ref) or ".." in ref or ref.endswith("/"):
            raise ValueError(f"Invalid Git ref: {ref!r}")
        if not isinstance(directory, str) or not directory or "\\" in directory:
            raise ValueError(f"Invalid source directory: {directory!r}")
        path = PurePosixPath(directory)
        if path.is_absolute() or ".." in path.parts or ".git" in path.parts:
            raise ValueError(f"Source directory must stay inside the checkout: {directory!r}")
    return entries


def series_landing(directory):
    """Require a single, real entry page for an imported series."""
    pages = [directory / name for name in ("README.md", "index.md") if (directory / name).is_file()]
    if len(pages) != 1:
        raise ValueError(f"Source directory needs exactly one README.md or index.md: {directory}")
    return pages[0]


def source_directory(checkout, directory):
    """Select a directory inside a checkout without following symlinks."""
    path = Path(checkout)
    for part in PurePosixPath(directory).parts:
        path = path / part
        if path.is_symlink():
            raise ValueError(f"Source directory contains a symlink: {path}")
    if not path.is_dir():
        raise ValueError(f"Source directory does not exist: {path}")
    return path


def copy_source(source, destination):
    """Copy an explicitly selected directory; never publish Git metadata or symlinks."""
    series_landing(source)
    outputs = {}
    for root, directories, files in os.walk(source, followlinks=False):
        directories[:] = [name for name in directories if name != ".git"]
        for name in directories + files:
            path = Path(root) / name
            if name == ".git":
                continue
            if path.is_symlink():
                raise ValueError(f"Source contains a symlink: {path}")
        for name in files:
            if name == ".git":
                continue
            path = Path(root) / name
            relative = path.relative_to(source)
            if path.suffix in {".markdown", ".mdown", ".mkdn", ".mkd"} or (path.suffix.lower() == ".md" and path.suffix != ".md"):
                raise ValueError(f"Source Markdown files must use the .md extension: {path}")
            if path.suffix == ".md":
                output = relative.parent / "index.html" if name in {"README.md", "index.md"} else relative.parent / path.stem / "index.html"
            else:
                output = relative
            if output in outputs:
                raise ValueError(f"Source output path collision: {outputs[output]} and {relative} both produce {output}")
            outputs[output] = relative
    for output, relative in outputs.items():
        for parent in output.parents:
            if parent in outputs:
                raise ValueError(f"Source output path collision: {outputs[parent]} blocks {relative}")
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns(".git"))


def fetch_checkout(source, destination):
    """Fetch a configured GitHub repository and revision without a shell."""
    destination.mkdir(parents=True)
    repository = source["repository"]
    ref = source["ref"]
    print(f"Fetching {repository} at {ref}", flush=True)
    environment = os.environ.copy()
    environment["GIT_TERMINAL_PROMPT"] = "0"
    subprocess.run(["git", "init", "--quiet", str(destination)], check=True)
    subprocess.run(
        ["git", "-C", str(destination), "fetch", "--quiet", "--depth=1", f"https://github.com/{repository}.git", ref],
        check=True, env=environment,
    )
    subprocess.run(["git", "-C", str(destination), "checkout", "--quiet", "--detach", "FETCH_HEAD"], check=True)
    revision = subprocess.run(
        ["git", "-C", str(destination), "rev-parse", "HEAD"], check=True, capture_output=True, text=True,
    ).stdout.strip()
    print(f"Resolved {repository} to {revision}", flush=True)
