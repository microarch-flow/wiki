# Shared Bus、Bus Matrix 与 Crossbar

上级：[04 微架构与系统集成](./README.md)

相关：[互连组件与数据路径分解](./interconnect-components.md)、[Arbitration、Ordering 与 Backpressure](../02-fundamentals/arbitration-ordering-backpressure.md)、[AXI Channel、ID 与 Outstanding](../03-on-chip-protocol-families/axi-channel-id-outstanding.md)、[AXI Crossbar 案例卡](../06-scenarios-case-studies/axi-crossbar-case-card.md)

## 这页在回答什么问题

想象一个办公楼的会议室预约系统——这就是 shared bus、bus matrix 和 crossbar 解决的问题：多个部门（master）如何共享有限的会议室（slave）。

**Shared bus** 就像整栋楼只有一个前台——所有预约都排在同一个队列里，一次只能安排一间会议室。**Bus matrix** 就像每层楼有自己的前台——同一层的人共用一个前台，但不同楼层可以同时预约。**Full crossbar** 就像每个部门和每间会议室之间都有直线电话——理论上所有不冲突的预约都能同时进行。

它们的差别不是”新旧代际”，而是同一时间能建立多少条不冲突的通道，以及一个卡住的预约会影响多大范围。

## 三种组织方式的核心差别

| 组织方式 | 同周期连接能力 | 共享点 | 主要收益 | 主要代价 |
| --- | --- | --- | --- | --- |
| shared bus | 一次只服务一条全局传输 | 全局 bus、全局 arbiter | 面积小、控制简单、波形容易解释 | 所有流量串行化，慢事务影响全局 |
| bus matrix | 多个 master 可同时访问不同 slave，但内部仍有共享点 | 分组 arbiter、局部通道、共享 return path | 局部并发，成本低于 full crossbar | 阻塞关系依赖实现，分析复杂 |
| full crossbar | 不同 input/output 可并行连接 | 每个输出端口、return path、buffer | 并发上限高，适合多 master 多 slave | 面积、布线、时序、验证状态增加 |

判断互连能力时，不能只看框图上的名字。一个标为 crossbar 的实现，如果每个 master 只有单输入队列，也可能出现 head-of-line blocking；一个 bus matrix 若按目标分队列，对某些流量组合可能接近 crossbar 的表现。

## Shared Bus：简单性来自全局串行化

shared bus 的设计动机是把互连控制做到最小。全局只有一条传输路径和一个主要仲裁点，协议观察、错误定位、低功耗关断和形式验证都更直接。

| 适合场景 | 为什么适合 |
| --- | --- |
| boot ROM、低速配置外设 | 流量低，latency 抖动不会影响主性能 |
| 小 MCU 或控制岛 | master 数量少，面积和验证成本更敏感 |
| debug 或 maintenance path | 可观察性和确定性比吞吐更重要 |

代价是所有请求共享同一个时间轴。一次慢 APB 访问、一次等待中的 flash read、一次长 burst，都可能阻止无关 master 访问其他 slave。模型里必须把 shared bus 当成单 server queue，而不是把每个 slave 独立建模。

| 周期 | 事件 | 全局影响 |
| --- | --- | --- |
| T0 | CPU 请求 SRAM | 获得 bus |
| T1 | DMA 请求 MMIO | 等待 CPU 完成 |
| T2 | CPU SRAM 返回 | bus 释放 |
| T3 | DMA MMIO 进入低速 bridge | bus 被低速 access 占住 |
| T4..T8 | MMIO 等 PREADY | CPU 新的 SRAM 请求也被阻塞 |

这个例子说明 shared bus 的瓶颈不是单个 slave，而是全局服务点。只要一笔事务占住 bus，其他本可并行的访问也会排队。

## Bus Matrix：用局部并发降低全局阻塞

bus matrix 的设计动机是打破“所有请求共用一条路径”的限制，同时避免 full crossbar 的面积和布线成本。它把互连拆成若干输入、输出和局部仲裁点，让访问不同目标的请求可以并行。

| 访问组合 | shared bus | bus matrix |
| --- | --- | --- |
| CPU -> SRAM，DMA -> APB | 串行 | 可能并行，取决于 APB bridge 是否共享入口 |
| CPU -> DDR，display -> DDR | 串行 | 仍在 DDR 出口仲裁 |
| debug -> APB，DMA -> SRAM | 串行 | 可并行，若两条路径不共享内部通道 |
| 两个 DMA -> 同一 SRAM | 串行 | 仍在 SRAM 出口仲裁 |

bus matrix 的核心 trade-off 是“并发关系不再一眼可见”。性能模型要知道哪些 input/output 组合可并行，哪些组合共享内部链路，哪些 response path 会重新合流。验证模型也要覆盖局部阻塞：A 目标的 stall 是否会影响 B 目标，取决于队列按 master、按目标还是按通道划分。

## Crossbar：并发上限高，但热点仍然存在

full crossbar 的设计动机是让不同 master 到不同 slave 的访问尽量并行。它适合多条高吞吐路径同时存在的系统，例如 CPU cluster 访问 DDR、NPU DMA 写 SRAM、display 读 frame buffer、ISP 写 memory。

| 设计点 | 价值 | 成本 |
| --- | --- | --- |
| 每输出端口独立仲裁 | 不同 slave 可并行服务 | 仲裁器数量增加 |
| 每输入/输出多队列 | 降低 head-of-line blocking | buffer 面积和状态增加 |
| ID/source remap | 支持更高 outstanding | response 匹配和错误恢复复杂 |
| QoS/priority per port | 保护实时流 | 配置和验证难度上升 |

crossbar 不等于无限并发。热点 slave 仍是单一服务点；DDR controller、SRAM bank、APB bridge、return data path 都可能成为出口瓶颈。crossbar 只能消除“不相关目标之间的无谓串行化”，不能让同一资源同时服务无限请求。

## 并发矩阵比名称更重要

评估互连组织时，最有用的不是拓扑名称，而是 master/slave 并发矩阵。

| 流量 A | 流量 B | 是否可并行 | 需要检查 |
| --- | --- | --- | --- |
| CPU -> SRAM | DMA -> APB | 可并行或部分并行 | 是否共享 input queue、bridge 入口或 return path |
| CPU -> DDR | NPU -> DDR | 同出口竞争 | DDR port、QoS、read/write turnaround |
| display -> DDR read | ISP -> DDR write | 同控制器竞争 | realtime priority、buffer underflow 风险 |
| debug -> system memory | CPU -> system memory | 可能被限速 | debug path 是否走低优先级入口 |
| DMA -> SRAM bank0 | CPU -> SRAM bank1 | 取决于 bank/port | SRAM 是否多 bank、多 port |

这个矩阵直接决定模型结构。可并行的组合应落在不同 service point；不可并行的组合要共享 queue、arbiter 或 server。若模型只按 slave 建模，可能漏掉共享 return path；若只按 master 建模，可能漏掉同一 slave 热点。

## Ordering 与 Response Path

互连组织越复杂，response path 越不能被当成“原路返回”。crossbar 可以让 request path 并行，但 read data 或 write response 仍要匹配回正确 master。

| 问题 | shared bus | bus matrix / crossbar |
| --- | --- | --- |
| response 匹配 | 顺序由全局传输隐含 | 需要 ID/source、端口或内部 tag |
| 返回顺序 | 更容易保持提交顺序 | 可能按目标、ID 或通道交错 |
| 错误返回 | default slave 或全局错误点 | 错误可能由 decoder、bridge、slave、timeout 多处产生 |
| backpressure | 全局 stall 直观 | 局部 stall 的扩散范围依赖队列结构 |

这也是 bus matrix 和 crossbar 验证成本上升的原因。它们不是只增加连接数量，还增加了“谁先返回、谁释放 slot、谁承受回压”的状态空间。

## 选型问题

| 设计问题 | 倾向 shared bus | 倾向 bus matrix | 倾向 crossbar |
| --- | --- | --- | --- |
| master 数量 | 1 到 2 个低流量 master | 多个 master，但热点有限 | 多个高吞吐 master |
| slave 热点 | 低速外设为主 | 部分 slave 热点明显 | 多个高带宽 slave 需并行 |
| 面积/功耗预算 | 很紧 | 中等 | 可接受较大布线和 buffer |
| latency jitter | 可接受全局等待 | 需要隔离部分等待 | 需要保护关键流 |
| 验证预算 | 希望状态少 | 能覆盖局部并发 | 能覆盖 ID、QoS、response 交错 |

选型的关键不是追求“更高级”，而是把并发能力投到真实流量上。若系统只有一个 DDR 热点，full crossbar 不能消除 DDR 出口竞争；若低速 APB 和高速 SRAM 被 shared bus 串在一起，即使平均带宽够，latency tail 也可能失控。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| bus matrix 是 crossbar 的低配版 | bus matrix 是成本、并发和验证边界的折中，不只是功能裁剪 |
| crossbar 可以解决所有带宽问题 | 同一 slave、同一 memory controller、同一 return path 仍会形成热点 |
| shared bus 只适合很旧的设计 | 控制岛、debug、boot、低速配置路径仍可能选择 shared bus |
| 拓扑名称足以决定性能 | 队列划分、仲裁点、buffer 深度和流量矩阵才决定可观察性能 |

## 一句话理解

shared bus、bus matrix 和 crossbar 的差别，是阻塞范围从全局逐步收缩到局部，但每一次收缩都要付出面积、布线、状态和验证成本。

## 建模启示

互连组织要建模成 service point 和并发矩阵。shared bus 是单一全局 server；bus matrix 是若干局部 server 加共享链路；crossbar 是按输出端口和返回路径组织的多 server 系统。性能模型要记录 master/slave 流量矩阵、可并行组合、热点出口、队列划分、仲裁策略、buffer 深度和 response path 带宽。

功能模型还要记录 ordering、ID/source 匹配、错误来源、decode miss 路径和 slot 释放条件。事件模型建议显式表达 `request_enqueue`、`route_select`、`output_arbiter_grant`、`hotspot_wait`、`response_route`、`slot_release`。只有把拓扑名称展开成这些状态，才能解释为什么某条路径在 shared bus 上被全局拖慢、在 bus matrix 上局部阻塞、在 crossbar 上仍受热点出口限制。
