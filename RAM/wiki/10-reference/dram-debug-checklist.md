# DRAM 系统调试 checklist

上级：[参考资料](./README.md)
相关：[为什么说 DRAM 的实际性能由 MC 决定](../06-memory-controller/why-mc-is-the-real-bottleneck.md), [峰值带宽 vs 有效带宽：损失发生在哪里](../07-system-architecture/effective-bandwidth-vs-peak.md)

## 这页在回答什么问题

当 DRAM 系统出现带宽不达标、尾延迟异常或 QoS 失衡时，应该按什么顺序排查访问模式、地址映射、page policy、refresh 和仲裁。

## 正文

这份 checklist 的目标，不是把所有 DRAM 细节都列一遍，而是给你一个不容易走偏的排障顺序。DRAM 系统出问题时，最常见的失败模式不是“完全没有线索”，而是太快跳到错误层级。看到带宽不够，就先怪颗粒不行；看到尾延迟高，就先怪 refresh；看到 QoS 差，就先改优先级。结果真正的问题也许是 row locality 被地址映射毁了，或者写排空把读请求切碎了，或者上游请求形状根本就喂不饱 controller。

这就像身体不舒服就直接吃止痛药——头疼可能是颈椎问题、可能是血压高、也可能只是没睡好，不分清病因就下药，最好的结果也只是暂时不疼。所以更稳的做法，是先把现象归类，再按层往下拆。下面这份顺序就是为这个目的组织的：先问“你看到的到底是哪种症状”，再问“它更像是流量形状问题、mapping 问题、controller 策略问题，还是更高层拓扑问题”。只要这个顺序守住，大多数 DRAM 性能问题都不会一上来就诊错层。

## 1. 先把症状说具体，不要只说“内存慢”

先确认属于哪一类：

- 峰值带宽打不满
- 平均延迟高
- p95 / p99 尾延迟异常
- 某些 master 明显饿死
- 读吞吐正常但写一多就掉速
- 单线程正常，多线程/多 master 才恶化

如果症状本身不具体，后面所有排查都会发散。因为“带宽低”和“尾延迟高”经常来自完全不同的根因。

## 2. 先确认问题在 DRAM path 上，还是更上游/下游已经断流

先回答：

- controller request queue 是否真的长期有请求？
- 无请求时，是 DRAM 忙，还是上游根本没发够？
- 下游是否能及时消费返回数据，还是出现 backpressure？

很多“DRAM 打不满”的问题，根本不是 DRAM 侧约束，而是上游 issue 不稳定、cache miss shaping 太碎、NoC 或 DMA 已经先饿住了。

## 3. 先看请求形状，再看原始峰值

先回答：

- 请求是长 burst 还是小碎包？
- 请求地址是否连续，还是高度随机？
- 读写混合比例如何？
- queue depth 是否足够深？

如果请求本身又碎、又浅、又混杂，DRAM 很难表现得像规格书峰值。这里先不要急着看颗粒标称参数，先看 workload 形状是不是天然就在漏水。

## 4. 先看 row locality，很多问题在这里就已经定性了

先回答：

- row hit / miss / conflict 比例是多少？
- 热点 bank 是否在频繁切 row？
- 某些请求流是否持续打在同一 bank 不同行上？

如果 row conflict 很高，那么性能差的第一嫌疑通常不是颗粒慢，而是访问模式或 mapping 让开行成本无法被摊薄。只要这一点没改，很多别的调优都只是止痛。

## 5. 再看地址映射：是不是它把局部性和并行度都塑坏了

先回答：

- 地址位是如何映射到 channel / rank / bank / row / col 的？
- 当前 workload 更需要 row reuse，还是更需要 bank/channel striping？
- 是否出现 bank hotspot、channel 不平衡、rank 偏载？

映射是最容易被低估的一层，就像城市道路的路口设计——同样的车流量，合理的路口分流能让每条路都通畅，糟糕的路口规划会让所有车挤到一个十字路口。它决定地址流在 DRAM 结构里的几何形状。很多“row locality 差”或“bank 利用率低”的根因，其实是映射早就把流量导歪了。

## 6. 再看 page policy：是不是在用错误的未来假设

先回答：

- 当前 controller 用的是 open-page、close-page 还是 adaptive？
- 当前 workload 是更偏短局部性，还是更偏快速切换？
- 保留 open row 的收益，是否真的大于未来 conflict 成本？

如果 page policy 和 workload 形状明显不匹配，就会出现很典型的现象：不是纯 row hit 低，就是 conflict 高得离谱。这里别把 page policy 当成小调参，它常常直接决定 row hit 分布。

## 7. 再看调度器：吞吐和公平是不是在错误方向上被偏置了

先回答：

- 调度是不是明显偏 `FR-FCFS` 风格？
- 某些流是不是长期被 row-hit-friendly 流量压住？
- 高优先级流是否持续切碎大块 burst？
- 队列里是不是“有请求，但合法候选很少”？

如果平均吞吐还行，但某些请求长尾特别糟，或者某类 master 明显挨饿，调度和 QoS 往往比颗粒本身更值得先看。

## 8. 再看写路径：是不是 write drain 和读写切换在吞时间片

先回答：

- 读写混合负载下，turnaround 开销占比高吗？
- write buffer 是否经常爆满？
- controller 是否在长时间 write drain，导致读请求尾延迟抬高？

这类问题很常见，尤其是在平均吞吐没那么差、但读延迟突然变坏的场景里。很多人会先看 read path，实际上是 write path 在背后制造节拍破碎。

## 9. 再看 refresh：它是总税，还是眼下主要痛点

先回答：

- refresh block cycles 占比多大？
- 尾延迟尖峰是否和 refresh 时间窗对齐？
- 用的是 rank-level 还是 bank-level refresh？
- postpone / pull-in 策略是否在某些相位把债务堆高了？

refresh 确实重要，但它经常被当成万能替罪羊。正确做法不是先假定它有罪，而是先量化它在当前症状里到底占了多少。

## 10. 再看 bank/channel/rank 利用率：是不是总资源不少，但空间分布很差

先回答：

- 各 bank 利用率是否严重不均？
- channel 是否一边很忙、一边很闲？
- rank 切换是否带来额外空洞？

如果资源总量很够，但利用率空间分布极差，那么继续堆资源通常帮助不大，先修分布更有效。

## 11. 多 master / QoS 问题要单独拆，不要和单流性能混在一起

先回答：

- 是谁在抢谁？CPU、DMA、GPU、NPU、IO 哪几类 master 在共享？
- 目标是最大总吞吐，还是某个关键流的 SLA？
- “公平”要求是平均等待公平，还是尾延迟/带宽保底公平？

如果多个 master 的目标函数不同，而 controller 只有单一吞吐导向策略，QoS 问题几乎必然出现。这里不是“优先级没调好”这么简单，而是目标函数可能先天冲突。

## 12. 最后才考虑：是不是规格或路线本身真的不够

先回答：

- 如果把 mapping、page policy、调度、写路径、refresh 形状都看过后，剩余瓶颈是否仍稳定指向总外带宽不足？
- 当前容量、通道数、外存路线是否已经在正确使用下仍不够？

只有走到这一步，才比较有资格说“也许要换更高带宽路线”“也许要加 channel”“也许得从 LPDDR 升到 HBM”。在此之前，很多问题都更像“现有资源没被兑现出来”。

## 如果时间很紧，最少先看哪几项

优先级最高的通常是：

- 请求形状是否太碎
- row hit / miss / conflict 比例
- 地址映射是否造成 hotspot
- page policy 是否明显反着 workload 来
- write drain / refresh 是否在制造尾延迟尖峰

这几项能快速帮你判断问题是“资源不够”，还是“资源用歪了”。

## 最常见的误判

最常见的几类误判是：

- 看到带宽低，就直接怪外存规格
- 看到尾延迟高，就直接怪 refresh
- 看到某类流慢，就只调 QoS，不看 mapping 和 row locality
- 看到 bank 利用率高，就以为系统一定健康，不看是否少数 bank 过热
- 看到 HBM/DDR 峰值高，就默认 controller 和上游一定喂得出来

这几类误判的共同问题是：太快跳到错误层级。

## 一句话理解

DRAM 排障最重要的不是背更多参数，而是按顺序把问题拆成：请求形状、row locality、地址映射、page policy、调度写路径、refresh、拓扑分布，最后才谈是不是规格不够。

## 建模启示

这份 checklist 最适合直接映射成一组观测计数器和分层诊断字段：

```text
DramDebugSnapshot {
  row_hit_rate: float
  row_conflict_rate: float
  bank_utilization: map
  channel_utilization: map
  refresh_block_cycles: int
  turnaround_cycles: int
  write_drain_cycles: int
  no_request_cycles: int
  no_legal_cmd_cycles: int
  per_master_avg_latency: map
  per_master_p99_latency: map
}
```

如果某个模型或硬件观测接口连这些字段都拿不到，那么很多 DRAM 问题最后只能停留在“感觉像是内存慢”，很难真正归因。
