"""Verify K03's publication and recompute its hypothetical profiling traces.

These are deterministic teaching examples, not measurements on any device or
inference service. The interventions vary only the stated model parameter.
"""

from itertools import accumulate
import unittest

import test_compiler_runtime_guides as guides


def launch_trace(n, submit_interval, service_time):
    """Serial host submissions and one in-order, non-overlapping device stream."""
    previous_end = 0
    intervals = []
    for i in range(1, n + 1):
        ready = i * submit_interval
        start = max(ready, previous_end)
        end = start + service_time
        intervals.append((ready, start, end))
        previous_end = end
    return intervals


def idle_gaps(intervals):
    ends = [0] + [end for _, _, end in intervals[:-1]]
    return [start - previous for (_, start, _), previous in zip(intervals, ends)]


def request_events(slowdown, closed):
    """H01's three requests and rounds; a closed client sends C as B completes."""
    planned_c = 14
    output_rounds = [(12, "AB"), (4, "AB"), (10, "AC"), (4, "AC"), (3, "C")]
    ends = list(accumulate(duration * slowdown for duration, _ in output_rounds))
    outputs = {name: [] for name in "ABC"}
    for (_, emits), end in zip(output_rounds, ends):
        for name in emits:
            outputs[name].append(end)
    b_done = outputs["B"][-1]
    arrivals = {"A": 0, "B": 0, "C": b_done if closed else planned_c}
    # Both sequence slots remain occupied by A/B through round 2. C can
    # arrive during round 1 or 2, or at their boundary with round 3.
    # Assumption: zero notification/send/receive delay, and an arrival at
    # the boundary is observed before choosing the next round.
    assert 0 < arrivals["C"] <= b_done
    # Count requests outstanding after completions/arrivals at each event time.
    changes = {}
    for name, arrival in arrivals.items():
        changes[arrival] = changes.get(arrival, 0) + 1
        final = outputs[name][-1]
        changes[final] = changes.get(final, 0) - 1
    outstanding = list(accumulate(changes[time] for time in sorted(changes)))
    return ends, arrivals, outputs, max(outstanding)


def critical_schedule(c1_duration=3, c2_duration=3):
    """Calculate longest predecessor chains for a fixed resource order (F02)."""
    # Predecessors express both required data and the selected exclusive resource
    # service order. Each task can start as soon as all its predecessors finish.
    tasks = [
        ("LA1", 2, ()),
        ("LB1", 2, ("LA1",)),
        ("LA2", 2, ("LB1",)),
        ("LB2", 2, ("LA2",)),
        ("C1", c1_duration, ("LA1", "LB1")),
        ("W1", 2, ("C1", "LB2")),
        ("C2", c2_duration, ("LA2", "LB2", "C1")),
        ("W2", 2, ("C2", "W1")),
    ]
    timing = {}
    chains = {}
    for name, duration, dependencies in tasks:
        if dependencies:
            predecessor = max(dependencies, key=lambda p: timing[p][1])
            start = timing[predecessor][1]
            preceding_chain = chains[predecessor]
        else:
            start = 0
            preceding_chain = ()
        timing[name] = (start, start + duration)
        chains[name] = preceding_chain + (name,)
    return timing, chains


class K03Tests(unittest.TestCase):
    def test_navigation_search_and_figures(self):
        route = "11-performance"
        slug = "k03-benchmarking-and-profiling"
        guides.CompilerRuntimeGuideTests()._check_article(
            route, "性能分析、建模与验证", slug,
            "系统变慢了，怎样找到真正的瓶颈？",
            ("k03-launch-gaps.svg", "k03-load-arrivals.svg", "k03-critical-path.svg"),
        )
        previous = guides.SITE / guides.PREFIX / route / "k02-correctness-and-validation/index.html"
        self.assertIn(f"../{slug}/", guides.GuideContent(previous.read_text()).links)

    def test_submission_service_intervention(self):
        short = launch_trace(100, 3, 1)
        long = launch_trace(100, 3, 5)
        self.assertEqual([row[2] for row in short[:4]], [4, 7, 10, 13])
        self.assertEqual([row[2] for row in long[:4]], [8, 13, 18, 23])
        self.assertEqual((short[-1][2], long[-1][2]), (301, 503))
        self.assertEqual(idle_gaps(short), [3] + [2] * 99)
        self.assertEqual(idle_gaps(long), [3] + [0] * 99)
        for trace in (short, long):
            busy = sum(end - start for _, start, end in trace)
            self.assertEqual(busy + sum(idle_gaps(trace)), trace[-1][2])
        # Hold device service times fixed while reducing host submission time.
        short_after = launch_trace(100, 1, 1)
        long_after = launch_trace(100, 1, 5)
        self.assertEqual((short_after[-1][2], long_after[-1][2]), (101, 501))
        self.assertEqual(idle_gaps(short_after), [1] + [0] * 99)
        self.assertEqual(idle_gaps(long_after), [1] + [0] * 99)
        self.assertEqual((short[-1][2] - short_after[-1][2],
                          long[-1][2] - long_after[-1][2]), (200, 2))
        self.assertEqual([row[0] for row in short], [row[0] for row in long])
        self.assertEqual([row[0] for row in short_after], [row[0] for row in long_after])

    def test_open_and_closed_arrival_times(self):
        for slowdown, b_done, c_first, ttft_open, ttft_closed, delayed in (
                (1, 16, 26, 12, 10, 2), (2, 32, 52, 38, 20, 18)):
            open_ends, open_arrivals, open_outputs, open_max = request_events(slowdown, closed=False)
            closed_ends, closed_arrivals, closed_outputs, closed_max = request_events(slowdown, closed=True)
            self.assertEqual(open_ends, [12 * slowdown, 16 * slowdown, 26 * slowdown,
                                        30 * slowdown, 33 * slowdown])
            self.assertEqual(open_ends, closed_ends)
            self.assertEqual(open_outputs, closed_outputs)
            self.assertEqual(open_outputs["B"][-1], b_done)
            self.assertEqual(open_outputs["C"][0], c_first)
            self.assertEqual(open_arrivals, {"A": 0, "B": 0, "C": 14})
            self.assertEqual(closed_arrivals, {"A": 0, "B": 0, "C": b_done})
            self.assertEqual((open_max, closed_max), (3, 2))  # outstanding client requests
            self.assertEqual(c_first - open_arrivals["C"], ttft_open)
            self.assertEqual(c_first - closed_arrivals["C"], ttft_closed)
            # If the client was supposed to send at t=14 but could not, latency
            # from the planned send includes the additional client-side delay.
            self.assertEqual(closed_arrivals["C"] - open_arrivals["C"], delayed)
            self.assertEqual(delayed + ttft_closed, ttft_open)

    def test_resource_chain_and_time_changes(self):
        base, base_chains = critical_schedule()
        self.assertEqual(base, {"LA1": (0, 2), "LB1": (2, 4), "LA2": (4, 6),
                                "LB2": (6, 8), "C1": (4, 7), "W1": (8, 10),
                                "C2": (8, 11), "W2": (11, 13)})
        self.assertEqual(base_chains["W1"], ("LA1", "LB1", "LA2", "LB2", "W1"))
        self.assertEqual(base_chains["W2"], ("LA1", "LB1", "LA2", "LB2", "C2", "W2"))
        self.assertEqual(sum(base[n][1] - base[n][0] for n in base_chains["W2"]), 13)
        faster_first, first_chains = critical_schedule(c1_duration=2)
        self.assertEqual(faster_first["C1"], (4, 6))
        self.assertEqual((faster_first["W1"][1], faster_first["W2"][1]), (10, 13))
        self.assertEqual(first_chains["W2"], base_chains["W2"])
        faster_second, second_chains = critical_schedule(c2_duration=1)
        self.assertEqual(faster_second["C2"], (8, 9))
        self.assertEqual(faster_second["W2"], (10, 12))
        self.assertEqual(second_chains["W2"], ("LA1", "LB1", "LA2", "LB2", "W1", "W2"))
        self.assertEqual(sum(faster_second[n][1] - faster_second[n][0]
                             for n in second_chains["W2"]), 12)


if __name__ == "__main__":
    unittest.main()
