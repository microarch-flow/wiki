# 知识地图

这页只保留章节级入口。

如果你要：

- 快速开始：看 [首页](./README.md)
- 学协议基础：看 [基础对象与事务语义](./02-fundamentals/README.md)
- 做系统分析：看 [微架构与系统集成](./04-microarchitecture-integration/README.md)

## 01 概览与问题定义

- [首页](./01-overview/README.md)
- [BUS 在解决什么问题](./01-overview/problem-statement.md)
- [BUS 分类框架](./01-overview/taxonomy.md)
- [学习路线图](./01-overview/learning-roadmap.md)
- [按目标学习 BUS](./01-overview/goal-oriented-navigation.md)

## 02 基础对象与事务语义

- [首页](./02-fundamentals/README.md)
- [BUS vs NoC vs Point-to-Point](./02-fundamentals/bus-vs-noc-vs-point-to-point.md)
- [地址、数据、响应与事务语义](./02-fundamentals/transaction-address-data-response.md)
- [仲裁、顺序性与 Backpressure](./02-fundamentals/arbitration-ordering-backpressure.md)
- [位宽、时钟、Burst 与延迟](./02-fundamentals/width-clock-burst-latency.md)

## 03 片上总线协议族

- [首页](./03-on-chip-protocol-families/README.md)
- [AXI / AHB / APB 对照](./03-on-chip-protocol-families/axi-ahb-apb-comparison.md)
- [AXI Channel、ID 与 Outstanding](./03-on-chip-protocol-families/axi-channel-id-outstanding.md)
- [AXI 五通道与 VALID/READY](./03-on-chip-protocol-families/axi-five-channels-handshake.md)
- [AXI Burst、对齐与边界](./03-on-chip-protocol-families/axi-burst-alignment-boundary.md)
- [AXI Narrow Transfer 与 WSTRB](./03-on-chip-protocol-families/axi-narrow-transfer-wstrb.md)
- [AXI Response 与错误路径](./03-on-chip-protocol-families/axi-response-error-path.md)
- [AHB-Lite 与 APB 深化](./03-on-chip-protocol-families/ahb-lite-and-apb-deep-dive.md)
- [分层总线与协议分工](./03-on-chip-protocol-families/hierarchical-bus-and-protocol-roles.md)
- [Coherent Bus vs Non-Coherent Bus](./03-on-chip-protocol-families/coherent-bus-vs-noncoherent-bus.md)
- [TileLink 概览](./03-on-chip-protocol-families/tilelink-overview.md)

## 04 微架构与系统集成

- [首页](./04-microarchitecture-integration/README.md)
- [互连组件与数据路径分解](./04-microarchitecture-integration/interconnect-components.md)
- [Bridge、CDC 与 Width Adapter](./04-microarchitecture-integration/bridge-cdc-width-adaptation.md)
- [Shared Bus、Bus Matrix 与 Crossbar](./04-microarchitecture-integration/shared-bus-bus-matrix-crossbar.md)
- [MMIO、Cache 与 Interrupt 视角](./04-microarchitecture-integration/mmio-cache-interrupt-view.md)
- [Boot Path 与地址映射初始化](./04-microarchitecture-integration/boot-path-address-map-initialization.md)
- [Debug Path 与 System Access](./04-microarchitecture-integration/debug-path-system-access.md)
- [IOMMU、SMMU 与 DMA 寻址](./04-microarchitecture-integration/iommu-smmu-dma-addressing.md)
- [Doorbell、Completion 与 Interrupt Flow](./04-microarchitecture-integration/doorbell-completion-interrupt-flow.md)
- [AXI 与 DMA 的系统接口](./04-microarchitecture-integration/axi-dma-system-interface.md)
- [DMA Descriptor Fetch、Data Move 与 Writeback](./04-microarchitecture-integration/dma-descriptor-fetch-data-move-writeback.md)
- [AXI 属性、Cacheability 与 Barrier](./04-microarchitecture-integration/axi-attributes-cacheability-barrier.md)
- [AXI 到 DDR Controller 的路径](./04-microarchitecture-integration/axi-to-ddr-controller-path.md)
- [Read/Write Combine 与 Bus Turnaround](./04-microarchitecture-integration/read-write-combine-turnaround.md)
- [Row Locality、Return Path 与 AXI 体验](./04-microarchitecture-integration/row-locality-return-path-axi-experience.md)
- [CPU、DMA、外设与内存之间的总线路径](./04-microarchitecture-integration/dma-cpu-peripheral-memory-path.md)

## 05 性能与调试

- [首页](./05-performance-debug/README.md)
- [带宽、延迟、利用率与拥塞](./05-performance-debug/bandwidth-latency-utilization.md)
- [争用、QoS 与可观测性](./05-performance-debug/contention-qos-observability.md)
- [Timeout、Fault 与 Hang 定位框架](./05-performance-debug/timeout-fault-hang-debug-framework.md)
- [Counters、Trace 与观测点设计](./05-performance-debug/counters-trace-observation-points.md)
- [AXI Waveform Debug 方法](./05-performance-debug/axi-waveform-debug-method.md)

## 06 典型系统与案例

- [首页](./06-scenarios-case-studies/README.md)
- [MCU / SoC / AI 芯片中的 BUS 对照](./06-scenarios-case-studies/mcu-soc-ai-bus-comparison.md)
- [AXI Crossbar 案例卡](./06-scenarios-case-studies/axi-crossbar-case-card.md)
- [APB Peripheral Subsystem 案例卡](./06-scenarios-case-studies/apb-peripheral-subsystem-case-card.md)
- [CPU 读 MMIO 卡死案例卡](./06-scenarios-case-studies/cpu-mmio-read-hang-case-card.md)
- [DMA Completion 丢失案例卡](./06-scenarios-case-studies/dma-completion-missing-case-card.md)
- [IOMMU Fault 案例卡](./06-scenarios-case-studies/iommu-fault-case-card.md)
- [AXI vs TileLink 对照](./06-scenarios-case-studies/axi-vs-tilelink-comparison.md)
- [AI 芯片里的 BUS vs NoC](./06-scenarios-case-studies/bus-vs-noc-in-ai-chip.md)
- [APB、MMIO 与普通内存的软件模型对照](./06-scenarios-case-studies/apb-mmio-memory-software-model.md)

## 07 术语与检查清单

- [首页](./07-reference/README.md)
- [BUS 一页版总览](./07-reference/bus-one-page.md)
- [术语表](./07-reference/glossary.md)
- [BUS 设计检查清单](./07-reference/bus-design-checklist.md)
- [Master/Slave/Bridge 设计清单](./07-reference/master-slave-bridge-checklists.md)
- [DDR/IOMMU/Debug 集成清单](./07-reference/ddr-iommu-debug-checklists.md)
- [BUS 高频问题](./07-reference/high-frequency-questions.md)
- [BUS 故障复盘模板](./07-reference/bus-debug-postmortem-template.md)
- [互连方案评估模板](./07-reference/interconnect-evaluation-template.md)
- [BUS 协议阅读模板](./07-reference/protocol-reading-template.md)

## 08 建模与架构探索

- [首页](./08-modeling/README.md)
- [BUS 建模参考](./08-modeling/bus-modeling-reference.md)
