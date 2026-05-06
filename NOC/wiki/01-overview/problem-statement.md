# NoC 在解决什么问题

上级：[01 概览与问题定义](./README.md)

相关：[NoC 分类框架](./taxonomy.md)、[AI Dataflow NoC vs CPU Coherent NoC](../04-ai-dataflow-system/ai-vs-cpu-noc.md)

## 一句话定义

`Network-on-Chip` 是把芯片内部大量模块之间的数据交换，抽象成一个分布式、小型网络系统。

## 它为什么会出现

当芯片内部只有少量 master / slave 时，bus 或小规模 crossbar 往往够用。  
当系统扩展到几十、几百个 tile，并同时挂接 SRAM、DMA、HBM port、control plane 时，集中式互连会迅速暴露问题：

- 带宽无法随节点数量平滑扩展
- 线长、仲裁与 mux 规模使面积和功耗恶化
- 全局控制路径过长，时序收敛困难
- traffic pattern 一复杂，就会出现热点和拥塞

## AI 芯片里真正关心的不是“能不能通信”

而是下面这些更工程化的问题：

- 权重从 HBM 到 tile 怎么走
- activation 是否能 tile-to-tile forward
- partial sum 是否需要 reduce
- KV cache 访问是否挤占主数据流
- destination 消费变慢时，stall 会不会通过 backpressure 传回 producer
- NoC 的拥塞会不会直接降低 compute utilization

## 从系统角度看，NoC 的价值

NoC 的核心价值是把片上通信变成可管理的设计对象：

- 可扩展：节点增加后仍能维持可接受的复杂度
- 可预测：编译器和架构师能够推断热点与瓶颈
- 可建模：可以在 workload、placement、traffic pattern 之上做分析
- 可分层：把 router、link、flow control、traffic injection 分开建模

## NoC 不是独立层，它总是服务 workload

对 AI accelerator 来说，NoC 不应脱离数据流讨论。  
更准确的提问方式是：

- 这个 workload 的主通信模式是什么
- 这个 mapping 会把压力集中到哪些 link/router
- 这个 NoC 设计是否能支撑预期吞吐
- 系统瓶颈究竟在 compute、HBM、DMA 还是 NoC

## 常见误区

- 把 NoC 当成“片上网线”，忽略其对系统吞吐的反作用
- 只看峰值带宽，不看拥塞、排队和 backpressure
- 只看平均 hop，不看 floorplan 与热点位置
- 脱离 compiler/runtime 谈 NoC

## 本页结论

NoC 在 AI 推理芯片中的本质，是一套面向数据流的分布式通信系统。  
学习 NoC 的正确主线不是单独背术语，而是把 `router 微架构 -> 流量模式 -> 系统吞吐` 连成同一张图。
