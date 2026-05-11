# Attention Prefill Case Study

上级：[AI Dataflow 系统视角](./README.md)

相关：[NI / DMA / 存储接口](./ni-dma-memory-interface.md)、[流量模式](./traffic-patterns.md)

## 为什么 prefill 要单独看

prefill（预填充）的特点是：

- 并行度高
- 数据块大
- 多数路径更接近吞吐型 bulk traffic

因此它和 decode（逐token解码）不应混成一个 attention（注意力机制）流量模型。

## 典型 NoC 压力来源

- Q / K / V 相关数据块搬运
- 中间激活在 tile（计算单元）间流动
- 大量 DMA（直接内存访问）与 compute overlap（重叠执行）
- 输出写回或下一阶段继续转发

## 它更像什么类型的问题

prefill 更像：

- bulk movement
- pipeline overlap
- HBM（高带宽存储器）+ NoC 双重吞吐协同

而不是纯低延迟事务问题。

## 你最该观察的点

- HBM port 与 NoC 哪个先饱和
- source injection（源端注入）是否形成大面积拥塞
- packet size 对 serialization latency（串行化延迟）与头开销的影响
- cluster-hierarchical 方案是否提升局部复用

## 常见热点

- HBM / DMA 注入端附近
- 大块流量共同经过的主干链路
- 跨 cluster 的边界路径

## 常见 stall

- `LINK_BUSY`
- `SWITCH_CONFLICT`
- `NO_CREDIT`

如果端点没建模好，还容易错误低估：

- `EJECTION_BLOCKED`

## 一个关键实验

比较：

- flat mesh（扁平网格）
- cluster-hierarchical NoC（分层片上网络）

在 prefill-like trace 下的：

- 主干链路利用率
- 平均和尾部延迟
- DMA overlap 成功率
- tile utilization（计算单元利用率）

## 本页结论

prefill case 的重点，不是事务复杂度，而是大量 bulk traffic 在 memory 和 NoC 之间如何协同，以及局部复用能否真正减少全局通信压力。
