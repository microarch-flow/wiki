"""Verify J03 navigation and the capacity-management teaching examples.

All rates below are fixed-workload request-equivalent rates, not measured
performance, device schedules or individual-request delay predictions.
"""

from collections import Counter
import json
import unittest
from urllib.parse import urljoin, urlsplit

import test_compiler_runtime_guides as guides


def queue_trace(arrivals, capacities, initial=0):
    """Account for work in one-second intervals without an admission limit."""
    assert len(arrivals) == len(capacities)
    backlog = [initial]
    completed = []
    for arrival, capacity in zip(arrivals, capacities):
        available = backlog[-1] + arrival
        done = min(available, capacity)
        completed.append(done)
        backlog.append(available - done)
    return backlog, completed


class J03Tests(unittest.TestCase):
    def test_navigation_search_figures_and_complete_topic(self):
        route = "10-serving"
        slug = "j03-serving-scaling"
        guides.CompilerRuntimeGuideTests()._check_article(
            route, "推理服务系统", slug,
            "请求量突然增加，为什么扩容不能立即解决拥塞？",
            ("j03-scale-up-backlog.svg", "j03-replica-lifecycle.svg",
             "j03-pd-capacity.svg"),
        )
        previous = guides.SITE / guides.PREFIX / route / "j02-request-and-resource-lifecycle/index.html"
        self.assertIn(f"../{slug}/", guides.GuideContent(previous.read_text()).links)

        relative = f"{guides.PREFIX}{route}/{slug}/"
        page = guides.GuideContent((guides.SITE / relative / "index.html").read_text())
        linked_paths = {urlsplit(urljoin("https://site.invalid/" + relative, link)).path
                        for link in page.links}
        for dependency in (
            "10-serving/j01-request-routing",
            "10-serving/j02-request-and-resource-lifecycle",
            "07-model-execution/g01-model-loading-and-execution",
            "07-model-execution/g06-prefix-cache",
            "09-distributed-execution/i05-prefill-decode-disaggregation",
            "11-performance/k01-performance-metrics",
        ):
            self.assertIn(f"/{guides.PREFIX}{dependency}/", linked_paths)

        topic = guides.PREFIX + route + "/"
        locations = Counter(entry["location"] for entry in json.loads(
            (guides.SITE / "search/search_index.json").read_text())["docs"]
            if "#" not in entry["location"] and entry["location"].startswith(topic))
        slugs = ("j01-request-routing", "j02-request-and-resource-lifecycle", slug)
        self.assertEqual(locations, Counter([topic] + [f"{topic}{s}/" for s in slugs]))

    def test_scale_up_delay_and_backlog_drain(self):
        warm_capacity = 4  # request-equivalent work/s, unchanged workload mix
        old_capacity = 2 * warm_capacity
        expanded_capacity = 3 * warm_capacity

        # Before the increase, six arrivals/s can be handled by eight/s.
        self.assertEqual(queue_trace([6], [old_capacity]), ([0, 0], [6]))

        # Start provisioning at t=0. The third replica first becomes routable
        # at t=10, and in this idealized case immediately has warm capacity.
        arrivals = [10] * 25
        capacities = [old_capacity] * 10 + [expanded_capacity] * 15
        backlog, completed = queue_trace(arrivals, capacities)
        self.assertEqual(backlog[:11], list(range(0, 21, 2)))
        self.assertEqual(backlog[10:21], list(range(20, -1, -2)))
        self.assertEqual(backlog[20:], [0] * 6)
        self.assertEqual(completed, [8] * 10 + [12] * 10 + [10] * 5)
        self.assertEqual(sum(arrivals), sum(completed) + backlog[-1])

    def test_cold_replica_is_routable_but_cannot_yet_drain_backlog(self):
        # On readiness, a cold replica initially contributes only two/s.
        # Capacity now equals arrivals, which prevents growth but cannot
        # remove previously accumulated work.
        backlog, completed = queue_trace([10] * 4, [8 + 2] * 4, initial=20)
        self.assertEqual(backlog, [20] * 5)
        self.assertEqual(completed, [10] * 4)
        # Once warm capacity becomes 12/s, ten more seconds are needed.
        backlog, _ = queue_trace([10] * 10, [12] * 10, initial=backlog[-1])
        self.assertEqual(backlog, list(range(20, -1, -2)))

    def test_short_burst_ends_before_added_capacity_is_usable(self):
        # The burst lasts five seconds, then arrivals return to six/s.
        # The existing replicas can already clear the backlog at t=10,
        # precisely when the new replica would finish provisioning.
        arrivals = [10] * 5 + [6] * 5
        backlog, completed = queue_trace(arrivals, [8] * 10)
        self.assertEqual(backlog, [0, 2, 4, 6, 8, 10, 8, 6, 4, 2, 0])
        self.assertEqual(completed, [8] * 10)
        self.assertEqual(sum(arrivals), sum(completed))

    def test_pd_capacity_requires_all_stages(self):
        # Convert every stage to the same request workload before taking
        # the bottleneck. These minima are steady-state capacity bounds.
        prefill, transfer, decode = 8, 6, 5
        self.assertEqual(min(prefill, transfer, decode), 5)
        self.assertEqual(min(12, transfer, decode), 5)
        self.assertEqual(min(12, transfer, 9), 6)

    def test_tenant_budget_changes_distribution_not_supply(self):
        # A policy reserves up to two/s for Y and shares remaining capacity
        # with X. Unused budget can be borrowed in this example.
        def allocate(x, y, capacity=8, y_budget=2):
            served_y = min(y, y_budget, capacity)
            served_x = min(x, capacity - served_y)
            return served_x, served_y, x - served_x, y - served_y

        served_x, served_y, excess_x, excess_y = allocate(8, 2)
        self.assertEqual((served_x, served_y, excess_x, excess_y), (6, 2, 2, 0))
        self.assertEqual(served_x + served_y, 8)
        self.assertEqual(excess_x + excess_y, 2)
        self.assertEqual(allocate(8, 1), (7, 1, 1, 0))
        self.assertEqual(allocate(8, 0), (8, 0, 0, 0))


if __name__ == "__main__":
    unittest.main()
