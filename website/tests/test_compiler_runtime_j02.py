"""Check J02's public page and the cancellation/retirement teaching model.

The model below orders illustrative events and accounts for one layer's KV
pool. It does not simulate GPU execution or claim a measured cancellation time.
"""

from math import ceil
import unittest
from urllib.parse import urljoin, urlsplit

import test_compiler_runtime_guides as guides


class Pool:
    """Track logical owners separately from the accesses already submitted."""

    def __init__(self, block_count):
        self.owners = {f"b{i}": set() for i in range(block_count)}
        self.accesses = {}

    def reference(self, request, blocks):
        for block in blocks:
            self.owners[block].add(request)

    def submit(self, work, request, blocks):
        assert work not in self.accesses
        assert all(request in self.owners[block] for block in blocks)
        self.accesses[work] = set(blocks)

    def forget(self, request):
        for owners in self.owners.values():
            owners.discard(request)

    def complete(self, work):
        del self.accesses[work]

    def free_blocks(self):
        busy = set().union(*self.accesses.values())
        return [block for block, owners in self.owners.items()
                if not owners and block not in busy]

    def allocate(self, request):
        free = self.free_blocks()
        if not free:
            return None
        block = free[0]
        self.reference(request, [block])
        return block


class J02Tests(unittest.TestCase):
    def test_navigation_search_and_figures(self):
        route = "10-serving"
        slug = "j02-request-and-resource-lifecycle"
        guides.CompilerRuntimeGuideTests()._check_article(
            route, "推理服务系统", slug,
            "用户取消请求之后，为什么不能立即回收资源？",
            ("j02-cancel-timeline.svg", "j02-block-lifecycle.svg"),
        )
        previous = guides.SITE / guides.PREFIX / route / "j01-request-routing/index.html"
        self.assertIn(f"../{slug}/", guides.GuideContent(previous.read_text()).links)
        relative = f"{guides.PREFIX}{route}/{slug}/"
        body = guides.GuideContent((guides.SITE / relative / "index.html").read_text())
        linked_paths = {urlsplit(urljoin("https://site.invalid/" + relative, link)).path
                        for link in body.links}
        for dependency in ("10-serving/j01-request-routing",
                           "06-execution-runtime/f03-runtime-buffer-management",
                           "07-model-execution/g06-prefix-cache"):
            self.assertIn(f"/{guides.PREFIX}{dependency}/", linked_paths)

    def test_cancel_keeps_inflight_blocks_until_last_access(self):
        # The first mixed round has computed A's nine and C's six KV positions,
        # with two and one committed output tokens respectively. The first four
        # positions refer to the same immutable physical block.
        positions = {"A": 9, "C": 6}
        tokens = {"A": 2, "C": 1}
        a = ["b0", "b1", "b2"]
        c = ["b0", "b3"]
        self.assertEqual([ceil(positions[r] / 4) for r in ("A", "C")],
                         [len(a), len(c)])
        self.assertEqual(len(set(a) | set(c)), 4)
        self.assertEqual((4 * 128, 4 * 4 * 128), (512, 2048))

        pool = Pool(4)
        pool.reference("A", a)
        pool.reference("C", c)
        self.assertEqual(pool.owners["b0"], {"A", "C"})
        self.assertEqual(pool.free_blocks(), [])

        # A and C have submitted their next Decode. The new positions fit the
        # already allocated tail blocks. These accesses keep the blocks live.
        targets = {r: (n + 1) for r, n in positions.items()}
        self.assertEqual([a[(targets["A"] - 1) // 4], c[(targets["C"] - 1) // 4]],
                         ["b2", "b3"])
        pool.submit("A-step", "A", a)
        pool.submit("C-step", "C", c)

        # A service-layer cancellation freezes C's output commit. Once observed
        # by the scheduler, C's logical references can be removed; neither act
        # proves completion of the submitted accesses.
        canceled = {"C"}
        pool.forget("C")
        pool.forget("C")  # repeated cancellation has no second release effect
        self.assertEqual(pool.owners["b0"], {"A"})
        self.assertFalse(pool.owners["b3"])
        self.assertIn("b3", pool.accesses["C-step"])
        self.assertEqual(pool.free_blocks(), [])
        self.assertIsNone(pool.allocate("D"))

        # At last access, A can accept the mixed-round result. C's result is
        # discarded even if execution calculated position seven successfully.
        for request in ("A", "C"):
            pool.complete(f"{request}-step")
            if request not in canceled:
                positions[request] = targets[request]
                tokens[request] += 1
        self.assertEqual((positions["A"], tokens["A"]), (10, 3))
        self.assertEqual((positions["C"], tokens["C"]), (6, 1))
        self.assertEqual(targets["C"], 7)  # physical work, not accepted new state
        self.assertEqual(pool.free_blocks(), ["b3"])
        self.assertEqual(len(pool.free_blocks()) * 4 * 128, 512)
        self.assertEqual(pool.allocate("D"), "b3")
        self.assertEqual(pool.free_blocks(), [])
        self.assertEqual(len(pool.owners) * 4 * 128, 2048)  # unchanged pool reservation
        self.assertEqual(pool.owners["b0"], {"A"})

    def test_device_completion_is_not_completion_of_a_separate_transfer(self):
        pool = Pool(4)
        pool.reference("A", ["b0", "b1", "b2"])
        pool.reference("C", ["b0", "b3"])
        pool.submit("C-step", "C", ["b0", "b3"])
        # In the additional variant, a legal transfer also holds b3. This only
        # accounts for lifetime, not transfer layout or producer ordering.
        pool.submit("C-copy", "C", ["b3"])
        pool.forget("C")
        pool.complete("C-step")
        self.assertIsNone(pool.allocate("D"))
        pool.complete("C-copy")
        self.assertEqual(pool.allocate("D"), "b3")
        self.assertEqual(pool.owners["b0"], {"A"})


if __name__ == "__main__":
    unittest.main()
