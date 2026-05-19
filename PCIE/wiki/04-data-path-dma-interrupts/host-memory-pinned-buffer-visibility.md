# 主机内存、Pinned Buffer 与设备可见性

上级：[04 数据路径、DMA 与中断](./README.md)

相关：[IOMMU、地址翻译与设备隔离](../03-configuration-enumeration-addressing/iommu-address-translation-device-isolation.md)

## 这页在回答什么问题

为什么软件侧“已经把 buffer 准备好了”，并不自动意味着设备就能正确、安全地 DMA 到它。

## 三个必须同时成立的条件

- buffer 对驱动和运行时是稳定可追踪的
- 设备拿到的是正确的 DMA 映射地址
- 数据对 CPU 和 device 的可见性顺序满足约束

## pinned buffer 常见价值

- 避免 buffer 生命周期和 DMA 生命周期错位
- 方便建立稳定的 DMA mapping
- 减少频繁换页或不可预期的地址变化

## 这里最容易出什么问题

- buffer 已释放，但设备还在 DMA
- CPU 认为数据已更新，但缓存或同步还没闭环
- IOMMU mapping 建得不完整

## 一句话理解

PCIE 数据路径真正依赖的不是“有个指针”，而是 host memory 生命周期、DMA 映射和可见性语义都已经闭环。
