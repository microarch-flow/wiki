# PCIE Wiki

> `PCIE 不是“主机插外设的高速接口”这么简单，而是在 host、device、memory、interrupt、IOMMU、software stack 和性能约束之间建立系统契约的一层互连体系。要真正理解 PCIE，必须同时看拓扑、事务层、配置空间、地址映射、DMA、completion、MSI-X、虚拟化以及调试路径。`

## Dashboard

| 你现在要做什么 | 直接入口 |
| --- | --- |
| 5 分钟快速建立判断力 | [PCIE 在解决什么问题](./01-overview/problem-statement.md) |
| 第一次系统学习 PCIE | [学习路线图](./01-overview/learning-roadmap.md) |
| 按目标选最短阅读路径 | [按目标学习 PCIE](./01-overview/goal-oriented-navigation.md) |
| 先建立全局分类框架 | [PCIE 分类框架](./01-overview/taxonomy.md) |
| 先把拓扑和角色分清 | [Root Complex、Switch、Endpoint 在系统里各做什么](./02-link-transaction-basics/topology-root-complex-switch-endpoint.md) |
| 先理解分层为什么重要 | [分层架构：Transaction / Data Link / Physical](./02-link-transaction-basics/layered-architecture-transaction-data-link-physical.md) |
| 先搞懂 packet 和 completion | [TLP、DLLP 与 Completion 语义](./02-link-transaction-basics/tlp-dllp-completion-basics.md) |
| 先把 ordering 和请求类型看懂 | [Posted / Non-Posted / Completion 与 Ordering](./02-link-transaction-basics/posted-nonposted-completion-ordering.md) |
| 理解设备是怎么被发现和配置出来的 | [配置空间、BAR 与 Capability](./03-configuration-enumeration-addressing/config-space-bar-capability.md) |
| 串起枚举和资源分配主线 | [枚举、总线号与资源分配](./03-configuration-enumeration-addressing/enumeration-bus-number-resource-allocation.md) |
| 快速分清 MMIO / PIO / DMA 地址视角 | [MMIO、配置访问、DMA 地址空间视角](./03-configuration-enumeration-addressing/mmio-config-dma-address-view.md) |
| 理解 PCIE 与 IOMMU 的交界 | [IOMMU、地址翻译与设备隔离](./03-configuration-enumeration-addressing/iommu-address-translation-device-isolation.md) |
| 看设备 DMA 是怎么跑起来的 | [设备 DMA 的读写路径](./04-data-path-dma-interrupts/device-dma-read-write-flow.md) |
| 串起 queue、doorbell、completion 和 MSI-X | [队列、Doorbell、Completion 与 MSI-X](./04-data-path-dma-interrupts/queues-doorbells-completions-msix.md) |
| 看为什么 PCIe read 往往更难做快 | [PCIe Read Completion 延迟为什么敏感](./04-data-path-dma-interrupts/pcie-read-completion-latency.md) |
| 开始做带宽和瓶颈分析 | [带宽、延迟、Credit、MPS 与 MRRS](./05-performance-debug/bandwidth-latency-credit-mps-mrrs.md) |
| 开始做调试定位 | [AER、计数器与链路调试路径](./05-performance-debug/aer-counters-link-debug.md) |
| 直接看系统案例 | [NIC DMA 案例卡](./06-workloads-case-studies/nic-dma-case-card.md) / [NVMe 队列与数据路径案例卡](./06-workloads-case-studies/nvme-queue-data-path-case-card.md) |
| 看工程故障怎么拆 | [枚举失败案例卡](./06-workloads-case-studies/enumeration-failure-case-card.md) / [链路降速案例卡](./06-workloads-case-studies/link-downgrade-case-card.md) |
| 看 PCIE 和片上互连的边界 | [PCIE vs AXI / NoC：边界与分工](./06-workloads-case-studies/pcie-vs-axi-noc-boundary.md) |
| 看高级主题入口 | [SR-IOV、ATS、PASID、PRI](./07-advanced-topics/sriov-ats-pasid-pri-overview.md) |
| 做方案或集成评审 | [PCIE 设计检查清单](./08-reference/pcie-design-checklist.md) |
| 快速查阅 | [PCIE 一页版总览](./08-reference/pcie-one-page.md) / [术语表](./08-reference/glossary.md) |
| 做量化建模 / 架构探索工具 | [PCIe 建模参数与公式速查](./08-reference/pcie-modeling-params.md) |

## 快速开始

### 路线 1：第一次系统学 PCIE

1. [PCIE 在解决什么问题](./01-overview/problem-statement.md)
2. [PCIE 分类框架](./01-overview/taxonomy.md)
3. [Root Complex、Switch、Endpoint 在系统里各做什么](./02-link-transaction-basics/topology-root-complex-switch-endpoint.md)
4. [分层架构：Transaction / Data Link / Physical](./02-link-transaction-basics/layered-architecture-transaction-data-link-physical.md)
5. [TLP、DLLP 与 Completion 语义](./02-link-transaction-basics/tlp-dllp-completion-basics.md)
6. [配置空间、BAR 与 Capability](./03-configuration-enumeration-addressing/config-space-bar-capability.md)
7. [学习路线图](./01-overview/learning-roadmap.md)

### 路线 2：想把 host-device 数据路径学透

1. [MMIO、配置访问、DMA 地址空间视角](./03-configuration-enumeration-addressing/mmio-config-dma-address-view.md)
2. [IOMMU、地址翻译与设备隔离](./03-configuration-enumeration-addressing/iommu-address-translation-device-isolation.md)
3. [设备 DMA 的读写路径](./04-data-path-dma-interrupts/device-dma-read-write-flow.md)
4. [队列、Doorbell、Completion 与 MSI-X](./04-data-path-dma-interrupts/queues-doorbells-completions-msix.md)
5. [PCIe Read Completion 延迟为什么敏感](./04-data-path-dma-interrupts/pcie-read-completion-latency.md)
6. [NIC DMA 案例卡](./06-workloads-case-studies/nic-dma-case-card.md)
7. [NVMe 队列与数据路径案例卡](./06-workloads-case-studies/nvme-queue-data-path-case-card.md)
8. [FPGA / 采集卡控制面与数据面案例卡](./06-workloads-case-studies/fpga-control-data-plane-case-card.md)

### 路线 3：想做性能分析、bring-up 或故障定位

1. [带宽、延迟、Credit、MPS 与 MRRS](./05-performance-debug/bandwidth-latency-credit-mps-mrrs.md)
2. [Host 到 Device 路径的瓶颈拆解](./05-performance-debug/host-device-bottleneck-breakdown.md)
3. [AER、计数器与链路调试路径](./05-performance-debug/aer-counters-link-debug.md)
4. [Unsupported Request、Completer Abort、Timeout 怎么看](./05-performance-debug/common-failures-ur-ca-timeout.md)
5. [PCIE 调试检查清单](./08-reference/pcie-debug-checklist.md)
6. [PCIE 高频问题](./08-reference/high-frequency-questions.md)

## 工作台

### 学习

- [概览与问题定义](./01-overview/README.md)
- [按目标学习 PCIE](./01-overview/goal-oriented-navigation.md)
- [链路、分层与事务基础](./02-link-transaction-basics/README.md)
- [配置、枚举与地址映射](./03-configuration-enumeration-addressing/README.md)
- [数据路径、DMA 与中断](./04-data-path-dma-interrupts/README.md)
- [系统案例](./06-workloads-case-studies/README.md)

### 分析

- [性能与调试](./05-performance-debug/README.md)
- [高级主题](./07-advanced-topics/README.md)
- [枚举失败案例卡](./06-workloads-case-studies/enumeration-failure-case-card.md)
- [链路降速案例卡](./06-workloads-case-studies/link-downgrade-case-card.md)
- [PCIE vs AXI / NoC：边界与分工](./06-workloads-case-studies/pcie-vs-axi-noc-boundary.md)
- [CXL 和 PCIE 的边界](./07-advanced-topics/cxl-and-pcie-boundary.md)

### 查阅

- [知识地图](./SUMMARY.md)
- [PCIE 一页版总览](./08-reference/pcie-one-page.md)
- [术语表](./08-reference/glossary.md)
- [PCIE 高频问题](./08-reference/high-frequency-questions.md)
- [PCIE 设计检查清单](./08-reference/pcie-design-checklist.md)
- [PCIE 调试检查清单](./08-reference/pcie-debug-checklist.md)
- [PCIe 建模参数与公式速查](./08-reference/pcie-modeling-params.md)

## 这套 Wiki 的边界

这套 wiki 的主线不是：

- 把协议规范逐条抄成手册
- 只讲某一家控制器 IP 的寄存器细节
- 把所有高速 SerDes、以太网、CXL 细节都混进来重写

这套 wiki 的主线是：

- 把 PCIE 作为 `host-device 系统互连层` 来理解
- 同时覆盖 `拓扑 / 事务 / 配置 / DMA / interrupt / virtualization / observability`
- 建立 `能解释系统瓶颈、能支持 bring-up、能指导调试` 的知识结构

## 维护原则

- 每页尽量只回答一个核心问题
- 优先区分 `链路角色 / 事务语义 / 配置寻址 / 数据路径 / 调试`
- 优先保留能转化成工程判断和系统分析的内容
- 与 [BUS Wiki](../../BUS/wiki/README.md)、[DMA Wiki](../../DMA/wiki/README.md)、[NOC Wiki](../../NOC/wiki/README.md)、[RAM Wiki](../../RAM/wiki/README.md) 保持可互相链接的术语体系
