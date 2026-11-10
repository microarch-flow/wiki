# 主机内存、Pinned Buffer 与设备可见性

上级：[04 数据路径、DMA 与中断](./README.md)

相关：[IOMMU、地址翻译与设备隔离](../03-configuration-enumeration-addressing/iommu-address-translation-device-isolation.md)

## 这页在回答什么问题

为什么软件侧“已经把 buffer 准备好了”，并不自动意味着设备就能正确、安全地 DMA 到它。

## 三个必须同时成立的条件

- buffer 对驱动和运行时是稳定可追踪的
- 设备拿到的是正确的 DMA 映射地址
- 数据对 CPU 和 device 的可见性顺序满足约束

以传统显式 DMA 映射、非一致 streaming buffer 为例：CPU 拥有缓冲区时先写数据；通过 DMA API 建立或按映射状态同步给设备，并按设备接口要求发布描述符；设备取得所有权后执行 DMA，CPU 不应同时访问该缓冲区。设备报告结束后，CPU 按方向和 DMA API 同步回 CPU 所有权，再读取或复用；确认 DMA 已停止后才能撤销映射并释放页面。coherent 映射不需要同样的缓存维护，但仍需要正确的发布顺序。

Pin 维持页面在 DMA 生命周期内可用，并不建立 DMA 地址或同步缓存。支持 SVA、ATS 和 PRI 的平台可以采用可分页的共享虚拟地址路径，其缺页和失效处理是另一套契约，不应默认适用于普通显式映射。参见 [Linux DMA 映射指南](https://docs.kernel.org/core-api/dma-api-howto.html) 和 [SVA 文档](https://docs.kernel.org/arch/x86/sva.html)。

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
