# Memory Wall 与 Von Neumann Bottleneck：为什么 CIM 在 AI 时代被重新点燃

上级：[01 Overview](./README.md)
相关：[CIM/PIM/NMC 的严格区分](./cim-pim-nmc-taxonomy.md), [两条正交主线](./two-axes-memory-and-paradigm.md), [RAM: Data Movement First Principle](../../../RAM/wiki/09-ai-chip-memory-architecture/data-movement-first-principle.md)

## 这页在回答什么问题

为什么 AI 芯片已经有很强的 MAC array、tensor core 和 HBM 带宽，业界仍然反复回到 CIM/PIM/NMC？真正的问题不是“还能不能再做一个更快的 MAC”，而是哪些 workload 的能耗、延迟和面积已经被数据搬运主导。

## 传统路径的问题不在一层 memory

AI 推理和训练的常见数据路径可以粗略写成：

```text
DRAM / HBM
  -> memory controller
  -> on-chip SRAM / cache / scratchpad
  -> NoC / bus
  -> MAC array / tensor core
  -> reduction / writeback
```

这条路径的每一跳都在消耗能量和时延。一次低比特 MAC 的能耗可以做到很低，但把权重、激活和 partial sum 在 HBM、SRAM、NoC 和计算阵列之间反复搬运，往往比计算本身更贵。RAM wiki 的 [data movement first principle](../../../RAM/wiki/09-ai-chip-memory-architecture/data-movement-first-principle.md) 已经从 AI memory hierarchy 角度讲过这个问题；CIM/PIM/NMC 是同一矛盾在器件、电路和系统边界上的另一种回应。

这也是 von Neumann bottleneck 在 AI 时代重新变尖的原因：模型变大后，计算和存储分离不只是抽象架构问题，而是具体的 bandwidth、energy per byte、buffer capacity、NoC congestion 和 host synchronization 问题。

## CIM/PIM/NMC 试图减少的不是同一种搬运

CIM、PIM、NMC 都在把计算推向数据，但它们减少的数据路径不同：

| 路线 | 主要减少的搬运 | 代价 |
| --- | --- | --- |
| CIM | memory array 内外的数据读取、局部乘加和局部归约搬运 | cell 稳定性、ADC/SA/peripheral 开销、精度和校准 |
| PIM | processor 与 memory die/bank 内 processing unit 之间的往返 | memory command/interface、host/runtime 协同、算子能力受限 |
| NMC | host/accelerator 与 memory subsystem 之间的远距离搬运 | 与 memory 的物理距离更远，收益依赖系统集成和软件接口 |

因此，“减少 data movement”不是足够精确的说法。评估一条路线时必须追问：减少的是 array read、tile 间 partial sum、HBM 到 GPU 的往返，还是 CPU/GPU 与 memory module 之间的系统级搬运？不同答案会把路线导向完全不同的电路、架构和软件设计。

## AI workload 为什么重新放大这个问题

CNN 让早期 CIM 论文容易展示价值，因为卷积和 MVM/GEMM 结构规整，权重复用高，固定模型推理适合 weight-stationary 映射。Transformer 和 LLM 让问题变复杂：prefill 阶段大 GEMM 很多，成熟 GPU/NPU 已经高度优化；decode 阶段 batch 小、token 逐步生成，KV cache、权重读取和 memory bandwidth 更容易成为瓶颈。MoE 又引入 routing、稀疏访问和负载不均衡。

这意味着 CIM 不会自动因为“AI 需要大量 MAC”而成立。它只在某个 workload 的关键瓶颈恰好能被靠近 memory 的计算减少时成立。对于 LLM decode 和 long-context attention，PIM/NMC 往往比 array-native CIM 更自然，因为瓶颈更接近大容量 memory-side access；对于低功耗 edge CNN 或小模型推理，SRAM-CIM 和部分 ReRAM/Flash CIM 更容易把 macro-level 节能转成系统收益。

## 为什么不能把 CIM 说成“解决 memory wall”

“解决 memory wall”是一个过大的说法。CIM 可以减少某些局部路径上的搬运，但它不会消除模型权重容量、activation buffering、tile 间 communication、host fallback 和软件映射问题。一个 ReRAM crossbar 可以在 array 内高效做 MVM，但如果 ADC、DAC、校准、buffer 和 NoC 把收益吃掉，system-level energy per inference 仍然可能不占优。

更准确的判断方式是：CIM/PIM/NMC 把 memory wall 从一个“外部带宽问题”拆成多个层级的设计问题。cell 是否能算、macro 是否高效、tile 是否能归约、chip 是否能喂饱、runtime 是否能少切换，这些层级任何一个失败，局部指标都无法自动外推到产品价值。

## 常见误解

常见误解：CIM 的价值等于更高 TOPS/W。实际上，TOPS/W 只有在注明层级、精度、workload 和是否包含外围后才有比较意义。

常见误解：LLM 让所有 CIM 路线都更有价值。实际上，LLM 让 memory-bound 问题更突出，但不同阶段的瓶颈不同，decode/KV cache 更偏 PIM/NMC 机会，prefill 的大 GEMM 未必让 CIM 优于成熟 NPU/GPU。

常见误解：把计算单元放到内存旁边就叫 CIM。实际上，如果 memory cell、bitline、wordline 或紧邻 cell 的 array path 没有参与计算，本 wiki 不称为 CIM。

## 一句话理解

CIM/PIM/NMC 的共同动机是减少数据搬运，但它们分别在 array、memory die/bank 和 memory-adjacent system 三个层级下注，不能用同一个“更省电的 MAC”叙事概括。
