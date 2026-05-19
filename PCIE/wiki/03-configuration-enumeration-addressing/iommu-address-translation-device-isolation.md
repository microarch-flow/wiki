# IOMMU、地址翻译与设备隔离

上级：[03 配置、枚举与地址映射](./README.md)

相关：[MMIO、配置访问、DMA 地址空间视角](./mmio-config-dma-address-view.md)、[BUS Wiki: IOMMU、SMMU 与 DMA 寻址](../../../BUS/wiki/04-microarchitecture-integration/iommu-smmu-dma-addressing.md)

## 这页在回答什么问题

为什么设备能 DMA 到主机内存并不代表它应该被允许任意访问，以及 IOMMU 在这里到底扮演什么角色。

## IOMMU 在解决什么问题

- 把设备侧 DMA 地址翻译成真正的主机物理地址
- 为不同设备或功能建立隔离域
- 支持虚拟化和更细粒度的权限控制

## 为什么这对 PCIE 尤其关键

因为 PCIE endpoint 常常是主机外部设备：

- 设备本身可能不可信
- 多个设备会共享主机内存系统
- 虚拟机或容器环境需要隔离 DMA 能力

## 没有 IOMMU 会怎样

- 驱动和平台软件更难控制 DMA 可达范围
- 错误 DMA 更容易破坏系统内存
- 多租户和直通场景难以建立安全边界

## 工程上最重要的判断

很多 “DMA 不通” 和 “性能变差” 的问题都不能只看设备：

- 映射建立是否正确
- TLB / IOTLB 行为是否成为开销
- 是否启用了中间地址翻译能力

## 一句话理解

IOMMU 让“设备能访问主机内存”这件事从裸奔变成受控、可隔离、可虚拟化的系统契约。
