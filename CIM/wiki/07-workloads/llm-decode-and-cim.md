# LLM Decode 阶段：Memory-Bound 工作负载与 CIM 的契合度

上级：[07 Workloads](./README.md)
相关：[Transformer on CIM](./transformer-on-cim.md), [RAM: HBM vs LPDDR for NPU](../../../RAM/wiki/09-ai-chip-memory-architecture/hbm-vs-lpddr-for-npu.md), [NoC: Decode KV Cache](../../../NoC/wiki/06-ai-noc-specifics/workload-attention-decode-kv-cache.md), [BUS: DMA Completion](../../../BUS/wiki/06-scenarios-case-studies/dma-completion-missing-case-card.md)

## 这页在回答什么问题

LLM decode 为什么经常被拿来讨论 PIM/NMC，而不是纯 CIM？因为 decode 的核心瓶颈往往是小 batch、逐 token 同步、KV cache 与权重访问，而不是单个 array 内 MVM 的峰值能效。

## Decode 的瓶颈

decode 每步生成一个或少量 token，batch 小，kernel 粒度碎，host/runtime 同步频繁。虽然仍有 GEMM/FFN/projection，但权重读取、KV cache 访问、attention 相关数据移动和 memory bandwidth 更容易主导 token latency。

长上下文会放大 KV cache 容量和带宽压力。RAM wiki 的 HBM/LPDDR 对比说明，高带宽 memory 本身已经是 AI 系统关键资源；decode 的问题是如何少搬、近搬和少同步。

## CIM 能做什么

CIM 可以加速部分低比特 projection、FFN 或小模型子图。SRAM digital/mixed-signal CIM 对 edge LLM 或专用小模型更现实；analog CIM 需要证明低比特和误差不会损害 token quality。

但 CIM 很难直接解决大容量 KV cache 和权重流动问题。即使某个 MVM macro 很省电，decode 的端到端 token latency 仍可能被 memory access、fallback 和 host synchronization 控制。

## PIM/NMC 为什么更自然

DRAM/HBM/GDDR-PIM 把 compute 放到 memory die/bank 内独立单元，更适合减少 memory-side 往返。HBM base die、interposer 或 package-side compute 属于 NMC，更适合利用 package bandwidth 和靠近 HBM 的数据路径。两者都不是 CIM macro，但更贴近 decode 的瓶颈位置。

## 三条 Paradigm 的 Decode 差异

Analog CIM 的 decode 机会窄，主要在固定低比特子图。Digital CIM 可作为 SoC 内特定算子加速，但必须和 NPU/GPU fallback 协作。Mixed-signal CIM 要额外处理 scale、校正和 runtime metadata，decode 小粒度同步会放大这些开销。

## 一句话理解

LLM decode 的主要机会常在 memory-side access 和 token latency，而不是 array-native CIM 的局部 MVM；PIM/NMC 往往比 CIM 更贴近瓶颈。

## 建模启示

decode 建模要以 token latency 为主，记录 prefill/decode phase、batch size、context length、KV cache bytes/token、weight residency、weight bandwidth、DMA/host stall、memory bandwidth、fallback frequency、host sync、memory-side offload ratio、energy per token 和 per-token latency。Resource 包括 HBM/DRAM、CIM macro、PIM/NMC engine 和 host；Topology 包括 KV cache path、memory-side offload path、NoC/reduction path 和 host-device transfer path；Interaction 是逐 token memory access 与 synchronization；Capability 是支持的子图和精度。GEMM macro 细节可折叠，KV cache placement、host/device transfer 和 token-by-token synchronization 不能折叠。
