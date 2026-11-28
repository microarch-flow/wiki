"""Verify I03's page and exact expert-placement/dispatch teaching model."""

from collections import Counter, defaultdict
from fractions import Fraction
import unittest

import test_compiler_runtime_guides as guides


class I03Tests(unittest.TestCase):
    routes = [(0, 1), (0, 2), (0, 1), (1, 2)]
    token_rank = [0, 0, 1, 1]
    expert_rank = [0, 0, 1]

    def assignments(self):
        return [(t, e, self.token_rank[t], self.expert_rank[e])
                for t, experts in enumerate(self.routes) for e in experts]

    def test_navigation_search_and_figures(self):
        route = "09-distributed-execution"
        slug = "i03-expert-parallelism"
        guides.CompilerRuntimeGuideTests()._check_article(
            route, "分布式执行与通信编排", slug,
            "每个 Token 选择不同专家，怎样将计算送到相应设备？",
            ("i03-dispatch.svg", "i03-combine.svg", "i03-expert-load.svg"),
        )
        previous = guides.SITE / guides.PREFIX / route / "i02-pipeline-and-data-parallelism/index.html"
        self.assertIn(f"../{slug}/", guides.GuideContent(previous.read_text()).links)

    def test_token_routing_and_payloads(self):
        entries = self.assignments()
        matrix = [[sum((i, j) == (src, dst) for _, _, src, dst in entries)
                   for j in range(2)] for i in range(2)]
        self.assertEqual(matrix, [[3, 1], [3, 1]])
        groups = defaultdict(list)
        for t, e, _, _ in entries:
            groups[e].append(t)
        self.assertEqual(dict(groups), {0: [0, 1, 2], 1: [0, 2, 3], 2: [1, 3]})
        bytes_per_vec = 8 * 2
        self.assertEqual(len(entries) * bytes_per_vec, 128)
        remote = [(t, e, src, dst) for t, e, src, dst in entries if src != dst]
        self.assertEqual(Counter(src for _, _, src, _ in remote), {0: 1, 1: 3})
        self.assertEqual(len(remote) * bytes_per_vec, 64)
        deduplicated = {(t, src, dst) for t, _, src, dst in remote}
        self.assertEqual(Counter(src for _, src, _ in deduplicated), {0: 1, 1: 2})
        self.assertEqual(len(deduplicated) * bytes_per_vec, 48)
        # Independent return: reverse each direction, retaining assignment identity.
        self.assertEqual(Counter(dst for _, _, _, dst in remote), {0: 3, 1: 1})
        self.assertEqual(len(remote) * bytes_per_vec, 64)
        self.assertEqual((8 * 16 + 16 * 8) * 2, 512)  # weight per expert
        self.assertEqual(3 * 512, 1536)
        per_assignment = 4 * 8 * 16
        self.assertEqual([sum(len(groups[e]) * per_assignment for e in range(3)
                              if self.expert_rank[e] == r) for r in range(2)], [3072, 1024])

    def test_combine_restores_token_identity(self):
        # Return order differs from input order and grouping by local expert.
        route_results = [(t, e, Fraction(1, 2), 10 * t + e)
                         for t, e, _, _ in self.assignments() if t != 2]
        route_results.extend([(2, 0, Fraction(2, 3), 4), (2, 1, Fraction(1, 3), 10)])
        reconstructed = defaultdict(Fraction)
        for t, _, weight, value in sorted(route_results, key=lambda entry: -entry[1]):
            reconstructed[t] += weight * value
        self.assertEqual([reconstructed[t] for t in range(4)],
                         [Fraction(1, 2), Fraction(11), Fraction(6), Fraction(63, 2)])

    def test_capacity_skew_replication_and_groups(self):
        entries = self.assignments()
        groups = defaultdict(list)
        for t, e, _, _ in entries:
            groups[e].append(t)
        self.assertEqual([groups[e][:2] for e in range(3)], [[0, 1], [0, 2], [1, 3]])
        self.assertEqual([groups[e][2:] for e in range(3)], [[2], [3], []])
        self.assertEqual(sum(len(g) for g in groups.values()), 8)
        hot = [(0, 1 if t < 4 else 2 if t < 7 else 3) for t in range(8)]
        counts = Counter(e for pair in hot for e in pair)
        loads = [counts[e] for e in range(4)]
        self.assertEqual(loads, [8, 4, 3, 1])
        self.assertEqual(sum(loads) / 4, 4)
        self.assertEqual(max(loads), 8)
        self.assertEqual(max([4, 4, *loads[1:]]), 4)
        self.assertEqual(Fraction(5 - 4, 4), Fraction(1, 4))
        rank = lambda d, p, t: ((d * 2) + p) * 2 + t
        self.assertEqual([[rank(d, p, t) for d in range(2) for t in range(2)]
                          for p in range(2)], [[0, 1, 4, 5], [2, 3, 6, 7]])


if __name__ == "__main__":
    unittest.main()
