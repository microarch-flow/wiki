# 06 Software Stack

上级：[CIM Wiki](../README.md)
相关：[05 Architecture And System](../05-architecture-and-system/README.md), [BUS: DMA Path](../../../BUS/wiki/04-microarchitecture-integration/dma-descriptor-fetch-data-move-writeback.md), [RAM: Data Movement First Principle](../../../RAM/wiki/09-ai-chip-memory-architecture/data-movement-first-principle.md), [NoC: DMA Interaction](../../../NoC/wiki/05-system-integration/dma-engine-noc-interaction.md), [FAB: Final Test](../../../FAB/wiki/05-final-test-and-reliability/final-test-methodology.md)

## 这页在回答什么问题

为什么 CIM 软件栈不是“把 GEMM 发给硬件”这么简单？因为 compiler/runtime 必须同时理解 array shape、weight residency、bit-width、encoding、calibration、error model、fallback、host DMA 和 memory hierarchy。

## 本章页面地图

| 页面 | 核心问题 | 软件栈风险 |
| --- | --- | --- |
| [Compilation Flow](./compilation-flow-overview.md) | 模型如何变成 CIM 可执行子图 | IR 表达不了硬件约束 |
| [Weight Mapping](./weight-mapping-to-arrays.md) | 权重如何切到 array/tile | tiling、duplication、folding 吃掉收益 |
| [Quantization for CIM](./quantization-for-cim.md) | 量化如何匹配电路精度 | nominal bit 与 effective precision 不一致 |
| [Model Adaptation](./model-adaptation-strategies.md) | QAT/noise-aware/retraining 如何介入 | 硬件误差不可建模 |
| [Runtime and Scheduling](./runtime-and-scheduling.md) | runtime 如何调度 write/read/fallback | host sync 和数据搬运吞掉收益 |
| [Software Stack Comparison](./software-stack-comparison.md) | SRAM/ReRAM/DRAM-PIM 软件难点何处不同 | 把 CIM/PIM/NMC 混成一种 runtime |

## 三条 Paradigm 的软件差异

Analog CIM 的软件栈必须表达低比特、ADC range、calibration、noise model、variation-aware mapping 和模型适配。Digital CIM 更接近传统 accelerator compiler，但仍要表达 bit-serial cycles、popcount、accumulator width 和 array residency。Mixed-signal CIM 要把 analog 局部计算与 digital correction 的边界写进 IR、quantization 和 runtime metadata。

DRAM/HBM/GDDR-PIM 的软件栈属于 memory-side offload，不是 CIM macro 编译；HBM base die、interposer 或 package-side compute 属于 NMC，需要按 host interface、memory command 或 die-to-die bandwidth 设计软件边界。

软件栈内部也要分层。offline compiler 负责 graph partition、quantization、mapping 和 codegen；deployment compiler 绑定具体 silicon profile、calibration 和 bad block map；runtime 负责调度、residency、DMA、fallback 和 health state；driver/host interface 负责 MMIO、doorbell、completion、IOMMU 和同步。

## 一句话理解

CIM 软件栈的核心任务是把模型图中的数值、数据流和误差约束，翻译成 array/tile/runtime 能稳定执行的计划。

## 工具链启示

CIM compiler 需要把硬件能力写成可查询约束：supported op、array shape、bit-width、encoding、ADC/SA 精度、weight update cost、calibration state、fallback target 和 transfer cost。runtime 不能只调度 kernel，还要管理 residency、DMA、校准、异常与混合执行。
