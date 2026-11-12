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
from prepare import TOPICS, stage_site  # noqa: E402


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_wiki(root):
    for name in TOPICS:
        write(root / name / "wiki" / "README.md", f"# {name}\n")
    write(root / "reviews" / "2026-11-09-topic-review.md", "# Review\n")
    for number in (2, 3):
        write(root / "reviews" / f"round-{number}" / "README.md", f"# Round {number}\n")
    write(root / "img" / "image.svg", "<svg xmlns='http://www.w3.org/2000/svg'/>\n")
    write(root / "electrical-timing-foundations.md", "# Timing\n")
    for name, content in {
        "home.md": "# 首页\n\n<!-- site-series -->\n",
        "series.md": "# 系列\n\n<!-- site-series -->\n",
        "microarchitecture.md": "# 微架构\n",
        "storage.md": "# 存储系统\n",
        "interconnect.md": "# 芯片与系统互连\n",
        "articles.md": "# 精选文章\n",
        "visuals.md": "# 互动图解\n",
    }.items():
        write(root / "website" / name, content)
    write(root / "website/source-layout.json", json.dumps({
        "topics": {name: name for name in TOPICS},
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
            write(development / "FAB/wiki/README.md", "# FAB\n\n[流程](../../process/README.md?x=1#top)\n")
            write(development / "FAB/wiki/img/diagram.svg", "<svg/>\n")
            write(development / "FAB/wiki/AGENTS.md", "# private\n")
            write(development / "FAB/wiki/raw/private.md", "# private\n")
            write(development / "FAB/wiki.old/private.md", "# private\n")
            write(wiki / "reviews/round-2/README.md", "# Review\n\n[FAB](../../series/chip-development/FAB/wiki/README.md#topic)\n")
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
            self.assertIn("[FAB](../../FAB/wiki/README.md#topic)",
                          (docs / "reviews/round-2/README.md").read_text(encoding="utf-8"))
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
            layout["topics"]["RAM"] = "../outside"
            layout_path.write_text(json.dumps(layout), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "inside the checkout"):
                stage_site(root=wiki, build_root=build)
            self.assertEqual((docs / "series/chip-development/README.md").read_text(encoding="utf-8"), staged)

            layout["topics"]["RAM"] = layout["topics"]["BUS"]
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
