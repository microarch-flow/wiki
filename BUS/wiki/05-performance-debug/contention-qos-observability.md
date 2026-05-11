# 争用、QoS 与可观测性

上级：[05 性能与调试](./README.md)

相关：[仲裁、顺序性与 Backpressure](../02-fundamentals/arbitration-ordering-backpressure.md)

## 这页在回答什么问题

当 BUS 出现“偶发慢”“某个外设卡住”“DMA 时好时坏”时，应该怎么建立可调试的观察框架。

## 争用最常见的来源

- 多个 master 抢同一个 memory slave
- 低优先级流量长期被压
- bridge 后面的慢外设把回压传回主干
- response 路径资源不足

## QoS 在解决什么

QoS 的目标通常不是让所有流量都快，而是：

- 保证关键路径不会被饿死
- 限制低优先级大流量的破坏性
- 控制延迟抖动

## 需要哪些观测点

最有价值的通常不是协议波形本身，而是：

- 每个 master 的等待周期
- 每个 slave 的 busy 周期
- FIFO occupancy
- outstanding 深度
- error / timeout 计数

## 一句话理解

BUS 调试的核心不是“多打一堆波形”，而是找出 `哪一类流量、在哪个共享点、以什么方式被卡住`。
