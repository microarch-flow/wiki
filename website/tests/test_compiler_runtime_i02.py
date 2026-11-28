"""Verify I02's page and conditional pipeline/placement teaching calculations."""

import unittest

import test_compiler_runtime_guides as guides


def finish_times(stage_lengths, microbatches):
    """Forward-only pipeline: independent microbatches, sufficient buffers."""
    end = [[0] * len(stage_lengths) for _ in range(microbatches)]
    for i in range(microbatches):
        for p, duration in enumerate(stage_lengths):
            end[i][p] = max(end[i - 1][p] if i else 0,
                            end[i][p - 1] if p else 0) + duration
    return end


class I02Tests(unittest.TestCase):
    def test_navigation_search_and_figures(self):
        route = "09-distributed-execution"
        slug = "i02-pipeline-and-data-parallelism"
        guides.CompilerRuntimeGuideTests()._check_article(
            route, "分布式执行与通信编排", slug,
            "模型太大需要多张卡，还是请求太多需要多个副本？",
            ("i02-placement.svg", "i02-pipeline-timeline.svg", "i02-rank-grid.svg"),
        )
        previous = guides.SITE / guides.PREFIX / route / "i01-tensor-parallelism/index.html"
        self.assertIn(f"../{slug}/", guides.GuideContent(previous.read_text()).links)

    def test_pipeline_fill_and_drain(self):
        self.assertEqual(finish_times([1, 1], 3), [[1, 2], [2, 3], [3, 4]])
        self.assertEqual([row[-1] for row in finish_times([1, 2], 3)], [3, 5, 7])
        self.assertEqual(3 * 2 / (2 * 4), 0.75)
        for p in range(1, 9):
            for m in range(1, 33):
                end = finish_times([1] * p, m)
                self.assertEqual(end[-1][-1], m + p - 1)
                self.assertEqual(end[0][-1], p)
        # DP2 replicas independently process one job in two time units.
        self.assertEqual(2 / 2, 1)

    def test_weight_activation_kv_and_capacity(self):
        weight = 4 * 64
        self.assertEqual(weight, 256)
        self.assertLessEqual(weight // 2, 160)
        self.assertGreater(weight, 160)
        kv_layer = 2 * 2 * 16 * 2
        self.assertEqual(kv_layer, 128)
        self.assertEqual([2 * n * kv_layer for n in (8, 9, 10, 11)],
                         [2048, 2304, 2560, 2816])
        activation = [n * 64 * 2 for n in (8, 1, 1, 1)]
        self.assertEqual(activation, [1024, 128, 128, 128])
        self.assertEqual(sum(activation), 1408)
        self.assertEqual(2 * (24 - 12 - 4), 16)
        self.assertEqual(min((24 - 6 - 4) * 2 for _ in range(2)), 28)
        self.assertEqual(8 * 2 * (kv_layer // 2), 1024)
        # TP4 places each of the two KV heads on two ranks; not four unique shards.
        self.assertEqual(8 * 2 * (2 * 16 * 2), 1024)
        self.assertEqual(2 * 512, 1024)
        self.assertEqual(2 * 1024, 2048)

    def test_independent_device_grid(self):
        rank = lambda d, p, t: ((d * 2) + p) * 2 + t
        tp = [[rank(d, p, t) for t in range(2)] for d in range(2) for p in range(2)]
        pp = [[rank(d, p, t) for p in range(2)] for d in range(2) for t in range(2)]
        dp = [[rank(d, p, t) for d in range(2)] for p in range(2) for t in range(2)]
        self.assertEqual(tp, [[0, 1], [2, 3], [4, 5], [6, 7]])
        self.assertEqual(pp, [[0, 2], [1, 3], [4, 6], [5, 7]])
        self.assertEqual(dp, [[0, 4], [1, 5], [2, 6], [3, 7]])
        self.assertEqual(sorted({r for g in tp for r in g}), list(range(8)))


if __name__ == "__main__":
    unittest.main()
