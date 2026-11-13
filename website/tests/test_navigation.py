"""Check navigation and breadcrumbs in the generated static site.

Run after `python website/prepare.py && mkdocs build`.
"""

from html import unescape
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from urllib.parse import unquote, urljoin, urlsplit


SITE = Path(__file__).resolve().parents[2] / ".site-build" / "site"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hooks import grouped_original_topics, make_tree, storage_resources_tree  # noqa: E402
from ownership import STORAGE, owner  # noqa: E402
from storage_navigation import MEMORY_HOME, MEMORY_SECTIONS, RESOURCE_SECTIONS  # noqa: E402

LANDING_PAGES = {
    "index.html", "series/index.html", "microarchitecture/index.html",
    "storage/index.html", "interconnect/index.html", "articles/index.html", "visuals/index.html",
}
ACTIVE_LINK = re.compile(r'<a\s+href="([^"]+)"\s+class="[^"]*\bmd-nav__link--active\b[^"]*"[^>]*>')
BREADCRUMB = re.compile(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', re.DOTALL)


def page_url(relative):
    directory = relative.parent.as_posix()
    return "https://example.test/" + ("" if directory == "." else directory + "/")


class GeneratedNavigationTests(unittest.TestCase):
    def test_series_covers_have_accessible_images_and_working_links(self):
        pages = (
            "storage/index.html", "interconnect/index.html", "external/workload-wiki/index.html",
            "series/inference-runtime/index.html", "series/chip-architectures/index.html",
            "series/chip-development/index.html",
        )
        images = set()
        for relative in pages:
            with self.subTest(page=relative):
                html = (SITE / relative).read_text(encoding="utf-8")
                figure = re.search(r'<figure class="series-cover-art">(.*?)</figure>', html, re.DOTALL)
                self.assertIsNotNone(figure)
                image = re.search(r'<img\s+src="([^"]+)"\s+alt="([^"]+)"', figure.group(1))
                self.assertIsNotNone(image)
                self.assertTrue(image.group(2).strip())
                target = urlsplit(urljoin(page_url(Path(relative)), unescape(image.group(1)))).path.lstrip("/")
                self.assertTrue((SITE / target).is_file(), target)
                images.add(target)
                self.assertIn('href="#series-home-content"', html)
                self.assertIn('id="series-home-content"', html)
        self.assertEqual(len(images), len(pages))

    def test_storage_topics_cover_sources_once_and_expose_hbm(self):
        docs = SITE.parent / "docs"
        topics = grouped_original_topics(docs, STORAGE)
        names = [next(iter(item)) for item in topics]
        self.assertEqual(names, [
            "存储层级与数据路径", "SRAM 器件与应用", "DRAM 器件与接口",
            "DRAM 控制器与请求调度", "HBF 高带宽闪存", "存储系统集成与选型",
        ])

        def paths(node):
            if isinstance(node, str):
                yield node
            elif isinstance(node, dict):
                for child in node.values():
                    yield from paths(child)
            else:
                for child in node:
                    yield from paths(child)

        resources = storage_resources_tree(docs)
        assigned = list(paths([*topics, *resources]))
        expected = {
            path.relative_to(docs).as_posix()
            for directory in ("RAM/wiki", "HBF/wiki", "COMPUTE/wiki/06-memory-discipline")
            for path in (docs / directory).rglob("*.md")
        }
        for name in ("RAM", "HBF"):
            for filename in ("README.md", "self-test-questions.md"):
                path = docs / name / filename
                if path.is_file():
                    expected.add(path.relative_to(docs).as_posix())
        self.assertEqual(len(assigned), len(set(assigned)))
        self.assertEqual(set(assigned), expected)
        memory = topics[0]["存储层级与数据路径"]
        self.assertEqual(memory[0], {"专题首页": MEMORY_HOME})
        self.assertEqual([next(iter(item)) for item in memory[1:]], [name for name, _, _ in MEMORY_SECTIONS])
        for node, (name, _directory, pages) in zip(memory[1:], MEMORY_SECTIONS):
            self.assertEqual(node[name], [{label: path} for label, path in pages])
        self.assertEqual([next(iter(item)) for item in resources[0]["查阅与练习"]],
                         [name for name, _, _ in RESOURCE_SECTIONS])
        self.assertIn("RAM/wiki/07-system-architecture/why-systems-choose-different-memory.md",
                      list(paths(topics[-1])))
        homepage = (SITE / "RAM/wiki/01-overview/index.html").read_text(encoding="utf-8")
        start = homepage.index('<div class="md-sidebar md-sidebar--primary"')
        end = homepage.index('<div class="md-sidebar md-sidebar--secondary"', start)
        self.assertIn('<span class="md-ellipsis">存储层级与数据路径</span>', homepage[start:end])
        search = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))
        locations = {entry["location"] for entry in search["docs"]}
        for page in paths([memory, *resources]):
            path = Path(page)
            location = (path.parent.as_posix() if path.name == "README.md" else path.with_suffix("").as_posix()) + "/"
            self.assertIn(location, locations, page)
        for topic in topics:
            children = next(iter(topic.values()))
            source_labels = {next(iter(item)) for item in children if isinstance(item, dict)}
            self.assertFalse(source_labels & {"RAM · 存储系统", "HBF · 高带宽闪存", "COMPUTE · 计算"})

        dram = topics[2]["DRAM 器件与接口"]
        hbm = "RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io.md"
        self.assertIn(hbm, dram)
        hbm_html = (SITE / "RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io/index.html").read_text(encoding="utf-8")
        article = re.search(r"<article\b.*?</article>", hbm_html, re.DOTALL).group()
        source_url = page_url(Path("RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io/index.html"))
        targets = {urlsplit(urljoin(source_url, unescape(href))).path for href in re.findall(r'<a\s+[^>]*href="([^"]+)"', article)}
        for target in (
            "/RAM/wiki/08-packaging-integration/hbm-2.5d-3d-tsv/",
            "/RAM/wiki/08-packaging-integration/why-hbm-is-expensive/",
            "/RAM/wiki/09-ai-chip-memory-architecture/hbm-vs-lpddr-for-npu/",
        ):
            self.assertIn(target, targets)

    def test_archived_reviews_are_reachable_but_not_in_reader_navigation(self):
        for relative in (Path("index.html"), Path("microarchitecture/index.html"),
                         Path("RAM/wiki/01-overview/index.html")):
            html = (SITE / relative).read_text(encoding="utf-8")
            start = html.index('<div class="md-sidebar md-sidebar--primary"')
            end = html.index('<div class="md-sidebar md-sidebar--secondary"', start)
            self.assertNotIn("reviews/", html[start:end], str(relative))
            self.assertNotIn("评审记录", html[start:end], str(relative))

        archive = SITE / "reviews"
        retained = [
            "2026-11-09-topic-review", "round-2",
            *(f"round-2/{name}" for name in ("BUS", "CIM", "COMPUTE", "CPO", "DMA", "FAB", "NOC", "PCIE", "RAM")),
            "round-3", "round-3/cases",
        ]
        for relative in retained:
            self.assertTrue((archive / relative / "index.html").is_file(), relative)
        self.assertTrue((archive / "round-3/model.py").is_file())
        self.assertTrue((archive / "round-3/expected.json").is_file())
        index = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))
        locations = {entry["location"] for entry in index["docs"]}
        self.assertFalse(any(location.startswith("reviews/") for location in locations))
        self.assertIn("RAM/wiki/01-overview/", locations)
        cases = {
            "reviews/2026-11-09-topic-review/index.html": ["首页", "九专题基线问题与正文证据"],
            "reviews/round-2/index.html": ["首页", "九专题逐篇评审"],
            "reviews/round-2/BUS/index.html": ["首页", "片上总线逐篇评审"],
            "reviews/round-3/cases/index.html": ["首页", "盲测题面（基线 84e459a）"],
        }
        for relative, expected in cases.items():
            with self.subTest(page=relative):
                html = (SITE / relative).read_text(encoding="utf-8")
                breadcrumb = BREADCRUMB.search(html)
                self.assertIsNotNone(breadcrumb)
                labels = [unescape(x) for x in re.findall(r'<(?:a\s[^>]*|span(?:\s[^>]*)?)>(.*?)</(?:a|span)>', breadcrumb.group(1))]
                self.assertEqual(labels, expected)

    def test_chip_examples_have_one_series_and_exclude_source_archives(self):
        directory = SITE / "series/chip-architectures"
        pages = sorted(directory.rglob("index.html"))
        self.assertEqual(len(pages), 7)
        for page in pages:
            if page == directory / "index.html":
                continue
            html = page.read_text(encoding="utf-8")
            breadcrumb = BREADCRUMB.search(html)
            self.assertIsNotNone(breadcrumb, str(page))
            labels = [unescape(x) for x in re.findall(r'<(?:a\s[^>]*|span(?:\s[^>]*)?)>(.*?)</(?:a|span)>', breadcrumb.group(1))]
            self.assertEqual(labels[1], "芯片架构实例", str(page))
        excluded = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
        self.assertFalse([path for path in directory.rglob("*") if path.is_file() and path.suffix.lower() in excluded])

    def test_cross_series_reading_routes(self):
        html = (SITE / "microarchitecture/index.html").read_text(encoding="utf-8")
        routes = {
            "on-chip-data-supply": [
                "DMA/wiki/04-programming-model/tiling-double-buffering/",
                "RAM/wiki/02-sram-foundations/single-port-dual-port-multi-port/",
                "COMPUTE/wiki/03-systolic-array/weight-loading-and-trickle-feed/",
            ],
            "architecture-modeling": [
                "external/workload-wiki/06-chip-workload-analysis/workload-analysis-methodology/",
                "RAM/wiki/06-memory-controller/mc-modeling-for-simulation/",
                "NOC/wiki/08-simulator-construction/verification-and-calibration/",
            ],
        }
        for anchor, targets in routes.items():
            section = re.search(rf'<section\b[^>]*id="{anchor}"[^>]*>(.*?)</section>', html, re.DOTALL)
            self.assertIsNotNone(section, anchor)
            for target in targets:
                self.assertIn(f'href="../{target}"', section.group(1))
                self.assertTrue((SITE / target / "index.html").is_file(), target)

    def test_primary_series_and_topic_for_moved_articles(self):
        cases = {
            "RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io/index.html": ("存储系统", "DRAM 器件与接口"),
            "RAM/wiki/02-sram-foundations/6t-cell-bistable-storage/index.html": ("存储系统", "SRAM 器件与应用"),
            "RAM/wiki/08-packaging-integration/hbm-2.5d-3d-tsv/index.html": ("存储系统", "存储系统集成与选型"),
            "RAM/wiki/08-packaging-integration/why-hbm-is-expensive/index.html": ("存储系统", "存储系统集成与选型"),
            "RAM/wiki/09-ai-chip-memory-architecture/hbm-vs-lpddr-for-npu/index.html": ("存储系统", "存储系统集成与选型"),
            "NOC/wiki/02-router-microarchitecture/credit-based-flow-control/index.html": ("芯片与系统互连", "片上网络（NoC）"),
            "SERDES/wiki/06-link-operation/pcie-training-case/index.html": ("芯片与系统互连", "高速电链路（SerDes）"),
            "DMA/wiki/04-programming-model/tiling-double-buffering/index.html": ("微架构", "DMA 与异步数据搬运"),
            "external/workload-wiki/01-foundation-model-components/contrastive-learning/index.html": ("算法与模型（Workload Wiki）", "表示学习与训练目标"),
            "series/chip-development/02_frontend_design_and_verification/05_dft_introduction/index.html": ("芯片开发与实现", "可测性设计、晶圆筛测与终测"),
            "FAB/wiki/03-wafer-test-and-cp/index.html": ("芯片开发与实现", "可测性设计、晶圆筛测与终测"),
            "series/chip-development/04_tapeout_and_post_silicon/03_packaging/index.html": ("芯片开发与实现", "封装与多芯粒集成"),
            "FAB/wiki/04-back-end-packaging/index.html": ("芯片开发与实现", "封装与多芯粒集成"),
            "FAB/wiki/06-cross-cutting-engineering/yield-economics-across-stages/index.html": ("芯片开发与实现", "可靠性、良率与量产生命周期"),
            "series/inference-runtime/topics/01-prefill-decode/index.html": ("推理运行时", "推理执行阶段与服务指标"),
            "series/inference-runtime/topics/06-paged-kv-cache/index.html": ("推理运行时", "KV 缓存管理与前缀复用"),
            "series/inference-runtime/topics/15-quantitative-estimation/index.html": ("推理运行时", "推理执行阶段与服务指标"),
        }
        for path, (series, topic) in cases.items():
            with self.subTest(path=path):
                html = (SITE / path).read_text(encoding="utf-8")
                breadcrumb = BREADCRUMB.search(html)
                self.assertIsNotNone(breadcrumb)
                labels = [unescape(x) for x in re.findall(r'<(?:a\s[^>]*|span(?:\s[^>]*)?)>(.*?)</(?:a|span)>', breadcrumb.group(1))]
                self.assertEqual(labels[1:3], [series, topic])

    def test_serdes_chapter_order_and_figures(self):
        counts = {
            "01-overview": 4, "02-signal-channel": 6, "03-transmitter": 5,
            "04-receiver": 7, "05-signaling-and-metrics": 5, "06-link-operation": 5,
            "07-design-and-validation": 6, "08-system-applications": 6, "09-modeling": 4,
            "10-reference": 10,
        }
        clean = lambda items: [(unescape(url), unescape(" ".join(label.split()))) for url, label in items]
        for chapter, expected_count in counts.items():
            with self.subTest(chapter=chapter):
                html = (SITE / "SERDES" / "wiki" / chapter / "index.html").read_text(encoding="utf-8")
                start = html.index('<div class="md-sidebar md-sidebar--primary"')
                end = html.index('<div class="md-sidebar md-sidebar--secondary"', start)
                primary = html[start:end]
                active = ACTIVE_LINK.search(primary)
                self.assertIsNotNone(active)
                section = re.search(r'<nav class="md-nav"[^>]*>.*?<ul class="md-nav__list"[^>]*>(.*?)</ul>', primary[active.end():], re.DOTALL)
                self.assertIsNotNone(section)
                nav_items = re.findall(r'<a\s+href="([^"]+)"[^>]*>\s*<span class="md-ellipsis">(.*?)</span>\s*</a>', section.group(1), re.DOTALL)
                reading_section = re.search(r'<h2\b[^>]*>[^<]*阅读顺序.*?</h2>.*?<ol>(.*?)</ol>', html, re.DOTALL)
                self.assertIsNotNone(reading_section)
                reading_items = re.findall(r'<li>\s*<a href="([^"]+)">(.*?)</a>', reading_section.group(1), re.DOTALL)
                self.assertEqual(len(reading_items), expected_count)
                self.assertEqual(clean(nav_items), clean(reading_items))

        landing = (SITE / "microarchitecture" / "index.html").read_text(encoding="utf-8")
        self.assertIn('../SERDES/wiki/', landing)
        for figure in ("link-overview.svg", "differential.svg", "reflection.svg", "tx-timing.svg", "rx-feedback.svg", "nrz-pam4.svg", "eye-metrics.svg", "training-feedback.svg", "event-model.svg"):
            self.assertTrue((SITE / "SERDES" / "wiki" / "img" / figure).is_file())

        figure_pages = {
            "01-overview/link-end-to-end": "link-overview.svg",
            "02-signal-channel/differential-and-return": "differential.svg",
            "02-signal-channel/impedance-and-reflection": "reflection.svg",
            "03-transmitter/parallel-to-serial": "tx-timing.svg",
            "04-receiver/receiver-signal-chain": "rx-feedback.svg",
            "05-signaling-and-metrics/nrz-and-pam4": "nrz-pam4.svg",
            "05-signaling-and-metrics/eye-and-jitter": "eye-metrics.svg",
            "06-link-operation/training-and-adaptation": "training-feedback.svg",
            "09-modeling/worked-model-and-limits": "event-model.svg",
        }
        for article, figure in figure_pages.items():
            with self.subTest(article=article):
                html = (SITE / "SERDES" / "wiki" / article / "index.html").read_text(encoding="utf-8")
                link = re.search(rf'<a\s+href="[^"]*{re.escape(figure)}"[^>]*>(.*?)</a>', html, re.DOTALL)
                self.assertIsNotNone(link)
                self.assertRegex(link.group(1), rf'<img\s+alt="[^"]+"\s+src="[^"]*{re.escape(figure)}"')

        self_check = (SITE / "SERDES/wiki/10-reference/phase2-self-check/index.html").read_text(encoding="utf-8")
        self.assertRegex(self_check, r'<details(?:\s|>)')
        self.assertIn('<summary>查看参考判断</summary>', self_check)
        self_check = (SITE / "SERDES/wiki/10-reference/phase3-self-check/index.html").read_text(encoding="utf-8")
        self.assertRegex(self_check, r'<details(?:\s|>)')
        self.assertIn('<summary>查看参考判断</summary>', self_check)

    def test_ram_chapter_reading_lists_match_navigation(self):
        chapters = sorted((SITE / "RAM/wiki").glob("[0-9][0-9]-*/index.html"))
        self.assertGreater(len(chapters), 0)
        clean = lambda items: [(unescape(url), unescape(" ".join(label.split()))) for url, label in items]
        for chapter in chapters:
            with self.subTest(chapter=chapter.parent.name):
                # These old URLs are now grouped by source topic rather than
                # their former on-disk publication directories.
                if chapter.parent.name in {"01-overview", "07-system-architecture", "09-ai-chip-memory-architecture"}:
                    continue
                html = chapter.read_text(encoding="utf-8")
                start = html.index('<div class="md-sidebar md-sidebar--primary"')
                end = html.index('<div class="md-sidebar md-sidebar--secondary"', start)
                primary = html[start:end]
                active = ACTIVE_LINK.search(primary)
                self.assertIsNotNone(active)
                section = re.search(r'<nav class="md-nav"[^>]*>.*?<ul class="md-nav__list"[^>]*>(.*?)</ul>', primary[active.end():], re.DOTALL)
                self.assertIsNotNone(section)
                nav_items = re.findall(r'<a\s+href="([^"]+)"[^>]*>\s*<span class="md-ellipsis">(.*?)</span>\s*</a>', section.group(1), re.DOTALL)
                reading_section = re.search(r'<h2\b[^>]*>[^<]*(?:阅读顺序|接下来怎么读).*?</h2>.*?<ol>(.*?)</ol>', html, re.DOTALL)
                self.assertIsNotNone(reading_section)
                reading_items = re.findall(r'<li>\s*<a href="([^"]+)">(.*?)</a>', reading_section.group(1), re.DOTALL)
                self.assertGreater(len(reading_items), 0)
                chapter_source = f"RAM/wiki/{chapter.parent.name}/README.md"
                def shares_section(url):
                    article_source = f"RAM/wiki/{chapter.parent.name}/{url.rstrip('/')}.md"
                    # HBM has a direct entry under DRAM, outside this chapter.
                    return url != "hbm-stacked-wide-io/" and owner(article_source) == owner(chapter_source)
                expected = [(url, label) for url, label in clean(reading_items) if shares_section(url)]
                self.assertEqual(clean(nav_items), expected)
                for url, _ in clean(reading_items):
                    if not shares_section(url):
                        self.assertTrue((chapter.parent / url / "index.html").is_file())

        overview = (SITE / "RAM/wiki/01-overview/index.html").read_text(encoding="utf-8")
        self.assertIn('data-ram-overview', overview)
        self.assertIn('ram-overview-diagram-mobile', overview)
        self.assertIn('id="6-用同一边界比较延迟和带宽"', overview)
        self.assertIn('id="7-对建模有什么启示"', overview)
        self.assertIn('A[1]', overview)

    def test_ram_sidebar_short_names_keep_full_article_titles(self):
        relative = Path("RAM/wiki/01-overview/problem-statement/index.html")
        html = (SITE / relative).read_text(encoding="utf-8")
        self.assertIn('title="为什么存储系统难设计？从一次读取看跨层约束"', html)
        self.assertIn('<span class="md-ellipsis">存储系统为何难设计</span>', html)
        self.assertIn('<h1 id="为什么存储系统难设计从一次读取看跨层约束">为什么存储系统难设计？从一次读取看跨层约束', html)

        start = html.index('<div class="md-sidebar md-sidebar--primary"')
        end = html.index('<div class="md-sidebar md-sidebar--secondary"', start)
        nav = re.findall(r'<a\s+href="([^"]+)"[^>]*>\s*<span class="md-ellipsis">(.*?)</span>\s*</a>', html[start:end], re.DOTALL)
        names = {urljoin(page_url(relative), unescape(href)): unescape(" ".join(label.split())) for href, label in nav}
        section = re.search(r'<h2 id="接下来怎么读".*?</h2>\s*<ul>(.*?)</ul>', html, re.DOTALL)
        self.assertIsNotNone(section)
        links = re.findall(r'<li>\s*<a href="([^"]+)">(.*?)</a>', section.group(1), re.DOTALL)
        self.assertGreater(len(links), 0)
        for href, label in links:
            self.assertEqual(names.get(urljoin(page_url(relative), unescape(href))), unescape(label))

    def test_numbered_reading_order_ignores_non_sibling_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chapter = root / "chapter"
            chapter.mkdir()
            for name in ("a.md", "b.md", "c.md"):
                (chapter / name).write_text("# Article\n", encoding="utf-8")
            (root / "outside.md").write_text("# Outside\n", encoding="utf-8")
            (chapter / "README.md").write_text(
                "# Chapter\n\n```md\n## 阅读顺序\n1. [ignored](./c.md)\n```\n\n"
                "## 阅读顺序\n\n1. [B](./b.md)\n2. [Outside](../outside.md)\n"
                "3. [A](./a.md)\n4. [B again](./b.md)\n5. [Missing](./missing.md)\n",
                encoding="utf-8",
            )
            self.assertEqual(
                make_tree(chapter, root),
                ["chapter/README.md", "chapter/b.md", "chapter/a.md", "chapter/c.md"],
            )

    def test_article_paths_and_distinct_parent_links(self):
        cases = {
            "RAM/wiki/01-overview/problem-statement/index.html": [
                "首页", "存储系统", "存储层级与数据路径", "系统基础",
                "为什么存储系统难设计？从一次读取看跨层约束",
            ],
            "RAM/wiki/02-sram-foundations/6t-cell-bistable-storage/index.html": [
                "首页", "存储系统", "SRAM 器件与应用", "SRAM 基础",
                "6T SRAM cell：它如何保存、读取和写入 1 bit",
            ],
            "CPO/wiki/08-research/detailed-cards/cpo-status-challenges-solutions/index.html": [
                "首页", "芯片与系统互连", "共封装光学（CPO）", "CPO · 光互连", "08 研究模板与术语",
                "完整论文卡", "完整卡：CPO status, challenges, and solutions",
            ],
            "electrical-timing-foundations/index.html": [
                "首页", "微架构", "时钟、流水线与吞吐", "从电荷到芯片时序：一条可手算的路径",
            ],
            "SERDES/wiki/05-signaling-and-metrics/ber-confidence-and-fec/index.html": [
                "首页", "芯片与系统互连", "高速电链路（SerDes）", "SerDes · 高速串行链路", "05 信号与指标：怎样读懂链路数据？",
                "BER、置信度与 FEC 怎样关联？",
            ],
            "SERDES/wiki/06-link-operation/pcie-training-case/index.html": [
                "首页", "芯片与系统互连", "高速电链路（SerDes）", "SerDes · 高速串行链路", "06 初始化与链路训练：链路怎样建立和维持？",
                "PCIe 链路训练案例：从现象到证据",
            ],
        }
        for filename, expected in cases.items():
            html = (SITE / filename).read_text(encoding="utf-8")
            breadcrumb = BREADCRUMB.search(html)
            self.assertIsNotNone(breadcrumb, filename)
            labels = re.findall(r'<(?:a\s[^>]*|span(?:\s[^>]*)?)>(.*?)</(?:a|span)>', breadcrumb.group(1))
            self.assertEqual([unescape(label) for label in labels], expected, filename)

        ram = (SITE / "RAM/wiki/02-sram-foundations/index.html").read_text(encoding="utf-8")
        fab = (SITE / "FAB/wiki/07-industry-map/index.html").read_text(encoding="utf-8")
        self.assertIn("<p>上级：", ram)
        self.assertIn("<p>上级:", fab)

    def test_current_navigation_and_breadcrumb_links(self):
        self.assertTrue(SITE.is_dir(), "Build the site before running this test")
        pages = sorted(p for p in SITE.rglob("*.html") if p.name != "404.html")
        self.assertGreater(len(pages), 1)
        errors = []
        for path in pages:
            relative = path.relative_to(SITE)
            html = path.read_text(encoding="utf-8")
            start = html.find('<div class="md-sidebar md-sidebar--primary"')
            end = html.find('<div class="md-sidebar md-sidebar--secondary"', start)
            primary = html[start:end] if start >= 0 and end >= 0 else ""
            active = list(ACTIVE_LINK.finditer(primary))
            if relative.parts[0] != "reviews":
                if len(active) != 1 or 'aria-current="page"' not in active[0].group():
                    errors.append(f"{relative}: expected one accessible current navigation link")
                    continue
                current = urlsplit(urljoin(page_url(relative), unescape(active[0].group(1)))).path
                if current.rstrip("/") != urlsplit(page_url(relative)).path.rstrip("/"):
                    errors.append(f"{relative}: current navigation link points to {current}")

            breadcrumbs = BREADCRUMB.findall(html)
            if relative.as_posix() in LANDING_PAGES:
                continue
            if len(breadcrumbs) != 1 or breadcrumbs[0].count('aria-current="page"') != 1:
                errors.append(f"{relative}: expected one breadcrumb with a current page")
                continue
            for href in re.findall(r'<a href="([^"]+)">', breadcrumbs[0]):
                target = urlsplit(urljoin(page_url(relative), unescape(href)))
                destination = SITE / unquote(target.path).lstrip("/")
                if destination.is_dir():
                    destination /= "index.html"
                if target.netloc != "example.test" or not destination.is_file():
                    errors.append(f"{relative}: broken breadcrumb link {href}")

        self.assertFalse(errors, "\n".join(errors[:30]))


if __name__ == "__main__":
    unittest.main()
