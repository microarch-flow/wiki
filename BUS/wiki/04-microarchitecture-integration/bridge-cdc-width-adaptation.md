# Bridge、CDC 与 Width Adapter

上级：[04 微架构与系统集成](./README.md)

相关：[位宽、时钟、Burst 与延迟](../02-fundamentals/width-clock-burst-latency.md)、[互连组件与数据路径分解](./interconnect-components.md)、[分层总线与协议分工](../03-on-chip-protocol-families/hierarchical-bus-and-protocol-roles.md)、[AHB-Lite 与 APB 深入理解](../03-on-chip-protocol-families/ahb-lite-and-apb-deep-dive.md)

## 这页在回答什么问题

Bridge 不是简单地把两根管子焊到一起——它更像一个**国际机场的转机大厅**：旅客（transaction）从国际航班（AXI 高速主干）下来，要换乘国内小飞机（APB 低速外设），中间要过海关（协议转换）、调整时区（时钟域跨越）、把大行李箱换成随身背包（位宽适配）。

这三种转换的共同风险是：国际航班允许的行李规格，国内小飞机不一定能装。建模时必须把 bridge 当成一个有排队区、有安检状态、有登机条件的转机环节，而不是零延迟的”穿墙术”。

## Bridge 改变了什么

一个 bridge 至少会改变下面几类语义：

| 转换对象 | 典型变化 | 模型必须记录 |
| --- | --- | --- |
| protocol | AXI outstanding 到 APB single access，AHB pipeline 到 APB setup/access | 并发窗口、phase 映射、response 生成 |
| clock | fast domain request 进入 slow domain | CDC FIFO 深度、同步延迟、reset 关系 |
| width | 128-bit master 访问 32-bit slave | beat 拆分/合并、byte lane、WSTRB |
| burst | INCR burst 被拆成多个 single access | burst 边界、子事务数量、完成聚合 |
| ordering | 多 ID、多请求在 bridge 处收缩 | slot 分配、返回顺序、head-of-line blocking |
| error | downstream timeout、PSLVERR、decode miss 被映射成 upstream response | 错误来源、错误优先级、是否释放 outstanding |

bridge 的设计动机是隔离复杂度。高速主互连不该为每个低速外设实现 APB 节拍；CPU 和 DMA 也不该直接理解每个外设的时钟域。代价是 bridge 成为语义收缩点：吞吐、延迟、错误和可观察顺序都可能在这里改变。

## 协议转换：能力收缩比连线更重要

以 AXI 到 APB bridge 为例，AXI 侧有独立 AW/W/B channel，可以有 outstanding，可以带 burst；APB 侧是 setup/access 两阶段，一次只服务一个 transfer。bridge 必须把上游的并发请求收缩成下游可执行的串行访问。

| AXI 侧输入 | Bridge 内部动作 | APB 侧输出 | 风险 |
| --- | --- | --- | --- |
| AW + W 同时到达 | 缓存地址和数据，等待 slot | PSEL=1 的 setup phase | 地址和数据配对错误 |
| 多个 write outstanding | 分配内部 slot 或直接 backpressure | 单个 APB access 队列 | outstanding 被 bridge 深度限制 |
| AXI burst | 拆成多个 APB access，或拒绝不支持的 burst | 多次 setup/access | completion 需要等全部子访问完成 |
| APB PSLVERR | 映射成 AXI BRESP/RRESP | B/R response 返回 master | 错误粒度可能从子访问聚合到整笔事务 |

协议转换的取舍在于：保留更多上游能力，需要更多 buffer、slot 和验证状态；快速收缩能力，逻辑更简单，但会降低吞吐并制造回压。低速配置寄存器路径更偏向简单收缩；DMA 到存储路径若引入过强收缩，会直接伤害带宽。

## CDC：跨时钟域是节奏转换

CDC（Clock Domain Crossing）就像两个**不同时区的办公室之间传递文件**——北京办公室早上 9 点开始工作，纽约办公室晚上 9 点才上班。CDC bridge 的目标不是”让文件飞过去”，而是保证文件在跨时区传递时不丢失、不错乱、不在时差间隙里被遗忘。

| CDC 方案 | 适合路径 | 代价 |
| --- | --- | --- |
| async FIFO | 有持续流量的 data 或 request path | 需要深度规划，满空判断影响回压 |
| toggle / pulse handshake | 低频控制事件 | 吞吐低，每次传输有固定同步延迟 |
| multi-flop sync | 单 bit 状态信号 | 不适合多 bit 数据或 transaction payload |
| credit-based crossing | 长距离或高吞吐链路 | credit 状态和恢复逻辑更复杂 |

CDC 的性能不是固定加几个周期就能描述。fast-to-slow 方向会因为 slow domain 消化速度形成 FIFO 积压；slow-to-fast 方向可能低延迟返回，但仍受同步器和 response FIFO 影响。reset 也要建模：一个时钟域已出 reset，另一个时钟域还没出 reset 时，bridge 是否接收请求、是否返回错误、是否保持 backpressure，都会影响 boot path 和 debug path。

## Width Adapter：数据粒度改变会影响语义

位宽适配看起来是 beat 数量变化，本质上是 byte lane 和 completion 粒度变化。

| 场景 | 转换行为 | 建模风险 |
| --- | --- | --- |
| 128-bit 写 32-bit 外设 | 一个上游 beat 拆成最多 4 个下游 beat | WSTRB 映射、寄存器副作用、子写顺序 |
| 32-bit 读 128-bit SRAM | 可能只读一个 narrow beat，也可能读宽 beat 后选 lane | 额外带宽消耗、read-modify-read 假象 |
| 非对齐写 | 拆成跨 word 或跨 beat 的多个访问 | byte enable、边界错误、partial write |
| narrow write 到宽 memory | 可能触发 read-modify-write | 写放大、原子性和错误聚合 |

位宽适配的核心 trade-off 是硬件复杂度与带宽效率。严格按访问粒度下发，语义清楚但下游 beat 数增加；合并窄访问可以提升效率，却需要等待、对齐和 side-effect 判断。MMIO 路径不应随意合并写入，因为多个寄存器写可能有顺序或触发语义。

## Burst 拆分与完成聚合

bridge 处理 burst 时要回答两个问题：下游是否支持同样的 burst 语义，若不支持，上游事务何时算完成。

| 上游事务 | 下游行为 | completion 判断 |
| --- | --- | --- |
| 4-beat AXI write 到 APB | 4 次 APB write | 全部子写完成后返回 B |
| 8-beat AXI read 到窄 SRAM | 拆成更多窄读 | 收齐并重组后按 RLAST 返回 |
| burst 中第 3 个子访问错误 | 停止后续或继续执行取决于 bridge 设计 | 错误映射到整笔 response 或对应 beat |
| crossing 4KB 边界 | bridge 应拒绝或拆分前保持协议规则 | 不能生成违反下游/上游规则的访问 |

completion 聚合会增加隐藏状态。bridge 需要知道哪些子事务已经发出、哪些已经返回、错误是否已经发生、上游 response 是否可以释放。这个状态直接决定 timeout、flush、reset 和错误恢复的复杂度。

## 例子：AXI 写 APB 寄存器

下面用一个 64-bit AXI master 写 32-bit APB 寄存器的路径说明 bridge 如何制造额外延迟和状态。

| 阶段 | AXI 侧 | Bridge 状态 | APB 侧 | 关键建模点 |
| --- | --- | --- | --- | --- |
| T0 | AWVALID/WVALID 到达 | 捕获地址、数据、WSTRB | idle | AW/W 是否同时到达，slot 是否可用 |
| T1 | AWREADY/WREADY 拉高 | 判断只需写低 32-bit lane | PSEL=1, PENABLE=0 | byte lane 映射 |
| T2 | 等待 B response | APB access active | PSEL=1, PENABLE=1 | PREADY 决定停留周期 |
| T3 | 等待 B response | 若 PREADY=0，保持 access | APB stall | backpressure 是否影响下一笔 AXI |
| T4 | BVALID 返回 | PSLVERR 映射为 BRESP | access done | response_match、slot release |

若上游 64-bit 写覆盖两个 32-bit APB 寄存器，bridge 还要决定是否拆成两次 APB write。若这两个寄存器有 side effect，拆分顺序和错误处理就不只是性能问题，而是功能语义。

## 回压和错误路径

bridge 需要把下游不可用转换成上游可理解的 backpressure 或错误。选择不同，系统行为完全不同。

| 下游状态 | Bridge 选择 | 上游可见结果 |
| --- | --- | --- |
| 下游暂时 busy | 保持 READY 低或填满后回压 | 上游 stall，事务未被接收 |
| 下游长期不响应 | timeout 后生成错误 response | 上游事务完成但带错误 |
| 下游返回错误 | 映射成协议 response | 软件或 master 可区分失败 |
| bridge 内部 FIFO 满 | 阻止新请求进入 | upstream latency 增加 |

错误路径必须释放资源。一个 timeout 若只产生错误但不释放 slot，后续事务会被永久阻塞；一个 reset 若清空子事务但不通知上游，上游会等待永不返回的 completion。bridge 模型要把错误生成和资源释放放在同一个状态机里。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| bridge 只是 glue logic | bridge 是协议、时钟、位宽、错误和完成语义的转换边界 |
| CDC 过形式验证就结束 | 形式验证证明跨域安全，不等于吞吐、reset、timeout 和回压已经被建模 |
| width adapter 只影响带宽 | byte lane、WSTRB、side effect 和 partial write 都可能改变功能结果 |
| 上游支持 burst/outstanding 就能保持性能 | bridge 的 slot、FIFO 和下游协议会重新定义有效并发窗口 |

## 一句话理解

bridge 把两个 BUS 世界接起来，也把上游能力压缩成下游能执行的状态机。

## 建模启示

bridge 必须按状态机建模，而不是按连线建模。性能模型要记录输入队列、CDC FIFO、bridge slot、下游 service time、burst 拆分数量、response 聚合点和 backpressure 传播方向。功能模型要记录协议 phase 映射、byte lane/WSTRB、attribute 传播、错误映射、timeout、reset 行为和 completion 释放条件。

事件模型建议显式表达 `bridge_accept`、`cdc_push/pop`、`width_split/merge`、`child_txn_issue`、`child_txn_done`、`error_map`、`response_release`。这些事件决定 bridge 是否只是增加固定延迟，还是会改变 ordering、吞吐、错误恢复和软件可见行为。
