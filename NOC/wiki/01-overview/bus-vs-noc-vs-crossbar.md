# Bus Vs NoC Vs Crossbar

上级：[01 Overview](./README.md)
相关：[Problem Statement](./problem-statement.md), [NoC Vs Bus Revisited](../05-system-integration/noc-vs-bus-revisited.md)

## 这页在回答什么问题

BUS、crossbar 和 NoC 都是片上互连，但它们优化的对象不同：BUS 优化共享事务语义，crossbar 优化小规模任意互连，NoC 优化大规模并发通信。

如果不先把这三者分清，后面讨论 “为什么 NPU 多用 mesh 而不是 crossbar” 或 “为什么 AI 芯片里仍然保留控制 BUS” 就会一直打架。

## 先讲结论：它们不是同一条坐标轴上的三档性能

很多介绍会把三者写成“BUS 最弱、crossbar 中等、NoC 最强”。这几乎一定会误导，因为它默认三者在解同一个问题。真实情况不是这样。

BUS 解决的是共享事务系统如何正确工作。它关心的是地址 decode、response、ordering、software-visible side effect、错误路径和调试可见性。你可以把它理解成片上控制和通用事务的骨架。

crossbar 解决的是在小到中等规模下，如何用硬件换单跳低延迟和高并发。它延续了很多 BUS 世界的直觉：请求仍像“直达目标”，仲裁仍相对集中，只是共享瓶颈从一根总线变成多个交叉点。

NoC 解决的是规模继续上升后，通信如何在物理上和流量上都可持续。它接受“多跳、局部仲裁、分布式缓冲、路径冲突”这些现实，不再试图维持全局单跳幻觉。

## BUS：交易语义优先

BUS 的第一价值不是峰值带宽，而是语义清晰。CPU 配寄存器、DMA 取 descriptor、软件轮询 status、异常回报 fault，这些行为要求互连先把“事务是否完成、顺序是否满足、错误如何呈现”处理清楚。也正因为如此，BUS 在 AI 芯片里不会消失。即使数据面已经是 NoC，控制面仍常常是 BUS 或 BUS-like fabric。

它的代价也明确。因为控制语义强，BUS 的扩展方式天然保守：共享时隙、集中 decode、明确 response 路径，这些都让它不适合承载大量 tile 间长期并发的数据流。

什么时候选 BUS？当你面对的是：

- 软件可见的寄存器与状态路径
- 启动、doorbell、completion、interrupt 这类控制闭环
- 端点数量有限，且事务吞吐不是主矛盾

什么时候不要强行用 BUS？当流量已经变成大块 tensor movement、many-to-many stream 或持续 memory response 汇聚时，BUS 的优先级就该退回控制面。

## Crossbar：用面积换单跳和并发

crossbar 的吸引力很直接：任意输入可在一跳到任意输出，延迟短，概念直观，适合 cluster 内小规模互连。很多 AI 芯片在 cluster 内、SRAM bank 组内、或者少量 DMA/compute 端口之间，仍然会用 crossbar，因为这时端口数还可控，物理跨度也没大到不可收敛。

crossbar 的问题在于它几乎把所有困难都推给硬件规模。端口数增加时，你不是只多几根线，而是同时放大：

- 交换矩阵规模
- 仲裁复杂度
- 全连接布线压力
- 功耗和频率收敛难度

这就是为什么 crossbar 在 chip-wide 级别不再划算。它不是“不能做”，而是继续做下去，你会越来越像在用二次方代价维持一次方的直觉。

## NoC：承认通信是分布式资源问题

NoC 的核心设计决定，是放弃“所有端点都像直连”的目标，改成“让每一跳只解决局部资源竞争”。这样做带来的好处是：

- link 可以更短，时序更容易分段
- 控制分散到每个 router，不需要全局大仲裁器
- 拓扑、路由和 traffic class 可以按 workload 定制
- 编译器和仿真器可以显式推导热点与延迟上界

代价同样真实：

- 需要 packetization 和 flow control
- 会出现排队、HoL blocking、deadlock、starvation
- 软件或编译器必须面对路径和资源占用问题

所以 NoC 不是“免费扩展”，而是“把不可避免的复杂性搬到一个可分层处理的框架里”。

## 三者的边界，放到 AI 芯片里最清楚

把它们放进 AI 芯片系统里看，分工会非常清楚：

| 场景 | 更适合 BUS | 更适合 Crossbar | 更适合 NoC |
| --- | --- | --- | --- |
| 寄存器配置 / doorbell / completion | 是 | 否 | 否，最多只承载内部传播 |
| cluster 内少量 tile 与本地 SRAM | 否 | 是 | 规模稍大时也可能是 concentrated mesh |
| 全芯片 tile-to-tile 数据流 | 否 | 一般不划算 | 是 |
| HBM port 到大量 tile 的大规模扇出 | 否 | 很难扩到全局 | 是 |
| 广播 / 多播 / reduction overlay | 否 | 小局部可用 | 常需要 NoC 或其专用叠加网络 |

这和 [AI 芯片里的 BUS vs NoC](../../../BUS/wiki/06-scenarios-case-studies/bus-vs-noc-in-ai-chip.md) 的判断一致：BUS 与 NoC 不是替代关系，而是系统分层；crossbar 则常是介于两者之间的局部互连工具。

## 不要把 crossbar 和 NoC 看成“是否分层”的道德判断

有一种常见误解是：用了 NoC 才现代，用 crossbar 就落后。这个判断很差，因为它把规模问题偷换成风格问题。

在 4 到 8 个本地端点、物理跨度也不大的 cluster 内，crossbar 往往是最干净的解。你如果硬上 mesh，可能只是为了追求形式统一，结果引入多跳、buffer 和额外仲裁，反而把简单问题做复杂了。

反过来，在上百个 tile 的全局数据面继续坚持 crossbar，通常也不是勇敢，而是拒绝承认全局布线和时序已经变成一阶约束。

真正应该问的是：这个规模下，哪种互连把主要矛盾暴露得最清楚、代价也最可控。

## 一个实用的选择顺序

先问软件语义是否主导。如果主导，优先考虑 BUS-like 控制路径。

再问互连是否局部、小规模、低跨度。如果是，优先考虑 crossbar 或类似集中互连。

最后问系统是否已经进入大量并发、多源多汇、长线和可调度通信的阶段。如果是，NoC 才是默认基线。

这个顺序看起来朴素，但比“谁性能更强”更可靠。因为你实际上是在按主矛盾选互连，而不是按名词做信仰排序。

## 常见误解

常见误解：crossbar 一定比 NoC 延迟低，所以能用 crossbar 就应该一直用。  
实际上：crossbar 的单跳优势只在规模和物理跨度受控时成立；规模失控后，频率和布线代价会吃掉这部分好处。

常见误解：NoC 出现后 BUS 就只剩历史意义。  
实际上：AI 芯片里的 boot、debug、status、fault 和 software-visible completion，仍然需要 BUS 或 BUS-like 控制骨架。

常见误解：BUS、crossbar、NoC 只是带宽不同。  
实际上：它们首先是三种不同的系统组织方式，带宽只是其中一个结果。

## 一句话理解

BUS 负责把事务语义讲清楚，crossbar 负责在小规模内维持单跳直觉，NoC 负责在大规模系统里把通信变成可扩展、可调度、可建模的分布式资源。

## 建模启示

在 architecture exploration 的早期，三者不需要用同一精度建模。一个很实用的抽象是把互连类型直接放进系统配置：

```text
InterconnectSpec {
  kind  // BUS, CROSSBAR, NOC
  num_endpoints
  per_port_bw
  arbitration_model
  topology_id
}
```

如果 `kind=BUS`，第一版模型要显式保留 `shared_bandwidth`、`arb_queue_len`、`response_order_constraint`。如果 `kind=CROSSBAR`，要保留 `port_conflict_matrix` 和 `crossbar_radix`。如果 `kind=NOC`，至少要继续展开到 `topology_graph`、`route_policy`、`link_bandwidth`。

事件层面可以统一成 `request_issue`、`grant`、`transfer_start`、`transfer_finish`，但只对 NoC 再细化出 `hop_advance`、`credit_return`、`route_blocked`。这样做的好处是：你能先在系统层比较“哪类互连更像瓶颈”，再决定是否进入 flit-level，而不是一开始就把所有方案都建成同一种复杂度。
