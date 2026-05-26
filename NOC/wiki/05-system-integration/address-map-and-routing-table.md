# Address Map And Routing Table

上级：[05 System Integration](./README.md)

相关：[Source Routing For Deterministic Systems](../04-routing-and-flow-control/source-routing-for-deterministic-systems.md)、[Topology Physical Realization](../03-topology/topology-physical-realization.md)、[RAM: address mapping channel rank bank row col](/mnt/e/wiki/RAM/wiki/06-memory-controller/address-mapping-channel-rank-bank-row-col.md)

## 这页在回答什么问题

这页回答：地址映射为什么不只是“软件视角的可访问性问题”，而是直接定义 NoC 流量落点、memory port 压力和热点分布的系统规则。

## 地址空间最终要落到物理 node

NoC 并不理解“这个 tensor 很重要”这类高层语义。对网络来说，更直接的问题是：

- 这个地址最终对应哪个 tile、哪个 SRAM、哪个 HBM channel、哪个 control hub
- 走哪张网络
- 在源端被解析成什么目的 node 或 route id

因此 address map 的后果至少有三层：

- 软件层：地址是否可用、是否符合编程模型
- 系统层：请求被送到哪个资源岛
- 网络层：哪几段链路和哪几个 memory port 会被压热

## NI decode 和 router decode

常见有两种方式：

- `NI-side decode`：源端先把地址解析成 node id / network / route id
- `router-side decode`：部分网络节点在中间继续根据地址判断转发

对 deterministic AI 芯片，更常见的是前者，因为：

- 编译器和 runtime 更容易静态推断路径
- router 保持更轻
- address map 可以直接服务 placement 和 DMA 计划

这也意味着：编译器、NI、memory map 三者必须共享同一套边界认知。

## address map 为什么会决定热点

假设一个大 tensor 被连续放进某一段地址区间，而这段区间最终集中映射到一个 HBM channel 或少数 SRAM cluster，那么：

- 连续 DMA 看起来像“顺序访问”
- 但从 NoC 视角看，所有流都在打同一组目的端口

这时热点根因不是 routing 不够聪明，而是 address placement 本身把需求集中到了同一个物理出口。

## interleaving 是典型的系统级调压手段

常见做法是把连续地址按固定粒度散到多个 channel 或 bank：

- page 级 interleaving
- bank 级 striping
- channel round-robin

它的价值在于把“逻辑上连续”的大对象拆散到多个物理服务点，从而：

- 降低单 port 热点
- 提高整体并发
- 让 bisection 带宽真正被用上

但代价也真实存在：

- 编译器和 runtime 需要理解这种映射
- locality 和 row-buffer friendliness 可能下降
- 某些 workload 的 memory behavior 会更难预测

所以 interleaving 不是免费午餐，而是 throughput 与局部性之间的交易。

## routing table 不是孤立存在的

无论是目的 node 路由还是 source-routed route table，最终都和 address map 紧耦合。

典型链条是：

```text
logical object
-> placed at address range
-> decoded to target node / channel / network
-> mapped to route or route id
-> injected into specific NoC resources
```

这说明一个很重要的系统事实：address map、routing table 和 placement 实际上是同一个问题的不同视角。

## deterministic NPU 为什么更依赖它

在 deterministic 系统里，很多优势都建立在“提前知道通信会去哪”之上。因此地址映射不是后处理细节，而是前期架构约束。

如果 address map 设计得模糊或多义，后果会包括：

- 编译器无法稳定做 traffic 规划
- 同一 workload 在不同运行下热点不可复现
- source routing 的静态价值被削弱

## 它和多网络的关系

地址解析结果不仅可以决定目标 node，也可以顺带决定：

- control traffic 走 control network
- tile SRAM traffic 走 data network
- HBM traffic 走 memory fabric

因此“哪段地址走哪张网”本身就是系统设计的一部分，而不是纯软件 convention。

## 常见误区

- 认为地址映射只是软件 ABI
- 认为热点是 router 算法问题，不是地址布局问题
- 认为 route table 一旦写好，地址空间怎么切都无所谓

更准确的说法是：

- 地址映射直接塑造了网络服务点分布
- 很多热点首先是 resource placement 问题
- route table 的价值要建立在稳定、清晰的地址映射之上

## 一句话理解

address map 决定“请求到底打到哪里”，routing table 决定“去那里走哪条路”；两者一起定义了 NoC 的真实流量地理。

## 建模启示

模型里至少要显式保留：

- `addr -> node`
- `addr -> memory channel / bank / cluster`
- `addr -> network / traffic class`
- `node / class -> route or route_id`

如果要做系统级探索，还应把下面几项参数化：

- interleaving granularity
- address region placement
- HBM / SRAM port count
- memory-side parallelism

否则你只能看到“链路上有流量”，看不到“为什么这些流总在同一处会师”。
