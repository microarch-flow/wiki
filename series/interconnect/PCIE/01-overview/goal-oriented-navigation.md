# 按目标学习 PCIE

上级：[01 概览与问题定义](./README.md)

相关：[学习路线图](./learning-roadmap.md)、[知识地图](../SUMMARY.md)

## 这页在回答什么问题

如果你的目标不同，PCIE 的阅读顺序也应该不同。这页给出按目标切分的最短学习路径。

## 目标 1：先建立系统判断力

1. [PCIE 在解决什么问题](./problem-statement.md)
2. [PCIE 分类框架](./taxonomy.md)
3. [Root Complex、Switch、Endpoint 在系统里各做什么](../02-link-transaction-basics/topology-root-complex-switch-endpoint.md)
4. [分层架构：Transaction / Data Link / Physical](../02-link-transaction-basics/layered-architecture-transaction-data-link-physical.md)
5. [PCIE vs AXI / NoC：边界与分工](../06-workloads-case-studies/pcie-vs-axi-noc-boundary.md)

## 目标 2：做设备、驱动或 host-device 软件路径

1. [配置空间、BAR 与 Capability](../03-configuration-enumeration-addressing/config-space-bar-capability.md)
2. [MMIO、配置访问、DMA 地址空间视角](../03-configuration-enumeration-addressing/mmio-config-dma-address-view.md)
3. [IOMMU、地址翻译与设备隔离](../03-configuration-enumeration-addressing/iommu-address-translation-device-isolation.md)
4. [设备 DMA 的读写路径](../04-data-path-dma-interrupts/device-dma-read-write-flow.md)
5. [队列、Doorbell、Completion 与 MSI-X](../04-data-path-dma-interrupts/queues-doorbells-completions-msix.md)
6. [NIC DMA 案例卡](../06-workloads-case-studies/nic-dma-case-card.md)
7. [NVMe 队列与数据路径案例卡](../06-workloads-case-studies/nvme-queue-data-path-case-card.md)

## 目标 3：做 bring-up、验证或调试定位

1. [TLP、DLLP 与 Completion 语义](../02-link-transaction-basics/tlp-dllp-completion-basics.md)
2. [Posted / Non-Posted / Completion 与 Ordering](../02-link-transaction-basics/posted-nonposted-completion-ordering.md)
3. [枚举、总线号与资源分配](../03-configuration-enumeration-addressing/enumeration-bus-number-resource-allocation.md)
4. [AER、计数器与链路调试路径](../05-performance-debug/aer-counters-link-debug.md)
5. [Unsupported Request、Completer Abort、Timeout 怎么看](../05-performance-debug/common-failures-ur-ca-timeout.md)
6. [PCIE 调试检查清单](../08-reference/pcie-debug-checklist.md)

## 目标 4：做性能分析和方案判断

1. [PCIe Read Completion 延迟为什么敏感](../04-data-path-dma-interrupts/pcie-read-completion-latency.md)
2. [带宽、延迟、Credit、MPS 与 MRRS](../05-performance-debug/bandwidth-latency-credit-mps-mrrs.md)
3. [Host 到 Device 路径的瓶颈拆解](../05-performance-debug/host-device-bottleneck-breakdown.md)
4. [GPU / 加速器 Host Link 视角](../06-workloads-case-studies/gpu-accelerator-host-link.md)
5. [CXL 和 PCIE 的边界](../07-advanced-topics/cxl-and-pcie-boundary.md)

## 目标 5：做虚拟化、多租户或平台架构

1. [IOMMU、地址翻译与设备隔离](../03-configuration-enumeration-addressing/iommu-address-translation-device-isolation.md)
2. [SR-IOV、ATS、PASID、PRI](../07-advanced-topics/sriov-ats-pasid-pri-overview.md)
3. [Peer-to-Peer、Switch 与拓扑约束](../07-advanced-topics/p2p-switch-topology-constraints.md)
4. [PCIE 高频问题](../08-reference/high-frequency-questions.md)

## 一句话理解

学 PCIE 最怕一开始掉进规范细节。先按你的工程目标选路径，更容易把知识转成可用判断。
