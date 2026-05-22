# Row Locality、Return Path 与 AXI 体验

上级：[04 微架构与系统集成](./README.md)

相关：[RAM Row Locality 与 Page Policy 深化](../../../RAM/wiki/04-system-architecture/row-locality-page-policy-deep-dive.md)、[AXI Burst、对齐与边界](../03-on-chip-protocol-families/axi-burst-alignment-boundary.md)、[AXI 到 DDR Controller 的路径](./axi-to-ddr-controller-path.md)、[Read/Write Combine 与 Bus Turnaround](./read-write-combine-turnaround.md)

## 这页在回答什么问题

AXI master 评价一次读访问时，看到的是 AR 被接收后多久返回 R data，以及 R channel 是否连续。DDR controller 评价同一批请求时，看到的是 row hit、row miss、bank conflict、read/write switch 和 data return buffer。两边的体验不是一一对应。

本页讨论两个层级如何叠加：DDR 侧 row locality 决定数据能否平滑产出，AXI return path 决定数据能否平滑回到 master。row locality 好但 return path 拥塞，master 仍会看到抖动；return path 空闲但 row conflict 多，RVALID 也会出现空洞。

## Row Locality 改变 DDR 出数节奏

row locality 指连续访问是否命中已经打开的 DRAM row。row hit 可以省掉 activate/precharge 代价；row miss 或 row conflict 会引入额外命令和等待。

| 访问形态 | DDR 侧行为 | AXI R channel 体验 |
| --- | --- | --- |
| 连续线性读，命中 open row | 连续 read command，数据节奏平滑 | RVALID 更容易连续 |
| stride 跨 row | 频繁 activate/precharge | R data 中间出现空洞 |
| 多 master 打同一 bank 不同 row | bank conflict | tail latency 上升 |
| 多 bank/channel 分散 | bank-level parallelism 提升 | 多个 burst 可交错返回 |
| row-hit 优先调度 | 局部吞吐提升 | row-miss request 可能等待更久 |

row locality 的设计取舍在于吞吐与公平。controller 优先服务 row-hit 能提高有效带宽，但会让不命中当前 row 的请求等待；按到达顺序更公平，却可能浪费 DDR 阵列效率。

## Return Path 决定数据能否顺利回流

DDR 准备好数据后，还要经过 controller return buffer、interconnect return arbiter、response FIFO、master input buffer 和 AXI R channel。任何一级拥塞都会改变 master 看到的返回节奏。

| Return path 位置 | 可能瓶颈 | 可见症状 |
| --- | --- | --- |
| controller read data buffer | 多 master read data 同时返回 | DDR 已出数，但无法立刻释放到 AXI |
| interconnect return arbiter | 多个 slave/DDR port 返回同一 master 或多个 master | R channel 间歇性空洞 |
| response FIFO | FIFO 深度不足或被慢 master 占住 | backpressure 传回 controller |
| ID reorder / matching | 多 ID 返回需要匹配和排序 | 某些 ID 的 response 被延后 |
| master RREADY | master 无法及时接收 | 下游反压扩散到 return path |

return path 的建模动机是把“DDR 出数”与“master 收到数”分开。性能计数器若只看 DDR data beats，可能判断 memory 侧很好；但 master 侧 R channel 仍可能因为 return arbiter 或 FIFO 争用而抖动。

## Row Locality 与 Return Path 的四种组合

| DDR row locality | Return path | Master 体验 | 解释 |
| --- | --- | --- | --- |
| 好 | 空闲 | R data 连续，latency 稳定 | 理想顺序读 |
| 好 | 拥塞 | DDR 吞吐高，但 R channel 被打散 | return arbiter/FIFO 是瓶颈 |
| 差 | 空闲 | RVALID 有空洞，tail latency 高 | row conflict 或 turnaround 是瓶颈 |
| 差 | 拥塞 | 吞吐和 tail 都差 | DDR 侧与回流侧双重限制 |

这个矩阵比单看 DDR bandwidth 更有诊断价值。若 DDR bandwidth 高但某个 master R latency 差，优先看 return path；若 DDR bandwidth 本身低且 row miss 多，先看 address mapping、stride 和 scheduler。

## 例子：两个 Master 的 Read Return 争用

CPU 和 DMA 同时读 DDR，CPU 是随机小读，DMA 是长 burst 顺序读。

| 阶段 | DDR 侧 | Return path | AXI master 观察 |
| --- | --- | --- | --- |
| T0 | DMA 顺序读命中 open row | DMA R data 连续进入 return buffer | DMA RVALID 平滑 |
| T1 | CPU 随机读进入队列 | row miss，需要额外命令 | CPU 等待增加 |
| T2 | CPU read data 与 DMA burst data 接近同时返回 | return arbiter 分配带宽 | CPU R data 可能再等 |
| T3 | DMA master 短暂 RREADY 低 | return FIFO 被占 | CPU 返回也被间接影响 |
| T4 | controller 切换到 CPU row | CPU 数据返回 | CPU latency 呈现尾部尖峰 |

这个例子说明 CPU 的慢不一定只来自 row miss，也可能来自 DMA 的 return path 占用。DMA 的顺不一定只来自 DDR row hit，也可能来自更高 return priority 或更深 FIFO。

## AXI Burst 与 R Channel 体验

AXI burst 的发出形态和返回形态可能不同。

| AXI 侧请求 | DDR / return path 处理 | 体验 |
| --- | --- | --- |
| 单个长 burst | 被拆到多个 row 或 bank | burst 内部 R beat 可能不连续 |
| 多个短 burst | controller 可重排为 row-hit 序列 | 返回顺序受 ID/ordering 约束 |
| 多 ID outstanding | 多条请求并行等待 | R data 可能交错，需要 master 能接收 |
| narrow / unaligned read | 额外 lane/beat 处理 | 有效 R bandwidth 下降 |
| high priority read | scheduler 和 return arbiter 优先 | 其他 master tail latency 上升 |

master 端若只看 outstanding 数量，会误判系统。outstanding 多只能填满等待窗口，不能保证 DDR 持续出数，也不能保证 return path 有足够带宽。

## 诊断方法

| 观察 | 更可能的原因 | 下一步检查 |
| --- | --- | --- |
| DDR bandwidth 高，某 master R latency 高 | return path 争用 | return arbiter、R FIFO、RREADY、ID matching |
| RVALID 周期性空洞 | row conflict 或 read/write turnaround | row miss counter、scheduler、turnaround 事件 |
| 长 burst 内部返回不连续 | burst 跨 row/bank 或 return path 被抢占 | address mapping、burst boundary、return priority |
| 小随机读尾延迟高 | row miss + queueing | bank conflict、row-hit priority、age limit |
| 多 master 同时读时才抖 | return arbiter 或 shared FIFO | per-master return bandwidth 和 QoS |

诊断时要把“数据生产侧”和“数据回流侧”分开。DDR 侧看 row hit/miss、bank conflict、turnaround；AXI 侧看 R channel utilization、RREADY、return FIFO、response arbitration 和 per-ID latency。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| row locality 好就等于 AXI 体验好 | return path 拥塞仍会打散 R data |
| RVALID 不连续就一定是 DDR 慢 | return arbiter、FIFO、RREADY 都可能制造空洞 |
| outstanding 深就能解决读延迟 | outstanding 只能隐藏等待，不能消除 row conflict 或 return 争用 |
| DDR 吞吐计数器足以解释 master 体验 | 还需要 per-master return latency 和 R channel 观察 |

## 一句话理解

AXI 读体验是 DDR 数据生产节奏和 AXI return path 回流节奏叠加后的结果。

## 建模启示

row locality 与 return path 要分层建模。性能模型要记录 address mapping、row-hit/miss、bank conflict、read/write turnaround、controller read data buffer、return arbiter、response FIFO、R channel bandwidth、RREADY 和 per-master/per-ID latency。功能模型要记录 AXI ID matching、ordering、burst boundary、error response 和 backpressure 传播。

事件模型建议显式表达 `row_hit`、`row_miss`、`bank_conflict_wait`、`read_cmd_issue`、`ddr_data_ready`、`return_fifo_push`、`return_arbiter_grant`、`rvalid_beat`、`rready_stall`、`read_response_done`。这些事件能把“DDR 已出数但 AXI 没收到”和“DDR 本身没出数”区分开。
