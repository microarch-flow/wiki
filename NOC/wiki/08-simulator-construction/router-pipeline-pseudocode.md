# Router Pipeline Pseudocode

上级：[08 Simulator Construction](./README.md)

相关：[Router Pipeline Stages](../02-router-microarchitecture/router-pipeline-stages.md)、[Core Data Structures](./core-data-structures.md)、[Verification And Calibration](./verification-and-calibration.md)

## 这页在回答什么问题

这页回答：一个最小但正确的 router tick 应该怎样组织——
- 哪些阶段顺序不能乱
- 每一拍的资源释放时机如何明确
- ejection blocked / injection blocked 这些边界事件如何在伪代码里被显式触发
- backpressure 如何从目的端一路传回源端

字段和不变量沿用 [Core Data Structures](./core-data-structures.md)。每段伪代码里出现的字段（如 `output_credit`、`output_vc_busy`、`active_packet_id`）都在那篇里有明确定义。

## 核心原则

router tick 最容易出错的地方不是算法，而是时序：

- 什么时候读旧状态
- 什么时候更新 route / VC / switch 结果
- credit 何时返回
- tail 何时释放资源
- backpressure 何时形成、何时消解

这几件事只要顺序模糊，结果就会飘。

## 推荐的单 router 逻辑顺序

一个稳定的顺序是：

1. **接收阶段**：吸收上游送来的 flit、吸收下游回传的 credit
2. **本地状态更新**：local ejection queue 是否能腾出空位
3. **路由计算 (RC)**：对每个待路由 HEADER 计算 `next_output_port`
4. **VC 分配 (VA)**：HEADER 申请下游 input VC
5. **Switch 请求 (SA req)**：所有可前进的 head-of-VC flit 发出 SA 请求
6. **Switch 仲裁 (SA)**：决出本拍 grant 集合
7. **Flit 推进 (ST/LT)**：被 grant 的 flit 从 input buffer 进 link
8. **Credit 调度**：被释放的 buffer slot 安排 credit 回传
9. **Tail 释放**：TAIL 离开后清空 input VC 与 output VC 占用

## 为什么这个顺序重要

阶段顺序不是实现风格问题，是模型语义问题。常见的反例：

- 在 flit 真正离开前就返回 credit → 高估吞吐
- tail 太早释放 path → 后包错误抢跑同一 output VC，wormhole 互斥破坏
- ejection 状态未先更新 → 目的端阻塞判断错误，credit 链失真
- credit 回传与本拍 SA 看到同一状态 → 同周期既读又写，出现"鬼速"前进

## 最小 tick 伪代码（骨架）

```text
tick_router(router, now):
  # 1. 接收
  accept_arriving_flits(router, now)
  accept_returning_credits(router, now)

  # 2. 本地状态
  update_local_ejection_state(router, now)

  # 3. RC
  for (ip, iv) in all_input_vcs(router):
    s = router.input_vcs[ip][iv]
    if not s.queue.empty() and head(s).flit_type in {HEADER, HEAD_TAIL} and not s.routed:
      compute_route(router, ip, iv)             # 写 s.output_port, s.routed=true

  # 4. VA
  for (ip, iv) in all_input_vcs(router):
    s = router.input_vcs[ip][iv]
    if s.routed and s.output_vc == -1:
      request_vc_allocation(router, ip, iv)
  run_vc_allocator(router)                       # 写 s.output_vc, output_vc_busy/holder

  # 5. SA 请求
  for (ip, iv) in all_input_vcs(router):
    s = router.input_vcs[ip][iv]
    if can_advance(router, ip, iv, now):
      request_switch(router, ip, iv, s.output_port)
    else:
      record_stall(s, reason_for_blocking(router, ip, iv))

  # 6. SA 仲裁
  run_switch_allocator(router)

  # 7. 推进
  for (ip, iv) where sa_grant[ip][iv]:
    move_flit(router, ip, iv, now)               # 出 input buffer，进 link 或 ejection queue

  # 8. credit 回传
  for each released_slot:
    schedule_credit_return(router, ip, iv, now)  # 进入 Link.return_pipe

  # 9. tail 释放
  for (ip, iv) where moved_flit.flit_type in {TAIL, HEAD_TAIL}:
    release_path_state(router, ip, iv)
```

## can_advance 的精确语义

`can_advance(router, ip, iv, now)` 是 SA 请求的看门。它必须同时满足：

```text
can_advance(router, ip, iv, now):
  s = router.input_vcs[ip][iv]
  if s.queue.empty():                            return false
  f = head(s.queue)

  # head 必须已经被 RC、HEADER 必须已经被 VA
  if f.flit_type in {HEADER, HEAD_TAIL}:
    if not s.routed:        record_stall(s, HEADER_NOT_ROUTED); return false
    if s.output_vc == -1:   record_stall(s, VC_ALLOC_FAIL);    return false
  else:
    # body / tail：复用 VC 必须存在
    if s.output_vc == -1:   record_stall(s, HEADER_NOT_ROUTED); return false

  # 下游 credit 必须 > 0
  if router.output_credit[s.output_port][s.output_vc] == 0:
    s.vc_state = BLOCKED_NO_CREDIT
    record_stall(s, NO_CREDIT); return false

  # 本拍 SA 还没授予过同 output port（双缓冲下由 allocator 决）
  return true
```

注意：`NO_CREDIT` 在这里就被显式归因。stats 里 `stall_cycles[NO_CREDIT]` 的来源**就是这里**，不要散落在别处。

## move_flit 的精确语义

```text
move_flit(router, ip, iv, now):
  s = router.input_vcs[ip][iv]
  f = s.queue.pop_front()

  # 7.1 credit 扣减必须发生在 flit 真正进入下游之前/同拍
  router.output_credit[s.output_port][s.output_vc] -= 1
  assert router.output_credit[s.output_port][s.output_vc] >= 0

  # 7.2 选择目的地：local ejection 还是 link
  if s.output_port == LOCAL_PORT:
    enqueue_to_ejection(router, f, now)
  else:
    link = link_of(router, s.output_port)
    link.forward_pipe[0] = f                     # 进入链路头一拍
    link.utilization_bytes += f.size_bytes

  # 7.3 hop 与统计
  f.hop_count += 1
  f.assigned_vc = s.output_vc                    # 写下游 input VC 编号
  f.enter_current_router_cycle = now + link.forward_latency_cycles

  # 7.4 标记本 input buffer slot 已释放，留给 schedule_credit_return
  mark_slot_released(router, ip, iv)
```

要点：
- `output_credit` 的扣减点决定了 credit-loop 的精度；如果放到 `accept_arriving_flits` 才扣，等价于零延迟传播，会严重高估吞吐
- `f.assigned_vc` 在这里**重写**为下游 VC——下一跳的 `accept_arriving_flits` 直接用它入队

## release_path_state 的精确语义

```text
release_path_state(router, ip, iv):
  s = router.input_vcs[ip][iv]
  p, v = s.output_port, s.output_vc

  # wormhole 互斥的释放：output VC 必须先被这条 input VC 占着
  assert router.output_vc_busy[p][v] == true
  assert router.output_vc_holder[p][v] == (ip, iv)

  router.output_vc_busy[p][v] = false
  router.output_vc_holder[p][v] = (-1, -1)

  s.active_packet_id = 0
  s.routed = false
  s.output_port = -1
  s.output_vc = -1
  s.vc_state = IDLE if s.queue.empty() else ROUTING
```

注意三件事：
1. **顺序**：TAIL 已经被 `move_flit` 推走，**这一拍**释放；后包要等下一拍才能 VA 抢同一 output VC——这道屏障是 wormhole 不交错的保证
2. **断言**：`output_vc_holder == (ip, iv)` 是不变量 4 的最直接的运行时检查
3. **input VC 后续状态**：如果 buffer 里还有下一 packet 的 HEADER（流水排队），状态进入 `ROUTING` 等下一拍 RC；否则回到 `IDLE`

## ejection 不是特殊小事

目的端最容易被简化错的场景：

> flit 到了目的 router，但 `local_ejection_queue.size() == ejection_depth`

正确处理：

```text
update_local_ejection_state(router, now):
  # 由 endpoint 在上一拍 / 本拍开头消费 ejection_queue 的头部
  drained = endpoint_drain(endpoint_of(router), now)
  for _ in range(drained):
    router.local_ejection_queue.pop_front()

enqueue_to_ejection(router, flit, now):
  if router.local_ejection_queue.size() == router.ejection_depth:
    # 本拍 SA 不应给出 grant；如果走到这里说明上游误判，回滚
    rollback_grant_and_record(router, flit, EJECTION_BLOCKED)
    return
  router.local_ejection_queue.push_back(flit)
```

更稳的做法是在 `can_advance` 阶段就提前判断 ejection 满：

```text
can_advance(...):
  ...
  if s.output_port == LOCAL_PORT and ejection_queue_full(router):
    s.vc_state = BLOCKED_NO_CREDIT  # 复用 NO_CREDIT 语义：把 local port 看成一个特殊下游
    record_stall(s, EJECTION_BLOCKED)
    return false
```

要点：
- ejection 满时**保留 flit 在 input buffer，不释放 slot，不回 credit**——backpressure 由此产生
- 同 input VC 上的后续 flit 也被卡住；这条 VC 的 credit 回传链断开，沿路上游一拍一拍堆积
- `EJECTION_BLOCKED` 必须作为独立 stall reason 上报，不要和 `NO_CREDIT` 合并，否则归因会失真

## injection 也应有对称规则

source 端不能因为 packet 被生成就立刻进网。注入伪代码：

```text
tick_endpoint_inject(ep, now):
  # 1. 先 drain workload 调度器，把 ready 的 packet 推进 injection_queue
  for pkt in scheduler.packets_ready_at(now):
    if ep.injection_queue.size() < ep.injection_depth:
      ep.injection_queue.push_back(pkt)
      pkt.state = IN_INJECTION_QUEUE
    else:
      record_injection_stall(ep, INJECTION_BLOCKED)
      break

  # 2. 选当前正在拆 flit 的 packet
  if ep.current_injection_packet == 0:
    if ep.injection_queue.empty(): return
    pkt = ep.injection_queue.front()
    ep.current_injection_packet = pkt.packet_id
    ep.current_injection_flit_seq = 0
    pkt.injection_cycle = now

  # 3. 注入下一个 flit，需要满足：
  pkt = packet_of(ep.current_injection_packet)
  vc_target = pick_injection_vc(pkt.traffic_class)
  if ep.injection_credit[vc_target] == 0:
    record_injection_stall(ep, INJECTION_BLOCKED)
    return
  if not route_precondition_ok(pkt, now):
    record_injection_stall(ep, ROUTE_BLOCKED)
    return

  # 4. 真正注入：构造 flit，放入接入 router 的 local input buffer
  f = build_flit(pkt, ep.current_injection_flit_seq, now)
  router = router_of(ep.attached_router)
  ip, iv = ep.attached_router.port, vc_target
  router.input_vcs[ip][iv].queue.push_back(f)
  ep.injection_credit[vc_target] -= 1
  ep.current_injection_flit_seq += 1

  # 5. packet 注入完毕：清当前句柄
  if ep.current_injection_flit_seq == pkt.num_flits:
    ep.injection_queue.pop_front()
    ep.current_injection_packet = 0
    pkt.state = IN_FLIGHT
```

要点：
- **packet 不能交错**：同一时刻 endpoint 最多拆一个 packet 的 flit；否则下游 wormhole 路径会被两个包的 HEADER 同时争抢同一 input VC
- `INJECTION_BLOCKED` 与 `ROUTE_BLOCKED` 分开归因：前者是网络反压，后者是 workload 依赖未满足
- endpoint 也有 credit：injection_credit 对应"接入 router 的 local input buffer 还能收几个 flit"

## backpressure 的完整回传链

把上面 ejection、move、credit、injection 串起来，就是 backpressure 的传播链：

```
consumer 不取  →  ejection_queue 满
              →  目的 router 的 local port 不能消化 flit
              →  目的 router 的 input VC 的 head flit 停在 buffer 里（slot 不释放）
              →  credit 不回传给前一跳 router
              →  前一跳 router 的 output_credit 耗尽
              →  前一跳 input VC 触发 NO_CREDIT，进入 BLOCKED_NO_CREDIT
              →  前一跳 buffer 也停止释放 slot
              →  ...
              →  传到源端 endpoint 的接入 router
              →  endpoint 的 injection_credit 耗尽
              →  endpoint 触发 INJECTION_BLOCKED
```

每一级都对应**一个明确的 stall reason 与一个 stats 计数器**。如果伪代码里某一级没归因，链就有断点，调试时无法在 wave 上对齐根因。

## 双缓冲值得优先考虑

如果担心同周期读写污染，推荐：

- `current_state`：本拍读
- `next_state`：本拍写
- tick 结尾 `swap(current, next)`

适用范围：
- `output_credit`：本拍 SA 看到的是 tick 开头的 credit；本拍 `move_flit` 扣减写入 `next.output_credit`
- `output_vc_busy / holder`：本拍 VA 看到的是上一拍的释放结果，避免 TAIL 和后包同拍抢同一 VC
- `input_vcs[*].queue`：accept 入队的 flit 不应在同一 tick 被 RC/VA 看见

哪怕多写一些代码，也能显著减少隐式抢跑和 debug 难度。

## 一句话理解

router pipeline 的关键不是把 RC/VA/SA/LT 名字写全，而是把**资源分配、移动、credit 返回、tail 释放和 backpressure 归因**的时序关系写对。每一处状态改写都对应一个不变量，每一处阻塞都对应一个 StallReason。

## 建模启示

实现阶段建议立刻为这些最小场景写手算对照：

- 3-hop 单 packet
- 两包抢同一输出
- buffer 满后的 backpressure
- tail 释放后下一包接续前进
- destination ejection blocked 沿路回传

这些最小场景的逐拍 expected state 见 [Verification And Calibration](./verification-and-calibration.md)。如果这些最小场景还不稳定，就不要急着上复杂 workload——大概率不是 workload 难，是 pipeline 的时序还在飘。
