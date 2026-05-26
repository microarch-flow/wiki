# NOC Meets Memory System

上级：[05 System Integration](./README.md)

相关：[RAM: npu memory hierarchy](/mnt/e/wiki/RAM/wiki/09-ai-chip-memory-architecture/npu-memory-hierarchy.md)、[RAM: why mc is the real bottleneck](/mnt/e/wiki/RAM/wiki/06-memory-controller/why-mc-is-the-real-bottleneck.md)、[RAM: qos multi-master arbitration](/mnt/e/wiki/RAM/wiki/06-memory-controller/qos-multi-master-arbitration.md)

## 这页在回答什么问题

这页回答：为什么 NoC 和 memory system 不能分开优化，以及为什么很多“网络瓶颈”最终其实是 local SRAM、HBM port 或 memory controller 在定义上限。

## NoC 不是独立的数据海关

NoC 只负责把流量送到 memory system 边界，真正的数据服务能力来自：

- tile 本地 SRAM / scratchpad
- cluster memory
- shared SRAM pool
- HBM / DRAM port
- memory controller 调度

所以网络吞吐的有效上限不只是 `link_bw`，而是：

```text
effective_bw <= min(network_path_bw, endpoint_bw, bank_port_bw, controller_service_bw)
```

这条关系听起来简单，但被忽略得非常频繁。

## 本地 SRAM 会反向定义 ejection 能力

当数据到达 tile 或 cluster 端时，还要经过：

- ejection FIFO
- local write port
- SRAM bank / port arbitration
- compute 与 DMA / NoC 的共享访问

如果这些局部资源吃不动，NoC 看到的就会是：

- credit 回不来
- ejection blocked
- 上游 injection 被迫放缓

这说明某些所谓的“网络 backpressure”，本质是 local memory consumption backpressure。

## HBM / memory controller 则定义 request-response 节奏

对外部 memory 路径，决定系统节奏的通常不是 NoC hop 数，而是：

- HBM channel 数量
- address interleaving
- controller scheduling
- row / bank / write-drain 行为
- 返回路径的聚合形状

如果 memory controller 本身已经是主瓶颈，那么单纯改善 NoC topology 的收益会迅速变小。

## 为什么 AI 工作负载特别容易暴露这件事

因为 AI 工作负载经常会同时触发：

- 大量规则 bulk read/write
- 局部 SRAM 高频复用
- 某些阶段性的 gather / reduce / writeback
- 对 HBM 返回路径的强依赖

这样一来，NoC 与 memory system 之间几乎没有清晰分界线。流量是否“跑得起来”，很大程度上取决于 memory hierarchy 是如何配平的。

## 一个常见误诊模式

常见误诊是：

- 看到 link 利用率不高
- 又看到系统总吞吐不佳
- 就怀疑 router、routing 或 topology

但更常见的根因其实是：

- DMA outstanding 太小，memory latency 没隐藏住
- HBM port 端口数或调度成了瓶颈
- local SRAM bank conflict 把 ejection 拖住

也就是说，网络“没满”不代表网络“不是系统瓶颈链的一部分”，它可能只是被 memory system 另一端卡住了。

## NoC 和 memory hierarchy 的耦合方式

最关键的耦合有四种：

- `placement coupling`：数据放在哪里，决定流量打向哪里
- `port coupling`：memory port 数量和位置决定热点出口
- `timing coupling`：controller 返回节奏决定 response burst 形状
- `local-consume coupling`：本地 SRAM / compute 消费能力决定终点 backpressure

这四种耦合里，前两种偏结构，后两种偏动态；都必须被建进系统模型。

## deterministic NPU 的典型处理思路

较稳妥的思路通常不是让 NoC 独自兜底，而是同时做：

- 数据布局与 address interleaving
- DMA 节奏控制
- local SRAM bank/port 规划
- 必要时 control/data/memory fabric 分离

这比单纯在 router 里加更多动态智能更贴近 deterministic 设计目标。

## 一句话理解

NoC 决定“数据怎么走到 memory 边界”，memory system 决定“数据到了以后能不能被服务和消化”；两者共同定义有效带宽。

## 建模启示

建模时，NoC 和 memory system 至少要通过这些状态连起来：

- ejection FIFO occupancy
- local bank / port service rate
- memory controller queue / service rate
- HBM channel mapping
- request-response return latency distribution

如果模型只给 memory 一个固定延迟常数，会错过：

- burst 返回峰值
- bank / port 局部热点
- request / response 互相拖累
- effective bandwidth 明显低于 peak 的真实原因
