# AXI 到 DDR Controller 的路径

上级：[04 微架构与系统集成](./README.md)

相关：[RAM 控制器、并行度与页策略](../../../RAM/wiki/04-system-architecture/controller-parallelism-page-policy.md)、[AXI 与 DMA 的系统接口](./axi-dma-system-interface.md)、[Read/Write Combine 与 Bus Turnaround](./read-write-combine-turnaround.md)、[Row Locality、Return Path 与 AXI 体验](./row-locality-return-path-axi-experience.md)

## 这页在回答什么问题

AXI master 和 DDR controller 看到的是**两种完全不同的世界**。AXI master 觉得自己在发快递（AR/AW/W 发出，R/B 返回），DDR controller 看到的却是一个**巨大图书馆的管理问题**：这本书在哪个书架（bank）、哪一排（row）、哪个格子（column）？书架正好开着吗（row hit）？需要先关上一排再打开另一排吗（precharge + activate）？同时有人在还书有人在借书怎么调度（read/write scheduling）？

AXI 侧的订单排得整整齐齐，不代表图书管理员能按这个顺序一本本取——他会根据书架位置重新优化取书路线。

## 路径分解

从 AXI master 到 DDR data 返回，一条 read path 可以拆成：

```text
AXI master
  -> interconnect arbitration
  -> address decode / remap
  -> DDR controller ingress queue
  -> request reorder / scheduler
  -> address mapping: channel / rank / bank / row / column
  -> DRAM commands: activate / read / precharge
  -> PHY / DFI / memory device
  -> read data return buffer
  -> AXI R channel back to master
```

write path 还要考虑 W data queue、write combining、write drain、B response 生成和 read/write turnaround。AXI 上的一笔 burst，进入 controller 后可能变成多条 DRAM command；多笔 AXI request 也可能因为落在同一 open row 而被 controller 连续服务。

| 路径位置 | 主要责任 | 模型需要记录 |
| --- | --- | --- |
| ingress queue | 接收 AXI read/write request | 队列深度、read/write 分队列、QoS |
| address mapper | 把地址拆成 channel/bank/row/column | mapping 规则、interleave 粒度 |
| scheduler | 决定执行顺序 | row-hit 优先、QoS、age、fairness |
| command generator | 生成 ACT/RD/WR/PRE 等命令 | timing 约束、bank 状态 |
| data buffer | 暂存 write data / read data | buffer 深度、方向切换 |
| return path | 生成 AXI R/B response | ID 匹配、返回带宽、response 聚合 |

## AXI Burst 与 DRAM Command 不一一对应

AXI burst 表达的是事务侧连续访问，DDR command 表达的是阵列侧资源操作。两者之间要经过地址映射和 controller 调度。

| AXI 现象 | DDR 侧可能发生的事 | 可见后果 |
| --- | --- | --- |
| 一个长 INCR burst | 跨 row、bank 或 page boundary 后被拆成多个 command 片段 | latency 中间出现台阶 |
| 多个相邻 AXI burst | 落在同一 row，被 controller 合并调度 | 吞吐好、返回集中 |
| 两个 master 交错访问 | 地址映射到同一 bank | bank conflict，尾延迟变长 |
| read/write 交替 | controller 批量读或批量写 | 单个请求等待方向切换 |
| 小而离散的 request | row locality 差，命令开销占比高 | 有效带宽低 |

设计取舍在于：controller 可以重排请求提高阵列效率，但 AXI master 看到的单笔 latency 会更不稳定。强保序能降低 jitter，却可能浪费 row locality 和 write combining 机会。

## Address Mapping 决定 Row Locality

地址到 channel/rank/bank/row/column 的映射，会影响哪些请求可以并行，哪些请求会冲突。

| Mapping 目标 | 收益 | 风险 |
| --- | --- | --- |
| channel interleave | 多 channel 分摊带宽 | 小步长访问可能跨 channel 增加返回乱序 |
| bank interleave | 提高 bank-level parallelism | bank queue 和调度更复杂 |
| row locality | 连续访问命中 open row | 随机访问 row conflict 成本高 |
| page coloring / partition | 给实时流或关键流隔离资源 | 软件和硬件配置复杂 |

同样的 AXI burst，在不同 address mapping 下可能表现完全不同。一个 DMA 线性搬运若落在连续 row，吞吐稳定；若 stride 让每个 request 都打到不同 row，controller 要频繁 activate/precharge，AXI 侧看到的 R latency 会抖动。

## Scheduler：吞吐、公平和尾延迟的取舍

DDR controller scheduler 不是简单 FIFO。它会在 row-hit、read/write batching、QoS、age 和 starvation protection 之间取舍。

| 调度偏好 | 收益 | 代价 |
| --- | --- | --- |
| row-hit first | 提高阵列效率和吞吐 | row-miss 请求可能等待更久 |
| read priority | 降低 CPU/DMA read latency | write queue 积压，后续 write drain 抖动 |
| write drain | 批量清空 write buffer | read 请求可能突然尾延迟上升 |
| QoS aware | 保护 display/audio/realtime 流 | 配置错误会饿死低优先级流 |
| age-based fairness | 限制 starvation | 吞吐可能低于纯 row-hit 策略 |

这就是 AXI 体验会“发飘”的原因。AXI master 看到的是自己的 request 排队时间；controller 优化的是整个 memory device 的效率。两者目标不总是一致。

## Read 与 Write 的返回语义不同

AXI read 的完成由 R data 返回决定；AXI write 的完成由 B response 返回决定。但 DDR 侧 write 可能先进入 controller write buffer，再由 scheduler 选择时机写入 DRAM。

| 路径 | AXI 侧完成 | DDR/controller 侧含义 | 建模风险 |
| --- | --- | --- | --- |
| read | R beat / RLAST 返回 | 数据已从 memory path 返回 | return path buffer 会影响 latency |
| write | B response 返回 | controller 接收并满足其完成定义 | B 可能早于真正 DRAM array 持久化，取决于系统定义 |
| posted-like write | 上游较早释放 | 下游继续 drain | 错误或 power loss 语义需要定义 |
| write followed by read same address | 需要 read-after-write 正确性 | controller/ordering 处理要保证可见性 | 模型要记录 hazard |

write response 不是简单“DDR 写完了”的同义词。系统要定义 B response 的完成点：写入 controller buffer、写入 memory controller domain、还是确认到 DRAM 阵列。不同定义会影响 barrier、power-down、reset 和错误恢复。

## 例子：两个 AXI Master 访问 DDR

考虑 CPU 和 DMA 同时访问 DDR：CPU 发随机小 read，DMA 发长 burst write。

| 阶段 | 事件 | Controller 侧行为 | AXI 可见结果 |
| --- | --- | --- | --- |
| T0 | CPU read 进入 read queue | 随机 row，row-hit 率低 | 单笔 latency 不稳定 |
| T1 | DMA write burst 进入 write queue | write buffer 快速积累 | AW/W 可被接收 |
| T2 | scheduler 先服务若干 CPU read | read priority 降低 CPU 等待 | write response 可能延后 |
| T3 | write buffer 达到阈值 | controller 进入 write drain | 新 CPU read 等待 turnaround |
| T4 | DMA write 批量写入 DDR | 提升总吞吐 | CPU read tail latency 上升 |
| T5 | controller 切回 read | 支付 turnaround 成本 | read 返回出现抖动 |

这个例子说明，AXI 总带宽不低时，单个 read 仍可能出现尾延迟。瓶颈不是 AXI master 发不出请求，而是 controller 为了 DDR 效率改变了服务顺序。

## 错误与 Timeout

DDR 路径的错误不只来自 DRAM device。它可能出现在 address decode、controller queue、ECC、training、refresh、power state 或 timeout 逻辑。

| 错误来源 | AXI 可见结果 | 建模关注点 |
| --- | --- | --- |
| unmapped/remap error | DECERR/SLVERR 类 response | 错误由 interconnect 还是 controller 产生 |
| controller queue timeout | read/write response error 或 hang | timeout 是否释放 slot |
| ECC error | data 返回带错误状态或触发 interrupt | 是否影响 R response、是否有 syndrome |
| DDR not initialized | access timeout 或错误 | boot 阶段可访问性 |
| power/self-refresh state | 等待唤醒或返回错误 | wake latency、低功耗策略 |

错误路径要和 return path 一起建模。read error 需要对应 R response；write error 需要对应 B response 或错误状态；若错误只停在 controller 内部而不上报，AXI master 会看到 hang。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| AXI burst 连续，DDR 就连续服务 | DDR 还受 bank/row/timing/scheduler 约束 |
| DDR 带宽够，AXI latency 就稳定 | scheduler 和 turnaround 会制造尾延迟 |
| write B response 等于数据已在 DRAM 阵列 | 完成点由 controller 和系统语义定义 |
| memory controller 只是协议转换 | controller 是受物理时序约束的调度器 |

## 一句话理解

AXI 到 DDR 的路径，是把通用 transaction 流转换成受 bank、row、timing、turnaround 和 return path 约束的 memory command 流。

## 继续阅读

- 如果你在追 `DMA 如何把 AXI 请求送进内存`：看 [DMA Descriptor Fetch、Data Move 与 Writeback](./dma-descriptor-fetch-data-move-writeback.md)
- 如果你在追 `为什么读写混合时体验发飘`：看 [Read/Write Combine 与 Bus Turnaround](./read-write-combine-turnaround.md)
- 如果你在追 `为什么 DDR 吞吐不差但 AXI 返回不稳`：看 [Row Locality、Return Path 与 AXI 体验](./row-locality-return-path-axi-experience.md)

## 建模启示

AXI 到 DDR controller 要建模成事务流到命令流的转换。性能模型要记录 ingress queue、read/write queue、address mapping、bank/row 状态、scheduler 策略、turnaround、refresh、write drain、return path buffer 和 AXI ID/response 匹配。功能模型要记录 write completion 定义、read-after-write hazard、ECC/error response、timeout、power/self-refresh 状态和 boot 初始化条件。

事件模型建议显式表达 `axi_req_accept`、`ddr_queue_enqueue`、`address_map_done`、`row_hit_or_miss`、`scheduler_pick`、`dram_cmd_issue`、`read_data_return`、`write_buffer_drain`、`axi_response_release`、`ddr_error_report`。这些事件能解释为什么 AXI 请求已经发出，DDR 侧却因为 row conflict、write drain、turnaround 或 return path 队列而改变可见 latency。
