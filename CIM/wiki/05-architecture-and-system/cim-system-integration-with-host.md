# CIM 加速器与 Host 的集成：从 PCIe Attached 到 SoC 内嵌

上级：[05 Architecture And System](./README.md)
相关：[BUS: MMIO Cache Interrupt View](../../../BUS/wiki/04-microarchitecture-integration/mmio-cache-interrupt-view.md), [BUS: AXI DMA System Interface](../../../BUS/wiki/04-microarchitecture-integration/axi-dma-system-interface.md), [DRAM-PIM 深入](../02-memory-technologies/dram-pim-deep-dive.md)

## 这页在回答什么问题

CIM 系统如何接入真实 host？无论是 SoC 内嵌、chiplet、PCIe card 还是 memory-side device，最终都需要 command、DMA、地址空间、同步、异常处理和 fallback 路径。

## 三种集成形态

SoC 内嵌 CIM 更容易共享片上 SRAM、NoC、DMA 和 runtime，延迟低，适合 edge AI 或固定 function block。代价是面积、验证和工艺风险进入主芯片。

PCIe attached CIM accelerator 可降低主 SoC 集成风险，但 host-device 往返、driver、DMA 和 batch 粒度会决定收益。若 workload 需要频繁小粒度同步，PCIe 延迟会吞掉 macro 优势。

Memory-side PIM/NMC 形态更接近 DRAM/HBM/GDDR-PIM、HBM base die NMC 或 memory module compute。PIM 位于 memory die/bank 内；HBM base die、interposer、package-side logic 属于 NMC。它们的 host 集成重点是 memory command、controller、address mapping 和 runtime offload。

## 三条 Paradigm 的 Host 压力

Analog CIM 对 host 的压力来自校准、模型版本、精度状态和 fallback。host/runtime 需要知道哪些 layer 能在 CIM 上跑、哪些需要数字 NPU/CPU/GPU 接管，以及校准参数何时更新。

Digital CIM 对 host 更像普通 accelerator，但仍需要表达 bit-width、dataflow、weight residency 和 unsupported op。它的优势是 deterministic behavior 更容易被 driver/runtime 管理。

Mixed-signal CIM 需要 host 或 runtime 处理更多 metadata：scale、zero-point、calibration table、noise profile、tile health 和 model adaptation 状态。

## 接口机制

MMIO 适合配置寄存器、doorbell 和状态查询；DMA 负责 activation、weight、output 和 calibration data 的搬运；interrupt/completion 负责同步。BUS wiki 的 [doorbell completion interrupt flow](../../../BUS/wiki/04-microarchitecture-integration/doorbell-completion-interrupt-flow.md) 和 [IOMMU/SMMU DMA addressing](../../../BUS/wiki/04-microarchitecture-integration/iommu-smmu-dma-addressing.md) 是这类集成的直接背景。

SoC 内 CIM 还要经过片上 NoC 和 memory hierarchy，可对照 NoC wiki 的 [tile architecture](../../../NoC/wiki/06-ai-noc-specifics/tile-architecture-and-noc.md) 与 RAM wiki 的 [NPU memory hierarchy](../../../RAM/wiki/09-ai-chip-memory-architecture/npu-memory-hierarchy.md)；PCIe card 要经过 host memory、IOMMU、DMA engine 和 driver；PIM/NMC 要通过 memory controller 或 vendor runtime 暴露能力。

## 一句话理解

CIM 的 host integration 决定 macro 能力如何变成可调用系统能力；接口粒度、同步和 fallback 常常比峰值算力更早限制部署价值。

## 建模启示

host 集成模型要记录 command latency、DMA bandwidth、setup overhead、batch size、fallback ratio、synchronization frequency、address mapping 和 runtime capability discovery。Resource 是 host、device、DMA、memory controller 和 accelerator queues；Topology 是 SoC/PCIe/memory-side 连接；Interaction 是 command、DMA、interrupt 和 fallback；Capability 是 runtime 能发现并调度的 CIM/PIM/NMC 能力。早期架构模型可折叠 driver 内部状态机，但不能忽略 host-device boundary，否则会高估小粒度 workload 的收益。
