# Bridge、CDC 与 Width Adapter

上级：[04 微架构与系统集成](./README.md)

相关：[位宽、时钟、Burst 与延迟](../02-fundamentals/width-clock-burst-latency.md)、[互连组件与数据路径分解](./interconnect-components.md)、[分层总线与协议分工](../03-on-chip-protocol-families/hierarchical-bus-and-protocol-roles.md)、[AHB-Lite 与 APB 深入理解](../03-on-chip-protocol-families/ahb-lite-and-apb-deep-dive.md)

## 这页在回答什么问题

Bridge 不是简单地把两根管子焊到一起——它更像一个**国际机场的转机大厅**：旅客（transaction）从国际航班（AXI 高速主干）下来，要换乘国内小飞机（APB 低速外设），中间要过海关（协议转换）、经过跨时钟域接口、把大行李箱换成随身背包（位宽适配）。

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

## CDC：跨域采样、同步和流控

CDC（Clock Domain Crossing）的输入是源域的状态、事件或数据；输出是目标域能够安全使用的对应信息。对于无已知固定相位关系的两个时钟，源信号可能在目标触发器的 setup/hold 采样窗口内变化。触发器可能进入亚稳态，其输出稳定所需时间不能由普通逻辑仿真准确决定。CDC 既要解决采样可靠性，也要保证数据不丢失、不重复和不混合。

| 信息 | 实现方式 | 必要条件与限制 |
| --- | --- | --- |
| 稳定单 bit 电平 | 目标域两级或多级触发器同步器 | 源值保持足够长；级数和布局按可靠性目标设计，只降低亚稳态传播概率，不能保证概率为零 |
| 短脉冲或一次性事件 | toggle 或请求/确认握手 | 脉冲可能完全落在两个目标采样沿之间而漏采；必须满足方案规定的事件间隔、确认和复位约束 |
| 多 bit 数据和持续事务 | 异步 FIFO；低频数据也可用保持数据稳定的跨域握手 | 不能把普通 payload 的每一位各自同步后直接拼成一个字；不同位的采样延迟可能不同 |

异步 FIFO 用写时钟写入、读时钟读出。数据存入可由两域安全访问的存储体；常见设计将读、写指针编码为 Gray code，再通过同步器送入对方时钟域，分别生成本地的 empty/full 判断。指针的跨域同步有延迟，读取已经发生后，写侧也不一定立刻看到空位。Gray code 不是免约束的多 bit 总线：仍需遵守具体实现的指针更新、跨域路径延迟及位间偏差约束。

`credit` 是流控信息，表示接收侧授予的空间或配额；它本身不解决亚稳态。credit 若跨域，仍需通过异步 FIFO、握手或适合该信号的安全 CDC 机制传递。复位释放及两侧 FIFO 初始化也需要明确协调；一侧仍在 reset 时能否接受流量取决于接口契约。

### 一个确定性的边沿例子

这是构造的仿真口径，不是某个 FIFO IP 的固定延迟。假设写时钟上升沿为 `0, 6, 12, … ns`，读时钟上升沿为 `1, 11, 21, … ns`。FIFO 初始为空，复位已完成；写指针用两级读域同步器，读侧用同步后的指针组合判断 empty。只写一次，指针在跨域期间保持稳定；抽象模型规定读请求接受后一个读周期输出有效数据，且读端一直请求。

| 时刻 | 输入和动作 | 读侧可见结果 |
| ---: | --- | --- |
| 6 ns | 写域在上升沿接受一个数据，随后更新写指针 | empty 仍为 1 |
| 11 ns | 读域第一级采到已稳定的写指针 | 第二级仍是旧值，empty 为 1 |
| 21 ns | 第二级更新；组合 empty 判断随后变化 | empty 变为 0，数据可请求读取 |
| 31 ns | 读域上升沿接受读请求 | FIFO 弹出一项 |
| 41 ns | 按本例的一个读周期数据延迟输出 | 读数据有效 |

这里 21 ns 的 empty 变化发生在该沿之后，因此最早在 31 ns 的下一个读沿接受请求。实际 IP 的 empty 与数据有效时间由其同步级数、标志寄存器和读模式决定，不能直接套用这张表。若源边沿靠近目标采样窗口，实际首级可能延后稳定；确定性周期模型只表达选定的抽象延迟、队列和事件，**不模拟亚稳态发生概率或可靠性指标**。需要检查不同相位、延迟与复位情形；电气可靠性还需要基于器件、时序约束和实现评估。

参考：[Cummings，SNUG 2002 异步 FIFO 设计](https://www.researchgate.net/publication/252160343_Simulation_and_Synthesis_Techniques_for_Asynchronous_FIFO_Design)、[AMD XPM_FIFO_ASYNC 读写与标志延迟](https://docs.amd.com/r/2025.2-English/ug1353-versal-architecture-ai-libraries/XPM_FIFO_ASYNC)、[AMD Gray-code CDC 路径约束](https://docs.amd.com/r/en-US/ug949-vivado-design-methodology/Constraints-on-Individual-CDC-Paths)。

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
| burst 中第 3 个子访问错误 | 是否停止后续**下游**子访问取决于设备副作用及 bridge 契约 | 上游 AXI 仍须收齐写数据并返回 B，或返回完整 R burst 和正确 RLAST；将错误映射到响应 |
| crossing 4KB 边界 | 跨界逻辑请求需在发出 AXI 地址前拆分；不应把非法跨界 burst 作为合法请求 | 不能生成违反下游/上游规则的访问 |

completion 聚合会增加隐藏状态。bridge 需要知道哪些子事务已经发出、哪些已经返回、错误是否已经发生、上游 response 是否可以释放。这个状态直接决定 timeout、flush、reset 和错误恢复的复杂度。

## 例子：AXI 写 APB 寄存器

下面是构造的单时钟例子：64-bit AXI master 向对齐的 32-bit APB 寄存器写一个 beat，`AWADDR=0x1000`、`AWSIZE=2`、`AWLEN=0`、`WLAST=1`、`WSTRB=0x0F`。假设 bridge 在同一个上升沿接收 AW 和 W，再发起一次 APB 写；`BREADY` 在响应阶段为 1。表中每一行描述对应上升沿的采样，注明“沿后”的状态在该沿之后生效。

| 上升沿 | AXI 侧 | Bridge 与 APB 侧 | 结果 |
| --- | --- | --- | --- |
| T0 | `AWVALID=WVALID=1`，`AWREADY=WREADY=0` | APB 空闲 | 尚未握手；发送方保持地址、数据、`WSTRB` 与 `WLAST` 稳定 |
| T1 | AW 与 W 均为 `VALID=READY=1` | 沿后保存地址和数据，开始 APB setup：`PSEL=1, PENABLE=0` | 两个 AXI 通道各接受一次；本例 AW 和 W 同拍接受 |
| T2 | 等待 B | 沿前仍是 setup；沿后进入 access：`PSEL=1, PENABLE=1` | setup 结束；该沿尚不按 access 接受 `PREADY` |
| T3 | 等待 B | access：`PREADY=0` | APB 等待；保持 `PSEL/PENABLE`、地址和写数据稳定 |
| T4 | 沿前 `BVALID=0` | access：`PREADY=1`；采样 `PSLVERR`，沿后生成 `BVALID` 与映射后的 `BRESP` | APB 子写在该沿完成；此前 AW 和全部 W 已接受 |
| T5 | `BVALID=BREADY=1` | APB 已完成 | B 在该沿握手；释放本例写 outstanding |

B 不会在 T4 因沿后才拉高的 `BVALID` 被提前计为握手；若 `BREADY=0`，bridge 必须保持 `BVALID/BRESP` 稳定直到握手。AXI 允许 AW 与 W 不同拍接受，本表只展示其中一种排列；APB `PREADY` 也可使 access 持续更多拍。实际跨时钟的 bridge 还要在相应时钟域和 CDC 延迟下重新安排这些事件。

若上游 64-bit 写覆盖两个 32-bit APB 寄存器，bridge 还要决定是否拆成两次 APB write。若这两个寄存器有 side effect，拆分顺序和错误处理就不只是性能问题，而是功能语义。

## 回压和错误路径

bridge 需要把下游不可用转换成上游可理解的 backpressure 或错误。选择不同，系统行为完全不同。

| 下游状态 | Bridge 选择 | 上游可见结果 |
| --- | --- | --- |
| 下游暂时 busy | 保持 READY 低或填满后回压 | 上游 stall，事务未被接收 |
| 下游长期不响应 | 若实现支持 timeout 收尾，可合成错误响应 | 上游协议响应完整且被消费后才完成；迟到下游响应必须隔离或排空 |
| 下游返回错误 | 映射成协议 response | 软件或 master 可区分失败 |
| bridge 内部 FIFO 满 | 阻止新请求进入 | upstream latency 增加 |

错误路径必须明确资源生命周期。timeout 检测本身不终止原事务：若 bridge 合成上游响应，须隔离、排空或标记丢弃迟到的下游响应，防止重复完成或误配给新事务。上游写仍须收齐 W，上游读仍须返回约定 beat 数。reset 的作用范围、两侧协调及在途请求如何失败、排空或随整个接口复位，必须由系统契约定义；仅清空内部 FIFO 会使未复位的上游永久等待。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| bridge 只是 glue logic | bridge 是协议、时钟、位宽、错误和完成语义的转换边界 |
| CDC 过形式验证就结束 | 形式验证只覆盖所建模的属性和假设；还需检查电气约束、复位、吞吐与回压 |
| width adapter 只影响带宽 | byte lane、WSTRB、side effect 和 partial write 都可能改变功能结果 |
| 上游支持 burst/outstanding 就能保持性能 | bridge 的 slot、FIFO 和下游协议会重新定义有效并发窗口 |

## 一句话理解

bridge 把两个 BUS 世界接起来，也把上游能力压缩成下游能执行的状态机。

## 建模启示

bridge 必须按状态机建模，而不是按连线建模。性能模型要记录输入队列、CDC FIFO、bridge slot、下游 service time、burst 拆分数量、response 聚合点和 backpressure 传播方向。功能模型要记录协议 phase 映射、byte lane/WSTRB、attribute 传播、错误映射、timeout、reset 行为和 completion 释放条件。

事件模型建议显式表达 `bridge_accept`、`cdc_push/pop`、`width_split/merge`、`child_txn_issue`、`child_txn_done`、`error_map`、`response_release`。这些事件决定 bridge 是否只是增加固定延迟，还是会改变 ordering、吞吐、错误恢复和软件可见行为。
