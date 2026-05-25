# Cache 和 DRAM 如何协同，miss 之后发生了什么

上级：[系统视角](./README.md)
相关：[Cache 里的 SRAM：tag 阵列与 data 阵列的差异](../03-sram-applications/cache-sram-tag-data-arrays.md), [地址映射：物理地址到 channel、rank、bank、row、col 的拆分艺术](../06-memory-controller/address-mapping-channel-rank-bank-row-col.md)

## 这页在回答什么问题

一次 cache miss 之后，系统内部到底会发生什么。更具体地说，从 miss 被发现、miss 状态被登记、请求被送到 memory controller、DRAM 返回数据、cache refill 或 writeback 完成，中间哪些环节在共同决定平均延迟、尾延迟和并发能力。

## 正文

很多关于内存系统的讨论，都会把“cache miss”当成一个自然边界：命中了就快，miss 了就去 DRAM。这种说法虽然方便，但会把最关键的系统行为全都压缩掉。真实系统里，miss 不是一个单点跳转，而是一串状态变化。请求并不是在 miss 的那个时刻”瞬移”到 DRAM；它要经过 miss 记录、合并、排队、映射、调度、返回、refill，甚至可能触发 victim line 的 writeback。这就像网购——你点了”下单”并不意味着包裹瞬间出现在你手里，后面还有仓库拣货、打包、分拣、运输、到站、派送一整条链路，每一步都可能排队或延迟。也就是说，miss 之后真正发生的，是 cache 层与 DRAM 层之间一段完整的协同过程。

最前面的动作发生在 cache 自己内部。一次访问 miss，首先意味着 tag 检查确认目标 line 不在本地，或者虽有 line 但状态不允许直接服务。此时 cache 不能只是简单地“发一个外存请求”然后忘掉，因为后续可能还有其他访问打到同一 line。于是很多实现会使用某种 miss status holding register，或等价的 miss tracking 结构，记录“这个 line 的 refill 正在路上”。这一步的价值，是把后续打到同一缺失 line 的请求合并起来，而不是让它们都独立冲向 DRAM。常见误解是认为 miss 数量就等于外存事务数量；实际上，miss 合并做得好坏，本身就是系统行为的重要分界点。就像办公室的打印任务——如果 10 个人分别提交了打印同一份文件的请求，聪明的打印队列只会实际打印一份然后复印分发，而不是重复打印 10 次。

下一步，请求才真正越过 cache 层边界，进入下层互连与 memory controller。这里开始，cache 看到的“一个 cache line 地址”会被翻译成更细的 DRAM 结构坐标：channel、rank、bank、row、column。于是原本只是一个 miss 的请求，会突然拥有行局部性、bank 冲突、QoS 优先级、refresh 碰撞和总线方向切换这些全新命运。也就是说，cache miss 到了 DRAM 世界，不再只是“慢一点的数据取回”，而是在参与一套完全不同的调度规则。

这一步有一个特别重要的认识：cache line 粒度和 DRAM burst / row 结构之间的关系，会直接影响 miss 惩罚。若 cache line 大小、内存 burst 粒度与地址映射配合得好，一次 refill 可以较自然地落在少量连续列访问上；若配合得差，甚至可能触发额外事务拼接或效率损失。也就是说，cache 不是独立于 DRAM 设计的，它的 refill 粒度其实已经在暗中和 DRAM 协议粒度耦合。

一个简化的 miss 路径可以写成：

```text
Load miss
  -> tag miss detected
  -> allocate miss status entry
  -> send line request downstream
  -> MC maps addr to channel/bank/row/col
  -> DRAM command sequence executes
  -> burst data returns
  -> line refill into cache
  -> waiting core/requesters wake up
```

如果这是一个 clean miss，路径可能到这里为止；但很多现实系统还要再叠一层：若 cache 需要为新 line 腾位置，而 victim line 是 dirty，则 miss 处理可能伴随 writeback。于是路径变成：

```text
miss + dirty victim
  -> maybe issue writeback of old line
  -> issue refill of new line
  -> serialize or overlap depending on implementation
```

这就说明了一点：一次 miss 的代价不只是”去外面读回来”，还可能包含”先把里面脏的送出去”。这就像酒店入住——如果房间满了，新客人要等的不只是”分配房间”的时间，还可能包括前一位客人退房、清洁打扫的时间。如果 writeback 不能很好隐藏或合并，尾延迟会明显恶化。

从平均性能角度看，cache 和 DRAM 协同最重要的一个作用，是把许多原本会直接打到 DRAM 的小粒度访问，汇聚成更少、更块状、更可调度的外存事务。cache 命中把访问截住；cache miss 则把需求放大成 line granularity。对 DRAM 来说，这通常是有利的，因为 line refill 更接近 burst 友好的事务形状。于是 cache 不只是降低访问次数，也在替 DRAM 塑形请求流。常见误解是以为 cache 只通过“命中率”影响外存；更准确地说，它同时在影响外存看到的请求粒度、顺序和并发形态。

但 cache 也可能把问题变复杂。比如多个 core 或多个 miss stream 同时触发大量 line refill，下游 controller 看到的就会是一串密集的 line-sized 读请求；若这些请求地址分布很差，row conflict 和 bank hotspot 依然会出现。再比如 write-back cache 在流量激烈变化时，可能把 demand read 和 dirty writeback 混在一起，放大写读切换压力。因此，cache 不是“天然把一切都整理好”的上游模块，而是一个可能改善、也可能重塑下游压力分布的中间层。

这也是为什么 `hit-under-miss`、`miss-under-miss` 能力会直接决定系统感觉“卡不卡”。若 cache 可以在一个 miss 尚未返回时继续服务其他命中，甚至继续跟踪多个并行 miss，那么前台 stall 会被明显削弱；若 cache 结构太保守，一个 miss 就把整个层级锁住，那么即使 DRAM 带宽本身不错，系统也会显得迟钝。换句话说，miss 之后发生了什么，不只是 DRAM 侧的问题，cache 自己的并发缺失承受能力也同样关键。

多级 cache 场景下，这条路径还会继续分层。L1 miss 不一定直接去 DRAM，可能先去 L2/L3；每一级都可能 hit、miss、merge、writeback。于是从核心角度看，“一次 miss”其实常常是一路沿层次树向下传播，直到某一级终于命中或真正打到主存。这个传播过程本身会决定端到端延迟分布：某些请求只在 L2 miss、很快被 LLC 命中；某些请求则一路穿透到 MC；还有些请求在 LLC 也 miss，并与其他 core 的流量互相干扰。也就是说，cache-DRAM coordination 从来不是单层边界，而是一条跨多层层次的接力。

从系统调优角度看，这条链里最常见的几个破口通常是：

- miss 合并能力不足，导致同一 line 重复下发
- refill / writeback 粒度与下游 burst 粒度不匹配
- writeback 与 demand read 相撞，放大 write drain 压力
- cache 允许的并行 miss 数太少，导致前台容易被一两个慢 miss 拖死
- 地址映射让大量 refill 集中撞到少数 bank/channel

这说明“miss penalty”不是一个单常数，而是由 cache 设计、controller 设计和 DRAM 结构共同生成的。

如果把这页的结论压回系统层，就是这样一句话：cache 和 DRAM 不是各干各的，cache 一方面在过滤外存请求，另一方面也在塑形外存请求；DRAM 则一方面在为 cache miss 兜底，另一方面也会通过自己的调度与冲突规律反过来决定 cache miss 最终看起来有多痛。真正的系统行为，正是这两个层次之间来回耦合的结果。

## 一句话理解

一次 cache miss 不是“去 DRAM 读一下”这么简单，而是一次跨 cache tracking、controller 调度、DRAM 命令执行、refill/writeback 协同的完整事务链。

## 建模启示

在模型里，cache miss 不应直接映射成一个固定的 `main_memory_latency`。更合理的做法是把 miss 建成一类带状态的事务，至少显式保留：`miss merge / outstanding miss slots / refill latency / dirty writeback interaction` 这几项。否则模型会严重低估多流 miss 和写回流量对外存的再塑形作用。

一个最小可用的抽象草图可以写成：

```text
CacheMissModel {
  line_bytes: int
  max_outstanding_misses: int
  merge_same_line_miss: bool
  writeback_required_on_dirty_evict: bool
}
```

配合事件流：

```text
event CacheMissDetect(req_id, line_addr)
event MissEntryAllocate(line_addr)
event RefillRequestSend(line_addr)
event RefillDataReturn(line_addr)
event CacheRefillCommit(line_addr)
event DirtyVictimWriteback(victim_line_addr)
```

如果只关心平均 miss penalty，可以把下游 controller/DRAM 延迟折成一个经验分布；但只要你要分析多线程争用、MLP、tail latency 或 cache line 粒度对外存压力的影响，`max_outstanding_misses` 和 `merge_same_line_miss` 这类字段就必须显式存在。因为很多“内存慢”的感觉，实际上是 miss 并发管理在放大或缩小 DRAM 的真实代价。
