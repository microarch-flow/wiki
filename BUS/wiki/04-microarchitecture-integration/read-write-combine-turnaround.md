# Read/Write Combine 与 Bus Turnaround

上级：[04 微架构与系统集成](./README.md)

相关：[AXI 到 DDR Controller 的路径](./axi-to-ddr-controller-path.md)、[带宽、延迟、利用率与拥塞](../05-performance-debug/bandwidth-latency-utilization.md)

## 这页在回答什么问题

为什么读写混合负载下，系统即使理论带宽足够，也会表现出明显抖动和吞吐损失。

## Read/Write Combine 在做什么

memory controller 往往不会严格按到达顺序逐条执行请求，而会：

- 先攒一批读
- 再攒一批写
- 或者在局部窗口内重排

这样做是为了：

- 减少总线方向切换
- 降低命令切换开销
- 提高整体吞吐

## Turnaround 为什么贵

从 read 切到 write，或从 write 切到 read，通常都不是零成本。  
代价可能来自：

- controller pipeline 切换
- PHY / DRAM 侧方向切换约束
- 返回路径和发起路径节奏重新对齐

所以读写交替越碎，效率往往越差。

## 对 AXI master 的可见后果

表现出来常常是：

- 某些读突然尾延迟变长
- 写 response（例如 AXI `B` 返回）集中回来
- 总体吞吐不低，但单请求体验不稳定

这类现象容易被误认为 interconnect 仲裁问题，但根源可能在 controller 侧。

## 一句话理解

read/write combine 是拿局部公平性换总吞吐，turnaround 则是读写切换必须支付的物理代价。
