# 路由器逐拍推进：怎样检查并提交动作？

<span id="router-pipeline-pseudocode"></span>

上级：[09 模拟器构建与验证](../SUMMARY.md#08-simulator-construction)；原章节：[08 Simulator Construction](./README.md)

相关：[核心数据结构](./core-data-structures.md)、[路由器流水线](../02-router-microarchitecture/router-pipeline-stages.md)、[最小逐拍仿真实作](./minimal-cycle-simulator.md)

## 目标与时间契约

本页定义一种教学实现：单播，RC、VA、SA 和 switch traversal 可在一个有效拍完成；每个物理输入和输出每拍最多服务一个 flit。其他流水线或 speedup 可以实现，但要另写资源约束和验证表。

## 时间与快照契约

S(t) 是拍 t 开始时的已提交状态。所有 router 和 endpoint 从同一份 S(t) 形成计划；成功动作、到期 flit、credit 和注入在拍末统一提交为 S(t+1)。本拍不能使用新到数据、刚返回的 credit 或刚消费出的 ejection 空位。

发送在拍 t 发生时，正向延迟 L≥1 的 flit 在 **t+L 拍末**进入下游 FIFO，最早在 t+L+1 前进。input slot 在拍 t 释放时，返回延迟 R<sub>return</sub>≥1 的 credit 在 **t+R<sub>return</sub> 拍末**提交，最早下一拍可用。这是本模型的定义，不是所有硬件的固定时序。

## 单拍流程

```text
tick(t):
  current = readonly_snapshot(S(t))
  due = collect_events_due_at_end_of(t)
  consumer_actions = plan_consumer(current)
  candidates, va_grants = route_and_allocate(current)
  eligible, blocked = check_resources(candidates, current, va_grants)
  grants, losers = arbitrate_as_input_output_matching(eligible)
  injection_actions = plan_injection(current)
  changes = combine(consumer_actions, va_grants, grants,
                    injection_actions, due, blocked, losers)
  next = apply_to_independent_state(current, changes)
  validate_capacity_and_invariants(next)
  S(t+1) = next
```

`current` 中的队列、packet 和 flit 不得被计划阶段修改。实现可使用深拷贝、不可变状态或安全的差量提交；只复制外层容器不能保证内部对象独立。同一 credit 在本拍既被消耗又有返还到期时，先依据旧值判断能否发送，再在提交结果中合并两项变化。

VA 可以在本拍授予 output VC，供该候选当拍使用。若授权成功但候选没有赢得 SA，按本模型保留该许可；必须检查同一 output VC 只有一个 owner。switch grant 必须同时满足输入和输出端口能力，不能让同一物理输入的两个 VC 分别赢得两个输出。

## 先检查，再提交

对每个非空 input VC 的队首，先检查合法 route、所需 VC 许可、credit、链路或 ejection 容量，再参与可用资源的仲裁。只有实际获 grant 的动作才能 pop input、扣 credit、安排正向 flit 并释放 slot。LOCAL 成功时进入 ejection FIFO，不扣跨 router credit，也不增加 hop。

LOCAL 失败时，flit 保留在原 input FIFO；不返还该 slot 的 credit、不清本地上下文。对跨路动作，发送前构造独立事件载荷并写入下一跳 VC 和 hop，避免后续修改旧对象。

每个非空队首每拍最多记一个主 stall；例如按 `ROUTE_BLOCKED → VC_ALLOC_FAIL → EJECTION_BLOCKED/NO_CREDIT → LINK_BLOCKED → SWITCH_CONFLICT` 固定顺序分类。只有具备仲裁资格且实际未获 grant 的候选才记 `SWITCH_CONFLICT`。其他可观察条件可以另存，不与主因重复累加。[Stall 分类](../07-evaluation-methodology/stall-taxonomy-and-attribution.md)说明分母。

## 注入与 VC 生命周期

注入控制器只处理已经就绪的 packet。选定本包的注入 VC 后，先检查该 VC 的许可和拍初 credit，再计划写入源 router input；首 flit 成功提交时记录 `injection_cycle`。同一包的 flit 保持绑定，不得逐 flit 换 VC。packet 记录和计数器的更新写入 next，不能通过别名改动 S(t)。

尾 flit 成功离开某个 input VC 时，本地上下文可清除，同时安排向其上游返还 slot credit；严格策略的 free 信息随尾部 credit 返回。下游真正移出尾 flit、free 到期并提交后，上游才可重新分配该下游 VC。workload 尚未满足依赖时不进入 ready 队列，记为依赖等待，不记为 router 的 `ROUTE_BLOCKED`。

## Backpressure 如何逐跳传播

consumer 停止后，ejection FIFO 可能先满；目的 router 无法移出队首，随后上游消耗完可用 credit。若上游继续提供足够数据，等待可能逐跳传播。传播时间取决于初始空槽、在途 flit、反馈延迟和仲裁，不能只由 buffer 深度确定。

## Trace 示例

例如[三跳场景](./verification-and-calibration.md#场景-1三跳三-flit无阻塞)的 tail 在拍 9 弹出时，可以记录：

```text
t=9 event=eject packet=P flit=T router=R3 input=W:0 output=LOCAL hop=3 upstream_credit_due=10 free=1
```

记录应能与同拍 input pop、ejection 入队及随后 credit/free 到达对应。不同实现需要注明其时间和资源边界，不得直接套用本表。
