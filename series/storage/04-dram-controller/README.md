# DRAM 控制器与请求调度 · Memory Controller

上级：<span id="memory-controller"></span>[存储系统](../README.md)

相关：[DRAM 命令与接口](../03-dram/protocols/README.md) · [存储系统基础](../01-memory-hierarchy/01-system-basics/README.md) · [原有 RAM 阅读入口](../reading-and-reference/01-reading/README.md)

## Memory Controller 的职责 {#这页在回答什么问题}

DRAM 控制器（Memory Controller，MC）连接上游请求与 DRAM 接口。它接收读写事务，在器件和系统约束下安排命令，并处理数据与响应。同一器件面对不同地址流、并发度和控制策略时，实际带宽和延迟可能不同。

本专题解释请求如何映射、排队和调度。DRAM 单元、命令及其时序由[器件与接口](../03-dram/protocols/README.md)介绍；端到端路径和瓶颈判断由[系统基础](../01-memory-hierarchy/01-system-basics/problem-statement.md)与[性能分析](../01-memory-hierarchy/03-performance/effective-bandwidth-vs-peak.md)展开。

## 命令合法性与调度策略

控制器要先判断一条命令是否满足目标接口的状态、时序及共享资源约束，再从可选命令中作决策。地址映射、行保留、读写切换、刷新和多请求源仲裁会共同改变选择空间。实际收益还取决于请求是否同时到达、是否存在依赖、数据通道和上游是否已经饱和。

这些机制不是每个控制器都以相同结构实现。阅读时先固定器件、模式、请求流和观察边界，再比较策略。

## 阅读顺序

1. [控制器：从请求到响应](./why-mc-is-the-real-bottleneck.md)
2. [地址映射](./address-mapping-channel-rank-bank-row-col.md)
3. [请求调度与行保留](./command-scheduling-fr-fcfs.md)：两笔读请求在同一个 bank 排队时，控制器这一拍能发什么命令？保留或关掉当前行，又会怎样改变下一次选择？
4. [写缓冲与写排空](./write-buffer-write-drain.md)
5. [刷新调度](./refresh-management-distributed-postponed.md)
6. [QoS、公平性与隔离](./qos-multi-master-arbitration.md)
7. [控制器仿真建模](./mc-modeling-for-simulation.md)

想理解一次请求怎样变成命令，可先读前 3 篇。分析读写混合、刷新或多请求源时，再读第 4 到 6 篇。最后一篇汇总建模和验证方法。

## 一句话理解

控制器在协议允许的范围内安排请求，最终性能还取决于器件、请求流和上下游共享路径。

## 建模启示

先确定研究问题。比较映射或策略时，需要保留会影响选择的地址、队列、行状态和约束；只估算已校准条件下的粗略耗时，可以采用更简单的模型，并说明它不能预测哪些变化。
