# BUS Wiki

> `BUS 不是“把模块接起来”的线网别名，而是在有限带宽、仲裁、时序、顺序性和软件可见约束下，把 CPU、DMA、memory、peripheral 和 accelerator 组织成可工作的事务系统。要真正理解 BUS，必须同时看 transaction、ordering、arbitration、backpressure、bridge、clock domain、协议族和系统路径。`

## Dashboard

| 你现在要做什么 | 直接入口 |
| --- | --- |
| 5 分钟快速建立判断力 | [BUS 在解决什么问题](./01-overview/problem-statement.md) |
| 5 分钟复习整套 BUS 主线 | [BUS 一页版总览](./07-reference/bus-one-page.md) |
| 第一次系统学习 BUS | [学习路线图](./01-overview/learning-roadmap.md) |
| 按你的目标选最短阅读路径 | [按目标学习 BUS](./01-overview/goal-oriented-navigation.md) |
| 先把 BUS、NoC、点到点链路分清 | [BUS vs NoC vs Point-to-Point](./02-fundamentals/bus-vs-noc-vs-point-to-point.md) |
| 先搞懂 transaction 基本对象 | [地址、数据、响应与事务语义](./02-fundamentals/transaction-address-data-response.md) |
| 抓住共享互连的核心矛盾 | [仲裁、顺序性与 Backpressure](./02-fundamentals/arbitration-ordering-backpressure.md) |
| 理解位宽、时钟和 burst 为什么重要 | [位宽、时钟、Burst 与延迟](./02-fundamentals/width-clock-burst-latency.md) |
| 快速分清 AXI / AHB / APB | [AXI / AHB / APB 对照](./03-on-chip-protocol-families/axi-ahb-apb-comparison.md) |
| 深入理解 AXI 为什么复杂 | [AXI Channel、ID 与 Outstanding](./03-on-chip-protocol-families/axi-channel-id-outstanding.md) |
| 先把 AXI 五通道握手看懂 | [AXI 五通道与 VALID/READY](./03-on-chip-protocol-families/axi-five-channels-handshake.md) |
| 细看 burst / 对齐 / 边界问题 | [AXI Burst、对齐与边界](./03-on-chip-protocol-families/axi-burst-alignment-boundary.md) |
| 看窄传输和 WSTRB 怎么影响实现 | [AXI Narrow Transfer 与 WSTRB](./03-on-chip-protocol-families/axi-narrow-transfer-wstrb.md) |
| 调试 response / decode / slave error | [AXI Response 与错误路径](./03-on-chip-protocol-families/axi-response-error-path.md) |
| 细看 AHB-Lite / APB 的使用边界 | [AHB-Lite 与 APB 深化](./03-on-chip-protocol-families/ahb-lite-and-apb-deep-dive.md) |
| 理解现代 SoC 为什么常见多层总线 | [分层总线与协议分工](./03-on-chip-protocol-families/hierarchical-bus-and-protocol-roles.md) |
| 对比 TileLink 和 AXI 的思路差别 | [TileLink 概览](./03-on-chip-protocol-families/tilelink-overview.md) |
| 把 BUS 放回 CPU / DMA / memory 路径里理解 | [CPU、DMA、外设与内存之间的总线路径](./04-microarchitecture-integration/dma-cpu-peripheral-memory-path.md) |
| 理解 bridge、CDC、width adapter 为什么不可省 | [Bridge、CDC 与 Width Adapter](./04-microarchitecture-integration/bridge-cdc-width-adaptation.md) |
| 快速比较 shared bus / bus matrix / crossbar | [Shared Bus、Bus Matrix 与 Crossbar](./04-microarchitecture-integration/shared-bus-bus-matrix-crossbar.md) |
| 理解 MMIO、cache、interrupt 如何映射到 BUS | [MMIO、Cache 与 Interrupt 视角](./04-microarchitecture-integration/mmio-cache-interrupt-view.md) |
| 看启动阶段总线是怎么被拉起来的 | [Boot Path 与地址映射初始化](./04-microarchitecture-integration/boot-path-address-map-initialization.md) |
| 看 debug master 如何接入系统 | [Debug Path 与 System Access](./04-microarchitecture-integration/debug-path-system-access.md) |
| 理解 DMA 地址为何离不开 IOMMU/SMMU | [IOMMU、SMMU 与 DMA 寻址](./04-microarchitecture-integration/iommu-smmu-dma-addressing.md) |
| 串起 doorbell、completion 和 interrupt | [Doorbell、Completion 与 Interrupt Flow](./04-microarchitecture-integration/doorbell-completion-interrupt-flow.md) |
| 看 AXI 和 DMA 是怎样真正连起来的 | [AXI 与 DMA 的系统接口](./04-microarchitecture-integration/axi-dma-system-interface.md) |
| 看 descriptor fetch / data move / writeback 三段链路 | [DMA Descriptor Fetch、Data Move 与 Writeback](./04-microarchitecture-integration/dma-descriptor-fetch-data-move-writeback.md) |
| 理解 cacheability、shareability 和 barrier | [AXI 属性、Cacheability 与 Barrier](./04-microarchitecture-integration/axi-attributes-cacheability-barrier.md) |
| 看 AXI 请求进入 DDR 后发生了什么 | [AXI 到 DDR Controller 的路径](./04-microarchitecture-integration/axi-to-ddr-controller-path.md) |
| 理解 read/write combine 和 turnaround | [Read/Write Combine 与 Bus Turnaround](./04-microarchitecture-integration/read-write-combine-turnaround.md) |
| 理解 row locality 如何反作用到总线体验 | [Row Locality、Return Path 与 AXI 体验](./04-microarchitecture-integration/row-locality-return-path-axi-experience.md) |
| 开始做性能分析 | [带宽、延迟、利用率与拥塞](./05-performance-debug/bandwidth-latency-utilization.md) |
| 开始做调试定位 | [争用、QoS 与可观测性](./05-performance-debug/contention-qos-observability.md) |
| 先分清 timeout / fault / hang | [Timeout、Fault 与 Hang 定位框架](./05-performance-debug/timeout-fault-hang-debug-framework.md) |
| 看总线计数器和 trace 点应该布在哪 | [Counters、Trace 与观测点设计](./05-performance-debug/counters-trace-observation-points.md) |
| 直接按波形排查 AXI 卡顿 | [AXI Waveform Debug 方法](./05-performance-debug/axi-waveform-debug-method.md) |
| 看不同系统为什么会选不同 BUS 组织 | [MCU / SoC / AI 芯片中的 BUS 对照](./06-scenarios-case-studies/mcu-soc-ai-bus-comparison.md) |
| 看一个典型片上互连案例 | [AXI Crossbar 案例卡](./06-scenarios-case-studies/axi-crossbar-case-card.md) |
| 看 CPU 读 MMIO 为什么会卡死 | [CPU 读 MMIO 卡死案例卡](./06-scenarios-case-studies/cpu-mmio-read-hang-case-card.md) |
| 看 DMA completion 为什么会丢失 | [DMA Completion 丢失案例卡](./06-scenarios-case-studies/dma-completion-missing-case-card.md) |
| 看 IOMMU fault 如何顺藤摸瓜 | [IOMMU Fault 案例卡](./06-scenarios-case-studies/iommu-fault-case-card.md) |
| 快速对比 AXI 和 TileLink | [AXI vs TileLink 对照](./06-scenarios-case-studies/axi-vs-tilelink-comparison.md) |
| 总结 AI 芯片里 BUS 和 NoC 的分工 | [AI 芯片里的 BUS vs NoC](./06-scenarios-case-studies/bus-vs-noc-in-ai-chip.md) |
| 从软件模型分清 APB、MMIO 和普通内存 | [APB、MMIO 与普通内存的软件模型对照](./06-scenarios-case-studies/apb-mmio-memory-software-model.md) |
| 做方案评审时快速过一遍 checklist | [BUS 设计检查清单](./07-reference/bus-design-checklist.md) |
| 分角色检查 master/slave/bridge 细节 | [Master/Slave/Bridge 设计清单](./07-reference/master-slave-bridge-checklists.md) |
| 补齐 DDR、IOMMU、Debug 集成检查点 | [DDR/IOMMU/Debug 集成清单](./07-reference/ddr-iommu-debug-checklists.md) |
| 快速查最容易混的概念 | [BUS 高频问题](./07-reference/high-frequency-questions.md) |
| 沉淀故障定位和方案评审记录 | [BUS 故障复盘模板](./07-reference/bus-debug-postmortem-template.md) / [互连方案评估模板](./07-reference/interconnect-evaluation-template.md) |
| 统一记录协议学习笔记 | [BUS 协议阅读模板](./07-reference/protocol-reading-template.md) |
| 快速查术语与检查清单 | [术语表](./07-reference/glossary.md) / [BUS 设计检查清单](./07-reference/bus-design-checklist.md) |

## 快速开始

### 路线 1：第一次学 BUS

1. [BUS 在解决什么问题](./01-overview/problem-statement.md)
2. [BUS 分类框架](./01-overview/taxonomy.md)
3. [BUS vs NoC vs Point-to-Point](./02-fundamentals/bus-vs-noc-vs-point-to-point.md)
4. [地址、数据、响应与事务语义](./02-fundamentals/transaction-address-data-response.md)
5. [学习路线图](./01-overview/learning-roadmap.md)
6. [按目标学习 BUS](./01-overview/goal-oriented-navigation.md)

### 路线 2：想把片上总线协议学透

1. [地址、数据、响应与事务语义](./02-fundamentals/transaction-address-data-response.md)
2. [仲裁、顺序性与 Backpressure](./02-fundamentals/arbitration-ordering-backpressure.md)
3. [位宽、时钟、Burst 与延迟](./02-fundamentals/width-clock-burst-latency.md)
4. [AXI / AHB / APB 对照](./03-on-chip-protocol-families/axi-ahb-apb-comparison.md)
5. [AXI Channel、ID 与 Outstanding](./03-on-chip-protocol-families/axi-channel-id-outstanding.md)
6. [AXI 五通道与 VALID/READY](./03-on-chip-protocol-families/axi-five-channels-handshake.md)
7. [AXI Burst、对齐与边界](./03-on-chip-protocol-families/axi-burst-alignment-boundary.md)
8. [AXI Narrow Transfer 与 WSTRB](./03-on-chip-protocol-families/axi-narrow-transfer-wstrb.md)
9. [AXI Response 与错误路径](./03-on-chip-protocol-families/axi-response-error-path.md)
10. [AHB-Lite 与 APB 深化](./03-on-chip-protocol-families/ahb-lite-and-apb-deep-dive.md)
11. [分层总线与协议分工](./03-on-chip-protocol-families/hierarchical-bus-and-protocol-roles.md)
12. [Coherent Bus vs Non-Coherent Bus](./03-on-chip-protocol-families/coherent-bus-vs-noncoherent-bus.md)
13. [TileLink 概览](./03-on-chip-protocol-families/tilelink-overview.md)

### 路线 3：想从系统与实现角度建立判断

1. [BUS vs NoC vs Point-to-Point](./02-fundamentals/bus-vs-noc-vs-point-to-point.md)
2. [互连组件与数据路径分解](./04-microarchitecture-integration/interconnect-components.md)
3. [Bridge、CDC 与 Width Adapter](./04-microarchitecture-integration/bridge-cdc-width-adaptation.md)
4. [Shared Bus、Bus Matrix 与 Crossbar](./04-microarchitecture-integration/shared-bus-bus-matrix-crossbar.md)
5. [MMIO、Cache 与 Interrupt 视角](./04-microarchitecture-integration/mmio-cache-interrupt-view.md)
6. [Boot Path 与地址映射初始化](./04-microarchitecture-integration/boot-path-address-map-initialization.md)
7. [Debug Path 与 System Access](./04-microarchitecture-integration/debug-path-system-access.md)
8. [IOMMU、SMMU 与 DMA 寻址](./04-microarchitecture-integration/iommu-smmu-dma-addressing.md)
9. [Doorbell、Completion 与 Interrupt Flow](./04-microarchitecture-integration/doorbell-completion-interrupt-flow.md)
10. [AXI 与 DMA 的系统接口](./04-microarchitecture-integration/axi-dma-system-interface.md)
11. [DMA Descriptor Fetch、Data Move 与 Writeback](./04-microarchitecture-integration/dma-descriptor-fetch-data-move-writeback.md)
12. [AXI 属性、Cacheability 与 Barrier](./04-microarchitecture-integration/axi-attributes-cacheability-barrier.md)
13. [AXI 到 DDR Controller 的路径](./04-microarchitecture-integration/axi-to-ddr-controller-path.md)
14. [Read/Write Combine 与 Bus Turnaround](./04-microarchitecture-integration/read-write-combine-turnaround.md)
15. [Row Locality、Return Path 与 AXI 体验](./04-microarchitecture-integration/row-locality-return-path-axi-experience.md)
16. [CPU、DMA、外设与内存之间的总线路径](./04-microarchitecture-integration/dma-cpu-peripheral-memory-path.md)
17. [带宽、延迟、利用率与拥塞](./05-performance-debug/bandwidth-latency-utilization.md)
18. [争用、QoS 与可观测性](./05-performance-debug/contention-qos-observability.md)
19. [Timeout、Fault 与 Hang 定位框架](./05-performance-debug/timeout-fault-hang-debug-framework.md)
20. [Counters、Trace 与观测点设计](./05-performance-debug/counters-trace-observation-points.md)
21. [AXI Waveform Debug 方法](./05-performance-debug/axi-waveform-debug-method.md)
22. [MCU / SoC / AI 芯片中的 BUS 对照](./06-scenarios-case-studies/mcu-soc-ai-bus-comparison.md)
23. [AXI Crossbar 案例卡](./06-scenarios-case-studies/axi-crossbar-case-card.md)
24. [CPU 读 MMIO 卡死案例卡](./06-scenarios-case-studies/cpu-mmio-read-hang-case-card.md)
25. [DMA Completion 丢失案例卡](./06-scenarios-case-studies/dma-completion-missing-case-card.md)
26. [IOMMU Fault 案例卡](./06-scenarios-case-studies/iommu-fault-case-card.md)

## 工作台

### 学习

- [概览与问题定义](./01-overview/README.md)
- [按目标学习 BUS](./01-overview/goal-oriented-navigation.md)
- [基础对象与事务语义](./02-fundamentals/README.md)
- [片上总线协议族](./03-on-chip-protocol-families/README.md)
- [微架构与系统集成](./04-microarchitecture-integration/README.md)
- [典型系统与案例](./06-scenarios-case-studies/README.md)
- [AXI Channel、ID 与 Outstanding](./03-on-chip-protocol-families/axi-channel-id-outstanding.md)
- [AXI 五通道与 VALID/READY](./03-on-chip-protocol-families/axi-five-channels-handshake.md)
- [AXI Burst、对齐与边界](./03-on-chip-protocol-families/axi-burst-alignment-boundary.md)
- [MMIO、Cache 与 Interrupt 视角](./04-microarchitecture-integration/mmio-cache-interrupt-view.md)
- [IOMMU、SMMU 与 DMA 寻址](./04-microarchitecture-integration/iommu-smmu-dma-addressing.md)
- [DMA Descriptor Fetch、Data Move 与 Writeback](./04-microarchitecture-integration/dma-descriptor-fetch-data-move-writeback.md)
- [AXI 到 DDR Controller 的路径](./04-microarchitecture-integration/axi-to-ddr-controller-path.md)

### 分析

- [性能与调试](./05-performance-debug/README.md)
- [带宽、延迟、利用率与拥塞](./05-performance-debug/bandwidth-latency-utilization.md)
- [争用、QoS 与可观测性](./05-performance-debug/contention-qos-observability.md)
- [Timeout、Fault 与 Hang 定位框架](./05-performance-debug/timeout-fault-hang-debug-framework.md)
- [AXI Waveform Debug 方法](./05-performance-debug/axi-waveform-debug-method.md)
- [BUS 设计检查清单](./07-reference/bus-design-checklist.md)

### 案例

- [AXI Crossbar 案例卡](./06-scenarios-case-studies/axi-crossbar-case-card.md)
- [CPU 读 MMIO 卡死案例卡](./06-scenarios-case-studies/cpu-mmio-read-hang-case-card.md)
- [DMA Completion 丢失案例卡](./06-scenarios-case-studies/dma-completion-missing-case-card.md)
- [IOMMU Fault 案例卡](./06-scenarios-case-studies/iommu-fault-case-card.md)
- [AXI vs TileLink 对照](./06-scenarios-case-studies/axi-vs-tilelink-comparison.md)
- [AI 芯片里的 BUS vs NoC](./06-scenarios-case-studies/bus-vs-noc-in-ai-chip.md)
- [APB、MMIO 与普通内存的软件模型对照](./06-scenarios-case-studies/apb-mmio-memory-software-model.md)

### 查阅

- [BUS 一页版总览](./07-reference/bus-one-page.md)
- [术语表](./07-reference/glossary.md)
- [BUS 高频问题](./07-reference/high-frequency-questions.md)
- [知识地图](./SUMMARY.md)

## 这套 Wiki 的边界

这套 wiki 的主线不是：

- 把外部高速串行协议都混进来讲
- 把 cache coherence 协议细节完整展开重写
- 只讲某一家 IP 的寄存器或用户手册

这套 wiki 的主线是：

- 把 BUS 作为 `片上事务互连层` 来理解
- 同时覆盖 `master / slave / ordering / arbitration / bridge / protocol family`
- 建立 `能解释系统瓶颈、能支持方案选型、能指导调试` 的知识结构

## 维护原则

- 每页尽量只回答一个核心问题
- 优先区分 `transaction / protocol / interconnect / integration / observability`
- 优先保留能转化成工程判断和系统分析的内容
- 与 [DMA Wiki](../../DMA/wiki/README.md)、[NOC Wiki](../../NOC/wiki/README.md)、[RAM Wiki](../../RAM/wiki/README.md) 保持可互相链接的术语体系
