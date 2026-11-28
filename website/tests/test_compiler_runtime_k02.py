"""K02's reproducible teaching checks: these are not production verifier tests.

All injected failures here affect an ordinary Python state model, never a real
runtime, compiler, or device. Exact integer examples model a subset of the
B03 contract; numerical examples declare their own tolerance/rounding rules.
"""

from fractions import Fraction
import math
import struct
import unittest

import test_compiler_runtime_guides as guides


def check_shapes(x, w, bias):
    """Example's declared dynamic interface [M,2], [2,2], [2], M in [2,4]."""
    if not (2 <= len(x) <= 4 and all(len(row) == 2 for row in x)
            and len(w) == 2 and all(len(row) == 2 for row in w) and len(bias) == 2):
        raise ValueError("shape outside teaching contract")


def reference(x, w, bias):
    check_shapes(x, w, bias)
    p = [[sum(a * b for a, b in zip(row, col)) for col in zip(*w)] for row in x]
    z = [[v + b for v, b in zip(row, bias)] for row in p]
    y = [[max(0, v) for v in row] for row in z]
    return p, z, y


def fused(x, w, bias, *, wrong_index=False):
    check_shapes(x, w, bias)
    return [[max(0, sum(x[i][k] * w[k][j] for k in range(2))
                     + bias[i if wrong_index else j])
             for j in range(2)] for i in range(len(x))]


def fp32(value):
    return struct.unpack("!f", struct.pack("!f", value))[0]


def close_to_reference(actual, expected, *, atol=0.001, rtol=0.001, signed_zero=False):
    """Example policy: NaN forbidden; infinities equal only with same sign."""
    if math.isnan(actual) or math.isnan(expected):
        return False
    if math.isinf(actual) or math.isinf(expected):
        return actual == expected
    if signed_zero and actual == expected == 0:
        return math.copysign(1, actual) == math.copysign(1, expected)
    return abs(actual - expected) <= atol + rtol * abs(expected)


class TeachingSlot:
    """An exclusive allocation with an explicit retirement/last-access rule."""

    def __init__(self):
        self.generation = 0
        self.owner = None
        self.active = set()
        self.retired = False
        self.returned = 0

    def allocate(self, owner, accesses):
        if self.owner is not None:
            raise RuntimeError("buffer is still owned")
        self.generation += 1
        self.owner = owner
        self.active = set(accesses)
        self.retired = False
        return self.generation

    def retire(self, generation):
        """Request cancellation/release; cannot declare outstanding accesses done."""
        if generation == self.generation and self.owner is not None:
            self.retired = True
            self._try_return()

    def access_ended(self, generation, access):
        """Only an explicit notification of quiescence ends an access."""
        if generation == self.generation and self.owner is not None:
            self.active.discard(access)
            self._try_return()

    def _try_return(self):
        if self.retired and not self.active:
            self.owner = None
            self.returned += 1


def can_execute(name, dependencies, status):
    """Actual execution readiness, not a prohibition on dependency-bearing submission."""
    return all(status.get(predecessor) == "success" for predecessor in dependencies[name])


class K02Tests(unittest.TestCase):
    x = [[1, 2], [-1, 0]]
    w = [[1, 2], [3, -1]]
    bias = [1, -2]

    def test_navigation_search_and_figures(self):
        route = "11-performance"
        slug = "k02-correctness-and-validation"
        guides.CompilerRuntimeGuideTests()._check_article(
            route, "性能分析、建模与验证", slug,
            "怎样验证编译优化和运行时实现仍然符合预期？",
            ("k02-structural-vs-semantic.svg", "k02-buffer-invariant.svg"),
        )
        previous = guides.SITE / guides.PREFIX / route / "k01-performance-metrics/index.html"
        self.assertIn(f"../{slug}/", guides.GuideContent(previous.read_text()).links)

    def test_reference_and_indexing_error(self):
        p, z, y = reference(self.x, self.w, self.bias)
        self.assertEqual(p, [[7, 0], [-1, -2]])
        self.assertEqual(z, [[8, -2], [0, -4]])
        self.assertEqual(y, [[8, 0], [0, 0]])
        self.assertEqual(fused(self.x, self.w, self.bias), y)
        wrong = fused(self.x, self.w, self.bias, wrong_index=True)
        self.assertEqual(wrong, [[8, 1], [0, 0]])
        self.assertEqual([len(row) for row in wrong], [len(row) for row in y])
        self.assertNotEqual(wrong, y)

    def test_input_boundaries_and_metamorphic_property(self):
        extended = self.x + [[0, 0]]
        expected = reference(extended, self.w, self.bias)[2]
        self.assertEqual(expected, [[8, 0], [0, 0], [1, 0]])
        self.assertEqual(fused(extended, self.w, self.bias), expected)
        with self.assertRaises(IndexError):
            fused(extended, self.w, self.bias, wrong_index=True)
        # A passing test with a symmetric bias does not establish equivalence.
        symmetric = [1, 1]
        self.assertEqual(fused(self.x, self.w, symmetric),
                         fused(self.x, self.w, symmetric, wrong_index=True))
        x_permuted = self.x[::-1]
        self.assertEqual(fused(x_permuted, self.w, self.bias),
                         fused(self.x, self.w, self.bias)[::-1])
        self.assertNotEqual(fused(x_permuted, self.w, self.bias, wrong_index=True),
                            fused(self.x, self.w, self.bias, wrong_index=True)[::-1])
        cases = [self.x, extended, extended + [[3, -2]]]
        for x in cases:
            self.assertEqual(fused(x, self.w, self.bias), reference(x, self.w, self.bias)[2])
        for x, w, bias in (([[1, 2]], self.w, self.bias), (self.x + [[0, 0]] * 3, self.w, self.bias),
                           ([[1, 2, 3], [-1, 0, 1]], self.w, self.bias),
                           (self.x, [[1, 2]], self.bias), (self.x, self.w, [1])):
            # Declared teaching contract, rather than undocumented input acceptance.
            with self.assertRaises(ValueError):
                fused(x, w, bias)

    def test_numeric_semantics_and_tolerance(self):
        a = fp32(2**24)
        first = fp32(fp32(a + 1) - a)
        second = fp32(a + fp32(1-a))
        self.assertEqual((first, second), (0, 1))
        self.assertEqual(fp32(a + 1), a)
        self.assertEqual(fp32(a + 2), a + 2)

        def dequant_int4(x):
            scale = Fraction(1, 4)
            encoding = max(-8, min(7, round(x / scale)))
            return encoding * scale

        self.assertEqual(dequant_int4(Fraction(76, 100)), Fraction(3, 4))
        self.assertEqual(dequant_int4(2), Fraction(7, 4))
        x = [1, Fraction(1, 2), Fraction(3, 2), 2]
        w = [Fraction(3, 4), Fraction(5, 4), 1, Fraction(1, 2)]
        ref = sum(a * b for a, b in zip(x, w))
        self.assertEqual(ref, Fraction(31, 8))
        self.assertEqual(11 * Fraction(1, 8) + 10 * Fraction(1, 4), ref)
        self.assertEqual((11+10) * Fraction(1, 8), Fraction(21, 8))
        atol = rtol = Fraction(1, 1000)
        limit = atol + rtol * abs(ref)
        self.assertEqual(limit, Fraction(39, 8000))  # 0.004875
        self.assertTrue(close_to_reference(Fraction("3.876"), ref, atol=atol, rtol=rtol))
        self.assertFalse(close_to_reference(Fraction("3.900"), ref, atol=atol, rtol=rtol))
        self.assertTrue(close_to_reference(Fraction(1, 2000), 0, atol=atol, rtol=rtol))
        self.assertFalse(close_to_reference(Fraction(2, 1000), 0, atol=atol, rtol=rtol))
        self.assertFalse(close_to_reference(math.nan, math.nan))
        self.assertTrue(close_to_reference(math.inf, math.inf))
        self.assertFalse(close_to_reference(-math.inf, math.inf))
        self.assertFalse(close_to_reference(0, math.inf))
        self.assertTrue(close_to_reference(-0.0, 0.0))
        self.assertFalse(close_to_reference(-0.0, 0.0, signed_zero=True))

    def test_resource_reuse_schedule(self):
        # F03 assumes tasks may access the whole shared buffer until completion.
        c1 = (4, 7)
        w1 = (8, 10)
        unsafe_c2 = (8, 11)
        start = max(8, c1[1], w1[1])
        c2 = (start, start + 3)
        w2_start = max(c2[1], w1[1])
        w2 = (w2_start, w2_start + 2)
        self.assertLess(c1[1], w1[0])
        self.assertLess(max(w1[0], unsafe_c2[0]), min(w1[1], unsafe_c2[1]))
        self.assertEqual((c2, w2), ((10, 13), (13, 15)))
        self.assertLessEqual(w1[1], c2[0])
        # One possible ordering inside the conflicting interval: C2 writes the
        # first element before W1 reads it. The exact hardware ordering is not asserted.
        y1 = [a + b for a, b in zip([2, 1, 4], [3, 4, 2])]
        y2 = [a + b for a, b in zip([1, 4, 1], [2, 6, 3])]
        self.assertEqual((y1, y2), ([5, 5, 6], [3, 10, 4]))
        slot = y1.copy()
        slot[0] = y2[0]
        bad_host_first = slot[0]
        self.assertEqual((y1[0], bad_host_first), (5, 3))
        self.assertNotEqual(y1, slot)

    def test_failure_timeout_and_repeated_completion(self):
        # Inject failure into an isolated model. Successful result readiness is
        # distinct from an ended access, a timeout, or a cancellation request.
        dependencies = {"C": {"LA", "LB"}, "W": {"C"}}
        status = {"LA": "success", "LB": "failed"}
        self.assertFalse(can_execute("C", dependencies, status))
        self.assertFalse(can_execute("W", dependencies, status))
        # For this model C may only start actual execution after both inputs have succeeded.
        status["LB"] = "success"
        self.assertTrue(can_execute("C", dependencies, status))
        status["C"] = "running"
        self.assertFalse(can_execute("W", dependencies, status))
        status["C"] = "success"
        self.assertTrue(can_execute("W", dependencies, status))

        slot = TeachingSlot()
        old = slot.allocate("request-1", {"C1", "W1"})
        slot.access_ended(old, "C1")
        slot.retire(old)  # caller timed out; W1 has not relinquished the access
        self.assertEqual(slot.owner, "request-1")
        self.assertEqual(slot.active, {"W1"})
        self.assertEqual(slot.returned, 0)
        with self.assertRaises(RuntimeError):
            slot.allocate("request-2", {"C2", "W2"})
        slot.access_ended(old, "W1")
        self.assertIsNone(slot.owner)
        self.assertEqual(slot.returned, 1)
        slot.access_ended(old, "W1")  # repeated completion before next allocation
        self.assertEqual(slot.returned, 1)
        new = slot.allocate("request-2", {"C2", "W2"})
        self.assertNotEqual(new, old)
        slot.retire(new)
        slot.access_ended(old, "W1")  # late completion of old generation
        slot.retire(old)
        self.assertEqual(slot.owner, "request-2")
        self.assertEqual(slot.active, {"C2", "W2"})
        slot.access_ended(new, "C2")
        self.assertEqual(slot.returned, 1)
        slot.access_ended(new, "W2")
        slot.access_ended(new, "W2")
        self.assertEqual(slot.returned, 2)
        self.assertIsNone(slot.owner)

    def test_generation_state_invariant(self):
        # G02/H01: ordinary autoregression only, full prefill, no early stopping
        # or prefix reuse/speculation. One model position per decode.
        prompts = {"A": 8, "B": 3, "C": 6}
        limits = {"A": 4, "B": 2, "C": 3}
        calculated = {r: 0 for r in prompts}
        emitted = {r: 0 for r in prompts}
        # H01 continuous batch: first participation does full Prefill.
        rows = []
        for batch in ("AB", "AB", "AC", "AC", "C"):
            for r in batch:
                self.assertLess(emitted[r], limits[r])
                calculated[r] += 1 if emitted[r] else prompts[r]
                emitted[r] += 1
                known = prompts[r] + emitted[r]
                self.assertEqual(calculated[r], known - 1)
            rows.append(tuple((emitted[r], calculated[r]) for r in "ABC"))
        self.assertEqual(rows, [((1, 8), (1, 3), (0, 0)),
                                ((2, 9), (2, 4), (0, 0)),
                                ((3, 10), (2, 4), (1, 6)),
                                ((4, 11), (2, 4), (2, 7)),
                                ((4, 11), (2, 4), (3, 8))])
        self.assertEqual(emitted, limits)
        self.assertEqual(sum(calculated.values()), 23)


    def test_cancel_waits_for_device_and_transfer(self):
        # Old request lifetime example: other slots are occupied. Even after
        # cancellation, A's block has two independent in-flight users.
        slot = TeachingSlot()
        generation = slot.allocate("A", {"device", "transfer"})
        slot.retire(generation)
        slot.retire(generation)
        with self.assertRaises(RuntimeError):
            slot.allocate("B", {"device"})
        slot.access_ended(generation, "device")
        with self.assertRaises(RuntimeError):
            slot.allocate("B", {"device"})
        slot.access_ended(generation, "transfer")
        next_generation = slot.allocate("B", {"device"})
        slot.access_ended(generation, "transfer")
        self.assertEqual(slot.owner, "B")
        self.assertNotEqual(next_generation, generation)
        self.assertEqual(slot.returned, 1)

    def test_speculative_valid_prefix_not_temporary_length(self):
        # G09 request A: 8 prompt positions, one formal token already known.
        # Verify processes y1, d2, d3. Rejecting a candidate discards its KV
        # logically; a newly sampled replacement is not computed yet.
        temporary = ["p" + str(i) for i in range(1, 9)] + ["y1", "d2", "d3"]
        cases = [(["r2"], 9), (["d2", "r3"], 10), (["d2", "d3", "y4"], 11)]
        for new, n_valid in cases:
            accepted_history = temporary[:9] + new[:-1]
            self.assertEqual(temporary[:n_valid], accepted_history)
            self.assertEqual(len(accepted_history), 8 + 1 + len(new) - 1)
        self.assertEqual(cases[1], (["d2", "r3"], 10))
        self.assertNotIn("d3", temporary[:cases[1][1]])


if __name__ == "__main__":
    unittest.main()
