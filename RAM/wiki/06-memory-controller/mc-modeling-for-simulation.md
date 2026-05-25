# MC 在 cycle-level 仿真里的建模方法

上级：[Memory Controller](./README.md)
相关：[多 master 场景下的 QoS 与公平性](./qos-multi-master-arbitration.md), [存储器在架构探索中的建模模板](../10-reference/memory-modeling-template.md)

## 这页在回答什么问题

如果目标是做 cycle-level 或 event-driven 仿真，memory controller 到底该保留哪些状态和事件，哪些细节可以折叠掉。更具体地说，怎样才能把前面整章讲过的 row/bank/timing/refresh/QoS 这些约束，压缩成一个既有解释力、又不会过度复杂的仿真模型。

## 正文

到了这一章最后，最容易犯的错误有两个。一个错误是把前面所有机制都原封不动搬进模型——就像画一张地图时把每棵树、每块砖都标上去，结果地图比真实城市还复杂，没人能用。另一个错误则相反：为了简化，直接把 controller 压成一个 `avg_latency + peak_bw` 黑盒——就像把整座城市画成一个点，你确实能在全国地图上找到它，但你永远无法用它导航，于是前面所有 row locality、bank conflict、refresh 插空、write drain、QoS 差异都消失了。真正有用的建模方法，通常介于这两者之间：保留那些会改变性能形状的显式状态，折叠那些不改变决策结构的电路细节。

判断“哪些必须保留”的最稳标准，不是看它在真实硬件里是否存在，而是看它是否会改变 controller 的选择空间。沿着这个标准，至少有五类东西通常必须显式建模。第一类是 `bank/open-row state`，因为没有它就没有 row hit/miss/conflict，也没有 FR-FCFS 和 page policy 的意义。第二类是 `timing guards`，因为 controller 之所以不能任意发命令，就是被这些 guard 限制。第三类是 `request queues and command issue logic`，因为调度的本质就是在多个候选请求间做选择。第四类是 `refresh/write-drain/QoS mode state`，因为这些机制会改变命令发射顺序和资源可见性。第五类是 `address mapping policy`，因为它决定请求流被塑形成怎样的 bank/channel 几何。

与之相对，有些细节通常可以折叠。比如单个 sense amp 的模拟放大波形、位线连续电压变化、具体电源噪声耦合、训练电路内部实现，这些对绝大多数架构探索并不会改变 controller 的离散决策结构。你可以把它们压成若干 timing guard 或能耗参数，而不必显式仿真电压演化。换句话说，MC 模型的目标不是把 DRAM 芯片”仿真得像示波器波形一样真”，而是把”什么时候能发哪条命令、发了之后谁会等、总线何时被占、哪些请求会被拖长尾”这类系统行为做对。好的 MC 模型就像一张好的城市交通地图：你不需要画出每栋楼的砖缝，但主干道、红绿灯、单行线和收费站必须标清楚，因为它们决定了你能不能顺利从 A 到 B。

一个比较稳的最小状态集合，可以写成下面这样：

```text
McState {
  now: cycle

  req_queue[master]: queue<MemReq>
  write_buffer: queue<MemReq>

  bank_state[channel][bank] {
    open_row: row_id | INVALID
    mode: enum { IDLE, ACTIVATING, ACTIVE, PRECHARGING, REFRESHING }
    ready_cycle: cycle
    last_act_cycle: cycle
    last_pre_cycle: cycle
  }

  shared_state[channel] {
    cmd_bus_ready_cycle: cycle
    data_bus_ready_cycle: cycle
    bus_direction: enum { READ, WRITE, TURNAROUND }
  }

  refresh_state[scope] {
    next_due_cycle: cycle
    postpone_budget: int
  }

  policy_state {
    scheduler_mode
    page_policy_mode
    write_drain_mode
  }
}
```

这套状态看起来已经不少，但它们基本都和“controller 下一拍能不能做什么选择”直接相关。反过来，如果某个状态删掉后，策略空间并没有变，只是数值精度稍粗，那么它通常就是可以折叠的候选。

在 event-driven 视角下，controller 的主循环通常也不复杂，核心就是四步：

```text
1. 接收新请求并入队
2. 根据地址映射更新请求的 channel/bank/row/col 解释
3. 根据 bank/timing/refresh 状态筛出当前 legal 的候选命令
4. 根据调度/QoS/page policy 选择下一条命令发射
```

可以把它写成一个很简化的伪码：

```text
while simulation_running:
  collect_arrivals(now)
  update_completed_events(now)
  candidates = build_legal_cmds(now, state)
  cmd = select_cmd(candidates, policy_state)
  if cmd exists:
      issue(cmd, state)
  now = next_event_or_next_cycle()
```

这里真正决定模型解释力的，不是 `while` 循环本身，而是 `build_legal_cmds` 和 `select_cmd` 里保留了哪些状态依赖。只要这两块做对，模型就能自然长出 row-hit 优先、refresh 插入、write drain 和 QoS 抢占这些行为。

如果目标只是做吞吐趋势比较，而不是逐条请求延迟分析，那么模型可以再简化一层。例如你可以不显式发 `ACT/RD/PRE` 三条命令，而直接把请求分类成 `ROW_HIT / ROW_MISS / ROW_CONFLICT` 三类成本，再叠加 refresh blocking 和 bus turnaround penalty。这种模型依然能保留 DRAM 最关键的非均匀性，却比全命令级更轻：

```text
if bank.open_row == target_row:
    service_cost = row_hit_cost
elif bank.open_row == INVALID:
    service_cost = row_miss_cost
else:
    service_cost = row_conflict_cost
```

再加上：

```text
if refresh_blocks(bank_or_rank):
    service_cost += refresh_penalty

if bus_direction_changes(req):
    service_cost += turnaround_penalty
```

这类“折叠后的半结构模型”在很多 design-space exploration 里很实用，因为它保留了决定性的不均匀成本来源，又不至于把命令级细节全部拉进来。

但有些场景下，你就不能再这么折。只要你的目标涉及下面几类问题，controller 模型最好显式到命令/状态级：

- 比较不同 page policy 或 FR-FCFS 变体
- 研究 refresh postpone / bank-level refresh 的尾延迟影响
- 看多 master QoS、公平性和 starvation
- 分析读写混合流量中的 write drain 行为
- 用 archax 这类框架评估 deterministic NPU 外存可预测性

因为这些问题的答案，正是来自 controller 在离散状态边界上如何做选择，而不是来自一个平均延迟数字。

如果要和更高层系统建模对接，一个很有效的方式是把 memory controller 显式放进 `Resource / Topology / Interaction / Capability` 这四个轴里。这里可以第一次用这套抽象，因为到本章已经进入系统级建模边界：

- `Resource`：channel、bank、data bus、refresh budget、write buffer
- `Topology`：master 到 channel 的连接关系，channel 到 rank/bank 的层次
- `Interaction`：读请求、写请求、refresh 命令、turnaround、precharge/activate 序列
- `Capability`：峰值带宽、可并行 bank 数、QoS 保底能力、可推迟 refresh 的窗口

这套映射的价值在于，它能把“controller 不只是一个算法，而是一个受资源和拓扑约束的调度器”这件事表达清楚。

最后还要强调一个很现实的建模原则：不要试图让模型一开始就同时精准回答带宽、平均延迟、p99 延迟、功耗、热和公平性全部问题。更稳妥的做法是先选清目标，再决定需要保留哪些 controller 结构。如果只关心吞吐上界，命令级 QoS 细节可以先弱化；如果关心 SLA 和实时性，refresh/QoS/page policy 必须保留；如果关心系统架构路线选型，则地址映射与 bank 并行形状往往比某个精确 tCL 数值更重要。模型应该服务问题，而不是反过来为了“细”而细。

所以，这一页真正要建立的不是某一种唯一正确的 MC 模型，而是一套裁剪准则：凡是会改变命令可发性、请求重排结果或资源共享形状的状态，都应该显式保留；凡是只影响底层连续电气细节、却不改变策略空间的部分，通常可以折叠。按这个原则，你就能在不同精度目标下得到一族合理的 controller 模型，而不是一个要么太粗、要么太重的极端。

## 一句话理解

MC 建模的关键，不是把所有 DRAM 细节都搬进仿真，而是显式保留那些会改变命令可发性、调度选择和资源共享形状的状态，把其余连续电气细节折叠成 timing 和能耗参数。

## 建模启示

如果要直接落成可实现的仿真骨架，一个很实用的最小接口是：

```text
struct MemReq {
  addr: uint64
  is_write: bool
  bytes: int
  source: MasterId
  arrival_cycle: cycle
  mapped_channel: int
  mapped_bank: int
  mapped_row: row_id
  mapped_col: col_id
}

struct McObservedMetrics {
  avg_latency: float
  p99_latency: float
  row_hit_rate: float
  bank_utilization[bank]
  bus_utilization[channel]
  refresh_block_cycles: cycle
  write_drain_cycles: cycle
}
```

一个最小事件集合可以是：

```text
event ReqArrive(req)
event CmdIssue(cmd, bank)
event DataBurstStart(req)
event DataBurstDone(req)
event RefreshStart(scope)
event RefreshDone(scope)
event TurnaroundStart(dir)
event TurnaroundDone(dir)
```

如果你要在 archax 里做 deterministic NPU 外存建模，我建议至少保留：

- `address_mapping_policy`
- `bank_state/open_row`
- `refresh scope + postpone budget`
- `write_drain mode`
- `per-master QoS priority / max wait`

因为这五类状态基本已经决定了“外存是否可预测”这件事。反过来，若你只是做 very-early-stage route screening，可以把命令流折叠成 `row_hit / miss / conflict + refresh/turnaround penalty` 模型，先跑趋势，再决定是否需要更细。
