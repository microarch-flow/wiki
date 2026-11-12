# BUS 建模参考

上级：[08 建模与架构探索](./README.md)

相关：[BUS 在解决什么问题](../01-overview/problem-statement.md)、[BUS 分类框架](../01-overview/taxonomy.md)、[仲裁、顺序性与 Backpressure](../02-fundamentals/arbitration-ordering-backpressure.md)、[位宽、时钟、Burst 与延迟](../02-fundamentals/width-clock-burst-latency.md)、[带宽、延迟、利用率与拥塞](../05-performance-debug/bandwidth-latency-utilization.md)

## 这页在回答什么问题

前面每一章的页脚都有"建模启示"，但它们是分散的。这一页把它们收敛成一份可直接编码的参考：建一个 BUS / 互连模型时，应该用哪些事件和协议依赖，选哪一层保真度，每个组件要带哪些参数，靠哪几个公式定容量，怎样映射到 SystemC TLM-2.0 / gem5，以及怎样校准。

这页面向的是"做架构探索工具的人"，不是"第一次学 BUS 的人"。如果概念还不熟，先回 [BUS 在解决什么问题](../01-overview/problem-statement.md) 和 [仲裁、顺序性与 Backpressure](../02-fundamentals/arbitration-ordering-backpressure.md)。

## 1. 统一事件词汇与协议依赖图

事件名要统一，顺序则由协议、方向和实现决定，不能把所有事务压成同一条串行状态链。先记录 `issue_attempt`、各通道 `fire/accept`、仲裁与目标服务、数据 beat、协议响应生成和消费；只有设备任务涉及 writeback、通知和软件消费时，才再记录相应的软件可见事件。

例如 AXI4 写：AW 与 W 可独立握手，W 可以先到并被缓冲；下游目标路由依赖地址上下文。已接受 AW 和全部 W 后才允许生成 B，B fire 才是该接口事务完成。读则由 AR fire 建立请求，R 各拍握手携数据和状态，最后 R fire 完成读事务。多个不同请求及通道可以重叠；仲裁和 service 在路径上可能出现多次。

```text
AW fire ───────┐
                ├─> 所需目标处理及全部 W 已接收 ─> B 生成 ─> B fire
W beat fire × N┘                 （目标处理可与 W 接收重叠）
AR fire ─> 目标处理 ─> R beat fire × N，最后一拍 RLAST（协议读完成）
设备任务：所需数据事务完成 ─> writeback ─> 通知/轮询 ─> CPU 同步和消费
```

各节点记录所属端口、方向、事务身份、时间及等待资源；每个协议依赖边记录触发条件。入口 accept 只说明该边界接收，不能代替末端协议完成；一次 B fire 也不自动表示软件任务 completion 已消费。性能模型据此测输入回压、仲裁等待、服务、返回阻塞与软件可见时间。

## 2. 三层保真度（fidelity tiers）

"选哪一层抽象"是建模工具的第一决策。wiki 各页反复说的"只关心 latency/bandwidth 就折叠 X，关心功能就保留 Y"，本质就是下面三层（对应 SystemC TLM-2.0 的 LT/AT 与 cycle-accurate）：

| 层级 | 保留什么 | 折叠什么 | 适合回答 |
| --- | --- | --- | --- |
| **L0 容量估算** | 端点、aggregate 带宽、平均延迟 | 仲裁、排队、顺序、回压可折叠 | 粗筛容量和带宽时延积 |
| **L1 资源与事件模型** | 依赖图、资源占用、outstanding、仲裁、FIFO、服务时间 | 信号编码、逐 bit payload、部分内部算法 | 拓扑、排队、QoS 和尾延迟探索 |
| **L2 周期精确** | 握手、每拍仲裁及所需协议状态 | 依研究目的定义 | 与目标 RTL 对拍、检查协议时序 |

这些层级描述模型内容，不由 `b_transport` 或 `nb_transport` 的 API 名称决定；它们也没有通用的误差百分比。先对目标负载和量测边界设定误差目标，再与 RTL/硬件对照。周期模型只有在实现和参数经过验证后才可声称对齐 RTL。

架构探索工具应该把 **L1 作为默认层**，并能在热点路径上局部下沉到 L2 做校准。L0 只用于早期方案漏斗。最危险的做法是"用 L0 的抽象去回答 L1 的问题"——例如只给链路一个带宽数字，却想预测某个 master 的尾延迟。

## 3. 把一笔 transaction 看成五张图

[仲裁、顺序性与 Backpressure](../02-fundamentals/arbitration-ordering-backpressure.md) 的结论值得提到建模层固化：一笔 transaction 不是沿单线移动，而是在五张资源图上切换。模型丢掉任意一张，都会系统性低估尾延迟或解释不了 hang。

| 图 | 描述什么 | 模型里的对象 |
| --- | --- | --- |
| 地址图 (routing) | 地址 → 目标 / 路径选择 | decode 表、地址映射、路由 |
| 仲裁图 (arbitration) | 谁先用稀缺资源 | arbiter 节点、候选队列、grant 粒度 |
| 数据图 (data) | 带宽占用 | data path busy、beat 计费 |
| 响应图 (response) | completion 与资源释放 | return path、response FIFO、outstanding 回收 |
| 顺序图 (ordering) | 哪些节点间存在不可越过的边 | 同 master / 同 ID 保序、barrier/fence/lock |

## 4. 组件参数 schema

这是建模工具最终要落库的东西。下面是各组件建 L1 模型时的最小参数集（具体推导见对应章节）。

**Master / Initiator**
| 参数 | 含义 |
| --- | --- |
| issue rate / pattern | 注入速率、读写比、地址局部性 |
| max outstanding | 同时在飞的 transaction 上限（按 ID 区分） |
| burst length 分布 | 决定占路时间与 beat 数 |
| 是否消费 return | 不及时消费返回会制造 response 回压 |

**Arbiter（每个仲裁点一份）**
| 参数 | 含义 |
| --- | --- |
| policy | fixed / round-robin / weighted / QoS-aware |
| weights / priority | 各 master 份额或优先级 |
| aging / boost | 是否防 starvation（影响 forward progress） |
| 粒度 | 按 beat / 服务窗口 / burst 保持 grant |

**Bridge / Width Adapter / CDC**
| 参数 | 含义 |
| --- | --- |
| fixed latency | 转换 / 同步固定延迟（拍） |
| FIFO depth | 吸收抖动 + 决定 backpressure 到达上游的延迟 |
| width ratio | 上下游位宽比 → 拆分 / 合并的 beat 变化 |
| 顺序行为 | bridge 两侧是否改变完成顺序 |

**Slave / Target**
| 参数 | 含义 |
| --- | --- |
| service time | 固定开销 + 分布（或可配 pipeline） |
| 是否可乱序 | 能否多 outstanding、不同 ID 乱序返回 |
| 错误响应 | decode error / slave error 条件 |
| 副作用 | 读写是否有副作用（影响功能层，不可随意重排） |

**Interconnect 拓扑**
| 参数 | 含义 |
| --- | --- |
| 拓扑 | shared bus / bus matrix / crossbar / 分层 |
| 冲突位置 | 全局总线 / 目标端口 / 中间链路 / bridge FIFO（见 [taxonomy](../01-overview/taxonomy.md)） |
| 端口并发度 | 哪些 master×slave 对能并行 |

**DDR / Memory Controller**：不在 BUS 模型内展开，作为一个带 service-time 分布的特殊 slave 接入；其内部 tRCD/tRP/tRAS、page policy、command scheduling 交给 [RAM Wiki 内存控制器章](../../../../../RAM/wiki/06-memory-controller/README.md)。BUS 模型只需在边界保留：请求大小、读写方向、地址（决定 row hit/miss）、QoS。

## 5. 定量主干

带宽与延迟的基础公式已在 [位宽、时钟、Burst 与延迟](../02-fundamentals/width-clock-burst-latency.md) 给出，这里不重复，只补上 wiki 里缺失但建模必需的一条核心关系。

**Little's Law（吞吐—延迟—并发的桥）**

```text
平均在飞 transaction 数  =  吞吐(事务/秒)  ×  平均延迟(秒)
```

它在稳定系统、统计边界一致且长期平均存在的前提下，把平均在途数、已完成吞吐和平均停留时间联系起来。它可估算并发容量需求，但不能单独保证吞吐：

```text
要在延迟 L 下打满带宽 B(字节/秒)，每笔搬 S 字节：
  平均所需在途数 = (B × L) / S
  硬件槽数至少 ceil(B × L / S)           ← 简化的容量下界
```

此处 B 是同一边界的目标有效字节吞吐，S 是每笔平均有效字节，L 是同一边界从接收到完整响应消费的平均停留时间。若槽数低于该下界，在这些假设下不能达到目标；还要检查注入率、服务带宽、顺序、缓冲和回压。增加 ID 数不必然增加同 ID 可用槽，也不能保证吞吐。若 outstanding 长期满而目标服务空闲，应同时检查返回路径、slot 回收和请求供给；仅凭该现象不能唯一定位。

**服务时间模型（L1 计费）**
```text
total_cycles = fixed_cycles + beat_count / service_rate + wait_cycles
beat_count   = ceil(payload_bytes / data_width_bytes)   （窄传输/未对齐/跨边界会增大）
```
`wait_cycles` 不是常数，而是上面五张图在该时刻的排队结果——这正是要靠仿真而非闭式公式求解的部分。

## 6. 映射到建模框架

框架调用是模型事件的载体，并不自动等同硬件握手。需要由模型定义映射、资源占用和时间注解：

| 关注点 | SystemC TLM-2.0 | gem5 timing mode |
| --- | --- | --- |
| 发起与接收 | `nb_transport_fw(BEGIN_REQ)` 表示发起阶段；按模型约定及时间注解，用 `END_REQ` 或等效协议进展表示接收点 | `sendTimingReq` 调到 `recvTimingReq`，返回 true 才表示该次请求被接收 |
| 暂不可接收 | 基础协议通过 phase、返回枚举与时间注解描述推进；`TLM_ACCEPTED` 是合法返回枚举，不等于本模型硬件 request_accept | 返回 false 时发送方保留请求，等待 `recvReqRetry` 后重试 |
| 返回 | `BEGIN_RESP`、`END_RESP` 或协议允许的 `TLM_UPDATED/TLM_COMPLETED` 路径；须按 phase 和注解处理 | `sendTimingResp`；未接收时按响应 retry 契约处理 |
| 仲裁与服务 | 组件内部状态、队列和 payload extension | 模型中的队列、仲裁与 Packet 状态 |

TLM-2.0 `nb_transport` 返回值是 `TLM_ACCEPTED`、`TLM_UPDATED` 或 `TLM_COMPLETED`，不是 gem5 的布尔拒收。一次调用何时代表实际资源接收，必须在模型中定义，并遵循基础协议 phase 与 timing annotation。`b_transport` 是阻塞调用，但实现仍可显式建资源队列、等待与延迟；是否足以研究争用取决于并发、时间和资源状态的建模，而不是 API 名。依据 [Accellera TLM-2.0 LRM](https://accellera.org/images/downloads/standards/systemc/TLM_2_0_LRM.pdf) 第 4、8 章和 [gem5 timing port 文档](https://www.gem5.org/documentation/learning_gem5/part2/memoryobject/)。

## 7. 校准与验证

一个性能模型不被信任，再精巧也没用。校准顺序建议：

1. **静态参数先对齐**：位宽、频率、FIFO 深度、outstanding 上限、bridge 固定延迟——这些有确定值，先锁死。
2. **单流校准 service time**：单 master 单 slave 跑通，用 RTL/silicon 的 per-transaction latency 对齐 `fixed_cycles` 和 `service_rate`，此时 `wait_cycles≈0`。
3. **多流校准排队**：加入争用，对齐 arbiter wait、FIFO occupancy、outstanding 直方图，校准仲裁粒度和权重。
4. **尾延迟校准**：对齐 p99 / max，而不只是平均；尾巴对不上通常是顺序约束或 return path 回压建得不对。

| 校准对象 | 对齐的观测量 | 数据来源 |
| --- | --- | --- |
| 服务时间 | per-transaction latency（平均） | RTL 波形 / 硬件 counter |
| 排队 | queue depth、arbiter wait、outstanding 分布 | trace / counter |
| 回压 | READY 低占比、FIFO occupancy | 波形 |
| 完成 | completion / interrupt latency 分布 | 软件可见 timestamp |

校准前按用途设定可接受误差：对指定负载、统一观测窗口分别比较吞吐、平均与尾延迟、未完成/超时数，并保留未参与拟合的验证场景。不能事先断言某个通用百分比足以选型。对不上时，**先怀疑五张图里漏建了哪一张**，而不是去调系数。

## 8. 最危险的简化（反模式清单）

把散落各页的告警收敛成一张表，建模时逐条自查：

| 反模式 | 后果 | 正确做法 |
| --- | --- | --- |
| 把访问建成"延迟 N 拍后完成"单事件 | 丢掉 outstanding / 排队 / 回压 / 尾延迟 | 用第 1 节的事件与协议依赖，分开 accept 和 complete |
| 用协议名直接推性能（"AXI 就高并发"） | 高估或低估系统 | 协议名只当默认参数来源，用角色/拓扑/能力校准 |
| 只给链路一个 aggregate 带宽 | 看不到 per-master 饿死、热点 slave、尾延迟 | 保留 per-master / per-slave / 仲裁点状态 |
| 合并 request accept 与 response complete | outstanding、回压、长尾全消失 | 永远两个事件 |
| 丢掉顺序图 | 解释不了"快请求被慢请求挡住"、hang | 显式建同 master/同 ID 保序与 barrier 边界 |
| FIFO 做深当成解决拥塞 | 只是把拥塞可见位置推远 | 持续拥塞要看注入>服务，深 FIFO 不治本 |
| 按 API 名称推断模型精度 | 忽略队列、并发和时间注解的实际实现 | 核对资源状态和事件依赖，再用量测校准 |

## 一句话理解

建一个能支撑架构探索的 BUS 模型，需要按问题选择保真度，以统一事件词汇和协议依赖表达各通道，在地址/仲裁/数据/响应/顺序资源图上跟踪占用；用 Little's Law 估算稳态并发下界，再用 RTL 或硬件数据校准。若合并 accept 与协议完成，或只留一个带宽数字，模型可能遗漏回压、尾延迟和 no-progress。
