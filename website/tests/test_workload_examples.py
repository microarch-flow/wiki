"""Recompute the fixed teaching examples in series/workload, without ML libraries."""

from collections import Counter
from itertools import accumulate
from math import exp, floor, log, sqrt
from statistics import mean, pvariance
import unittest


class FoundationExamples(unittest.TestCase):
    def test_parameter_update(self):
        def loss(w):
            return (2 * w - 3) ** 2 / 2

        step = 1e-5
        gradient = (loss(1 + step) - loss(1 - step)) / (2 * step)
        trained_weight = 1 - 0.1 * gradient
        self.assertAlmostEqual(gradient, -2)
        self.assertAlmostEqual(loss(trained_weight), 0.18)
        self.assertAlmostEqual(trained_weight * 5, 6)

    def test_shapes_and_traffic(self):
        rows = [[1, 2, 3], [4, 5, 6]]
        bias = [10, 20, 30]
        self.assertEqual([sum(x + b for x, b in zip(row, bias)) for row in rows], [66, 75])
        m, k, n = 4, 8, 6
        macs = sum(k for _row in range(m) for _col in range(n))
        nbytes = 2 * (m*k + k*n + m*n)
        self.assertEqual((macs, nbytes, round(2 * macs / nbytes, 2)), (192, 208, 1.85))

    def test_expert_selection_and_capacity(self):
        scores = [0.6, 0.3, 0.1]
        chosen = sorted(range(len(scores)), key=scores.__getitem__, reverse=True)[:2]
        weight = sum(scores[i] for i in chosen)
        self.assertAlmostEqual(sum(scores[i] * v / weight for i, v in zip(chosen, [4, 10])), 6)
        loads = Counter([0, 0, 2, 0])
        self.assertEqual([min(loads[i], 2) for i in range(3)], [2, 0, 1])

    def test_masked_loss_and_teacher(self):
        # Large errors in the four visible patches do not enter the masked mean.
        errors = [100] * 4 + [2] + [0] * 11
        self.assertAlmostEqual(mean(x*x for x in errors[4:]), 1/3)
        self.assertAlmostEqual(sum((x-y)**2 for x, y in zip([1, 0], [0.6, 0.8])), 0.8)
        self.assertAlmostEqual(0.9 * 1 + 0.1 * 1.4, 1.04)

    def test_next_token_labels(self):
        tokens = ["BOS", "红", "杯", "在", "桌上"]
        training = [(tokens[:i], token) for i, token in enumerate(tokens[1:], start=1)]
        self.assertEqual(training[2], (["BOS", "红", "杯"], "在"))
        self.assertEqual([label for _, label in training], tokens[1:])

    def test_conditional_velocity(self):
        endpoints = [(0, 2), (-1, 3)]
        self.assertEqual([(a+b)/2 for a, b in endpoints], [1, 1])
        velocities = [b-a for a, b in endpoints]
        risk = lambda v: mean((v-target)**2 for target in velocities)
        self.assertLess(risk(3), min(risk(2.9), risk(3.1)))
        self.assertAlmostEqual(1 + 0.1 * mean(velocities), 1.3)

    def test_vocabulary_projection(self):
        batch, tokens, width, vocab = 2, 4, 8, 30
        hidden = [[[0]*width for _ in range(tokens)] for _ in range(batch)]
        full = sum(len(row)*vocab for row in hidden)
        self.assertEqual((full, len(hidden)*vocab), (240, 60))
        logits = [2, 1, 0]
        self.assertEqual([round(exp(z)/sum(map(exp, logits)), 3) for z in logits], [.665, .245, .09])

    def test_visual_prefix_and_loss_positions(self):
        visual = ["patch"] * (224 // 16)**2
        prompt = visual + ["这", "是", "什么"]
        sequence = prompt + ["红", "杯", "EOS"]
        labels = [(i, sequence[i]) for i in range(len(prompt), len(sequence))]
        # i also equals the one-based position of the preceding input.
        self.assertEqual(labels, [(199, "红"), (200, "杯"), (201, "EOS")])

    def test_planner_and_controller(self):
        def cost(u):
            path = list(accumulate(u, initial=0))
            return (path[-1]-1.5)**2 + 0.1*sum(a*a for a in u)

        self.assertAlmostEqual(cost((1, .5)), .125)
        self.assertAlmostEqual(cost((0, .5)), 1.025)
        self.assertEqual(min(1, 2 * (1.5-.8)), 1)

    def test_policy_gradient_and_baseline(self):
        def p(theta):
            return 1 / (1 + exp(-theta))

        # An independent finite difference of the selected action's log probability.
        eps = 1e-5
        derivative = (log(p(eps)) - log(p(-eps))) / (2*eps)
        advantage = sum([0, 2]) - 1
        new_logit = .2 * advantage * derivative
        self.assertAlmostEqual(new_logit, .1)
        self.assertEqual(round(p(new_logit), 3), .525)
        self.assertAlmostEqual(1 + .1 * advantage, 1.1)

    def test_ssm_state_and_scan(self):
        updated = [a*h + b*2 for a, h, b in zip([.5, .25], [4, 1], [1, 2])]
        self.assertEqual(updated, [4, 4.25])
        self.assertEqual(sum(c*h for c, h in zip([1, -1], updated)), -.25)
        self.assertEqual(3*(2*5+1)+4, (3*2)*5 + (3*1+4))
        update, readout = 256 * 16 * 3, 256 * (16 + 15)
        self.assertEqual((update + readout, 2 * (256 * 16 * 2)), (20224, 16384))

    def test_moe_delivery(self):
        assignments = [(0, 1), (0, 2), (0, 1), (1, 2)]
        loads = Counter(e for pair in assignments for e in pair)
        total = sum(loads.values())
        self.assertEqual([loads[i] for i in range(3)], [3, 3, 2])
        self.assertEqual((total*8*2, loads[2]*8*2), (128, 32))
        self.assertEqual((total*4*8*16, 4*8*3), (4096, 96))


class MechanismExamples(unittest.TestCase):
    def test_ddpm_last_two_steps(self):
        alpha, beta = .8, .2
        cumulative = alpha**2
        mu = (.6 - beta*.3/sqrt(1-cumulative)) / sqrt(alpha)
        variance = beta*(1-alpha)/(1-cumulative)
        x1 = mu + sqrt(variance)*.3
        self.assertAlmostEqual(variance, 1/9)
        self.assertEqual(tuple(round(x, 4) for x in (mu, x1, x1/sqrt(alpha))),
                         (.5590, .6590, .7368))

    def test_lift_and_splat(self):
        grid = Counter()
        for q, feature, probs in ((.1, 4, [.75, .25]), (.3, 6, [.5, .5])):
            for depth, prob in zip([2, 4], probs):
                grid[floor(depth), floor(q*depth)] += feature * prob
        self.assertEqual(grid, {(2, 0): 6, (4, 0): 1, (4, 1): 3})
        self.assertEqual(sum(grid.values()), 10)

    def test_real_and_imagined_state(self):
        prior = .2
        evidence = prior*.9 + (1-prior)*.15
        self.assertAlmostEqual(prior*.9/evidence, .6)

    def test_cem_refit(self):
        candidates = [-1, 0, 1, 2]
        elite = sorted(candidates, key=lambda a: abs(a-1.4))[:2]
        self.assertEqual(elite, [1, 2])
        self.assertEqual((mean(elite), pvariance(elite)), (1.5, .25))

    def test_prefill_and_decode(self):
        weights = sum(i*o for i, o in [(64, 64), (64, 32), (64, 32), (64, 64),
                                        (64, 128), (128, 64)])
        per_pair = 2 * (16*2) * 4  # QK and AV, 16 channels, 4 query heads.
        kv_per_token = 2*2*16*2
        self.assertEqual(2*weights, 56*1024)
        self.assertEqual(4*2*weights + sum(range(1, 5))*per_pair, 231936)
        self.assertEqual(2*weights + 5*per_pair, 58624)
        self.assertEqual((4*kv_per_token, kv_per_token, 5*kv_per_token), (512, 128, 640))


if __name__ == "__main__":
    unittest.main()
