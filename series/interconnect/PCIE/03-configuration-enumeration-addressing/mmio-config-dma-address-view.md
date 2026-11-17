---
title: "配置、BAR 与 DMA：一次访问使用哪个地址？"
---

<div id="mmio配置访问dma-地址空间视角" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# 配置、BAR 与 DMA：一次访问使用哪个地址？

上级：[配置、枚举与地址映射](README.md)

地址必须和发起者、地址空间及目标资源一起解释。BAR 描述设备的目标窗口；DMA 地址是平台提供给设备发起访问时使用的地址。普通 DMA 常以主机内存为目标，受支持的 P2P DMA 也可以访问对端设备资源。

<div id="三种常见地址视角" class="pcie-legacy-anchor"></div>

## 三种访问，三个问题

| 访问 | 如何定位 | 目标与用途 |
| --- | --- | --- |
| 配置访问 | segment/domain、BDF、配置偏移 | 发现 Function，配置资源与能力 |
| CPU 访问 Memory BAR | CPU 虚拟映射、CPU 物理资源、主机桥转换后的总线地址 | 设备寄存器或本地内存窗口 |
| 设备 DMA | 描述符中的 DMA 地址，及适用的请求身份/翻译上下文 | 已映射的主机缓冲区或受支持的对端资源 |

CPU 通过 ECAM 地址窗口访问配置空间，属于平台实现配置机制的方式。它不意味着配置请求与普通 BAR Memory Read 是同一种事务。

## CPU 怎样访问 BAR

下面是构造地址，不代表任何机器的实际映射：设备 BAR 的总线基址为 `0x80000000`，主机桥把它映射到 CPU 物理资源 `0x480000000`，驱动再通过 `ioremap()` 一类 API 得到 CPU 可用的 I/O 映射。

> CPU 的 I/O 虚拟映射 + 偏移 → CPU 物理资源 + 偏移 → 主机桥转换 → BAR 总线地址 + 偏移 → 设备寄存器

若访问偏移 `0x100`，链路上的目标可为 `0x80000100`。驱动应使用平台资源和 I/O 访问 API，不应把 BAR 寄存器里的总线地址直接转换成普通 CPU 指针。

<div id="一个典型交互" class="pcie-legacy-anchor"></div>

## 设备怎样访问主机缓冲区

假设软件持有 CPU 指针 X，背后物理页地址为 `0x12000000`。DMA API 返回设备可用地址 `0x40000000`，IOMMU 将该地址映射回同一物理页。

| 发起者 | 转换路径 |
| --- | --- |
| CPU | 指针 X → CPU 页表 → 主机物理页 |
| 设备 | 描述符中的 DMA 地址 → IOMMU 域与映射 → 同一主机物理页 |

驱动向设备发布的是 DMA API 返回的地址，不是 X，也不是凭空假定的物理地址。没有 IOMMU 时仍应使用 DMA API：主机桥偏移、地址宽度限制或 bounce buffer 也可能影响设备可用地址。

上述不同地址空间及 API 职责依据 [Linux DMA 地址指南](https://docs.kernel.org/core-api/dma-api-howto.html)。数值相同只是一种平台可能性，不是通用接口保证。

<div id="最容易混淆的地方" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## P2P 与共享虚拟地址的边界

P2P 中，目标可以是对端 BAR 的可访问资源；请求者仍须取得适用映射并满足路由条件。SVA 中，支持的平台可让设备使用进程虚拟地址及 PASID 上下文；这是专门配置的能力，不能据此允许普通 DMA 使用任意用户指针。

因此不能用“BAR 只供 CPU 访问”或“DMA 地址总是主机物理地址”作为定义。继续读 [IOMMU](iommu-address-translation-device-isolation.md)、[P2P](../07-advanced-topics/p2p-switch-topology-constraints.md)和[地址空间扩展](../07-advanced-topics/sriov-ats-pasid-pri-overview.md)。
