# AI 芯片里的 BUS vs NoC

上级：[06 典型系统与案例](./README.md)

相关：[BUS vs NoC vs Point-to-Point](../02-fundamentals/bus-vs-noc-vs-point-to-point.md)、[NoC Wiki 首页](../../../NOC/wiki/README.md)

## 这页在回答什么问题

为什么 AI 芯片里既需要 BUS，也需要 NoC，而且两者通常不会互相替代。

## BUS 更常负责什么

在 AI 芯片里，BUS 常负责：

- 寄存器配置
- 启停控制
- status / completion
- debug / boot / 管理路径

这些路径的特点是：

- 流量不一定大
- 但语义必须清楚
- 软件可见性要求高

## NoC 更常负责什么

NoC 更常负责：

- tile 到 tile 数据流
- DMA 到 local SRAM / HBM 的高吞吐路径
- collective / multicast / 大规模并发流量

这些路径的特点是：

- 节点多
- 共享带宽压力大
- 需要拓扑和流控层面的扩展性

## 最常见的误判

- “AI 芯片里有 NoC，就不需要 BUS”
- “BUS 也能搬数据，所以不必上 NoC”

现实里更常见的是分工：

- BUS 做控制骨架
- NoC 做主数据面
- point-to-point 做局部专线

## 一句话理解

AI 芯片里的 BUS 和 NoC 不是二选一，而是分别承担 `控制语义` 和 `大规模数据交换` 两种不同职责。
