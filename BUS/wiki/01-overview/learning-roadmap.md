# 学习路线图

上级：[01 概览与问题定义](./README.md)

相关：[BUS Wiki 首页](../README.md)、[知识地图](../SUMMARY.md)

## 这页在回答什么问题

如果你想系统掌握 BUS，最短的有效学习顺序是什么。

## 路线 1：建立最小判断框架

1. [BUS 在解决什么问题](./problem-statement.md)
2. [BUS 分类框架](./taxonomy.md)
3. [BUS vs NoC vs Point-to-Point](../02-fundamentals/bus-vs-noc-vs-point-to-point.md)
4. [地址、数据、响应与事务语义](../02-fundamentals/transaction-address-data-response.md)

目标是先分清：

- BUS 为什么存在
- 它和 NoC 的边界在哪里
- 一个事务最少包含哪些对象

## 路线 2：把协议读懂

1. [仲裁、顺序性与 Backpressure](../02-fundamentals/arbitration-ordering-backpressure.md)
2. [位宽、时钟、Burst 与延迟](../02-fundamentals/width-clock-burst-latency.md)
3. [AXI / AHB / APB 对照](../03-on-chip-protocol-families/axi-ahb-apb-comparison.md)
4. [Coherent Bus vs Non-Coherent Bus](../03-on-chip-protocol-families/coherent-bus-vs-noncoherent-bus.md)

目标是建立：

- 看协议时知道自己在看什么
- 看性能问题时知道瓶颈可能落在哪

## 路线 3：把系统实现看透

1. [互连组件与数据路径分解](../04-microarchitecture-integration/interconnect-components.md)
2. [Bridge、CDC 与 Width Adapter](../04-microarchitecture-integration/bridge-cdc-width-adaptation.md)
3. [CPU、DMA、外设与内存之间的总线路径](../04-microarchitecture-integration/dma-cpu-peripheral-memory-path.md)
4. [带宽、延迟、利用率与拥塞](../05-performance-debug/bandwidth-latency-utilization.md)
5. [争用、QoS 与可观测性](../05-performance-debug/contention-qos-observability.md)

目标是把 BUS 从“协议文档”提升到“系统分析工具”。

## 最后再看案例

- [MCU / SoC / AI 芯片中的 BUS 对照](../06-scenarios-case-studies/mcu-soc-ai-bus-comparison.md)
- [AXI Crossbar 案例卡](../06-scenarios-case-studies/axi-crossbar-case-card.md)

## 一句话理解

先学事务语义，再学协议机制，再看系统集成，最后用案例固化判断。
