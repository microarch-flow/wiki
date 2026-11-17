---
title: "配置空间、BAR 与 Capability：设备公开哪些资源？"
---

<div id="配置空间bar-与-capability" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# 配置空间、BAR 与 Capability：设备公开哪些资源？

上级：[配置、枚举与地址映射](README.md)

配置空间是主机发现和管理 PCI Function 的标准入口。BAR 描述可分配的地址资源，Capability 描述扩展能力。三者并不包含设备的全部业务寄存器，也不保证能力已被启用。

<div id="配置空间在做什么" class="pcie-legacy-anchor"></div>

## 配置空间按 Function 组织

软件用 Bus、Device、Function（BDF）及所属 PCI segment/domain 定位 Function。PCIe 配置空间可扩展到每 Function 4 KiB；前 256 B 兼容传统 PCI 配置布局。Vendor ID、Device ID、Command/Status、BAR 和 Capability 入口承担不同职责。

配置访问以配置事务定位 Function。平台可以用 ECAM 等机制让 CPU 经地址窗口发起配置访问，但这不把配置空间变成设备的普通 BAR。

<div id="bar-在做什么" class="pcie-legacy-anchor"></div>

## BAR 声明资源，系统分配地址

普通 Endpoint 的 Type 0 配置头有六个 BAR 槽位；一个 64-bit Memory BAR 占相邻两个槽位，不能据此断言设备一定有六个独立窗口。BAR 可以描述 Memory 或 I/O 资源；本文的数据路径示例采用 Memory BAR。

系统软件在允许的配置阶段探测资源需求、分配满足大小与对齐条件的总线地址，并设置沿途桥窗口。传统大小探测利用 BAR 可写位的掩码，之后恢复或写入分配值；它不是应对运行中设备随意执行的诊断写操作。Resizable BAR 等扩展另有能力和选择流程。

教学例：某 BAR 需要 64 KiB，分到总线地址 `0x80000000`，则窗口为 `0x80000000–0x8000FFFF`。软件访问偏移 `0x100` 的寄存器，还要经过主机桥地址转换和 CPU 映射。地址分配不等于该偏移对应的寄存器存在。

| 检查项 | 作用 | 失败现象 |
| --- | --- | --- |
| BAR 获得合法地址 | 给目标窗口确定位置 | 无可用资源或地址冲突 |
| 桥窗口覆盖该地址 | 允许请求逐级到达下游 | Function 可发现，MMIO 却不可达 |
| Memory Space Enable | 允许 Function 译码其内存资源 | 地址已分配但不能正常访问 |

<div id="capability-为什么重要" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## Capability 是能力清单，不是运行状态

传统 Capability 链与 PCIe Extended Capability 链位于不同配置区域。MSI/MSI-X、PCIe Capability 与 SR-IOV 等应按各自链和版本解释，不能把所有能力都放进同一个固定偏移表。

发现 MSI-X Capability 后，驱动仍须申请中断资源、配置表项及屏蔽状态，再使能所选模式。MSI-X 表和 PBA 所在 BAR 及偏移由 Capability 描述；不能把整个 MSI-X 表当成嵌在 Capability 内。

下一篇[枚举与资源分配](enumeration-bus-number-resource-allocation.md)把这些对象连成初始化过程。寄存器布局可查 [Linux PCI 寄存器定义](https://github.com/torvalds/linux/blob/master/include/uapi/linux/pci_regs.h)，驱动流程见 [Linux PCI 指南](https://docs.kernel.org/PCI/pci.html)；MSI-X 使用见 [MSI 指南](https://docs.kernel.org/PCI/msi-howto.html)。
