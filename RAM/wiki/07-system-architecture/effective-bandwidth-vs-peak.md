# 峰值带宽 vs 有效带宽：损失发生在哪里

上级：[系统视角](./README.md)
相关：[为什么说 DRAM 的实际性能由 MC 决定](../06-memory-controller/why-mc-is-the-real-bottleneck.md), [带宽与延迟：为什么不能兼得](./bandwidth-vs-latency-fundamental.md)

## 这页在回答什么问题

为什么规格书上的峰值带宽往往和真实 workload 能拿到的有效带宽差得很远。更具体地说，这个差距不是神秘地“一下子少掉”，而是怎样在 row conflict、读写切换、refresh、队列空洞、映射失配和请求粒度不匹配这些环节里被一层层吃掉的。

## 正文

“峰值带宽打不满”几乎是所有系统性能分析里最常见的一句话，但如果只停在这句抱怨上，几乎没有诊断价值。因为峰值带宽本来就不是“默认能拿到”的现实值，它只是一个在理想条件下成立的上限：总线持续满负荷传输、burst 足够长、方向切换极少、row hit 充分、refresh 不打断、bank/channel 并行被吃满、controller 没有额外约束。真实 workload 只要偏离这些前提中的任何几个，带宽就会开始漏。有效带宽的差距，本质上是一系列局部损失叠加出来的结果。

第一层损失通常发生在 `row conflict`。峰值带宽的理想图景里，你会默认一旦数据总线开始传，就能一拍接一拍地发 burst。可现实是，很多请求并不是恰好命中当前 open row。只要命不中，controller 就要付出 `PRE -> ACT -> RD/WR` 这一整段前置成本，而这段成本期间总线未必能一直高效送数据。于是本来应该用来“发有效载荷”的时间片，先被拿去做行切换。若访问模式在 bank 内频繁跨行，这笔损失会非常可观。也就是说，有效带宽的第一道漏水口，往往不是总线不够宽，而是 row 没开对。

第二层损失来自 `请求粒度与 burst 粒度不匹配`。DRAM 和控制器更喜欢长 burst、大块搬运，因为 activate 成本、列访问启动成本和数据总线占用开销都可以被摊薄。如果 workload 总是小而碎的请求，即使总字节数不少，也会不断重复支付前置开销。你可以把它理解成：峰值带宽假设的是”卡车一直满载跑”，而很多真实流量却是在不停发半空的车。就像快递公司宣称日吞吐量 10 万件，那是假设每辆车都满载的理想情况。如果每辆车只装一个小包裹就出发，实际吞吐可能只有宣称值的零头——车次数很多，但每次都在浪费装载和出发的固定成本。小请求、随机请求和大量分散的 cache miss 往往会在这里掉很多效率。

第三层损失来自 `读写方向切换`。上一章已经讲过，数据总线不是理想双向无限切换资源。若请求流读写混杂，controller 就要在 READ 和 WRITE 模式间切换，并支付 turnaround 时间。峰值带宽模型通常默认方向固定、burst 连续；真实 workload 里，尤其在多 master 混合流量下，方向切换会频繁侵蚀有效传输窗口。写缓冲和 write drain 的存在，正是在努力把这类损失重新组织得更少、更可预测。

第四层损失来自 `refresh`。refresh 不搬应用真正需要的新数据，却会占用阵列与时间窗口。若把峰值带宽比作理想流水线，那么 refresh 就像周期性强制暂停。它可能表现为 rank 级大窗口，也可能在 bank 级上更碎、更局部，但无论形式如何，它都会让某些本可服务普通请求的时间片变成背景维护成本。平均吞吐看，这像是持续漏掉了一部分可服务时间；单请求视角看，它还会制造额外抖动和 tail spike。

第五层损失来自 `bank/channel 并行没有被真正利用`。理论峰值通常默认多个 bank、多个 channel 都能保持较高利用率。但现实中，地址映射也许把热点压在少数 bank 上，某些 master 的请求流也许本身不够宽，或者 queue depth 不够深，导致其他 bank/channel 明明空着却吃不到流量。此时系统看起来”总资源挺多”，但真正忙碌的只有一小部分。就像一个有 20 个收银台的超市，理论结账能力很强，但如果所有顾客都排在 3 号和 5 号收银台，其余 18 个收银台闲着也帮不上忙。换句话说，并行资源是潜在带宽，不是自动到账的带宽。

第六层损失来自 `controller 调度与队列形状`。就算 bank/channel 都足够多，如果控制器看见的请求队列不够深、不够稳定，或者被 QoS / priority / write drain / refresh policy 切成很多不连续片段，也很难把总线一直喂满。峰值带宽隐含了“永远有合适的下一条请求等着发”，而真实队列里常常会出现这种情况：有请求，但都暂时不合法；有合法请求，但不是最有价值的；有高优先级请求，但它阻断了大块连续 burst。于是有效带宽不仅由资源量决定，也由队列的“可服务形状”决定。

第七层损失来自 `上游供数或下游消费节拍不匹配`。这在 GPU/NPU 系统里尤其明显。即使 DRAM 侧一切都很健康，若 cache miss 回填节拍、DMA 提交节拍、NoC 带宽或片上 SRAM 银行组织跟不上，外存也未必能持续收到足够多且合适的请求。换句话说，峰值带宽不是只要 DRAM 自己准备好就能自然兑现，它还要求上游能稳定发请求、下游能稳定接结果。端到端有任何一段断流，总线就会出现空洞。

可以把这些损失串成一条非常实用的“漏水链”：

```text
Peak BW
  -> lost to row conflicts / activate-precharge overhead
  -> lost to small requests / short bursts
  -> lost to read-write turnaround
  -> lost to refresh windows
  -> lost to poor bank/channel balance
  -> lost to queue starvation / policy fragmentation
  -> lost to upstream/downstream mismatch
  = Effective BW
```

这个链条的价值在于，它把“打不满”从情绪词变成了诊断路径。你不能只问“为什么没有达到规格书峰值”，而应该问“这条链里哪几项在吞我的时间片”。同样是只达到 60% 峰值，一种系统可能主要坏在 row conflict，另一种可能主要坏在写读混合导致的 turnaround，再另一种可能其实是 NoC/片上 SRAM 把外存喂不饱。对症下药的方法完全不同。

看一个极简构造案例会更直观。假设一条理论峰值 100 GB/s 的通道，workload 的几个损失项大致如下：

```text
Row conflict / activate overhead   : -15 GB/s
Read-write turnaround              : -10 GB/s
Refresh windows                    : -5  GB/s
Bank imbalance / queue holes       : -20 GB/s
Upstream issue starvation          : -10 GB/s
----------------------------------------------
Observed effective bandwidth       : 40 GB/s
```

这只是构造案例，不代表固定比例，但它很好地说明了为什么“只看峰值 100 GB/s”在工程上几乎没有诊断意义。真正重要的是分解每一项漏损，再决定是该改地址映射、改 page policy、增 queue depth、改 burst 聚合、调整 write drain，还是根本回头看上游是否在正确地产生请求。

这也解释了为什么某些系统升级了更高代 DDR 或更多 HBM stack 后，性能却没按比例提升。外层带宽天花板当然更高了，但如果之前主要卡在 bank hotspot、refresh 干扰、控制流阻塞或片上供数链路，那么新的峰值只是在更高的位置继续漏水。换句话说，扩大水塔高度不会自动修好漏管子。这就像一家餐厅换了更大的厨房，但瓶颈其实在服务员太少——菜出得更快了，但端到餐桌上的速度并没有变，食客体验的等待时间几乎一样。系统级性能优化之所以难，就难在很多问题并不在“总资源不够”，而在“资源兑现形状不对”。

所以，这一页真正要建立的不是“有效带宽低于峰值很正常”这种空话，而是一套更具体的判断：峰值带宽描述的是理想连续有效载荷传输能力；有效带宽描述的是在真实访问模式和控制策略下，所有前置成本、共享冲突与节拍失配扣完之后剩下的那部分。只要这两者区分清楚，后面的系统调优和路线选择才会有真正抓手。

## 一句话理解

峰值带宽是理想条件下总线一直搬有效载荷时的上限；有效带宽则是 row conflict、turnaround、refresh、映射失配和队列空洞等一层层扣完之后，系统真正持续拿到的数据输送能力。

## 建模启示

在模型里，`effective_bw` 不应被当成一个神秘测量结果，而应被分解成若干可归因的损失项。即使你不精确建每一项，也最好至少把损失来源分开统计。否则模型只能告诉你“打不满”，却无法回答“该改哪里”。

一个很实用的观测量集合可以写成：

```text
BandwidthLossBreakdown {
  row_conflict_cycles: cycle
  turnaround_cycles: cycle
  refresh_block_cycles: cycle
  idle_due_to_no_legal_cmd_cycles: cycle
  idle_due_to_no_requests_cycles: cycle
  bank_imbalance_score: float
}
```

然后定义：

```text
effective_bw = useful_bytes_transferred / total_time
peak_bw      = theoretical_interface_limit
efficiency   = effective_bw / peak_bw
```

如果要进一步把问题和系统调优动作关联起来，可以再加一个简化的归因表：

```text
if row_conflict_cycles high -> inspect mapping/page policy/workload locality
if turnaround_cycles high   -> inspect read/write mix and write drain
if refresh_block high       -> inspect refresh policy / density / thermal behavior
if no_requests high         -> inspect upstream producer / NoC / cache miss shaping
```

这种分解虽然粗，但它比单独报告一个“带宽利用率 63%”要有用得多。因为从系统层开始，优化从来不是盯着一个总数，而是找出哪一类损失最先在漏。
