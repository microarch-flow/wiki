# Verification And Calibration

上级：[08 Simulator Construction](./README.md)

相关：[Core Data Structures](./core-data-structures.md)、[Router Pipeline Pseudocode](./router-pipeline-pseudocode.md)、[Stall Taxonomy And Attribution](../07-evaluation-methodology/stall-taxonomy-and-attribution.md)、[Case Card Template](../07-evaluation-methodology/case-card-template.md)

## 这页在回答什么问题

这页回答两件事：

1. 第一版 NoC simulator 怎样**验证"基础规则没写错"**——给出可逐拍对照的 expected state
2. 怎样把结果**校到至少不会明显离谱**——分层校准的判据

字段名沿用 [Core Data Structures](./core-data-structures.md)；阶段顺序沿用 [Router Pipeline Pseudocode](./router-pipeline-pseudocode.md)。

## verification 和 calibration 不是一回事

先要区分：

- `verification`：实现是否符合你定义的模型语义（不变量是否成立、逐拍状态是否吻合手算）
- `calibration`：模型参数和趋势是否与更高保真参考或常识一致

第一版最优先的是 verification。没有规则正确性，calibration 没意义。

## 不变量永远在线检查

下面 8 条在 [Core Data Structures](./core-data-structures.md#跨结构不变量) 已经定义，这里只列名字——它们应该被实现成 `debug_assert`，每个 tick 末尾扫一遍：

| # | 不变量 | 触发后大概率的 bug |
|---|--------|--------------------|
| 1 | Credit 守恒 | `move_flit` 与 `schedule_credit_return` 时序错位 |
| 2 | Wormhole 互斥 | `release_path_state` 与 `run_vc_allocator` 双缓冲没做 |
| 3 | VC holder 一致 | VA 写 `output_vc_busy` 但忘了写 `output_vc_holder` |
| 4 | Wormhole 同路径 | body/tail 错走了别的 output port |
| 5 | TAIL 释放 | `release_path_state` 漏调用或断言失败 |
| 6 | Credit 不超发 | 同周期既扣减又使用 |
| 7 | In-flight 闭合 | 死锁 / 漏统计 |
| 8 | Packet 状态单调 | scheduler 状态机回退 |

verification 模式下任何一条断言失败都应**立刻打印当前 tick 的全 router 状态快照**，而不是仅抛异常。下面的最小场景就是为了把这些断言推到边界。

## 最小场景对照表的读法

每个场景给出：

- **拓扑/参数**：最小可复现的配置
- **初始状态**：tick 0 开头的关键字段
- **逐拍 expected state**：每拍结束时哪些字段是什么值
- **期望的 stall reason**：每拍主导的 StallReason
- **通过判据**：最终统计字段的期望值

只要某一拍偏离 expected state，就停下来对 router-pipeline-pseudocode 里对应的阶段。

约定缩写：`oc[p][v]` = `output_credit[port=p][vc=v]`；`q(ip,iv)` = `input_vcs[ip][iv].queue.size()`；`busy[p][v]` = `output_vc_busy[p][v]`。

---

## 场景 1：单 packet / 三跳延迟

最简单的健全性测试。

**配置**：
- 拓扑：4 个 router 直线 `R0—R1—R2—R3`，每段 link `forward_latency=1, return_latency=1`
- 每 VC `buffer_depth=4`，`num_vcs=1`
- packet：1 HEADER + 1 BODY + 1 TAIL（共 3 flit），`src=N0, dst=N3`
- 路由：DOR（这里就是一路向东）
- router 流水线：单拍（RC+VA+SA+ST 同拍完成）

**期望 per-hop latency**：每跳 `1 (router) + 1 (link forward) = 2 cycles`，三跳共 6 cycles，再加注入拆 1 flit 1 拍、ejection 1 拍 ≈ 8 cycles 完成。

**逐拍 expected state**（只列关键字段）：

| 拍 | 事件 | R0 q(L,0) | R0 oc[E][0] | R1 q(W,0) | R2 q(W,0) | R3 q(W,0) | R3 ejection | flit.last_stall |
|----|------|-----------|-------------|-----------|-----------|-----------|-------------|-----------------|
| 0 | 注入 HEADER | 1 | 4 | 0 | 0 | 0 | 0 | NONE |
| 1 | HEADER 进 link / 注入 BODY | 1 | 3 | 0 | 0 | 0 | 0 | NONE |
| 2 | HEADER 到 R1 / 注入 TAIL | 1 | 2 | 1 | 0 | 0 | 0 | NONE |
| 3 | HEADER 出 R1 进 link / BODY 出 R0 | 0 | 1→2* | 0→1 | 0 | 0 | 0 | NONE |
| 4 | HEADER 到 R2 / BODY 到 R1 / TAIL 出 R0 | 0 | 3 | 1 | 1 | 0 | 0 | NONE |
| 5 | HEADER 进 R3 link / BODY 出 R1 / TAIL 到 R1 | 0 | 4 | 1 | 0→1 | 0 | 0 | NONE |
| 6 | HEADER 到 R3 / BODY 到 R2 / TAIL 出 R1 | 0 | 4 | 0 | 1 | 1 | 0 | NONE |
| 7 | HEADER 进 ejection / BODY 进 R3 link / TAIL 进 R2 link | 0 | 4 | 0 | 0 | 1 | 1 | NONE |
| 8 | BODY 进 ejection / TAIL 到 R3 → ejection / packet COMPLETED | 0 | 4 | 0 | 0 | 0 | 3 | NONE |

*第 3 拍 R0.oc[E][0] 由 1（HEADER 扣完）+ 1（HEADER 释放 R1 input buffer slot 后回传，return_latency=1，下一拍到达）= 2。手算时要把 credit return pipe 当成显式的一拍延迟。

**通过判据**：
- `completion_cycle - injection_cycle == 6`（首 flit 注入 → tail ejection）
- `stall_cycles[*] == 0`
- `hop_count == 3`（HEADER）
- `flits_in_flight == 0` after tick 8
- 8 条跨结构不变量全程不触发

**最常见失败**：
- per-hop 多了 1 拍 → 八成是 `enter_current_router_cycle` 没加 `forward_latency_cycles`
- credit return 提前 1 拍 → `schedule_credit_return` 写到了 `current_state` 而不是 `next_state`

---

## 场景 2：buffer 满后 source 停发

考验 credit 反压。

**配置**：
- 同场景 1 拓扑，但 R3 的 consumer 全程不取（`consumer_rate=0`）
- packet：10 个 flit 一个 packet（HEADER + 8 BODY + TAIL）
- `buffer_depth=4`，`num_vcs=1`

**期望**：前若干 flit 一路灌满 R1/R2/R3 的 input buffer，credit 链断裂，source 端 endpoint 触发 `INJECTION_BLOCKED`。

**逐拍 expected state**（节选关键拍）：

| 拍 | R3 q(W,0) | R2 oc[E][0] | R2 q(W,0) | R1 oc[E][0] | R0 oc[E][0] | R0 q(L,0) 头 flit stall | ep.injection_credit |
|----|-----------|-------------|-----------|-------------|-------------|------------------------|---------------------|
| 0 | 0 | 4 | 0 | 4 | 4 | NONE | 4 |
| ... |  |  |  |  |  |  |  |
| k₁ | 4 | 0 | 0 | 4 | 4 | NONE | 4 |
| k₁+1 | 4 | 0 | 1 | 3 | 4 | NONE | 4 |
| k₂ | 4 | 0 | 4 | 0 | 4 | NONE | 4 |
| k₂+1 | 4 | 0 | 4 | 0 | 1 | NONE | 3 |
| k₃ | 4 | 0 | 4 | 0 | 0 | NO_CREDIT | 0 |
| k₃+1 | 4 | 0 | 4 | 0 | 0 | NO_CREDIT | 0 |

**通过判据**：
- 进入稳态后 `R0/R1/R2/R3 oc[E][0] == 0`，所有这些 router 的西向 input VC 满（`queue.size() == 4`）
- 源端 endpoint 的 `injection_queue` 卡住，`stall_cycles[INJECTION_BLOCKED]` 单调增长
- `stall_cycles[NO_CREDIT]` 在 R0 上单调增长
- 不变量 1（credit 守恒）始终成立：`Σ oc + Σ in-flight + Σ in-buffer + Σ return-pipe == buffer_depth`，可在任意拍快照验证

**最常见失败**：
- 反压链有断点 → 某中间 router 的 oc 一直 >0：八成是 ejection 满时还在回 credit
- 不死锁但吞吐异常 → credit 守恒不成立：八成是 `move_flit` 多扣或少扣

---

## 场景 3：tail 释放后后续 packet 才能复用路径

考验 wormhole 互斥和 `release_path_state` 的时序。

**配置**：
- 同场景 1 拓扑，1 VC
- packet A：3 flit，`src=N0, dst=N3`，注入时间 cycle 0
- packet B：3 flit，`src=N0, dst=N3`，注入时间 cycle 0（紧跟 A 后面）

**期望**：A 的 HEADER 占用 R0 的 East output VC 后，B 的 HEADER 在源端 endpoint 排队，**必须等到 A 的 TAIL 离开 R0 那拍之后**，B 才能 VA 抢到同一 output VC。

**关键拍 expected state**：

| 拍 | R0 input_vcs[L][0].active_packet | R0 busy[E][0] | R0 holder[E][0] | endpoint.current_injection_packet | B HEADER 位置 |
|----|----------------------------------|---------------|-----------------|-----------------------------------|---------------|
| 0 | A | true（VA 完成后） | (L,0) | A | 在 injection_queue 里 |
| 1 | A | true | (L,0) | A | 同上 |
| 2 | A（注入 TAIL）| true | (L,0) | A | 同上 |
| 3 | A | true | (L,0) | A（最后一拍）| 同上 |
| 4 | A（TAIL 离开 R0）| true→false | (L,0)→(-1,-1) | B（切换）| 即将注入 |
| 5 | B | false→true | (-1,-1)→(L,0) | B | R0 input buffer L,0 |
| 6 | B | true | (L,0) | B | 推进中 |

**关键断言**（第 4→5 拍交界）：
- 第 4 拍**之内** TAIL 走、`release_path_state` 把 `busy[E][0]=false`、`holder=(-1,-1)`
- 第 5 拍**之内** B 的 HEADER 才能进入 VA 并把 `busy[E][0]=true`
- 如果 B 的 HEADER 在第 4 拍就 VA 成功 → wormhole 互斥被破坏（不变量 2 应触发断言）

**通过判据**：
- A 完成 → B 完成的 `injection_cycle` 间距 ≥ A 的 `num_flits`
- `wormhole_path_violations == 0`，`tail_release_violations == 0`
- 两个 packet 的 per-hop 路径完全一致

**最常见失败**：
- B 错误抢跑 → 八成是 `release_path_state` 和 `run_vc_allocator` 都在同一 tick 的 current_state 上写，没做双缓冲

---

## 场景 4：两包抢同一输出，仲裁稳定

考验 SA 的公平性与可复现性。

**配置**：
- 4 个 router T 形：`N0—R0—R2—R3` 和 `N1—R1—R2—R3`，R2 是合流点
- 1 VC，`buffer_depth=4`
- packet A：`N0→N3`，3 flit，注入 cycle 0
- packet B：`N1→N3`，3 flit，注入 cycle 0
- 仲裁：round-robin，初始指针 → A

**期望**：A 和 B 的 HEADER 同时到达 R2，都申请 E 端口。第一拍 A grant、B 记 `SWITCH_CONFLICT`；A 走完整个 packet（wormhole 不可抢断），B 才能 grant。

**关键拍**：

| 拍 | R2 head from W (=A) | R2 head from S (=B) | sa_grant A | sa_grant B | B.last_stall |
|----|---------------------|---------------------|------------|------------|--------------|
| k | HEADER | HEADER | true | false | SWITCH_CONFLICT |
| k+1 | BODY | HEADER（仍在 head） | true | false | SWITCH_CONFLICT |
| k+2 | TAIL | HEADER | true | false | SWITCH_CONFLICT |
| k+3 | empty | HEADER | n/a | true | NONE |

**通过判据**：
- `stall_cycles[SWITCH_CONFLICT]` 在 B 上 == 3
- A 的 3 个 flit 连续 3 拍 grant；B 在 A TAIL 走的下一拍才 grant
- 多次跑结果**完全一致**（仲裁器无随机性）
- 不变量 2（wormhole 互斥）始终成立——B 不能插队抢 A 没释放的 output VC

**最常见失败**：
- B 在 A TAIL 同拍就 grant → wormhole 互斥破坏；同场景 3 的根因
- B 在 A TAIL 后第 2 拍才 grant → release 时机晚了 1 拍

---

## 场景 5：ejection blocked 沿路 backpressure

考验完整反压链，把 [Router Pipeline Pseudocode](./router-pipeline-pseudocode.md#backpressure-的完整回传链) 的 8 级传播跑一遍。

**配置**：
- 同场景 1 拓扑
- R3 的 `ejection_depth=2`，`consumer_rate=0`（消费完全停下）
- 持续注入 packet（每个 3 flit）

**期望传播顺序**（用 `t_eject_block, t_input_full, t_credit_zero, ...` 表示每一级首次触发的拍）：

| 级 | 触发条件 | 期望 stall reason | 首次触发拍 |
|----|----------|------------------|------------|
| 1 | R3 的 local_ejection_queue 满 | EJECTION_BLOCKED on R3.local | t₁ |
| 2 | R3.input_vcs[W][0] 头 flit 卡住，buffer 不释放 | （内部，不上报）| t₁ |
| 3 | R3 不向 R2 回 credit，R2.oc[E][0] 减到 0 | NO_CREDIT on R2 | t₁ + buffer_depth |
| 4 | R2.input_vcs[W][0] buffer 满 | （内部）| t₃ + buffer_depth |
| 5 | R1.oc[E][0] 归零 | NO_CREDIT on R1 | 类推 |
| 6 | R0.oc[E][0] 归零 | NO_CREDIT on R0 | 类推 |
| 7 | endpoint.injection_credit 耗尽 | INJECTION_BLOCKED on N0 | 类推 |
| 8 | scheduler 推不进 injection_queue | （workload 侧停滞）| 类推 |

**通过判据**：
- 各级首次触发的相对拍差 ≈ `buffer_depth + forward_latency + return_latency`（每跨一跳堆 1 个 buffer_depth 的空间）
- 稳态下 `stall_cycles_by_class[*][EJECTION_BLOCKED]` 只出现在 R3.local
- `stall_cycles_by_class[*][NO_CREDIT]` 出现在 R0/R1/R2
- `stall_cycles_by_class[*][INJECTION_BLOCKED]` 出现在 endpoint
- consumer 恢复 (`consumer_rate=1`) 后，反压**反向消解**，先 R3 后 R2/R1/R0，最后 endpoint 重新注入

**最常见失败**：
- NO_CREDIT 没有沿路出现，只在 R3 上看到 EJECTION_BLOCKED → credit 链有断点
- consumer 恢复后传播不消解 → `update_local_ejection_state` 与 `accept_returning_credits` 之间有死锁顺序

---

## stall reason 也要被验证

不要只验证"包最终到了"。每一拍主导的 stall reason 必须能落到上面表格里的那一列：

| 现象 | 应该看到的主导 stall reason |
|------|----------------------------|
| 下游 buffer 满 | `NO_CREDIT` |
| 输出争抢 | `SWITCH_CONFLICT` |
| VA 竞争 | `VC_ALLOC_FAIL` |
| 目的端吃不动 | `EJECTION_BLOCKED` |
| 源端注入侧反压 | `INJECTION_BLOCKED` |
| workload 依赖未满足 | `ROUTE_BLOCKED` |
| body/tail 等 HEADER 建路 | `HEADER_NOT_ROUTED` |

如果分类不对，归因会整体失真——后面的 stall taxonomy / case card 看上去都"合理"但实际指向错的瓶颈。

## calibration 应该怎么做

第一版不必追求工艺级绝对数值。更现实的目标：

- 趋势对（注入率上升，latency 应单调上升，throughput 应饱和）
- 拐点对（饱和点应在 `bisection_bw / 单包率` 附近）
- 相对比较不离谱（mesh 8×8 vs torus 8×8 的 bisection 比应接近 2:1）

典型可作为对照的来源：

- 手算带宽 / hop 上界（latency lower bound = `hop * (router_delay + link_latency)`）
- 已知拓扑常识（mesh diameter = `2(N-1)`、torus = `N`）
- 旧模型或更粗的 analytical 模型的趋势
- 小规模 sanity benchmark（uniform random、hotspot、bit-reverse）

## 建议的分层校准方式

可以按 [Modeling Layers](../07-evaluation-methodology/modeling-layers-analytical-event-cycle.md) 校准：

| 对照 | 关注点 | 容忍度 |
|------|--------|--------|
| analytical vs event | throughput / hotspot 方向是否一致 | ±20% |
| event vs flit | phase-level slowdown 方向是否一致 | ±15% |
| flit vs cycle | stall / tail latency 量级是否一致 | ±10% |

差异超出容忍度时，先怀疑实现，再怀疑抽象层次不够。

## 为什么 debug trace 仍然重要

即使有结构化 stats 和不变量断言，第一版 simulator 仍建议支持可选的：

- `flit move trace`：每个 flit 在每拍的 `(router, port, vc, stage)`
- `credit return trace`：每条 credit 的发出拍、到达拍、对应 buffer slot
- `ejection blocked trace`：每次 EJECTION_BLOCKED 的 endpoint / packet / 持续时长
- `vc state trace`：每个 VC 状态机的转移序列

聚合统计不能第一时间发现 timing bug。trace 可以——把上面 5 个场景的 trace 做成 golden trace 存到仓库，回归时直接 diff，比眼睛看快得多。

## 验证资产应该结构化

把验证本身写成数据，而不是一次性脚本：

```text
UnitScenario {
  name
  topology_config
  packet_schedule
  expected_state[cycle] := { (router, field) -> value }
  expected_stall_per_cycle[cycle][node] := StallReason
  trend_checks := { metric -> direction | bound }
  pass_criteria := { metric -> value | range }
}
```

这样验证就能成为 simulator 的**持续约束**，每次改完跑一遍——而不是早期做完一次就丢。

## 一句话理解

第一版 simulator 的验证重点是：**8 条跨结构不变量永远成立、5 个最小场景的逐拍 state 与 stall reason 都可对照、趋势和拐点不会明显错向**。三条都过，才算"规则语义稳定"。

## 建模启示

落地建议：

1. 把 8 条不变量写成 `debug_assert`，verification 模式下每拍扫一遍
2. 把 5 个最小场景的 expected state 表落成 JSON / YAML，跑一次 diff 一次
3. 把 stall reason 分布作为每个 case card 的必填字段——它比平均 latency 更早暴露问题
4. trace 保留可选开关，回归时打开做 golden diff，sweep 时关掉省 IO

不变量 + 最小场景 + trend check 三件套撑起来后，再往复杂 workload 走，模拟器才有底气说"规则没写错"。
