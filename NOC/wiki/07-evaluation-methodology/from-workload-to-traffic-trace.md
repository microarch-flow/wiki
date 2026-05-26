# From Workload To Traffic Trace

上级：[07 Evaluation Methodology](./README.md)

相关：[Traffic Patterns And Characterization](../05-system-integration/traffic-patterns-and-characterization.md)、[Compiler NOC Co Design](../06-ai-noc-specifics/compiler-noc-co-design.md)

## 这页在回答什么问题

这页回答：真实 workload 怎样一步步变成 simulator 能消费的 traffic trace，以及中间哪些信息绝对不能丢。

## 核心原则

trace 的目标不是复刻完整软件栈，而是保住最影响 NoC 结论的结构信息。

最关键的通常是五件事：

- 谁和谁通信
- 什么时候通信
- 通信多大
- 属于什么 traffic class
- 它被放在硬件的什么位置

如果这五项保住了，第一版 trace 通常就已经进入有效区间。

## 推荐转换流程

一个稳定的流程通常是：

1. 定义 workload 计算图
2. 定义 mapping / placement
3. 定义 memory placement
4. 提取通信事件
5. 事件转 packet / flow
6. flow 转 trace

这六步的意义在于：NoC 压力不是 workload 天生自带的，而是在 workload 遇到具体硬件布局之后才真正出现。

## Step 1: 先定计算骨架

先不要急着拆 packet。先把最小有意义的计算对象和依赖列出来，例如：

- operator sequence
- producer-consumer relation
- stage boundary
- synchronization point

这样后面才能判断哪些通信处在关键路径上。

## Step 2: 再定 placement

没有 placement，就没有真实的：

- hop
- hotspot
- cluster boundary
- cross-die path

同一个逻辑 workload，在不同 placement 下会变成完全不同的 NoC 问题。

## Step 3: memory placement 单独处理

至少要明确：

- weight 放哪里
- activation / scratchpad 放哪里
- KV cache 放哪里
- HBM channel / SRAM cluster 如何映射

很多 NoC 结论实际上首先由 memory placement 决定，而不是由 routing 决定。

## Step 4: 提取通信事件

这一步要把计算关系翻译成 NoC 语义对象。常见类型包括：

- read request
- read response
- write / writeback
- tile-to-tile stream
- multicast / broadcast
- gather / reduce
- barrier / control / completion

最重要的是尽早固定一套 canonical traffic class，否则后面 simulator 和实验模板会不断漂移。

## Step 5: 事件转 flow / packet

第一版最实用的抽象通常不是 bit-accurate packet，而是一个 flow 记录：

- `src`
- `dst`
- `traffic_class`
- `bytes`
- `release_time`
- `dependency`

如果是 collective，再转成：

- one-to-many
- many-to-one
- many-to-many

即可。

## Step 6: flow 转 trace

最终 trace 不一定一开始就要 cycle-perfect。可以先有两级：

- event trace
- packet / flit trace

event trace 适合更快的上层探索；packet / flit trace 适合更细粒度模拟。

## 最小 schema 应该长什么样

一个最小 flow/event trace 至少应包含：

```text
time, src, dst, traffic_class, bytes, flow_id, dependency, placement_context
```

如果需要 packetize，再补：

```text
packet_id, flow_id, num_flits, release_time, route_hint
```

## 第一版可以先忽略什么

通常可以先忽略：

- payload bit pattern
- 完整 runtime bookkeeping
- 非关键路径的细碎 metadata
- 过细地址编码

因为你的目标是架构洞察，不是协议复刻。

## workload-specific 提示

- GEMM：先提取 broadcast、forwarding、gather/reduce
- prefill：先提取 bulk movement 和 HBM 注入热点
- decode：务必保留 request/response 与 dependency chain
- MoE：务必保留 expert skew 与 many-to-many 结构

## 一句话理解

从 workload 到 trace 的关键，不是“越细越真”，而是把最决定 NoC 结论的依赖、位置、类别和时间结构稳定保留下来。

## 建模启示

trace 生成器和 simulator 之间最好有明确契约：

- trace schema 固定
- traffic class 枚举固定
- placement / memory placement 上下文固定
- simplification 列表显式记录

这样 trace 才能作为可复现实验资产，而不是一次性脚本产物。
