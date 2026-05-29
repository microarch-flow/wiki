# BUS 建模参考

上级：[08 建模与架构探索](./README.md)

相关：[BUS 在解决什么问题](../01-overview/problem-statement.md)、[BUS 分类框架](../01-overview/taxonomy.md)、[仲裁、顺序性与 Backpressure](../02-fundamentals/arbitration-ordering-backpressure.md)、[位宽、时钟、Burst 与延迟](../02-fundamentals/width-clock-burst-latency.md)、[带宽、延迟、利用率与拥塞](../05-performance-debug/bandwidth-latency-utilization.md)

## 这页在回答什么问题

前面每一章的页脚都有"建模启示"，但它们是分散的。这一页把它们收敛成一份可直接编码的参考：建一个 BUS / 互连模型时，应该用哪个统一 transaction 状态机，选哪一层保真度，每个组件要带哪些参数，靠哪几个公式定容量，怎样映射到 SystemC TLM-2.0 / gem5，以及怎样校准。

这页面向的是"做架构探索工具的人"，不是"第一次学 BUS 的人"。如果概念还不熟，先回 [BUS 在解决什么问题](../01-overview/problem-statement.md) 和 [仲裁、顺序性与 Backpressure](../02-fundamentals/arbitration-ordering-backpressure.md)。

## 1. 统一 transaction 状态机

整套 wiki 的多个页脚用了略有差异的状态名（`request_accepted`、`target_service_start`、`request_issue_attempt`……）。建模时应该统一成一条权威状态机，所有 counter、trace、事件和断言都挂在它上面。

```text
issue_attempt        master 想发，握手尚未完成
  -> request_accept    地址/控制被互连接收（!= 完成）
  -> arbiter_grant     在某个共享资源上获得服务机会
  -> service_start     目标 slave/controller 开始处理
  -> data_beat × N     每一拍数据传输（读或写）
  -> response_generate slave 产生 response（含 error 编码）
  -> response_consume  master 接收并匹配回原请求
  -> completion_visible 软件可见的完成（writeback / interrupt / cache 可见）
```

每个转移上挂着一个"等待原因"，这才是性能藏身处：

| 状态转移 | 阻塞它的资源 / 条件 | 对应可观测量 |
| --- | --- | --- |
| issue_attempt → request_accept | input queue 满、下游 backpressure | master VALID 高 / READY 低 |
| request_accept → arbiter_grant | 共享点争用、QoS 低、优先级 starvation | arbiter wait cycle、grant 历史 |
| arbiter_grant → service_start | bridge / CDC / width adapter 固定延迟 | bridge latency、adapter 拆分计数 |
| service_start → data_beat | slave 服务时间、DDR row miss、APB wait | service time 分布、wait state |
| data_beat → response_generate | 服务完成、写语义闭环 | beat counter、burst 剩余拍数 |
| response_generate → response_consume | return path 争用、RREADY/BREADY 低、response FIFO 满 | response wait、FIFO occupancy |
| response_consume → completion_visible | completion writeback、interrupt、cache 可见性 | completion latency、interrupt 分布 |

**最关键的一条规则：`request_accept` 和 `completion_visible` 永远是两个事件，不能合并。** 一旦把一次访问压成"延迟 N 拍后完成"的单事件，就丢掉了 outstanding、排队、回压和长尾——而这些正是架构探索要回答的东西。

## 2. 三层保真度（fidelity tiers）

"选哪一层抽象"是建模工具的第一决策。wiki 各页反复说的"只关心 latency/bandwidth 就折叠 X，关心功能就保留 Y"，本质就是下面三层（对应 SystemC TLM-2.0 的 LT/AT 与 cycle-accurate）：

| 层级 | 保留什么 | 折叠什么 | 误差量级 | 适合回答 |
| --- | --- | --- | --- | --- |
| **L0 容量估算 (analytic / LT-loose)** | 端点连接、aggregate 带宽、平均延迟 | 仲裁、排队、顺序、回压全部折叠成系数 | 稳态 ±20%~50%，瞬态不可信 | "这条路够不够宽"的粗筛 |
| **L1 近似时序 (AT, approximately-timed)** | 统一状态机、per-resource busy、outstanding 计数、仲裁粒度、FIFO 深度、service-time 分布 | 逐 bit payload、信号级编码、slave 内部算法 | 吞吐 ±5%~15%，尾延迟趋势可信 | 架构探索主力：选拓扑、定 outstanding/FIFO、QoS 权衡 |
| **L2 周期精确 (cycle-accurate / RTL)** | 信号级握手、精确编码、每拍仲裁决策、协议状态空间 | 几乎不折叠 | 对齐 RTL | 协议验证、最终签核、L1 校准基准 |

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

**DDR / Memory Controller**：不在 BUS 模型内展开，作为一个带 service-time 分布的特殊 slave 接入；其内部 tRCD/tRP/tRAS、page policy、command scheduling 交给 [RAM Wiki 内存控制器章](../../../RAM/wiki/06-memory-controller/README.md)。BUS 模型只需在边界保留：请求大小、读写方向、地址（决定 row hit/miss）、QoS。

## 5. 定量主干

带宽与延迟的基础公式已在 [位宽、时钟、Burst 与延迟](../02-fundamentals/width-clock-burst-latency.md) 给出，这里不重复，只补上 wiki 里缺失但建模必需的一条核心关系。

**Little's Law（吞吐—延迟—并发的桥）**

```text
平均在飞 transaction 数  =  吞吐(事务/秒)  ×  平均延迟(秒)
```

它把"延迟隐藏"和"吞吐"定量连起来，是给 outstanding 深度和 FIFO 定容量的唯一硬约束：

```text
要在延迟 L 下打满带宽 B(字节/秒)，每笔搬 S 字节：
  所需 outstanding ≈ (B × L) / S          ← bandwidth-delay product
```

推论，建模工具应该能自动报警的情形：
- `outstanding 上限 < B×L/S` → 这条路**被并发度卡死，不是被带宽卡死**。加宽 datapath 无效，要加 outstanding 槽 / ID 数 / FIFO 深度。
- outstanding 长期顶到上限且 service 仍有空闲 → 瓶颈在 return path 或 slot 回收，不在 slave。

**服务时间模型（L1 计费）**
```text
total_cycles = fixed_cycles + beat_count / service_rate + wait_cycles
beat_count   = ceil(payload_bytes / data_width_bytes)   （窄传输/未对齐/跨边界会增大）
```
`wait_cycles` 不是常数，而是上面五张图在该时刻的排队结果——这正是要靠仿真而非闭式公式求解的部分。

## 6. 映射到建模框架

把统一状态机映射到主流框架，概念就能直接落到 API：

| 本 wiki 状态机 | SystemC TLM-2.0 | gem5 |
| --- | --- | --- |
| L0/L1 粗粒度 | `b_transport`（LT，阻塞，带 delay 注解） | atomic / `AtomicSimpleCPU` 风格 |
| request_accept | `nb_transport_fw(BEGIN_REQ)` | `sendTimingReq` / `recvTimingReq` |
| arbiter_grant + service | 模块内部建模（payload 的 extension 带属性） | crossbar / `XBar` 仲裁 + `Packet` |
| response_generate | `nb_transport_bw(BEGIN_RESP)` | `sendTimingResp` |
| response_consume | `END_RESP` | `recvTimingResp` |
| backpressure | `TLM_UPDATED` / 返回 false 阻塞 | `recvReqRetry` / `sendRetryReq` |
| 地址/属性 | generic payload + extensions | `Packet` 的 `Request` 字段 |

要点：TLM-2.0 的 4 个 phase（BEGIN_REQ / END_REQ / BEGIN_RESP / END_RESP）天然对应"请求—响应分离"。**不要用 LT 的 `b_transport` 去研究争用和尾延迟**——那等于用第 2 节的 L0 层回答 L1 问题。

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

可接受误差带：L1 模型稳态吞吐对齐到 ±10% 通常够用于选型；尾延迟看趋势是否同向，绝对值可以更宽。对不上时，**先怀疑五张图里漏建了哪一张**，而不是去调系数。

## 8. 最危险的简化（反模式清单）

把散落各页的告警收敛成一张表，建模时逐条自查：

| 反模式 | 后果 | 正确做法 |
| --- | --- | --- |
| 把访问建成"延迟 N 拍后完成"单事件 | 丢掉 outstanding / 排队 / 回压 / 尾延迟 | 用第 1 节统一状态机，至少分 accept 与 complete |
| 用协议名直接推性能（"AXI 就高并发"） | 高估或低估系统 | 协议名只当默认参数来源，用角色/拓扑/能力校准 |
| 只给链路一个 aggregate 带宽 | 看不到 per-master 饿死、热点 slave、尾延迟 | 保留 per-master / per-slave / 仲裁点状态 |
| 合并 request accept 与 response complete | outstanding、回压、长尾全消失 | 永远两个事件 |
| 丢掉顺序图 | 解释不了"快请求被慢请求挡住"、hang | 显式建同 master/同 ID 保序与 barrier 边界 |
| FIFO 做深当成解决拥塞 | 只是把拥塞可见位置推远 | 持续拥塞要看注入>服务，深 FIFO 不治本 |
| 用 LT/`b_transport` 研究争用 | 用 L0 层回答 L1 问题 | 争用/尾延迟用 AT 层 |

## 一句话理解

建一个能支撑架构探索的 BUS 模型，等于：选定 L1 保真度，把每笔 transaction 建成一条"请求—响应分离"的统一状态机，让它在地址/仲裁/数据/响应/顺序五张资源图上流动，用 Little's Law 给并发资源定容量，再用 RTL/硬件 counter 分四步校准——任何把 accept 和 complete 合并、或只留一个带宽数字的简化，都会让模型在尾延迟和 hang 上失真。
