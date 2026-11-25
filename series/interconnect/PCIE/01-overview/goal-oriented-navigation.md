---
title: "按目标学习 PCIe"
---

<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# 按目标学习 PCIe

上级：[概览与问题定义](README.md)

这里按工程任务选择阅读入口，不重复顺序学习课程。缺少前置概念时，回到[学习路线图](learning-roadmap.md)；需要完整目录时，查看[知识地图](../SUMMARY.md)。

<div id="目标-1先建立系统判断力" class="pcie-legacy-anchor"></div>

## 先判断系统边界

从[系统问题](problem-statement.md)和[拓扑](../02-link-transaction-basics/topology-root-complex-switch-endpoint.md)开始，再读 [PCIe、AXI 与 NoC 的边界](../06-workloads-case-studies/pcie-vs-axi-noc-boundary.md)。目标是画出请求者、目标和桥，而不是比较几个协议名称。

<div id="目标-2做设备驱动或-host-device-软件路径" class="pcie-legacy-anchor"></div>

## 实现驱动或设备数据路径

先读[第一次寄存器读与 BAR](../03-configuration-enumeration-addressing/config-space-bar-capability.md)、[地址视角](../03-configuration-enumeration-addressing/mmio-config-dma-address-view.md)和[缓冲区可见性](../04-data-path-dma-interrupts/host-memory-pinned-buffer-visibility.md)，再读[DMA 读写](../04-data-path-dma-interrupts/device-dma-read-write-flow.md)与[队列通知](../04-data-path-dma-interrupts/queues-doorbells-completions-msix.md)。

目标是为每个描述符地址说明映射来源，并明确何时可以复用缓冲区。

<div id="目标-3做-bring-up验证或调试定位" class="pcie-legacy-anchor"></div>

## 调试设备不可用或报错

设备看不见，从[发现、资源与启动失败](../06-workloads-case-studies/enumeration-failure-case-card.md)开始；已能运行但出错，从 [AER](../05-performance-debug/aer-counters-link-debug.md)和 [UR、CA、Timeout](../05-performance-debug/common-failures-ur-ca-timeout.md)开始。用[调试清单](../08-reference/pcie-debug-checklist.md)保存检查结果。

<div id="目标-4做性能分析和方案判断" class="pcie-legacy-anchor"></div>

## 分析吞吐与延迟

先用[性能参数](../05-performance-debug/bandwidth-latency-credit-mps-mrrs.md)确定计数边界，再读[信用与重放](../02-link-transaction-basics/credit-flow-control-and-replay.md)、[读并发](../04-data-path-dma-interrupts/pcie-read-completion-latency.md)和[瓶颈定位](../05-performance-debug/host-device-bottleneck-breakdown.md)。公式查[建模速查](../08-reference/pcie-modeling-params.md)。

目标是提出可被计数器或对照实验否定的瓶颈假设。

<div id="目标-5做虚拟化多租户或平台架构" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 设计虚拟化、共享地址或 P2P

先读 [IOMMU](../03-configuration-enumeration-addressing/iommu-address-translation-device-isolation.md)，再分别读 [SR-IOV 与地址空间扩展](../07-advanced-topics/sriov-ats-pasid-pri-overview.md)、[P2P 路由条件](../07-advanced-topics/p2p-switch-topology-constraints.md)。只有涉及一致性或设备内存语义时，再进入 [CXL 边界](../07-advanced-topics/cxl-and-pcie-boundary.md)。

目标是列出设备、主机、驱动和隔离策略分别必须满足的条件，避免把“声明支持”当成“路径已可用”。
