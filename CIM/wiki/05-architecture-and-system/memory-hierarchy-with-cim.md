# CIM 系统的存储层次：On-Array、Buffer、Main Memory 的分工

上级：[05 Architecture And System](./README.md)
相关：[RAM: NPU Memory Hierarchy](../../../RAM/wiki/09-ai-chip-memory-architecture/npu-memory-hierarchy.md), [RAM: Scratchpad vs Cache](../../../RAM/wiki/03-sram-applications/scratchpad-vs-cache.md), [RAM: DRAM Commands](../../../RAM/wiki/05-dram-protocol-families/commands-act-rd-wr-pre.md)

## 这页在回答什么问题

CIM 把一部分计算放进 memory array，是否就简化了 memory hierarchy？不会。它只是新增了 on-array compute/storage 这一层，其他 buffer、SRAM、HBM、DMA 和 host memory 仍要分工。

## 层次分工

| 层级 | 存什么 | 风险 |
| --- | --- | --- |
| on-array cell | weights 或局部 bit state | 容量、写入、误差、驻留策略 |
| macro buffer | input/output/partial sum | 面积、带宽、双缓冲 |
| tile SRAM | activation、scale、metadata | reuse 与调度复杂度 |
| global SRAM / LLC | layer 间数据 | 容量和 NoC traffic |
| HBM/DRAM | 大模型权重和 KV/cache | 带宽、latency、energy per byte |
| host memory | runtime 管理和 fallback | 同步和接口成本 |

CIM 的关键不是消灭上层 memory，而是减少某些高复用数据在层级间反复移动。RAM wiki 的 [data movement first principle](../../../RAM/wiki/09-ai-chip-memory-architecture/data-movement-first-principle.md) 仍然适用；tile 级 SRAM 更接近 [scratchpad/cache](../../../RAM/wiki/03-sram-applications/scratchpad-vs-cache.md) 的系统分工，而不是 CIM 定义本身。

## 三条 Paradigm 的层次差异

Analog ReRAM/Flash CIM 更依赖权重驻留，因为写入和校准成本高。memory hierarchy 要支持少换权重、多流 activation、低频校准和结果回收。

Digital SRAM-CIM 更接近传统 NPU memory hierarchy。它可以更灵活更新权重和 activation，但容量有限，常常需要上层 SRAM/HBM 持续供给，系统收益取决于 reuse 与 tiling。

Mixed-signal CIM 需要额外存储 scale、calibration、noise model 或 correction 参数。它的 hierarchy 不只存 tensor，还存硬件状态。

## DRAM/HBM/GDDR-PIM 与 NMC 的区别

PIM 把 compute 放进 memory die/bank 内独立单元，目标是减少 processor-memory 往返；它不是 on-array CIM hierarchy。PIM 的 hierarchy 要建模 bank/channel 粒度、command queue、result return 和 host-visible offload，背景可见 RAM wiki 的 [bank organization](../../../RAM/wiki/04-dram-foundations/bank-organization-parallelism.md)、[HBM stacked wide-IO](../../../RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io.md) 与 [DRAM command timing](../../../RAM/wiki/05-dram-protocol-families/commands-act-rd-wr-pre.md)。

若 compute 放在 HBM base die、interposer 或 package-side logic，它属于 NMC。NMC hierarchy 要建模 die-to-die/package bandwidth、HBM stack proximity、coherency/interface 和 host offload latency，而不是 DRAM bank 内 command execution。

## 一句话理解

CIM 不是把 memory hierarchy 变平，而是在最底层新增一个能计算的存储层，并把一部分复杂度转移到 buffer、metadata、calibration 和 host 协同。

## 建模启示

memory hierarchy 模型要区分 capacity、bandwidth、latency、energy per access、bank count、port count、reuse distance、fetch/replacement policy、residency、write/update cost、KV/cache placement 和 metadata storage。on-array 细节可抽象成 Resource 的容量与 Capability，但 weight reload、activation double-buffering、partial sum storage、bank conflict、data placement 和 calibration metadata 必须保留为 Interaction。
