# NOC Vs Bus Revisited

上级：[05 System Integration](./README.md)

相关：[Bus Vs Noc Vs Crossbar](../01-overview/bus-vs-noc-vs-crossbar.md)、[BUS: AI 芯片里的 BUS vs NoC](/mnt/e/wiki/BUS/wiki/06-scenarios-case-studies/bus-vs-noc-in-ai-chip.md)、[Multiple Physical Networks](./multiple-physical-networks.md)

## 这页在回答什么问题

这页回答：到了系统集成层面，为什么 `BUS` 和 `NoC` 不再是课本里“二选一的互连风格”，而是经常在同一芯片里承担完全不同职责。

## 在 overview 里只回答了抽象区别

在 `01-overview` 里，我们主要说的是：

- BUS 擅长小规模共享与强语义边界
- NoC 擅长大规模并发与可扩展路径组织

到了系统层，这种差异会更具体地落在：

- 谁承载软件可见控制语义
- 谁承载 tile/HBM 之间的大带宽数据面
- completion、fault、debug、boot 通过什么边界闭环

所以这不是“哪个更先进”的问题，而是“哪些职责必须保持简单可见，哪些职责必须扩展到大规模并行”。

## BUS 更像控制骨架

在很多 AI 芯片里，BUS 更适合承载：

- MMIO 配置
- doorbell / start
- status / completion 可见性
- interrupt / debug / boot / reset

原因是这些事务更在意：

- 顺序语义
- side effect 可解释性
- 软件可见性
- 故障恢复和最小可达路径

这类需求不是 NoC 做不到，而是 NoC 不是为了这个目标优化的。

## NoC 更像数据平面

NoC 更适合承载：

- tile-to-tile 数据流
- SRAM/HBM 间大规模搬运
- 多 source 多 destination 并发访问
- collective 或 memory-centric 路径

它的核心优势在于：

- 并发性
- 可扩展性
- 资源空间可分解
- 可做 traffic class 管理

但这套优势主要服务的是数据流，不是软件控制语义。

## 真正关键的是交界处

系统设计里最重要的不是“有 BUS 还是有 NoC”，而是二者的交界处定义得好不好。

关键边界对象通常包括：

- NI 配置块
- DMA command queue
- descriptor fetch path
- completion / status aggregator
- error / timeout 映射路径

这些边界如果定义不好，就会出现经典坏味道：

- 软件已经下发门铃，但 NoC 数据面还没真正起跑
- NoC 内部任务已经完成，但 completion 没回到软件可见边界
- debug 时只看得到控制侧，看不到网络进展

## 为什么这对 deterministic NPU 更敏感

deterministic 系统强调：

- 路径可预测
- completion 时机可控
- 问题可复现

这恰好要求 BUS-control 与 NoC-data 的分界清楚。否则你会得到一个很糟的系统：

- 数据面看似 deterministic
- 但 completion、doorbell、fault 路径却不可解释

这会直接削弱软件与编译器的可推理性。

## 什么时候应该继续用 BUS 思维

当问题是下面这些时，优先用 BUS/control 骨架去思考：

- 某个寄存器写下去后为什么没生效
- 为什么 runtime 没看到 completion
- 为什么 boot/debug 阶段还没起网就要可达

## 什么时候必须切到 NoC 思维

当问题变成下面这些时，就要用 NoC/data-plane 视角：

- 为什么 HBM 到 tile 的大搬运顶不住
- 为什么多个流在某些 router 或 memory port 汇聚成热点
- 为什么不同 traffic class 需要隔离

## 一句话理解

在 AI 芯片里，BUS 负责把控制语义、可见性和故障闭环讲清楚，NoC 负责把大规模数据交换跑起来；真正难的是这两层怎么接住彼此。

## 建模启示

系统模型里，BUS 和 NoC 最好分成两类事件流：

- control-visible：`mmio_write`、`doorbell`、`status_visible`、`interrupt`
- data-plane：`packet_inject`、`route_wait`、`credit_wait`、`response_arrive`

同时要显式定义跨边界事件：

- `descriptor_fetch`
- `command_accept`
- `completion_aggregate`
- `fault_map_to_status`

没有这些跨边界事件，模型就只能解释一半系统。
