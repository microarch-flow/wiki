# 带宽、延迟、利用率与拥塞

上级：[05 性能与调试](./README.md)

相关：[位宽、时钟、Burst 与延迟](../02-fundamentals/width-clock-burst-latency.md)、[Arbitration、Ordering 与 Backpressure](../02-fundamentals/arbitration-ordering-backpressure.md)、[Read/Write Combine 与 Bus Turnaround](../04-microarchitecture-integration/read-write-combine-turnaround.md)、[Row Locality、Return Path 与 AXI 体验](../04-microarchitecture-integration/row-locality-return-path-axi-experience.md)

## 这页在回答什么问题

BUS 性能分析不能只问“带宽跑满没有”。带宽、延迟、利用率和拥塞描述的是同一条路径的不同侧面：带宽看单位时间完成多少，延迟看单笔事务等多久，利用率看资源忙不忙，拥塞看排队和回压在哪里形成。

这四个指标必须一起看。高带宽可能伴随高尾延迟；高利用率可能来自有效载荷，也可能来自低效占路；平均延迟正常时，少数关键流量仍可能被 write drain、return path 或低速 bridge 拖出长尾。

## 四个指标的关系

| 指标 | 它回答的问题 | 容易误读的地方 |
| --- | --- | --- |
| bandwidth | 单位时间完成多少 payload 或 transaction | 总带宽高不代表每个 master 都好 |
| latency | 单笔 transaction 从发起到完成等多久 | 平均值会掩盖 tail latency |
| utilization | 某个 link、queue、slave、controller 忙了多久 | 忙不等于有效，可能是 stall 或低效 burst |
| congestion | 请求在哪个共享点排队并传播回压 | 拥塞点不一定在报慢的 master 附近 |

带宽是结果指标，延迟是体验指标，利用率是资源状态，拥塞是因果位置。只看其中一个，会把症状当成原因。

## 带宽：总量与分布要分开

BUS 带宽至少要分成总带宽、per-master 带宽、per-slave 带宽和有效 payload 带宽。

| 带宽口径 | 适合回答 | 不足 |
| --- | --- | --- |
| fabric aggregate bandwidth | 主干是否接近上限 | 看不出谁被饿死 |
| per-master bandwidth | 每个发起方实际拿到多少 | 看不出目标热点 |
| per-slave bandwidth | 哪个目标最忙 | 看不出上游排队 |
| payload bandwidth | 有效数据量 | 忽略协议开销、空洞和重试 |
| completion bandwidth | 软件可见完成速度 | 容易被 data bandwidth 掩盖 |

设计取舍在于，提升总带宽会推动更宽 datapath、更深 outstanding、更复杂仲裁和更高功耗；改善某个 master 的带宽，可能要牺牲其他流的公平性或尾延迟。

## 延迟：平均值不够

延迟要拆成多个阶段，否则无法定位。

| 延迟阶段 | 含义 | 常见原因 |
| --- | --- | --- |
| issue wait | master 想发但握手未完成 | upstream backpressure、queue full |
| arbitration wait | 已进入共享点但未获 grant | 多 master 争用、QoS 低 |
| service time | slave/controller 真正处理请求 | DDR row miss、APB wait、bridge 转换 |
| response wait | 数据或 response 返回 master | return path 争用、RREADY/BREADY、response FIFO |
| software-visible latency | 软件看到完成所需时间 | completion writeback、interrupt、cache visibility |

平均延迟只能说明中心趋势。tail latency 才暴露低频拥塞、write drain、timeout 前等待、debug/low-priority starvation 和 interrupt 可见性问题。性能模型至少要记录 p50、p90、p99 或 max，而不是只记录平均值。

## 利用率：忙不等于有效

利用率看资源忙了多久，但要分清有效忙和无效占用。

| 高利用率来源 | 含义 | 判断方法 |
| --- | --- | --- |
| payload 连续传输 | 资源被有效数据占满 | payload counter 高，stall counter 低 |
| long burst 占路 | 某流量长时间占据共享点 | 其他 master wait 增加 |
| slave wait / PREADY 低 | 资源被慢目标拖住 | valid 保持、ready 长期低 |
| read/write turnaround | 方向切换消耗窗口 | R/B 返回成批且有空洞 |
| response backpressure | 下游不能接收返回 | response FIFO 高占用，RREADY/BREADY 低 |

低利用率也不一定代表没有问题。若一个 master 因为前级回压发不出请求，目标资源可能看起来空闲；真正瓶颈在上游 queue、bridge、translation 或仲裁点。

## 拥塞：找第一个排队点

拥塞分析的目标是找第一个让请求开始排队的 service point，而不是找最后一个看到 stall 的地方。

```text
master issue
  -> input queue
  -> arbiter
  -> bridge / adapter
  -> slave / controller
  -> return path
  -> completion / interrupt
```

| 观察到的现象 | 可能的第一个拥塞点 |
| --- | --- |
| master VALID 高、READY 低 | input queue 或下游 backpressure |
| arbiter wait cycle 高 | shared output / slave 争用 |
| FIFO occupancy 持续高 | 下游服务速度低于上游注入 |
| outstanding 达上限 | response path、slave slot 或 ID slot 未释放 |
| DDR 带宽高但某 master 慢 | return path、QoS 或 scheduler tail |
| data done 但 software 等待 | completion/writeback/interrupt path |

拥塞会沿 backpressure 反向传播。看到 master stall，不代表 master 附近有问题；看到 slave busy，也不代表 slave 是唯一瓶颈。要沿 request path 和 response path 同时追。

## 例子：总带宽正常但 DMA Completion 慢

| 阶段 | 指标 | 结论 |
| --- | --- | --- |
| T0 | DDR payload bandwidth 高 | 数据面吞吐没有明显不足 |
| T1 | DMA data write outstanding 长期接近上限 | write path 被填满 |
| T2 | completion writeback 与 data write 共用 port | completion 排在大数据写之后 |
| T3 | interrupt latency 分布出现长尾 | CPU 被通知时间不稳定 |
| T4 | 软件看到 DMA 偶发超时 | 软件可见完成路径慢，不是数据未搬完 |

这个例子说明，带宽指标不能替代 completion latency。对 driver 来说，任务完成时间由 data move、writeback、interrupt 和 cache 可见性共同决定。

## 指标组合表

| 现象 | 可能解释 | 下一步观测 |
| --- | --- | --- |
| 带宽高、tail latency 高 | batching、turnaround、QoS、return path | latency histogram、queue depth、R/B burstiness |
| 利用率高、payload 低 | stall、wait state、低效 burst | payload/stall 分离 counter |
| 利用率低、master 慢 | 上游发不出请求 | master wait、input FIFO、READY 信号 |
| 平均延迟正常、偶发 hang | timeout 前等待或错误路径缺失 | max latency、timeout counter、last transaction |
| per-slave 忙、per-master 不均 | 热点 slave + 仲裁策略 | arbiter grants、QoS、starvation counter |

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| 利用率高说明设计好 | 高利用率也可能是 stall 或低效占路 |
| 总带宽够就不会慢 | tail latency、completion 和关键 master 仍可能慢 |
| 平均延迟正常就没风险 | p99/max 才能暴露低频拥塞和 timeout 前等待 |
| 拥塞点在报慢的模块附近 | 回压会传播，瓶颈可能在 response path 或远端 slave |

## 一句话理解

BUS 性能分析要把吞吐、排队、利用率、回压和尾延迟放在同一条事务路径上看。

## 建模启示

性能模型要同时记录 bandwidth、latency histogram、utilization、queue occupancy、outstanding、arbiter wait、stall cycles、response wait 和 completion latency。功能模型要把 timeout、fault、error response 和 completion release 纳入性能观测，否则“慢”和“不会完成”会被混在一起。

事件模型建议显式表达 `request_issue_attempt`、`request_accept`、`arbiter_wait_start`、`arbiter_grant`、`queue_full`、`backpressure_assert`、`service_start`、`response_release`、`completion_visible`。这些事件能把平均带宽背后的真实瓶颈拆成可定位的排队点和回压路径。
