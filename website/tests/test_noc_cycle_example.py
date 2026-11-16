"""Execute the published NoC teaching model against independent scenarios."""

from pathlib import Path
import json
import random
import re
import unittest


ARTICLE = (Path(__file__).resolve().parents[2] / "series/interconnect/NOC"
           / "08-simulator-construction/minimal-cycle-simulator.md")


class NocCycleExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        match = re.search(r"```python\n(.*?)\n```", ARTICLE.read_text(encoding="utf-8"), re.DOTALL)
        if match is None:
            raise AssertionError("published Python example is missing")
        cls.module = {"__name__": "noc_cycle_example"}
        exec(compile(match.group(1), str(ARTICLE), "exec"), cls.module)

    def test_three_hop_snapshots_match_hand_table(self):
        sim = self.module["LineNoC"]()
        rows = sim.run()
        # Input queues, ejection and four credits are end-of-cycle values.
        expected = [
            ([[0], [], [], []], [], [3, 4, 4, 4]),
            ([[1], [], [], []], [], [2, 3, 4, 4]),
            ([[2], [0], [], []], [], [2, 2, 4, 4]),
            ([[], [1], [], []], [], [3, 1, 3, 4]),
            ([[], [2], [0], []], [], [4, 2, 2, 4]),
            ([[], [], [1], []], [], [4, 3, 1, 3]),
            ([[], [], [2], [0]], [], [4, 4, 2, 2]),
            ([[], [], [], [1]], [0], [4, 4, 3, 1]),
            ([[], [], [], [2]], [1], [4, 4, 4, 2]),
            ([[], [], [], []], [2], [4, 4, 4, 3]),
            ([[], [], [], []], [], [4, 4, 4, 4]),
        ]
        self.assertEqual(len(rows), len(expected))
        for row, (queues, ejection, credits) in zip(rows, expected):
            with self.subTest(cycle=row["cycle"]):
                self.assertEqual((row["inputs"], row["ejection"], row["credit"]),
                                 (queues, ejection, credits))
        self.assertEqual((sim.injection_cycle, sim.network_arrival_cycle,
                          sim.consumer_complete_cycle, sim.quiescent_cycle), (0, 9, 10, 10))
        self.assertEqual(sim.consumed, [0, 1, 2])
        self.assertEqual(sim.free_seen, [True] * 4)
        sim.tick()
        self.assertEqual(sim.quiescent_cycle, 10)  # Record the first quiescent cycle.

    def test_backpressure_then_recovery(self):
        sim = self.module["LineNoC"](num_flits=30, ejection_depth=2)
        rows = [sim.tick(consumer_ready=False) for _ in range(18)]
        blocked = rows[-1]
        self.assertEqual([len(q) for q in blocked["inputs"]], [4, 4, 4, 4])
        self.assertEqual(len(blocked["ejection"]), 2)
        self.assertEqual(blocked["credit"], [0, 0, 0, 0])
        self.assertEqual(blocked["source_pending"], 12)
        sim.run(block_until=30)
        self.assertEqual(sim.consumed, list(range(30)))
        self.assertEqual((sim.consumer_complete_cycle, sim.quiescent_cycle), (59, 59))
        self.assertTrue(sim.is_quiescent())

    def test_single_flit_and_credit_visibility(self):
        single = self.module["LineNoC"](num_flits=1)
        single.run()
        self.assertEqual(single.label(0), "HT")
        self.assertEqual((single.network_arrival_cycle, single.consumer_complete_cycle), (7, 8))
        sim = self.module["LineNoC"](num_flits=3, depth=1)
        rows = sim.run()
        sends = [row["cycle"] for row in rows
                 if any(action.startswith("R0->R1") for action in row["actions"])]
        self.assertEqual(sends[:2], [1, 5])

    def test_full_ejection_does_not_use_same_cycle_drain(self):
        sim = self.module["LineNoC"](num_flits=30, ejection_depth=1)
        while not (len(sim.ejection) == 1 and sim.inputs[3]):
            sim.tick(consumer_ready=False)
            self.assertLess(sim.cycle, 100)
        row = sim.tick(consumer_ready=True)
        self.assertTrue(any(a.startswith("consume") for a in row["actions"]))
        self.assertFalse(any(a.startswith("eject") for a in row["actions"]))
        self.assertEqual(row["ejection"], [])
        row = sim.tick(consumer_ready=True)
        self.assertTrue(any(a.startswith("eject") for a in row["actions"]))

    def test_timeout_and_invalid_parameters(self):
        with self.assertRaises(ValueError):
            self.module["LineNoC"](depth=0)
        sim = self.module["LineNoC"](num_flits=30, ejection_depth=2)
        with self.assertRaises(TimeoutError):
            sim.run(block_until=100, max_cycles=20)
        self.assertFalse(sim.is_quiescent())
        self.assertGreater(len(sim.source), 0)

    def test_invariants_detect_duplicate_flit_and_invalid_credit(self):
        sim = self.module["LineNoC"](num_flits=2)
        sim.source[1] = 0  # Preserve total count while losing one identity.
        with self.assertRaisesRegex(AssertionError, "identity"):
            sim.check_invariants()
        sim = self.module["LineNoC"](num_flits=2)
        sim.credit[0] += 1
        with self.assertRaisesRegex(AssertionError, "credit conservation"):
            sim.check_invariants()

    def test_single_flit_parameterized_latency(self):
        for forward in (1, 2, 3):
            for returned in (1, 2, 3):
                with self.subTest(forward=forward, returned=returned):
                    sim = self.module["LineNoC"](num_flits=1, forward_latency=forward,
                                                return_latency=returned)
                    sim.run()
                    arrival = 1 + 3 * (forward + 1)
                    self.assertEqual(sim.network_arrival_cycle, arrival)
                    self.assertEqual(sim.consumer_complete_cycle, arrival + 1)
                    self.assertEqual(sim.quiescent_cycle, max(arrival + 1, arrival + returned))

    def test_varied_buffers_and_eventual_consumer_recovery(self):
        for seed in range(8):
            with self.subTest(seed=seed):
                rng = random.Random(seed)
                count = rng.randint(1, 12)
                sim = self.module["LineNoC"](
                    num_flits=count, depth=rng.randint(1, 4), ejection_depth=rng.randint(1, 3),
                    forward_latency=rng.randint(1, 3), return_latency=rng.randint(1, 3))
                for cycle in range(400):
                    sim.tick(consumer_ready=(cycle >= 50 or rng.random() < 0.4))
                    if sim.is_quiescent():
                        break
                self.assertTrue(sim.is_quiescent())
                self.assertEqual(sim.consumed, list(range(count)))
                self.assertEqual(sim.credit, [sim.depth] * 4)

    def test_workload_contract_accepts_zero_duration_compute(self):
        trace_article = (ARTICLE.parent.parent / "07-evaluation-methodology"
                         / "trace-generation-worked-example.md")
        match = re.search(r"```python\n(.*?)\n```", trace_article.read_text(encoding="utf-8"),
                          re.DOTALL)
        self.assertIsNotNone(match)
        trace_module = {"__name__": "noc_trace_example"}
        exec(compile(match.group(1), str(trace_article), "exec"), trace_module)
        trace = trace_module["make_trace"]()
        compute = next(event for event in trace["events"] if event["kind"] == "compute")
        compute["duration_cycles"] = 0
        trace_module["validate_trace"](trace)
        compute["duration_cycles"] = -1
        with self.assertRaises(ValueError):
            trace_module["validate_trace"](trace)

    def test_flow_to_completion_documented_example(self):
        worked = ARTICLE.parent / "workload-to-completion-worked-example.md"
        match = re.search(r"```json\n(.*?)\n```", worked.read_text(encoding="utf-8"), re.DOTALL)
        self.assertIsNotNone(match)
        trace = json.loads(match.group(1))
        trace_article = ARTICLE.parent.parent / "07-evaluation-methodology/trace-generation-worked-example.md"
        trace_code = re.search(r"```python\n(.*?)\n```", trace_article.read_text(encoding="utf-8"), re.DOTALL)
        self.assertIsNotNone(trace_code)
        trace_module = {"__name__": "noc_trace_example"}
        exec(compile(trace_code.group(1), str(trace_article), "exec"), trace_module)
        trace_module["validate_trace"](trace)
        flow, compute = trace["events"]
        self.assertEqual((flow["src_node"], flow["dst_set"], compute["depends_on"]), (0, [3], [flow["id"]]))
        num_flits = (flow["payload_bytes"] + 16 + 15) // 16  # The article's 16 B header and flit.
        self.assertEqual(num_flits, 3)
        sim = self.module["LineNoC"](num_flits=num_flits)
        sim.run()
        self.assertEqual((sim.injection_cycle, sim.network_arrival_cycle,
                          sim.consumer_complete_cycle, sim.quiescent_cycle), (0, 9, 10, 10))
        compute_start = sim.consumer_complete_cycle + 1  # Manual dependency visibility contract.
        compute_end_cycle = compute_start + compute["duration_cycles"] - 1
        self.assertEqual((compute_start, compute_end_cycle), (11, 12))


if __name__ == "__main__":
    unittest.main()
