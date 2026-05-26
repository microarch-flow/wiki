# Core Data Structures

上级：[08 Simulator Construction](./README.md)

相关：[Simulator Design Spec](./simulator-design-spec.md)、[Router Pipeline Pseudocode](./router-pipeline-pseudocode.md)

## 这页在回答什么问题

这页回答：第一版 NoC simulator 的核心状态到底应该落成哪些数据结构，哪些字段是必须的，哪些可以晚点补。

## 设计原则

第一版数据结构最重要的不是“通用到包打天下”，而是：

- 清晰表达当前状态
- 支持可解释的状态转移
- 不把未来扩展卡死

因此推荐对象少而清楚，而不是大而全。

## Packet

第一版 `Packet` 至少建议包含：

- `packet_id`
- `src`
- `dst`
- `traffic_class`
- `num_flits`
- `creation_cycle`
- `flow_id`
- `route_hint` 或 `route_id`

`Packet` 更偏 workload / flow 语义，是“一个传输请求”的抽象。

## Flit

`Flit` 是真正进入网络推进的对象，至少建议包含：

- `flit_id`
- `packet_id`
- `flit_type`：`HEADER/BODY/TAIL`
- `seq_in_packet`
- `traffic_class`
- `current_router`
- `assigned_vc`
- `enter_cycle`

如果不把 `Flit` 单独建出来，很多 wormhole 和 credit 规则会变得很难表达。

## VC / Input Buffer State

对每个 input VC，推荐至少保留：

- flit queue
- packet_active
- route_ready
- output_port
- output_vc

关键思想是：

- header 建路
- body / tail 复用已有分配
- tail 释放状态

这层状态是 wormhole 路径占用的核心。

## Router

`Router` 建议至少持有：

- `input_vcs[port][vc]`
- `output_credit[port][vc]`
- `output_vc_free[port][vc]`
- `switch_requests`
- `switch_grants`
- `local_ejection_queue`

不要把 credit 或 ejection 这类状态藏进临时变量里。它们是后面绝大多数解释力的来源。

## Link

`Link` 至少应有：

- `src_router / src_port`
- `dst_router / dst_port`
- `pipeline_latency`
- `in_flight_flits`

如果第一版链路只是一拍延迟，可以把 `in_flight_flits` 简化成单槽，但接口最好别写死。

## Endpoint / NI

`Endpoint` 推荐至少保留：

- `injection_queue`
- `ejection_queue`
- `pending_packets`
- `consumer_state`

对 AI NoC，endpoint 不是附属对象；很多关键 stall 就发生在这里。

## Stats

统计对象最好也是一等结构，而不是边跑边打日志。至少建议：

- packet latency histogram
- per-link utilization
- per-router occupancy
- stall cycles by reason
- stall cycles by class
- workload completion cycle

## 推荐的枚举

最值得固定的是：

- `FlitType`
- `TrafficClass`
- `StallReason`

越早固定枚举，后面的 trace、stats、case card 越容易保持一致。

## 一句话理解

第一版核心数据结构的任务，是把 wormhole、credit、endpoint 和统计边界都显式化，而不是把一切塞进一个“大状态对象”里。

## 建模启示

实现时建议让：

- `Packet` 偏 workload 语义
- `Flit` 偏网络推进语义
- `VCState` 偏资源占用语义
- `Stats` 偏归因语义

这四层分开，后续扩展最稳。
