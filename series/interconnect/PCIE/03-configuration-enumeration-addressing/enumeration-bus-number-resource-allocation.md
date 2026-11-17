---
title: "枚举、总线号与资源分配：从发现到可运行"
---

<div id="枚举总线号与资源分配" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# 枚举、总线号与资源分配：从发现到可运行

上级：[配置、枚举与地址映射](README.md)

枚举发现已有 Function，并建立访问下游所需的总线号与资源配置。固件、操作系统和驱动会分担这些工作；真实平台可能保留固件分配，也可能重分配，不能把下面的逻辑步骤当成唯一实现顺序。

<div id="枚举在做什么" class="pcie-legacy-anchor"></div>

## 枚举需要哪些输入和输出

输入包括可用 Root Port、可访问的配置机制、平台地址窗口及下游组件。输出是已发现的 Function、桥层次、资源分配及能力信息。Device/Function 并非软件随意创造；桥的 bus number 范围则需要软件组织。

1. 访问当前可达 Function 的配置空间，识别普通 Function 与桥。
2. 为桥建立可用的次级总线及下级范围，使配置请求能继续到达下游。
3. 读取资源需求，为 BAR 和桥窗口分配合法地址范围。
4. 驱动绑定设备，申请资源，设置 DMA 能力和映射，按需打开 Memory Space、Bus Master 和中断模式。

最后一步属于运行准备。MSI-X 不是发现设备或执行 DMA 的必选项。

## 两级桥怎样选择配置路径

教学拓扑：上游桥 B0 的 secondary=1、subordinate=3；其下总线 1 上有桥 B1，secondary=2、subordinate=3。位于 bus 3 的 Function 处于两个范围内，配置请求才有对应的下游转发路径。若 B0 的 subordinate 错设为 2，下游 bus 3 就不在该桥覆盖范围内。

这里讨论的是配置路由。Memory BAR 访问还需要另一组地址窗口；总线号范围正确不代表 Memory 窗口也正确。

<div id="它为什么本质上是系统资源组织" class="pcie-legacy-anchor"></div>

## 地址资源怎样沿桥覆盖

假设某 Endpoint 的 Memory BAR 被分配到一个 64 KiB 窗口。沿途每一级适用的桥 Memory 窗口都必须覆盖它，并满足对应桥窗口的粒度、类型及平台资源限制。配置读本身不要求目标 BAR 已经分配好，因此“读得到 Vendor ID”和“读得到 BAR 寄存器”是不同验证。

<div id="为什么这里经常出问题" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 把失败定位到具体阶段

| 证据 | 优先检查 | 不能直接推断 |
| --- | --- | --- |
| 配置结果没有目标 Function | 链路、复位、设备就绪、总线号和配置路由 | 一定是 BAR 不够 |
| Function 可见但资源未分配 | 平台地址窗口、BAR 需求、桥窗口 | Function 没有被枚举 |
| MMIO 正常但 DMA 不发出 | Bus Master、设备启动条件、描述符与映射 | 配置路径故障 |
| DMA 已发出但访问失败 | 地址、权限、目标状态及事务错误 | MSI-X 未开就是根因 |

下一步用[地址视角](mmio-config-dma-address-view.md)区分 CPU 与设备拿到的地址。复盘示例见[设备不可用案例](../06-workloads-case-studies/enumeration-failure-case-card.md)。实际驱动初始化职责参考 [Linux PCI 驱动指南](https://docs.kernel.org/PCI/pci.html)。
