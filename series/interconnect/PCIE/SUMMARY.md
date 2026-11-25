---
title: "PCIe 知识地图"
---

<div id="知识地图" class="pcie-legacy-anchor"></div>

# PCIe 知识地图

本页是全部文章索引。顺序学习见[学习路线图](01-overview/learning-roadmap.md)，问题定位见[目标导航](01-overview/goal-oriented-navigation.md)。

## 01 概览与问题定义

[章节导读](01-overview/README.md)

- [PCIe 解决什么问题](01-overview/problem-statement.md)

- [问题地图](01-overview/taxonomy.md)

- [学习路线图](01-overview/learning-roadmap.md)

- [按目标学习](01-overview/goal-oriented-navigation.md)

## 02 链路、分层与事务基础

[章节导读](02-link-transaction-basics/README.md)

- [拓扑与角色](02-link-transaction-basics/topology-root-complex-switch-endpoint.md)

- [协议三层职责](02-link-transaction-basics/layered-architecture-transaction-data-link-physical.md)

- [一次读取与 Completion](02-link-transaction-basics/tlp-dllp-completion-basics.md)

- [信用流控与链路重放](02-link-transaction-basics/credit-flow-control-and-replay.md)

- [请求类型与排序](02-link-transaction-basics/posted-nonposted-completion-ordering.md)

## 03 配置、枚举与地址映射

[章节导读](03-configuration-enumeration-addressing/README.md)

- [第一次寄存器读与 BAR](03-configuration-enumeration-addressing/config-space-bar-capability.md)

- [桥的总线号与地址窗口](03-configuration-enumeration-addressing/enumeration-bus-number-resource-allocation.md)

- [配置、BAR 与 DMA 地址](03-configuration-enumeration-addressing/mmio-config-dma-address-view.md)

- [IOMMU 翻译与隔离](03-configuration-enumeration-addressing/iommu-address-translation-device-isolation.md)

## 04 数据路径、DMA 与中断

[章节导读](04-data-path-dma-interrupts/README.md)

- [缓冲区与可见性](04-data-path-dma-interrupts/host-memory-pinned-buffer-visibility.md)

- [设备 DMA 读写](04-data-path-dma-interrupts/device-dma-read-write-flow.md)

- [队列、CQE 与 MSI-X](04-data-path-dma-interrupts/queues-doorbells-completions-msix.md)

- [读延迟与并发](04-data-path-dma-interrupts/pcie-read-completion-latency.md)

## 05 性能与调试

[章节导读](05-performance-debug/README.md)

- [带宽与协议参数](05-performance-debug/bandwidth-latency-credit-mps-mrrs.md)

- [数据路径瓶颈](05-performance-debug/host-device-bottleneck-breakdown.md)

- [AER 与链路观测](05-performance-debug/aer-counters-link-debug.md)

- [UR、CA 与 Timeout](05-performance-debug/common-failures-ur-ca-timeout.md)

## 06 工作负载与案例

[章节导读](06-workloads-case-studies/README.md)

- [一次跨桥读取](06-workloads-case-studies/pcie-vs-axi-noc-boundary.md)

- [NIC 的 RX 与 TX](06-workloads-case-studies/nic-dma-case-card.md)

- [NVMe 队列与数据路径](06-workloads-case-studies/nvme-queue-data-path-case-card.md)

- [GPU 主机链路瓶颈](06-workloads-case-studies/gpu-accelerator-host-link.md)

- [FPGA 控制与 DMA](06-workloads-case-studies/fpga-control-data-plane-case-card.md)

- [设备不可用的三个阶段](06-workloads-case-studies/enumeration-failure-case-card.md)

- [链路降速与降宽](06-workloads-case-studies/link-downgrade-case-card.md)

## 07 高级主题

[章节导读](07-advanced-topics/README.md)

- [SR-IOV 与地址空间扩展](07-advanced-topics/sriov-ats-pasid-pri-overview.md)

- [P2P 路由与隔离](07-advanced-topics/p2p-switch-topology-constraints.md)

- [PCIe 与 CXL 的边界](07-advanced-topics/cxl-and-pcie-boundary.md)

<div id="08-术语与检查清单" class="pcie-legacy-anchor"></div>

## 08 查阅、建模与检查清单

[章节导读](08-reference/README.md)

- [一页总览](08-reference/pcie-one-page.md)

- [术语表](08-reference/glossary.md)

- [高频问题](08-reference/high-frequency-questions.md)

- [建模参数与公式](08-reference/pcie-modeling-params.md)

- [设计检查清单](08-reference/pcie-design-checklist.md)

- [调试检查清单](08-reference/pcie-debug-checklist.md)

- [故障复盘模板](08-reference/pcie-debug-postmortem-template.md)
