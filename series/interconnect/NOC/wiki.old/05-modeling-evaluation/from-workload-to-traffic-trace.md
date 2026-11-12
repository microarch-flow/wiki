# 从 Workload 到 Traffic Trace 操作手册

上级：[建模与评估](./README.md)

相关：[流量模式](../04-ai-dataflow-system/traffic-patterns.md)、[架构探索方法](./architecture-exploration.md)

## 读这页前先统一几个词

- `workload`：真实要执行的模型、算子序列和数据依赖
- `event`：一次有语义的通信动作，比如一次读请求或一次 tile-to-tile 发送
- `flow`：一类持续或成组出现的通信，可由多个 packet 组成
- `trace`：按时间顺序记录好的事件或 packet 序列，供 simulator 直接消费
- `abstraction`：保留决定结论的关键信息，先忽略暂时不影响判断的细节

## 这页解决什么问题

很多人知道 NoC 概念，也知道 workload 很重要，但真正开始建模时会卡在这里：

- 一个 workload（工作负载）到底怎么变成 NoC（片上网络）输入
- 哪些通信该抽象成 packet（数据包）
- 哪些信息必须保留，哪些可以先忽略

这页的目标，就是把 `workload -> traffic trace` 的转换过程明确下来。

## 一条总流程

建议固定按下面 6 步走：

1. 定义 workload 计算图
2. 定义 mapping（映射）/ placement（放置策略）
3. 定义 memory placement（存储放置位置）
4. 提取通信事件
5. 事件转 packet / flow
6. packet / flow 转 trace

## Step 1：先定义 workload 的计算骨架

不要一上来就生成 packet。  
先把 workload 抽象成最小计算对象之间的依赖关系。

至少明确：

- 算子序列
- tile（计算单元）切分粒度
- producer / consumer（生产者/消费者）关系
- 哪些阶段需要同步

## Step 2：定义 mapping / placement

NoC 压力不是 workload 自带的，而是 workload 映射到硬件后才产生的。

至少明确：

- 哪个 tile 执行哪个子任务
- 哪些 tile 邻近
- 哪些子任务跨 cluster

如果没有 placement，就没有真实的 hop（跳数）和热点。

## Step 3：定义 memory placement

至少要明确：

- 权重放在哪里
- activation（激活值）缓存在哪里
- KV cache（键值缓存）放在哪里
- HBM（高带宽内存）/ SRAM（静态随机存储）/ shared memory（共享存储）节点位置

同一个 workload，在不同 memory placement 下会变成完全不同的 NoC 问题。

## Step 4：提取通信事件

把“计算关系”翻译成“通信事件”。

常见事件类型：

- read request
- read response
- write / writeback
- tile-to-tile stream
- multicast（组播）/ broadcast（广播）
- reduce（归约）/ gather（收集）
- barrier（屏障同步）/ control

这一步的关键不是精确字节数，而是先把通信语义分清。

同时建议尽早固定一套 canonical traffic class（统一流量类别口径），例如：

- `CONTROL`
- `MEMORY_REQUEST`
- `MEMORY_RESPONSE`
- `STREAM`
- `BULK_DMA`

这样后面的 trace、simulator 和实验模板才不会各写各的。

## Step 5：事件转 packet / flow

把每个通信事件转成可以输入 NoC 模型的对象。

### 对第一版最实用的抽象

每个事件至少转成：

- `src`
- `dst`
- `traffic_class`
- `size`
- `start_time` 或依赖触发条件

如果是 collective（集合通信），可以先拆成：

- one-to-many flows
- many-to-one flows
- many-to-many flows

## Step 6：packet / flow 转 trace

最终 trace 不一定一开始就要精确到每周期。  
第一版可以先做 event trace（事件轨迹），再逐步细化成 cycle-aware trace（周期感知轨迹）。

### 最小 trace 格式建议

```text
time, src, dst, traffic_class, bytes, flow_id, dependency
```

如果进一步 packetize，再拆成：

```text
packet_id, flow_id, src, dst, class, num_flits, release_time
```

## 你必须保留的 5 类信息

- 通信方向
- 通信大小
- 通信类别
- 时序关系
- placement / memory placement

如果丢了其中几项，后面的 NoC 分析通常会失真。

## 第一版可以先忽略什么

- bit-accurate payload
- 具体地址编码
- 完整软件 runtime 细节
- 非关键路径上的细碎控制元数据

你现在的目标是形成架构洞察，不是复刻软件栈。

## 四类最常见 workload 的转换思路

### GEMM（通用矩阵乘法）

- 提取权重（weight）分发
- 提取 activation 流动
- 提取 partial sum（部分和）gather

### Prefill（预填充）

- 提取 bulk read / write（大块读写）
- 提取阶段间 activation 流
- 标记 HBM 注入热点

### Decode（解码）

- 提取 KV（键值）request / response
- 标记 response 在关键路径上的依赖
- 单独保留 control / sync 类消息

### MoE（混合专家模型）

- 提取 dispatch（分发）/ gather
- 标记 expert（专家）分布
- 保留 many-to-many 结构

## 一个简单但很重要的原则

先把 trace 做“对”，再把 trace 做“细”。  
不要一上来就试图做极高精度 trace，否则你会把时间花在不关键的细节上。

## 一份最小工作模板

```md
# Workload To Trace

## Workload

## Mapping / Placement

## Memory Placement

## Traffic Events

## Packetization Assumptions

## Resulting Trace Schema

## Known Simplifications
```

## 本页结论

从 workload 到 traffic trace 的关键，不是“把所有实现细节都还原”，而是先保住 `依赖、类别、大小、方向、位置` 这 5 件最影响 NoC 结论的东西。  
只要这一步做对，你的建模就已经进入有效区间。
