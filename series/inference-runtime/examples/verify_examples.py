"""Recompute article examples and check the teaching scheduler's invariants."""

import math
import unittest

from runtime_model import Request, example, simulate


class FormulaExamples(unittest.TestCase):
    def test_kv_units_transfer_and_capacity(self):
        kv = 2 * 80 * 8 * 128 * 2
        self.assertEqual(kv, 320 * 1024)
        self.assertEqual(kv * 8192, 2.5 * 1024**3)
        self.assertEqual(kv * 2000, 625 * 1024**2)
        self.assertAlmostEqual(kv * 2000 / 64e9 * 1000, 10.24)
        self.assertEqual(int(140e9 // (kv * 4096)), 104)
        self.assertEqual(int(140e9 // (kv * 8192)), 52)

    def test_paging_and_gemm(self):
        allocated = math.ceil(1500 / 16) * 16
        self.assertEqual(allocated, 1504)
        self.assertAlmostEqual(1500 / allocated, .9973404255319149)
        self.assertEqual(sum(s*s for s in [3, 5]), 34)
        self.assertEqual(2 * max(3, 5)**2, 50)
        self.assertEqual(2*4096*4096, 33554432)

    def test_latency_samples_and_joint_slo(self):
        times = [100, 120, 160]
        self.assertEqual((times[-1]-times[0])/(len(times)-1), 30)
        samples = sorted([25]*999+[570])
        self.assertEqual(samples[math.ceil(.99*len(samples))-1], 25)
        ttft_pass = set(range(99))
        tpot_pass = set(range(1, 100))
        self.assertEqual(len(ttft_pass & tpot_pass), 98)

    def test_speculative_distribution_and_cost(self):
        p, q = [.6, .4], [.8, .2]
        accepted = [min(x, y) for x, y in zip(p, q)]
        residual = [max(0, x-y) for x, y in zip(p, q)]
        rejection = 1-sum(accepted)
        output = [a+rejection*r/sum(residual) for a, r in zip(accepted, residual)]
        for actual, target in zip(output, p):
            self.assertAlmostEqual(actual, target)
        expected = sum(.8**j for j in range(5))
        self.assertAlmostEqual(expected, 3.3616)
        self.assertAlmostEqual(expected*10/(4*2+12+1), 1.600761904761905)

    def test_conditional_h100_case(self):
        kv = 327680
        for batch, ms in [(1, 15.068), (32, 19.504), (100, 29.234)]:
            estimate = (140e9+batch*4096*kv)/(13.4e12*.7)*1000
            self.assertAlmostEqual(estimate, ms, places=3)
        attention = 2*80*64*128*3500*3501
        prefill_ms = (2*70e9*3500+attention)/(4*989.5e12*.5)*1000
        self.assertAlmostEqual(prefill_ms, 255.715, places=3)


class EventExamples(unittest.TestCase):
    def test_reference_event_sequence(self):
        result = example()
        self.assertEqual(len(result["steps"]), 8)
        self.assertAlmostEqual(result["time_ms"], 10.943)
        self.assertEqual(result["requests"]["A"]["output_times_ms"], [3.0, 4.308, 5.72, 7.33])
        self.assertEqual(result["requests"]["B"]["output_times_ms"], [4.308, 5.72])
        self.assertEqual(result["requests"]["C"]["output_times_ms"], [8.53, 9.736, 10.943])

    def test_arrival_budget_progress_and_output_invariants(self):
        requests = [Request("late", 8, 2, 3), Request("early", 0, 7, 2), Request("one", 3, 1, 1)]
        for budget in [1, 2, 5, 20]:
            result = simulate(requests, budget)
            prefilled = {r.name: 0 for r in requests}
            arrivals = {r.name: r.arrival_ms for r in requests}
            lengths = {r.name: r.prompt_tokens for r in requests}
            previous_end = 0
            for step in result["steps"]:
                self.assertGreaterEqual(step["start_ms"], previous_end)
                self.assertGreater(step["end_ms"], step["start_ms"])
                self.assertLessEqual(sum(w["tokens"] for w in step["work"]), budget)
                for work in step["work"]:
                    name = work["request"]
                    self.assertGreaterEqual(step["start_ms"], arrivals[name])
                    if work["phase"] == "prefill":
                        prefilled[name] += work["tokens"]
                    else:
                        self.assertEqual(prefilled[name], lengths[name])
                for name in step["emitted"]:
                    self.assertEqual(prefilled[name], lengths[name])
                previous_end = step["end_ms"]
            for request in requests:
                actual = result["requests"][request.name]
                self.assertEqual(actual["prefilled"], request.prompt_tokens)
                self.assertEqual(len(actual["output_times_ms"]), request.output_tokens)
                self.assertTrue(all(a < b for a,b in zip(actual["output_times_ms"], actual["output_times_ms"][1:])))

    def test_single_output_and_idle_jump(self):
        result = simulate([Request("one", 50, 1, 1)])
        self.assertEqual(len(result["steps"]), 1)
        self.assertEqual(result["steps"][0]["start_ms"], 50)
        self.assertIsNone(result["requests"]["one"]["tpot_ms"])
        self.assertEqual(simulate([])["steps"], [])

    def test_invalid_inputs(self):
        for budget in [0, -1, True, 1.5]:
            with self.assertRaises(ValueError):
                simulate([], budget)
        for request in [Request("x", -1, 1, 1), Request("x", float("nan"), 1, 1),
                        Request("x", 0, 0, 1), Request("x", 0, 1, 0)]:
            with self.assertRaises(ValueError):
                simulate([request])
        with self.assertRaises(ValueError):
            simulate([Request("x", 0, 1, 1), Request("x", 1, 1, 1)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
