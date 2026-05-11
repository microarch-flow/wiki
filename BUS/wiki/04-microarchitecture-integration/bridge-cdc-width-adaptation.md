# Bridge、CDC 与 Width Adapter

上级：[04 微架构与系统集成](./README.md)

相关：[位宽、时钟、Burst 与延迟](../02-fundamentals/width-clock-burst-latency.md)、[分层总线与协议分工](../03-on-chip-protocol-families/hierarchical-bus-and-protocol-roles.md)

## 这页在回答什么问题

为什么一个看似简单的 bridge，往往是 SoC 集成里最容易藏延迟、吞吐损失和 bug 的地方。

## Bridge 在做什么

bridge 常见职责包括：

- 协议转换
- 时钟域跨越
- 位宽转换
- burst 拆分或合并
- error / timeout 处理

## CDC 带来的代价

跨时钟域几乎一定需要额外缓冲或握手。  
这会带来：

- 固定额外延迟
- 峰值吞吐下降
- 背压传播更复杂

## Width Adapter 的隐含问题

宽到窄时要拆拍，窄到宽时要拼拍。  
这会影响：

- 对齐要求
- byte enable 组织
- 小包效率
- burst 边界处理

## 常见误区

- “bridge 只是 glue logic”
- “协议能对上就说明性能没问题”
- “CDC 只要过形式验证就结束了”

## 一句话理解

bridge 是片上总线系统的变换层，它把不同协议、位宽和时钟域接起来，也把很多性能和正确性风险集中在一起。
