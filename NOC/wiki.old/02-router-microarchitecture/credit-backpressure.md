# Credit / Backpressure

上级：[Router 微架构](./README.md)

相关：[Packet / Flit / Wormhole](./packet-flit-wormhole.md)、[Buffer Depth / Credit Sizing / Allocator Policy](./buffer-depth-credit-sizing-allocator-policy.md)、[指标与实验设计](../05-modeling-evaluation/metrics-experiments.md)

## 核心问题

上游什么时候可以安全地把 flit（流控单元）发给下游？  
如果下游堵住了，这个压力如何一路传回 producer tile（生产者计算单元）？

## 为什么需要 flow control

router（路由器）的 input buffer（输入缓冲区）是有限的。  
如果发送方不关心接收方是否还有空位，最终一定会发生 buffer overflow（缓冲区溢出），flit 丢失。

所以 flow control（流控）的本质是：**保证 sender 不会发送 receiver 无法接收的 flit。**

## Ready/Valid vs Credit

### Ready/Valid（就绪/有效握手）

工作方式：

- 发送方拉高 `valid` 表示"数据准备好了"
- 接收方拉高 `ready` 表示"我能收"
- 同一个周期 valid 和 ready 都为 1 时，数据传输发生

适合：

- 短距离 pipeline stage（如同一模块内部）
- 本地模块握手

### 为什么 Ready/Valid 不适合多跳 NoC

`ready` 信号必须在同一个周期内从接收方传回发送方才能阻止溢出。当路径变长时这变得不可能：

```
A ──link(1周期)──> B ──link(1周期)──> C

如果 C 的 buffer 满了，ready=0 需要传回 A：
  C.ready=0 → 经 1 周期到 B → B.ready=0 → 经 1 周期到 A
  共 2 个周期，但 A 在这 2 个周期里已经多发了 2 个 flit
  → C 或 B 可能溢出
```

解法一：每一跳插寄存器同步 ready 信号 → 每增加一跳多一周期延迟，时序恶化。  
解法二：改用 credit → 发送方本地查计数器就知道能不能发，不需要等对方的实时信号。

### Credit-based（基于信用的流控）

发送方维护一个 credit counter（信用计数器），表示下游尚可接收的 buffer slot（缓冲槽位）数量。

规则：

- 发送 1 个 flit → credit 减 1
- 下游释放 1 个 slot → 返回 1 个 credit → 发送方 credit 加 1
- credit > 0 时才能发送，credit = 0 时停发

**credit 的优势：把"能不能发"的判断从远端实时信号变成了本地计数器查询，完全解耦了发送方和接收方的时序。**

### Credit 是 per-VC 的

**每个 VC 有独立的 buffer，所以每个 VC 有独立的 credit counter。** 发送方需要分别追踪下游每个 VC 的剩余空间：

```
Router A → Router B 的一条物理 link，B 侧有 3 个 VC

A 维护 3 个独立的 credit counter：
  credit_to_B_VC0 = 4   ← B 的 VC0 有 4 个 slot
  credit_to_B_VC1 = 4   ← B 的 VC1 有 4 个 slot
  credit_to_B_VC2 = 2   ← B 的 VC2 只有 2 个 slot（VC 之间可以不等深）

A 往 B 的 VC1 发 flit → credit_to_B_VC1: 4→3（只影响 VC1 的计数器）
B 的 VC0 释放 slot     → 返回 credit 标注"是 VC0 的" → credit_to_B_VC0: 不变（已经满了就不变）
```

### Credit 返回的物理实现

一个常见的疑问：VC 数量增加是否需要更多的物理导线来传 credit？

**不需要与 VC 数量成正比的额外导线。** 实际设计中 credit 返回通过编码共享一条窄的反向通道：

```
前向通道（A→B，传 flit）：
  数据线：flit_width（如 128-bit）    ← 和 VC 数量无关，所有 VC 共享
  控制线：vc_id + valid              ← 告诉 B 这个 flit 属于哪个 VC

反向通道（B→A，传 credit return）：
  credit_valid : 1-bit               ← "有 credit 返回"
  credit_vc_id : log₂(VC数) bit      ← "是哪个 VC 的 credit"

举例：
  4 个 VC → credit_vc_id 需要 2-bit → 反向通道只有 3 根线
  8 个 VC → credit_vc_id 需要 3-bit → 反向通道只有 4 根线
  → 布线开销是 log₂(N) 级别，几乎可忽略
```

每周期反向通道最多返回一个 VC 的 credit。这通常不是瓶颈——因为每个 output port 每周期最多发走一个 flit（SA 只选一个获胜者），所以 credit 释放也通常是每周期最多一个。

**VC 数量增加真正贵的不是导线，而是 buffer 面积和 SA 复杂度：**

| 开销 | 随 VC 数量的增长 | 说明 |
|------|-----------------|------|
| buffer SRAM | 线性增长 | 每个 VC 要独立的 buffer，这是主要面积开销 |
| SA 仲裁逻辑 | 超线性增长 | local arbitration 输入变多，组合逻辑变复杂 |
| credit counter 寄存器 | 线性增长 | 每个 VC 一个 counter，但每个只有几 bit |
| 物理导线 | 对数增长 | 只需 log₂(N) bit 的 VC 编号 |

### Credit 的初始化与完整流转

credit counter 在系统启动时初始化为**下游 buffer 的深度**（即下游有多少个 slot 可用），不是从 0 开始攒。这保证了一开始就能全速发送。

```
初始状态：
  Router A → Router B，B 的目标 VC 有 4 个 buffer slot
  A 的 credit counter = 4

完整流转（假设 link 延迟 = 1 周期，credit 返回延迟 = 1 周期）：

  周期  A 的动作            credit  B 的状态              credit 返回
  ───  ─────────────────  ──────  ─────────────────────  ──────────
   1   发 flit0            4→3    slot0 被写入
   2   发 flit1            3→2    slot0,1 被占用
   3   发 flit2            2→1    flit0 被下游取走，        B 发回 credit
                                   slot0 释放
   4   发 flit3            1→0    flit1 被取走，slot1 释放  B 发回 credit
                                                           周期3的 credit 到达 A
                                   ─── A 收到 credit ───   credit 0→1
   5   发 flit4            1→0    ……继续流转               周期4的 credit 到达
                                                           credit 0→1
   6   发 flit5            1→0    ……
```

关键观察：credit 到达 A 需要时间（1 周期 link 延迟），所以 A 的 credit 在周期 4 短暂为 0 后才恢复。如果 buffer 深度只有 3，A 在周期 4 就会被卡住 1 个周期——link 空闲，带宽浪费。

## Credit 返回的时机

一条容易搞错的原则：**credit 返回的时机不是"下游收到了 flit"，而是"下游释放了 buffer slot"。**

```
flit 到达 B 的 buffer → 此时 B 不返回 credit（slot 还被占着）
flit 从 B 的 buffer 被取走（穿过 crossbar 去下一跳、或被目的 tile 消费）
  → 此时 slot 空出 → B 返回 credit
```

这意味着：

- credit 防的是 overflow（buffer 溢出）
- credit 不等价于"flit 成功送达最终目的地"
- 如果下游消费慢（比如 tile compute 慢、SRAM bank conflict），slot 迟迟不释放，credit 就迟迟不回来

## Credit Round-trip 与 Buffer 深度的关系

credit round-trip latency（R）= 从 A 发出 flit 到 A 收回对应 credit 的总周期数。

```
R = link_latency(A→B) + consume_latency(B内部处理) + link_latency(B→A)

典型值：R = 1 + 1 + 1 = 3 周期
长链路：R = 2 + 1 + 2 = 5 周期（link 需要插流水级）
```

### buffer 深度 = R 时：恰好满载

```
buffer 深度 = 3，R = 3

  周期1: 发 flit0, credit 3→2
  周期2: 发 flit1, credit 2→1
  周期3: 发 flit2, credit 1→0  ← credit 刚好用完
  周期4: 第一个 credit 返回, credit 0→1, 立即继续发  ← 无气泡

  link 利用率 = 100%（每个周期都在传 flit）
```

### buffer 深度 < R 时：出现气泡

```
buffer 深度 = 2，R = 3

  周期1: 发 flit0, credit 2→1
  周期2: 发 flit1, credit 1→0  ← 用完了
  周期3: 等待……（credit 还没到）  ← 气泡！link 空闲
  周期4: credit 返回, credit 0→1, 继续发

  link 利用率 = 2/3 ≈ 67%，白白丢了 33% 带宽
```

### buffer 深度 > R 时：有余量应对突发

```
buffer 深度 = 5，R = 3

  即使下游短暂变慢（少返回几个 credit），A 仍有余量继续发
  代价：更多的 buffer 面积
```

**结论：buffer 深度 ≥ R 是保持 link 满载的最低要求。** 实际设计通常在 R 的基础上多留 1-2 个 slot 的余量，以应对突发和仲裁竞争。

## Backpressure 是什么

当下游没有空间或不能继续消费时，上游被迫停止发送。这种停止如果继续沿路径反向传播，就是 backpressure（反压）。

### Backpressure 逐跳传播的完整过程

```
4 个节点的路径：Tile0 → R0 → R1 → R2 → Tile3
假设每跳 buffer 深度 = 3

正常时：
  Tile0 ──flit──> R0 ──flit──> R1 ──flit──> R2 ──flit──> Tile3
       <──credit──  <──credit──  <──credit──  <──credit──
  全速流动，无 stall

Tile3 消费变慢（比如 compute 忙、SRAM bank conflict）：

  周期 T   : Tile3 停止取 flit → R2 的 buffer 开始堆积
  周期 T+3 : R2 buffer 满（3 个 slot 全占）→ R2 不再返回 credit 给 R1
  周期 T+6 : R1 对 R2 的 credit=0 → R1 被迫停发 → R1 的 buffer 开始堆积
  周期 T+9 : R1 buffer 满 → R0 的 credit=0 → R0 被迫停发
  周期 T+12: R0 buffer 满 → Tile0 的 credit=0
             → Tile0 无法注入新 flit → producer pipeline stall
             → compute utilization 下降！
```

**backpressure 传播速度 ≈ 每跳 buffer 深度（周期数）。** buffer 越深，backpressure 传到源端越慢（相当于缓冲了更多），但面积成本越高。

### 为什么 AI NoC 特别怕 backpressure

因为它最终不只是通信 stall，而会演化成 compute stall：

```
  destination 消费变慢
    → ejection buffer 堆积
      → 沿途 router buffer 依次填满
        → source injection 停止
          → producer tile pipeline stall
            → compute utilization 下降
              → 整个 workload 被拖慢
```

AI 加速器的 tile pipeline 是高度流水化的，一旦某个 tile 因为 NoC backpressure 停顿，它的 MAC 阵列就在空转——这是最昂贵的浪费。

### 常见 backpressure 来源

| 来源 | 原因 | 典型场景 |
| --- | --- | --- |
| destination ejection FIFO 太浅 | tile 取 flit 的速度跟不上到达速度 | 多个源同时向一个 tile 发数据 |
| HBM（高带宽存储器）response 延迟 | HBM 访问延迟高，response 回来慢 | decode 阶段 KV cache 读取 |
| DMA（直接存储器访问）response 被堵 | DMA 控制器繁忙或排队 | 大量 DMA read request 同时发出 |
| reduce fan-in 过大 | 多个 tile 的 partial sum 同时汇聚到一个目的地 | GEMM 的 reduce 阶段 |
| bulk data 压住 control packet | 大数据包占满 buffer 和 link | data 和 barrier/descriptor 混在同一 VC |
| 下游 compute 消费慢 | tile 上一阶段计算还没结束，无法接收新数据 | pipeline 阶段间不平衡 |

## Credit Stall 与 Switch Stall 的区分

### Credit stall（信用停顿）

```
场景：Router A 的 VC0 有一个 flit 想去 East

  A 检查 credit counter → credit = 0
  → 这个 flit 连参加 SA 竞争的资格都没有
  → 只能等下游释放 buffer 返回 credit
```

根因：下游 buffer 满了。  
持续时间：可能很长（需要等 backpressure 链条解除）。  
优化方向：加深 buffer、加快下游消费、减少流量注入。

### Switch stall（交换停顿）

```
场景：Router A 的 VC0 有一个 flit 想去 East

  A 检查 credit counter → credit > 0，可以参加竞争
  → 参加 SA 仲裁，但另一个 input port 的 flit 也要去 East
  → 仲裁结果：对方赢了，A 的 flit 本周期让路
```

根因：多个流量争同一个 output port。  
持续时间：通常 1-2 个周期（下周期大概率能赢或竞争者走了）。  
优化方向：改善 routing 分散流量、调整仲裁策略、增加 link 带宽。

### 对比总结

| | Credit stall | Switch stall |
|---|---|---|
| 根因 | 下游 buffer 满 | 多流竞争同一端口 |
| 能否参与 SA 仲裁 | 不能 | 能，但没赢 |
| 典型持续时间 | 可能很长（链式阻塞） | 通常 1-2 周期 |
| 诊断信号 | credit counter = 0 | SA grant 失败 |
| 反映的问题 | 流量超过路径承载 或 下游消费慢 | 局部热点 或 流量汇聚 |
| 优化方向 | buffer 深度、消费速度、流量控制 | routing 分散、仲裁策略、link 带宽 |

如果 simulator 显示 credit stall 远多于 switch stall → 问题大概率在下游消费能力或 buffer sizing。  
如果 switch stall 远多于 credit stall → 问题大概率在路由热点或 link 带宽不足。

## 第一版 simulator 至少要统计什么

| 指标 | 看什么 | 异常意味着什么 |
| --- | --- | --- |
| per-link utilization（链路利用率） | 各 link 每周期实际传 flit 的比例 | 某些 link 接近 100% → 热点；大量 link 很低 → 流量分布不均或整体注入不足 |
| per-router input occupancy | 每个 router 的 input buffer 平均占用率 | 持续高占用 → 即将或已经 backpressure；持续低占用 → 该路径流量少 |
| credit stall cycles | 每个 VC 因 credit=0 而停发的周期数 | 多 → 下游消费不够快或 buffer 太浅 |
| switch stall cycles | 每个 VC 因 SA 竞争失败的周期数 | 多 → 局部热点或 link 带宽不足 |
| packet latency 分布 | 从注入到送达的延迟直方图（注意看 P50/P99/P99.9） | 长尾 → 尾部热点或少数路径拥塞严重 |
| source injection stall | 源端 tile 想注入 flit 但 credit=0 的周期数 | 多 → backpressure 已传到源端，compute 可能在 stall |
| destination ejection stall | 目的端 flit 到达但 tile 取不走的周期数 | 多 → tile 消费速度不足，是 backpressure 的根源 |
| tile busy / idle / blocked 比例 | 每个 tile 的时间分解：在计算 / 空闲等数据 / 被阻塞 | blocked 比例高 → NoC 或 memory 是瓶颈，不是 compute |

## 本页结论

credit-based flow control 的本质，是用"下游空位计数"代替长距离实时 ready 信号。  
它能安全防止 overflow，但不能自动保证高吞吐（buffer 太浅则 link 空转），更不能自动避免死锁（那是 VC 和 routing 的职责）。  
AI NoC 中很多看似"算力没打满"的问题，最后会在 credit → backpressure → compute stall 这条链条上找到根源。
