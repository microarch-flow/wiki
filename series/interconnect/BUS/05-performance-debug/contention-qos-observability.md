# 争用、QoS 与可观测性

上级：[05 性能与调试](./README.md)

相关：[Arbitration、Ordering 与 Backpressure](../02-fundamentals/arbitration-ordering-backpressure.md)、[Shared Bus、Bus Matrix 与 Crossbar](../04-microarchitecture-integration/shared-bus-bus-matrix-crossbar.md)、[带宽、延迟、利用率与拥塞](./bandwidth-latency-utilization.md)、[Counters、Trace 与观测点设计](./counters-trace-observation-points.md)

## 这页在回答什么问题

当你遇到”偶发卡顿””DMA 时好时坏””CPU 读 MMIO 卡住””display 掉帧”时，不要急着翻监控录像（波形）。就像交通事故调查一样，第一步是弄清楚：**哪辆车（哪类流量）、在哪个路口（哪个共享点）、被什么规则或障碍（哪种策略或回压）卡住了**。

争用、QoS 和可观测性必须一起设计——就像交通管理需要同时有红绿灯（QoS）和监控摄像头（observability）：没有摄像头，你无法验证红绿灯配时是否合理；没有车辆识别，摄像头拍到的只是一堆无法归因的车流数字。

## 争用来自共享点

争用不是抽象的”路很堵”——它是**多辆车在同一个路口排队等绿灯**。每个路口（共享点）的堵车原因和影响范围都不同。

| 共享点 | 竞争流量 | 可见症状 |
| --- | --- | --- |
| output arbiter | 多 master 访问同一 slave | grant wait 增加，低优先级流尾延迟变长 |
| bridge / adapter | 高速主干进入低速外设 | READY 低、FIFO 满、控制访问变慢 |
| SMMU/IOMMU translation queue | 多 DMA/device 同时翻译 | data request 未发出但 DMA 已等待 |
| DDR controller | CPU、DMA、display、accelerator 共享 memory | row conflict、write drain、tail latency |
| return path | 多 slave 或 DDR port 返回同一方向 | R/B response 抖动，outstanding slot 不释放 |
| interrupt/status path | completion、polling、clear 共用低速路径 | 软件可见完成延迟 |

设计时的关键取舍是隔离还是共享。隔离能降低互相影响，但增加面积、布线和配置；共享能降低成本，但必须有仲裁、QoS、限速和观测点。

## QoS 不是让所有流量都快

QoS 不是魔法加速器——它更像**医院的分诊台**：急诊优先、普通门诊排队、体检可以等。目标是把有限的医疗资源（服务能力）合理分配给严重程度不同的病人（流量）。实时显示是急诊、CPU 交互是普通门诊、DMA 批量搬运是住院手术、debug 访问是夜间查房。

| QoS 目标 | 典型策略 | 风险 |
| --- | --- | --- |
| 防止关键流饿死 | priority、deadline、reserved slot | 低优先级流长期等待 |
| 限制大流量破坏性 | bandwidth cap、token bucket | 批量任务完成时间变长 |
| 降低 tail latency | age-based boost、max wait | 吞吐下降，row locality 变差 |
| 保护实时流 | QoS class、dedicated queue | 配置错误会掩盖真实瓶颈 |
| 保持公平 | round-robin、weighted fair | 不一定满足低延迟需求 |

QoS 是 trade-off，不是万能开关。给 display 提高优先级可以避免 underflow，但可能拖慢 CPU 或 DMA；给 DMA 限速可以保护交互 latency，但会延长 batch completion。调试时要验证 QoS 是否按设计改变了等待时间，而不是只看配置寄存器。

## 可观测性要覆盖请求、服务和返回

只在高速入口看"车排队了"，你不知道是前方事故、收费站慢还是出口堵了。监控摄像头（观测点）要覆盖**入口、路段、收费站、出口和目的地**——对应 request path、service point、response path 和 software-visible completion。

| 位置 | 需要观测 | 能回答的问题 |
| --- | --- | --- |
| master issue | request count、issue wait、outstanding | master 是否被上游限制 |
| arbiter | grant count、grant wait、priority/QoS class | 谁在争用，谁长期等不到服务 |
| queue/FIFO | occupancy、full/empty、high watermark | backpressure 从哪里开始 |
| slave/controller | busy、service time、error/timeout | 目标是否真正慢 |
| return path | response wait、R/B beat、FIFO occupancy | outstanding 为什么不释放 |
| completion/interrupt | completion visible、interrupt latency、clear latency | 软件为什么还没看到完成 |

可观测性的设计动机是缩短定位路径。代价是 counter/trace 会占面积和功耗，观测点过多也会让分析噪音增加。工程上更重要的是观测点能形成因果链，而不是数量最大。

## 例子：DMA 时好时坏

| 观察 | 可能解释 | 下一步 |
| --- | --- | --- |
| DMA data bandwidth 波动 | DDR 与 CPU/display 争用 | 看 DDR queue、QoS、row conflict |
| descriptor fetch latency 高 | descriptor port 被 data flow 或 SMMU miss 阻塞 | 看 descriptor read、translation miss |
| writeback completion 晚 | completion 与 data write 共用 write path | 看 writeback queue、B response |
| interrupt 到达晚 | interrupt controller 或 MMIO status path 排队 | 看 completion visible 到 interrupt assert 的间隔 |
| 只有某队列慢 | AXI ID/queue/channel 映射或 QoS 配置 | 看 per-ID latency 和 grant |

这个例子说明，单个“DMA 慢”要拆成 descriptor、data、writeback、interrupt 四条路径。每条路径的共享点不同，QoS 策略也不同。

## 观测点放置原则

| 原则 | 原因 |
| --- | --- |
| 每个共享点前后各有一个观测 | 区分上游注入不足还是下游服务不足 |
| request 和 response 都要观测 | outstanding 不释放常来自 response path |
| counter 要能按 master/slave/ID/QoS 分类 | 否则无法归因到流量类别 |
| 记录 high watermark 和 max wait | 平均值掩盖短时拥塞 |
| timeout/fault 与性能 counter 对齐 | 区分慢、错和不前进 |

可观测性还要考虑复盘。一次故障结束后，工程师需要知道最后一个 transaction、最长等待点、最高 FIFO 水位、哪个 master 占用服务点、错误是否返回。没有这些信息，波形也难以缩小范围。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| QoS 配好就能解决争用 | QoS 只改变服务分配，不能消除共享点容量限制 |
| 低优先级慢是正常的 | 低优先级也需要 starvation bound 和可诊断性 |
| 波形越多越好 | 没有流量分类和观测点链路，波形会变成噪音 |
| 只看 request path 就够 | response path 和 completion path 同样会造成等待 |

## 一句话理解

争用定位要回答三件事：谁在争、争哪个共享点、QoS 和回压如何改变等待时间。

## 建模启示

争用模型要把每个共享点建成 service point，并把流量按 master、slave、ID、QoS class、transaction type 分类。性能模型要记录 grant wait、service time、queue occupancy、high watermark、starvation bound、return wait、completion latency 和 per-class bandwidth。功能模型要把 timeout、fault、priority override、debug access、boot/low-power 状态和错误返回纳入同一观察框架。

事件模型建议显式表达 `traffic_classify`、`queue_enqueue`、`arbiter_request`、`qos_select`、`grant_wait`、`service_start`、`backpressure_propagate`、`response_wait`、`completion_observed`。这些事件能把“系统偶发慢”拆成可复盘的共享点争用和 QoS 决策。
