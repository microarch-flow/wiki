# Buffer Depth / Credit Sizing / Allocator Policy

上级：[Router 微架构](./README.md)

相关：[Credit / Backpressure](./credit-backpressure.md)、[Router Pipeline 与 Allocator](./router-pipeline-allocator.md)

## 为什么这三件事要放在一起看

很多 NoC 调参最后都会落到这三个旋钮：

- buffer depth
- credit window / round-trip
- allocator policy

它们共同决定：

- 吞吐能否拉起来
- 阻塞扩散得多快
- 哪类流量更容易被饿死

## 一：Buffer Depth

### 太浅会怎样

- credit 很快耗尽
- link 利用率起不来
- 微小抖动就会变成明显 bubble

### 太深会怎样

- 面积成本上升
- 阻塞会在网络里“藏得更深”
- 某些场景下会拖长拥塞恢复时间

### 一个实用直觉

buffer 深度至少要覆盖有效 credit round-trip 的量级，否则长链路或多级 pipeline 下吞吐很容易受限。

## 二：Credit Sizing

credit 本质上是：

- 下游可接收能力的本地代理

但对系统表现来说，更关键的是：

- credit 要飞多久才能回来
- credit 是按 VC 还是按 port 管
- 长链路 / pipeline link 是否拉长 round-trip

### 为什么长链路会推高 buffer 需求

链路越长、pipeline 越多，credit return 越慢。  
如果 buffer 深度没同步增加，发送方会频繁等 credit，网络看起来就像“带宽没打满但又一直在停”。

## 三：Allocator Policy

### 你至少会碰到的几类策略

- fixed priority
- round-robin
- weighted round-robin
- age-based

### 它们真正影响什么

- 谁更容易拿到输出口
- 某类流量会不会长期饥饿
- control / response 是否能穿过 bulk traffic

所以 allocator policy 不只是公平性问题，也是系统 forward progress 问题。

## 这三者如何耦合

### 情况 1：buffer 太浅

allocator 再聪明，也可能只是反复看到“没人有 credit 可发”。

### 情况 2：allocator 太偏

即使 buffer 足够，也可能让某些流量长期拿不到服务。

### 情况 3：credit window 太慢

会把明明有潜在并行度的链路硬生生打成断续发送。

## 第一版 simulator 至少该扫哪些参数

- buffer depth：例如 2 / 4 / 8 / 16
- allocator policy：round-robin / fixed-priority / age-based
- long-link pipeline latency：0 / 1 / 2
- control / response priority on/off

## 最值得看的指标

- link utilization
- average / tail latency
- `NO_CREDIT`
- `SWITCH_CONFLICT`
- starvation 现象
- workload completion time

## 常见误区

- 认为 buffer 越深越好
- 认为 allocator 只影响公平，不影响吞吐
- 认为 credit 只是实现细节，不影响架构结论

这三条都不成立。

## 一个高价值实验

在同一 workload 下比较：

1. 浅 buffer + round-robin
2. 深 buffer + round-robin
3. 深 buffer + fixed priority
4. 深 buffer + response 优先

观察：

- throughput 是由 buffer 限制还是由调度限制
- tail latency 是否因优先级显著改善
- 是否出现低优先级饥饿

## 一个实用判断

如果网络整体 utilization 不低，但关键小消息尾延迟很差，优先怀疑 allocator / QoS。  
如果 utilization 上不去且 `NO_CREDIT` 很高，优先怀疑 buffer / credit sizing。

## 本页结论

buffer depth、credit sizing 和 allocator policy 不是三个孤立参数，而是决定 NoC“能不能稳住吞吐、能不能保护关键路径”的一组耦合旋钮。  
做架构探索时，单独扫其中一个参数往往不足以解释真实表现。
