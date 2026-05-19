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

BAR 的关键价值不是“寄存器放哪”，而是把 `device resource` 映射进主机地址视角。

## Capability 为什么重要

Capability 让设备能声明更多能力，而不把基本头部无限膨胀。工程上最常见的是：

- MSI / MSI-X
- PCIe capability 本身
- power management
- SR-IOV 等高级功能

## 一句话理解

配置空间负责“认设备”，BAR 负责“给设备分主机可见资源窗口”，Capability 负责“声明额外能力”。
