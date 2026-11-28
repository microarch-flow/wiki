"""K06 publication, pinned source references, and logical request progression.

The request is a deterministic teaching state machine. These tests neither
execute vLLM/SGLang nor compare their actual latency, memory use or outputs.
Pinned links are checked locally (no network dependency in the site tests).
"""

import re
import unittest
from urllib.parse import urlsplit

import test_compiler_runtime_guides as guides


class K06Tests(unittest.TestCase):
    route = "11-performance"
    slug = "k06-framework-code-walkthrough"
    title = "沿着同一个请求，怎样读懂 vLLM 和 SGLang 的源码执行路径？"

    def test_navigation_search_and_figures(self):
        guides.CompilerRuntimeGuideTests()._check_article(
            self.route, "性能分析、建模与验证", self.slug, self.title,
            ("k06-request-path.svg", "k06-token-state.svg"),
        )
        previous = guides.SITE / guides.PREFIX / self.route / "k05-capacity-and-performance-estimation/index.html"
        self.assertIn(f"../{self.slug}/", guides.GuideContent(previous.read_text()).links)
        # K06 should remain the one concluding/deepening case in this topic;
        # its plan and guide both point to the completed article, not a stub.
        guide_text = (guides.SOURCE / self.route / "README.md").read_text()
        plan_text = (guides.ROOT / "docs/compiler-runtime-plan.md").read_text()
        guide_row = re.search(r"^\| K06 \|.*$", guide_text, re.M).group(0)
        plan_row = re.search(r"^\| K06 \|.*$", plan_text, re.M).group(0)
        self.assertIn(f"[{self.title}]({self.slug}.md)", guide_row)
        self.assertIn(f"`{self.slug}.md`", plan_row)
        for row in (guide_row, plan_row):
            self.assertIn("已发布", row.split("|")[-2])
            self.assertIn("深化", row.split("|")[-2])

    def test_pinned_framework_source_links(self):
        source = (guides.SOURCE / self.route / f"{self.slug}.md").read_text()
        repositories = {
            "vllm-project/vllm": ("v0.12.0", "4fd9d6a85c00ac0186aa9abbeff73fc2ac6c721e"),
            "sgl-project/sglang": ("v0.5.6", "7ae368efde14f0b2abe769a5fbb99b8154b2a9b7"),
        }
        for version, _ in repositories.values():
            self.assertRegex(source, rf"\b{re.escape(version)}\b")
        files = {repo: set() for repo in repositories}
        refs = {repo: set() for repo in repositories}
        for url in re.findall(r"https://github\.com/[^\s<>)\]`]+", source):
            pieces = urlsplit(url).path.strip("/").split("/")
            repo = "/".join(pieces[:2])
            if repo not in repositories or len(pieces) < 4 or pieces[2] not in {"blob", "tree"}:
                continue
            ref = pieces[3]
            self.assertIn(ref, repositories[repo], url)
            refs[repo].add(ref)
            if pieces[2] == "blob":
                self.assertGreaterEqual(len(pieces), 5, url)
                files[repo].add("/".join(pieces[4:]))
        # Check core source evidence covers the request path (not just a link to
        # a repository/release). These are module paths at the named versions.
        expected = {
            "vllm-project/vllm": {
                "vllm/entrypoints/openai/api_server.py",
                "vllm/entrypoints/openai/serving_completion.py",
                "vllm/v1/engine/input_processor.py",
                "vllm/v1/engine/output_processor.py",
                "vllm/v1/engine/detokenizer.py",
                "vllm/v1/engine/core.py",
                "vllm/v1/core/sched/scheduler.py",
                "vllm/v1/core/kv_cache_manager.py",
                "vllm/v1/core/block_pool.py",
                "vllm/v1/worker/gpu_model_runner.py",
                "vllm/v1/attention/backends/flash_attn.py",
            },
            "sgl-project/sglang": {
                "python/sglang/srt/entrypoints/http_server.py",
                "python/sglang/srt/entrypoints/openai/serving_completions.py",
                "python/sglang/srt/managers/tokenizer_manager.py",
                "python/sglang/srt/managers/detokenizer_manager.py",
                "python/sglang/srt/managers/scheduler.py",
                "python/sglang/srt/managers/schedule_batch.py",
                "python/sglang/srt/managers/scheduler_output_processor_mixin.py",
                "python/sglang/srt/mem_cache/common.py",
                "python/sglang/srt/mem_cache/radix_cache.py",
                "python/sglang/srt/model_executor/model_runner.py",
                "python/sglang/srt/layers/attention/flashinfer_backend.py",
                "python/sglang/srt/layers/sampler.py",
            },
        }
        for repo, modules in expected.items():
            self.assertTrue(modules <= files[repo], (repo, modules - files[repo]))
            self.assertTrue(refs[repo], repo)

    def test_request_generation_and_release(self):
        # A: 8 prompt token IDs, exactly 4 committed sampled outputs, no early
        # stopping, no prefix hits, no chunking, no speculative decode. This
        # models the common mathematical events, not either runtime's counters.
        prompt = tuple(f"x{i}" for i in range(1, 9))
        planned_outputs = tuple(f"y{i}" for i in range(1, 5))
        known = list(prompt)
        kv = []
        emitted = []
        snapshots = [(len(known), len(kv), len(emitted))]
        compute_indices = []
        for next_token in planned_outputs:
            # Each round consumes the preexisting input tail, then commits one
            # next token; that token is not itself computed in this same round.
            positions = range(len(kv), len(known))
            compute_indices.append(tuple(positions))
            kv.extend(known[len(kv):])
            emitted.append(next_token)
            known.append(next_token)
            self.assertEqual(kv, known[:-1])
            self.assertLessEqual(len(emitted), len(planned_outputs))
            snapshots.append((len(known), len(kv), len(emitted)))
        self.assertEqual(compute_indices, [tuple(range(8)), (8,), (9,), (10,)])
        self.assertEqual(snapshots, [(8, 0, 0), (9, 8, 1), (10, 9, 2), (11, 10, 3), (12, 11, 4)])
        source = (guides.SOURCE / self.route / f"{self.slug}.md").read_text()
        # Compare the article's three numeric state columns to the computed
        # sequence (known, generated, KV); the row labels may be edited freely.
        stated = [tuple(map(int, row)) for row in re.findall(
            r"^\|[^|]+\|[^|]+\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|$", source, re.M)]
        expected = [(known_count, generated_count, kv_count)
                    for known_count, kv_count, generated_count in snapshots]
        self.assertTrue(any(stated[i:i+len(expected)] == expected
                            for i in range(len(stated)-len(expected)+1)), stated)
        self.assertEqual(len(kv), len(prompt) + len(planned_outputs) - 1)
        self.assertEqual(tuple(emitted), planned_outputs)
        self.assertNotIn(planned_outputs[-1], kv)
        # When final access/references have ended, the active request's state
        # can be released. This is not a claim about physical CUDA allocation
        # or about retention of shareable cache blocks by a real implementation.
        kv.clear()
        self.assertEqual((len(known), len(kv), len(emitted)), (12, 0, 4))
        self.assertEqual(tuple(emitted), planned_outputs)


if __name__ == "__main__":
    unittest.main()
