# Transformer：Attention 与 KV Cache 给 CIM 带来的新挑战

上级：[07 Workloads](./README.md)
相关：[Model Adaptation](../06-software-stack/model-adaptation-strategies.md), [NoC: Attention Prefill](../../../NoC/wiki/06-ai-noc-specifics/workload-attention-prefill.md), [NoC: Attention Decode KV Cache](../../../NoC/wiki/06-ai-noc-specifics/workload-attention-decode-kv-cache.md)

## 这页在回答什么问题

Transformer 适不适合 CIM？不能整模型回答，必须拆成 projection、FFN、attention score、softmax、normalization、KV cache 和 sampling；这些子模块的瓶颈完全不同。

## 子模块拆解

| 子模块 | CIM 适配性 | 主要瓶颈 |
| --- | --- | --- |
| Q/K/V projection | 中高 | GEMM 规整，但精度和 tiling 要闭合 |
| FFN | 中高 | 大 GEMM，传统 NPU/GPU 也很强 |
| attention score | 中 | 动态数据、mask、reduction、softmax |
| softmax / normalization | 低 | 非线性、归约和数值稳定 |
| residual / layer glue | 低到中 | tensor movement、format conversion、fallback boundary |
| KV cache | CIM 不自然，PIM/NMC 更自然 | 大容量 memory access 和 token latency |
| sampling / control | 低 | 标量控制和 host/runtime |

## Prefill 与 Decode 不同

Prefill 阶段大 GEMM 多，batch 或 sequence 较大，成熟 GPU/NPU 利用率高。CIM 只有在权重驻留、低比特和数据搬运明显受益时才有竞争力。

Decode 阶段 batch 小、逐 token 迭代，KV cache 和权重读取更突出。这里的机会更偏 DRAM/HBM/GDDR-PIM 或 NMC，因为瓶颈靠近大容量 memory-side access，而不是小 CIM macro 的局部 MVM。NMC 在这里指 HBM base die、interposer 或 package-side compute，不是 memory die/bank 内 PIM。

## 三条 Paradigm 的 Transformer 差异

Analog CIM 对 Transformer 挑战最大。projection/FFN 可以映射为低比特 MVM，但 LLM 常见的精度、outlier、动态范围和模型质量要求会压缩 analog 空间。

Digital CIM 对小模型、edge Transformer 或特定 projection/FFN 子图更现实。它的挑战是 INT8/FP8、fallback、softmax/normalization 和 host sync。

Mixed-signal CIM 需要把 scale、校正和 tile-level accumulation 暴露给 compiler。它可能适合部分低比特子图，但不能把 KV cache 或 attention 全链路简单归入 CIM。

## 一句话理解

Transformer 不是一个 CIM workload，而是一组瓶颈不同的子图；projection/FFN 可能适合 CIM，KV cache 和 decode memory path 更偏 PIM/NMC。

## 建模启示

Transformer 建模必须按 phase 和子模块拆分：prefill/decode、Q/K/V projection、head count、hidden size、FFN expansion、attention score、softmax、normalization、residual、KV cache、sampling 分别记录 sequence length、batch、compute intensity、memory footprint、precision sensitivity、fallback ratio、tensor transfer、NoC traffic、latency target、energy target 和 synchronization。可折叠单个 macro 细节，但不能折叠 phase boundary、KV traffic、residual/fallback boundary 和 unsupported op。
