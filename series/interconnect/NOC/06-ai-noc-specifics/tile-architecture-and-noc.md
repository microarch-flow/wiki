# Tile Architecture And NOC

上级：[06 AI NOC Specifics](./README.md)

相关：[NI Network Interface Design](../05-system-integration/ni-network-interface-design.md)、[NOC Meets Memory System](../05-system-integration/noc-meets-memory-system.md)

## 这页在回答什么问题

这页回答：在 AI 芯片里，tile 为什么必须被当成 NoC 建模的一等公民，以及 tile 的 compute、local SRAM、NI 组织怎样反推网络需求。

## tile 不是普通 endpoint

一个 AI tile 通常至少包含：

- compute engine
- local SRAM / scratchpad
- SRAM controller / local scheduler
- NI
- 若干 data/control port

因此它不是“收到包就结束”的被动终点，而是：

- 会主动发起读写流量
- 会因为本地 SRAM 组织不同而改变 NoC 压力
- 会因为 compute pipeline 节奏不同而改变注入和弹出节奏

## tile 的三个 NoC 相关上限

从网络视角看，tile 至少有三个上限：

- 能以多快速度注入数据
- 能以多快速度弹出并消费数据
- 能以多高并发度在本地 SRAM 与 compute 之间周转数据

这三者里任一项过弱，都可能先于 router 成为系统瓶颈。

## local SRAM 直接决定流量形状

SRAM 容量影响的是“要不要频繁进网”，bank/port 影响的是“进了网之后能不能及时消化”。

典型后果：

- 容量大：更多本地复用，NoC 总流量下降
- bank 多、端口够：compute 与 NI 更容易并行
- bank 少、端口紧：ejection blocked 和 local conflict 更容易放大

所以 tile 设计与 NoC 设计从来不是解耦的。

## 注入和弹出通常不对称

很多分析喜欢把 tile 视作“对称端口”。真实系统里更常见的是：

- 注入侧受数据准备、read port、packetization 约束
- 弹出侧受reassembly、write port、bank arbitration 约束

尤其是 fan-in 强的模式里，弹出侧更容易先出问题。

## tile-to-tile forwarding 很重要

AI 芯片里经常有一种非常关键的优化：

- 数据不回全局 memory
- 而是从 producer tile 直接 forward 给 consumer tile

这会让 NoC 的价值不只是“连外部 memory”，而是成为片上 pipeline 的延伸部分。此时 tile 端口、邻近链路和 local FIFO 的设计都会直接影响 pipeline 是否稳。

## 为什么 DSL 必须描述 tile 内部参数

如果 DSL 只描述 router 和 link，而不描述 tile：

- 无法知道本地复用率
- 无法知道 NI 有效带宽
- 无法知道 compute/communication 比例
- 无法判断某个 stall 是网络问题还是本地 SRAM 问题

因此 tile 必须是架构 DSL 的一等对象，而不是网络旁边的注释。

## 一句话理解

AI NoC 的端点不是抽象主机，而是带计算、存储和调度行为的 tile；不把 tile 建进去，就很难得到真实的 NoC 结论。

## 建模启示

tile 模型至少要暴露：

- compute throughput / phase timing
- local SRAM capacity
- bank count / port count
- NI injection / ejection queue
- 每张网络对应的端口能力

只有这样，模型才能解释为什么某些工作负载明明 link 没满，却已经被 endpoint 端限制住了。
