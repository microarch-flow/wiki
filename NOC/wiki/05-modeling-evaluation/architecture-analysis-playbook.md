# 架构分析题库 / 决策模板 / 自测清单

上级：[建模与评估](./README.md)

相关：[从 Workload 到 Traffic Trace 操作手册](./from-workload-to-traffic-trace.md)、[检查清单](../06-reference/checklists.md)

## 为什么这页重要

知道知识点，不等于真的会做架构分析。  
真正的能力来自两件事：

- 知道该问什么问题
- 知道该如何收敛成决策

这页给你的是“可反复使用的分析套路”。

## 一：架构分析主问题模板

每次分析一个 NoC 方案，先固定回答下面 8 个问题：

1. workload 的主通信类型是什么
2. traffic 的关键路径是什么
3. memory placement 是什么
4. 最先饱和的链路 / 端点在哪里
5. 主要 stall 类型是什么
6. 根因在 NoC、endpoint、memory 还是 mapping
7. 哪个参数最可能改善结果
8. 这个结论的边界是什么

如果这 8 个问题答不清，说明分析还没站稳。

## 二：决策模板

适用于：

- 选 topology
- 选 QoS 策略
- 选 response isolation
- 选 hierarchical 与否

推荐格式：

```md
# Decision: <topic>

## Goal

## Options

## Workload Assumptions

## Key Metrics

## Main Tradeoff

## Best Option Under Current Assumptions

## What Could Change This Decision
```

## 三：按场景的分析题库

### 场景 1：GEMM-like 规则 workload

你应该优先问：

- forwarding 是否值得
- hierarchical 是否提高局部复用
- partial sum gather 会不会成热点

### 场景 2：Decode-like memory-centric workload

你应该优先问：

- response path 是否被压住
- KV placement 是否不合理
- QoS 是否改善 tail latency

### 场景 3：MoE-like dynamic workload

你应该优先问：

- all-to-all 是否暴露 topology 弱点
- source routing 是否 still useful
- QoS / fairness 是否成为关键

### 场景 4：Collective-heavy workload

你应该优先问：

- software replication 是否已经不够
- reduce / gather 是否需要层级化
- tree-like 或 hierarchical 结构是否更合适

## 四：常见错误决策模板

下面这些判断要警惕：

- “带宽够大，所以 NoC 不会是瓶颈”
- “平均 latency 下降，所以架构更好”
- “链路利用率不高，所以系统没被 NoC 限制”
- “adaptive routing 更复杂，所以一定更好或一定更差”

真正稳妥的做法是把判断拉回：

- stall breakdown
- tail latency
- endpoint behavior
- workload completion time

## 五：自测清单

如果你读完整套 wiki，应该能独立回答下面这些题：

### 基础题

- 为什么 wormhole 会放大 backpressure
- 为什么 response path 常常比 request path 更敏感
- 为什么 VC 不只是吞吐优化

### 建模题

- 怎么把 GEMM workload 转成 traffic trace
- 为什么 decode 要单独保留 response class
- 为什么 hierarchical NoC 只有在有局部性时才值

### 分析题

- 如果 `NO_CREDIT` 很高但 link utilization 不高，先查什么
- 如果 tail latency 很差但平均 latency 正常，说明什么
- 如果 prefill 表现好但 decode 表现差，优先怀疑什么

## 六：一个最实用的分析顺序

每次拿到结果后，建议按这个顺序看：

1. workload completion time
2. tail latency
3. stall breakdown
4. hotspot link / endpoint
5. topology / QoS / placement 参数变化

不要先盯着平均带宽或平均 latency。

## 七：什么时候说明你已经“能上手了”

如果你已经能：

- 把一个 workload 变成 trace
- 说清主 bottleneck 在哪里
- 解释主要 stall 类型
- 给出一个有边界的设计判断

那就已经具备了做 first-order NoC architecture analysis 的能力。

## 本页结论

架构分析能力的核心，不在于再多记几个概念，而在于把问题、证据、结论和边界稳定地串起来。  
这页的题库、模板和自测清单，正是为了把这种能力固定下来。
