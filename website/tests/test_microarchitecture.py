"""Verify the source migration, old public links, and worked teaching models."""

from collections import Counter
from html import unescape
from html.parser import HTMLParser
from itertools import product
import json
from pathlib import Path
import re
import sys
import unittest
from urllib.parse import unquote, urljoin, urlsplit


ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / ".site-build"
SITE = BUILD / "site"
sys.path.insert(0, str(ROOT / "website"))
from microarchitecture_navigation import MICRO_TOPICS, micro_navigation
from ownership import MICRO, owner


class Article(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.inside = False
        self.ids = []
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article":
            self.inside = True
        if self.inside:
            if "id" in attrs:
                self.ids.append(attrs["id"])
            if tag == "a" and "href" in attrs:
                self.links.append(attrs["href"])
            if tag == "img" and "src" in attrs:
                self.links.append(attrs["src"])

    def handle_endtag(self, tag):
        if tag == "article":
            self.inside = False


def html_path(staged):
    path = Path(staged)
    return (path.parent if path.name == "README.md" else path.with_suffix("")) / "index.html"


class MicroarchitecturePublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping = json.loads((BUILD / "microarchitecture-navigation.json").read_text())
        cls.pages = set(cls.mapping.values()) | {"microarchitecture.md"}

    def test_source_topics_coverage_and_unique_navigation(self):
        tree, labels = micro_navigation(BUILD / "docs")
        self.assertEqual([next(iter(group)) for group in tree], list(MICRO_TOPICS.values()))
        assigned = []

        def visit(item):
            if isinstance(item, str):
                assigned.append(item)
            elif isinstance(item, list):
                for child in item:
                    visit(child)
            else:
                for child in item.values():
                    visit(child)

        visit(tree)
        self.assertEqual(set(assigned), set(self.mapping.values()))
        self.assertTrue(all(count == 1 for count in Counter(assigned).values()))
        for source, staged in self.mapping.items():
            self.assertEqual(owner(staged), (MICRO, MICRO_TOPICS[source.split("/")[0]]))
            self.assertIn(staged, labels)

    def test_legacy_pages_anchors_and_canonical_urls(self):
        baseline = json.loads((ROOT / "website/tests/data/microarchitecture-legacy-pages.json").read_text())
        self.assertEqual(len(baseline), 173)
        for staged, record in baseline.items():
            with self.subTest(page=staged):
                text = (SITE / record["html"]).read_text()
                self.assertTrue(set(record["ids"]).issubset(Article(text).ids))
                expected = "https://microarch-flow.github.io/wiki/" + record["html"].removesuffix("index.html")
                self.assertIn(f'<link rel="canonical" href="{expected}">', text)

    def test_first_reads_link_to_the_published_articles_in_order(self):
        home = (SITE / "microarchitecture/index.html").read_text()
        content = home.split('id="series-home-content"', 1)[1]
        reading = re.search(r'<h2 id="first-reads">.*?</h2>\s*<ol>(.*?)</ol>', content, re.DOTALL)
        self.assertIsNotNone(reading)
        questions = [
            ["00-overview/microarchitecture-decisions.md"],
            ["02-pipeline/pipeline-register-insertion.md"],
            ["03-instruction-execution/dependencies-bypass-issue.md"],
            ["04-parallel-execution/simd-vector-simt.md", "04-parallel-execution/why-systolic-array.md"],
            ["06-task-control/dma-compute-writeback.md"],
            ["07-chip-organization/cpu-vs-gpu-core-area.md"],
        ]
        items = re.findall(r'<li>(.*?)</li>', reading.group(1), re.DOTALL)
        self.assertEqual(len(items), len(questions))
        for item, sources in zip(items, questions):
            links = re.findall(r'<a href="([^"]+)">', item)
            paths = [urlsplit(urljoin("/microarchitecture/", href)).path.strip("/") for href in links]
            self.assertEqual(paths, [html_path(self.mapping[source]).parent.as_posix() for source in sources])

        sequence = [html_path(self.mapping[source]) for question in questions for source in question]
        for current, following in zip(sequence, sequence[1:]):
            body = Article((SITE / current).read_text())
            base = "/" + current.parent.as_posix() + "/"
            targets = {urlsplit(urljoin(base, href)).path.rstrip("/") for href in body.links}
            self.assertIn("/" + following.parent.as_posix(), targets, current)

    def test_dma_reading_path_returns_to_the_two_tile_example(self):
        sources = [
            "05-dma/02-fundamentals/address-descriptor-burst.md",
            "05-dma/03-dma-microarchitecture/multidimensional-stride-dma.md",
            "05-dma/03-dma-microarchitecture/scheduling-outstanding.md",
            "05-dma/04-programming-model/queues-doorbells-completions.md",
        ]
        entry = html_path(self.mapping["05-dma/README.md"])
        text = (SITE / entry).read_text()
        reading = re.search(r'<h3 id="dma-first-reads">.*?</h3>\s*<ol>(.*?)</ol>', text, re.DOTALL)
        self.assertIsNotNone(reading)
        entry_url = "/" + entry.parent.as_posix() + "/"
        hrefs = re.findall(r'<li><a href="([^"]+)">', reading.group(1))
        sequence = [html_path(self.mapping[source]) for source in sources]
        self.assertEqual([urljoin(entry_url, href).rstrip("/") for href in hrefs],
                         ["/" + page.parent.as_posix() for page in sequence])

        tiles = html_path(self.mapping["06-task-control/dma-compute-writeback.md"])
        cycle = [tiles, *sequence, tiles]
        for page, following in zip(cycle, cycle[1:]):
            content = Article((SITE / page).read_text())
            base = "/" + page.parent.as_posix() + "/"
            targets = {urlsplit(urljoin(base, href)).path.rstrip("/") for href in content.links}
            self.assertIn("/" + following.parent.as_posix(), targets, page)

    def test_first_read_anchors_added_after_the_legacy_snapshot(self):
        anchors = {
            "00-overview/microarchitecture-decisions.md": {
                "微架构在决定什么软件语义执行资源与实现约束", "先区分三种问题", "同一个点积两种资源日程",
                "一项工作至少经过四种约束", "本系列的阅读主线", "如何验证自己的理解",
            },
            "03-instruction-execution/dependencies-bypass-issue.md": {
                "数据依赖旁路与发射", "先把依赖和冲突分开", "一个明示时序的例子", "旁路需要哪些硬件和判断",
                "就绪不等于获准执行", "延迟启动间隔与依赖距离",
            },
            "04-parallel-execution/simd-vector-simt.md": {
                "simd向量与-simt工作如何分配到执行通道", "三种表达方式", "十个元素如何映射",
                "活动掩码与控制分歧", "物理通道数如何进入吞吐估算", "与矩阵阵列的关系",
            },
            "04-parallel-execution/why-systolic-array.md": {
                "一个-22-矩阵的逐拍例子", "计算结束与结果排空", "插入一拍供数停顿",
                "流量时间和实现成本分别统计", "与-cim-的边界", "资料与模型范围",
            },
            "06-task-control/dma-compute-writeback.md": {
                "dma计算与写回如何协作", "先定义事件与所有权", "两个-tile-的具体日程",
                "同样两个-buffer为何仍可能无法重叠", "完成记录可见性与错误", "从日程走向实现",
            },
            "07-chip-organization/cpu-vs-gpu-core-area.md": {"控制机制与比较层级"},
        }
        for source, expected in anchors.items():
            with self.subTest(article=source):
                article = SITE / html_path(self.mapping[source])
                self.assertLessEqual(expected, set(Article(article.read_text()).ids))

    def test_article_links_and_ids(self):
        parsed = {}
        for staged in self.pages:
            path = html_path(staged)
            body = Article((SITE / path).read_text())
            self.assertFalse([key for key, count in Counter(body.ids).items() if count > 1], staged)
            url = "https://example.test/" + str(path).removesuffix("index.html")
            for link in body.links:
                target = urlsplit(urljoin(url, link))
                if target.netloc != "example.test" or target.scheme not in {"http", "https"}:
                    continue
                target_path = SITE / unquote(target.path).lstrip("/")
                if target.path.endswith("/"):
                    target_path /= "index.html"
                self.assertTrue(target_path.is_file(), (staged, link))
                if target.fragment and target_path.suffix == ".html":
                    if target_path not in parsed:
                        parsed[target_path] = set(re.findall(r'\bid="([^"]+)"', target_path.read_text()))
                    self.assertIn(unquote(target.fragment), parsed[target_path], (staged, link))

    def test_search_and_six_mainline_articles(self):
        index = json.loads((SITE / "search/search_index.json").read_text())["docs"]
        locations = Counter(item["location"] for item in index if "#" not in item["location"])
        mainline = {
            "00-overview/microarchitecture-decisions.md",
            "02-pipeline/stalls-and-backpressure.md",
            "03-instruction-execution/instruction-lifecycle.md",
            "03-instruction-execution/dependencies-bypass-issue.md",
            "04-parallel-execution/simd-vector-simt.md",
            "06-task-control/dma-compute-writeback.md",
        }
        self.assertTrue(mainline.issubset(self.mapping))
        for staged in self.pages:
            location = html_path(staged).as_posix().removesuffix("index.html")
            self.assertEqual(locations[location], 1, staged)
            source = (BUILD / "docs" / staged).read_text()
            heading = re.search(r"^# (.+)$", source, re.MULTILINE).group(1)
            entry = next(item for item in index if item["location"] == location)
            self.assertEqual(unescape(entry["title"]).replace("\u200b", ""), heading, staged)
        self.assertFalse(any("wiki.old" in item["location"] or "archive/microarchitecture" in item["location"] for item in index))


class WorkedModelTests(unittest.TestCase):
    def test_elastic_register_never_loses_or_repeats_items(self):
        # Enumerate all downstream stalls over five edges, then drain. The
        # source obeys the article's stable-until-accepted contract.
        for pattern in product((False, True), repeat=5):
            waiting = iter("ABCDEF")
            offered = next(waiting, None)
            occupied = None
            accepted, output = [], []
            for ready in (*pattern, *([True] * 12)):
                in_ready = occupied is None or ready
                in_fire = offered is not None and in_ready
                out_fire = occupied is not None and ready
                before = occupied
                if out_fire:
                    output.append(occupied)
                if in_fire:
                    occupied = offered
                    accepted.append(offered)
                    offered = next(waiting, None)
                elif out_fire:
                    occupied = None
                if before is not None and not ready:
                    self.assertEqual(occupied, before)
                self.assertEqual(len(accepted) - len(output), int(occupied is not None))
            self.assertEqual(output, list("ABCDEF"))

    def test_systolic_skew_and_global_stall(self):
        a, b = [[1, 2], [3, 4]], [[5, 6], [7, 8]]
        expected = [[19, 22], [43, 50]]
        for pause_at in (None, 2):
            sums = [[0, 0], [0, 0]]
            phase = wall = macs = 0
            snapshots = []
            while phase < 4:
                wall += 1
                if wall - 1 == pause_at:
                    continue
                for i, j in product(range(2), repeat=2):
                    k = phase - i - j
                    if 0 <= k < 2:
                        sums[i][j] += a[i][k] * b[k][j]
                        macs += 1
                snapshots.append([row[:] for row in sums])
                phase += 1
            self.assertEqual(sums, expected)
            self.assertEqual(macs, 8)
            self.assertEqual(snapshots[1], [[19, 6], [15, 0]])
            self.assertEqual(snapshots[2], [[19, 22], [43, 18]])
            self.assertEqual(wall + 4, 8 if pause_at is None else 9)

    def test_three_engine_schedule_and_shared_port_counterexample(self):
        independent = {
            "load": [(0, 2), (2, 4)],
            "compute": [(2, 5), (5, 8)],
            "store": [(5, 7), (8, 10)],
        }
        shared = {
            "load": [(0, 2), (5, 7)],
            "compute": [(2, 5), (7, 10)],
            "store": [(5, 7), (10, 12)],
        }
        for schedule in (independent, shared):
            for k in range(2):
                self.assertLessEqual(schedule["load"][k][1], schedule["compute"][k][0])
                self.assertLessEqual(schedule["compute"][k][1], schedule["store"][k][0])
            for intervals in schedule.values():
                self.assertLessEqual(intervals[0][1], intervals[1][0])
        port = sorted(shared["load"] + shared["compute"])
        self.assertTrue(all(left[1] <= right[0] for left, right in zip(port, port[1:])))
        self.assertEqual(independent["store"][-1][1], 10)
        self.assertEqual(shared["store"][-1][1], 12)


if __name__ == "__main__":
    unittest.main()
