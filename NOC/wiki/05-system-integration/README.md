# 05 System Integration

上级：[NOC Wiki](../README.md)

相关：[Routing And Flow Control](../04-routing-and-flow-control/README.md)、[AI 芯片里的 BUS vs NoC](/mnt/e/wiki/BUS/wiki/06-scenarios-case-studies/bus-vs-noc-in-ai-chip.md)、[RAM: memory hierarchy as system](/mnt/e/wiki/RAM/wiki/07-system-architecture/memory-hierarchy-as-system.md)

## 这页在回答什么问题

这一章回答：NoC 不再被当成“router 和 link 的组合”之后，它和真实系统里的哪些对象发生耦合，这些耦合又如何反过来改变 NoC 的瓶颈形状。

真正的芯片里，NoC 从来不是孤立存在的。它至少要和下面这些东西一起看：

- endpoint 的 `NI`
- DMA 的 request / response 组织方式
- 地址空间到 node / memory port 的映射
- tile 本地 SRAM 与 cluster memory 的消费能力
- control path 与 data path 的分离方式
- 多物理网络或多平面的组织

如果这些边界没建进去，NoC 分析通常会出现一个假象：网络看起来并不忙，但系统还是慢。

## 这一章的主线

这章不再讨论“packet 在路上怎么跑”，而讨论“谁把 packet 发上路、谁在终点接住它、为什么端点和 memory system 会反向定义网络行为”。

要点可以概括成五句：

- `NI` 决定语义层事务如何变成 packet 流
- `DMA` 决定 memory traffic 是平滑还是脉冲式爆发
- `address map` 决定流量最终落到哪些物理 node 和 port
- `local memory` 与 `memory controller` 决定目的端能不能真正吃下流量
- `multiple networks` 决定不同 traffic class 是共享冲突，还是物理隔离

## 为什么这章对 deterministic NPU 特别关键

deterministic NPU 的主流量往往不是“随机出现”的，而是由：

- 编译器 placement
- DMA 计划
- local SRAM 容量与 bank 组织
- HBM channel 分配
- control / data / collective 的系统分工

共同塑造的。

这意味着 NoC 的很多关键现象其实来自系统集成边界，而不是 router 局部策略本身。工程上经常发生的情况是：

- 你以为是 topology 问题，其实是 address interleaving 不好
- 你以为是 routing 问题，其实是 DMA outstanding 太激进
- 你以为是网络堵了，其实是 ejection 端 bank conflict

## 和前后章节的关系

- 前一章讲的是路径、仲裁、QoS 和 deadlock 机制；这一章讲的是这些机制承载的真实系统对象。
- 后一章 `06-ai-noc-specifics` 会继续深入 AI 工作负载、collective、chiplet、memory-centric 路径和 compiler co-design。
- 如果只想先建立最小系统直觉，这一章比 AI case study 更优先。

## 读完这章后应该得到什么

读完后，你应该能回答：

- 为什么 `NI`、DMA 和 memory port 常常比 router 更先成为系统瓶颈
- 为什么地址映射会决定热点，不只是决定“能不能访问到”
- 为什么 `NoC vs BUS` 在 AI 芯片里不是替代关系，而是分层关系
- 为什么 control/data 分离常常比继续加 QoS 规则更有效
- 为什么本地 SRAM bank conflict 会伪装成 NoC backpressure

## 一句话理解

NoC 只有放回 `NI + DMA + address map + memory system + multi-network` 这个系统边界里，性能和瓶颈才有真实含义。

## 建模启示

这一章对应的模型，至少要增加五类端点与系统状态：

- `NI`：packetization、reassembly、injection/ejection FIFO
- `DMA`：burst size、outstanding window、request/response queue
- `address map`：`addr -> node / port / network` 的解析规则
- `memory system`：local SRAM bank/port、HBM port、controller service rate
- `network partitioning`：traffic class 到 VC 或物理网络的映射

如果模型只有 router/link，而没有这些对象，常见误差会包括：

- 高估有效带宽
- 低估 tail latency
- 错把 endpoint stall 当成网络拥塞
- 错把地址布局问题当成 routing 问题
