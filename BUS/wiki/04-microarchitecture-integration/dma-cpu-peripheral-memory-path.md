# CPU、DMA、外设与内存之间的总线路径

上级：[04 微架构与系统集成](./README.md)

相关：[DMA Wiki 首页](../../../DMA/wiki/README.md)、[RAM Wiki 首页](../../../RAM/wiki/README.md)

## 这页在回答什么问题

为什么 BUS 不应该孤立地看，而要放回 CPU、DMA、memory 和 peripheral 的完整路径里理解。

## 一条典型控制路径

CPU 配置 DMA 时，常见路径是：

`CPU -> main interconnect -> bridge -> low-speed peripheral bus -> DMA register block`

这条路看起来流量不大，但会影响：

- driver 配置时延
- doorbell 触发及时性
- status polling 行为

这里的 `main interconnect` 和 `low-speed peripheral bus` 是角色级叫法，不是固定协议名；真实实现可能分别落成 AXI、AHB、APB 或其他厂内 fabric 组合。

## 一条典型数据路径

DMA 搬数据时，常见路径是：

`DMA master -> interconnect -> memory controller / SRAM / accelerator local memory`

这条路的关键是：

- 是否与 CPU 争主干带宽
- 是否穿越多个 bridge
- 返回路径是否也会堵

## 为什么同一系统常常有多条 BUS

因为控制路径和数据路径诉求不同：

- 控制路径更关注简单、稳定、易集成
- 数据路径更关注带宽、并发和低额外开销

## 与 NoC 的边界

在较大的 AI 芯片里，常见做法是：

- BUS 负责寄存器、配置、启动、状态
- NoC 负责 tile 之间和到 HBM 的高吞吐数据交换

## 一句话理解

BUS 的价值不只是“连通”，而是把控制路径和数据路径接入到同一系统地址和事务框架里。
