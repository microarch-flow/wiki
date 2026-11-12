# Transformer：Attention 与 KV Cache 给 CIM 带来的新挑战

上级：[07 Workloads](./README.md)
相关：[Model Adaptation](../06-software-stack/model-adaptation-strategies.md), [NoC: Attention Prefill](../../../series/interconnect/NOC/wiki/06-ai-noc-specifics/workload-attention-prefill.md), [NoC: Attention Decode KV Cache](../../../series/interconnect/NOC/wiki/06-ai-noc-specifics/workload-attention-decode-kv-cache.md)

## 这页在回答什么问题

Transformer 适不适合 CIM？不能整模型回答，必须拆成 projection、FFN、QKᵀ score、mask/softmax、PV/context、normalization、KV cache 和 sampling；这些子模块的瓶颈完全不同。

## 子模块拆解

| 子模块 | CIM 适配性 | 主要瓶颈 |
| --- | --- | --- |
| Q/K/V projection | 中高 | GEMM 规整，但精度和 tiling 要闭合 |
| FFN | 中高 | 大 GEMM，传统 NPU/GPU 也很强 |
| QKᵀ score | 中 | Q 和 K 随序列更新，沿每个 head 的特征维 d_k 归约 |
| mask / softmax | 低 | 掩码、非线性、归约和数值稳定 |
| PV / context | 中 | softmax 概率 P 与历史 V 均为动态操作数，沿 key 序列维 T_k 归约 |
| normalization | 低 | 独立归约与数值稳定 |
| residual / layer glue | 低到中 | tensor movement、format conversion、fallback boundary |
| KV cache | CIM 不自然，PIM/NMC 更自然 | 大容量 memory access 和 token latency |
| sampling / control | 低 | 标量控制和 host/runtime |

单 head 的形状为 `Q[T_q,d_k] × K[T_k,d_k]ᵀ -> score[T_q,T_k]`，沿 `d_k` 求和；经 mask/softmax 得 `P[T_q,T_k]`，再算 `P[T_q,T_k] × V[T_k,d_v] -> context[T_q,d_v]`，沿 `T_k` 求和。实现可融合步骤并避免物化 P，但数学依赖不变。

Q/K/V 投影的模型权重可跨 token 复用；QKᵀ 与 PV 的操作数随序列更新。若将动态操作数映射到需编程的 NVM 权重阵列，还要计 program/verify；softmax 是独立归约和非线性步骤。

## Prefill 与 Decode 不同

Prefill 阶段大 GEMM 多，batch 或 sequence 较大，成熟 GPU/NPU 利用率高。CIM 只有在权重驻留、低比特和数据搬运明显受益时才有竞争力。

Decode 按 token 序列迭代；在小 batch、长上下文且 KV/权重未被近端充分命中的服务配置下，KV cache 和权重读取可能更突出。连续批处理与驻留状态会改变这一结论。这里的机会更偏 DRAM/HBM/GDDR-PIM 或 NMC，因为瓶颈靠近大容量 memory-side access，而不是小 CIM macro 的局部 MVM。NMC 在这里指 HBM base die、interposer 或 package-side compute，不是 memory die/bank 内 PIM。

## 三条 Paradigm 的 Transformer 差异

Analog CIM 对 Transformer 挑战最大。projection/FFN 可以映射为低比特 MVM，但 LLM 常见的精度、outlier、动态范围和模型质量要求会压缩 analog 空间。

Digital CIM 对小模型、edge Transformer 或特定 projection/FFN 子图更现实。它的挑战是 INT8/FP8、fallback、softmax/normalization 和 host sync。

Mixed-signal CIM 需要把 scale、校正和 tile-level accumulation 暴露给 compiler。它可能适合部分低比特子图，但不能把 KV cache 或 attention 全链路简单归入 CIM。

## 一句话理解

Transformer 不是一个 CIM workload，而是一组瓶颈不同的子图；projection/FFN 可能适合 CIM，KV cache 和 decode memory path 更偏 PIM/NMC。

## 建模启示

Transformer 建模必须按 phase 和子模块拆分：prefill/decode、Q/K/V projection、head count、hidden size、FFN expansion、QKᵀ score、mask/softmax、PV/context、normalization、residual、KV cache、sampling 分别记录 sequence length、batch、compute intensity、memory footprint、precision sensitivity、fallback ratio、tensor transfer、NoC traffic、latency target、energy target 和 synchronization。可折叠单个 macro 细节，但不能折叠 phase boundary、KV traffic、residual/fallback boundary 和 unsupported op。
