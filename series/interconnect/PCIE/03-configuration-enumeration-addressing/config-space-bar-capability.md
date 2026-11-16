# 配置空间、BAR 与 Capability

上级：[03 配置、枚举与地址映射](./README.md)

相关：[枚举、总线号与资源分配](./enumeration-bus-number-resource-allocation.md)、[MMIO、配置访问、DMA 地址空间视角](./mmio-config-dma-address-view.md)

## 这页在回答什么问题

为什么设备一接入系统就不是“黑盒”，以及主机是通过什么结构认识和配置它的。

## 配置空间在做什么

配置空间是设备对主机公开的一套标准化管理入口，常见信息包括：

- vendor / device identity
- command / status
- BAR
- capability 列表
- 中断相关能力

它不是设备的全部寄存器地图，而是“让系统先把设备组织起来”的最小公共接口。

## BAR 在做什么

BAR 描述的是设备希望暴露给主机的一段地址资源，常见用于：

- MMIO control register
- device local memory window
- doorbell / queue register

BAR 给出资源类型、所需大小等信息；系统为其分配总线地址，并配置沿途 bridge 的转发窗口。比如配置空间已可读，但内存 BAR 没有得到地址，或桥窗口不覆盖该地址，CPU 的相应 MMIO 就不能按预期到达设备。即使地址已分配，Function 的 Memory Space Enable 关闭时也不会正常译码该内存 BAR。BAR 分配、桥转发和 Function 译码是三个可分别检查的条件。

## Capability 为什么重要

Capability 让设备能声明更多能力，而不把基本头部无限膨胀。工程上最常见的是：

- MSI / MSI-X
- PCIe capability 本身
- power management
- SR-IOV 等高级功能

例如 Capability 声明 MSI-X，只表示设备提供该机制；软件还须配置表项的消息地址/数据及屏蔽状态，并在选择该中断模式后使能。可发现能力不等于已经配置或正在使用。

## 一句话理解

配置空间负责“认设备”，BAR 负责“给设备分主机可见资源窗口”，Capability 负责“声明额外能力”。
