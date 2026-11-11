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
        "articles.md": "# 精选文章\n",
        "visuals.md": "# 互动图解\n",
    }.items():
        write(root / "website" / name, content)
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
