"""Verify K01's publication and recompute its teaching metrics exactly.

The resource schedules and request events are constructed inputs, not device or
serving benchmark results. Keep their verification separate from site checks.
"""

from collections import defaultdict
from fractions import Fraction
from itertools import accumulate
from math import ceil
import unittest

import test_compiler_runtime_guides as guides


def schedule(tasks):
    """Place each task after its predecessors and prior work on its resource."""
    available = defaultdict(int)
    intervals = {}
    busy = defaultdict(int)
    for name, resource, duration, dependencies in tasks:
        start = max([available[resource], *(intervals[d][1] for d in dependencies)])
        end = start + duration
        intervals[name] = (start, end)
        available[resource] = end
        busy[resource] += duration
    return intervals, dict(busy)


def latencies(arrival, times):
    """Observe individual token events on one clock, not chunk timestamps."""
    gaps = [b - a for a, b in zip(times, times[1:])]
    return (times[0] - arrival, times[-1] - arrival, gaps,
            Fraction(sum(gaps), len(gaps)) if gaps else None)


def emit_times(rounds):
    """Use H01's assumed round durations and the output events at each end."""
    outputs = defaultdict(list)
    for end, (_, requests) in zip(accumulate(duration for duration, _ in rounds), rounds):
        for name in requests:
            outputs[name].append(end)
    return dict(outputs)


class K01Tests(unittest.TestCase):
    arrivals = {"A": 0, "B": 0, "C": 14}
    inputs = {"A": 8, "B": 3, "C": 6}
    fixed = [(12, "AB"), (4, "AB"), (3, "A"), (3, "A"),
             (9, "C"), (3, "C"), (3, "C")]
    continuous = [(12, "AB"), (4, "AB"), (10, "AC"), (4, "AC"), (3, "C")]

    def test_navigation_search_and_figures(self):
        guides.CompilerRuntimeGuideTests()._check_article(
            "11-performance", "性能分析、建模与验证", "k01-performance-metrics",
            "怎样定义可以公平比较的延迟和吞吐量？",
            ("k01-request-timeline.svg", "k01-async-boundaries.svg"),
        )

    def test_compiler_example(self):
        # C03/C05: X is local, W is already arranged; measure from L0 to S1.
        x_rows, reduction, w_columns = 2, 4, 2
        macs = x_rows * reduction * w_columns
        self.assertEqual(macs, 16)
        self.assertEqual((reduction * w_columns, x_rows * w_columns * 2), (8, 8))
        l0 = ("L0", "DMA", 2, [])
        c0 = ("C0", "compute", 4, ["L0"])
        s0 = ("S0", "DMA", 2, ["C0"])
        l1 = ("L1", "DMA", 2, [])
        c1 = ("C1", "compute", 4, ["L1"])
        s1 = ("S1", "DMA", 2, ["C1"])
        serial, serial_busy = schedule([l0, c0, s0, l1, c1, s1])
        overlap, overlap_busy = schedule([l0, c0, l1, s0, c1, s1])
        self.assertEqual((serial["S1"][1], overlap["S1"][1]), (16, 12))
        self.assertEqual(serial_busy, overlap_busy)
        self.assertEqual(overlap_busy, {"DMA": 8, "compute": 8})
        self.assertEqual(Fraction(macs, serial["S1"][1]), 1)
        self.assertEqual(Fraction(macs, overlap["S1"][1]), Fraction(4, 3))
        self.assertEqual(Fraction(serial["S1"][1], overlap["S1"][1]), Fraction(4, 3))

    def test_device_schedule_and_utilization(self):
        # F02: two independent three-element int32 vectors, both ready at t=0.
        # Each group moves three 12-byte vectors (both inputs and the result).
        self.assertEqual(2 * 3 * 3 * 4, 72)
        a1 = ("LA1", "DMA", 2, [])
        b1 = ("LB1", "DMA", 2, [])
        c1 = ("C1", "compute", 3, ["LA1", "LB1"])
        w1 = ("W1", "DMA", 2, ["C1"])
        a2 = ("LA2", "DMA", 2, [])
        b2 = ("LB2", "DMA", 2, [])
        c2 = ("C2", "compute", 3, ["LA2", "LB2"])
        w2 = ("W2", "DMA", 2, ["C2"])
        serial, serial_busy = schedule([a1, b1, c1, w1, a2, b2, c2, w2])
        pipeline, pipeline_busy = schedule([a1, b1, c1, a2, b2, w1, c2, w2])
        self.assertEqual([serial[n][1] for n in ("W1", "W2")], [9, 18])
        self.assertEqual([pipeline[n][1] for n in ("W1", "W2")], [10, 13])
        self.assertEqual(pipeline, {"LA1": (0, 2), "LB1": (2, 4), "C1": (4, 7),
                                   "LA2": (4, 6), "LB2": (6, 8), "W1": (8, 10),
                                   "C2": (8, 11), "W2": (11, 13)})
        self.assertEqual(serial_busy, pipeline_busy)
        self.assertEqual(pipeline_busy, {"DMA": 12, "compute": 6})
        self.assertEqual([Fraction(2, serial["W2"][1]), Fraction(2, pipeline["W2"][1])],
                         [Fraction(1, 9), Fraction(2, 13)])
        self.assertEqual([Fraction(serial_busy[r], serial["W2"][1])
                          for r in ("DMA", "compute")], [Fraction(2, 3), Fraction(1, 3)])
        self.assertEqual([Fraction(pipeline_busy[r], pipeline["W2"][1])
                          for r in ("DMA", "compute")], [Fraction(12, 13), Fraction(6, 13)])

    def test_token_events_and_delay_metrics(self):
        fixed = emit_times(self.fixed)
        continuous = emit_times(self.continuous)
        self.assertEqual(fixed, {"A": [12, 16, 19, 22], "B": [12, 16], "C": [31, 34, 37]})
        self.assertEqual(continuous, {"A": [12, 16, 26, 30], "B": [12, 16], "C": [26, 30, 33]})
        self.assertEqual([latencies(self.arrivals[r], fixed[r]) for r in "ABC"],
                         [(12, 22, [4, 3, 3], Fraction(10, 3)),
                          (12, 16, [4], Fraction(4)), (17, 23, [3, 3], Fraction(3))])
        self.assertEqual([latencies(self.arrivals[r], continuous[r]) for r in "ABC"],
                         [(12, 30, [4, 10, 4], Fraction(6)),
                          (12, 16, [4], Fraction(4)), (12, 19, [4, 3], Fraction(7, 2))])
        for scenario, request_average, gap_average in ((fixed, Fraction(31, 9), Fraction(10, 3)),
                                                       (continuous, Fraction(9, 2), Fraction(29, 6))):
            metrics = [latencies(self.arrivals[r], scenario[r]) for r in "ABC"]
            self.assertEqual(sum(m[3] for m in metrics) / 3, request_average)
            all_gaps = [gap for m in metrics for gap in m[2]]
            self.assertEqual(Fraction(sum(all_gaps), len(all_gaps)), gap_average)
            for r, (ttft, e2e, gaps, tpot) in zip("ABC", metrics):
                self.assertEqual(len(gaps), len(scenario[r]) - 1)
                self.assertEqual(e2e, ttft + len(gaps) * tpot)
        self.assertEqual(latencies(0, [100, 120, 160]), (100, 160, [20, 40], Fraction(30)))
        self.assertEqual(latencies(9, [12]), (3, 3, [], None))

    def test_window_throughput_and_goodput(self):
        fixed = emit_times(self.fixed)
        continuous = emit_times(self.continuous)
        for events, window, pass_17_4, pass_15_5 in ((fixed, 37, "ABC", "AB"),
                                                    (continuous, 33, "BC", "BC")):
            elapsed = Fraction(max(times[-1] for times in events.values()) - min(self.arrivals.values()), 1000)
            self.assertEqual(elapsed, Fraction(window, 1000))
            n_requests = len(events)
            n_outputs = sum(map(len, events.values()))
            n_inputs = sum(self.inputs.values())
            self.assertEqual((n_requests, n_outputs, n_inputs), (3, 9, 17))
            self.assertEqual((n_requests / elapsed, n_outputs / elapsed, (n_inputs + n_outputs) / elapsed),
                             (Fraction(3000, window), Fraction(9000, window), Fraction(26000, window)))
            for ttft_limit, tpot_limit, expected in ((17, 4, pass_17_4), (15, 5, pass_15_5)):
                passed = []
                for r, times in events.items():
                    ttft, _, _, tpot = latencies(self.arrivals[r], times)
                    if ttft <= ttft_limit and tpot <= tpot_limit:  # all succeed, all output >1 token
                        passed.append(r)
                self.assertEqual(passed, list(expected))
                self.assertEqual(Fraction(len(passed), n_requests), Fraction(len(expected), 3))
                request_goodput = len(passed) / elapsed
                output_goodput = sum(len(events[r]) for r in passed) / elapsed
                # Derive token counts from request identities separately from arrival ordering.
                outputs = {"A": 4, "B": 2, "C": 3}
                self.assertEqual(request_goodput, Fraction(1000 * len(expected), window))
                self.assertEqual(output_goodput, Fraction(1000 * sum(outputs[r] for r in expected), window))
        self.assertGreater(Fraction(9000, 33), Fraction(9000, 37))
        self.assertLess(Fraction(2000, 33), Fraction(3000, 37))  # thresholds 17/4
        self.assertGreater(Fraction(2000, 33), Fraction(2000, 37))  # thresholds 15/5
        self.assertLess(Fraction(5000, 33), Fraction(6000, 37))  # output-token goodput, 15/5

    def test_tail_latency_and_joint_slo(self):
        all_requests = set(range(100))
        ttft_pass = all_requests - {0}
        tpot_pass = all_requests - {99}
        self.assertEqual(Fraction(len(ttft_pass), len(all_requests)), Fraction(99, 100))
        self.assertEqual(Fraction(len(tpot_pass), len(all_requests)), Fraction(99, 100))
        self.assertEqual(Fraction(len(ttft_pass & tpot_pass), len(all_requests)), Fraction(98, 100))
        samples = sorted([25] * 999 + [570])
        rank = ceil(Fraction(99, 100) * len(samples))
        self.assertEqual(rank, 990)
        self.assertEqual(samples[rank - 1], 25)
        self.assertEqual(samples[-1], 570)


if __name__ == "__main__":
    unittest.main()
