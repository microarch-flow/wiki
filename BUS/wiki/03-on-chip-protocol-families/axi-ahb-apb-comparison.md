# AXI / AHB / APB 对照

上级：[03 片上总线协议族](./README.md)

相关：[BUS 分类框架](../01-overview/taxonomy.md)、[分层总线与协议分工](./hierarchical-bus-and-protocol-roles.md)

## 这页在回答什么问题

为什么同一个 SoC 里经常同时出现 AXI、AHB、APB，而不是只保留一种协议。

## APB：低复杂度寄存器总线

适合：

- 配置寄存器
- 状态读取
- 低速外设访问

特点是：

- 协议简单
- 一般不追求 burst 和高并发
- 面积和验证成本低

## AHB / AHB-Lite：中等复杂度主干或子系统总线

适合：

- 中低复杂度 SoC 主干
- MCU 级别 memory/peripheral 访问
- 对成本敏感但又需要一定吞吐的系统

特点是：

- 比 APB 强
- 比 AXI 简单
- 更容易实现和调试

## AXI：高性能通用主干总线

适合：

- CPU、DMA、DDR controller 之间的主路径
- 需要独立读写通道和高 outstanding 的场景
- 大量现成 IP 对接

特点是：

- 吞吐潜力高
- 协议自由度大
- 桥接和互连 IP 丰富
- 但实现和验证复杂度明显更高

## 为什么常常会三者并存

因为它们分别覆盖不同层级：

- `AXI` 负责高带宽主干
- `AHB` 负责中等复杂度子系统
- `APB` 负责低速寄存器访问

这比强行用一种协议包打天下更合理。

## 一句话理解

`APB` 追求简单，`AHB` 追求平衡，`AXI` 追求吞吐和扩展性。
