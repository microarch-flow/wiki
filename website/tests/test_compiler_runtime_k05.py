"""K05's conditional Llama 3 70B/H100 estimates and publication checks.

These tests use exact byte/FLOP counts and rational arithmetic. Hardware peak
specifications, logical traffic, assumed efficiencies and model results are
different things. Passing these tests establishes arithmetic consistency, not
measured performance or achievable production capacity/SLOs.
"""

from fractions import Fraction
import unittest

import test_compiler_runtime_guides as guides


class K05Tests(unittest.TestCase):
    cards = 4
    layers = 80
    query_heads = 64
    kv_heads = 8
    head_dim = 128
    element_bytes = 2
    block_positions = 16
    p_rounded = 70 * 10**9
    weight_bytes = 2 * p_rounded
    kv_bytes = 2 * layers * kv_heads * head_dim * element_bytes
    pool_bytes = cards * (72 - 2 - 35) * 10**9
    bandwidth = cards * 3_350_000_000_000  # B/s, aggregate peak
    compute_peak = cards * 989_500_000_000_000  # dense FLOP/s, aggregate peak

    def test_navigation_search_and_figures(self):
        route = "11-performance"
        slug = "k05-capacity-and-performance-estimation"
        guides.CompilerRuntimeGuideTests()._check_article(
            route, "性能分析、建模与验证", slug,
            "一套模型和设备配置究竟能够服务多少请求？",
            ("k05-kv-budget.svg", "k05-decode-estimates.svg", "k05-prefill-work.svg"),
        )
        previous = guides.SITE / guides.PREFIX / route / "k04-trace-and-event-model/index.html"
        self.assertIn(f"../{slug}/", guides.GuideContent(previous.read_text()).links)

    def test_capacity_budget_and_growth(self):
        self.assertEqual(self.cards * 80, 320)  # nominal GB, not available byte count
        usable = self.cards * 72 * 10**9  # constructed budget
        other = self.cards * 2 * 10**9
        self.assertEqual(usable - other - self.weight_bytes, self.pool_bytes)
        self.assertEqual(self.pool_bytes, 140 * 10**9)
        self.assertEqual(self.weight_bytes // self.cards, 35 * 10**9)
        self.assertEqual(self.pool_bytes // self.cards, 35 * 10**9)
        self.assertEqual(self.kv_bytes, 327680)
        self.assertEqual(self.kv_bytes, 320 * 1024)
        rank_kv = 2 * self.layers * (self.kv_heads // self.cards) * self.head_dim * self.element_bytes
        self.assertEqual(rank_kv, 81920)
        self.assertEqual(rank_kv * self.cards, self.kv_bytes)
        block_bytes = self.kv_bytes * self.block_positions
        self.assertEqual(block_bytes, 5242880)
        available = self.pool_bytes // block_bytes
        self.assertEqual(available, 26702)
        self.assertEqual(available, (self.pool_bytes // self.cards) // (rank_kv * self.block_positions))

        current_positions = 4096
        blocks_per_seq = current_positions // self.block_positions
        n, remainder = divmod(available, blocks_per_seq)
        self.assertEqual((n, remainder), (104, 78))
        bytes_for_100 = 100 * current_positions * self.kv_bytes
        self.assertEqual(bytes_for_100, 134_217_728_000)
        self.assertEqual(Fraction(current_positions * self.kv_bytes, 2**30), Fraction(5, 4))
        new_live_bytes = 100 * self.kv_bytes
        new_allocated_bytes = 100 * block_bytes
        self.assertEqual(new_live_bytes, 32_768_000)
        self.assertEqual(new_allocated_bytes, 524_288_000)
        self.assertLess(remainder, n)  # not all 104 sequences can grow by one position
        self.assertEqual(available // (blocks_per_seq + 1), 103)

        context_limit = 8192  # model's specified context, still assuming no extension
        full_seq_blocks = context_limit // self.block_positions
        self.assertEqual(available // full_seq_blocks, 52)
        remaining_context = context_limit - full_seq_blocks * self.block_positions
        self.assertEqual(remaining_context, 0)  # capacity count does not allow continued growth
        # Fix the pool byte count; change only KV effective byte count to 1 byte.
        half_block = block_bytes // 2
        half_available = self.pool_bytes // half_block
        self.assertEqual(half_available // blocks_per_seq, 208)
        self.assertEqual(half_available // full_seq_blocks, 104)

    def test_original_parameter_count_and_budget_sensitivity(self):
        d, ff, vocab = 8192, 28672, 128256
        q_width = self.query_heads * self.head_dim
        kv_width = self.kv_heads * self.head_dim
        self.assertEqual(q_width, d)
        # Bias-free attention Q,K,V,O; gated MLP with gate, up and down matrices.
        attention = d * q_width + 2 * d * kv_width + q_width * d
        mlp = 3 * d * ff
        block_matrices = self.layers * (attention + mlp)
        norms = (2 * self.layers + 1) * d  # two per block and final RMSNorm scale
        embedding = vocab * d
        head = d * vocab  # independent (not tied to token embedding)
        parameters = block_matrices + norms + embedding + head
        self.assertEqual(block_matrices, 68_451_041_280)
        self.assertEqual(norms, 1_318_912)
        self.assertEqual((embedding, head), (1_050_673_152, 1_050_673_152))
        self.assertEqual(parameters, 70_553_706_496)
        self.assertEqual(2 * (block_matrices + head) + 4 * self.layers * self.query_heads * self.head_dim * 4097,
                         149_743_468_544)
        weight = parameters * self.element_bytes
        self.assertEqual(weight, 141_107_412_992)
        # Hypothetical perfect balance across ranks, all other reservations fixed.
        pool = self.cards * (72 - 2) * 10**9 - weight
        self.assertEqual(pool, 138_892_587_008)
        blocks = pool // (self.block_positions * self.kv_bytes)
        self.assertEqual(blocks, 26491)
        self.assertEqual(divmod(blocks, 4096 // self.block_positions), (103, 123))

    def test_decode_work_bandwidth_and_conditional_output_rate(self):
        eta = Fraction(7, 10)  # assumed sustained bandwidth ratio, not observed
        history = 4096
        rows = [(1, 141_342_177_280, 10.548, 15.068, 0.038),
                (32, 182_949_672_960, 13.653, 19.504, 1.219),
                (100, 274_217_728_000, 20.464, 29.234, 3.808)]
        for batch, expected_read, peak_ms, conditional_ms, compute_ms in rows:
            # Count logical old KV reads and one weight read; omit new KV writes
            # and other bytes. This is not a measured HBM counter value.
            logical = self.weight_bytes + batch * history * self.kv_bytes
            self.assertEqual(logical, expected_read)
            time_bw_peak = Fraction(logical, self.bandwidth)
            time_bw_conditioned = time_bw_peak / eta
            visible = history + 1
            flop = batch * (2*self.p_rounded + 4*self.layers*self.query_heads*self.head_dim*visible)
            time_compute_peak = Fraction(flop, self.compute_peak)
            self.assertAlmostEqual(float(time_bw_peak * 1000), peak_ms, places=3)
            self.assertAlmostEqual(float(time_bw_conditioned * 1000), conditional_ms, places=3)
            self.assertAlmostEqual(float(time_compute_peak * 1000), compute_ms, places=3)
            self.assertGreater(time_bw_peak, time_compute_peak)
        # Last chosen point, *if* this bandwidth estimate were the whole round's
        # time and every one of 100 requests emitted a token in every round.
        self.assertAlmostEqual(float(Fraction(100) / time_bw_conditioned), 3420.64, places=2)

    def test_prefill_work_and_refined_count(self):
        n = 3500
        pair_count = n * (n + 1) // 2
        attn = 4 * self.layers * self.query_heads * self.head_dim * pair_count
        self.assertEqual(attn, 16_060_907_520_000)
        approximate = 2 * self.p_rounded * n + attn
        self.assertEqual(approximate, 506_060_907_520_000)
        peak_seconds = Fraction(approximate, self.compute_peak)
        assumed_eff = Fraction(1, 2)
        self.assertAlmostEqual(float(peak_seconds*1000), 127.858, places=3)
        self.assertAlmostEqual(float(peak_seconds/assumed_eff*1000), 255.715, places=3)
        # Refine linear work: count block matrices at every position and a single
        # final LM head (only the last logits needed); still omit other operators.
        d, ff, vocab = 8192, 28672, 128256
        kv_width = self.kv_heads * self.head_dim
        block_matrices = self.layers * (2*d*d + 2*d*kv_width + 3*d*ff)
        refined = 2 * block_matrices * n + 2 * d * vocab + attn
        self.assertEqual(refined, 495_220_297_826_304)
        self.assertAlmostEqual(float(Fraction(refined*1000, self.compute_peak) / assumed_eff), 250.238, places=3)

    def test_communication_payload_hypotheses(self):
        # Classical TP=4 hypothetical layout with two allreduces per block,
        # ring send ratio (two ring phases) = 2*(ranks-1)/ranks.
        hidden_width = 8192
        allreduces = self.layers * 2
        self.assertEqual(allreduces, 160)
        ring_send_ratio = Fraction(2 * (self.cards - 1), self.cards)
        self.assertEqual(ring_send_ratio, Fraction(3, 2))
        bw_assumed = 200 * 10**9  # effective per-rank send B/s, not measured
        for positions, send, ms in ((100, 393_216_000, Fraction("1.96608")),
                                    (3500, 13_762_560_000, Fraction("68.8128"))):
            tensor = positions * hidden_width * self.element_bytes
            per_rank_send = allreduces * ring_send_ratio * tensor
            self.assertEqual(per_rank_send, send)
            if positions == 100:
                self.assertEqual(per_rank_send * self.cards, 1_572_864_000)
            self.assertEqual(per_rank_send/bw_assumed*1000, ms)
            ideal = per_rank_send / (450 * 10**9) * 1000
            self.assertAlmostEqual(float(ideal), 0.873813 if positions == 100 else 30.583467, places=6)
            self.assertEqual(Fraction(allreduces * 5, 1000), Fraction("0.8"))
        # I05 cross-pool transfer, single logical KV state, different topology
        # and bandwidth assumption. These costs cannot simply be added as a rule.
        payload = 2000 * self.kv_bytes
        self.assertEqual(payload, 625 * 2**20)
        self.assertEqual(Fraction(payload * 1000, 64 * 10**9), Fraction("10.24"))

    def test_complete_request_work_budget(self):
        prompt, output = 3500, 100
        positions = prompt + output - 1  # Prefill emits first token; 99 ordinary decode steps
        self.assertEqual(positions, 3599)
        visible = range(prompt + 1, positions + 1)
        self.assertEqual((len(visible), sum(visible)), (99, 351450))
        prefill_attn = 2*self.layers*self.query_heads*self.head_dim*prompt*(prompt+1)
        decode_attn = 4*self.layers*self.query_heads*self.head_dim*sum(visible)
        request_approx_flop = 2*self.p_rounded*positions + prefill_attn + decode_attn
        self.assertEqual(request_approx_flop, 520_842_212_608_000)
        # Simplified workload-rate comparison using only the approximate FLOP
        # count and peak arithmetic budget. This is neither a proven upper bound
        # on the actual implementation's throughput nor evidence of an SLO.
        self.assertAlmostEqual(float(Fraction(self.compute_peak, request_approx_flop)), 7.599, places=3)

    def test_old_efficiency_examples_not_a_combined_factor(self):
        # Different denominators: reserved capacity, slot-iterations, duration.
        self.assertEqual(Fraction(4*1024, 4*8192), Fraction(1, 8))
        self.assertEqual(Fraction(2+4+8, 3*8), Fraction(14, 24))
        self.assertEqual(25 + 545, 570)


if __name__ == "__main__":
    unittest.main()
