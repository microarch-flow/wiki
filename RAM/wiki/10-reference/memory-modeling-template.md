# 存储器在架构探索中的建模模板

上级：[参考资料](./README.md)
相关：[MC 在 cycle-level 仿真里的建模方法](../06-memory-controller/mc-modeling-for-simulation.md), [把 register、cache、scratchpad、DRAM、HBM 看作一个系统](../07-system-architecture/memory-hierarchy-as-system.md)

## 这页在回答什么问题

如果要把一种存储层建成可用于架构探索的抽象模型，应该至少列出哪些资源、状态、事件、约束和统计量。

## 正文

这一页的目标，是把前面整套 wiki 里分散出现的“建模启示”收成一个统一模板。它不试图告诉你唯一正确的 memory model 长什么样，而是回答一个更实用的问题：`如果你现在要做架构探索，最少该保留哪些对象，模型才不至于把关键矛盾压没`。因为存储器建模最容易走向两个极端。一个极端是过度详细，把模型做成几乎要替代 RTL；另一个极端是过度粗糙，把一整套层次、状态和共享关系压成几个均值参数。前者太重，后者太盲。就像画地图——如果要精确到每棵树，你画不完也读不了；但如果只画一个点代表"某个城市"，你根本无法用它规划路线。好的模型应该像城市交通图：省掉了建筑细节，但保留了道路、交叉口和瓶颈位置。真正有用的模板，应该允许你按问题裁剪，但始终保留那些会改变结论形状的骨架。

前面几章其实已经给出了这套骨架的线索。SRAM 章节提醒你，端口数、banking、作用域和 low-power 状态会直接改写片上资源语义；DRAM 章节提醒你，open-row 状态、timing guard、refresh、write drain 和映射会改变外存行为；系统章节提醒你，层次不是一串容量参数，而是一张由不同资源角色构成的网络；AI 芯片章节提醒你，数据角色、层间链路和时间重叠关系会决定是不是喂得饱阵列。这些线索如果不统一起来，模型很容易在某一层看上去“合理”，但跨层一连就失真。

所以，一个能跨场景复用的 memory model，通常至少要显式回答五类问题：

- `有哪些资源`
- `这些资源当前处于什么状态`
- `系统里会发生哪些事件`
- `什么约束阻止某些动作立刻发生`
- `最后要观测哪些统计量`

这五类对象比具体语法更重要。因为无论你写的是 cycle-level simulator、event-driven model、性能估算器还是设计空间搜索器，真正决定解释力的往往不是语言，而是这五类对象有没有被保留。

如果把前面已经建立过的建模启示压成一个最稳的中性骨架，它通常包含四层：

- `资源对象`
- `连接关系`
- `运行时交互`
- `能力边界`

这里刻意不用更强框架色彩的命名，因为这一页的目标是做通用 memory modeling 模板，而不是绑定到某一种方法论。四层的作用分别是：列出层次里的节点和可争用对象，描述它们如何连接，表达请求/搬运/刷新/读写切换等事件如何发生，以及把每个资源的上界能力和约束窗口参数化。

下面给出一个够通用、也够节制的模板。

## 1. 资源对象：先把系统里真正会被争用的东西列出来

最小层面，资源不该只有“内存层”本身，还应该包括它旁边会改变行为的边界对象。

```text
MemoryResource {
  id: str
  kind: enum {
    regfile,
    cache,
    scratchpad,
    sram_buffer,
    dram_bank,
    dram_channel,
    hbm_stack,
    noc_link,
    dma_engine
  }
  capacity_bytes: int
  read_bw_Bps: float
  write_bw_Bps: float
  startup_latency_ns: float
  bank_count: int
  scope: enum { pe, cluster, chip, package, board, remote }
  low_power_modes: set
}
```

如果你的模型连资源边界都没分清，比如把整颗 NPU 片上所有 SRAM 压成一个统一池，把整组 DRAM 通道压成一个黑盒，那么很多后续现象根本无从产生。

## 2. 连接关系：写清资源如何连接，而不是默认“一切互通”

很多错误模型的问题，不是资源参数不准，而是默认资源之间可以理想直连。真实系统里，连接关系本身就是性能结论的一部分。

```text
MemoryTopologyEdge {
  src: str
  dst: str
  bandwidth_Bps: float
  latency_ns: float
  granularity_bytes: int
  supports_multicast: bool
  arbitration_group: str
}
```

这类边会让模型自然表达出：某层虽然容量足够，但它到消费者之间只有一条窄链路；或者某级共享 SRAM 明明很近，但需要经过一个会和 DMA 抢占的 NoC 入口。

## 3. State：别只记录参数，要记录会改变未来决策的状态

状态和参数的区别是：参数通常固定，状态会随着运行演化，并且改写后续可发动作。真正该保留的状态，标准不是“硬件里有没有”，而是“删掉它会不会改变选择空间”。

一个通用状态骨架可以写成：

```text
MemoryState {
  now: cycle

  resident_data[resource_id]: set<data_block_id>
  bank_busy_until[resource_id][bank_id]: cycle
  port_busy_until[resource_id][port_id]: cycle

  open_row[channel_id][bank_id]: row_id | INVALID
  bank_mode[channel_id][bank_id]: enum { idle, active, precharging, refreshing }

  bus_direction[channel_id]: enum { read, write, turnaround }
  refresh_due[channel_or_rank]: cycle

  queue_depth[resource_id]: int
  low_power_mode[resource_id]: enum { active, retention, sleep, off }
}
```

如果是 NPU 场景，再补几个角色化状态就会很关键：

```text
TileResidence {
  tile_id: int
  location: resource_id
  role: enum { weight, activation, accumulator }
  state: enum { filling, ready, consuming, draining }
}
```

## 4. 运行时交互：把系统里真的会发生的事情写成事件

很多 memory model 之所以过于模糊，是因为“访问”只被写成一个统一动作。更稳的做法，是让重要交互显式出现，即使它们最后会被折叠。

```text
MemoryEvent = enum {
  req_arrive,
  req_issue,
  data_fill_start,
  data_fill_done,
  data_consume_start,
  data_consume_done,
  act,
  rd,
  wr,
  pre,
  refresh_start,
  refresh_done,
  write_drain_start,
  write_drain_end,
  sleep_enter,
  sleep_exit
}
```

如果你的目标很粗，可以把其中一些折叠成更大粒度事件；但在模板层，先把它们分出来会更安全，因为你能清楚知道自己折掉了什么。

## 5. Constraint：用 guard 表达“为什么现在不能做”

架构探索里很多结论并不来自“平均多快”，而来自“什么时候 legal，什么时候不 legal”。所以约束最好显式存在，而不是只折进均值。

```text
ConstraintGuard {
  name: str
  applies_to: event_type
  condition: predicate(state)
}
```

典型 guard 包括：

- SRAM bank / port 冲突
- DRAM `tRCD / tRAS / tRP / tWR / tRFC`
- 读写方向切换窗口
- refresh 占用窗口
- low-power 唤醒窗口
- double buffering 中“下一 tile 尚未 ready”

如果这些 guard 都不在，模型通常只会得到“平均还行”的幻觉，却解释不了 stall 为什么会成片发生。

## 6. 能力边界：把上界能力参数化，但不要只剩它们

能力边界指资源或链路的静态上界，比如峰值带宽、名义延迟、bank 数、并发上限、QoS 保底能力等。它们很重要，但绝不能代替 state 和 interaction。

```text
CapabilityProfile {
  peak_bw_Bps: float
  min_latency_ns: float
  max_concurrent_requests: int
  max_open_banks: int
  refresh_postpone_budget: int
  qos_guarantee: optional<object>
}
```

如果模型里只剩 capability，没有状态和事件，那它更像一张汽车参数表——只告诉你"最高时速 200 km/h"，却说不出在拥挤的城市里你实际能开多快、在哪个路口会被堵住。真正的系统模型需要能回答后者。

## 7. Observation：最后输出什么统计量，决定模型能回答什么问题

很多模型最后只给总吞吐或平均延迟，这通常不够。更稳的做法，是按层收集统计量，让后续能定位问题而不是只看到结果。

```text
MemoryMetrics {
  throughput_Bps: float
  avg_latency_ns: float
  p95_latency_ns: float
  p99_latency_ns: float

  row_hit_rate: float
  bank_utilization: map
  bus_utilization: map

  refill_overlap_success_rate: float
  bank_conflict_cycles: int
  turnaround_cycles: int
  refresh_block_cycles: int
  low_power_wakeup_cycles: int

  per_master_latency: map
  per_data_role_traffic: map
}
```

这些指标不一定都要实现，但如果一个模型连“问题发生在哪一层”都看不出来，通常很难指导设计决策。

## 8. 怎么按问题裁剪精度

最重要的一条经验是：不要从“最细模型”开始，再考虑删什么；而应从“要回答什么问题”开始，再决定哪些对象不能删。

一个实用的裁剪顺序可以是：

1. 只关心路线筛选：
   保留 `capacity / peak_bw / startup_latency / major traffic edges`

2. 关心片上 vs 片外瓶颈：
   再保留 `bank_count / queueing / overlap state / per-edge utilization`

3. 关心 DRAM 调度与 tail latency：
   再保留 `open_row / timing guards / refresh / write drain / QoS`

4. 关心 NPU 可预测性和数据流：
   再保留 `tile residence / role-specific buffers / refill-consume overlap`

也就是说，模板是完整骨架，具体模型则应按问题裁剪。

## 9. 一个最小可复用骨架

如果要把上面内容压成一个最小却仍有解释力的统一接口，可以写成：

```text
MemoryModel {
  resources: list<MemoryResource>
  edges: list<MemoryTopologyEdge>
  state: MemoryState
  capabilities: map<resource_id, CapabilityProfile>
  metrics: MemoryMetrics
}
```

驱动循环可以保持很简单：

```text
while running:
  collect_new_requests()
  update_completed_events()
  build_legal_actions_from_state_and_guards()
  choose_actions_according_to_policy()
  apply_actions()
  update_metrics()
  advance_time()
```

真正决定模型价值的，不是这个循环本身，而是 `legal_actions` 和 `policy` 是不是建立在正确的资源、状态和拓扑之上。

## 最后一个判断标准

如果你不确定一个状态该不该保留，可以用一个很实用的问题判断：

`删掉它之后，系统是否仍会做出同样的调度选择、暴露同样的争用形状、得到同样的瓶颈结论？`

如果答案是否定的，这个状态通常就不能删。这个标准比“真实硬件里有没有这个信号”更适合作为架构探索中的裁剪准则。

## 一句话理解

一个够用的 memory model，至少要把资源、拓扑、状态、事件、约束和统计量这六层骨架立住；细节可以裁剪，但会改变选择空间和瓶颈形状的状态不能被抹平。

## 建模启示

这页本身就是模板，所以最直接的落地方式，是把它变成一次建模前的结构化问卷：

```text
1. 我有哪些 memory-related resources？
2. 它们怎么连接，哪些边会争用？
3. 哪些运行时状态会改变下一步 legal action？
4. 系统里有哪些关键事件必须显式存在？
5. 哪些 guard 决定“现在不能做”？
6. 我要输出哪些指标，才能定位问题发生在哪一层？
```

如果这六问还答不完整，就先不要急着写 simulator。先把骨架立住，模型自然会稳很多。
