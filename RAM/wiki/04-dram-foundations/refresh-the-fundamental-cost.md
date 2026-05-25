# 刷新：DRAM 的原罪和它的代价

上级：[DRAM 基础](./README.md)
相关：[1T1C cell，一颗电容为什么改变了一切](./1t1c-cell-destructive-read.md), [Refresh 调度：分散刷新、推迟刷新、bank-level refresh](../06-memory-controller/refresh-management-distributed-postponed.md)

## 这页在回答什么问题

refresh 为什么不是 DRAM 的一个附属特性，而是从 1T1C cell 物理出发不可回避的系统成本。更具体地说，为什么“电容会漏电”这件事最后会一路演化成带宽损失、功耗峰值、尾延迟抖动和 memory controller 调度问题。

## 正文

如果说 1T1C cell 把 DRAM 推上了高密度路线，那么 refresh 就是这条路线永远摆脱不掉的代价。很多资料把 refresh 讲成一句很轻的定义：“DRAM 每隔一段时间要重写一次数据”。这句话当然正确，但它会掩盖真正重要的东西。refresh 不是维护质量更好的可选动作，也不是某个边角条件下才会触发的后台任务；它是 DRAM 为了让电容存储这件事成立，不得不持续支付的基本税。想象你在沙滩上写了一排字——海浪不断涌来冲刷，你必须不停地重新描画才能保住信息。这不是"偶尔维护"，而是"不描就没了"。DRAM 的 refresh 就是这个不停描画的过程。

物理原因并不复杂。DRAM cell 用一颗极小电容存储电荷，而电荷不会永久留在电容里。无论通过结漏电流、亚阈值泄漏还是其他寄生路径，电荷都会逐渐衰减。只要电荷衰减到 sense amp 无法可靠区分“原来是 0 还是 1”的程度，数据就等于丢了。于是系统必须在这之前，把 cell 的内容重新感测并写回。常见的 `64 ms` retention 窗口，讲的就是在 worst-case 工艺、电压、温度角下，必须在这个时间量级内把所有行至少 refresh 一遍。这里的关键不是具体数字，而是“所有 cell 都背着倒计时”这一事实。

这也是为什么 refresh 是 DRAM 的原罪，而不是普通开销。一次正常读写请求，至少还能说是为了服务上层真正的数据访问；refresh 则完全不是为应用本身产生的新信息，它做的只是避免已有信息自然消失。也就是说，refresh 消耗的时间、能量和阵列可用性，本质上都不是“创造性能”的投入，而是“维持存储介质不崩”的保底成本。你如果从系统角度看，这类开销天然最令人头疼，因为它不可取消、不可忽略、只能尽量管理。

refresh 的第一层代价是可用带宽损失。当某个 rank、bank 或更大范围正在 refresh 时，其中一部分正常访问会被阻塞，因为同一套 sense amp、位线、阵列控制路径正在为 refresh 服务，而不能同时接收普通请求。你可以把它理解成：本来可用于服务 workload 的阵列时间片，被强制拿去做”维持生命”活动了。就像一家餐厅每隔一段时间就必须关门消毒——消毒时间不能接客，但不消毒餐厅就得被关停。refresh 就是 DRAM 的”强制消毒时间”：不做就会丢数据，做了就会占掉原本可以服务请求的窗口。早期容量较小、带宽要求较低时，这件事还比较容易被掩在平均统计里；随着 DRAM 容量变大，受控行数增加，refresh 本身占掉的服务窗口会越来越难忽略。在更大容量器件上，`tRFC` 这类刷新占用时间常常显著增长，这也是为什么现代系统越来越在意 refresh 对有效带宽的侵蚀。

第二层代价是尾延迟和抖动。即使平均带宽损失不是压倒性的，refresh 对单次请求的影响也可能非常尖锐。一个请求如果恰好撞上正在进行的 refresh，它看到的延迟不是“平滑增加一点”，而往往是突然多等一整段不可服务窗口。这意味着 refresh 对实时性、QoS 和 tail latency 极不友好。常见误解是把 refresh 看成对所有请求”平均摊薄”的小成本；实际上，它在请求级别上经常表现为明显的 blocking event，而不是均匀背景噪声。这就像高速公路上的收费站——平均来看，全天通行量只减少了几个百分点；但如果你恰好在拥堵时段到达收费站前，等待时间可能比正常行驶多出好几倍。refresh 对单个请求的伤害，远比统计平均值显示的更剧烈。

第三层代价是功耗与热。refresh 本质上是在周期性激活并恢复一批 cell，这会带来额外动态功耗，而且这种功耗并不总是与应用访问高度重合。对移动场景来说，refresh 是待机功耗的重要来源之一；对高容量、高温系统来说，refresh 甚至会和温度形成正反馈压力，因为温度升高往往会进一步恶化 retention，需要更保守的刷新策略。也正因为如此，LPDDR 场景会特别强调 self-refresh、partial-array self-refresh 这类机制，用来降低“不需要全部阵列一直全额保活”的代价。

refresh 的第四层代价是它把 memory controller 拉进来了。只要 refresh 会占用阵列资源，控制器就不能把它当成完全不可见的底噪，而必须决定“什么时候刷、刷多大范围、是否可以往后拖一点、能否避开最忙时段、是否只锁住部分 bank”。这一步，refresh 就从物理层问题升级成了调度问题。也就是说，refresh 不仅影响阵列，还改变了 controller 的自由度。你后面看到的 distributed refresh、postponed refresh、fine-grained refresh、bank-level refresh，本质上都不是在发明新功能，而是在努力让这笔不可取消的税收缴得更不打断正常业务。

一个简化的刷新时序可以这样理解：

```text
Cycle        0        1 ... k           k+1
Req Queue    normal requests arrive ------------>
Refresh      due ----- issue REF ----- complete
Bank/Rank    idle? --- blocked ------------ free
Service      stop normal accesses ---- resume
```

如果再把请求级现象展开一点，会更直观：

```text
Case A: request arrives before refresh window
  req -> served -> refresh later

Case B: request arrives during refresh window
  req -> wait(refresh completes) -> served

Case C: controller postpones refresh briefly
  req burst -> served first -> refresh forced later
```

这三种 case 说明了一个重要事实：refresh 的代价不仅取决于它自身多长，还取决于它与请求流形状怎样相撞。对 bursty workload，controller 也许能通过适度推迟刷新把局部吞吐做得更好；对持续高压负载，刷新则迟早会回来，而且还可能与最不希望被打断的时段重叠。也就是说，refresh 不是单纯的“每隔固定周期扣掉一点时间”，而是一个会和访问模式相互作用的事件源。

这里还要澄清一个常见误解：refresh 不等于“把整个 DRAM 一口气重新写一遍”。真实实现会按行、按 bank、按 rank、按时间片去组织，以避免把所有可服务性一次性打空。也正因为如此，refresh 才有“怎么切、怎么摊、怎么推迟”的优化空间。但这种优化空间并不改变其本质：被 refresh 覆盖到的那部分阵列，终究还是得在 deadline 之前完成恢复。优化只是让损失分布更可控，而不是让损失消失。

从系统演化角度看，refresh 的麻烦还在于它会随着容量和温度条件变得更顽固。密度上升意味着要维护的 cell 更多；堆叠和高带宽封装则可能把热分布做得更复杂；大模型时代的内存压力又让你更不愿意把任何一个服务窗口白白让给 refresh。于是一个从 cell 物理出发的“低层约束”，最终被推成了平台级的性能和功耗问题。这也解释了为什么 refresh 在现代 DRAM 研究和产品设计里长期是核心议题，而不是某个已经解决的小细节。

所以，本页真正要建立的结论是：refresh 不是 DRAM 的背景噪音，而是它存在方式的一部分。只要 bit 是靠会漏失的电荷保存，refresh 就会持续吃掉时间片、打断请求、消耗能量、压缩调度自由度。后面一切关于 row buffer、controller policy、HBM/LPDDR 取舍、QoS 分析的讨论，只要涉及 DRAM，都绕不过这笔原罪。

## 一句话理解

Refresh 是 DRAM 为了让会漏电的 1T1C 存储还能成立而持续缴纳的系统税，它消耗的不是“额外优化空间”，而是原本可以服务正常请求的时间、能量和调度自由度。

## 建模启示

在 cycle-level 仿真里，refresh 不能简单建模成“每隔固定时间加一个平均延迟”，至少要把它建成会占用资源、会与请求流相撞的显式事件。否则模型可以大致估平均带宽，却解释不了 tail latency、QoS 抖动和 controller policy 的差异。

一个最小可用的状态草图可以是：

```text
RefreshState {
  next_due_cycle: cycle
  postpone_budget: int
  target_scope: enum { BANK, BANK_GROUP, RANK }
  busy_until[target_scope_id]: cycle
}
```

对应事件流可以写成：

```text
event RefreshDue(scope_id)
event RefreshIssue(scope_id)
event RefreshComplete(scope_id)
```

如果只关心非常粗的 SLA 级平均性能，可以把 refresh 折叠成“每个 bank 每 X 周期损失 Y% 服务能力”的简化模型；但只要你关心 worst-case latency、bank-level parallelism 或 controller 调度效果，就必须把 refresh 作为显式 blocking event 保留下来。一个更接近实际控制器的数据结构草图可以是：

```text
DramControllerState {
  req_queue: queue<MemReq>
  refresh_queue: queue<RefreshCmd>
  bank_open_row[bank]: row_id | INVALID
  bank_busy_until[bank]: cycle
  refresh_credit[bank_or_rank]: int
}
```

这里的关键不是字段完整，而是承认 refresh 不是一项固定扣税公式，而是一类带 deadline、带资源占用、带调度策略的事件。
