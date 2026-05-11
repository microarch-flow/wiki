# Buffer Depth / Credit Sizing / Allocator Policy

上级：[Router 微架构](./README.md)

相关：[Credit / Backpressure](./credit-backpressure.md)、[Router Pipeline 与 Allocator](./router-pipeline-allocator.md)

## 为什么这三件事要放在一起看

很多 NoC 调参最后都会落到这三个旋钮：

- buffer depth（缓冲区深度）：每个 VC 能存多少 flit
- credit round-trip（信用往返延迟）：发出 flit 到收回 credit 的周期数
- allocator policy（分配器策略）：多个 flit 竞争同一资源时谁优先

它们共同决定：

- 吞吐能否拉起来（buffer 和 credit 决定上限）
- 阻塞扩散得多快（buffer 深度决定 backpressure 传播速度）
- 哪类流量更容易被饿死（allocator 策略决定公平性）

**三者是耦合的——单独调任何一个，效果都可能被另外两个抵消。**

## 一：Buffer Depth

### Sizing 公式

```
每个 VC 的最小 buffer 深度 = credit round-trip 周期数（R）

R = link_latency(forward) + consume_latency + link_latency(credit return)
```

其中：
- `link_latency(forward)`：flit 从当前 router 到下游 router 的传输周期数
- `consume_latency`：下游 router 从 buffer 中取走 flit 并释放 slot 的周期数（通常 1 周期）
- `link_latency(credit return)`：credit 从下游飞回上游的周期数

### 具体计算示例

```
场景 1：短链路（相邻 router）
  forward link = 1 周期
  consume = 1 周期
  credit return = 1 周期
  R = 3
  → 每个 VC 至少 3 个 slot

场景 2：长链路（跨 cluster，link 中插入流水寄存器）
  forward link = 3 周期（2 级 pipeline register）
  consume = 1 周期
  credit return = 3 周期
  R = 7
  → 每个 VC 至少 7 个 slot

场景 3：场景 2 + 留余量应对 SA 竞争
  R = 7，但 SA 竞争可能导致 1-2 周期额外延迟
  → 实际设计：每个 VC 设 8-10 个 slot
```

### buffer 深度与 link 利用率的关系

```
buffer 深度 = R 时：
  理想状态下 link 利用率 100%（credit 刚好接得上）
  但任何 SA 竞争或微小抖动都会造成气泡

buffer 深度 = R + 2 时：
  有 2 个 slot 的余量吸收竞争和抖动
  link 利用率在实际 traffic 下接近 100%

buffer 深度 = R - 1 时：
  link 利用率上限 = (R-1)/R
  例如 R=3 时，buffer=2 → 利用率上限 67%，丢了 33% 带宽

buffer 深度 = 1 时：
  利用率上限 = 1/R
  例如 R=3 时 → 利用率仅 33%，基本不可用
```

### 太浅 vs 太深

| | 太浅（< R） | 适中（R 到 R+2） | 太深（>> R） |
|---|---|---|---|
| link 利用率 | 受限，有气泡 | 接近 100% | 接近 100%（收益不再增加） |
| 面积成本 | 最小 | 适中 | 大（SRAM 线性增长） |
| backpressure 传播 | 极快（buffer 瞬间填满） | 适中 | 很慢（阻塞被大量 buffer 吸收） |
| 拥塞恢复 | 快（积压少） | 适中 | 慢（大量积压需要排空） |

**实用原则：buffer 深度 = R + 2 是性价比最高的起点。** 既保证 link 不空转，又不过度浪费面积。

### 总 buffer 预算计算

```
一个 router 的 input buffer 总量 = 端口数 × VC数 × 每个VC深度

例：5-port router（East/West/North/South/Local），3 个 VC，每个 VC 深度 6
  总量 = 5 × 3 × 6 = 90 flit slots

如果 flit 宽度 = 128-bit = 16 bytes：
  总 SRAM = 90 × 16 = 1440 bytes ≈ 1.4 KB per router

一个 8×8 mesh 有 64 个 router：
  全网 input buffer = 64 × 1.4 KB ≈ 90 KB
```

这就是为什么 VC 数量和 buffer 深度的乘积是关键面积约束。

## 二：Credit Sizing

credit 的初始值 = 对应下游 VC 的 buffer 深度（详见 [Credit / Backpressure](./credit-backpressure.md)）。Credit sizing 真正需要关注的是 **round-trip 延迟在不同场景下的变化**。

### 影响 credit round-trip 的因素

| 因素 | 影响 | 典型值 |
|------|------|--------|
| link 物理长度 | 长 link 需要插入 pipeline register，增加传输周期 | 短 link 1 周期，长 link 2-4 周期 |
| pipeline register 级数 | 每增加一级，forward 和 credit return 各多 1 周期 | 0-3 级 |
| 下游 buffer read 延迟 | flit 从 buffer 被取走到 slot 释放的延迟 | 通常 1 周期 |
| credit return 路径 | credit 信号是否也走 pipeline link（通常是） | 与 forward link 对称 |

### 不同场景的 credit round-trip

```
场景 A：cluster 内部短链路
  forward: 1    consume: 1    return: 1    → R = 3
  → 每个 VC 需 3-5 slot

场景 B：cluster 间中等链路（1 级 pipeline）
  forward: 2    consume: 1    return: 2    → R = 5
  → 每个 VC 需 5-7 slot

场景 C：跨芯片长链路（3 级 pipeline）
  forward: 4    consume: 1    return: 4    → R = 9
  → 每个 VC 需 9-11 slot

实际设计中，同一芯片内可能同时存在场景 A 和 B：
  cluster 内 router：VC 深度 4-6
  cluster 间 router：VC 深度 8-10
  → 不同位置的 router 可以有不同的 buffer 配置
```

### credit 是 per-VC 还是 per-port

两种管理方式：

```
Per-VC credit（最常见）：
  每个 VC 独立 credit counter
  优点：精确，VC 之间互不干扰
  缺点：某个 VC 空闲时 credit 不能借给其他 VC

Per-port shared credit pool（共享池）：
  同一 output port 的所有 VC 共享 credit 池
  优点：buffer 利用率高（忙的 VC 可以多用）
  缺点：实现复杂，一个 VC 可能耗尽整个 pool 导致其他 VC 饿死

第一版 simulator 建议用 per-VC credit，简单且行为可预测。
```

## 三：Allocator Policy

Allocator policy 决定了 SA（Switch Allocation）仲裁时"谁先通过"。这不只影响公平性——它直接影响吞吐、尾延迟和 forward progress（前进保证）。

### 四种常见策略详解

#### Fixed priority（固定优先级）

```
规则：每个 VC 或 input port 有固定的优先级编号，高优先级始终先获得服务

  优先级：VC0（control）> VC1（response）> VC2（request）> VC3（stream）

  场景：VC2 和 VC0 同时竞争 East port
  → VC0 永远赢，VC2 永远等

优点：实现最简单（纯组合逻辑），关键流量延迟最低
缺点：低优先级可能永远得不到服务（starvation）
适用：control 流量极少且必须低延迟，data 流量对延迟不敏感
```

#### Round-robin（轮询）

```
规则：维护一个指针，每次服务后指针移到下一个候选者
  下次从指针位置开始，找到第一个有请求的候选者服务

  周期 1: 指针在 VC0 → VC0 有请求 → 服务 VC0 → 指针移到 VC1
  周期 2: 指针在 VC1 → VC1 无请求，VC2 有 → 服务 VC2 → 指针移到 VC3
  周期 3: 指针在 VC3 → VC3 有请求 → 服务 VC3 → 指针移到 VC0

优点：绝对公平，无 starvation
缺点：不区分优先级，control 小消息和 bulk data 同等对待
适用：流量类型相近、不需要差异化服务的场景
```

#### Weighted round-robin（加权轮询）

```
规则：每个候选者有权重，权重高的在一轮中获得更多次服务

  权重：VC0 = 1, VC1 = 2, VC2 = 4
  一轮周期分配：VC0 服务 1 次，VC1 服务 2 次，VC2 服务 4 次

  效果：VC2（如 bulk data）获得约 57% 带宽
        VC1（如 response）获得约 29% 带宽
        VC0（如 control）获得约 14% 带宽
        但每类流量都保证能得到服务

优点：可控的带宽分配，无 starvation
缺点：权重设定需要了解 workload 特征，配错了反而有害
适用：不同 traffic class 带宽需求差异大但都不能饿死的场景
```

#### Age-based（基于等待时间）

```
规则：每个 flit（或 packet）有一个 age 计数器，每等待一个周期 age+1
      SA 仲裁时选 age 最大的（等得最久的优先）

  周期 T:
    VC0 的 flit 等了 2 周期（age=2）
    VC1 的 flit 等了 5 周期（age=5）
    VC2 的 flit 等了 1 周期（age=1）
    → 服务 VC1（age 最大）

优点：天然防 starvation（等久了一定会被优先服务）
缺点：需要维护 age 计数器，面积和逻辑开销略高
适用：需要保证 worst-case latency bound 的场景
```

### 四种策略的对比

| 策略 | 公平性 | starvation 风险 | control 延迟 | 实现复杂度 | 适用场景 |
|------|--------|----------------|-------------|-----------|---------|
| Fixed priority | 无公平性 | 高（低优先级可能饿死） | 最低（如果 control 是最高优先级） | 最简单 | control 极少、data 不敏感 |
| Round-robin | 绝对公平 | 无 | 中等 | 简单 | 流量类型相近 |
| Weighted RR | 可控公平 | 无 | 可调 | 中等 | traffic class 差异大 |
| Age-based | 自适应公平 | 无 | 中等偏低 | 较高 | 需要 worst-case 保证 |

**第一版 simulator 建议从 round-robin 开始**——行为最可预测，baseline 数据最干净。之后加 fixed priority 或 weighted RR 做对比实验。

## 三者如何耦合

### 场景 1：buffer 够深 + round-robin → 公平但 control 被堵

```
配置：VC 深度 8，round-robin 仲裁，3 个 VC（request/response/control）

现象：
  link 利用率 85%（不错）
  bulk data throughput 很好
  但 barrier / descriptor 延迟的 P99 非常差

原因：
  round-robin 对 control 和 data 一视同仁
  当 data VC 有大量 flit 排队时，control 每 3 个周期才获得 1 次服务
  control flit 本身很少但对延迟极敏感 → P99 被拖长

修复：
  方案 A：control 用 fixed priority（control VC 始终最优先）
  方案 B：weighted RR，给 control VC 较高权重
  → 对 data throughput 影响很小（control 流量本身就少），但 control P99 大幅改善
```

### 场景 2：buffer 太浅 + 再好的 allocator 也没用

```
配置：VC 深度 2，credit round-trip R=3，任意 allocator

现象：
  link 利用率上限 67%（buffer < R）
  所有 VC 频繁 credit stall
  allocator 大部分周期找不到可发的 flit（全部 credit=0）

原因：
  buffer 太浅导致 credit 来不及回来
  allocator 无论怎么选，都面对"所有候选者都没 credit"的局面

修复：
  必须先加深 buffer 到 ≥ R
  allocator 调优要在 buffer 足够的前提下才有意义
```

### 场景 3：buffer 够深 + fixed priority → starvation

```
配置：VC 深度 8，fixed priority（response > request > stream）

现象：
  response 延迟极好
  但 stream（tile-to-tile activation）在高流量时几乎停滞
  → 部分 tile 拿不到 activation → compute stall

原因：
  response 和 request 流量持续占用 SA
  stream 优先级最低，只有其他 VC 都空时才能通过
  在高负载下 stream 近乎饿死

修复：
  方案 A：改用 weighted RR，保证 stream 最低带宽份额
  方案 B：给 stream 独立的物理 link（不经过 SA 竞争）
```

### 耦合关系总结

```
buffer depth 决定：能不能发（credit 够不够）
  → 如果 buffer < R，allocator 怎么调都没用，link 利用率被硬性限制

allocator policy 决定：谁先发（在有 credit 的候选者之间选择）
  → 如果所有 VC 都有 credit，allocator 是唯一的竞争仲裁者
  → 如果只有一个 VC 有 credit，allocator 没什么可选的

credit round-trip 决定：buffer 的最低深度要求
  → R 越大，buffer 必须越深，面积成本越高
  → 长链路（跨 cluster）的 R 远大于短链路 → 需要不同的 buffer 配置
```

## 第一版 simulator 参数扫描建议

| 参数 | 推荐扫描值 | 观察什么 |
|------|-----------|---------|
| buffer depth | 2 / 4 / 8 / 16 | link 利用率在哪个深度开始饱和（不再随深度增加而提升） |
| allocator policy | round-robin / fixed-priority / age-based | throughput 差异和 starvation 现象 |
| long-link pipeline latency | 0 / 1 / 2 额外周期 | 长链路对 buffer 需求的放大效应 |
| control/response priority | on / off | 开启优先级后 control P99 改善多少、data throughput 下降多少 |

### 参数扫描的正确方法

```
错误做法：同时改 buffer depth 和 allocator policy
  → 无法区分效果来源

正确做法：固定其他参数，只变一个
  实验 1：固定 round-robin，扫 buffer depth → 找到吞吐拐点
  实验 2：固定 buffer depth = 拐点值，扫 allocator policy → 看公平性差异
  实验 3：固定最优的 depth + policy，扫 long-link latency → 看跨 cluster 影响
```

## 最值得看的指标

| 指标 | 看什么 | 异常意味着什么 |
|------|--------|--------------|
| link utilization | 各 link 传输 flit 的周期占比 | 远低于 100% 且 CREDIT_STALL 高 → buffer 太浅 |
| average latency | packet 从注入到送达的平均周期数 | 高 → 整体拥塞或路径太长 |
| tail latency（P99/P99.9） | 延迟分布的高百分位 | P99 远大于 P50 → 某些路径或消息类型受到不公平对待 |
| CREDIT_STALL cycles | 各 VC 因 credit=0 停发的周期数 | 高 → buffer 太浅或下游消费太慢 |
| SWITCH_CONFLICT cycles | 各 VC 因 SA 竞争失败的周期数 | 高 → 热点或流量汇聚，可能需要分散 routing |
| per-VC throughput | 每个 VC 实际传输量占总量的比例 | 某 VC 占比极低 → 可能被饿死（starvation） |
| workload completion time | 整个 workload 从开始到所有 tile 计算完成的总时间 | 这是最终目标指标，其他指标是诊断手段 |

## 快速诊断流程

```
workload 比预期慢
  │
  ├─ link utilization 低 + CREDIT_STALL 高
  │   → buffer 太浅或 credit round-trip 太长
  │   → 优先加深 buffer
  │
  ├─ link utilization 高 + SWITCH_CONFLICT 高
  │   → 热点或流量汇聚
  │   → 优先调整 routing 或 placement 分散流量
  │
  ├─ link utilization 中等 + 某类 VC throughput 极低
  │   → allocator starvation
  │   → 优先调整 allocator policy 或增加该类流量的权重
  │
  └─ link utilization 低 + CREDIT_STALL 低 + SWITCH_CONFLICT 低
      → 瓶颈不在 NoC 内部
      → 检查端点：destination ejection stall、SRAM bank conflict、DMA 排队
```

## 常见误区

| 误区 | 实际情况 |
|------|---------|
| buffer 越深越好 | 超过 R+2 后收益递减，但面积持续增长；且深 buffer 会拖长拥塞恢复时间 |
| allocator 只影响公平不影响吞吐 | 不公平的 allocator 会让关键路径（如 response）饿死，导致 protocol deadlock 或 compute stall，系统吞吐骤降 |
| credit 只是实现细节不影响架构结论 | credit round-trip 直接决定 buffer 最低深度，间接决定面积预算；在长链路场景下是主要设计约束 |
| 所有 router 用同一套参数 | cluster 内短链路和 cluster 间长链路的 R 不同，应该配不同的 buffer 深度 |

## 本页结论

buffer depth、credit sizing 和 allocator policy 不是三个孤立参数，而是决定 NoC"能不能稳住吞吐、能不能保护关键路径"的一组耦合旋钮。  
调优顺序是：**先用 buffer depth 保证 link 不空转（≥ R），再用 allocator policy 解决公平性和优先级，最后针对长链路单独增大 buffer。**
