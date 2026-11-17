---
title: "设备不可用：区分发现、资源分配与 DMA 启动失败"
---

<div id="枚举失败案例卡" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# 设备不可用：区分发现、资源分配与 DMA 启动失败

上级：[工作负载与案例](README.md)

“枚举失败”常被用来描述所有设备不可用现象，但它会掩盖关键差别。先确认配置空间是否发现 Function，再分别检查 MMIO 和设备发起的 DMA。

<div id="典型现象" class="pcie-legacy-anchor"></div>
<div id="最短排查链" class="pcie-legacy-anchor"></div>

## 三类现象与三条路径

| 现象 | 已有证据 | 优先检查 |
| --- | --- | --- |
| 没有目标 BDF | 配置发现未成功 | 链路、复位、设备就绪、总线号和配置路由 |
| BDF 可见，BAR 资源未分配或 MMIO 不通 | 配置路径至少部分有效 | 地址资源、桥窗口、Memory Space Enable |
| MMIO 正常，DMA 不动 | 控制访问可用 | Bus Master、映射、设备状态、描述符与发布顺序 |

Bus Master 未打开通常不会单独让配置读消失；BAR 资源不足也不等于 Function 没有被发现。

<div id="最常见根因" class="pcie-legacy-anchor"></div>

## 构造案例：可见但没有可用 BAR

假设系统能读到设备 Vendor/Device ID，日志提示某个 Memory BAR 无法分配；驱动申请该资源失败。此时先记录 BAR 需求、平台可用地址窗口和所有上游桥窗口，检查资源覆盖及类型限制。

不能先把问题归因于 SerDes，因为配置事务已提供链路可工作的证据；也不能据此排除间歇性链路故障。需要在同一复现窗口检查实际链路与错误状态。

## 对照案例：MMIO 正常但 DMA 被拒绝

若寄存器可访问，设备发出 DMA 后出现 IOMMU fault，则应检查请求身份、映射地址与权限。它与前例的资源分配问题不同。若设备根本没有发请求，则先检查 Bus Master 和设备引擎启动条件。

<div id="为什么这个案例很重要" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 保存能决定下一步的证据

保留拓扑、配置读结果、资源分配日志、BAR/桥窗口及 Command 状态，再记录 DMA 与 IOMMU 证据。修复后验证的路径必须对应原失败阶段，并继续验证后续阶段，不能以“现在有 BDF”作为整卡验收。

机制详见[枚举与资源分配](../03-configuration-enumeration-addressing/enumeration-bus-number-resource-allocation.md)；驱动资源与使能职责参见 [Linux PCI 指南](https://docs.kernel.org/PCI/pci.html)。
