"""Verify I04 page and distributed attention teaching calculations."""

import math
import random
import re
import unittest

import test_compiler_runtime_guides as guides


def partial(scores, values):
    if not scores:
        return None
    m = max(scores)
    w = [math.exp(s - m) for s in scores]
    return m, sum(w), sum(a * b for a, b in zip(w, values))


def merge(parts):
    # Empty fragments contribute zero; all-empty has no mathematical quotient.
    parts = [p for p in parts if p is not None]
    if not parts:
        return None
    m = max(p[0] for p in parts)
    factors = [math.exp(p[0] - m) for p in parts]
    l = sum(f * p[1] for f, p in zip(factors, parts))
    z = sum(f * p[2] for f, p in zip(factors, parts))
    return z / l


class I04Tests(unittest.TestCase):
    def test_navigation_math_search_and_figures(self):
        route = "09-distributed-execution"
        slug = "i04-context-parallelism"
        guides.CompilerRuntimeGuideTests()._check_article(
            route, "分布式执行与通信编排", slug,
            "上下文太长，怎样将历史状态分给多张卡？",
            ("i04-kv-layout.svg", "i04-prefill-causal.svg",
             "i04-softmax-merge.svg", "i04-decode-handoff.svg"),
        )
        previous = guides.SITE / guides.PREFIX / route / "i03-expert-parallelism/index.html"
        self.assertIn(f"../{slug}/", guides.GuideContent(previous.read_text()).links)
        page = (guides.SITE / guides.PREFIX / route / slug / "index.html").read_text()
        body = re.search(r"<article\b[^>]*>(.*?)</article>", page, re.S)[1]
        self.assertEqual(len(re.findall(r'class="arithmatex(?: |")', body)), 3)

    def test_head_and_position_shards(self):
        kv_head = 2 * 16 * 2
        self.assertEqual(kv_head, 64)
        self.assertEqual(8 * 2 * kv_head, 1024)
        self.assertEqual(8 * kv_head, 512)
        self.assertEqual(4 * 2 * kv_head, 512)
        self.assertEqual(4 * 8 * kv_head, 2048)
        self.assertEqual(4 * 4 * kv_head, 1024)
        self.assertEqual(8 * 2 * kv_head, 1024)
        whole = 4096 * 2 * 80 * 8 * 128 * 2
        self.assertEqual(whole, 5 * 2**28)
        self.assertEqual(whole // 2, 5 * 2**27)

    def test_causal_prefill_and_payload(self):
        contiguous = [list(range(1, 5)), list(range(5, 9))]
        paired = [[1, 2, 7, 8], [3, 4, 5, 6]]
        for positions, expected, traffic in [(contiguous, [10, 26], 512),
                                              (paired, [18, 18], 768)]:
            work = [sum(1 for q in group for k in range(1, 9) if k <= q)
                    for group in positions]
            self.assertEqual(work, expected)
            self.assertEqual(sum(work), 36)
            # Each source sends each needed position at most once to its peer.
            cross = [sum(any(k <= q for q in positions[1 - src])
                         for k in positions[src]) * 128 for src in range(2)]
            self.assertEqual(sum(cross), traffic)
        self.assertEqual(2 * 4 * 128, 1024)

    def test_decode_ownership_and_cross_rank_communication(self):
        counts = [[sum((j // 4) % 2 == rank for j in range(n)) for rank in range(2)]
                  for n in (8, 9, 10, 11)]
        self.assertEqual(counts, [[4, 4], [5, 4], [6, 4], [7, 4]])
        self.assertEqual([[n * 128 for n in pair] for pair in counts],
                         [[512, 512], [640, 512], [768, 512], [896, 512]])
        self.assertEqual(2 * 4 * 128, 1024)  # two allocated blocks at Rank 0
        q = 4 * 16 * 2
        m = 4 * 4
        ell_z = 4 * (1 + 16) * 4
        self.assertEqual((q, m, ell_z), (128, 16, 272))
        self.assertEqual(m + ell_z, 288)
        self.assertEqual(q + m + ell_z, 416)
        self.assertEqual(2 * (m + ell_z), 576)

    def test_softmax_partial_and_global_merge(self):
        self.assertAlmostEqual(merge([partial([0], [0]), partial([math.log(3)], [4])]), 3)
        a = partial([17, 16], [2, 4])
        b = partial([18, 17], [6, 8])
        self.assertAlmostEqual(merge([a, b]), 5.46211715726001)
        self.assertAlmostEqual((a[2] / a[1] + b[2] / b[1]) / 2, 4.53788284273999)
        self.assertIsNone(merge([None, None]))
        self.assertEqual(merge([None, partial([2], [5])]), 5)
        rng = random.Random(42)
        for _ in range(256):
            scores = [rng.uniform(-100, 100) for _ in range(rng.randint(1, 30))]
            values = [rng.uniform(-10, 10) for _ in scores]
            cut = rng.randint(0, len(scores))
            expected = merge([partial(scores, values)])
            actual = merge([partial(scores[:cut], values[:cut]),
                            partial(scores[cut:], values[cut:])])
            self.assertAlmostEqual(actual, expected, places=11)


if __name__ == "__main__":
    unittest.main()
