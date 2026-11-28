"""Verify I05 navigation and PD handoff teaching calculations."""

from collections import Counter
from fractions import Fraction
import json
import unittest

import test_compiler_runtime_guides as guides


class I05Tests(unittest.TestCase):
    def test_navigation_search_figures_and_complete_topic(self):
        route = "09-distributed-execution"
        slug = "i05-prefill-decode-disaggregation"
        guides.CompilerRuntimeGuideTests()._check_article(
            route, "分布式执行与通信编排", slug,
            "Prefill 和 Decode 分开执行时，KV 怎样完成交接？",
            ("i05-state-handoff.svg", "i05-layout-transfer.svg",
             "i05-first-token-timeline.svg", "i05-backpressure.svg"),
        )
        previous = guides.SITE / guides.PREFIX / route / "i04-context-parallelism/index.html"
        self.assertIn(f"../{slug}/", guides.GuideContent(previous.read_text()).links)
        topic = guides.PREFIX + route + "/"
        locations = Counter(entry["location"] for entry in json.loads(
            (guides.SITE / "search/search_index.json").read_text())["docs"]
            if "#" not in entry["location"] and entry["location"].startswith(topic))
        slugs = ("i01-tensor-parallelism", "i02-pipeline-and-data-parallelism",
                 "i03-expert-parallelism", "i04-context-parallelism", slug)
        self.assertEqual(locations, Counter([topic] + [f"{topic}{s}/" for s in slugs]))

    def test_prefill_handoff_and_next_input(self):
        kv_per_position = 2 * 2 * 16 * 2  # K/V, heads, dimension, FP16
        p = list(range(1, 9))
        histories = {7: p[:4], 2: p[4:]}
        # y1 already chosen, not yet consumed by a forward step.
        known, generated, valid = 9, 1, len(p)
        self.assertEqual((known, generated, valid), (9, 1, 8))
        self.assertEqual(valid * kv_per_position, 1024)
        destination = {9: histories[7][:], 12: histories[2][:]}
        self.assertEqual(destination[9] + destination[12], p)
        self.assertEqual(len(destination[12]) * kv_per_position, 512)
        # After D consumes y1 and samples y2, one more position is valid.
        self.assertEqual(((known + 1), (generated + 1), (valid + 1)), (10, 2, 9))
        self.assertEqual((valid + 1) * kv_per_position, 1152)

    def test_head_to_position_layout(self):
        p = [{(head, pos) for pos in range(1, 9)} for head in range(2)]
        d = [{(head, pos) for head in range(2) for pos in range(1, 5)},
             {(head, pos) for head in range(2) for pos in range(5, 9)}]
        payload = [[len(src & dest) * 64 for dest in d] for src in p]
        self.assertEqual(payload, [[256, 256], [256, 256]])
        self.assertEqual(sum(map(sum, payload)), 1024)
        for dest in d:
            self.assertEqual(set.union(*(src & dest for src in p)), dest)
        self.assertEqual(sum(row[1] for row in payload), 512)

    def test_transfer_cost_and_first_token_timing(self):
        bytes_per_position = 80 * 8 * 128 * 2 * 2
        self.assertEqual(bytes_per_position, 320 * 1024)
        payload = 2000 * bytes_per_position
        self.assertEqual(payload, 625 * 2**20)
        transfer_ms = Fraction(payload * 1000, 64 * 10**9)
        self.assertEqual(transfer_ms, Fraction(1024, 100))
        second = transfer_ms + 2
        self.assertEqual(second, Fraction(1224, 100))
        self.assertEqual(second - 0, Fraction(1224, 100))
        self.assertEqual(second - transfer_ms, 2)

    def test_bounded_queue_and_backpressure(self):
        def run(capacity=None):
            q = 0
            trace = [q]
            produced = []
            for _ in range(3):
                q -= min(q, 1)
                amount = 2 if capacity is None else min(2, capacity - q)
                q += amount
                produced.append(amount)
                trace.append(q)
            return trace, produced

        self.assertEqual(run(), ([0, 2, 3, 4], [2, 2, 2]))
        self.assertEqual(run(2), ([0, 2, 2, 2], [2, 1, 1]))


if __name__ == "__main__":
    unittest.main()
