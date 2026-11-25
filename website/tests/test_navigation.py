"""Check navigation and breadcrumbs in the generated static site.

Run after `python website/prepare.py && mkdocs build`.
"""

from collections import Counter
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
from hooks import (COHERENCE_MSI_REDIRECT, CPO_SECTIONS, ORIGINAL_TOPIC_REDIRECTS,
                   grouped_original_topics, make_tree, storage_resources_tree)  # noqa: E402
from ownership import GROUPS, INTERCONNECT, STORAGE, owner  # noqa: E402
from prepare import (FOUNDATION_COMPANIONS, FOUNDATION_MERGED_ARTICLES, FOUNDATION_SPLIT_ARTICLES,
                     SILICON_TO_LOGIC_LEGACY_SECTIONS)  # noqa: E402
from d2d_navigation import D2D_READ_REDIRECT  # noqa: E402
from storage_navigation import (STORAGE_LEGACY_PAGES, INTEGRATION_AFTER, INTEGRATION_HOME, INTEGRATION_PACKAGING,
                                MEMORY_HOME, MEMORY_SECTIONS, RESOURCE_HOME, RESOURCE_SECTIONS,
                                SYSTEM_SELECTION)  # noqa: E402

SHARED_PATHS_DIAGRAM = Path("NOC/wiki/01-overview/img/shared-paths.html")
UNLISTED_LANDING_PAGES = {"articles/index.html", "visuals/index.html"}
LANDING_PAGES = {
    "index.html", "microarchitecture/index.html",
    "storage/index.html", "interconnect/index.html", *UNLISTED_LANDING_PAGES,
}
ACTIVE_LINK = re.compile(r'<a\s+href="([^"]+)"\s+class="[^"]*\bmd-nav__link--active\b[^"]*"[^>]*>')
BREADCRUMB = re.compile(r'<nav class="site-breadcrumbs"[^>]*>(.*?)</nav>', re.DOTALL)


def page_url(relative):
    directory = relative.parent.as_posix()
    return "https://example.test/" + ("" if directory == "." else directory + "/")


class GeneratedNavigationTests(unittest.TestCase):
    def test_homepage_series_are_grouped_by_reader_question(self):
        home = (SITE / "index.html").read_text(encoding="utf-8")
        body = re.search(r'<article\b[^>]*>(.*?)</article>', home, re.DOTALL).group(1)
        self.assertLess(body.index("第一个字出现之前"), body.index('id="series"'))
        directory = re.search(r'<nav\b[^>]*id="common-foundations"[^>]*>(.*?)</nav>', body, re.DOTALL).group(1)
        self.assertIn('id="common-foundations-heading"', directory)
        expected_groups = [
            ("硬件怎样工作？", [
                ("foundations/", "半导体与电路基础"), ("microarchitecture/", "计算微架构"),
                ("storage/", "存储系统"), ("interconnect/", "芯片与系统互连"),
            ]),
            ("模型怎样计算，一次推理怎样跑起来？", [
                ("external/workload-wiki/", "算法与模型"), ("series/inference-runtime/", "推理运行时"),
            ]),
            ("一颗真实芯片怎样设计、实现和交付？", [
                ("series/chip-architectures/", "芯片架构实例"), ("series/chip-development/", "芯片开发与实现"),
            ]),
        ]
        sections = re.findall(r'<section\b([^>]*)>(.*?)</section>', directory, re.DOTALL)
        self.assertEqual(len(sections), len(expected_groups))
        card_pattern = r'<a class="portal-series-card" href="([^"]+)">\s*<strong>([^<]+)</strong>'
        for (attrs, contents), (question, expected_cards) in zip(sections, expected_groups):
            with self.subTest(question=question):
                heading = re.search(r'<h3\b[^>]*id="([^"]+)"[^>]*>([^<]+)', contents)
                self.assertIsNotNone(heading)
                self.assertEqual(heading.group(2).strip(), question)
                self.assertIn(f'aria-labelledby="{heading.group(1)}"', attrs)
                self.assertEqual(directory.count(f'id="{heading.group(1)}"'), 1)
                self.assertEqual(re.findall(card_pattern, contents), expected_cards)
        cards = [card for _, group in expected_groups for card in group]
        self.assertEqual(re.findall(card_pattern, directory), cards)
        tabs = re.search(r'<nav class="md-tabs"[^>]*>(.*?)</nav>', home, re.DOTALL).group(1)
        tab_links = re.findall(r'<a\s+href="([^"]+)"', tabs)
        card_links = [href for href, _ in cards]
        self.assertEqual([href for href in tab_links if href in card_links], card_links)

    def test_renamed_guides_keep_their_published_anchors(self):
        for guide, anchor in [
            ("foundations", "半导体基础"),
            ("microarchitecture", "微架构执行数据通路与资源协作"),
            ("microarchitecture/00-overview", "微架构系列导读"),
        ]:
            with self.subTest(guide=guide):
                page = (SITE / guide / "index.html").read_text(encoding="utf-8")
                self.assertEqual(page.count(f'id="{anchor}"'), 1)

    def test_semiconductor_series_guide_lists_all_articles(self):
        home = (SITE / "index.html").read_text(encoding="utf-8")
        body = re.search(r'<article\b[^>]*>(.*?)</article>', home, re.DOTALL).group(1)
        guide = (SITE / "foundations/index.html").read_text(encoding="utf-8")
        guide_body = re.search(r'<article\b[^>]*>(.*?)</article>', guide, re.DOTALL).group(1)
        expected = ["electrons-to-diode", "bands-to-channel", "cmos-logic-gates", "latch-and-divider",
                    "transistor-amplifier", "quartz-oscillator", "integer-pll", "fanout-and-wire-delay",
                    "supply-voltage-and-frequency", "pvt-and-path-delay"]
        section = guide_body.split('id="阅读顺序"', 1)[1].split("<h2 ", 1)[0]
        listing = re.search(r"<ol>(.*?)</ol>", section, re.DOTALL).group(1)
        entries = re.findall(r'<li><a href="([^"/]+)/">([^<]+)</a>', listing)
        self.assertEqual([slug for slug, _ in entries], expected)
        self.assertEqual(entries[0][1], "从电子到二极管")
        source = Path(__file__).resolve().parents[2] / "series/semiconductor-foundations"
        redirects = set(FOUNDATION_MERGED_ARTICLES) | set(FOUNDATION_SPLIT_ARTICLES)
        titles = {page.parent.name: page.read_text(encoding="utf-8").splitlines()[0].removeprefix("# ")
                  for page in source.glob("*/README.md") if page.parent.name not in redirects}
        self.assertCountEqual(expected, titles)
        primary = guide.split('<div class="md-sidebar md-sidebar--primary"', 1)[1].split(
            '<div class="md-sidebar md-sidebar--secondary"', 1)[0]
        nav_links = re.findall(r'<a\s+href="([^"/?#]+)/"[^>]*>', primary)
        self.assertEqual([slug for slug in nav_links if slug in titles], expected)
        for old_slug in ("inverter-to-package", "silicon-to-logic", "voltage-to-clock"):
            self.assertNotIn(old_slug, nav_links)
            self.assertNotRegex(guide_body, rf'href="{old_slug}/')
        foundation_nav = primary.split('href="electrons-to-diode/"', 1)[1].split('data-md-level="1"', 1)[0]
        for old_group in ("延伸阅读", "历史导读"):
            self.assertNotRegex(foundation_nav, rf'<span class="md-ellipsis">\s*{old_group}\s*</span>')
        for slug, short in entries:
            with self.subTest(article=slug):
                self.assertNotIn(f'href="foundations/{slug}/"', body)
                article = Path(f"foundations/{slug}/index.html")
                html = (SITE / article).read_text(encoding="utf-8")
                active = re.search(r'<a\s+href="\./"[^>]*class="[^"]*md-nav__link--active[^"]*"([^>]*)>'
                                   r'\s*<span class="md-ellipsis">(.*?)</span>', html, re.DOTALL)
                self.assertIsNotNone(active)
                self.assertEqual(unescape(active.group(2).strip()), unescape(short))
                if unescape(short) != titles[slug]:
                    self.assertIn(f'title="{titles[slug]}"', unescape(active.group(1)))
                breadcrumb = BREADCRUMB.search(html).group(1)
                labels = re.findall(r"<(?:a|span)\b[^>]*>([^<]+)</(?:a|span)>", breadcrumb)
                self.assertEqual(labels, ["首页", "半导体与电路基础", titles[slug]])
                links = {label: unquote(urljoin(page_url(article), href))
                         for href, label in re.findall(r'<a href="([^"]+)">([^<]+)</a>', breadcrumb)}
                self.assertEqual(links["半导体与电路基础"], "https://example.test/foundations/")

    def test_merged_foundations_old_links_and_search(self):
        guide = (SITE / "foundations/index.html").read_text(encoding="utf-8")
        search = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))
        locations = [entry["location"] for entry in search["docs"]]
        cases = (
            ("switching-energy-and-power", "fanout-and-wire-delay", "energy",
             "同样的频率为什么跑不同任务时芯片功耗不同",
             ("一次翻转从电源取多少能量", "将-1000-个节点放在同一个观察窗口", "还有哪些电流流过电源")),
            ("ir-drop-and-decoupling", "supply-voltage-and-frequency", "supply-loop",
             "电源设定为-08-v逻辑门两端实际有多少",
             ("先把电流固定算电阻上的-ir-drop", "一批门同时翻转时电流从哪里来", "为什么平均功耗够低某一拍仍可能出问题")),
        )
        for old_slug, new_slug, default, old_title, old_sections in cases:
            with self.subTest(redirect=old_slug):
                old_url = f"foundations/{old_slug}/"
                new_url = f"foundations/{new_slug}/"
                old = (SITE / old_url / "index.html").read_text(encoding="utf-8")
                new = (SITE / new_url / "index.html").read_text(encoding="utf-8")
                self.assertNotIn(f'href="{old_slug}/"', guide)
                self.assertIn(f'<link rel="canonical" href="../{new_slug}/">', old)
                self.assertIn('name="robots" content="noindex"', old)
                for fragment in (old_title, *old_sections):
                    self.assertEqual(old.count(f'id="{fragment}"'), 1, fragment)
                    self.assertEqual(new.count(f'id="{fragment}"'), 1, fragment)
                for fragment in (default, *old_sections):
                    self.assertIn(f'href="../{new_slug}/#{fragment}"', old)
                if old_slug == "ir-drop-and-decoupling":
                    self.assertIn(f'href="../{new_slug}/#{old_title}"', old)
                self.assertEqual(new.count(f'id="{default}"'), 1)
                self.assertIn(f'location.replace("../{new_slug}/" + location.search + (location.hash || "#{default}"))', old)
                self.assertEqual(locations.count(new_url), 1)
                self.assertFalse(any(url.startswith(old_url) for url in locations))
        loop = Path("ir-drop-and-decoupling/img/local-supply-loop.png")
        self.assertTrue((SITE / "foundations" / loop).is_file())
        article = (SITE / "foundations/supply-voltage-and-frequency/index.html").read_text(encoding="utf-8")
        self.assertIn(f'src="../{loop}"', article)

    def test_supply_and_pvt_article_bookmarks(self):
        bookmarks = {
            "supply-voltage-and-frequency": (
                "为什么降低供电电压能省电却可能需要降频", "levels", "先认清三个电压", "energy", "固定活动量先算节省的能量",
                "drive", "timing", "再看数据能否及时送到下一级", "dvfs", "supply-loop", "decoupling",
            ),
            "pvt-and-path-delay": (
                "同一条逻辑路径为什么会有不同的延迟", "拿同一个反相器逐次改变一个条件", "在两个工作点查同一条路径",
                "数据到得过早同样有风险", "setup", "hold", "corners",
            ),
        }
        for slug, anchors in bookmarks.items():
            html = (SITE / "foundations" / slug / "index.html").read_text(encoding="utf-8")
            article = re.search(r'<article\b[^>]*>(.*?)</article>', html, re.DOTALL).group(1)
            for anchor in anchors:
                with self.subTest(article=slug, anchor=anchor):
                    self.assertEqual(article.count(f'id="{anchor}"'), 1)

    def test_split_foundations_bookmarks_link_to_indexed_sections(self):
        baseline = json.loads((Path(__file__).parent / "fixtures/silicon-to-logic-legacy.json").read_text(encoding="utf-8"))
        index = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))
        locations = Counter(entry["location"] for entry in index["docs"])
        source_anchors = {
            "silicon-to-logic": baseline["fragments"],
            "inverter-to-package": ["电路图上的反相器在真实芯片里长什么样", "在硅片上找回电路图的四根线",
                                    "从一片晶圆追到板上的一颗芯片", "同一个-gpu-封装里哪段横着走哪段竖着走"],
            "voltage-to-clock": ["从电容充电到时钟边沿", "电压升到指定值要多久", "比较器怎样让翻转重复",
                                 "石英晶振怎样定频", "时钟边沿怎样触发采样"],
        }
        defaults = {
            "silicon-to-logic": "foundations/electrons-to-diode/#bjt",
            "inverter-to-package": "foundations/cmos-logic-gates/#physical-inverter",
            "voltage-to-clock": "foundations/fanout-and-wire-delay/#rc-half",
        }
        routes = [(slug, slug, default) for slug, default in defaults.items()]
        routes.extend((f"silicon-to-logic/{child}", "silicon-to-logic", None) for child in baseline["redirects"])
        anchors_by_page = {}
        targets = {}
        for path, guide, default in routes:
            with self.subTest(route=path):
                relative = Path("foundations") / path / "index.html"
                html = (SITE / relative).read_text(encoding="utf-8")

                def resolved(href):
                    url = urlsplit(urljoin(page_url(relative), unescape(href)))
                    self.assertEqual(url.netloc, "example.test")
                    return unquote(url.path.lstrip("/") + "#" + url.fragment)

                self.assertIn('name="robots" content="noindex"', html)
                self.assertFalse(any(location.startswith(relative.parent.as_posix() + "/") for location in locations))
                # All fallbacks must work with JavaScript disabled, including an old section on a nested URL.
                fallback = {}
                for item in re.findall(r"<li\b[^>]*>.*?</li>", html, re.DOTALL):
                    href = re.search(r'<a\b[^>]*href="([^"]+)"', item).group(1)
                    target = resolved(href)
                    for anchor in re.findall(r'\bid="([^"]+)"', item):
                        self.assertNotIn(anchor, fallback)
                        fallback[anchor] = target
                self.assertEqual(set(source_anchors[guide]), set(fallback))
                default_link = re.search(r'<a\b(?=[^>]*id="default-target")[^>]*href="([^"]+)"', html).group(1)
                if default is None:
                    default = targets[guide][baseline["redirects"][path.split("/")[-1]]]
                    self.assertEqual(fallback, targets[guide])
                self.assertEqual(resolved(default_link), default)
                canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html).group(1)
                self.assertEqual(resolved(canonical).split("#")[0], default.split("#")[0])
                targets[path] = fallback
                for target in {default, *fallback.values()}:
                    page, fragment = target.split("#", 1)
                    self.assertEqual(locations[page], 1, target)
                    if fragment:
                        if page not in anchors_by_page:
                            text = (SITE / page / "index.html").read_text(encoding="utf-8")
                            article = re.search(r"<article\b[^>]*>(.*?)</article>", text, re.DOTALL).group(1)
                            anchors_by_page[page] = Counter(re.findall(r'\bid="([^"]+)"', article))
                        self.assertEqual(anchors_by_page[page][fragment], 1, target)
        for section, page in {
            "三极管怎样放大电流并作为开关": "electrons-to-diode/#bjt",
            "用负载检查一次开关状态": "transistor-amplifier/#bjt-load",
            "反接时充稳后只剩少量漏电": "electrons-to-diode/#reverse",
            "用串联和并联推导-nand-与-nor": "cmos-logic-gates/#nand-nor",
        }.items():
            self.assertEqual(targets["silicon-to-logic"][section], "foundations/" + page)
        self.assertEqual(targets["inverter-to-package"]["从一片晶圆追到板上的一颗芯片"],
                         "foundations/supply-voltage-and-frequency/#board-to-die")
        self.assertEqual(targets["inverter-to-package"]["同一个-gpu-封装里哪段横着走哪段竖着走"],
                         "FAB/wiki/04-back-end-packaging/hbm-as-case-study/ai-gpu-hbm-package-architecture/#hbm-section")
        for section, page in {"电压升到指定值要多久": "fanout-and-wire-delay/#rc-half",
                              "比较器怎样让翻转重复": "quartz-oscillator/#rc",
                              "石英晶振怎样定频": "quartz-oscillator/#mode",
                              "时钟边沿怎样触发采样": "latch-and-divider/#edge"}.items():
            self.assertEqual(targets["voltage-to-clock"][section], "foundations/" + page)

    def test_split_foundations_figures_render_in_their_receiving_articles(self):
        figures = {
            "foundations/electrons-to-diode/": "foundations/silicon-to-logic/img/npn-injection.svg",
            "foundations/transistor-amplifier/": "foundations/transistor-amplifier/img/bjt-load-line.svg",
            "foundations/cmos-logic-gates/": "foundations/inverter-to-package/img/planar-inverter.png",
            "foundations/fanout-and-wire-delay/": "img/electrical-timing-rc.svg",
            "FAB/wiki/04-back-end-packaging/hbm-as-case-study/ai-gpu-hbm-package-architecture/":
                "foundations/inverter-to-package/img/gpu-hbm-section.png",
        }
        for page, figure in figures.items():
            with self.subTest(page=page):
                path = Path(page) / "index.html"
                html = (SITE / path).read_text(encoding="utf-8")
                article = re.search(r"<article\b[^>]*>(.*?)</article>", html, re.DOTALL).group(1)
                images = re.findall(r'<img\b[^>]*src="([^"]+)"', article)
                self.assertIn("https://example.test/" + figure, [urljoin(page_url(path), src) for src in images])
                self.assertTrue((SITE / figure).is_file())

    def test_electrons_to_diode_article_search_and_interactive_links(self):
        topic = "foundations/electrons-to-diode/"
        page = (SITE / topic / "index.html").read_text(encoding="utf-8")
        article = re.search(r'<article\b[^>]*>(.*?)</article>', page, re.DOTALL).group(1)
        self.assertEqual(article.count('id="bjt"'), 1)
        self.assertIn('href="../transistor-amplifier/#bjt-load"', article)
        amplifier = (SITE / "foundations/transistor-amplifier/index.html").read_text(encoding="utf-8")
        self.assertEqual(amplifier.count('id="bjt-load"'), 1)
        self.assertIn('href="../electrons-to-diode/#bjt"', amplifier)
        index = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))
        entries = [entry for entry in index["docs"] if entry["location"].startswith(topic)]
        self.assertEqual([entry["location"] for entry in entries if "#" not in entry["location"]], [topic])
        indexed_sections = [entry for entry in entries if entry["location"].startswith(topic + "#")]
        text = " ".join(entry["text"] for entry in indexed_sections).replace("\u200b", "")
        for term in ("能带", "耗尽区"):
            self.assertIn(term, text)

        companion = (SITE / topic / "interactive.html").read_text(encoding="utf-8")
        anchors = set(re.findall(r'\bid="([^"]+)"', companion))
        links = re.findall(r'<a\b[^>]*href="(?:\./)?interactive\.html#([^"]+)"[^>]*>(.*?)</a>', article, re.DOTALL)
        self.assertTrue(links, "The native article should link directly to the interactive illustrations")
        for fragment, label in links:
            with self.subTest(interactive_section=fragment):
                self.assertIn(unquote(unescape(fragment)), anchors)
                name = unescape(re.sub(r"<[^>]*>", "", label)).strip()
                self.assertTrue(name)
                self.assertNotIn(name, ("这里", "点击这里", "interactive.html"))

    def test_foundation_articles_link_to_their_experiments(self):
        panels = (
            ("bands-to-channel", "bands-to-channel/experiments.html", "channel"),
            ("cmos-logic-gates", "bands-to-channel/experiments.html", "gates"),
            ("latch-and-divider", "latch-and-divider/experiment.html", "write"),
            ("latch-and-divider", "latch-and-divider/experiment.html", "edge"),
            ("transistor-amplifier", "transistor-amplifier/experiment.html", "gain"),
            ("transistor-amplifier", "transistor-amplifier/experiment.html", "step"),
            ("quartz-oscillator", "quartz-oscillator/experiment.html", "mode"),
            ("quartz-oscillator", "quartz-oscillator/experiment.html", "startup"),
            ("integer-pll", "integer-pll/experiment.html", "edges"),
            ("integer-pll", "integer-pll/experiment.html", "correction"),
            ("fanout-and-wire-delay", "fanout-and-wire-delay/experiment.html", "load"),
            ("fanout-and-wire-delay", "fanout-and-wire-delay/experiment.html", "wire"),
            ("supply-voltage-and-frequency", "supply-voltage-and-frequency/experiment.html", "edge"),
            ("supply-voltage-and-frequency", "supply-voltage-and-frequency/experiment.html", "clock"),
            ("pvt-and-path-delay", "pvt-and-path-delay/experiment.html", "timing"),
        )
        for slug, filename, fragment in panels:
            with self.subTest(article=slug, panel=fragment):
                page = Path("foundations") / slug / "index.html"
                companion = Path("foundations") / filename
                article = (SITE / page).read_text(encoding="utf-8").split("<article", 1)[1].split("</article>", 1)[0]
                targets = {urljoin(page_url(page), unescape(href)) for href in re.findall(r'href="([^"]+)"', article)}
                self.assertIn(f"https://example.test/{companion}#{fragment}", targets)
                html = (SITE / companion).read_text(encoding="utf-8")
                self.assertEqual(html.count(f'id="{fragment}"'), 1)

    def test_series_redirect_targets_homepage_section(self):
        redirect = (SITE / "series/index.html").read_text(encoding="utf-8")
        self.assertIn('http-equiv="refresh" content="0; url=../#series"', redirect)
        self.assertIn('href="../#series"', redirect)
        self.assertIn('id="series"', (SITE / "index.html").read_text(encoding="utf-8"))
        index = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))
        self.assertFalse(any(entry["location"].startswith("series/#") or entry["location"] == "series/"
                             for entry in index["docs"]))

    def test_interconnect_topics_navigation_search_and_cpo_coverage(self):
        docs = SITE.parent / "docs"
        groups = grouped_original_topics(docs, INTERCONNECT)
        self.assertEqual([next(iter(group)) for group in groups], list(GROUPS[INTERCONNECT]))
        self.assertEqual(len(groups), 9)
        self.assertEqual(groups[2], {"封装内芯粒互连": [
            "D2D/wiki/README.md", {"知识地图": "D2D/wiki/SUMMARY.md"},
            {"01 芯粒与连接基础": [
                "D2D/wiki/01-foundations/what-is-a-chiplet.md",
                "D2D/wiki/01-foundations/in-package-connections.md",
                "D2D/wiki/ucie-pcie-read.md",
            ]},
            {"02 接口与案例": [
                "D2D/wiki/02-interfaces/ucie-1-1-link-bring-up.md",
                "D2D/wiki/02-interfaces/ucie-3d.md",
                "D2D/wiki/02-interfaces/ucie-memory.md",
                "D2D/wiki/bow-phy.md",
                "D2D/wiki/02-interfaces/bow-phy-redundancy.md",
                "D2D/wiki/02-interfaces/bow-memory.md",
                "D2D/wiki/bow-flexi.md",
                "D2D/wiki/02-interfaces/aib-2.md",
                "D2D/wiki/02-interfaces/oif-cei-112g-xsr-plus.md",
                "D2D/wiki/02-interfaces/chi-c2c.md",
            ]},
            {"03 系统集成与验证": [
                "D2D/wiki/03-system-design/interoperability-and-bring-up.md",
                "D2D/wiki/03-system-design/flow-control-and-forward-progress.md",
                "D2D/wiki/03-system-design/link-reliability.md",
                "D2D/wiki/03-system-design/effective-bandwidth-and-latency.md",
                "D2D/wiki/03-system-design/multi-chiplet-topology.md",
                "D2D/wiki/03-system-design/link-testing-and-diagnosis.md",
                "D2D/wiki/03-system-design/ucie-dfx-test-access.md",
            ]},
            {"04 产品与系统案例": [
                "D2D/wiki/04-product-cases/stratix-10-tx.md",
                "D2D/wiki/04-product-cases/amd-epyc-9004-gmi.md",
                "D2D/wiki/04-product-cases/amd-mi300a.md",
            ]},
        ]})
        scaleup = groups[5]["加速器互连"]
        self.assertEqual(scaleup[0], "SCALEUP/wiki/README.md")
        self.assertEqual([next(iter(section)) for section in scaleup[1:]], [
            "01 访问语义", "02 交换结构", "03 协议与系统案例", "04 软件与集体通信",
            "05 负载与性能", "06 建模、诊断与查阅",
        ])
        network = groups[6]["系统网络"]
        self.assertEqual(network[0], "NETWORK/wiki/README.md")
        self.assertEqual([next(iter(section)) for section in network[1:]], [
            "01 基础概念", "02 Ethernet 与 IP 网络", "03 RDMA 端点", "04 RoCE",
            "05 InfiniBand", "06 系统集成与新协议", "07 性能、诊断与查阅",
        ])
        coherence = groups[4]["一致性与内存互连"]
        self.assertEqual(coherence[0], "COHERENCE/wiki/README.md")
        self.assertEqual([next(iter(section)) for section in coherence[1:]], [
            "01 基础概念", "02 协议与控制器", "03 CHI", "04 CXL 内存访问",
            "05 性能与可靠性", "06 查阅与验证",
        ])
        self.assertEqual(coherence[4]["04 CXL 内存访问"][0], "COHERENCE/wiki/cxl-host-memory.md")
        for group, name in zip(GROUPS[INTERCONNECT],
                               ("BUS", "NOC", "D2D", "PCIE", "COHERENCE", "SCALEUP", "NETWORK", "SERDES", "CPO")):
            self.assertEqual(next(item[group] for item in groups if group in item)[0], f"{name}/wiki/README.md")

        def pages(item):
            if isinstance(item, str):
                return [item] if item.endswith(".md") else []
            if isinstance(item, list):
                return [page for child in item for page in pages(child)]
            if isinstance(item, dict):
                return [page for child in item.values() for page in pages(child)]
            return []

        nav_pages = pages(groups)
        cpo_pages = [page for page in nav_pages if page.startswith("CPO/wiki/")]
        expected_cpo = {path.relative_to(docs).as_posix() for path in (docs / "CPO/wiki").rglob("*.md")}
        expected_cpo -= ORIGINAL_TOPIC_REDIRECTS
        self.assertEqual(set(cpo_pages), expected_cpo)
        self.assertEqual(len(cpo_pages), len(expected_cpo))
        cpo = groups[-1]["共封装光学（CPO）"]
        group_labels = [next(iter(item)) for item in cpo if isinstance(item, dict)]
        self.assertEqual(group_labels[-4:], [label for label, _ in CPO_SECTIONS])
        for label, directories in CPO_SECTIONS:
            section = next(item[label] for item in cpo if isinstance(item, dict) and label in item)
            expected = {path.relative_to(docs).as_posix()
                        for directory in directories
                        for path in (docs / "CPO/wiki" / directory).rglob("*.md")}
            self.assertEqual(set(pages(section)), expected - ORIGINAL_TOPIC_REDIRECTS, label)

        search_index = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))
        self.assertEqual(search_index["config"]["pipeline"], [])
        search = search_index["docs"]
        locations = {item["location"] for item in search}
        cases = {
            "D2D/wiki/": "封装内芯粒互连",
            "D2D/wiki/SUMMARY/": "封装内芯粒互连",
            "D2D/wiki/01-foundations/what-is-a-chiplet/": "封装内芯粒互连",
            "D2D/wiki/01-foundations/in-package-connections/": "封装内芯粒互连",
            "D2D/wiki/ucie-pcie-read/": "封装内芯粒互连",
            "D2D/wiki/02-interfaces/ucie-1-1-link-bring-up/": "封装内芯粒互连",
            "D2D/wiki/02-interfaces/ucie-3d/": "封装内芯粒互连",
            "D2D/wiki/02-interfaces/ucie-memory/": "封装内芯粒互连",
            "D2D/wiki/bow-phy/": "封装内芯粒互连",
            "D2D/wiki/02-interfaces/bow-phy-redundancy/": "封装内芯粒互连",
            "D2D/wiki/02-interfaces/bow-memory/": "封装内芯粒互连",
            "D2D/wiki/bow-flexi/": "封装内芯粒互连",
            "D2D/wiki/02-interfaces/aib-2/": "封装内芯粒互连",
            "D2D/wiki/02-interfaces/oif-cei-112g-xsr-plus/": "封装内芯粒互连",
            "D2D/wiki/02-interfaces/chi-c2c/": "封装内芯粒互连",
            "D2D/wiki/03-system-design/interoperability-and-bring-up/": "封装内芯粒互连",
            "D2D/wiki/03-system-design/flow-control-and-forward-progress/": "封装内芯粒互连",
            "D2D/wiki/03-system-design/link-reliability/": "封装内芯粒互连",
            "D2D/wiki/03-system-design/effective-bandwidth-and-latency/": "封装内芯粒互连",
            "D2D/wiki/03-system-design/multi-chiplet-topology/": "封装内芯粒互连",
            "D2D/wiki/03-system-design/link-testing-and-diagnosis/": "封装内芯粒互连",
            "D2D/wiki/03-system-design/ucie-dfx-test-access/": "封装内芯粒互连",
            "D2D/wiki/04-product-cases/stratix-10-tx/": "封装内芯粒互连",
            "D2D/wiki/04-product-cases/amd-epyc-9004-gmi/": "封装内芯粒互连",
            "D2D/wiki/04-product-cases/amd-mi300a/": "封装内芯粒互连",
            "COHERENCE/wiki/": "一致性与内存互连",
            "COHERENCE/wiki/cxl-host-memory/": "一致性与内存互连",
            "SCALEUP/wiki/": "加速器互连",
            "NETWORK/wiki/": "系统网络",
            "BUS/wiki/02-fundamentals/bus-vs-noc-vs-point-to-point/": "片上事务与总线（BUS）",
            "NOC/wiki/06-ai-noc-specifics/chiplet-and-die-to-die-interconnect/": "片上网络（NoC）",
            "PCIE/wiki/07-advanced-topics/cxl-and-pcie-boundary/": "系统 I/O 互连（PCIe）",
            "SERDES/wiki/08-system-applications/chiplet-and-d2d/": "高速电链路（SerDes）",
            "CPO/wiki/01-overview/taxonomy/": "共封装光学（CPO）",
        }
        for location, group in cases.items():
            with self.subTest(location=location):
                html = (SITE / location / "index.html").read_text(encoding="utf-8")
                self.assertIn(location, locations)
                self.assertIn(group, BREADCRUMB.search(html).group(1))
                self.assertIsNotNone(ACTIVE_LINK.search(html))

        ucie = (SITE / "D2D/wiki/ucie-pcie-read/index.html").read_text(encoding="utf-8")
        self.assertIn('title="一次跨芯粒的寄存器读，什么时候才算完成？"', ucie)
        self.assertIn("<title>一次跨芯粒的寄存器读，什么时候才算完成？ - 从硅到系统</title>", ucie)
        self.assertRegex(ucie, r'<span class="md-ellipsis">\s*跨芯粒寄存器读\s*</span>')

        bow = (SITE / "D2D/wiki/bow-phy/index.html").read_text(encoding="utf-8")
        self.assertIn('title="BoW PHY 2.0：数据怎样通过并行线路跨越芯粒？"', bow)
        self.assertIn("<title>BoW PHY 2.0：数据怎样通过并行线路跨越芯粒？ - 从硅到系统</title>", bow)
        self.assertRegex(bow, r'<span class="md-ellipsis">\s*BoW PHY 2\.0\s*</span>')

        flexi = (SITE / "D2D/wiki/bow-flexi/index.html").read_text(encoding="utf-8")
        self.assertIn('title="BoW.Flexi：AHB 读取怎样封装成跨芯粒数据包？"', flexi)
        self.assertIn("<title>BoW.Flexi：AHB 读取怎样封装成跨芯粒数据包？ - 从硅到系统</title>", flexi)
        self.assertRegex(flexi, r'<span class="md-ellipsis">\s*BoW\.Flexi 读取案例\s*</span>')

        cxl = (SITE / "COHERENCE/wiki/cxl-host-memory/index.html").read_text(encoding="utf-8")
        self.assertIn('title="CXL：从设备发现到内存访问"', cxl)
        self.assertRegex(cxl, r'<span class="md-ellipsis">\s*04 CXL 内存访问\s*</span>')

        for location, anchor in (
            ("D2D/wiki/", "封装内芯粒互连数据怎样跨越-die-边界"),
            ("D2D/wiki/", "先区分四个问题"),
            ("D2D/wiki/", "以-ucie-为例"),
            ("D2D/wiki/", "不同接口解决不同问题"),
            ("D2D/wiki/", "阅读顺序"),
            ("D2D/wiki/", "继续阅读"),
            ("D2D/wiki/ucie-pcie-read/", "ucie-11-如何承载一次-pcie-读取"),
            ("D2D/wiki/ucie-pcie-read/", "先约定一次读取"),
            ("D2D/wiki/ucie-pcie-read/", "请求经过哪些职责边界"),
            ("D2D/wiki/ucie-pcie-read/", "链路就绪前要确定什么"),
            ("D2D/wiki/ucie-pcie-read/", "一次请求怎样完成"),
            ("D2D/wiki/ucie-pcie-read/", "链路确认不等于事务完成"),
            ("D2D/wiki/ucie-pcie-read/", "接下来怎么读"),
            ("D2D/wiki/bow-phy/", "bow-phy-20数据怎样通过并行线路跨越芯粒"),
            ("D2D/wiki/bow-phy/", "一个-slice-有哪些信号"),
            ("D2D/wiki/bow-phy/", "怎样同时向两个方向传输"),
            ("D2D/wiki/bow-phy/", "一个数据字要占用多久"),
            ("D2D/wiki/bow-phy/", "采样之后还需要什么"),
            ("D2D/wiki/bow-phy/", "phy-怎样接入上层协议"),
            ("D2D/wiki/bow-phy/", "bowflexi-的边界"),
            ("D2D/wiki/bow-phy/", "接下来怎么读"),
            ("D2D/wiki/bow-flexi/", "bowflexiahb-读取怎样封装成跨芯粒数据包"),
            ("D2D/wiki/bow-flexi/", "先约定接口和读取"),
            ("D2D/wiki/bow-flexi/", "一次读取经过哪些层"),
            ("D2D/wiki/bow-flexi/", "请求和响应怎样封包"),
            ("D2D/wiki/bow-flexi/", "读取何时完成"),
            ("D2D/wiki/bow-flexi/", "写入响应和可选-ecc"),
            ("D2D/wiki/bow-flexi/", "接下来怎么读"),
            ("BUS/wiki/02-fundamentals/bus-vs-noc-vs-point-to-point/", "三者的分界不是线多线少"),
            ("NOC/wiki/06-ai-noc-specifics/chiplet-and-die-to-die-interconnect/", "跨-die-不再是多几-hop"),
            ("SERDES/wiki/08-system-applications/chiplet-and-d2d/", "宽接口与较高速接口的取舍"),
        ):
            html = (SITE / location / "index.html").read_text(encoding="utf-8")
            self.assertIn(f'id="{anchor}"', html)

    def test_interconnect_legacy_pages_and_anchors_survive_source_migration(self):
        legacy = json.loads((Path(__file__).parent / "fixtures/interconnect-legacy-anchors.json").read_text(encoding="utf-8"))
        search = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))["docs"]
        locations = {unquote(entry["location"]) for entry in search}
        for path, anchors in legacy.items():
            with self.subTest(page=path):
                html = (SITE / path / "index.html").read_text(encoding="utf-8")
                article = re.search(r'<article\b[^>]*>(.*?)</article>', html, re.DOTALL)
                self.assertIsNotNone(article)
                ids = set(re.findall(r'\bid="([^"]+)"', article.group(1)))
                self.assertFalse(set(anchors) - ids, (path, set(anchors) - ids))
                self.assertIn(path + "/", locations)

    def test_self_test_question_numbers_continue_across_sections(self):
        html = (SITE / "RAM/self-test-questions/index.html").read_text(encoding="utf-8")
        article = re.search(r'<article\b[^>]*>(.*?)</article>', html, re.DOTALL).group(1)
        sections = re.findall(r'<ol start="(\d+)">(.*?)</ol>', article, re.DOTALL)
        starts_and_counts = [(int(start), len(re.findall(r'<li\b', content))) for start, content in sections]
        self.assertEqual(starts_and_counts, [(1, 5), (6, 8), (14, 7), (21, 10), (31, 10),
                                             (41, 12), (53, 10), (63, 5), (68, 8), (76, 5), (81, 2)])
        items = [item for _, content in sections for item in re.findall(r"<li\b[^>]*>(.*?)</li>", content, re.DOTALL)]
        for number in (7, 14, 29, 44, 56, 70, 71, 74):
            bookmark = f'id="q{number}"'
            self.assertEqual(article.count(bookmark), 1)
            self.assertIn(bookmark, items[number - 1])

    def test_storage_practice_entry_points(self):
        practice = Path("RAM/wiki/reading-and-reference/first-read-practice/index.html")
        html = (SITE / practice).read_text(encoding="utf-8")
        breadcrumb = BREADCRUMB.search(html).group(1)
        self.assertIn("查阅与练习", breadcrumb)
        self.assertIn("阅读路线与自测", breadcrumb)
        article = re.search(r"<article\b.*?</article>", html, re.DOTALL).group()
        fragments = ("cpu-read", "npu-move")
        for fragment in fragments:
            self.assertEqual(article.count(f'id="{fragment}"'), 1)
        search = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))
        self.assertIn(practice.parent.as_posix() + "/", {item["location"] for item in search["docs"]})

        for source in (Path("storage/index.html"), Path("RAM/self-test-questions/index.html")):
            html = (SITE / source).read_text(encoding="utf-8")
            article = re.search(r"<article\b.*?</article>", html, re.DOTALL).group()
            links = {urljoin(page_url(source), unescape(href)) for href in re.findall(r'<a\s+[^>]*href="([^"]+)"', article)}
            for fragment in fragments:
                self.assertIn(page_url(practice) + "#" + fragment, links, source)

    def test_reference_legacy_urls_anchors_and_search(self):
        fixture = Path(__file__).parent / "fixtures/storage-reference-legacy-anchors.json"
        legacy = json.loads(fixture.read_text(encoding="utf-8"))
        search = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))["docs"]
        locations = {entry["location"] for entry in search}
        for path, anchors in legacy.items():
            with self.subTest(page=path):
                html = (SITE / path / "index.html").read_text(encoding="utf-8")
                ids = re.findall(r'\bid="([^"]+)"', html)
                for anchor in anchors:
                    self.assertEqual(ids.count(anchor), 1, (path, anchor))
                self.assertIn(path + "/", locations)
                breadcrumb = BREADCRUMB.search(html).group(1)
                self.assertIn("查阅与练习", breadcrumb)
        self.assertIn("RAM/wiki/reading-and-reference/", locations)
        self.assertFalse(any(item["location"].startswith("reviews/") for item in search))

    def test_integration_navigation_legacy_anchors_and_search(self):
        group = grouped_original_topics(SITE.parent / "docs", STORAGE)[5]["存储系统集成与选型"]
        self.assertEqual(group, [
            {"存储系统集成与选型": INTEGRATION_HOME},
            {"不同系统的存储选型": SYSTEM_SELECTION},
            {"封装与集成": [{label: path} for label, path in INTEGRATION_PACKAGING]},
            *[{label: path} for label, path in INTEGRATION_AFTER],
        ])
        legacy = {
            SYSTEM_SELECTION: ("mcucpugpunpu-为什么选择不同存储器", "不同处理器的存储目标"),
            INTEGRATION_PACKAGING[0][1]: ("封装与集成", "封装如何改变存储接口边界", "阅读顺序"),
            INTEGRATION_PACKAGING[1][1]: ("dimmsodimm传统封装形态的电气与机械约束", "模块化容量与板级链路"),
            INTEGRATION_PACKAGING[2][1]: ("popmcp移动端的集成方式", "移动封装的位置与容量取舍"),
            INTEGRATION_AFTER[0][1]: ("npu-选-hbm-还是-lpddr决策框架", "从工作负载反推外存需求"),
            INTEGRATION_AFTER[1][1]: ("cxl近存计算与未来封装方向", "协议计算位置与封装的边界"),
        }
        locations = {entry["location"] for entry in json.loads(
            (SITE / "search/search_index.json").read_text(encoding="utf-8"))["docs"]}
        for name, anchors in legacy.items():
            path = Path(name)
            directory = path.parent if path.name == "README.md" else path.with_suffix("")
            html = (SITE / directory / "index.html").read_text(encoding="utf-8")
            for anchor in (*anchors, "这页在回答什么问题", "一句话理解", "建模启示"):
                self.assertIn(f'id="{anchor}"', html, (name, anchor))
            self.assertIn(directory.as_posix() + "/", locations)
        self.assertIn("RAM/wiki/system-integration/", locations)
        cxl = (SITE / "RAM/wiki/08-packaging-integration/future-packaging-cxl-near-memory/index.html").read_text(encoding="utf-8")
        breadcrumb = BREADCRUMB.search(cxl).group(1)
        self.assertIn("存储系统集成与选型", breadcrumb)
        self.assertNotIn("封装与集成", breadcrumb)
        self.assertIn("system-integration/", breadcrumb)

    def test_series_covers_have_accessible_images_and_working_links(self):
        pages = (
            "foundations/index.html", "storage/index.html", "interconnect/index.html", "external/workload-wiki/index.html",
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
        self.assertEqual(set(assigned), expected - STORAGE_LEGACY_PAGES)
        memory = topics[0]["存储层级与数据路径"]
        self.assertEqual(memory[0], {"专题首页": MEMORY_HOME})
        self.assertEqual([next(iter(item)) for item in memory[1:]], [name for name, _, _ in MEMORY_SECTIONS])
        for node, (name, _directory, pages) in zip(memory[1:], MEMORY_SECTIONS):
            self.assertEqual(node[name], [{label: path} for label, path in pages])
        self.assertEqual(resources[0]["查阅与练习"][0], {"查阅与练习": RESOURCE_HOME})
        self.assertEqual([next(iter(item)) for item in resources[0]["查阅与练习"][1:]],
                         [name for name, _, _ in RESOURCE_SECTIONS])
        for node, (name, _directory, pages) in zip(resources[0]["查阅与练习"][1:], RESOURCE_SECTIONS):
            self.assertEqual(node[name], [{label: path} for label, path in pages])
        self.assertIn("RAM/wiki/07-system-architecture/why-systems-choose-different-memory.md",
                      list(paths(topics[-1])))
        homepage = (SITE / "RAM/wiki/01-overview/index.html").read_text(encoding="utf-8")
        start = homepage.index('<div class="md-sidebar md-sidebar--primary"')
        end = homepage.index('<div class="md-sidebar md-sidebar--secondary"', start)
        self.assertIn('<span class="md-ellipsis">存储层级与数据路径</span>', homepage[start:end])
        route = re.search(r'<h3[^>]*>访问路径与数据管理：按哪条线读？.*?</h3>.*?<ol>(.*?)</ol>', homepage, re.DOTALL)
        self.assertIsNotNone(route)
        links = re.findall(r'<li><a href="([^"]+)">([^<]+)</a>', route.group(1))
        guide = Path("RAM/wiki/01-overview/index.html")
        expected_access = next(pages for name, _, pages in MEMORY_SECTIONS if name == "访问路径与数据管理")
        expected_links = [(page_url(Path(path).with_suffix("") / "index.html"), label) for label, path in expected_access]
        self.assertEqual([(urljoin(page_url(guide), href), label) for href, label in links], expected_links)
        self.assertEqual([label for _, label in links[:2]], ["Cache 怎样判断命中", "Cache miss 的处理"])
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
        self.assertEqual([next(iter(section)) for section in dram],
                         ["DRAM 单元与阵列", "DRAM 命令与接口"])
        self.assertEqual(list(paths(dram)).count(hbm), 1)
        self.assertIn(hbm, list(paths(dram[1])))
        for page in paths(dram):
            path = Path(page)
            location = (path.parent.as_posix() if path.name == "README.md" else path.with_suffix("").as_posix()) + "/"
            self.assertIn(location, locations, page)
        hbm_html = (SITE / "RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io/index.html").read_text(encoding="utf-8")
        article = re.search(r"<article\b.*?</article>", hbm_html, re.DOTALL).group()
        source_url = page_url(Path("RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io/index.html"))
        targets = {urljoin(source_url, unescape(href)) for href in re.findall(r'<a\s+[^>]*href="([^"]+)"', article)}
        selection = page_url(Path("RAM/wiki/09-ai-chip-memory-architecture/hbm-vs-lpddr-for-npu/index.html"))
        for fragment in ("path", "yield", "choose"):
            self.assertIn(selection + "#" + fragment, targets)

    def test_memory_controller_order_and_legacy_anchors(self):
        group = grouped_original_topics(SITE.parent / "docs", STORAGE)[3]["DRAM 控制器与请求调度"]
        root = "RAM/wiki/06-memory-controller/"
        entries = [
            ("README.md", "memory-controller"),
            ("why-mc-is-the-real-bottleneck.md", "memory-controller-如何影响-dram-的实际性能"),
            ("address-mapping-channel-rank-bank-row-col.md", "地址映射物理地址到-channelrankbankrowcol-的拆分艺术"),
            ("command-scheduling-fr-fcfs.md", "命令调度fr-fcfs-及其变体"),
            ("write-buffer-write-drain.md", "写缓冲与-write-drain为什么读优先"),
            ("refresh-management-distributed-postponed.md", "refresh-调度分散刷新推迟刷新bank-level-refresh"),
            ("qos-multi-master-arbitration.md", "多-master-场景下的-qos-与公平性"),
            ("mc-modeling-for-simulation.md", "mc-在-cycle-level-仿真里的建模方法"),
        ]
        self.assertEqual(group, [root + name for name, _ in entries])
        search = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))
        locations = {entry["location"] for entry in search["docs"]}
        for name, anchor in entries:
            slug = "" if name == "README.md" else name.removesuffix(".md") + "/"
            page = SITE / root / slug / "index.html"
            self.assertTrue(page.is_file(), str(page))
            self.assertIn(f'id="{anchor}"', page.read_text(encoding="utf-8"))
            self.assertIn(root + slug, locations)

        article = (SITE / root / "command-scheduling-fr-fcfs/index.html").read_text(encoding="utf-8")
        start = article.index('<div class="md-sidebar md-sidebar--primary"')
        end = article.index('<div class="md-sidebar md-sidebar--secondary"', start)
        active = re.search(r'<label\b[^>]*md-nav__link--active[^>]*for="__toc"[^>]*>\s*'
                           r'<span class="md-ellipsis">(.*?)</span>', article[start:end], re.DOTALL)
        self.assertIsNotNone(active)
        self.assertEqual(unescape(active.group(1).strip()), "请求调度与行保留")
        self.assertIn('aria-label="DRAM 控制器为什么先服务后来排队的读取？"', active.group())

    def test_hbf_order_search_anchors_and_mobile_label(self):
        group = grouped_original_topics(SITE.parent / "docs", STORAGE)[4]["HBF 高带宽闪存"]
        root = "HBF/wiki/"
        entries = [
            ("README.md", "hbf-wiki从-nand-到近计算存储系统"),
            ("01-position.md", "hbf-的位置为什么需要新的存储层"),
            ("02-nand-foundations.md", "nand-基础从电荷到-page-和-block"),
            ("03-architecture.md", "hbf-结构core-diebase-die-和接口"),
            ("04-read-walkthrough.md", "一次-4-kib-读取从请求到数据返回"),
            ("05-mapping-and-performance.md", "地址映射并行度与带宽"),
            ("06-write-and-reliability.md", "写入ftl-与可靠性管理"),
            ("07-workload-and-modeling.md", "ai-工作负载与系统建模"),
            ("08-spec-and-industry.md", "规范产品目标与量产进展"),
            ("09-reference.md", "术语资料与自测"),
        ]
        self.assertEqual(group, [root + name for name, _ in entries])
        search = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))
        locations = {entry["location"] for entry in search["docs"]}
        for name, anchor in entries:
            slug = "" if name == "README.md" else name.removesuffix(".md") + "/"
            page = SITE / root / slug / "index.html"
            self.assertTrue(page.is_file(), str(page))
            self.assertIn(f'id="{anchor}"', page.read_text(encoding="utf-8"))
            self.assertIn(root + slug, locations)

        html = (SITE / root / "06-write-and-reliability/index.html").read_text(encoding="utf-8")
        start = html.index('<div class="md-sidebar md-sidebar--primary"')
        end = html.index('<div class="md-sidebar md-sidebar--secondary"', start)
        active = re.search(r'<label\b[^>]*md-nav__link--active[^>]*for="__toc"[^>]*>\s*'
                           r'<span class="md-ellipsis">(.*?)</span>', html[start:end], re.DOTALL)
        self.assertIsNotNone(active)
        self.assertEqual(unescape(active.group(1).strip()), "写入与可靠性")
        self.assertIn('aria-label="HBF 写入与可靠性：主机和设备如何分工"', active.group())

    def test_nand_lesson_keeps_storage_landing_link_and_legacy_sections(self):
        canonical = Path("HBF/wiki/02-nand-foundations/index.html")
        html = (SITE / canonical).read_text(encoding="utf-8")
        article = re.search(r"<article\b.*?</article>", html, re.DOTALL).group()
        ids = re.findall(r'\bid="([^"]+)"', article)
        for fragment in (
            "nand-基础电荷阵列与-pageblock", "nand-基础从电荷到-page-和-block", "cell-怎样表示数据",
            "stringwordline-和-bitline", "page-与-block-分别做什么", "用-4-kib-检查数据量", "编程擦除与覆盖",
            "两种堆叠不是同一件事",
        ):
            self.assertEqual(ids.count(fragment), 1, fragment)
        home = Path("storage/index.html")
        html = (SITE / home).read_text(encoding="utf-8")
        article = re.search(r"<article\b.*?</article>", html, re.DOTALL).group()
        links = re.findall(r'<a href="([^"]+)">([^<]+)</a>', article)
        self.assertTrue(any(urljoin(page_url(home), href) == page_url(canonical) and "NAND" in label and "SSD" in label
                            for href, label in links))

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

    def test_chip_examples_preserve_pages_anchors_and_search(self):
        prefix = "series/chip-architectures/"
        root = SITE.parents[1]
        source = root / prefix
        legacy = json.loads((root / "website/tests/fixtures/chip-architecture-legacy.json").read_text())["pages"]
        pages = {
            (entry.parent if entry.name == "README.md" else entry.with_suffix("")).relative_to(root).as_posix() + "/"
            for entry in source.rglob("*.md")
        }
        self.assertLessEqual(set(legacy) | {prefix + product + "/" for product in (
            "nvidia-h100-sxm", "google-tpu-v4", "groq-tsp", "stm32n657-neural-art",
        )}, pages)
        self.assertEqual({page.parent.relative_to(SITE).as_posix() + "/"
                          for page in (SITE / prefix).rglob("index.html")}, pages)

        index = json.loads((SITE / "search/search_index.json").read_text())["docs"]
        indexed = Counter(unquote(entry["location"]) for entry in index
                          if entry["location"].startswith(prefix) and "#" not in entry["location"])
        self.assertEqual(indexed, Counter(pages))
        for location in sorted(pages):
            with self.subTest(location=location):
                html = (SITE / location / "index.html").read_text()
                article = re.search(r"<article\b[^>]*>(.*?)</article>", html, re.S)[1]
                ids = Counter(re.findall(r'\s+id="([^"]+)"', article))
                self.assertTrue(all(count == 1 for count in ids.values()), ids)
                self.assertLessEqual(set(legacy.get(location, ())), set(ids))
                self.assertIsNotNone(ACTIVE_LINK.search(html))
                if location != prefix:
                    breadcrumb = BREADCRUMB.search(html)[1]
                    self.assertIn(">芯片架构实例</a>", breadcrumb)
                    self.assertIn("/#", breadcrumb)
                for href in re.findall(r'<a\s+href="([^"]+)"', article):
                    uri = urlsplit(urljoin("https://example.test/" + location, unescape(href)))
                    if uri.netloc != "example.test":
                        continue
                    target = SITE / unquote(uri.path.lstrip("/"))
                    if target.is_dir():
                        target /= "index.html"
                    self.assertTrue(target.is_file(), href)
                    if uri.fragment:
                        self.assertIn(f'id="{unquote(uri.fragment)}"', target.read_text(), href)

        directory = SITE / prefix
        excluded = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
        self.assertFalse([path for path in directory.rglob("*") if path.is_file() and path.suffix.lower() in excluded])

    def test_chip_examples_sidebar_uses_guide_order_and_short_titles(self):
        prefix = "series/chip-architectures/"
        page = (SITE / prefix / "index.html").read_text()
        article = re.search(r"<article\b[^>]*>(.*?)</article>", page, re.S)[1]
        content = article[article.index('id="series-home-content"'):]
        lists = re.findall(r"<ol>\s*(<li>\s*<a .*?)</ol>", content, re.S)
        guide_entries = re.findall(r'<li>\s*<a href="([^"]+)">([^<]+)</a>', "".join(lists))
        self.assertGreaterEqual(len(guide_entries), 10)
        start = page.index('<div class="md-sidebar md-sidebar--primary"')
        end = page.index('<div class="md-sidebar md-sidebar--secondary"', start)
        sidebar_entries = re.findall(
            r'<a\s+href="([^"]+)"[^>]*class="[^"]*md-nav__link[^"]*"[^>]*>\s*'
            r'<span class="md-ellipsis">\s*([^<]+?)\s*</span>', page[start:end],
        )
        targets = {unquote(href) for href, _ in guide_entries}
        self.assertEqual([(unquote(href), unescape(name)) for href, name in sidebar_entries if unquote(href) in targets],
                         [(unquote(href), unescape(name)) for href, name in guide_entries])

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
            "RAM/wiki/09-ai-chip-memory-architecture/hbm-vs-lpddr-for-npu/index.html": ("存储系统", "存储系统集成与选型"),
            "NOC/wiki/02-router-microarchitecture/credit-based-flow-control/index.html": ("芯片与系统互连", "片上网络（NoC）"),
            "SERDES/wiki/06-link-operation/pcie-training-case/index.html": ("芯片与系统互连", "高速电链路（SerDes）"),
            "DMA/wiki/04-programming-model/tiling-double-buffering/index.html": ("计算微架构", "DMA 与异步数据搬运"),
            "external/workload-wiki/01-foundation-model-components/contrastive-learning/index.html": ("算法与模型", "表示学习与训练目标"),
            "series/chip-development/02_frontend_design_and_verification/05_dft_introduction/index.html": ("芯片开发与实现", "可测性设计、晶圆筛测与终测"),
            "FAB/wiki/03-wafer-test-and-cp/index.html": ("芯片开发与实现", "可测性设计、晶圆筛测与终测"),
            "series/chip-development/04_tapeout_and_post_silicon/03_packaging/index.html": ("芯片开发与实现", "封装与多芯粒集成"),
            "FAB/wiki/04-back-end-packaging/index.html": ("芯片开发与实现", "封装与多芯粒集成"),
            "FAB/wiki/06-cross-cutting-engineering/yield-economics-across-stages/index.html": ("芯片开发与实现", "可靠性、良率与量产生命周期"),
            "series/inference-runtime/topics/01-prefill-decode/index.html": ("推理运行时", "请求路径与服务指标"),
            "series/inference-runtime/topics/06-paged-kv-cache/index.html": ("推理运行时", "运行时状态与 KV 管理"),
            "series/inference-runtime/topics/15-quantitative-estimation/index.html": ("推理运行时", "测量、建模与框架案例"),
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
            "01-overview": 4, "02-signal-channel": 6, "03-transmitter": 4,
            "04-receiver": 6, "05-signaling-and-metrics": 5, "06-link-operation": 5,
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
        for figure in ("link-overview.svg", "differential.svg", "reflection.svg", "crosstalk-and-isi.svg", "tx-timing.svg", "rx-feedback.svg", "nrz-pam4.svg", "eye-metrics.svg", "training-feedback.svg", "event-model.svg"):
            self.assertTrue((SITE / "SERDES" / "wiki" / "img" / figure).is_file())

        figure_pages = {
            "01-overview/link-end-to-end": "link-overview.svg",
            "02-signal-channel/differential-and-return": "differential.svg",
            "02-signal-channel/impedance-and-reflection": "reflection.svg",
            "02-signal-channel/isi-noise-and-eye": "crosstalk-and-isi.svg",
            "03-transmitter/tx-path-worked-example": "tx-timing.svg",
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
                    return owner(article_source) == owner(chapter_source)
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

    def test_merged_dram_article_and_legacy_deep_links(self):
        chapter = Path("RAM/wiki/04-dram-foundations")
        canonical = chapter / "1t1c-cell-destructive-read" / "index.html"
        html = (SITE / canonical).read_text(encoding="utf-8")
        article = re.search(r"<article\b.*?</article>", html, re.DOTALL).group()
        ids = re.findall(r'\bid="([^"]+)"', article)
        for fragment in (
            "1t1c-dram电荷保存与读出恢复", "1t1c-cell一颗电容为什么改变了一切", "这页在回答什么问题",
            "电容存储与破坏性读出", "电容密度与保存电荷", "电荷泄漏与读出限制", "一句话理解", "建模启示",
            "charge-sharing", "sense-restore", "column-select", "write", "row-state", "access-granularity", "model",
        ):
            self.assertEqual(ids.count(fragment), 1, fragment)

        expected = {
            "row-column-decode-sense-amplify": ("dram-行列解码感测恢复与列选择", {
                "行列解码与读出放大为什么-dram-必须先开行": "sense-restore",
                "这页在回答什么问题": "access-granularity", "位线感测整行恢复与列选择": "sense-restore",
                "位线电荷共享与整行感测": "charge-sharing", "行选通与列选择": "column-select",
                "一句话理解": "access-granularity", "建模启示": "model",
            }),
            "row-buffer-as-cache": ("row-buffer-与-dram-行状态", {
                "row-bufferdram-内部的小-cache": "row-state", "这页在回答什么问题": "sense-restore",
                "打开行的工作副本": "row-state", "一句话理解": "row-state", "建模启示": "model",
            }),
        }
        index = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))
        locations = {entry["location"].partition("#")[0] for entry in index["docs"]}
        self.assertIn(canonical.parent.as_posix() + "/", locations)
        for slug, (old_title, fragments) in expected.items():
            with self.subTest(slug=slug):
                path = chapter / slug / "index.html"
                legacy = (SITE / path).read_text(encoding="utf-8")
                self.assertIn(f'id="{old_title}"', legacy)
                self.assertNotIn(path.parent.as_posix() + "/", locations)
                fallback = re.search(r'<div [^>]*data-storage-redirect[^>]*>(.*?)</div>', legacy, re.DOTALL)
                self.assertIsNotNone(fallback)
                routes = dict(re.findall(r'<span id="([^"]+)"></span>\s*<a href="([^"]+)"', fallback.group(1)))
                self.assertEqual(set(routes), set(fragments))
                for old, new in fragments.items():
                    self.assertEqual(urljoin(page_url(path), routes[old]), page_url(canonical) + "#" + new)

    def test_dram_timing_bookmarks_land_in_merged_command_article(self):
        chapter = Path("RAM/wiki/05-dram-protocol-families")
        canonical = chapter / "commands-act-rd-wr-pre" / "index.html"
        legacy = chapter / "timing-parameters-trcd-trp-tras" / "index.html"
        old_fragments = {
            "dram-时序从命令采样到读写恢复", "关键-timing-参数trcdtrptrastcl-的物理来源", "这页在回答什么问题",
            "命令时序对应的物理等待", "开行列访问与首数据", "行保持与预充", "写恢复与参数适用条件",
            "ddr4-同-bank-显式-pre-的完整下界", "一句话理解", "建模启示",
        }
        self.assert_storage_merge_links(canonical, legacy, {
            "dram-命令actrdwr-与-pre", "actrdwrpredram-命令集为什么长这样", "命令如何改变-bank-和行状态",
            "actrdwrpre-的职责", "行命中关闭行和行冲突", "pre-不是列命令发出后立即可用",
        }, {key: key for key in old_fragments}, default="命令时序对应的物理等待")

    def test_page_policy_bookmarks_land_in_scheduling_article(self):
        chapter = Path("RAM/wiki/06-memory-controller")
        canonical = chapter / "command-scheduling-fr-fcfs/index.html"
        legacy = chapter / "page-policy-open-close-adaptive/index.html"
        self.assert_storage_merge_links(canonical, legacy, {
            "dram-命令调度就绪判断与-fr-fcfs", "命令调度fr-fcfs-及其变体", "就绪命令选择与等待代价",
            "一个可复核的仲裁例子", "吞吐与等待",
            "行缓冲策略保留预充与自适应选择", "opencloseadaptive-page-policy-的权衡",
            "这页在回答什么问题", "一句话理解", "建模启示",
        }, {
            "行缓冲策略保留预充与自适应选择": "page-policy", "opencloseadaptive-page-policy-的权衡": "page-policy",
            "这页在回答什么问题": "page-policy", "打开行的保留与关闭决策": "打开行的保留与关闭决策",
            "行驻留与后续请求": "行驻留与后续请求", "观察到达时间": "观察到达时间",
            "自适应策略要看什么": "自适应策略要看什么", "策略与-auto-precharge-的区别": "策略与-auto-precharge-的区别",
            "一句话理解": "page-policy", "建模启示": "model",
        }, default="page-policy")

    def test_sram_macro_bookmarks_land_in_timing_article(self):
        chapter = Path("RAM/wiki/02-sram-foundations")
        canonical = chapter / "read-write-cycle-timing/index.html"
        legacy = chapter / "sram-macro-interface-and-semantics/index.html"
        self.assert_storage_merge_links(canonical, legacy, {
            "sram-一次访问电气阶段与接口时序", "访问由哪些阶段构成", "一个同步宏的接口例子",
            "为什么延迟和接纳间隔不能混为一谈", "工艺频率与可见边界", "建模启示", "接下来怎么读",
            "electrical", "collision", "timing-checks",
        }, {
            "sram-宏接口地址时序与访问语义": "macro-pins", "sram-宏接口怎样正确发起读写": "macro-pins",
            "1-宏向外提供什么": "macro-pins", "2-从一个-64-32-bit-的宏读接口": "word-address",
            "byte-地址怎样对应-word-地址": "word-address", "写掩码改变哪些位": "write-mask",
            "部分写入需要读改写时": "read-modify-write", "3-数据有效时间与下一次接纳间隔": "pipeline",
            "4-两个端口可以同时做什么": "ports", "5-宏接口与系统接口在哪里分界": "wrapper",
            "一句话理解": "timeline", "建模启示": "model", "接下来怎么读": "next",
        }, default="macro-pins")

    def test_npu_weight_lessons_merge_without_losing_bookmarks(self):
        chapter = Path("RAM/wiki/09-ai-chip-memory-architecture")
        canonical = chapter / "npu-memory-hierarchy/index.html"
        canonical_ids = {
            "npu-存储层次数据放在哪里如何到达计算单元", "npu-的存储层次l0l1l2-sram-与-hbmlpddr", "这页在回答什么问题",
            "各级存储的距离复用与职责", "一个贯穿本组文章的构造例子", "真实架构的路径可以不同", "一句话理解",
            "建模启示", "接下来怎么读", "tile", "implementations",
        }
        legacy_routes = {
            "data-movement-first-principle": ("traffic", {
                "npu-数据搬运如何权衡复用时间与能耗": "traffic", "数据搬运优先原则在-npu-设计中的体现": "paths",
                "这页在回答什么问题": "traffic", "计算所需的数据跨越哪些边界": "paths",
                "同一任务两种权重驻留策略": "traffic", "搬运量减少以后还要检查什么": "energy",
                "一句话理解": "traffic", "建模启示": "model", "接下来怎么读": "next",
            }),
            "weight-buffer-design": ("residency", {
                "权重缓冲区从工作集与供数需求确定容量和组织": "residency", "weight-buffer-的容量与组织从-model-size-反推": "residency",
                "这页在回答什么问题": "residency", "权重工作集容量与复用": "residency",
                "weight-buffer-的容量与组织": "supply", "局部与共享怎样选择": "shared",
                "一句话理解": "residency", "建模启示": "model", "接下来怎么读": "next",
            }),
        }
        for slug, (default, routes) in legacy_routes.items():
            with self.subTest(slug=slug):
                self.assert_storage_merge_links(canonical, chapter / slug / "index.html", canonical_ids, routes, default)

    def test_hbm_packaging_and_cost_bookmarks_land_in_selection_article(self):
        canonical = Path("RAM/wiki/09-ai-chip-memory-architecture/hbm-vs-lpddr-for-npu/index.html")
        fragments = {
            "path", "width", "yield", "budget", "choose", "model", "next",
            "npu-外存选型hbm-与-lpddr", "npu-选-hbm-还是-lpddr决策框架", "这页在回答什么问题",
            "从工作负载反推外存需求", "一个教学算例", "按什么顺序比较", "一句话理解", "建模启示",
        }
        old_directory = Path("RAM/wiki/08-packaging-integration")
        packaging = {
            "hbm-的堆叠与封装内互连": "path", "hbm-的-25d3d-集成与-tsv-技术": "path",
            "这页在回答什么问题": "path", "tsv堆叠与近距宽接口": "path", "宽接口怎样形成带宽": "width",
            "一句话理解": "path", "建模启示": "model",
        }
        cost = {
            "hbm-的成本从哪里来": "yield", "hbm-的成本结构为什么这么高": "yield",
            "这页在回答什么问题": "yield", "堆叠良率与封装成本": "yield", "两个有边界的算例": "yield",
            "比较时固定目标": "choose", "一句话理解": "yield", "建模启示": "model",
        }
        self.assert_storage_merge_links(canonical, old_directory / "hbm-2.5d-3d-tsv/index.html",
                                        fragments, packaging, "path")
        self.assert_storage_merge_links(canonical, old_directory / "why-hbm-is-expensive/index.html",
                                        fragments, cost, "yield")

    def assert_storage_merge_links(self, canonical, legacy, main_fragments, expected_routes, default):
        html = (SITE / canonical).read_text(encoding="utf-8")
        article = re.search(r"<article\b.*?</article>", html, re.DOTALL).group()
        for fragment in main_fragments | set(expected_routes.values()):
            self.assertEqual(article.count(f'id="{fragment}"'), 1, fragment)
        stub = (SITE / legacy).read_text(encoding="utf-8")
        fallback = re.search(r'<div [^>]*data-storage-redirect[^>]*>(.*?)</div>', stub, re.DOTALL)
        self.assertIsNotNone(fallback)
        routes = re.findall(r'<span id="([^"]+)"></span>\s*<a href="([^"]+)"', fallback.group(1))
        self.assertEqual({fragment for fragment, _ in routes}, set(expected_routes))
        self.assertEqual(unquote(urlsplit(routes[0][1]).fragment), default)
        for fragment, href in routes:
            self.assertEqual(unquote(urljoin(page_url(legacy), href)), page_url(canonical) + "#" + expected_routes[fragment])
        index = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))
        locations = {entry["location"].partition("#")[0] for entry in index["docs"]}
        self.assertIn(canonical.parent.as_posix() + "/", locations)
        self.assertNotIn(legacy.parent.as_posix() + "/", locations)

    def test_cache_scratchpad_comparison_keeps_legacy_entry(self):
        main = Path("COMPUTE/wiki/06-memory-discipline/cache-vs-scratchpad/index.html")
        legacy = Path("RAM/wiki/03-sram-applications/scratchpad-vs-cache/index.html")
        main_html = (SITE / main).read_text(encoding="utf-8")
        legacy_html = (SITE / legacy).read_text(encoding="utf-8")

        for anchor in ("cache-与-scratchpad数据放置和访问时间", "两种数据管理方式", "同时访问的反例", "建模启示"):
            self.assertIn(f'id="{anchor}"', main_html)
        for anchor in ("scratchpad-和-cache-都是-sram差异在哪", "这页在回答什么问题", "地址管理与数据放置方式", "一句话理解", "建模启示"):
            self.assertIn(f'id="{anchor}"', legacy_html)

        article = re.search(r"<article\b.*?</article>", legacy_html, re.DOTALL).group()
        targets = {urlsplit(urljoin(page_url(legacy), unescape(href))).path
                   for href in re.findall(r'<a\s+[^>]*href="([^"]+)"', article)}
        self.assertIn("/COMPUTE/wiki/06-memory-discipline/cache-vs-scratchpad/", targets)

        entries = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))["docs"]
        locations = {unquote(entry["location"]) for entry in entries}
        self.assertIn("COMPUTE/wiki/06-memory-discipline/cache-vs-scratchpad/", locations)
        self.assertIn("RAM/wiki/03-sram-applications/scratchpad-vs-cache/", locations)
        self.assertTrue(any(
            entry["location"].startswith("RAM/wiki/03-sram-applications/scratchpad-vs-cache/")
            and "Scratchpad 和 cache 都是 SRAM，差异在哪" in (entry["title"] + entry["text"]).replace("\u200b", "")
            for entry in entries
        ))

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
                "6T SRAM 怎样读出一个 bit，又怎样把它改写？",
            ],
            "CPO/wiki/08-research/detailed-cards/cpo-status-challenges-solutions/index.html": [
                "首页", "芯片与系统互连", "共封装光学（CPO）", "学习与查阅", "文献与术语",
                "完整论文卡", "完整卡：CPO status, challenges, and solutions",
            ],
            "electrical-timing-foundations/index.html": [
                "首页", "计算微架构", "流水线、时序与时钟域", "从电荷到芯片时序：一条可手算的路径",
            ],
            "SERDES/wiki/05-signaling-and-metrics/ber-confidence-and-fec/index.html": [
                "首页", "芯片与系统互连", "高速电链路（SerDes）", "05 信号与指标",
                "BER、置信度与 FEC 怎样关联？",
            ],
            "SERDES/wiki/06-link-operation/pcie-training-case/index.html": [
                "首页", "芯片与系统互连", "高速电链路（SerDes）", "06 初始化与训练",
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
        # SRAM parent is already in breadcrumbs; the historical RAM route remains available.
        self.assertNotIn("<p>上级：", ram)
        self.assertIn(">RAM 阅读路线</a>", ram)
        self.assertIn("<p>上级:", fab)

    def test_sram_cell_keeps_old_reading_and_demo_links(self):
        path = Path("RAM/wiki/02-sram-foundations/6t-cell-bistable-storage/index.html")
        html = (SITE / path).read_text(encoding="utf-8")
        article = re.search(r"<article\b.*?</article>", html, re.DOTALL).group()
        ids = re.findall(r'\bid="([^"]+)"', article)
        for fragment in (
            "6t-sram-cell它如何保存读取和写入-1-bit", "1-先认识六个晶体管", "2-保持两个反相器互相维持状态",
            "3-读先建立位线差分再感测", "步骤一预充并均衡", "步骤二打开字线形成差分", "步骤三感测并结束访问",
            "为什么读也可能改变数据", "4-写让外部驱动改变旧状态", "步骤一准备目标数据",
            "步骤二打开字线与旧状态竞争", "步骤三反馈推动新状态建立", "5-读稳定性与可写入性为什么需要折中",
            "6-从-cell-到架构模型", "接下来怎么读", "延伸阅读", "sram-arrow-read", "sram-arrow-write",
        ):
            self.assertEqual(ids.count(fragment), 1, fragment)
        for mode in ("read", "write"):
            self.assertEqual(article.count(f'data-sram-demo="{mode}"'), 1)
        featured = (SITE / "articles/index.html").read_text(encoding="utf-8")
        card = re.search(rf'<a class="article-card" href="\.\./{path.parent.as_posix()}/">.*?<h2>(.*?)</h2>', featured)
        self.assertIsNotNone(card)
        self.assertEqual(card.group(1), "6T SRAM 怎样读出一个 bit，又怎样把它改写？")

    def test_sram_array_path_keeps_old_section_links(self):
        path = SITE / "RAM/wiki/02-sram-foundations/wordline-bitline-sense-amp/index.html"
        html = path.read_text(encoding="utf-8")
        article = re.search(r"<article\b.*?</article>", html, re.DOTALL).group()
        ids = re.findall(r'\bid="([^"]+)"', article)
        for fragment in (
            "字线位线与读出放大器sram-的阵列路径", "阵列中的职责", "一次读取行列和外围怎样配合",
            "读位线电荷与差分", "写位线驱动-cell", "线为什么影响访问时间",
            "一句话理解", "建模启示", "接下来怎么读",
        ):
            self.assertEqual(ids.count(fragment), 1, fragment)

    def test_sram_reading_order_and_reliability_search(self):
        applications = (SITE / "RAM/wiki/03-sram-applications/index.html").read_text(encoding="utf-8")
        reading = re.search(r'<h2\b[^>]*>[^<]*阅读顺序.*?</h2>.*?<ol>(.*?)</ol>', applications, re.DOTALL)
        self.assertIsNotNone(reading)
        links = re.findall(r'<li>\s*<a href="([^"]+)">', reading.group(1))
        self.assertEqual(links, [
            "register-file-as-sram/", "cache-sram-tag-data-arrays/", "scratchpad-vs-cache/",
            "tcm-itcm-dtcm-in-mcu/", "npu-weight-buffer-activation-buffer/",
        ])
        third_item = re.findall(r"<li>(.*?)</li>", reading.group(1), re.DOTALL)[2]
        self.assertIn('href="../../../COMPUTE/wiki/06-memory-discipline/cache-vs-scratchpad/"', third_item)
        foundations = (SITE / "RAM/wiki/02-sram-foundations/index.html").read_text(encoding="utf-8")
        self.assertIn('href="sram-reliability-ecc-mbist-repair/"', foundations)
        index = json.loads((SITE / "search/search_index.json").read_text(encoding="utf-8"))
        self.assertIn("RAM/wiki/02-sram-foundations/sram-reliability-ecc-mbist-repair/",
                      {entry["location"] for entry in index["docs"]})
        self.assertFalse(any(entry["location"].startswith("reviews/") for entry in index["docs"]))

    def test_noc_comparison_links_to_its_interactive_diagram(self):
        page = Path("NOC/wiki/01-overview/bus-vs-noc-vs-crossbar/index.html")
        body = (SITE / page).read_text(encoding="utf-8").split("<article", 1)[1].split("</article>", 1)[0]
        diagram_url = f"https://example.test/{SHARED_PATHS_DIAGRAM.as_posix()}"
        for pattern in (r'<iframe\b[^>]*\bsrc="([^"]+)"', r'<a\b[^>]*\bhref="([^"]+)"'):
            targets = {urljoin(page_url(page), unescape(ref)) for ref in re.findall(pattern, body)}
            self.assertIn(diagram_url, targets)

        diagram = (SITE / SHARED_PATHS_DIAGRAM).read_text(encoding="utf-8")
        controls = re.findall(r'<input type="radio" name="([^"]+)" value="([^"]+)"', diagram)
        self.assertCountEqual(controls, [
            ("structure", "bus"), ("structure", "crossbar"), ("structure", "mesh"),
            ("target", "x"), ("target", "y"),
        ])

    def test_current_navigation_and_breadcrumb_links(self):
        self.assertTrue(SITE.is_dir(), "Build the site before running this test")
        standalone_pages = {
            SITE / SHARED_PATHS_DIAGRAM,
            SITE / "series/index.html",
            *(SITE / "foundations" / slug / "index.html" for slug in (*FOUNDATION_MERGED_ARTICLES, *FOUNDATION_SPLIT_ARTICLES)),
            *(SITE / "foundations" / companion for companion in FOUNDATION_COMPANIONS),
            *(SITE / "foundations/silicon-to-logic" / slug / "index.html" for slug in SILICON_TO_LOGIC_LEGACY_SECTIONS),
        }
        unlisted = UNLISTED_LANDING_PAGES | {
            (Path(path).with_suffix("") / "index.html").as_posix() for path in {*ORIGINAL_TOPIC_REDIRECTS, D2D_READ_REDIRECT, COHERENCE_MSI_REDIRECT}
        }
        pages = sorted(p for p in SITE.rglob("*.html") if p.name != "404.html" and p not in standalone_pages)
        self.assertGreater(len(pages), 1)
        errors = []
        for path in pages:
            relative = path.relative_to(SITE)
            html = path.read_text(encoding="utf-8")
            start = html.find('<div class="md-sidebar md-sidebar--primary"')
            end = html.find('<div class="md-sidebar md-sidebar--secondary"', start)
            primary = html[start:end] if start >= 0 and end >= 0 else ""
            active = list(ACTIVE_LINK.finditer(primary))
            if relative.as_posix() in unlisted:
                if active:
                    errors.append(f"{relative}: unlisted page has an active sidebar link")
            elif relative.parts[0] != "reviews":
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
