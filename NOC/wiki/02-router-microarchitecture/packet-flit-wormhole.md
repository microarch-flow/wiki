# Packet / Flit / Wormhole

上级：[Router 微架构](./README.md)

相关：[Credit / Backpressure](./credit-backpressure.md)、[NI / DMA / 存储接口](../04-ai-dataflow-system/ni-dma-memory-interface.md)

## 核心心智模型

一个 packet 不是瞬间从源端移动到目的端，而是被切成多个 flit，在多个 router 和 link 上像流水线一样逐跳推进。

## Packet / Flit / Phit

### Packet

packet 是一次完整通信事务的语义单位。

在 AI dataflow NoC 中，一个 packet 可能表示：

- tile-to-tile activation stream
- DMA write burst
- DMA read request
- read response
- partial sum fragment
- barrier 或 descriptor

### Flit

flit 是 router buffer、credit、仲裁所围绕的流控单位。  
现代 NoC 建模中，第一版最值得建立的是 flit-level 模型。

### Phit

phit 是物理链路每周期真正可传输的位宽单位。  
如果你当前目标是架构探索而不是物理链路设计，通常可以暂时不引入 phit。

## Router 的最小结构

可以先把 router 理解为下面四部分：

- input buffer
- routing / allocation logic
- internal crossbar
- output link

更接近真实实现的流水阶段通常包括：

- route computation
- VC allocation
- switch allocation
- switch traversal
- link traversal

## 三种 switching

### Store-and-forward

下游 router 必须先收完整个 packet，才能继续转发。

优点：

- 模型简单
- 局部控制直观

缺点：

- 延迟大
- buffer 需求高

### Virtual cut-through

如果下游有空间容纳整个 packet，就提前开始转发。

它比 store-and-forward 更灵活，但仍然要求较大的 buffer 条件。

### Wormhole

header flit 先行探路，body/tail 紧随其后，packet 像“虫子”一样跨多个 router 拉开。

优点：

- buffer 小
- 可流水
- 更适合面积和延迟敏感的 NoC

代价：

- packet 可能长期占住路径资源
- 阻塞会通过 wormhole 链条扩散

## 为什么 wormhole 对 AI NoC 特别重要

AI 芯片里的流量通常具有：

- tile 数量多
- packet 量大
- 流量持续时间长
- producer-consumer pipeline 明显

此时 wormhole 的低 buffer、低延迟和高吞吐优势很自然，但也意味着：

- destination ejection 变慢会把阻塞一路传回源头
- bulk data 可能压住 control packet
- request / response 若混池，容易形成协议级耦合

## Packet 大小是架构参数，不只是格式参数

大 packet：

- header 开销更低
- 对连续 bulk transfer 更有利

但也会：

- 增大序列化延迟
- 加重 HOL blocking
- 拉长资源占用时间

小 packet：

- 更灵活
- 更适合混合 traffic

但也会：

- 增大 header 比例
- 增加 router 处理压力

## 对建模最重要的三个提醒

- 不要把 packet 当成单周期“数据块”
- 不要只看总带宽，要看 serialization latency
- 不要忽略 destination ejection 和本地 NI FIFO

## 本页结论

面向 AI dataflow 的 NoC，最重要的入口不是复杂拓扑，而是先建立 `packet -> flit -> wormhole -> 资源占用 -> 阻塞扩散` 这条主线。后面的 credit、VC、deadlock 都建立在这条主线之上。
