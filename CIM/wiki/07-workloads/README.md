# 07 Workloads

上级：[CIM Wiki](../README.md)
相关：[Workload Characterization](./workload-characterization-for-cim.md), [RAM: Memory Bound vs Compute Bound](../../../RAM/wiki/09-ai-chip-memory-architecture/memory-bound-vs-compute-bound.md), [NoC: Attention Decode KV Cache](../../../NoC/wiki/06-ai-noc-specifics/workload-attention-decode-kv-cache.md), [BUS: DMA Path](../../../BUS/wiki/04-microarchitecture-integration/dma-descriptor-fetch-data-move-writeback.md), [FAB: Thermal Management](../../../FAB/wiki/06-cross-cutting-engineering/thermal-path-and-management.md)

## 这页在回答什么问题

哪些 workload 真的适合 CIM？答案不取决于“有没有很多 MAC”，而取决于权重复用、数据流规整性、精度容忍、写入频率、memory-bound 程度、fallback 成本和系统部署场景。

## 本章页面地图

| 页面 | 核心判断 |
| --- | --- |
| [Workload Characterization](./workload-characterization-for-cim.md) | 用哪些维度判断 workload 是否适合 CIM/PIM/NMC |
| [CNN on CIM](./cnn-on-cim.md) | 为什么 CNN 是标准场景，以及它的上限 |
| [Transformer on CIM](./transformer-on-cim.md) | projection/FFN、attention、KV cache 为什么不能混谈 |
| [LLM Decode and CIM](./llm-decode-and-cim.md) | decode 阶段为什么更偏 memory-side 路线 |
| [Edge AI and CIM](./edge-ai-and-cim.md) | 端侧为何更容易把 CIM 局部收益变成产品价值 |

## 三条 Paradigm 的 Workload 偏好

Analog CIM 偏低比特、固定权重、误差可容忍、MVM 密集的 workload，典型是 edge CNN、小模型和特定 always-on 检测。Digital CIM 更适合需要确定性精度、INT4/INT8、可量产 SoC 集成和较灵活权重更新的 workload。Mixed-signal CIM 适合愿意用数字校正和 QAT 换取一部分 analog 局部能效的中间地带。

DRAM/HBM/GDDR-PIM 更适合大容量 memory-side bottleneck，例如 LLM decode、long context、KV cache 和部分 memory-bound HPC。HBM base die、interposer 或 package-side compute 属于 NMC，评价重点是 package bandwidth、host offload 和软件接口。

Workload 判断至少要看 arithmetic intensity、weight reuse、activation movement、partial sum reduction、batch size、sequence length、KV cache、fallback ratio、latency target、power budget 和 thermal budget。适合 array MVM 只是第一关，端到端还要穿过 software partition、NoC、memory hierarchy 和 host/runtime。

## 一句话理解

Workload 是 CIM 价值的过滤器：规整、低比特、高复用、少 fallback 的任务更适合 CIM；memory-side 大容量瓶颈更可能走 PIM/NMC。

## 建模启示

workload 建模要记录 phase、operator mix、tensor shape、batch、reuse factor、precision sensitivity、weight update frequency、activation traffic、partial-sum reduction、fallback ratio、memory footprint、NoC traffic、host sync、latency target 和 energy target。Resource 是 macro/tile/memory/host，Topology 是 broadcast/reduction/memory path，Interaction 是 tensor movement 与 synchronization，Capability 是 op、precision、error tolerance 和 residency。
