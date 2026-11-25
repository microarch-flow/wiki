---
title: "学习路线图：从设备发现到性能解释"
---

<div id="学习路线图" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# 学习路线图：从设备发现到性能解释

上级：[概览与问题定义](README.md)

这条路线用于顺序学习。每阶段先完成一个可检查的问题，再进入下一阶段。已有故障或设计目标时，可改用[目标导航](goal-oriented-navigation.md)。

<div id="阶段-1先建立系统图景" class="pcie-legacy-anchor"></div>

## 阶段 1：画出请求经过的路径

依次读[系统问题](problem-statement.md)、[问题地图](taxonomy.md)、[拓扑与角色](../02-link-transaction-basics/topology-root-complex-switch-endpoint.md)和[协议分层](../02-link-transaction-basics/layered-architecture-transaction-data-link-physical.md)。

检查：在“两个 Endpoint 共用一个 Switch 上行口”的图中，指出同向竞争发生在哪里。不要把 Root Complex 和单个 Root Port 当成同一对象。

<div id="阶段-2建立事务和配置主线" class="pcie-legacy-anchor"></div>

## 阶段 2：追踪一笔读取和一个发送条件

读[一次 PCIe 读取](../02-link-transaction-basics/tlp-dllp-completion-basics.md)、[信用流控与链路重放](../02-link-transaction-basics/credit-flow-control-and-replay.md)、[请求类型与排序](../02-link-transaction-basics/posted-nonposted-completion-ordering.md)。

检查：链路 ACK 已到，但最终 CplD 未到，哪些资源可以释放，哪些仍要保留？

## 阶段 3：让设备获得可用的地址与缓冲区

从[主机第一次读卡上寄存器](../03-configuration-enumeration-addressing/config-space-bar-capability.md)入手，沿[配置与枚举章](../03-configuration-enumeration-addressing/README.md)核对桥窗口和地址映射。接着读[缓冲区、映射与可见性](../04-data-path-dma-interrupts/host-memory-pinned-buffer-visibility.md)，把方向换成设备访问主机。

检查：给同一块主机缓冲区分别标出 CPU 指针、物理地址和 DMA 地址。说明为什么不能把 CPU 指针直接写入普通 DMA 描述符。

<div id="阶段-3建立-host-device-数据路径理解" class="pcie-legacy-anchor"></div>

## 阶段 4：走通提交、搬运和完成

读[设备 DMA](../04-data-path-dma-interrupts/device-dma-read-write-flow.md)、[队列与通知](../04-data-path-dma-interrupts/queues-doorbells-completions-msix.md)、[读延迟与并发](../04-data-path-dma-interrupts/pcie-read-completion-latency.md)。

检查：NVMe Read 的数据为什么通常由设备发 PCIe Memory Write 返回？它与 PCIe Read 的 Completion 有何区别？可用 [NVMe 案例](../06-workloads-case-studies/nvme-queue-data-path-case-card.md)核对。

<div id="阶段-4转成性能和调试判断" class="pcie-legacy-anchor"></div>
<div id="阶段-5用案例稳固理解" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 阶段 5：用证据解释快慢与失败

读[性能参数](../05-performance-debug/bandwidth-latency-credit-mps-mrrs.md)、[瓶颈拆解](../05-performance-debug/host-device-bottleneck-breakdown.md)、[AER](../05-performance-debug/aer-counters-link-debug.md)和[事务错误](../05-performance-debug/common-failures-ur-ca-timeout.md)。再选一个[系统案例](../06-workloads-case-studies/README.md)复述其路径。

检查：链路空闲、Tag 满和软件队列空分别能支持哪些解释？给每个判断补一个反例。最后使用[设计检查清单](../08-reference/pcie-design-checklist.md)检查自己的系统假设。
