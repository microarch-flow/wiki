# DMA 与 NoC

上级：[05 系统集成](./README.md)

相关：[调度、Outstanding 与回包组织](../03-dma-microarchitecture/scheduling-outstanding.md)、[NOC：从 Workload 到 Traffic Trace](../../../NOC/wiki/07-evaluation-methodology/from-workload-to-traffic-trace.md)、[NOC：NI / 网络接口设计](../../../NOC/wiki/05-system-integration/ni-network-interface-design.md)

## 这页在回答什么问题

为什么在片上大系统和 AI accelerator 里，DMA 往往直接决定 NoC 上看到的 traffic pattern；以及为什么只看拓扑或链路宽度，通常不足以解释 DMA 驱动的拥塞与断供。

## NoC 看到的往往不是“应用流量”，而是 DMA 重新塑形后的流量

应用或 runtime 描述的是“下一块数据该搬到哪里”；真正注入 NoC 的却是 DMA 按自己的 burst、outstanding、priority、completion 节拍组织出来的 request/response 流。于是 NoC 看到的不是原始 workload，而是一个已经被 DMA 调度器重新塑形过的 traffic trace。

这点和 [NOC wiki 的 traffic trace 抽象](../../../NOC/wiki/07-evaluation-methodology/from-workload-to-traffic-trace.md) 直接相连。workload 只给出需求，DMA 决定这些需求以什么粒度、什么节奏、什么方向进入网络。也就是说，DMA 是 NoC 的主动流量源，不是边缘挂件。

## DMA 在 NoC 上常表现出哪几类流量形状

片上 DMA 的典型流量通常落在几类模式里：

- `bulk refill`：大块、连续、偏带宽导向的单向流
- `writeback`：从 compute 侧回流到 SRAM/HBM 的成批写流
- `descriptor/completion`：小而稀疏，但时序敏感的控制流
- `multi-stream mixed traffic`：多个 cluster、tile 或外设同时发起的混合流

这些流在 NoC 上的伤害方式完全不同。bulk refill 容易占满注入带宽与 ejection 口；descriptor 和 completion 虽然带宽小，却常常对尾延迟极敏感；writeback 若和 refill 共享同一条 return/ejection 路，会形成放大回压。

## 只看链路规格会错在哪里

很多系统诊断一上来就问“是不是 mesh 不够宽”“是不是链路带宽太小”。这类问题有时成立，但经常把因果关系看反。因为 DMA 在 NoC 上造成的问题，常常不是单纯链路不够，而是：

- request 注入太猛，把 return path 周期性打爆
- bulk refill 压住了时序敏感 response
- DMA 到 local SRAM 的写入节拍与 compute 读取节拍冲突
- 多路 DMA 流在同一 memory endpoint 前聚成热点

这些都不是单看拓扑能解释的，而必须把 DMA 的 issue policy、outstanding 窗口和 completion 节奏一起放进分析。

## 在 AI 系统里最该盯哪几种冲突

AI accelerator 里的 DMA 与 NoC 耦合尤其强，因为很多流量都围绕“供数是否稳定”展开。最常见的冲突包括：

- refill 和 writeback 互相抬高波峰
- bulk transfer 挤压关键 response，导致 consumer 断供
- NoC 明明没到全局饱和，但某些 ejection 端口已先饱和
- DMA 对 local SRAM 注入过快，bank/port 冲突把下游自己堵死

这也是为什么 `DMA ↔ NOC` 关系不该停留在“DMA 会在 NoC 上搬数据”。更准确的说法是：DMA 决定 NoC 上哪类流成为主流量、哪类流被压成尾流量、哪类流的 latency 被系统放大。

## 从系统建模角度怎么看

这一页是最适合显式接入 `Resource / Topology / Interaction / Capability` 抽象的地方：

- `Resource`：router、NI、ejection port、SRAM port、memory port
- `Topology`：DMA 到 memory / compute / SRAM 的路径长度与共享点
- `Interaction`：request injection、response return、credit/backpressure、completion 反馈
- `Capability`：DMA 的 outstanding、priority、rate control、NoC 的 VC/QoS 能力

如果这四层里少了任意一层，就很容易把“DMA 导致的 NoC 问题”误看成“拓扑问题”或“endpoint 问题”。

## 常见误解

常见误解：`NoC 看到的就是应用原始流量`。实际上 NoC 经常看到的是 DMA 重新组织后的 request/response 波形。

常见误解：`链路没满就说明 NoC 不是瓶颈`。实际上 ejection 端口、response return path 和局部热点都可能先成为瓶颈。

常见误解：`DMA 流量大，所以控制流量可以忽略`。实际上 descriptor、doorbell、completion 这类小流量经常最先被尾延迟伤害。

## 一句话理解

在很多系统里，NoC 看到的不是应用本身，而是被 DMA 调度器重新塑形成的流量；理解 DMA，就必须理解它如何塑造 traffic pattern。

## 建模启示

这一页的最小模型不是“DMA 带宽上限 + NoC 带宽上限”，而是 `DMA issue process -> NoC injection -> response return -> endpoint ejection` 的闭环。event-driven 仿真里，建议显式保留 `injection_rate`、`return_queue_occupancy`、`ejection_stall_cycles` 和 `stream_priority`。

可直接使用的抽象结构是：

```text
DMANoCFlow {
  src_node
  dst_node
  req_rate
  resp_rate
  priority
  path_class
}
```

如果只关心粗粒度吞吐，可以把 path 折叠成平均 hop latency；如果关心局部热点、尾延迟或断供，就必须显式保留路径共享点和 ejection 端口状态。
