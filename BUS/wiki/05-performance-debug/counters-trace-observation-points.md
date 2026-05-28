# Counters、Trace 与观测点设计

上级：[05 性能与调试](./README.md)

相关：[争用、QoS 与可观测性](./contention-qos-observability.md)、[带宽、延迟、利用率与拥塞](./bandwidth-latency-utilization.md)、[互连组件与数据路径分解](../04-microarchitecture-integration/interconnect-components.md)、[Timeout、Fault 与 Hang 定位框架](./timeout-fault-hang-debug-framework.md)

## 这页在回答什么问题

BUS observability 就像交通系统的**监控摄像头和数据记录仪**。目标不是”装越多摄像头越好”，而是在出事后能回答四个问题：**谁上的路**（谁发起请求），**堵在哪个路口**（在哪排队），**谁没到达**（谁没有返回），**哪里出的事故**（错误由哪一层生成）。

如果摄像头没标注路口名（counter 语义不清），录像回放时看不出堵在哪；如果摄像头 24 小时无差别录（trace 没有触发条件），硬盘很快就满了；如果摄像头只装在入口（观测点只放在 master 端），就分不清是”没车进来”还是”进去了出不来”。

## Counter 要先定义语义

同名 counter 在不同团队里可能含义不同。设计时必须把计数边界钉死。

| Counter | 建议定义 | 不能混淆 |
| --- | --- | --- |
| request_accept_count | 地址或请求 channel 上 `VALID && READY` 的次数 | 不等于 source 尝试次数 |
| payload_beat_count | data channel 上成功传输的 beat 数 | 不等于有效 payload byte 数 |
| backpressure_cycles | `VALID && !READY` 的周期数 | 需区分 request/data/response channel |
| arbiter_wait_cycles | 请求已入队但未获 grant 的周期数 | 不等于 master issue wait |
| service_cycles | slave/controller 从开始服务到完成的周期数 | 不含上游排队，除非明确定义 |
| completion_latency | request accepted 到最后 response/beat 返回 | 读写完成点要分开定义 |
| timeout_count | timeout wrapper 触发次数 | 不等于软件等待超时次数 |
| fault_count | 原生 fault source 记录次数 | 不等于最终软件异常次数 |

语义清楚后，counter 才能成为模型变量。否则“latency counter 变大”无法说明是 request wait、service time、response wait 还是 completion visibility 变慢。

## Counter 要能分类

总计数只能说明系统忙，无法归因。至少要按以下维度切分：

| 分类维度 | 价值 |
| --- | --- |
| master ID / source | 找出谁发起、谁被饿死 |
| slave / target | 找出热点目标 |
| read / write | 区分 R path、B path、turnaround |
| ID / queue / channel | 区分多队列、多 outstanding |
| QoS class / priority | 验证 QoS 是否生效 |
| error type | 区分 decode、slave、timeout、translation fault |
| boot/debug/normal mode | 区分非运行态访问 |

分类会增加面积和寄存器数量。取舍方式是把高粒度 counter 放在关键共享点，把低粒度 aggregate counter 放在边缘路径；对低频错误使用 sticky status 和 last-event snapshot，比大量持续计数更有价值。

## 观测点放在哪里

观测点应覆盖一次 transaction 的生命周期。

| 位置 | 观测内容 | 能定位的问题 |
| --- | --- | --- |
| master issue boundary | issue attempt、accept、outstanding | master 是否被上游或 slot 限制 |
| ingress FIFO | occupancy、full、push/pop | 请求是否在入口排队 |
| arbiter | request、grant、wait、selected QoS | 谁在竞争共享点 |
| bridge/adapter | accept、split/merge、downstream wait | 协议/宽度/CDC 转换是否阻塞 |
| slave/controller | service start/done、busy、error | 目标是否慢或报错 |
| return path | response FIFO、R/B beat、response wait | outstanding 为什么不释放 |
| completion/interrupt | completion visible、interrupt assert、clear done | 软件为什么没看到完成 |

每个共享点前后各有一个观测，才能区分“上游没给我活”和“我下游做不完”。只在最终 slave 放 counter，会漏掉 bridge、return path 和 completion path 的排队。

## Trace 点：少量关键事件比全量波形更有用

Counter 告诉你"今天这个路口通过了 10 万辆车、平均等待 3 秒"。Trace 告诉你"14:32:07 那辆红色卡车等了 45 秒才通过，因为前面有事故"。Trace 适合记录低频但关键的事件链，不适合 24 小时全量录像。

| Trace 点 | 建议记录字段 | 用途 |
| --- | --- | --- |
| request accepted | timestamp、master、target、ID、addr、type、QoS | 建立 transaction 起点 |
| arbiter grant | timestamp、shared point、winner、wait cycles | 复盘争用 |
| queue high watermark | timestamp、queue id、occupancy | 找拥塞峰值 |
| response returned | timestamp、ID、response、latency | 闭环 transaction |
| timeout/fault | timestamp、source、addr/ID、fault type | 错误归因 |
| completion/interrupt | timestamp、task/channel、status | 连接硬件完成和软件可见性 |

Trace 的设计动机是补 counter 的因果缺口。Counter 告诉你发生了多少次，trace 告诉你哪一次、按什么顺序发生。

## 触发与 Snapshot

好的监控系统不是"一直录"，而是**"发现异常时自动保存前后 30 秒"**——就像行车记录仪的碰撞检测功能。trace 需要触发条件和 snapshot。

| 触发条件 | 适合捕捉 |
| --- | --- |
| latency 超过阈值 | tail latency、near-timeout |
| FIFO occupancy 超过 high watermark | 短时拥塞 |
| timeout/fault 触发 | 错误现场 |
| outstanding age 超过阈值 | response missing / hang |
| QoS starvation counter 超阈值 | 低优先级长期等待 |
| interrupt latency 超阈值 | completion 到软件可见的长尾 |

snapshot 应记录“最后 N 个关键事件”，而不是只记录触发瞬间。定位 hang 时，最后一个 forward progress 事件比当前静止状态更有价值。

## 例子：DMA Completion 丢失的观测链

| 阶段 | 需要的观测 | 说明 |
| --- | --- | --- |
| T0 | doorbell accepted trace | 软件确实启动了任务 |
| T1 | descriptor fetch request/response counter | DMA 是否拿到任务 |
| T2 | data read/write completion counter | 数据面是否完成 |
| T3 | completion write accepted trace | writeback 是否发出 |
| T4 | completion visible / memory write response | CPU 是否应看到 completion |
| T5 | interrupt assert trace | 设备是否发通知 |
| T6 | interrupt clear/EOI trace | ISR 是否正确清理 |

缺少任意一段，调试都会退化成猜测。若只看 interrupt 没来，无法判断是 DMA 未完成、completion 未写、interrupt 丢失，还是 clear 语义错误。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| counter 越多越好 | 语义不清或无法分类的 counter 只会增加噪音 |
| trace 可以替代 counter | counter 适合长期趋势，trace 适合低频因果 |
| 只要抓协议波形就够 | 复盘还需要 master/target/ID/QoS/latency/error 字段 |
| 观测点放在 master 端就够 | return path、bridge、completion path 也会制造等待 |

## 一句话理解

好的 BUS observability 不是全量抓取，而是用定义清楚的 counter 和关键 trace 把 transaction 的发起、排队、服务、返回和错误串起来。

## 建模启示

观测点要和性能模型使用同一组事件。模型里有 queue、arbiter、bridge、slave、return path、completion path，硬件观测就要覆盖这些节点。性能模型要能消费 request count、wait cycles、queue high watermark、service time、response latency、timeout/fault count 和 completion latency。功能模型要能关联 error type、fault source、resource release、interrupt clear 和最后一次 forward progress。

事件模型建议显式表达 `counter_increment`、`trace_request_accept`、`trace_arbiter_grant`、`trace_queue_high_watermark`、`trace_response_return`、`trace_timeout_fault`、`trace_completion_interrupt`、`snapshot_freeze`。这些事件让性能分析、波形调试和故障复盘使用同一套事实。
