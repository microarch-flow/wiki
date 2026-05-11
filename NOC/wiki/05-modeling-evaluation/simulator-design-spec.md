# Simulator 设计规格

上级：[建模与评估](./README.md)

相关：[建模层次](./modeling-layers.md)、[Router Pipeline 与 Allocator](../02-router-microarchitecture/router-pipeline-allocator.md)

## 目标边界

这份规格面向的是：

- workload-driven（工作负载驱动的）NoC（片上网络）architecture exploration
- flit-level（流控单元级别）
- wormhole（虫孔转发）
- credit-based flow control（基于信用的流量控制）
- 可扩展到 VC（虚通道）/ traffic class（流量类别）/ hierarchical topology（层次化拓扑）

它不是 RTL（寄存器传输级），也不是物理实现模型。

## 第一版必须回答的问题

- 哪些 link / port 最先饱和
- stall（停顿）主要来自 credit（信用）、switch（交叉开关）、ejection（弹出）还是系统等待
- 不同拓扑、packet size（数据包大小）、buffer depth（缓冲深度）、placement（放置策略）的相对差异
- NoC 是否已经影响 tile utilization（计算单元利用率）和 workload completion time（工作负载完成时间）

## 推荐的核心对象

### Packet（数据包）

建议至少包含：

- `packet_id`
- `src`
- `dst`
- `traffic_class`
- `size_in_flits`
- `route_id` 或 hop list（跳数列表）
- `creation_cycle`

### Flit（流控单元）

建议至少包含：

- `flit_id`
- `packet_id`
- `flit_type`：header（头）/ body（体）/ tail（尾）
- `seq_in_packet`
- `src`
- `dst`
- `traffic_class`
- `current_router`
- `assigned_vc`

### Router（路由器）

建议至少包含：

- input ports（输入端口）
- per-port VC buffers（每端口虚通道缓冲）
- routing state
- output credit table（输出信用表）
- output VC state
- arbitration state（仲裁状态）

### Link

建议至少包含：

- src router / port
- dst router / port
- bandwidth：默认 1 flit / cycle
- optional pipeline latency

### Endpoint / NI（网络接口）

建议至少包含：

- injection queue（注入队列）
- ejection queue（弹出队列）
- traffic generator / consumer（流量生成器/消费者）
- DMA（直接内存访问）/ memory interface hooks

## 拓扑与路由表示

第一版建议：

- 用 graph 或邻接表表示 topology
- deterministic routing（确定性路由）用函数生成 next hop（下一跳）
- source routing（源路由）用 route table 或 hop list

不要一开始把 route encoding 做成过重的 bit-accurate 结构。

## 每周期主循环建议

推荐统一采用两阶段思路：

### Phase A：收集本周期输入

- 接收 arriving flits
- 接收 returning credits
- 记录 endpoint 新生成的 packet

### Phase B：执行状态转移

- packet -> flit 注入检查
- router RC（路由计算）/ VA（虚通道分配）/ SA（交叉开关仲裁）
- flit move：ST（交叉开关传输）/ LT（链路传输）
- destination ejection
- credit generation
- 统计指标

如果实现上需要，进一步拆成”读旧状态 / 写新状态”的双缓冲（double buffering）模式会更稳。

## 注入与弹出规则

### Injection

packet 不能因为“软件产生了”就立即进入网络，必须满足：

- source injection queue 非空
- 本地可用 VC / 注入通道可用
- 下游 credit 或等效接收条件满足

### Ejection

packet 到达 destination router 不等于任务完成，还要满足：

- ejection queue 有空位
- NI / SRAM（静态随机存储）/ compute consumer 可以接收

否则应统计：

- `EJECTION_BLOCKED`

## Credit 建模规则

必须遵守两条：

1. flit 占用下游 buffer slot 后，credit 先减
2. 只有当该 slot 真正被下游释放时，credit 才返回

不要把 credit 建成同周期瞬时返回，否则吞吐会被高估。

## VC 与 traffic class 的最小支持

第一版建议至少支持：

- `control`
- `memory_response`
- `stream`
- `bulk_dma`

实现上可以从简：

- 每类 1 个逻辑队列
- 或共享物理队列但统计逻辑类

更推荐的做法是显式分离至少部分关键类，以免结果被错误耦合污染。

## 推荐的 stall taxonomy

至少统一支持：

- `NO_CREDIT`
- `SWITCH_CONFLICT`
- `LINK_BUSY`
- `EJECTION_BLOCKED`
- `INJECTION_BLOCKED`
- `ROUTE_BLOCKED`
- `WAITING_FOR_OTHER_STREAM`

并要求：

- 每周期每个活跃 flit / endpoint 只打一个主 stall 标签

## 指标接口

至少输出：

- packet latency 分布
- per-link utilization
- per-router occupancy
- per-traffic-class throughput
- stall breakdown
- tile utilization
- workload completion time

建议输出格式尽量结构化，便于后续扫参数。

## 最小实验集

第一版 simulator 完成后，至少跑这些：

1. 单链路 credit 深度扫描
2. 2D mesh（二维网格）hotspot traffic（热点流量）
3. destination ejection 阻塞传播
4. flat mesh（扁平网格）vs hierarchical NoC（层次化片上网络）
5. GEMM-like（通用矩阵乘法类）和 attention-like trace（注意力类轨迹）

## 第一版不必过度实现的功能

- 复杂 adaptive routing（自适应路由）
- speculatively pipelined allocator（推测式流水线分配器）
- bit-accurate header encoding（位精确包头编码）
- 物理时钟域与 long-wire 细节

## 一个推荐的代码模块划分

- `topology`
- `routing`
- `packet_flit`
- `router`
- `vc_allocator`
- `switch_allocator`
- `link`
- `endpoint`
- `traffic_generators`
- `stats`
- `experiments`

## 完成标准

这版 simulator 至少应该让你能稳定回答：

- 为什么这个 workload 慢
- 慢在网络哪里
- 该改 topology（拓扑）、buffer、QoS（服务质量）还是 mapping（映射）
- 这个结论是否只在某种 traffic 下成立

## 本页结论

一份好的 simulator 规格，不是把实现细节堆满，而是先把状态边界、时序规则、统计口径和实验目标固定下来。  
只要这些边界清楚，你就能逐步加真实度，而不会把模型越写越乱。
