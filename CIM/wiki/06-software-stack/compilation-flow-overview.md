# CIM 编译流程总览：模型到算子再到 Macro 映射

上级：[06 Software Stack](./README.md)
相关：[Dataflow Mapping](../05-architecture-and-system/dataflow-mapping-on-cim.md), [BUS: MMIO and Interrupt](../../../BUS/wiki/04-microarchitecture-integration/mmio-cache-interrupt-view.md), [RAM: SRAM Array](../../../RAM/wiki/02-sram-foundations/sram-array-organization.md), [NoC: Tile Architecture](../../../NoC/wiki/06-ai-noc-specifics/tile-architecture-and-noc.md), [FAB: Process Variation](../../../FAB/wiki/02-front-end-fabrication/process-nodes-and-ppa-tradeoffs.md)

## 这页在回答什么问题

一个模型怎样真正跑到 CIM 上？软件栈必须先识别可映射子图，再 lowering 成硬件友好的 IR，最后把张量、权重、scale、calibration 和 fallback 路径一起交给 runtime。

## 编译流程

```text
model graph
  -> op canonicalization
  -> CIM-friendly subgraph detection
  -> quantization / encoding decision
  -> array and tile mapping
  -> fallback partition
  -> runtime command stream
  -> host / DMA / completion handling
```

这条链上任何一步缺失，都会让“macro 支持 MVM”停留在 kernel demo，而不是完整部署。

## IR 必须表达什么

IR 至少要表达 tensor shape、layout、dataflow、bit-width、weight residency、partial sum location、calibration metadata、error budget、supported fallback target 和 transfer cost。传统 graph IR 只表达算子依赖不够，因为 CIM 的执行合法性取决于 array shape、encoding 和硬件状态。

Analog CIM 需要 IR 表达 ADC bit、scale、noise profile、calibration table 和 variation-aware placement。Digital CIM 需要表达 bit-serial cycle、popcount、accumulator width 和 deterministic latency。Mixed-signal CIM 需要表达 analog/digital 边界，以及数字校正发生在 macro、tile 还是 runtime。

## Graph Partition

真实模型很少整网都适合 CIM。GEMM、MVM、Conv lowering 后的矩阵乘、Transformer projection 和 FFN 更自然；softmax、normalization、sampling、动态控制流和小粒度 scalar op 常需要 CPU/GPU/NPU fallback。

partition 粒度越细，理论利用率越高，但 host synchronization、DMA、layout conversion 和 cache pollution 越重。BUS wiki 的 doorbell、completion、DMA 路径会直接影响这个边界。

## PIM/NMC 编译边界

DRAM/HBM/GDDR-PIM 的 compiler 目标是 memory-side command/offload，不是 array mapping。它要表达 bank/channel 粒度、memory command、result return 和 host coordination。HBM base die、interposer 或 package-side compute 属于 NMC，更像靠近 memory subsystem 的 accelerator，需要 die-to-die/package bandwidth 和 runtime offload 模型。

## 一句话理解

CIM 编译不是把矩阵乘切块这么简单，而是把数值、阵列、误差、数据搬运和 fallback 同时纳入 IR 与 runtime plan。

## 工具链启示

编译器前端要能标注 CIM-capable 子图，IR 要携带硬件约束，后端要生成 array/tile mapping 与 host command stream。不能被 IR 表达的约束会落到手工脚本和 runtime hack，最终限制产品化。
