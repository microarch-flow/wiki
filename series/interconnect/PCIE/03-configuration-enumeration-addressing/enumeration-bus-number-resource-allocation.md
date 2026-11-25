---
title: "桥怎样用总线号找到设备，又怎样用地址窗口转发访问？"
---

<div id="枚举总线号与资源分配" class="pcie-legacy-anchor"></div>
<div id="枚举总线号与资源分配从发现到可运行" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# 桥怎样用总线号找到设备，又怎样用地址窗口转发访问？

上级：[配置、枚举与地址映射](README.md)

主机能从加速卡读出 Vendor ID，却读不到卡上已经分配地址的寄存器。两次都是主机发起的读，也都必须穿过同一棵 PCIe 树。为什么一次能通过，另一次却可能在桥上就走错了路？

[主课](config-space-bar-capability.md)跟着同一个 64 KiB BAR 走完发现、分配和第一次寄存器读取。这里把镜头停在沿途的桥上。只改一个范围，就能分别让配置请求或内存读请求失去通路。

## 一个配置请求怎样找到第三条总线？

<div id="枚举在做什么" class="pcie-legacy-anchor"></div>
<div id="枚举需要哪些输入和输出" class="pcie-legacy-anchor"></div>
<div id="两级桥怎样选择配置路径" class="pcie-legacy-anchor"></div>

设同一个 PCI segment 中，Root Port 接到一颗交换机，加速卡接在它的一个下行端口。软件把交换机的上、下行端口各看成一座桥，端口之间还有一条内部逻辑总线。下表按根端口 B0、交换机上行端口 B1、下行端口 B2 的次序排列。总线号用十六进制，区间包含两端。

<div class="bus-read-trace" markdown="1">

| 桥与自身 BDF | 直接下游总线 | 下游编号上限 |
| --- | :---: | :---: |
| B0　`00:01.0` | 01 | 03 |
| B1　`01:00.0` | 02 | 03 |
| B2　`02:01.0` | 03 | 03 |

</div>

看 B1：它位于总线 01（`Primary`），下游直接接着总线 02（`Secondary`），它的子树一直覆盖到总线 03（`Subordinate`）。读 `03:00.0` 的 Vendor ID 时，目标总线号是 03。它落在 B0 的 01～03 内，也落在 B1 的 02～03 内。到 B2 时，03 正好是这座桥的直接下游总线，配置请求可以送往那条链路上的目标设备和 Function。把 B0 的上限单独从 03 改成 02，最外层的覆盖就断了。哪怕末端链路仍然工作，后两座桥也没有机会把这个请求送到卡上。[Broadcom PEX 8664 器件手册，配置与地址路由](https://docs.broadcom.com/doc/PEX_8664-AA_Data_Book_v1.5_25Jan13.pdf)

枚举时，软件最初只知道平台提供了哪些根总线、配置访问机制和地址资源。在当前可达的总线上找到一座桥，才能继续扫描它下面的设备。需要新分配总线号时，可以先给这座桥设置次级总线号，在可用范围内暂时留出扫描空间，递归发现下游后再确定覆盖上限。这也解释了为什么根端口的覆盖范围要包含孙辈总线。固件可能已完成分配，操作系统可以沿用；需要重分配时还受平台资源限制。软件组织总线编号，桥下有哪些 Function、各自报告哪些能力，则取决于实际设备。[Linux PCI 枚举与桥资源读取实现](https://github.com/torvalds/linux/blob/master/drivers/pci/probe.c)

## 卡找到了，哪座桥还可能挡住寄存器读？

<div id="它为什么本质上是系统资源组织" class="pcie-legacy-anchor"></div>
<div id="地址资源怎样沿桥覆盖" class="pcie-legacy-anchor"></div>

保持上表中的总线号。设这张卡的非预取 Memory BAR 已分配到 PCIe 总线地址 `0x8000_0000`，长度 64 KiB，最后一个字节是 `0x8000_FFFF`。这样，读 BAR 内偏移 `0x100` 的寄存器，会在 PCIe 侧产生目标地址为 `0x8000_0100` 的 Memory Read。桥此时按**地址**选择下游。假设主机桥映射正确，沿途内存转发和端点内存译码均已使能。

在这个简化配置中，让三座桥的非预取内存窗口都覆盖 `0x8000_0000`～`0x800F_FFFF`，即 1 MiB。这个总线地址范围逐级通到卡所在的分支，端点再用自己的 64 KiB BAR 选出更小的区间。上级桥的窗口可以同时容纳多个下游资源；桥放行的整个 1 MiB 不会因此都变成这张卡的寄存器。实际分配还要检查窗口类型、对齐、兄弟分支的占用和主机侧可用地址范围。

反过来算一次容量。假如这个分支的设备还需要第二个同类的 64 KiB BAR，而 `0x8001_0000`～`0x8001_FFFF` 尚未占用，就能把它放在这个已对齐的区间。三个桥窗口都不用扩大，总线号也不用增加。如果这段地址已经给了别的 BAR，窗口再大也不能重复分配同一资源。CPU 映射地址与 PCIe 总线地址如何对应，见[配置、MMIO 与 DMA 的地址视角](mmio-config-dma-address-view.md)。

热插拔也会分别消耗这两种资源。新加入一颗交换机时，可能需要为它的下游总线留出编号；换入一个 BAR 更大的端点时，即使总线号够用，还得找到能沿树逐级覆盖的地址空间。Linux 将热插拔桥的额外总线号、非预取 MMIO 空间和可预取 MMIO 空间列作不同的预留项。[Linux 内核 PCI 热插拔资源参数](https://docs.kernel.org/admin-guide/kernel-parameters.html)

## 怎样区分枚举、MMIO 和 DMA 的故障？

<div id="为什么这里经常出问题" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>
<div id="把失败定位到具体阶段" class="pcie-legacy-anchor"></div>

<div class="bus-read-trace" markdown="1">

| 已观察到的现象 | 下一处要查的边界 |
| --- | --- |
| 目标 Function 的配置读不通 | 设备就绪、复位、链路，以及每座桥的总线号范围。此时还没验证 BAR。 |
| Function 可见，BAR 没有获得资源 | BAR 大小、类型、对齐、主机地址资源，以及下游窗口能否容纳分配结果。 |
| 配置读正常，BAR 有地址，MMIO 失败 | 主机映射、逐级内存窗口、Memory Space Enable，以及偏移和寄存器访问条件。 |
| 寄存器可读，设备没有发起 DMA | Bus Master Enable、设备引擎启动条件、描述符和 DMA 映射。 |
| DMA 已发出但报错 | 设备使用的 DMA 地址、权限、目标状态及事务错误，再核对完成通知机制。 |

</div>

枚举可以发现 Function、桥层次和 Capability，也能为设备准备资源。驱动绑定后，还须按用途申请资源、建立映射和启动设备；MSI-X 是否启用由通知方案决定。建模时可分别记录配置请求通过了哪些总线范围、内存请求命中了哪些桥窗口、设备是否真的发出了 DMA。这样报告“失败”时，就能指出哪一层的哪一个条件没有满足。[设备不可用案例](../06-workloads-case-studies/enumeration-failure-case-card.md) · [Linux PCI 驱动指南](https://docs.kernel.org/PCI/pci.html)
