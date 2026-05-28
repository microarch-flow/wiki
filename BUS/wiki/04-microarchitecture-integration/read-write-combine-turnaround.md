# Read/Write Combine 与 Bus Turnaround

上级：[04 微架构与系统集成](./README.md)

相关：[AXI 到 DDR Controller 的路径](./axi-to-ddr-controller-path.md)、[Row Locality、Return Path 与 AXI 体验](./row-locality-return-path-axi-experience.md)、[带宽、延迟、利用率与拥塞](../05-performance-debug/bandwidth-latency-utilization.md)

## 这页在回答什么问题

想象一个**单车道双向隧道**——每次只能走一个方向的车。如果来一辆切换一次方向，大部分时间都浪费在"掉头"上。所以隧道管理员会积攒一批同方向的车一起放行，再换方向放另一批。这就是 read/write combine 和 bus turnaround 的本质。

读写混合负载下，系统可能出现一种看似矛盾的现象：总体 DDR 带宽不低（隧道一天通过的车总量不少），但某些 AXI read latency 突然变长（你的车等了好久才轮到你这个方向放行），write response 集中返回（一批写操作被积攒后集中处理），DMA completion 被拖后。

## Read/Write Combine 在换什么

read/write combine 的设计动机是减少方向切换和命令碎片。DDR/PHY/data bus 在读写方向之间切换需要付出时序代价；controller 批量处理同方向请求，可以摊薄这个代价。

| 策略 | 收益 | 代价 |
| --- | --- | --- |
| 连续服务 read queue | 降低 read tail，提升 CPU 读体验 | write queue 可能积压 |
| write drain | 清空 write buffer，避免 overflow | 新 read 等待，read tail 上升 |
| read/write batching | 减少 turnaround 次数 | 单笔请求完成顺序偏离到达顺序 |
| row-hit + direction 优先 | 同时利用 row locality 和方向一致性 | row-miss 或反方向请求等待更久 |
| age threshold | 限制等待时间 | 吞吐低于纯批处理策略 |

这是一个明确 trade-off：controller 用更大的调度窗口和更复杂的状态换吞吐，用请求等待时间的不均匀换方向切换次数减少。

## Turnaround 为什么贵

Turnaround 就像隧道的**换向操作**——不是简单地"换个信号灯"，而是要等最后一辆出方向的车彻底通过（pipeline 清空），确认对面安全（PHY 方向切换、DRAM timing），调整照明和通风方向（data bus tri-state/drive），以及重新校准入口设备（write leveling/read capture）。每次换向都要花好几个时钟周期，这就是为什么 controller 宁可攒一批再切换。

| 切换 | 典型代价 | AXI 可见影响 |
| --- | --- | --- |
| read -> write | 等待 read data drain，切换到写数据发出 | write response 延后或集中返回 |
| write -> read | 等待 write drain / bus direction 切换 | read data 出现空洞，RVALID 不连续 |
| small alternating R/W | 每几笔请求就支付切换成本 | 有效带宽下降，latency 抖动放大 |
| large batching | 切换次数少 | 某一方向请求等待时间变长 |

因此，最差模式不是单纯读，也不是单纯写，而是细碎读写交替且 row locality 差。AXI master 可能认为自己只是发出合理 burst，controller 看到的却是频繁方向切换和 row conflict。

## 对 AXI R/B Channel 的影响

read/write combine 会改变 AXI 返回节奏。

| AXI channel | 现象 | Controller 侧解释 |
| --- | --- | --- |
| R channel | 一段时间无 RVALID，随后连续返回 | controller 从 write drain 切回 read batch |
| B channel | BRESP 批量返回 | 多个 write 被 controller 接收或 drain 后集中释放 |
| AW/W ready | READY 阶段性下降 | write buffer 接近阈值或处于反方向服务 |
| AR ready | read queue 暂时不接收 | read queue 满，或调度窗口保护写队列 |
| latency histogram | 平均值可接受，尾部很长 | batching 和 turnaround 影响 tail |

这类现象容易被误判为 interconnect 仲裁问题。interconnect 可能确实参与排队，但若 R/B 返回呈现方向性批量特征，DDR controller 调度就是必须检查的层级。

## 例子：CPU Read 与 DMA Write 混合

考虑 CPU 发随机小 read，DMA 连续写 frame buffer。

| 阶段 | 输入流量 | Controller 决策 | AXI 侧观察 |
| --- | --- | --- | --- |
| T0 | CPU read 进入 read queue | 优先服务部分 read | CPU read latency 较低 |
| T1 | DMA write 持续进入 write queue | write buffer 积压 | AW/W 仍可被接收 |
| T2 | write queue 达到 drain 阈值 | 切到 write drain | 新 CPU read 开始等待 |
| T3 | DMA write 批量进入 DDR | 吞吐提升，turnaround 减少 | B response 可能集中 |
| T4 | write drain 结束 | 支付 write->read turnaround | R channel 出现空洞后恢复 |
| T5 | CPU read 被批量服务 | read data 连续返回 | CPU 看到尾延迟尖峰 |

这个例子的关键是平均带宽无法解释 CPU tail latency。若只看 DDR 利用率，会认为系统很好；若看 per-master read latency，会发现 write drain 对 CPU 造成周期性等待。

## Completion 为什么会被拖后

DMA completion/writeback 常是小写流量，但它可能排在大数据写之后。

| 场景 | 结果 | 建模点 |
| --- | --- | --- |
| completion 与 data write 共用 AXI ID/port | completion 被 data burst 排队 | writeback 是否有独立 port 或 QoS |
| controller 处于 read batch | completion write 等待 write service | write queue 何时被 drain |
| write buffer 满 | completion 无法进入或延后 response | buffer threshold、backpressure |
| interrupt 早于 completion 可见 | CPU ISR 读到旧状态 | completion visible 先于 interrupt |

这就是“数据已经搬完但软件还没看到完成”的常见来源。completion 的数据量小，不代表它的 latency 小；它要经过同一套 write queue、scheduler、B response 和 cache/coherence 可见性规则。

## 建模 Read/Write Combine

一个可用模型不需要完整复刻 DDR controller，但要表达几个关键状态：

| 状态 | 作用 |
| --- | --- |
| read_queue_depth / write_queue_depth | 判断是否进入 read batch 或 write drain |
| current_direction | 当前服务 read 还是 write |
| turnaround_pending | 切换方向前的不可服务窗口 |
| write_drain_threshold | write queue 到达何值触发 drain |
| max_batch / age_limit | 限制某方向独占时间 |
| row_hit_rate | 与 direction batching 共同影响服务时间 |
| return_buffer_depth | 影响 R/B 返回节奏 |

如果模型只用一个平均 DDR service time，就会看不到读写交替造成的尾延迟。需要至少有方向、队列和切换代价三个状态。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| DDR 带宽够就不会抖 | 带宽高不代表每个 read 的 tail latency 稳定 |
| write response 集中说明 AXI 写侧有问题 | 也可能是 controller write drain 后集中释放 |
| 小 completion 不会被大 data write 影响 | 共用 write queue/port 时，小写也会排队 |
| 公平调度一定更好 | 公平降低尾延迟，但可能牺牲 row locality 和吞吐 |

## 一句话理解

read/write combine 用局部等待换 DDR 总吞吐，turnaround 是读写方向切换必须支付的物理和控制代价。

## 建模启示

read/write combine 要按方向状态机建模。性能模型要记录 read/write queue、current direction、batch size、write drain threshold、turnaround latency、row-hit rate、return buffer、R/B response release 和 per-master latency。功能模型要记录 write completion 定义、barrier 可见点、completion writeback 顺序、timeout 和错误 response。

事件模型建议显式表达 `read_enqueue`、`write_enqueue`、`read_batch_start`、`write_drain_start`、`turnaround_start`、`turnaround_done`、`read_data_release`、`write_resp_release`、`completion_write_visible`。这些事件能解释为什么总体吞吐正常时，某个 AXI master 的 read tail、DMA completion 或 B response 仍然出现明显抖动。
