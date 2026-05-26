# Problem Statement

上级：[01 Overview](./README.md)
相关：[Bus Vs NoC Vs Crossbar](./bus-vs-noc-vs-crossbar.md), [Taxonomy](./taxonomy.md)

## 这页在回答什么问题

为什么 BUS 和小规模 crossbar 在多 tile 系统里会先后失效，以及 NoC 为什么不是“更高级的连线风格”，而是被规模、时序和流量结构逼出来的系统组织方式。

当你后面进入 router、topology 和 source routing 时，如果忘了这个出发点，就很容易把 NoC 学成一堆术语，而不是一套对瓶颈负责的设计。

## 从共享互连到分布式网络，问题是一步步长出来的

少量 master 和 slave 的系统，先遇到的是“谁先访问”问题，所以 BUS 很合适。它把地址、数据、响应和顺序性放在一条共享事务骨架上，软件容易理解，debug 也直接。你在 [BUS 在解决什么问题](../../../BUS/wiki/01-overview/problem-statement.md) 和 [AI 芯片里的 BUS vs NoC](../../../BUS/wiki/06-scenarios-case-studies/bus-vs-noc-in-ai-chip.md) 已经看到这一点：BUS 擅长承载控制语义，擅长让 CPU、DMA、寄存器块和外设围绕统一事务模型工作。

当系统规模上升到十几个端点，设计者通常先想到 crossbar，因为它保留了“单跳、集中仲裁、地址直达”的直觉。这个阶段确实能换到低延迟和简单的事务体验，但代价也开始出现：端口数一增加，mux、仲裁器和全连接布线会一起膨胀；跨芯片长线一多，时序和功耗就不再是局部问题，而变成全局问题。

再往上走到几十、几百个 tile，问题的性质变了。此时互连不再只是“让 A 能访问 B”，而是：

- 多个 producer 同时向多个 consumer 持续灌流量
- HBM、SRAM bank、DMA、tile 之间形成多源多汇的长期并发
- 局部热点会通过 backpressure 反向扩散，直接影响 compute utilization
- 路径、缓冲、仲裁、隔离与调度都开始成为一等设计对象

这时继续用集中式互连，系统会在四个方向同时失稳。

## NoC 要解决的不是“能不能通”，而是“通得是否可持续”

第一类压力是扩展性。共享 BUS 的本质是共享时隙；crossbar 的本质是用更多硬件维持“任意到任意”的直达幻觉。两者都能工作，但节点数量每翻一轮，代价不会线性增长。NoC 的做法不是继续维持全局单点控制，而是把互连拆成 router、link、buffer 和局部仲裁，让复杂度沿拓扑分摊。

第二类压力是物理实现。很多初学者只看逻辑 hop 数，忽略线长。现实里，长线经常比 router 更贵：要插 pipeline、要占 metal layer、要吃掉时钟余量。NoC 之所以演化为多跳网络，并不是因为多跳“更优雅”，而是因为把长线切短、把控制局部化之后，时序和面积才更可收敛。

第三类压力是流量结构。BUS 更像事务串行化器，crossbar 更像单跳交换矩阵；而 AI 芯片里的真实压力来自持续流。权重分发、activation 转发、partial sum 归约、KV cache 回包，这些都不是“一次访问结束就完”的控制事务，而是会在很多周期里持续占用互连资源。NoC 必须显式处理排队、阻塞传播、消息隔离和路径冲突。

第四类压力是可分析性。对 deterministic NPU 而言，互连不是“尽量快一点”就够了，而是要可建模、可调度、最好还能给出 latency 上界。NoC 把通信抽成包、流控单元和路径资源之后，编译器和架构师才有机会讨论 source routing、静态时隙、traffic class 分离和 worst-case analysis。

## AI 系统里真正关心的是哪几条路径会先塌

NoC 在 AI 芯片里最重要的价值，不是替代 BUS，而是把数据搬运从局部接口问题升级成系统资源问题。一个设计是否合理，最后会落到这些问题上：

- 权重从 HBM 到 tile 时，热点集中在哪些 link 和 port
- activation 是本地复用、邻近转发，还是要穿越全网
- partial sum 是在端点归约，还是在网络中途做聚合
- decode 场景里 response path 是否比 request path 更容易先饱和
- 某个 destination 慢下来时，stall 会不会沿 credit/backpressure 一路传回 producer

这也是 NoC 和 BUS 的关键区别。BUS 里你常先问 ordering、decode、response；NoC 里你常先问热点、饱和、阻塞扩散和隔离。两者都处理 backpressure，但层级不同：BUS 上的 `ready/valid` 通常在短路径上解决单笔传输节奏，NoC 上的 flow control 要解决多跳网络中“下游 buffer 满了，上游何时停、何时恢复”的问题。

## 为什么不是“把 BUS 做宽一点”或“把 crossbar 做大一点”

这两个想法都自然，但都只能缓解，不会改变量级。

把 BUS 做宽一点，只能提高单拍可搬运数据量，不能消除共享时隙的本质。多个端点并发时，你仍然要围绕同一控制骨架做仲裁，热点只会从数据位宽转移到事务入口。

把 crossbar 做大一点，可以维持单跳和低延迟，但端口数增加时，布线、仲裁和功耗一起上涨。更要命的是，crossbar 的优点建立在“全局资源仍可集中控制”上；当 floorplan 已经拉开、链路需要分段、端点数量很大时，这个前提就不成立了。

NoC 的演化路径本质上是：承认通信会成为分布式问题，然后用 topology、routing、flow control 和局部资源管理去显式处理它。代价当然存在：你放弃了 BUS/crossbar 的简单事务直觉，引入了 packetization、buffering、deadlock、QoS 和更复杂的验证工作。但不这样做，系统会在更早的规模上失去可实现性。

## 常见误解

常见误解：NoC 只是“更复杂、更快的总线”。  
实际上：NoC 不是 BUS 的提速版，而是把互连从共享事务模型改造成分布式资源模型。

常见误解：只要峰值带宽够高，NoC 就不是瓶颈。  
实际上：真实瓶颈通常先表现为局部拥塞、回包延迟、buffer 耗尽和 backpressure 扩散，不是链路标称带宽不够。

常见误解：NoC 是独立章节，学完 router 再说系统。  
实际上：NoC 如果脱离 workload、DMA、HBM 和 tile interface，就很容易失去工程判断力。

## 一句话理解

NoC 的出现不是因为工程师喜欢网络，而是因为当互连必须同时承受大规模并发、长线时序和可调度数据流时，BUS 和 crossbar 的集中式方法已经不再够用。

## 建模启示

这页对应的第一层模型，不该从“一个 router 有几个阶段”起步，而该从“系统里有哪些通信端点、哪些路径长期有压”起步。最小数据结构可以先是：

```text
Endpoint {
  id
  kind  // TILE, SRAM_BANK, DMA, HBM_PORT, CONTROL
  injection_bw
  ejection_bw
}

FlowDemand {
  src
  dst
  bytes
  traffic_class
  start_time
}
```

在 event-driven 或 analytical 第一版模型里，先显式记录 `flow_inject`、`flow_arrive`、`flow_blocked_by_hotspot` 三类事件就够了。此时可以抽象掉 flit、VC 和 allocator，只看端点对之间的负载矩阵与链路容量。

如果目标升级为 latency/throughput 曲线或 backpressure 归因，就必须把状态细化到 `link_occupancy`、`router_input_queue_depth`、`credit_available`。如果目标是 deterministic NPU 的 worst-case latency 分析，还要继续保留 `route_id`、`traffic_class` 和每条路径上的资源占用顺序，否则“为什么会堵、堵多久、是否可证明无死锁”这三个问题都回答不了。
