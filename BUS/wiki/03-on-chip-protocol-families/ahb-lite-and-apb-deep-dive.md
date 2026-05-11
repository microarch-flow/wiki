# AHB-Lite 与 APB 深化

上级：[03 片上总线协议族](./README.md)

相关：[AXI / AHB / APB 对照](./axi-ahb-apb-comparison.md)、[分层总线与协议分工](./hierarchical-bus-and-protocol-roles.md)

## 这页在回答什么问题

AHB-Lite 和 APB 经常被当作“老协议”一笔带过，但它们为什么在很多 SoC 和 MCU 里仍然非常合理。

## AHB-Lite 的定位

AHB-Lite 通常用于：

- 单 master 或低复杂度子系统
- SRAM、ROM、简单 DMA、本地 memory block
- 对时序、面积和验证成本更敏感的设计

它的价值在于：

- 比 APB 更有吞吐能力
- 比 AXI 更容易做小而稳的实现
- 更适合作为 MCU 或轻量 SoC 的骨架

## APB 的定位

APB 更像寄存器访问层，而不是高性能数据层。  
它最适合：

- UART、GPIO、timer、watchdog
- control/status register
- 低频、低带宽、低复杂度外设

## 为什么 APB 很难替代主干总线

因为它本来就不是为这些目标设计的：

- 大 burst
- 多 outstanding
- 高并发 master
- 高带宽 memory access

如果强行拿 APB 承担主干路径，系统会很快暴露吞吐和等待问题。

## 为什么很多设计仍然保留 AHB-Lite

因为不是所有系统都值得付出 AXI 的复杂度。  
当场景满足下面条件时，AHB-Lite 往往更划算：

- master 数量不多
- 流量模型简单
- 软件更关注稳定性而非极致吞吐
- 验证资源有限

## 一句话理解

AHB-Lite 和 APB 之所以长期存在，不是因为“旧”，而是因为它们在很多成本敏感系统里仍然是更合适的复杂度等级。
