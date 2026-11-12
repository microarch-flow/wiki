# Router Pipeline Pseudocode

上级：[08 Simulator Construction](./README.md)

相关：[Core Data Structures](./core-data-structures.md)、[Verification And Calibration](./verification-and-calibration.md)、[Router Pipeline Stages](../02-router-microarchitecture/router-pipeline-stages.md)

## 目标与时间契约

这里给出一种明确的教学实现。它支持单播、一个周期内完成 RC/VA/SA/ST、每个输出每拍最多发送一个 flit。模型输入是 router、link、endpoint 状态及 workload；输出是提交后的状态和事件。其他流水线结构可行，但必须重新计算验证表。

## 时间与快照契约

`S(t)` 是拍 `t` 开头的已提交状态。所有 router 和 endpoint 从同一份 `S(t)` 读取；候选和仲裁结果在本拍内部计算；成功动作写入 `next`，最后统一提交。到期 flit、credit、注入 flit 也在拍末写入 `next`，本拍不能参与路由和仲裁。禁止按 router 遍历顺序把刚写入的队列用于另一个 router。

发送发生在 `t` 时，`forward_latency=L≥1` 的 flit 在 `t+L` 拍末进入下游 FIFO，最早在 `t+L+1` 前进。输入槽在 `t` 释放时，`return_latency=R≥1` 的 credit 在 `t+R` 拍末加入上游计数，最早在 `t+R+1` 使用。消费 ejection FIFO 和本地输出都读取 `S(t)`；本拍刚消费腾出的空间，下一拍才能用于弹出。这些边界是本模型的定义，不是所有硬件的规定。

RC、VA、SA 可在一次候选计算中完成，且分配的 output VC 可供该候选当拍使用。对同一个 output VC，分配器在 `S(t)` 的许可和本拍候选中保证互斥。已成功分配但未赢得 SA 的包保留该许可。信用和 free 消息到期后本拍末才生效。

## 单拍流程

```text
tick(t):
  current = S(t); next = copy(current)
  # 每个 endpoint 从 current 取至多 consumer_rate 个已在队列中的 flit
  plan_consumer_drain(current, next)
  # 每个非空 input VC 只考察队首；空 VC 不计 stall
  candidates = route_and_allocate(current, next)
  eligible, blocked = check_resources(candidates, current)
  grants, losers = arbitrate(eligible)  # 每 input/output 的硬件限制显式检查
  for candidate in grants:
    commit_move(candidate, current, next, t)
  for blocked or losers:
    record_one_primary_stall_per_head_per_tick(reason)
  plan_injection(current, next, t)
  stage_due_link_arrivals_and_credits(current, next, t)
  validate_capacity_and_invariants(next)
  S(t+1) = next
```

每个非空队首每拍至多记录一个主因；可用固定优先级，例如 `ROUTE_BLOCKED → VC_ALLOC_FAIL → EJECTION_BLOCKED/NO_CREDIT → LINK_BLOCKED → SWITCH_CONFLICT`。多因诊断可以另存 bitset，但不能把同一个 flit 的一个 stall 周期重复累加。计数范围是 flit-router-cycle；endpoint 注入失败另记，避免与 router 计数混用。

## 先检查，再提交

```text
check_resources(candidate, current):
  s, f = input_context_and_head(candidate)
  if no_valid_route_or_context: return BLOCKED(ROUTE_BLOCKED)
  if output == LOCAL:
    if current.ejection_fifo.full: return BLOCKED(EJECTION_BLOCKED)
    return ELIGIBLE                       # 无下游 VC / 跨路 credit
  if f is HEADER or HEAD_TAIL:
    if not candidate.owns_output_vc and not allocation_granted_to_candidate:
      return BLOCKED(VC_ALLOC_FAIL)       # busy 属于本包时可继续
  else:
    assert candidate.owns_output_vc      # BODY/TAIL 沿用本包已持有的绑定
  if current.output_credit[output][vc] == 0: return BLOCKED(NO_CREDIT)
  if link_cannot_accept: return BLOCKED(LINK_BLOCKED)
  return ELIGIBLE

commit_move(candidate, current, next, t):
  f = pop(next.input_fifo)                # 仅被授权的成功动作进入这里
  if output == LOCAL:
    next.ejection_fifo.push(f)
    if f is TAIL or HEAD_TAIL: record network_arrival_cycle = t
    # 不访问 link，不扣跨路 credit，不增加 hop
  else:
    next.output_credit[output][vc] -= 1
    outgoing = copy(f)                     # 独立事件载荷，不修改快照对象
    outgoing.assigned_vc = vc
    outgoing.hop_count += 1
    schedule_forward(link, outgoing, vc, t + forward_latency)
  schedule_slot_credit_to_input_upstream(t + return_latency,
                                         free=(f is TAIL or HEAD_TAIL))
  if f is TAIL or HEAD_TAIL:
    clear_local_input_context(next)       # 不提前清下游 VC 分配许可
```

跨路发送前构造独立的 flit 事件载荷，先更新下游 VC 和 hop，再排入 link。即使事件队列按值复制，接收端也能看到更新后的 hop；排队后再改局部对象并不可靠。

目的端 `LOCAL` 只检查 ejection FIFO 和 switch 资源。失败时 flit 仍在原 FIFO，不产生 slot credit/free，不释放上下文，不计 hop。成功后才释放输入槽，向该输入槽的**上游**返回 credit；这是本 router 的输入信用，不是向不存在的本地 link 扣 credit。源 router 的 LOCAL 输入由 endpoint 信用接口承接同样的返回规则。

## 注入与 VC 生命周期

```text
inject(ep, current, next, t):
  pkt = current.current_packet or select_ready_packet(current)
  if no pkt: return
  if no pinned_vc_for(pkt):
    reserve_one_free_injection_vc_for_packet_and_pin(pkt)
    if none available: record_one_endpoint_stall(INJECTION_BLOCKED); return
  assert injection_permission_owned_by(pkt)  # busy 但归当前包，不阻止后续 flit
  if current.injection_credit[pinned_vc] == 0:
    record_one_endpoint_stall(INJECTION_BLOCKED); return
  f = next_flit(pkt)
  enqueue_for_next_snapshot(source_router.input_vc[pinned_vc], f)
  next.injection_credit[pinned_vc] -= 1
  if f is first: pkt.injection_cycle = t
  if f is last: clear_current_packet_handle_after_success()
```

同一 packet 的每个 flit 固定使用已选注入 VC。源接口的 VC 许可也采用严格策略：源 router 的尾 flit 成功离开后，free 信号返回并提交，后包才可获得许可。若当前包选中时还无法获得许可，可以等到许可可用再固定；不能逐 flit 重选。workload 未满足依赖不进入 ready 注入队列，另以 workload 对象记 `WAITING_FOR_DEPENDENCY`，不计 router 的 `ROUTE_BLOCKED`。

跨路 output VC 的本地 holder 可以在尾 flit 离开本 router 时解除，但指向下游 VC 的分配许可要保持 busy。下游真正移出该尾 flit时，返回 slot credit 并携带 free；该消息提交后才允许新包分配。目的 LOCAL 没有下游 output VC，只有本地 input 上下文。严格策略与可证明 FIFO 复用的取舍见 [核心状态](./core-data-structures.md#三种独立状态)。

## Backpressure 如何逐跳传播

consumer 停止后，ejection FIFO 先满。目的 router 的队首因此无法移出，其输入 slot 不再释放。上游消耗完现有 credit 后才停止发送；它的输入 FIFO 随后可能填满，再阻塞更上游。实际传播时间取决于在途 flit、现有空槽、仲裁和正反向延迟，不能只用 buffer 深度估计一个固定拍差。流量不足时反压可能永远到不了源端。

实现 trace 应记录每个 slot 消耗与返回、free 信号、成功转发、弹出、消费和单一主阻塞原因。[逐拍验证表](./verification-and-calibration.md) 使用同一快照口径。

## Trace 示例

例如场景 1 的 T 在拍 9 弹出时，可记录一行：

```text
t=9 event=eject packet=P flit=T router=R3 input=W:0 output=LOCAL hop=3 upstream_credit_due=10 free=1
```

该记录必须能与同拍 input pop、ejection push 及下一拍末的 credit/free 到达对应。LOCAL 没有发送链路字段。可另记录拍初候选、主 stall、拍末 credit 与 VC 许可；字段含义和采样边界须固定。
