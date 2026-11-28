"""Check I01's published entry and exact two-rank teaching model."""

import unittest

import test_compiler_runtime_guides as guides


def matmul(x, w):
    return [[sum(a * b for a, b in zip(row, col))
             for col in zip(*w)] for row in x]


def add(a, b):
    return [[v + w for v, w in zip(row_a, row_b)]
            for row_a, row_b in zip(a, b)]


class I01Tests(unittest.TestCase):
    def test_navigation_search_and_figures(self):
        guides.CompilerRuntimeGuideTests()._check_article(
            "09-distributed-execution", "分布式执行与通信编排",
            "i01-tensor-parallelism", "同一次矩阵乘法分给两张卡，哪些数据必须交换？",
            ("i01-column-sharding.svg", "i01-reduction-sharding.svg",
             "i01-collective-dependency.svg"),
        )

    def test_matmul_shards_and_communication(self):
        x = [[2, 1, 3, 4], [1, 2, 1, 2]]
        w = [[3, 1], [5, 2], [2, 3], [1, 4]]
        y = matmul(x, w)
        self.assertEqual(y, [[21, 29], [17, 16]])
        col = [matmul(x, [[r[j]] for r in w]) for j in range(2)]
        self.assertEqual(col, [[[21], [17]], [[29], [16]]])
        self.assertEqual([a + b for a, b in zip(*col)], y)
        part = [matmul([r[k:k + 2] for r in x], w[k:k + 2]) for k in (0, 2)]
        self.assertEqual(part, [[[11, 4], [13, 5]], [[10, 25], [4, 11]]])
        self.assertEqual(add(*part), y)
        # ReduceScatter: rank 0 owns row 0; rank 1 owns row 1.
        scattered = [add([part[0][i]], [part[1][i]])[0] for i in range(2)]
        self.assertEqual(scattered, y)
        self.assertLessEqual(4 * 15 * 15, 65535)
        self.assertEqual(8 + 8 + 8, 24)
        self.assertEqual(8 + 4 + 4, 16)
        self.assertEqual(4 + 4 + 8, 16)
        # Compact u16 payloads: sends per rank and system sends.
        col_bytes = len(col[0]) * len(col[0][0]) * 2
        partial_bytes = len(part[0]) * len(part[0][0]) * 2
        scatter_bytes = len(scattered[0]) * 2
        self.assertEqual((col_bytes, 2 * col_bytes), (4, 8))
        self.assertEqual((partial_bytes, 2 * partial_bytes), (8, 16))
        self.assertEqual((scatter_bytes, 2 * scatter_bytes), (4, 8))
        self.assertEqual(scatter_bytes + col_bytes, partial_bytes)
        # A second independent elementwise activation and row-sharded linear.
        v = [[1, 2], [3, 4]]
        local = [matmul(col[j], [v[j]]) for j in range(2)]
        self.assertEqual(add(*local), matmul(y, v))
        self.assertEqual(128 * 4096 * 2, 2**20)
        self.assertEqual(max(4, 4) + 3, 7)
        self.assertEqual(max(4, 6) + 3, 9)


if __name__ == "__main__":
    unittest.main()
