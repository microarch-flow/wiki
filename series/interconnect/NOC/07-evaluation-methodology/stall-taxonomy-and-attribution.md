# Stall 分类与归因：等待发生在哪里？

<span id="stall-taxonomy-and-attribution"></span>

上级：[08 性能评估与架构探索](../SUMMARY.md#07-evaluation-methodology)；原章节：[07 Evaluation Methodology](./README.md)

相关：[Credit 与反压](../02-router-microarchitecture/credit-based-flow-control.md)、[网络接口 NI](../05-system-integration/ni-network-interface-design.md)、[验证与校准](../08-simulator-construction/verification-and-calibration.md)

<span id="这页在回答什么问题"></span><span id="为什么-taxonomy-比平均-latency-更重要"></span>延迟告诉我们等待了多久；stall 分类记录某个对象当时不能前进的条件。分类有助于定位，但**一个局部标签不自动证明系统根因**。

## 先固定统计对象

<span id="attribution-的核心规则"></span>例如，router 统计每个非空 input VC 的队首 flit：每个队首在每个 cycle 成功前进，或记录至多一个主阻塞原因。空 VC 不计 stall。这个分母是 `flit-router-cycle`，不是 packet 数或全网 cycle 数。

多个可观察的阻塞条件可能同时存在。可以按固定顺序选择一个主标签供汇总，另记其他已观察到的条件；但没有 credit 的候选若未进入 switch 仲裁，不能把它假定为实际输掉了仲裁。端点注入和工作负载依赖使用各自对象与分母，不与 router 队首周期直接相加。统计规则与[第九章快照契约](../08-simulator-construction/router-pipeline-pseudocode.md#时间与快照契约)保持一致。

## 一组可观察的等待

<span id="一套实用的主-stall-类别"></span>

| 标签 | 本例统计对象 | 直接观察到的条件 |
| --- | --- | --- |
| <span id="route_blocked"></span>`ROUTE_BLOCKED` | router 队首 | 当前规则下没有可选择的合法路由；永久非法路径应作为配置或正确性问题处理。 |
| `VC_ALLOC_FAIL` | router 队首 | 路由已确定，但尚未获得所需下游 VC 许可。 |
| <span id="no_credit"></span>`NO_CREDIT` | router 队首 | 发送端记录的目标 VC 可用 credit 为 0。 |
| <span id="link_blocked"></span>`LINK_BLOCKED` | router 队首 | 已满足其他发送条件，但链路或 serializer 本拍不能接收。 |
| <span id="switch_conflict"></span>`SWITCH_CONFLICT` | 已参与仲裁的队首 | 该候选具备参与条件，但没有获得 switch 服务。 |
| <span id="ejection_blocked"></span>`EJECTION_BLOCKED` | 目的 router 队首 | 本地输出无法将队首交给目的端接收队列。 |
| <span id="injection_blocked"></span>`INJECTION_BLOCKED` | 已就绪、尝试注入的端点对象 | 注入许可、credit 或其他明确的注入资源不可用。 |
| <span id="waiting_for_dependency"></span>`WAITING_FOR_DEPENDENCY` | 工作负载事件 | 前驱或本地数据条件尚未满足，事件还没有就绪。 |

端点可以按 endpoint-cycle、队列头 packet-cycle 或其他方式计数，但要明确对象和分母。同一周期有多个待注入 packet 时，这些口径并不相等。

## Credit 为零不等于下游此刻满

单 VC 深度为 B，每次发送预留一个下游槽，每次出队返回一个 credit，且无丢失或重复时，可以检查：

> 发送端可用 credit + 前向在途 flit + 下游已占槽 + 返回在途 credit = B。

例如下游已消费一个 flit，腾出的槽对应 credit 还在返回路径上；发送端仍可能观察到 `NO_CREDIT`。批量返回或额外预留需要把相应状态加入守恒式。[窗口深度与发送速率](../02-router-microarchitecture/credit-based-flow-control.md#窗口深度与发送速率)说明时间边界。

## 从现象走向可检验的解释

<span id="一个实用的归因顺序"></span>假设目的 consumer 停止，ejection 队列逐渐填满。目的 router 先观察到 `EJECTION_BLOCKED`；下游输入槽随后不再释放，上游耗尽已有 credit 后可能观察到 `NO_CREDIT`。继续供数且资源有限时，阻塞还可能向更远处传播。

要判断这个路径是否主导任务延迟，应同时查看 consumer 服务、ejection 和 input 队列、credit 往返及任务依赖。可以在相同工作负载和其他配置下改变目的端服务能力，比较等待和任务完成时间；这验证的是所选模型中的干预，不自动证明真实硬件只有同一原因。

## 对齐观测点和时间窗口

先记录每个计数器观察的是请求、packet、flit、字节，还是某种等待周期；注明方向、端口、class、时钟域、开始和结束时间，以及计数器清零、溢出或采样方式。发起端尝试发送、接口实际握手、链路实际传输和 consumer 消费是不同事件。不能直接把不同对象的计数相减，也不能把每 VC 的等待周期相加当作全网经过的时间。

例如，观察到发起端 `valid=1` 而 `ready=0`，只能说明该接口当时未完成握手；若另有对应资源的 `NO_CREDIT` 观测，才能进一步确认发送许可不足。链路空闲同时发起端等待，可能涉及注入、反馈、目的端或依赖，还要沿路径取证。可在相同输入和测量边界下改变一个资源条件，比较等待与完成；实际计数器是否提供这些事件由器件决定。[AMD 的 Versal NoC 监控文档](https://docs.amd.com/r/en-US/pg313-network-on-chip/NoC-Performance-Monitoring)给出了在不同 NoC 组件设置监控的实例；[公开案例](../07-workload-cases/published-noc-case.md)说明其使用边界。

<span id="qos-和-fairness-为什么要一起看"></span>按 class、端点和时间窗口查看等待，检查是否有持续未获服务的对象。固定优先级、权重和共享路径会影响不同流量的结果；P99 或一次有限运行中的最长等待不构成公平性或最坏延迟证明。服务保证的前提见[端到端服务保证](../04-routing-and-flow-control/service-guarantees-and-latency-bounds.md)。

<span id="常见误区"></span><span id="一句话理解"></span><span id="建模启示"></span>先记录谁在什么资源前等待，再沿依赖和反压追踪；用明确的对照验证解释，避免把“拥塞”或某个标签直接当成最终结论。
