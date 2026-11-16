# Simulator 数据结构与伪代码

上级：[建模与评估](./README.md)

相关：[Simulator 设计规格](./simulator-design-spec.md)、[Router Pipeline 与 Allocator](../02-router-microarchitecture/router-pipeline-allocator.md)

## 读这页前先统一几个词

- `data structure`：程序里保存网络状态和 packet 状态的对象定义
- `state`：某个周期结束后，系统当前持有的所有关键信息
- `tick`：模拟器向前推进一个周期的动作
- `pseudocode`：表达控制流程的近代码描述，不要求可直接运行
- `metadata`：不直接参与转发，但对统计、调试或 workload 关联有用的附加字段

## 为什么这页单独存在

`Simulator（模拟器）设计规格` 解决的是边界和目标。  
真正开始写代码时，你还会立刻碰到两个问题：

- 数据结构到底怎么落
- 每周期 tick 到底怎么写

这页提供的是第一版可执行粒度的抽象。

## 推荐的数据结构骨架

### Packet

```text
Packet {
  id
  src
  dst
  traffic_class
  num_flits
  route_id
  creation_cycle
  metadata
}
```

`metadata` 可用于放：

- stream_id
- request_id
- workload tag
- multicast（组播）/ reduce（归约）hint

### Flit

```text
Flit {
  id
  packet_id
  type            // HEADER / BODY / TAIL
  seq
  src
  dst
  traffic_class
  route_progress
  assigned_vc
  enter_cycle
}
```

### VC Buffer Entry

```text
VCState {
  flit_queue
  packet_active
  route_ready
  output_port
  output_vc
}
```

关键点：

- `packet_active` 表示这个 VC（虚通道）目前是否被某个 wormhole（虫孔转发）packet（数据包）占住
- `output_port / output_vc` 由 header 建立，body / tail 复用

### Router

```text
Router {
  id
  input_vcs[port][vc]
  output_credit[port][vc]
  output_vc_free[port][vc]
  switch_requests
  switch_grants
  local_ejection_queue
}
```

### Link

```text
Link {
  src_router
  src_port
  dst_router
  dst_port
  pipeline_latency
  in_flight_flits
}
```

如果第一版链路是 1-cycle，可把 `in_flight_flits` 简化成单槽。

### Endpoint / NI（网络接口）

```text
Endpoint {
  id
  injection_queue
  ejection_queue
  pending_packets
  consumer_state
}
```

### Stats

```text
Stats {
  packet_latency_hist
  link_utilization
  router_occupancy
  stall_cycles_by_reason
  stall_cycles_by_class
  workload_completion_cycle
}
```

## 一套推荐的枚举

### FlitType

```text
HEADER
BODY
TAIL
```

### TrafficClass（流量类别）

```text
CONTROL
MEMORY_REQUEST
MEMORY_RESPONSE
STREAM
BULK_DMA
```

### StallReason（停顿原因）

```text
NONE
NO_CREDIT            // 无可用信用
SWITCH_CONFLICT      // 交叉开关冲突
LINK_BUSY            // 链路繁忙
EJECTION_BLOCKED     // 弹出受阻
INJECTION_BLOCKED    // 注入受阻
ROUTE_BLOCKED        // 路由受阻
WAITING_FOR_OTHER_STREAM  // 等待其他数据流
VC_UNAVAILABLE       // 虚通道不可用
```

第一版可以把 `VC_UNAVAILABLE` 并入 `ROUTE_BLOCKED`，但单独保留更利于分析。

## Router Tick 伪代码

```text
tick_router(router):
  accept_arriving_flits(router)
  accept_returning_credits(router)
  update_local_ejection_state(router)

  for each input_vc:
    if head_flit is HEADER and route not ready:
      compute_route(head_flit)

  for each input_vc:
    if head_flit is HEADER and needs output_vc:
      request_vc_allocation(input_vc)

  run_vc_allocator(router)

  for each input_vc:
    if head_flit can advance:
      request_switch(input_vc, output_port)

  run_switch_allocator(router)

  for each granted input_vc:
    move_flit_to_output_or_ejection(router, input_vc)
    if input buffer slot released:
      generate_credit_to_upstream()
    if flit is TAIL:
      release_packet_path_state()
```

## 全局 Tick 伪代码

```text
tick_system():
  endpoints_generate_packets()
  endpoints_packetize_to_injection_queue()

  for each router:
    phase_collect_inputs(router)

  for each router:
    tick_router(router)

  advance_links()
  deliver_link_outputs()
  update_stats()
  cycle += 1
```

如果担心读写同周期互相污染，建议做双缓冲（double buffering）：

- `current_state`
- `next_state`

## Injection 伪代码

```text
try_inject(endpoint, attached_router):
  if injection_queue empty:
    return
  pkt = peek(injection_queue)
  if no local input_vc available:
    record(INJECTION_BLOCKED)
    return
  if local route / vc precondition not met:
    record(ROUTE_BLOCKED)
    return
  push first flit into router local input_vc
```

## Ejection 伪代码

```text
try_eject(router, flit):
  if ejection_queue full:
    record(EJECTION_BLOCKED)
    keep flit at local output staging
    return
  enqueue_to_endpoint(flit)
```

## Credit Return 伪代码

```text
on_pop_input_buffer(router, input_port, input_vc):
  schedule_credit_to_upstream(input_port, input_vc)
```

关键原则：

- credit（信用）在 slot（槽位）释放时返回
- 不是 flit（流控单元）抵达时立即返回

## 一组推荐的最小单元测试

1. 3-hop（三跳）单 packet 延迟是否符合手算
2. input buffer（输入缓冲）满时 source 是否停发
3. tail 释放后 output_vc_free 是否恢复
4. 两个输入抢一个输出时仲裁是否稳定
5. ejection queue（弹出队列）满时 backpressure（反压）是否传回

## Debug 时最该打印什么

第一版建议可选打印：

- flit move trace
- credit update trace
- vc allocation trace
- switch grant trace
- stall reason trace

不要一开始就打印一切，否则很难看。

## 一个很实用的实现建议

把“移动 flit”和“统计 stall”分开写。  
状态转移逻辑和统计逻辑分离后，模型更容易 debug，也更容易改统计口径。

## 本页结论

第一版 NoC（片上网络）simulator 的关键，不在于把类设计得多优雅，而在于让 `packet / flit / VC / credit / tick order（时钟步进顺序）/ stall accounting（停顿统计）` 这几件事边界清楚、行为一致。
