---
title: "PCIe 与 CXL 的边界：I/O 事务之外增加了什么？"
---

<div id="cxl-和-pcie-的边界" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# PCIe 与 CXL 的边界：I/O 事务之外增加了什么？

上级：[高级主题](README.md)

CXL 复用 PCIe 的物理基础和部分 I/O 基础设施，并提供缓存与内存访问协议。普通 PCIe 链路不会仅因连接器或速率相同，就自动具备 CXL 一致性能力。

<div id="一个最实用的判断" class="pcie-legacy-anchor"></div>

## 三种协议的主要职责

| 协议 | 典型职责 | 与本文的关系 |
| --- | --- | --- |
| CXL.io | 发现、配置及 I/O 访问 | 延续 PCIe 相关管理与事务基础 |
| CXL.cache | 设备一致地访问和缓存主机内存 | 需要额外的一致性协议与状态 |
| CXL.mem | 主机访问设备连接的内存 | 具有对应的内存访问语义 |

这是典型主机与设备关系的入口说明，不是所有 CXL 版本和复杂拓扑的完整方向表。[Linux CXL 设备与协议说明](https://docs.kernel.org/driver-api/cxl/devices/device-types.html)可用于核对这些基本职责。

<div id="两者边界怎么抓" class="pcie-legacy-anchor"></div>

## 一个 Type 3 内存扩展例子

设备使用 CXL.io 与 CXL.mem。主机先发现并配置资源，再按系统映射访问设备内存。它不因此需要用 CXL.cache 缓存主机内存，也不等于驱动让设备用普通 DMA 将所有数据复制进主机 DRAM。

要成立，主机和设备须支持相应协议与类型，路径须协商和配置到适用模式，软件须管理可访问内存。仅有普通 PCIe BAR 和总线枚举不足以提供这条内存路径。

<div id="为什么先学-pcie" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 本专题讲到哪里

这里保留发现、配置、物理链路和协议选择的边界。CXL 的内存映射、一致性、扩展、池化与共享继续读[一致性专题：从设备发现到内存访问](../../COHERENCE/cxl-host-memory.md)。讨论性能时应指定规范版本和目标系统，不把某代 PCIe 的 Non-Flit 包开销直接用于所有 CXL 协议。
