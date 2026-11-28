"""K04's deterministic event models, exact arithmetic, and publication checks.

These checks validate the stated teaching rules. They do not validate a
cost model against real hardware or establish production SLO guarantees.
"""

from dataclasses import dataclass
from fractions import Fraction
import runpy
import unittest

import test_compiler_runtime_guides as guides


@dataclass(frozen=True)
class Request:
    name: str
    arrival: int  # microseconds
    prompt: int
    output: int


@dataclass(frozen=True)
class Round:
    start: int
    end: int
    prefill: tuple
    decode: tuple
    history: int
    emitted: tuple

    @property
    def prefill_count(self):
        return sum(n for _, n in self.prefill)

    @property
    def decode_count(self):
        return len(self.decode)


def request_schedule(requests, budget, prefill_us=100):
    """Independently compute rounds on an exact integer microsecond clock.

    A round's assigned work is committed only at its end. Arrivals at that
    boundary are admitted before selecting the following round. There is one
    exclusive executor and no memory limit, preemption or speculation.
    """
    if type(budget) is not int or budget < 1:
        raise ValueError("positive integer budget required")
    ordered = sorted(requests, key=lambda r: r.arrival)  # stable tie order
    if len({r.name for r in ordered}) != len(ordered):
        raise ValueError("duplicate request name")
    if any(not r.name or type(r.arrival) is not int or r.arrival < 0
           or type(r.prompt) is not int or r.prompt < 1
           or type(r.output) is not int or r.output < 1 for r in ordered):
        raise ValueError("invalid request")
    prefilled = {r.name: 0 for r in ordered}
    outputs = {r.name: [] for r in ordered}
    rounds = []
    now = 0
    while pending := [r for r in ordered if len(outputs[r.name]) < r.output]:
        ready = [r for r in pending if r.arrival <= now]
        if not ready:
            now = min(r.arrival for r in pending)
            continue
        decode = [r for r in ready if prefilled[r.name] == r.prompt][:budget]
        left = budget - len(decode)
        prefill = []
        for r in ready:
            n = min(left, r.prompt - prefilled[r.name])
            if n:
                prefill.append((r, n))
                left -= n
        p = sum(n for _, n in prefill)
        d = len(decode)
        s = sum(r.prompt + len(outputs[r.name]) - 1 for r in decode)
        assert 0 < p + d <= budget
        end = now + 1000 + prefill_us * p + 200 * d + s
        emitted = list(decode)
        for r, n in prefill:
            prefilled[r.name] += n
            if prefilled[r.name] == r.prompt:
                emitted.append(r)
        for r in emitted:
            outputs[r.name].append(end)
        rounds.append(Round(now, end, tuple((r.name, n) for r, n in prefill),
                            tuple(r.name for r in decode), s, tuple(r.name for r in emitted)))
        now = end
    return rounds, outputs


def metrics(r, outputs):
    ts = outputs[r.name]
    tpot = Fraction(ts[-1] - ts[0], len(ts) - 1) if len(ts) > 1 else None
    return (ts[0] - r.arrival, ts[-1] - r.arrival, tpot)


def fcfs_exclusive(arrivals, service_time):
    finish = 0
    intervals = []
    for arrival in sorted(arrivals):
        begin = max(arrival, finish)
        finish = begin + service_time
        intervals.append((begin, finish))
    return intervals


def f02_resource_events():
    """Advance to completions; dispatch fixed resource queues after updates."""
    queues = {"DMA": ["LA1", "LB1", "LA2", "LB2", "W1", "W2"],
              "compute": ["C1", "C2"]}
    dependencies = {"C1": {"LA1", "LB1"}, "C2": {"LA2", "LB2"},
                    "W1": {"C1"}, "W2": {"C2"}}
    active = {}
    done = set()
    intervals = {}
    trace = {}
    now = 0
    while len(done) < 8:
        completed = []
        for resource, (name, end) in list(active.items()):
            if end == now:
                done.add(name)
                completed.append(name)
                del active[resource]
        started = []
        for resource, queue in queues.items():
            if queue and resource not in active and dependencies.get(queue[0], set()) <= done:
                name = queue.pop(0)
                end = now + (2 if resource == "DMA" else 3)
                active[resource] = (name, end)
                intervals[name] = (now, end)
                started.append(name)
        trace[now] = (set(completed), set(started), {r: name for r, (name, _) in active.items()})
        if active:
            now = min(end for _, end in active.values())
        elif len(done) != 8:
            raise RuntimeError("unfinished work without events")
    return intervals, trace


class K04Tests(unittest.TestCase):
    requests = [Request("A", 0, 8, 4), Request("B", 0, 3, 2), Request("C", 5000, 6, 3)]

    def test_navigation_search_and_figures(self):
        route = "11-performance"
        slug = "k04-trace-and-event-model"
        guides.CompilerRuntimeGuideTests()._check_article(
            route, "性能分析、建模与验证", slug,
            "知道请求何时到达，怎样预测它们何时完成？",
            ("k04-resource-events.svg", "k04-token-budget-trace.svg", "k04-arrival-boundary.svg"),
        )
        previous = guides.SITE / guides.PREFIX / route / "k03-benchmarking-and-profiling/index.html"
        self.assertIn(f"../{slug}/", guides.GuideContent(previous.read_text()).links)

    def test_resource_events_and_queue(self):
        intervals = fcfs_exclusive([0, 0], 9)
        self.assertEqual(intervals, [(0, 9), (9, 18)])
        schedule, trace = f02_resource_events()
        self.assertEqual(schedule, {"LA1": (0, 2), "LB1": (2, 4), "LA2": (4, 6),
                                    "C1": (4, 7), "LB2": (6, 8), "W1": (8, 10),
                                    "C2": (8, 11), "W2": (11, 13)})
        self.assertEqual(trace[4], ({"LB1"}, {"C1", "LA2"}, {"DMA": "LA2", "compute": "C1"}))
        self.assertEqual(trace[6], ({"LA2"}, {"LB2"}, {"DMA": "LB2", "compute": "C1"}))
        # W1's data dependency becomes ready at t=7, but DMA is still busy.
        self.assertEqual(trace[7], ({"C1"}, set(), {"DMA": "LB2"}))
        self.assertEqual(trace[8], ({"LB2"}, {"W1", "C2"}, {"DMA": "W1", "compute": "C2"}))
        self.assertEqual(trace[13], ({"W2"}, set(), {}))
        self.assertEqual(sorted(trace), [0, 2, 4, 6, 7, 8, 10, 11, 13])

    def test_token_budget_traces_and_legacy_model(self):
        # Both cases are independently recomputed in integer us, then compared
        # against the unmodified older floating-point teaching implementation.
        legacy = runpy.run_path(str(guides.ROOT / "series/inference-runtime/examples/runtime_model.py"))
        cases = {
            5: ({"A": [3000, 4308, 5720, 7330], "B": [4308, 5720], "C": [8530, 9736, 10943]},
                [1500, 3000, 4308, 5720, 7330, 8530, 9736, 10943]),
            6: ({"A": [3100, 4511, 5720, 7430], "B": [3100, 4511], "C": [8530, 9736, 10943]},
                [1600, 3100, 4511, 5720, 7430, 8530, 9736, 10943]),
        }
        for budget, (expected_outputs, expected_ends) in cases.items():
            rounds, outputs = request_schedule(self.requests, budget)
            self.assertEqual(outputs, expected_outputs)
            self.assertEqual([r.end for r in rounds], expected_ends)
            self.assertEqual(len(rounds), 8)
            self.assertEqual([sum(getattr(r, a) for r in rounds)
                              for a in ("prefill_count", "decode_count", "history")], [17, 6, 43])
            self.assertEqual(rounds[-1].end, 8000 + 100*17 + 200*6 + 43)
            old = legacy["example"](budget)
            self.assertEqual(len(old["steps"]), len(rounds))
            self.assertEqual(round(old["time_ms"] * 1000), 10943)
            for step, old_step in zip(rounds, old["steps"]):
                self.assertEqual((step.start, step.end), tuple(round(old_step[k] * 1000)
                                                             for k in ("start_ms", "end_ms")))
                self.assertEqual(step.history, old_step["decode_kv_positions"])
                self.assertEqual(list(step.emitted), old_step["emitted"])
                self.assertEqual(list(step.prefill), [(w["request"], w["tokens"]) for w in old_step["work"]
                                                       if w["phase"] == "prefill"])
                self.assertEqual(list(step.decode), [w["request"] for w in old_step["work"]
                                                     if w["phase"] == "decode"])
            for req in self.requests:
                old_req = old["requests"][req.name]
                self.assertEqual(outputs[req.name], [round(t * 1000) for t in old_req["output_times_ms"]])
                for metric, field in zip(metrics(req, outputs), ("ttft_ms", "e2e_ms", "tpot_ms")):
                    self.assertAlmostEqual(float(metric), old_req[field] * 1000)
        # Explicit user-visible metrics, microseconds; use fractions for means.
        outputs5 = cases[5][0]
        self.assertEqual([metrics(r, outputs5) for r in self.requests], [
            (3000, 7330, Fraction(4330, 3)), (4308, 5720, Fraction(1412)), (3530, 5943, Fraction(2413, 2))])
        outputs6 = cases[6][0]
        self.assertEqual([metrics(r, outputs6) for r in self.requests], [
            (3100, 7430, Fraction(4330, 3)), (3100, 4511, Fraction(1411)), (3530, 5943, Fraction(2413, 2))])

    def test_cost_change_reschedules_rounds(self):
        original, _ = request_schedule(self.requests, 5)
        changed, outputs = request_schedule(self.requests, 5, prefill_us=200)
        self.assertEqual((original[2].end, changed[2].end), (4308, 5408))
        self.assertIn(("C", 3), changed[3].prefill)
        self.assertEqual(len(changed), 7)
        self.assertEqual((changed[-1].end, outputs["C"][0]), (11643, 9230))
        self.assertEqual(original[-1].end + 17 * 100, 12643)

    def test_arrival_boundary(self):
        for arrival, expected_end, expected_first, expected_ttft, expected_a, expected_count in (
                (5720, 10943, 8530, 2810, 7330, 8),
                (5721, 11943, 9530, 3809, 6930, 9)):
            requests = self.requests[:2] + [Request("C", arrival, 6, 3)]
            rounds, outputs = request_schedule(requests, 5)
            self.assertEqual((rounds[-1].end, outputs["C"][0], metrics(requests[-1], outputs)[0],
                              outputs["A"][-1], len(rounds)),
                             (expected_end, expected_first, expected_ttft, expected_a, expected_count))
            self.assertEqual([sum(getattr(r, a) for r in rounds)
                              for a in ("prefill_count", "decode_count", "history")], [17, 6, 43])

    def test_request_occupancy_area(self):
        rounds, outputs = request_schedule(self.requests, 5)
        changes = {}
        for request in self.requests:
            changes[request.arrival] = changes.get(request.arrival, 0) + 1
            end = outputs[request.name][-1]
            changes[end] = changes.get(end, 0) - 1
        active = area = old_t = 0
        for t, delta in sorted(changes.items()):
            area += active * (t - old_t)
            active += delta
            old_t = t
        self.assertEqual(active, 0)
        self.assertEqual(area, 18993)  # request-us
        elapsed = rounds[-1].end
        mean_e2e = Fraction(sum(metrics(r, outputs)[1] for r in self.requests), 3)
        self.assertEqual(mean_e2e, 6331)
        mean_population = Fraction(area, elapsed)
        self.assertEqual(mean_population, Fraction(18993, 10943))
        self.assertEqual(Fraction(3, elapsed) * mean_e2e, mean_population)

    def test_calibration_held_out_residual(self):
        # Constructed values in ms, distinct from a real calibration dataset.
        p3, p5 = Fraction("1.3"), Fraction("1.5")
        d6, d8 = Fraction("1.206"), Fraction("1.208")
        beta = (p5 - p3) / (5 - 3)
        alpha = p3 - 3 * beta
        delta = (d8 - d6) / (8 - 6)
        gamma = d6 - alpha - 6 * delta
        self.assertEqual((alpha, beta, gamma, delta),
                         (Fraction(1), Fraction(1, 10), Fraction(1, 5), Fraction(1, 1000)))
        predict = alpha + beta + gamma + 8 * delta
        observe = Fraction("1.340")
        residual = observe - predict  # measured minus predicted under stated convention
        self.assertEqual(predict, Fraction("1.308"))
        self.assertEqual(residual, Fraction("0.032"))
        self.assertEqual(abs(residual) * 1000, 32)
        self.assertEqual(abs(residual) / observe, Fraction(32, 1340))
        self.assertAlmostEqual(float(abs(residual) / observe * 100), 2.39, places=2)

    def test_empty_idle_and_progress_invariants(self):
        self.assertEqual(request_schedule([], 5), ([], {}))
        single = Request("one", 57000, 1, 1)
        rounds, outputs = request_schedule([single], 5)
        self.assertEqual((len(rounds), rounds[0].start, rounds[0].end), (1, 57000, 58100))
        self.assertEqual(metrics(single, outputs), (1100, 1100, None))
        requests = [Request("late", 8000, 2, 3), Request("early", 0, 7, 2), Request("one", 3000, 1, 1)]
        expected = {r.name: r for r in requests}
        for budget in (1, 2, 5, 20):
            rounds, outputs = request_schedule(requests, budget)
            prior_end = 0
            prefilled = {r.name: 0 for r in requests}
            generated = {r.name: 0 for r in requests}
            for step in rounds:
                self.assertGreaterEqual(step.start, prior_end)
                self.assertGreater(step.end, step.start)
                self.assertLessEqual(step.prefill_count + step.decode_count, budget)
                self.assertGreater(step.prefill_count + step.decode_count, 0)
                self.assertEqual(step.end - step.start, 1000 + 100*step.prefill_count + 200*step.decode_count + step.history)
                self.assertEqual(step.history, sum(expected[n].prompt + generated[n] - 1 for n in step.decode))
                for name in step.decode:
                    self.assertGreaterEqual(step.start, expected[name].arrival)
                    self.assertEqual(prefilled[name], expected[name].prompt)
                    self.assertGreater(generated[name], 0)
                for name, n in step.prefill:
                    self.assertGreaterEqual(step.start, expected[name].arrival)
                    self.assertGreater(n, 0)
                    prefilled[name] += n
                    self.assertLessEqual(prefilled[name], expected[name].prompt)
                    self.assertEqual(generated[name], 0)
                for name in step.emitted:
                    self.assertEqual(prefilled[name], expected[name].prompt)
                    generated[name] += 1
                    self.assertLessEqual(generated[name], expected[name].output)
                prior_end = step.end
            for req in requests:
                self.assertEqual(prefilled[req.name], req.prompt)
                self.assertEqual(len(outputs[req.name]), req.output)
                self.assertTrue(all(a < b for a, b in zip(outputs[req.name], outputs[req.name][1:])))
        for budget in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                request_schedule([], budget)


if __name__ == "__main__":
    unittest.main()
