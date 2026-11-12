# 学习路线图

上级：[01 概览与问题定义](./README.md)

相关：[按目标学习 PCIE](./goal-oriented-navigation.md)、[知识地图](../SUMMARY.md)

## 这页在回答什么问题

如果你不是为了背规范，而是为了建立体系结构判断，PCIE 应该按什么顺序学。

## 阶段 1：先建立系统图景

1. [PCIE 在解决什么问题](./problem-statement.md)
2. [PCIE 分类框架](./taxonomy.md)
3. [Root Complex、Switch、Endpoint 在系统里各做什么](../02-link-transaction-basics/topology-root-complex-switch-endpoint.md)
4. [分层架构：Transaction / Data Link / Physical](../02-link-transaction-basics/layered-architecture-transaction-data-link-physical.md)

目标是先知道谁和谁在交互，不急着掉进字段细节。

## 阶段 2：建立事务和配置主线

1. [TLP、DLLP 与 Completion 语义](../02-link-transaction-basics/tlp-dllp-completion-basics.md)
2. [Posted / Non-Posted / Completion 与 Ordering](../02-link-transaction-basics/posted-nonposted-completion-ordering.md)
3. [配置空间、BAR 与 Capability](../03-configuration-enumeration-addressing/config-space-bar-capability.md)
4. [枚举、总线号与资源分配](../03-configuration-enumeration-addressing/enumeration-bus-number-resource-allocation.md)

目标是把“设备为何能被发现、为何能收发事务”这条主线串起来。

## 阶段 3：建立 host-device 数据路径理解

1. [MMIO、配置访问、DMA 地址空间视角](../03-configuration-enumeration-addressing/mmio-config-dma-address-view.md)
2. [IOMMU、地址翻译与设备隔离](../03-configuration-enumeration-addressing/iommu-address-translation-device-isolation.md)
3. [设备 DMA 的读写路径](../04-data-path-dma-interrupts/device-dma-read-write-flow.md)
4. [队列、Doorbell、Completion 与 MSI-X](../04-data-path-dma-interrupts/queues-doorbells-completions-msix.md)
5. [PCIe Read Completion 延迟为什么敏感](../04-data-path-dma-interrupts/pcie-read-completion-latency.md)

## 阶段 4：转成性能和调试判断

1. [带宽、延迟、Credit、MPS 与 MRRS](../05-performance-debug/bandwidth-latency-credit-mps-mrrs.md)
2. [Host 到 Device 路径的瓶颈拆解](../05-performance-debug/host-device-bottleneck-breakdown.md)
3. [AER、计数器与链路调试路径](../05-performance-debug/aer-counters-link-debug.md)
4. [Unsupported Request、Completer Abort、Timeout 怎么看](../05-performance-debug/common-failures-ur-ca-timeout.md)

## 阶段 5：用案例稳固理解

1. [NIC DMA 案例卡](../06-workloads-case-studies/nic-dma-case-card.md)
2. [NVMe 队列与数据路径案例卡](../06-workloads-case-studies/nvme-queue-data-path-case-card.md)
3. [GPU / 加速器 Host Link 视角](../06-workloads-case-studies/gpu-accelerator-host-link.md)
4. [PCIE vs AXI / NoC：边界与分工](../06-workloads-case-studies/pcie-vs-axi-noc-boundary.md)

## 一句话理解

先看系统角色，再看事务和配置，再看 DMA 和中断，最后把它变成性能与调试判断，这条路径最稳。
