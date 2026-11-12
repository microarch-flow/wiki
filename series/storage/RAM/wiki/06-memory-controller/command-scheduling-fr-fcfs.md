# 命令调度：FR-FCFS 及其变体

上级：[Memory Controller](./README.md)
相关：[Memory controller 如何影响 DRAM 的实际性能](./why-mc-is-the-real-bottleneck.md), [Open、close、adaptive page policy 的权衡](./page-policy-open-close-adaptive.md)

## 这页在回答什么问题

FR-FCFS 如何利用已打开行，以及在什么条件下改变吞吐或请求等待。收益和公平性都取决于候选命令、到达时序与资源约束。

## 就绪命令选择与等待代价

FR-FCFS，即 `First-Ready, First-Come-First-Serve`，利用当前打开行的局部性。若有多个合法候选，优先服务 row-hit 可能避免一部分 PRE/ACT；实际效果取决于其他请求、总线和时序。只有一个候选，或所有候选都命中同一行时，本页规则可能与 FCFS 选择相同命令。

这里的 ready 包括完整的命令合法性。对 PRE，须同时检查 ACT、同 bank 的 RD 和 WR 所形成的下界；参见 [MC PRE 记分板](./mc-modeling-for-simulation.md#同-bank-pre-记分板)。

本文使用一个明确的 FR-FCFS 变体。先根据当前 bank 状态，为每个请求生成下一条必需命令；再过滤掉不满足所有 timing、模式和共享资源 guard 的命令。在剩余合法候选中，优先发目标行已打开的 RD/WR；同类候选按请求到达时间排序。PRE 和 ACT 是非 row-hit 候选，即使它们为某个未来请求做准备，也不能算当前 row-hit。没有合法候选时等待下一事件，之后重新计算。

在相同资源和调度条件下，row hit 通常省去本次请求的 PRE/ACT；多个候选可选时优先服务它可能减少切行并提高吞吐。具体收益取决于流量、数据总线和其他约束，也可能增加其他请求的等待。对有行局部性的 workload，应通过仿真或测量检查吞吐、尾延迟和公平性。

一个条件化例子说明它可能如何减少切行。假设当前时刻不早于周期 12，同一 bank 的 open row 是 `R10`，队列里有三笔请求，且当前 A/C 的 RD 和 B 的 PRE 均合法：

```text
Req A: bank0, row10, col1   arrival=10
Req B: bank0, row22, col8   arrival=8
Req C: bank0, row10, col9   arrival=12
```

若完全按到达顺序，controller 可能会想先做 `Req B`，但这意味着：

```text
PRE(row10) -> ACT(row22) -> RD(B)
```

之后如果还要回到 `Req A/C`，又得再切回 row10。按本页规则先发 A 的 RD；若 A 之后 C 的 RD 在 B 的 PRE 可发之前成为下一条合法命令，则可得到：

```text
RD(A) -> RD(C) -> PRE(row10) -> ACT(row22) -> RD(B)
```

在该时序下，两次 row10 访问共享开行，减少切行。若 C 的 RD 尚不合法，而 B 的 PRE 已合法，调度器可先发 PRE；不能把示意顺序当作所有 timing 配置的必然结果。

持续竞争时，该规则可能增加非 row-hit 请求的等待。是否发生饥饿还取决于合法候选何时出现、资源占用、请求流及是否存在 aging 或服务上限；不能仅凭策略名称断言不公平。

再看一个更尖锐的例子。假设 bank1 当前 open row 是 `R5`，某个流 `S` 连续不断地访问 row5 的不同列；同时另一个流 `T` 偶尔访问 bank1 的 row9。队列可能持续呈现：

```text
S1: bank1 row5
T1: bank1 row9
S2: bank1 row5
S3: bank1 row5
S4: bank1 row5
...
```

假设每次存在发射机会时都有合法 row5 RD 与 T1 的 PRE 竞争，其他时刻 T1 的 PRE 不合法或没有发令机会，并且没有 aging、连续命中上限或其他强制服务机制。此时 row-hit 会反复获选：

```text
RD(S1) -> RD(S2) -> RD(S3) -> RD(S4) -> ...
```

而 `T1` 可能长期等不到 `PRE(row5) -> ACT(row9)` 这一步真正发生。也就是说，FR-FCFS 的吞吐提升，来自把“昂贵切换”尽量推迟；但被推迟的请求恰恰会形成尾延迟长尾。

这就是为什么 FR-FCFS 虽然经典，却很少会在真实系统里原封不动裸跑。很多控制器会在它外面叠加各种“变体保护”：老化机制、服务计数、最大连续 row-hit 数限制、read/write 分级队列、per-thread/per-master fairness cap，或者直接在 QoS 场景里为高优先级流保底。所有这些变体的核心目标都一样：保住 FR-FCFS 对 row locality 的利用，但别让它把某些请求永远饿在门外。

FR-FCFS 的候选还取决于 page policy：close-page 可能减少连续 hit 的机会；open-page 可能保留更多复用，也可能延长冲突请求的等待。实际差异要看访问和命令合法时刻，不能仅由策略名决定。

它还和地址映射高度耦合。若地址映射把相关请求分散到不同 bank，FR-FCFS 也许更容易在多 bank 间交织，既吃 row-hit 又保并行；若映射让某些流集中撞到同一 bank，则 FR-FCFS 会更像“偏爱某一小撮幸运行”的策略。因此，看到 FR-FCFS 表现好或差，不应只评价调度本身，还要问：请求流是怎么被映射成 row/bank 结构的。

从建模角度看，本页变体先过滤合法命令，再按 row-hit 和到达时间排序。它可作为吞吐基线；若目标包括 QoS、实时性或隔离，需要检验等待分布，并在需要时加入明确的服务约束。

可用候选不同、且选择会影响未来切行或排队时，row-hit 优先才可能改变结果。相同候选顺序、单候选或无持续等待压力时，它可以与 FCFS 表现相同。

## 一句话理解

本页 FR-FCFS 变体在合法候选中优先 row-hit，再按到达顺序选择。它可能减少切行，也可能在持续竞争下增加其他请求的等待；两者都要看具体请求流和时序。

## 建模启示

模型先按完整 guard 过滤，再对合法候选按 row-hit 和到达时间排序。not-ready 命令不能发射；row-hit 必须在每次仲裁时依据目标 bank 当前打开行和下一命令重新判断。

一个简化的调度伪码可以写成：

```text
candidates = []  # 每次仲裁重新构造
for req in pending_requests:
    bank = bank_state[req.bank_id]
    cmd = next_required_command(req, bank)
    if cmd is not NONE and all_guards_allow(cmd):
        hit = cmd in {RD, WR} and bank.open_row == req.target_row
        candidates.append({req, cmd, hit})
if candidates is empty:
    wait_until_next_event()
else:
    chosen = min(candidates, key=lambda c: (not c.hit,
                                            c.req.arrival_cycle,
                                            c.req.stable_id))
    issue_if_still_legal_and_update_state_atomically(chosen)
# 下一次仲裁重新生成候选；PRE/ACT 可能改变其他请求的行状态
```

`next_required_command` 对已经发出列命令、仅等待数据或响应的请求返回 `NONE`，防止重复发射。若原子发射时 guard 已被其他同刻动作改变，则不发出旧候选，依据新状态重新仲裁。

若要探索 starvation 缓解，可先过滤合法候选，再使用 aging 作为另一种策略：

```text
priority = row_hit_bonus_if_applicable + age_weight * waiting_cycles
```

一个够用的数据结构草图可以是：

```text
SchedReq {
  stable_id: id
  arrival_cycle: cycle
  bank_id: (channel, rank, bank_group, bank)
  target_row: row_id
  row_hit: bool  # 每次根据当前状态重新计算
  ready: bool    # 当前下一命令是否满足全部 guard
  waiting_cycles: cycle
  source_master: MasterId
}
```

评估 tail latency、QoS 或多 master 场景时，应比较原规则与 aging/fairness 变体。单独设置 aging 权重不自动证明等待上界；还需约束到达、不可抢占占用、刷新和资源服务。
