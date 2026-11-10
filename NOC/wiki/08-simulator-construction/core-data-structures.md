# Core Data Structures

上级：[08 Simulator Construction](./README.md)

相关：[Router Pipeline Pseudocode](./router-pipeline-pseudocode.md)、[Verification And Calibration](./verification-and-calibration.md)、[VC 基础](../02-router-microarchitecture/virtual-channel-fundamentals.md)

## 对象与模型边界

本文定义一个可验证的单播、flit 级、wormhole 模型。输入是拓扑、端口和 VC 容量、路由规则、链路时延、endpoint 消费规则及 packet 到达时间。输出是逐拍事件、完成时间、阻塞原因和资源状态。它是教学模型，不声明与任何实现的时序完全一致。

| 对象 | 主要状态 | 职责 |
|---|---|---|
| Packet | `id, src, dst, class, num_flits, ready_cycle`，三个完成时间 | 承载 workload 与统计语义 |
| Flit | `packet_id, seq, type, assigned_vc, hop_count` | 在队列、switch 和 link 中前进；单 flit 包的类型为 `HEAD_TAIL` |
| Input VC | FIFO、`active_packet`, `route`, `out_vc` | 暂存 flit；保存队首包的本地路由上下文 |
| Output VC | `credit`, `permission`, `owner_packet` | 记录下游空槽数量与分配许可；只用于跨 router link。busy 且 owner 是本包时，BODY/TAIL 可继续使用绑定 |
| Link | 正向 flit 和反向 credit/free 消息的定时队列 | 按声明的延迟传输，不在发送拍直达接收端 |
| Endpoint | injection FIFO、当前包和固定注入 VC、ejection FIFO、consumer | 管理注入、弹出、消费及相应反压 |
| Stats | 注入、到达、消费、静止、hop、stall 和 trace | 保留可复核的事件边界 |

同一包的 flit 在一个 input VC 中按 HEADER、BODY、TAIL 的顺序前进；单 flit 包兼具 HEADER 和 TAIL。不同包是否可以提前共用 FIFO，必须由分配策略定义，不能从 wormhole 一词推导。本文主模型选择保守许可：直到下游 TAIL 离开该 input VC，带 `free` 的 credit 返回后，上游才把该 output VC 重新标记为可分配。

## 最小字段和写入者

下表是实现契约的建议，整数宽度由目标规模选择；`None` 不能与合法 ID 混用。输入 trace 的包 ID 必须唯一，`num_flits≥1`，路由算法必须为每个候选输出给出合法端口。

| 字段 | 建议类型 | 写入者与条件 | 主要读取者 |
|---|---|---|---|
| `Packet.id/src/dst/class/num_flits/ready_cycle` | ID、枚举、非负整数 | workload 或 trace；注入前冻结 | scheduler、routing、统计 |
| `Packet.injection_cycle/network_arrival_cycle/consumer_complete_cycle` | 可空 cycle | 分别由首 flit 注入、tail 弹出、tail 消费成功时写入 | latency 和依赖检查 |
| `Flit.packet_id/seq/type` | ID、非负整数、枚举 | 构造时写入，类型为 HEADER/BODY/TAIL/HEAD_TAIL | router、验证 |
| `Flit.assigned_vc/hop_count` | VC ID、非负整数 | 入网或跨路发送时写 VC；只有跨 router link 发送时 hop 加 1 | 下游入队、路径统计 |
| `InputVC.queue/active_packet/route/out_vc` | FIFO、可空 ID/端口/VC | 到达入队；队首建立上下文；tail 成功移出后清理本地上下文 | RC/VA/SA、断言 |
| `OutputVC.credit/permission/owner_packet` | 整数、busy/free、可空 ID | 跨路发送扣 credit；credit 到达加回；VA 与 tail free 更新许可 | VA/SA、守恒断言 |
| `Link.forward_pipe/return_pipe` | 带 `due_cycle` 的 FIFO | 发送 flit 或释放 input slot 时建立消息，到期提交 | 下游 FIFO、上游 credit/free |
| `Endpoint.injection_queue/current_packet/pinned_vc/injection_credit` | FIFO、可空 ID/VC、整数 | 接纳 ready packet，成功注入或收到 credit 时更新 | 注入仲裁与反压统计 |
| `Endpoint.ejection_fifo/consumer_rate` | FIFO、flit/拍 | LOCAL 成功弹出入队，consumer 成功读取出队 | packet 完成与反压统计 |
| `Stats.stalls[class,reason]/link_flits/packet_times` | 计数器、时间表 | 相应提交或阻塞事件发生时更新 | 输出、回归与诊断 |

input 上下文可以用 `IDLE → ROUTING → WAITING_VA → ACTIVE → IDLE` 表达。某些阶段可合并，但不得跳过资源检查。为避免定义冲突，`BLOCKED_NO_CREDIT` 可以是状态标签，也可以只是一拍的 stall 原因；选择其一并保持一致。endpoint 注入阻塞、空队列和 workload 依赖等待不属于同一计数对象。

建议将每个成功注入、跨路发送、slot 释放、credit/free 到达、弹出和消费记录为带 cycle 的事件。对每个 flit，`injected - ejected` 计入网络在途数；`ejected - consumed` 计入 endpoint 待消费数。区分两者后，不能在网络到达时就声称 consumer 已完成。

## 三种独立状态

1. **本地上下文**：当前 input VC 记住本包的 output port、output VC 和 holder。TAIL 成功离开此 input VC 后，本地上下文可释放。弹出失败时必须保留。output VC 许可可继续由本包占有，直到 free 消息返回。
2. **slot credit**：一个 credit 表示下游该 VC 中一个可预留的 buffer slot。跨路发送消耗一个；下游真正移出一个 flit 后，返回一个。它不代表包已经完成。
3. **VC 分配许可**：许可表示新包能否分配该下游 VC。它与空槽数量分开。即使 credit 大于 0，在严格策略里，未收到尾 flit 的 free 信号也不能重新分配。

严格策略参考 [gem5 Garnet 2.0](https://www.gem5.org/documentation/general_docs/ruby/garnet-2/) 的 credit 与 free 信号。另一种设计允许在尾部 credit 返回前复用，前提是端到端 FIFO 顺序、包边界和下游上下文切换均可证明正确；不得只提前清 busy。BookSim 将 `wait_for_tail_credit` 作为可配置项，参见 [BookSim 手册](https://github.com/booksim/booksim2/blob/master/doc/manual.tex)。两种策略的吞吐、资源依赖和验证条件不同，不应混用。

## 时间字段和统计边界

| 字段 | 写入时刻 | 含义 |
|---|---|---|
| `injection_cycle` | 首 flit 成功进入源 router 的 input VC | 选中一个包、排队或注入失败都不计注入 |
| `network_arrival_cycle` | TAIL/HEAD_TAIL 成功进入目的 ejection FIFO | 网络已交付最后一个 flit；consumer 未必已处理 |
| `consumer_complete_cycle` | consumer 接收该 TAIL/HEAD_TAIL | 端点已消费包；依赖何时释放由 workload 契约决定 |
| `protocol_quiescent_cycle` | 全局待发工作、队列、正反向 link 和 VC 占用均清空的首次拍末 | 包消费完成不自动说明网络或控制消息已静止 |

上述前三项按 packet 记录；静止是全局条件。未发生的时间用 `None`，不能以 0 充当默认值。记录的事件按 [逐拍时序](./router-pipeline-pseudocode.md#时间与快照契约) 解释。可以分别报告 `network_arrival_cycle - injection_cycle` 与 `consumer_complete_cycle - injection_cycle`，并同时说明采样边界。

## 断言与守恒

对每一条有固定深度 `D` 的单向 link 和对应下游 VC，在每次提交后的快照检查：

```text
D = upstream.credit + forward_pipe_flits + downstream_input_queue_flits
    + return_pipe_slot_credits
```

四项只统计同一条 link、同一个下游 VC；转发走的 flit 不再留在原队列。slot 释放与发出 credit 必须作为同一个提交动作。源 endpoint 到源 router 的连接也要用相同守恒关系，或者明确定义不同的接入接口。LOCAL ejection 不使用这个跨路 credit 公式。

其他必要断言：每个已分配的 output VC 至多一个 owner；每个 input VC 只处理队首包的上下文；发送时 credit 必须大于 0；严格策略下只有收到带 free 的尾部 credit 才能再次分配；本地失败不 pop、不回 credit、不清上下文；空队列不记 stall。同一包固定注入 VC，成功的跨路转发才增加 hop。静止时所有 credit 恢复初始值、队列与链路为空，且所有 VC 许可已释放。启用 trace 回归时，逐项输出拍、对象 ID、期望值和观测值；示例见 [回归记录](./verification-and-calibration.md#回归记录与独立验证)。

这些断言验证已定义的模型，不证明路由无死锁，也不证明数值符合真实芯片。[最小场景](./verification-and-calibration.md) 给出逐拍预期与反例。
