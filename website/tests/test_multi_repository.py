"""Exercise multi-repository staging and a real MkDocs build with local Git fixtures."""

from html import unescape
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urljoin

from mkdocs.commands.build import build
from mkdocs.config import load_config


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "website"))
from prepare import SOURCE_TOPICS, stage_site  # noqa: E402


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_wiki(root):
    write(root / "README.md", "# Repository overview\n")
    for name in SOURCE_TOPICS:
        write(root / name / "wiki" / "README.md", f"# {name}\n")
    storage = root / "series/storage"
    storage_roots = ("01-memory-hierarchy", "02-sram", "03-dram", "04-dram-controller",
                     "05-hbf", "06-system-integration", "assets")
    for name in storage_roots:
        (storage / name).mkdir(parents=True, exist_ok=True)
    write(storage / "README.md", "# 存储系统\n")
    write(storage / "01-memory-hierarchy/README.md", "# RAM\n")
    write(storage / "05-hbf/README.md", "# HBF\n")
    write(root / "docs" / "reviews" / "2026-11-09-topic-review.md", "# Review\n")
    for number in (2, 3):
        write(root / "docs" / "reviews" / f"round-{number}" / "README.md", f"# Round {number}\n")
    write(root / "docs/reviews/round-3/model.py", "print('fixture model')\n")
    write(root / "docs/reviews/round-3/expected.json", '{"fixture": true}\n')
    write(root / "img" / "image.svg", "<svg xmlns='http://www.w3.org/2000/svg'/>\n")
    write(root / "electrical-timing-foundations.md", "# Timing\n")
    for name, content in {
        "home.md": "# 首页\n\n<!-- site-series -->\n",
        "series.md": "# 系列\n\n<!-- site-series -->\n",
        "microarchitecture.md": "# 微架构\n",
        "interconnect.md": "# 芯片与系统互连\n",
        "articles.md": "# 精选文章\n",
        "visuals.md": "# 互动图解\n",
    }.items():
        write(root / "website" / name, content)
    write(root / "website/source-layout.json", json.dumps({
        "topics": {name: name for name in SOURCE_TOPICS},
        "storage": {
            "homepage": "series/storage/README.md",
            "roots": [f"series/storage/{name}" for name in storage_roots],
            "mappings": [
                {"kind": "file", "source": "series/storage/01-memory-hierarchy/README.md", "target": "RAM/wiki/README.md"},
                {"kind": "directory", "source": "series/storage/05-hbf", "target": "HBF/wiki"},
                {"kind": "directory", "source": "series/storage/assets", "target": "RAM/wiki/img"},
            ],
            "aliases": [{"source": "series/storage/01-memory-hierarchy", "target": "RAM/wiki"}],
        },
        "foundations": {"article": "electrical-timing-foundations.md", "images": "img"},
    }))
    shutil.copytree(ROOT / "website" / "assets", root / "website" / "assets")


def series(slug, repository, directory):
    return {
        "title": f"{slug} 系列",
        "description": f"{slug} 内容",
        "source": {"slug": slug, "repository": repository, "ref": "main", "directory": directory},
    }


def git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def fixture_repo(path, files):
    path.mkdir(parents=True)
    git("init", "--quiet", str(path))
    git("symbolic-ref", "HEAD", "refs/heads/main", cwd=path)
    for name, content in files.items():
        write(path / name, content)
    git("add", ".", cwd=path)
    git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
        "commit", "--quiet", "-m", "Fixture", cwd=path)


class MultiRepositoryTests(unittest.TestCase):
    def test_storage_split_preserves_public_links_search_and_coverage(self):
        with tempfile.TemporaryDirectory() as temp:
            temporary = Path(temp)
            wiki = temporary / "wiki"
            fixture_wiki(wiki)
            storage = wiki / "series/storage"
            write(storage / "README.md", (
                "# 存储系统\n\n[SRAM](02-sram/foundations/README.md?view=1#sram)\n"
                "[HBM](03-dram/hbm-stacked-wide-io.md#layers)\n"
            ))
            write(storage / "01-memory-hierarchy/overview/README.md", (
                "# Overview\n\n"
                "[DRAM](../../03-dram/protocols/README.md?mode=1#timing)\n"
                "![图](../../assets/overview.svg?size=1#shape)\n"
                "[上级](../)\n"
                # A merged destination must not invent this source path.
                "[缺失](../ai-chip-memory/hbm-vs-lpddr-for-npu.md#missing)\n"
            ))
            write(storage / "02-sram/foundations/README.md", "# SRAM\n\n## SRAM\n")
            write(storage / "03-dram/protocols/README.md", (
                "# DRAM\n\n## Timing\n\n"
                "[概览](../../01-memory-hierarchy/overview/README.md#overview)\n"
            ))
            write(storage / "03-dram/hbm-stacked-wide-io.md", (
                "# HBM\n\n## Layers\n\n"
                "[封装](../06-system-integration/packaging/README.md?view=1#pkg)\n"
            ))
            write(storage / "06-system-integration/packaging/README.md", "# Packaging\n\n## Pkg\n")
            write(storage / "06-system-integration/hbm-vs-lpddr-for-npu.md", "# Selection\n")
            write(storage / "01-memory-hierarchy/ai-chip-memory/README.md", "# AI memory\n")
            write(storage / "01-memory-hierarchy/cache-scratchpad/README.md", "# Cache\n")
            write(storage / "assets/overview.svg", "<svg/>\n")
            write(storage / "01-memory-hierarchy/task.md", "# Historical task\n")
            write(wiki / "COMPUTE/wiki/README.md", (
                "# COMPUTE\n\n[存储首页](../../series/storage/README.md#storage)\n"
                "[缓存](../../series/storage/01-memory-hierarchy/cache-scratchpad/README.md#cache)\n"
            ))

            layout_path = wiki / "website/source-layout.json"
            layout = json.loads(layout_path.read_text(encoding="utf-8"))
            extra = [
                ("directory", "01-memory-hierarchy/overview", "RAM/wiki/01-overview"),
                ("directory", "02-sram/foundations", "RAM/wiki/02-sram-foundations"),
                ("directory", "03-dram/protocols", "RAM/wiki/05-dram-protocol-families"),
                ("file", "03-dram/hbm-stacked-wide-io.md", "RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io.md"),
                ("directory", "06-system-integration/packaging", "RAM/wiki/08-packaging-integration"),
                # Place the split file first to exercise merging in both orders.
                ("file", "06-system-integration/hbm-vs-lpddr-for-npu.md", "RAM/wiki/09-ai-chip-memory-architecture/hbm-vs-lpddr-for-npu.md"),
                ("directory", "01-memory-hierarchy/ai-chip-memory", "RAM/wiki/09-ai-chip-memory-architecture"),
                ("directory", "01-memory-hierarchy/cache-scratchpad", "COMPUTE/wiki/06-memory-discipline"),
            ]
            layout["storage"]["mappings"].extend({"kind": kind, "source": f"series/storage/{source}", "target": target}
                                                 for kind, source, target in extra)
            layout_path.write_text(json.dumps(layout), encoding="utf-8")
            registry = temporary / "series.json"
            registry.write_text(json.dumps({"series": [{"title": "存储", "description": "storage", "page": "storage.md"}]}), encoding="utf-8")
            build_root = temporary / "build"
            stage_site(root=wiki, build_root=build_root, registry=registry)
            docs = build_root / "docs"

            landing = (docs / "storage.md").read_text(encoding="utf-8")
            self.assertIn("[SRAM](RAM/wiki/02-sram-foundations/README.md?view=1#sram)", landing)
            self.assertIn("[HBM](RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io.md#layers)", landing)
            overview = (docs / "RAM/wiki/01-overview/README.md").read_text(encoding="utf-8")
            self.assertIn("[DRAM](../05-dram-protocol-families/README.md?mode=1#timing)", overview)
            self.assertIn("![图](../img/overview.svg?size=1#shape)", overview)
            self.assertIn("[上级](../)", overview)
            self.assertIn("[缺失](../ai-chip-memory/hbm-vs-lpddr-for-npu.md#missing)", overview)
            hbm = (docs / "RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io.md").read_text(encoding="utf-8")
            self.assertIn("[封装](../08-packaging-integration/README.md?view=1#pkg)", hbm)
            compute = (docs / "COMPUTE/wiki/README.md").read_text(encoding="utf-8")
            self.assertIn("[存储首页](../../storage.md#storage)", compute)
            self.assertIn("[缓存](06-memory-discipline/README.md#cache)", compute)
            self.assertTrue((docs / "RAM/wiki/09-ai-chip-memory-architecture/hbm-vs-lpddr-for-npu.md").is_file())
            self.assertTrue((docs / "COMPUTE/wiki/06-memory-discipline/README.md").is_file())
            self.assertFalse(any(docs.rglob("task.md")))

            # The deliberately unresolved link above tests ghost mappings;
            # remove it before the real build, which should have no bad links.
            overview_source = storage / "01-memory-hierarchy/overview/README.md"
            overview_source.write_text(overview_source.read_text(encoding="utf-8").replace(
                "[缺失](../ai-chip-memory/hbm-vs-lpddr-for-npu.md#missing)\n", ""), encoding="utf-8")
            stage_site(root=wiki, build_root=build_root, registry=registry)
            site = temporary / "site"
            config = load_config(config_file=str(ROOT / "mkdocs.yml"), docs_dir=str(docs), site_dir=str(site))
            build(config)
            self.assertTrue((site / "storage/index.html").is_file())
            self.assertTrue((site / "RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io/index.html").is_file())
            self.assertTrue((site / "COMPUTE/wiki/06-memory-discipline/index.html").is_file())
            search = json.loads((site / "search/search_index.json").read_text(encoding="utf-8"))
            locations = {entry["location"] for entry in search["docs"]}
            self.assertIn("RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io/", locations)
            self.assertIn("COMPUTE/wiki/06-memory-discipline/", locations)

            # Fail closed for a new file inside or outside declared roots.
            for path in (storage / "06-system-integration/new.md", storage / "new-topic/new.md", storage / "new.svg"):
                write(path, "new\n")
                with self.assertRaisesRegex(ValueError, "Storage mappings do not cover source files"):
                    stage_site(root=wiki, build_root=build_root, registry=registry)
                path.unlink()
            self.assertEqual((docs / "storage.md").read_text(encoding="utf-8"), landing)

            duplicate = storage / "01-memory-hierarchy/ai-chip-memory/hbm-vs-lpddr-for-npu.md"
            write(duplicate, "# Duplicate\n")
            with self.assertRaisesRegex(ValueError, "Storage output path collision"):
                stage_site(root=wiki, build_root=build_root, registry=registry)
            duplicate.unlink()

            symlink = storage / "02-sram/foundations/leak.md"
            symlink.symlink_to(temporary / "outside.md")
            with self.assertRaisesRegex(ValueError, "symlink"):
                stage_site(root=wiki, build_root=build_root, registry=registry)
            symlink.unlink()

            entry = layout["storage"]["mappings"][-1]
            entry["target"] = "RAM/wiki/02-sram-foundations/cache"
            layout_path.write_text(json.dumps(layout), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "published navigation differ"):
                stage_site(root=wiki, build_root=build_root, registry=registry)
            self.assertEqual((docs / "storage.md").read_text(encoding="utf-8"), landing)

    def test_moved_sources_keep_site_paths_and_rewrite_cross_links(self):
        with tempfile.TemporaryDirectory() as temp:
            wiki = Path(temp) / "wiki"
            fixture_wiki(wiki)
            development = wiki / "series/chip-development"
            development.mkdir(parents=True)
            shutil.move(str(wiki / "FAB"), development / "FAB")
            process = development / "process"
            write(process / "README.md", (
                "# Development\n\n"
                "[FAB](../FAB/wiki/README.md?view=1#topic)\n"
                "![图](../FAB/wiki/img/diagram.svg?size=1#shape)\n"
                "[目录](../FAB/wiki/)\n"
                "<a href=\"../FAB/wiki/README.md?view=1#topic\">FAB</a>\n"
                "<img src=\"../FAB/wiki/img/diagram.svg?size=1#shape\">\n"
                "[ref]: ../FAB/wiki/README.md?view=1#topic\n"
                "`[code](../FAB/wiki/README.md)`\n"
                "```markdown\n[code](../FAB/wiki/README.md)\n```\n"
                "    [indented](../FAB/wiki/README.md)\n"
                "<pre><a href=\"../FAB/wiki/README.md\">code</a></pre>\n"
            ))
            write(process / "AGENTS.md", "# private\n")
            write(process / "wiki.old/private.md", "# private\n")
            write(development / "FAB/wiki/README.md", (
                "# FAB\n\n[流程](../../process/README.md?x=1#top)\n"
                "[评审](../../../../docs/reviews/round-2/README.md#topic)\n"
            ))
            write(development / "FAB/wiki/img/diagram.svg", "<svg/>\n")
            write(development / "FAB/wiki/AGENTS.md", "# private\n")
            write(development / "FAB/wiki/raw/private.md", "# private\n")
            write(development / "FAB/wiki.old/private.md", "# private\n")
            write(wiki / "docs/reviews/round-2/README.md", (
                "# Review\n\n[FAB](../../../series/chip-development/FAB/wiki/README.md#topic)\n"
                "[首页](../../../README.md?ref=review#overview)\n"
            ))
            template = "# 首页\n\n[模板链接](docs/reviews/round-2/README.md)\n"
            write(wiki / "website/home.md", template)
            layout_path = wiki / "website/source-layout.json"
            layout = json.loads(layout_path.read_text(encoding="utf-8"))
            layout["topics"]["FAB"] = "series/chip-development/FAB"
            layout_path.write_text(json.dumps(layout), encoding="utf-8")
            registry = wiki / "website/series.json"
            registry.write_text(json.dumps({"series": [{
                "title": "芯片开发与实现", "description": "development",
                "local": {"directory": "series/chip-development/process", "publish": "series/chip-development"},
            }]}), encoding="utf-8")
            build = Path(temp) / "build"
            stage_site(root=wiki, build_root=build)
            docs = build / "docs"
            staged = (docs / "series/chip-development/README.md").read_text(encoding="utf-8")
            self.assertIn("[FAB](../../FAB/wiki/README.md?view=1#topic)", staged)
            self.assertIn("![图](../../FAB/wiki/img/diagram.svg?size=1#shape)", staged)
            self.assertIn("[目录](../../FAB/wiki/)", staged)
            self.assertIn('<a href="../../FAB/wiki/?view=1#topic">FAB</a>', staged)
            self.assertIn('<img src="../../FAB/wiki/img/diagram.svg?size=1#shape">', staged)
            self.assertIn("[ref]: ../../FAB/wiki/README.md?view=1#topic", staged)
            self.assertIn("`[code](../FAB/wiki/README.md)`", staged)
            self.assertIn("```markdown\n[code](../FAB/wiki/README.md)\n```", staged)
            self.assertIn("    [indented](../FAB/wiki/README.md)", staged)
            self.assertIn('<pre><a href="../FAB/wiki/README.md">code</a></pre>', staged)
            self.assertIn("[流程](../../series/chip-development/README.md?x=1#top)",
                          (docs / "FAB/wiki/README.md").read_text(encoding="utf-8"))
            self.assertIn("[评审](../../reviews/round-2/README.md#topic)",
                          (docs / "FAB/wiki/README.md").read_text(encoding="utf-8"))
            self.assertIn("[FAB](../../FAB/wiki/README.md#topic)",
                          (docs / "reviews/round-2/README.md").read_text(encoding="utf-8"))
            self.assertIn("[首页](../../README.md?ref=review#overview)",
                          (docs / "reviews/round-2/README.md").read_text(encoding="utf-8"))
            self.assertEqual((docs / "README.md").read_text(encoding="utf-8"), template)
            for name in ("FAB/wiki/AGENTS.md", "FAB/wiki/raw/private.md", "FAB/wiki.old/private.md",
                         "series/chip-development/AGENTS.md", "series/chip-development/wiki.old/private.md"):
                self.assertFalse((docs / name).exists(), name)

            # A topic nested inside the selected local series must not be
            # recursively staged a second time (or expose its wiki.old).
            write(development / "README.md", "# Development\n")
            data = json.loads(registry.read_text(encoding="utf-8"))
            data["series"][0]["local"]["directory"] = "series/chip-development"
            registry.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "overlaps a local series source"):
                stage_site(root=wiki, build_root=build)
            self.assertEqual((docs / "series/chip-development/README.md").read_text(encoding="utf-8"), staged)

            data["series"][0]["local"]["directory"] = "series/chip-development/process"
            registry.write_text(json.dumps(data), encoding="utf-8")
            layout["storage"]["mappings"][0]["source"] = "../outside"
            layout_path.write_text(json.dumps(layout), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "inside the checkout"):
                stage_site(root=wiki, build_root=build)
            self.assertEqual((docs / "series/chip-development/README.md").read_text(encoding="utf-8"), staged)

            layout["storage"]["mappings"][0]["source"] = "series/storage/01-memory-hierarchy/README.md"
            layout["topics"]["COMPUTE"] = layout["topics"]["BUS"]
            layout_path.write_text(json.dumps(layout), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "staged to multiple paths"):
                stage_site(root=wiki, build_root=build)
            self.assertEqual((docs / "series/chip-development/README.md").read_text(encoding="utf-8"), staged)

    def test_local_source_preserves_public_path_and_excludes_maintenance(self):
        with tempfile.TemporaryDirectory() as temp:
            temporary = Path(temp)
            wiki = temporary / "wiki"
            fixture_wiki(wiki)
            write(wiki / "series/local/README.md", "# 本地系列\n\n[正文](chapter/article.md)\n")
            write(wiki / "series/local/chapter/article.md", "# 本地正文\n\n![图](../img/chart.svg)\n")
            write(wiki / "series/local/img/chart.svg", "<svg xmlns='http://www.w3.org/2000/svg'/>\n")
            write(wiki / "series/local/AGENTS.md", "# 内部维护\n")
            write(wiki / "series/local/task.md", "# 维护任务\n")
            write(wiki / "series/local/raw/private.md", "# 原始资料\n")
            write(wiki / "series/local/source.pdf", "not for publication\n")
            registry = temporary / "series.json"
            entries = [{"title": "微架构", "description": "本仓库", "page": "microarchitecture.md"},
                       {"title": "本地系列", "description": "本地正文", "local": {
                           "directory": "series/local", "publish": "external/legacy"}}]
            registry.write_text(json.dumps({"series": entries}, ensure_ascii=False), encoding="utf-8")
            build_root = temporary / "build"
            with patch("prepare.fetch_checkout", side_effect=AssertionError("unexpected remote fetch")):
                stage_site(root=wiki, build_root=build_root, registry=registry)
            docs = build_root / "docs"
            self.assertTrue((docs / "external/legacy/img/chart.svg").is_file())
            for name in ("AGENTS.md", "task.md", "raw/private.md", "source.pdf"):
                self.assertFalse((docs / "external/legacy" / name).exists())

            site = temporary / "site"
            config = load_config(config_file=str(ROOT / "mkdocs.yml"), docs_dir=str(docs), site_dir=str(site))
            build(config)
            article = (site / "external/legacy/chapter/article/index.html").read_text(encoding="utf-8")
            self.assertIn("本地系列", article)
            self.assertIn('class="site-breadcrumbs"', article)
            search = json.loads((site / "search/search_index.json").read_text(encoding="utf-8"))
            matches = [entry for entry in search["docs"] if entry["location"] == "external/legacy/chapter/article/"]
            self.assertEqual(len(matches), 1)
            locations = {entry["location"] for entry in search["docs"]}
            for location in ("reviews/2026-11-09-topic-review/", "reviews/round-2/", "reviews/round-3/"):
                self.assertNotIn(location, locations)
                self.assertTrue((site / location / "index.html").is_file())
            self.assertFalse(any(location.startswith("reviews/") for location in locations))
            self.assertEqual((site / "reviews/round-3/model.py").read_text(encoding="utf-8"),
                             "print('fixture model')\n")
            self.assertEqual((site / "reviews/round-3/expected.json").read_text(encoding="utf-8"),
                             '{"fixture": true}\n')

            (wiki / "series/local/leak.md").symlink_to(temporary / "outside.md")
            with self.assertRaisesRegex(ValueError, "symlink"):
                stage_site(root=wiki, build_root=build_root, registry=registry)
            (wiki / "series/local/leak.md").unlink()
            entries[1]["local"]["publish"] = "microarchitecture"
            registry.write_text(json.dumps({"series": entries}, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "output path collision"):
                stage_site(root=wiki, build_root=build_root, registry=registry)
            self.assertTrue((docs / "external/legacy/chapter/article.md").is_file())

    def test_two_git_sources_build_with_shared_navigation_and_search(self):
        with tempfile.TemporaryDirectory() as temp:
            temporary = Path(temp)
            wiki = temporary / "wiki"
            fixture_wiki(wiki)
            remotes = temporary / "remotes"
            fixture_repo(remotes / "example" / "alpha.git", {
                "blog/README.md": "# Alpha 首页\n\n[阅读文章](article.md)\n",
                "blog/article.md": "# Alpha 文章\n\n[章节](chapter/index.md)\n\n![图片](img/chart.svg)\n",
                "blog/chapter/index.md": "# Alpha 章节\n\n[深入阅读](detail.md)\n",
                "blog/chapter/detail.md": "# Alpha 深入文章\n",
                "blog/img/chart.svg": "<svg xmlns='http://www.w3.org/2000/svg'/>\n",
                "not-for-publication.txt": "outside selected directory\n",
            })
            fixture_repo(remotes / "example" / "beta.git", {
                "docs/index.md": "# Beta 首页\n\n[阅读文章](article.md)\n",
                "docs/article.md": "# Beta 文章\n\n来自第二个仓库。\n",
            })
            beta_revision = git("rev-parse", "HEAD", cwd=remotes / "example" / "beta.git").strip()
            registry = temporary / "series.json"
            registry.write_text(json.dumps({"series": [
                {"title": "芯片微架构笔记", "description": "本仓库", "page": "microarchitecture.md"},
                series("alpha", "example/alpha", "blog"),
                series("beta", "example/beta", "docs"),
            ]}, ensure_ascii=False), encoding="utf-8")

            git_config = temporary / "gitconfig"
            write(git_config, f'[url "{remotes.as_uri()}/"]\n\tinsteadOf = https://github.com/\n')
            build_root = temporary / "build"
            with patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": str(git_config), "GIT_CONFIG_NOSYSTEM": "1"}):
                stage_site(root=wiki, build_root=build_root, registry=registry)

            docs = build_root / "docs"
            self.assertTrue((docs / "external/alpha/img/chart.svg").is_file())
            self.assertFalse((docs / "external/alpha/not-for-publication.txt").exists())
            self.assertFalse((docs / "external/alpha/.git").exists())

            site = temporary / "site"
            config = load_config(config_file=str(ROOT / "mkdocs.yml"), docs_dir=str(docs), site_dir=str(site))
            build(config)

            home = (site / "index.html").read_text(encoding="utf-8")
            self.assertIn('href="external/alpha/"', home)
            self.assertIn('href="external/beta/"', home)
            self.assertIn("alpha 系列", home)
            self.assertIn("beta 系列", home)
            series_page = (site / "series/index.html").read_text(encoding="utf-8")
            self.assertIn('href="../external/alpha/"', series_page)
            self.assertIn('href="../external/beta/"', series_page)
            self.assertTrue((site / "RAM/wiki/index.html").is_file())
            self.assertTrue((site / "external/alpha/img/chart.svg").is_file())

            article = (site / "external/alpha/article/index.html").read_text(encoding="utf-8")
            self.assertIn('href="../chapter/"', article)
            self.assertIn('src="../img/chart.svg"', article)
            self.assertIn('class="site-breadcrumbs"', article)
            self.assertIn("alpha 系列", article)
            primary = article.split('<div class="md-sidebar md-sidebar--primary"', 1)[1].split('<div class="md-sidebar md-sidebar--secondary"', 1)[0]
            active = re.findall(r'<a\s+href="([^"]+)"\s+class="[^"]*\bmd-nav__link--active\b[^"]*"[^>]*aria-current="page"', primary)
            self.assertEqual(len(active), 1)
            self.assertEqual(urljoin("https://example.test/external/alpha/article/", unescape(active[0])),
                             "https://example.test/external/alpha/article/")
            chapter = (site / "external/alpha/chapter/detail/index.html").read_text(encoding="utf-8")
            self.assertIn("Alpha 章节", chapter)
            self.assertIn("Alpha 深入文章", chapter)

            search = json.loads((site / "search/search_index.json").read_text(encoding="utf-8"))
            locations = {unescape(entry["location"]) for entry in search["docs"]}
            self.assertIn("external/alpha/article/", locations)
            self.assertIn("external/beta/article/", locations)

            write(remotes / "example" / "beta.git" / "docs" / "article.md", "# Beta 更新后的文章\n")
            git("add", ".", cwd=remotes / "example" / "beta.git")
            git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                "commit", "--quiet", "-m", "Update", cwd=remotes / "example" / "beta.git")
            with patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": str(git_config), "GIT_CONFIG_NOSYSTEM": "1"}):
                stage_site(root=wiki, build_root=build_root, registry=registry)
                self.assertIn("更新后", (docs / "external/beta/article.md").read_text(encoding="utf-8"))
                data = json.loads(registry.read_text(encoding="utf-8"))
                data["series"][2]["source"]["ref"] = beta_revision
                registry.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
                stage_site(root=wiki, build_root=build_root, registry=registry)
                self.assertIn("来自第二个仓库", (docs / "external/beta/article.md").read_text(encoding="utf-8"))

    def test_unavailable_or_unsafe_source_preserves_previous_staging(self):
        with tempfile.TemporaryDirectory() as temp:
            temporary = Path(temp)
            wiki = temporary / "wiki"
            fixture_wiki(wiki)
            sources = temporary / "checkouts"
            write(sources / "alpha" / "docs" / "README.md", "# Alpha 首页\n")
            registry = temporary / "series.json"
            entries = [{"title": "微架构", "description": "本仓库", "page": "microarchitecture.md"},
                       series("alpha", "example/alpha", "docs")]
            registry.write_text(json.dumps({"series": entries}, ensure_ascii=False), encoding="utf-8")
            build_root = temporary / "build"
            stage_site(root=wiki, build_root=build_root, registry=registry, source_root=sources)
            staged_registry = (build_root / "series.json").read_text(encoding="utf-8")

            outside = temporary / "private.txt"
            write(outside, "private\n")
            (sources / "alpha" / "docs" / "leak.txt").symlink_to(outside)
            with self.assertRaisesRegex(ValueError, "symlink"):
                stage_site(root=wiki, build_root=build_root, registry=registry, source_root=sources)
            self.assertEqual((build_root / "docs/external/alpha/README.md").read_text(encoding="utf-8"), "# Alpha 首页\n")
            self.assertEqual((build_root / "series.json").read_text(encoding="utf-8"), staged_registry)
            self.assertFalse((build_root / "docs/external/alpha/leak.txt").exists())

            (sources / "alpha" / "docs" / "leak.txt").unlink()
            write(sources / "alpha" / "docs" / "index.html", "<p>conflicting page</p>\n")
            with self.assertRaisesRegex(ValueError, "output path collision"):
                stage_site(root=wiki, build_root=build_root, registry=registry, source_root=sources)
            self.assertEqual((build_root / "series.json").read_text(encoding="utf-8"), staged_registry)

            entries[1]["source"]["directory"] = "../private"
            registry.write_text(json.dumps({"series": entries}, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "inside the checkout"):
                stage_site(root=wiki, build_root=build_root, registry=registry, source_root=sources)
            self.assertEqual((build_root / "series.json").read_text(encoding="utf-8"), staged_registry)

            entries[1]["source"]["directory"] = "docs"
            registry.write_text(json.dumps({"series": entries}, ensure_ascii=False), encoding="utf-8")
            shutil.rmtree(sources / "alpha")
            with self.assertRaisesRegex(ValueError, "Missing local checkout"):
                stage_site(root=wiki, build_root=build_root, registry=registry, source_root=sources)
            self.assertEqual((build_root / "series.json").read_text(encoding="utf-8"), staged_registry)


if __name__ == "__main__":
    unittest.main()
