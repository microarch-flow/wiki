"""Verify the new software guides coexist with the published runtime series."""

from collections import Counter
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "series/compiler-runtime"
DOCS = ROOT / ".site-build/docs"
SITE = ROOT / ".site-build/site"
PREFIX = "series/compiler-runtime/"
ROUTES = (
    "01-foundations", "02-frontend-and-optimization", "03-mapping-and-planning",
    "04-code-generation", "05-device-driver", "06-execution-runtime",
    "07-model-execution", "08-request-scheduling", "09-distributed-execution",
    "10-serving", "11-performance",
)


class GuideContent(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.in_article = False
        self.links = []
        self.images = []
        self.ids = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "article":
            self.in_article = True
        elif self.in_article and tag == "a":
            self.links.append(attrs.get("href", ""))
        elif self.in_article and tag == "img":
            self.images.append((attrs.get("src", ""), attrs.get("alt", "")))

    def handle_endtag(self, tag):
        if tag == "article":
            self.in_article = False


class CompilerRuntimeGuideTests(unittest.TestCase):
    def test_article_baseline_matches_guides_and_legacy_inventory(self):
        plan = (ROOT / "docs/compiler-runtime-plan.md").read_text()
        planned = {}
        for match in re.finditer(
                r"^\| ([A-K]\d\d) \| ([^|]+?) \| [^|]+? \| [^|]+? \| `([^`]+)` \| ([^|]+?) \|$", plan, re.M):
            id_, title, filename, status = match.groups()
            self.assertNotIn(id_, planned)
            planned[id_] = (title, filename, status)
        actual = {}
        for prefix, route in zip("ABCDEFGHIJK", ROUTES):
            guide = (SOURCE / route / "README.md").read_text()
            for match in re.finditer(r"^\| ([A-K]\d\d) \| ([^|]+?) \| [^|]+? \| [^|]+? \| ([^|]+?) \|$", guide, re.M):
                id_, title, status = match.groups()
                self.assertTrue(id_.startswith(prefix))
                self.assertNotIn(id_, actual)
                link = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", title)
                if status == "未发布":
                    self.assertIsNone(link, id_)
                else:
                    self.assertIsNotNone(link, id_)
                    self.assertTrue((SOURCE / route / link.group(2)).is_file(), id_)
                actual[id_] = link.group(1) if link else title
        self.assertEqual({id_: title for id_, (title, _, _) in planned.items()}, actual)
        self.assertEqual(len(planned), 59)
        self.assertEqual(sum("深化" in status for _, _, status in planned.values()), 6)
        legacy = ROOT / "series/inference-runtime"
        existing = {path.relative_to(legacy).as_posix() for path in legacy.rglob("*.md")
                    if path.name not in {"README.md", "_conventions.md", "glossary.md"}}
        mapped = set(re.findall(r"^\| \[[^\]]+\]\(\.\./series/inference-runtime/([^)]*)\) \|", plan, re.M))
        self.assertEqual(existing, mapped)
        self.assertEqual(len(mapped), 29)

    def test_existing_series_stays_the_primary_entry(self):
        entries = json.loads((ROOT / "website/series.json").read_text())["series"]
        self.assertEqual(len(entries), 8)
        self.assertEqual([entry["local"]["publish"] for entry in entries
                          if entry.get("local", {}).get("publish") == "series/inference-runtime"],
                         ["series/inference-runtime"])
        self.assertNotIn(PREFIX.rstrip("/"), [entry.get("local", {}).get("publish") for entry in entries])

        legacy = SITE / "series/inference-runtime/index.html"
        self.assertTrue(legacy.is_file())
        page = legacy.read_text()
        self.assertIn("新版建设中", page)
        links = GuideContent(page).links
        self.assertIn("../compiler-runtime/", links)
        self.assertTrue((SITE / PREFIX / "index.html").is_file())

    def test_staged_guides_are_searchable_with_valid_links(self):
        locations = Counter(entry["location"] for entry in json.loads(
            (SITE / "search/search_index.json").read_text())["docs"] if "#" not in entry["location"])
        for route in ("", *ROUTES):
            relative = PREFIX + (route + "/" if route else "")
            with self.subTest(route=route):
                self.assertTrue((SOURCE / route / "README.md").is_file())
                self.assertTrue((DOCS / relative / "README.md").is_file())
                page = (SITE / relative / "index.html").read_text()
                self.assertEqual(locations[relative], 1)
                breadcrumbs = re.search(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', page, re.S)
                self.assertIsNotNone(breadcrumbs)
                self.assertIn("编译器与运行时系统", breadcrumbs.group(1))
                body = GuideContent(page)
                self.assertTrue(any("knowledge-map.svg" in src and alt for src, alt in body.images))
                for link in [*body.links, *(src for src, _ in body.images)]:
                    target = urlsplit(urljoin("https://site.invalid/" + relative, link))
                    if target.netloc != "site.invalid":
                        continue
                    path = SITE / unquote(target.path).lstrip("/")
                    if path.is_dir():
                        path /= "index.html"
                    self.assertTrue(path.is_file(), (relative, link))

    def test_b01_article_navigation_search_and_diagrams(self):
        self._check_article(
            "02-frontend-and-optimization",
            "编译前端与程序优化",
            "b01-compiler-frontend",
            "一段源代码怎样变成编译器能够处理的表示？",
            ("b01-expression-trees.svg",),
        )

    def test_b02_article_navigation_search_and_diagrams(self):
        route = "02-frontend-and-optimization"
        slug = "b02-control-flow-and-ssa"
        self._check_article(
            route,
            "编译前端与程序优化",
            slug,
            "遇到分支和循环，编译器怎样表示不同执行路径上的值？",
            ("b02-branch-cfg.svg", "b02-loop-values.svg"),
        )
        previous = SITE / PREFIX / route / "b01-compiler-frontend/index.html"
        previous_body = GuideContent(previous.read_text())
        self.assertIn(f"../{slug}/", previous_body.links)

    def test_b03_article_navigation_search_and_diagrams(self):
        route = "02-frontend-and-optimization"
        slug = "b03-graph-capture"
        self._check_article(
            route,
            "编译前端与程序优化",
            slug,
            "AI 框架运行过一次模型，为什么编译器仍可能不知道完整的计算过程？",
            ("b03-operator-graph.svg", "b03-branch-capture.svg"),
        )
        previous = SITE / PREFIX / route / "b02-control-flow-and-ssa/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_b04_article_navigation_search_and_diagrams(self):
        route = "02-frontend-and-optimization"
        slug = "b04-dependency-and-alias-analysis"
        self._check_article(
            route,
            "编译前端与程序优化",
            slug,
            "两项运算究竟能不能交换执行顺序？",
            ("b04-alias-ranges.svg", "b04-loop-dependence.svg"),
        )
        previous = SITE / PREFIX / route / "b03-graph-capture/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_b05_article_navigation_search_and_diagrams(self):
        route = "02-frontend-and-optimization"
        slug = "b05-dataflow-analysis-and-optimization"
        self._check_article(
            route,
            "编译前端与程序优化",
            slug,
            "程序中哪些计算可以提前完成、复用或直接删除？",
            ("b05-constants-at-join.svg", "b05-live-values.svg"),
        )
        previous = SITE / PREFIX / route / "b04-dependency-and-alias-analysis/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_b06_article_navigation_search_and_diagrams(self):
        route = "02-frontend-and-optimization"
        slug = "b06-legal-transformation"
        self._check_article(
            route,
            "编译前端与程序优化",
            slug,
            "看起来等价的两种计算，编译器为什么不能任意替换？",
            ("b06-fusion-uses.svg", "b06-float-rounding.svg"),
        )
        previous = SITE / PREFIX / route / "b05-dataflow-analysis-and-optimization/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_f01_article_navigation_search_and_diagrams(self):
        self._check_article(
            "06-execution-runtime",
            "通用执行运行时",
            "f01-module-loading-and-dispatch",
            "设备已经准备好了，运行时怎样启动第一次计算？",
            ("f01-module-and-context.svg", "f01-dispatch-and-buffers.svg"),
        )

    def test_f02_article_navigation_search_and_diagrams(self):
        route = "06-execution-runtime"
        slug = "f02-asynchronous-execution"
        self._check_article(
            route,
            "通用执行运行时",
            slug,
            "提交任务的函数已经返回，为什么不能马上读取计算结果？",
            ("f02-sequential-vs-async.svg", "f02-stream-dependencies.svg"),
        )
        previous = SITE / PREFIX / route / "f01-module-loading-and-dispatch/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_f03_article_navigation_search_and_diagrams(self):
        route = "06-execution-runtime"
        slug = "f03-runtime-buffer-management"
        self._check_article(
            route,
            "通用执行运行时",
            slug,
            "两项任务需要使用同一块 Buffer，什么时候才能安全复用？",
            ("f03-output-buffer-reuse.svg", "f03-pool-lifecycle.svg", "f03-pool-fragmentation.svg"),
        )
        previous = SITE / PREFIX / route / "f02-asynchronous-execution/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_f04_article_navigation_search_and_diagrams(self):
        route = "06-execution-runtime"
        slug = "f04-execution-graphs-and-replay"
        self._check_article(
            route,
            "通用执行运行时",
            slug,
            "多次执行相同的任务序列，怎样减少每轮提交开销？",
            ("f04-task-graph.svg", "f04-submit-overhead.svg"),
        )
        previous = SITE / PREFIX / route / "f03-runtime-buffer-management/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_f05_article_navigation_search_and_diagrams(self):
        route = "06-execution-runtime"
        slug = "f05-dynamic-shapes-and-specialization"
        self._check_article(
            route,
            "通用执行运行时",
            slug,
            "实际输入形状发生变化，运行时怎样找到可以执行的程序？",
            ("f05-shape-resource-mismatch.svg", "f05-shape-buckets.svg", "f05-variant-selection.svg"),
        )
        previous = SITE / PREFIX / route / "f04-execution-graphs-and-replay/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)
        guide = GuideContent((SITE / PREFIX / route / "index.html").read_text())
        self.assertEqual(sum(any(f"f0{i}-" in link for i in range(1, 6)) for link in guide.links), 5)

    def test_a01_article_navigation_search_and_diagrams(self):
        self._check_foundation_article(
            "a01-program-semantics",
            "同一段计算，软件究竟要求计算机做什么？",
            ("a01-values-and-state.svg", "a01-observable-behavior.svg"),
        )

    def test_a02_article_navigation_search_and_diagrams(self):
        self._check_foundation_article(
            "a02-program-representation",
            "程序中的计算、分支和先后关系怎样被明确表达？",
            ("a02-value-flow.svg", "a02-branch-flow.svg"),
        )

    def test_a03_article_navigation_search_and_diagrams(self):
        self._check_foundation_article(
            "a03-tensor-representation",
            "同一个张量，为什么可以在内存中有不同的排列？",
            ("a03-layout-comparison.svg", "a03-transpose-view.svg"),
        )

    def test_a04_article_navigation_search_and_diagrams(self):
        self._check_foundation_article(
            "a04-execution-contract",
            "软件怎样把一项计算交给硬件？",
            ("a04-execution-layers.svg", "a04-device-task.svg"),
        )

    def test_a05_article_navigation_search_and_diagrams(self):
        self._check_foundation_article(
            "a05-task-and-resource-lifecycle",
            "一项任务被提交之后，什么时候结果才可以使用？",
            ("a05-task-dependencies.svg", "a05-buffer-lifecycle.svg"),
        )

    def test_c01_article_navigation_search_and_diagrams(self):
        self._check_article(
            "03-mapping-and-planning",
            "资源映射与执行规划",
            "c01-tensor-mapping",
            "一块矩阵怎样分给有限数量的计算单元？",
            ("c01-output-mapping.svg",),
        )

    def test_c02_article_navigation_search_and_diagrams(self):
        route = "03-mapping-and-planning"
        slug = "c02-layout-and-dataflow-planning"
        self._check_article(
            route,
            "资源映射与执行规划",
            slug,
            "同一组数据怎样安排布局和驻留，才能减少搬运？",
            ("c02-reuse-paths.svg", "c02-weight-layout.svg"),
        )
        previous = SITE / PREFIX / route / "c01-tensor-mapping/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_c03_article_navigation_search_and_diagrams(self):
        route = "03-mapping-and-planning"
        slug = "c03-static-execution-planning"
        self._check_article(
            route,
            "资源映射与执行规划",
            slug,
            "计算与数据搬运怎样安排在同一张时间表上？",
            ("c03-column-dependencies.svg", "c03-schedules.svg"),
        )
        previous = SITE / PREFIX / route / "c02-layout-and-dataflow-planning/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_c04_article_navigation_search_and_diagrams(self):
        route = "03-mapping-and-planning"
        slug = "c04-static-buffer-allocation"
        self._check_article(
            route,
            "资源映射与执行规划",
            slug,
            "已经使用过的缓冲空间，什么时候可以交给下一项任务？",
            ("c04-buffer-lifetimes.svg", "c04-buffer-placement.svg"),
        )
        previous = SITE / PREFIX / route / "c03-static-execution-planning/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_c05_article_navigation_search_and_diagrams(self):
        route = "03-mapping-and-planning"
        slug = "c05-cost-model-and-search"
        self._check_article(
            route,
            "资源映射与执行规划",
            slug,
            "许多方案都能正确执行，怎样找到更好的一个？",
            ("c05-pareto.svg", "c05-search-loop.svg"),
        )
        previous = SITE / PREFIX / route / "c04-static-buffer-allocation/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_d01_article_navigation_search_and_diagrams(self):
        self._check_article(
            "04-code-generation",
            "算子实现与代码生成",
            "d01-lowering-and-bufferization",
            "一句张量计算，怎样逐步变成循环和内存操作？",
            ("d01-lowering-stages.svg", "d01-buffer-reuse.svg"),
        )

    def test_e01_article_navigation_search_and_diagrams(self):
        self._check_article(
            "05-device-driver",
            "设备驱动与底层资源管理",
            "e01-device-context-and-driver",
            "应用程序怎样找到并获得计算设备的使用权？",
            ("e01-control-path.svg", "e01-device-contexts.svg"),
        )

    def test_e02_article_navigation_search_and_diagrams(self):
        route = "05-device-driver"
        slug = "e02-device-memory-mapping"
        self._check_article(
            route,
            "设备驱动与底层资源管理",
            slug,
            "计算设备怎样访问一块由软件分配的内存？",
            ("e02-address-views.svg", "e02-buffer-preparation.svg", "e02-mapping-lifecycle.svg"),
        )
        previous = SITE / PREFIX / route / "e01-device-context-and-driver/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_e03_article_navigation_search_and_diagrams(self):
        route = "05-device-driver"
        slug = "e03-command-submission"
        self._check_article(
            route,
            "设备驱动与底层资源管理",
            slug,
            "驱动怎样告诉设备有一项工作需要执行？",
            ("e03-command-descriptors.svg", "e03-ring-queue.svg", "e03-submit-path.svg"),
        )
        previous = SITE / PREFIX / route / "e02-device-memory-mapping/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_e04_article_navigation_search_and_diagrams(self):
        route = "05-device-driver"
        slug = "e04-completion-and-error-handling"
        self._check_article(
            route,
            "设备驱动与底层资源管理",
            slug,
            "设备完成任务或发生错误后，驱动怎样归还资源？",
            ("e04-completion-queue.svg", "e04-completion-path.svg",
             "e04-resource-release.svg", "e04-error-recovery.svg"),
        )
        previous = SITE / PREFIX / route / "e03-command-submission/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_d02_article_navigation_search_and_diagrams(self):
        route = "04-code-generation"
        slug = "d02-instruction-selection"
        self._check_article(
            route,
            "算子实现与代码生成",
            slug,
            "一个 IR 操作怎样变成目标机器的指令？",
            ("d02-ir-to-machine.svg", "d02-wide-add.svg"),
        )
        previous = SITE / PREFIX / route / "d01-lowering-and-bufferization/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_d03_article_navigation_search_and_diagrams(self):
        route = "04-code-generation"
        slug = "d03-register-allocation-and-scheduling"
        self._check_article(
            route,
            "算子实现与代码生成",
            slug,
            "临时值比硬件寄存器多，编译器怎样处理？",
            ("d03-live-intervals.svg", "d03-spill-reload.svg", "d03-schedule-pressure.svg"),
        )
        previous = SITE / PREFIX / route / "d02-instruction-selection/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_d04_article_navigation_search_and_diagrams(self):
        route = "04-code-generation"
        slug = "d04-executable-artifacts"
        self._check_article(
            route,
            "算子实现与代码生成",
            slug,
            "生成的代码怎样成为可加载、可调用的程序？",
            ("d04-relocation.svg", "d04-object-to-load.svg", "d04-kernel-artifact.svg"),
        )
        previous = SITE / PREFIX / route / "d03-register-allocation-and-scheduling/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_d05_article_navigation_search_and_diagrams(self):
        route = "04-code-generation"
        slug = "d05-matrix-multiplication-kernels"
        self._check_article(
            route,
            "算子实现与代码生成",
            slug,
            "分块方案确定后，怎样生成可执行的矩阵乘法内核？",
            ("d05-plan-to-kernels.svg", "d05-accumulator-states.svg",
             "d05-npu-commands.svg"),
        )
        for previous in ("d01-lowering-and-bufferization", "d04-executable-artifacts"):
            page = SITE / PREFIX / route / previous / "index.html"
            self.assertIn(f"../{slug}/", GuideContent(page.read_text()).links)

    def test_g01_article_navigation_search_and_diagrams(self):
        self._check_article(
            "07-model-execution",
            "模型执行与生成控制",
            "g01-model-loading-and-execution",
            "模型文件怎样变成可以反复执行的模型实例？",
            ("g01-model-instance.svg", "g01-request-ownership.svg"),
        )

    def test_g02_article_navigation_search_and_diagrams(self):
        route = "07-model-execution"
        slug = "g02-prefill-and-decode"
        self._check_article(
            route,
            "模型执行与生成控制",
            slug,
            "生成一个 Token 之前，模型到底执行了哪些工作？",
            ("g02-prefill.svg", "g02-generation-progress.svg", "g02-stage-work.svg"),
        )
        previous = SITE / PREFIX / route / "g01-model-loading-and-execution/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_d06_article_navigation_search_and_diagrams(self):
        route = "04-code-generation"
        slug = "d06-fused-kernels"
        self._check_article(
            route,
            "算子实现与代码生成",
            slug,
            "两个算子已经决定融合，怎样真正减少中间数据搬运？",
            ("d06-epilogue-dataflow.svg", "d06-row-reduction.svg"),
        )
        previous = SITE / PREFIX / route / "d05-matrix-multiplication-kernels/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_g03_article_navigation_search_and_diagrams(self):
        route = "07-model-execution"
        slug = "g03-sampling-and-generation"
        self._check_article(
            route,
            "模型执行与生成控制",
            slug,
            "模型给出一组 Logits，怎样决定下一个 Token？",
            ("g03-logits-to-token.svg", "g03-generation-state.svg", "g03-stop-buffer.svg"),
        )
        previous = SITE / PREFIX / route / "g02-prefill-and-decode/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def test_d07_article_navigation_search_and_diagrams(self):
        route = "04-code-generation"
        slug = "d07-attention-kernels"
        self._check_article(
            route,
            "算子实现与代码生成",
            slug,
            "Attention 为什么可以不将完整的分数矩阵写入显存？",
            ("d07-online-softmax.svg", "d07-causal-mask.svg",
             "d07-paged-kv-read.svg"),
        )
        previous = SITE / PREFIX / route / "d06-fused-kernels/index.html"
        self.assertIn(f"../{slug}/", GuideContent(previous.read_text()).links)

    def _check_foundation_article(self, slug, title, diagram_names):
        self._check_article("01-foundations", "软件执行共同基础", slug, title, diagram_names)

    def _check_article(self, route, route_title, slug, title, diagram_names):
        relative = f"{PREFIX}{route}/{slug}/"
        url = "https://site.invalid/" + relative
        source = SOURCE / route / f"{slug}.md"
        staged = DOCS / PREFIX / route / source.name
        self.assertRegex(source.read_text(), rf"(?m)^# {re.escape(title)}$")
        self.assertTrue(staged.is_file())

        page = (SITE / relative / "index.html").read_text()
        body = re.search(r"<article\b[^>]*>(.*?)</article>", page, re.S)[1]
        headings = re.findall(r"<h1\b[^>]*>(.*?)</h1>", body, re.S)
        self.assertEqual(len(headings), 1)
        heading = re.sub(r'<a\b[^>]*class="headerlink"[^>]*>.*?</a>', "", headings[0], flags=re.S)
        self.assertEqual(unescape(re.sub(r"<[^>]+>", "", heading)).strip(), title)
        self.assertIn(f'<link rel="canonical" href="https://microarch-flow.github.io/wiki/{relative}">', page)

        entries = json.loads((SITE / "search/search_index.json").read_text())["docs"]
        indexed = [item for item in entries if unquote(item["location"]) == relative]
        self.assertEqual(len(indexed), 1)
        self.assertEqual(indexed[0]["title"].replace("\u200b", ""), title)

        primary = page.split('<div class="md-sidebar md-sidebar--primary"', 1)[1].split(
            '<div class="md-sidebar md-sidebar--secondary"', 1)[0]
        active = re.findall(r'<a\b[^>]*class="[^"]*\bmd-nav__link--active\b[^"]*"[^>]*>', primary)
        self.assertEqual(len(active), 1)
        self.assertIn('aria-current="page"', active[0])
        href = re.search(r'href="([^"]+)"', active[0])[1]
        self.assertEqual(urljoin(url, unescape(href)), url)

        crumb = re.search(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', page, re.S)[1]
        self.assertIn(f'<span aria-current="page">{title}</span>', crumb)
        crumb_targets = {unescape(label): urljoin(url, unescape(href)) for href, label in
                         re.findall(r'<a href="([^"]+)">([^<]+)</a>', crumb)}
        self.assertEqual(crumb_targets["新版：编译器与运行时系统"], "https://site.invalid/" + PREFIX)
        self.assertEqual(crumb_targets[route_title], "https://site.invalid/" + PREFIX + route + "/")
        guide_url = "https://site.invalid/" + PREFIX + route + "/"
        guide = GuideContent((SITE / PREFIX / route / "index.html").read_text())
        self.assertIn(url, [urljoin(guide_url, link) for link in guide.links])

        content = GuideContent(page)
        for filename in diagram_names:
            original = SOURCE / route / "assets" / filename
            published = SITE / PREFIX / route / "assets" / filename
            self.assertTrue(original.is_file())
            self.assertTrue(published.is_file())
            self.assertEqual(ElementTree.parse(published).getroot().tag, "{http://www.w3.org/2000/svg}svg")
            self.assertTrue(any(src.endswith("/" + filename) and alt for src, alt in content.images), filename)

        for ref in [*content.links, *(src for src, _ in content.images)]:
            target = urlsplit(urljoin(url, ref))
            if target.netloc != "site.invalid":
                continue
            path = SITE / unquote(target.path).lstrip("/")
            if path.is_dir():
                path /= "index.html"
            self.assertTrue(path.is_file(), (relative, ref))
            if target.fragment and path.suffix == ".html":
                self.assertIn(unquote(target.fragment), GuideContent(path.read_text()).ids, (relative, ref))


if __name__ == "__main__":
    unittest.main()
