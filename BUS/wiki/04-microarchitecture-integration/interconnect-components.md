# 互连组件与数据路径分解

上级：[04 微架构与系统集成](./README.md)

相关：[BUS 在解决什么问题](../01-overview/problem-statement.md)、[Arbitration、Ordering 与 Backpressure](../02-fundamentals/arbitration-ordering-backpressure.md)、[AXI、AHB、APB 对比](../03-on-chip-protocol-families/axi-ahb-apb-comparison.md)、[AXI Crossbar 案例卡](../06-scenarios-case-studies/axi-crossbar-case-card.md)

## 这页在回答什么问题

片上 BUS 互连不是协议接口的简单拼接，而是一条由 decode、route、arbitrate、buffer、adapt 和 response 组成的事务路径。评估互连时，核心问题不是“有没有 crossbar”，而是每个事务经过哪些组件、在哪个组件排队、哪个组件决定顺序、哪个组件把回压扩散到上游。

本页把互连拆成可建模的组件边界。这样做的目的有两个：一是让性能瓶颈能落到具体队列、端口或仲裁点；二是让功能语义能落到具体责任方，例如 decode miss 谁返回错误、burst 被谁切分、response 被谁合并。

## 从事务路径看互连

一次 read transaction 可以被拆成下面的路径：

```text
master
  -> request input buffer
  -> address decoder
  -> route selection
  -> output arbiter
  -> width / clock / protocol adapter
  -> slave
  -> response buffer
  -> return route
  -> master
```

write transaction 还要额外考虑 address path、data path 和 response path 是否共用队列。AXI 这类多 channel 协议把这些路径拆开后，提高了并发上限，也引入了新的建模责任：地址与数据要在目标侧重新配对，response 要按 ID 或 ordering 规则回到正确 master。

| 路径位置 | 主要责任 | 建模时要记录 |
| --- | --- | --- |
| input buffer | 接收 master 请求，吸收短期突发 | 深度、是否按 ID/目标分队列、满时回压方式 |
| decoder | 把地址映射到目标端口或错误路径 | 地址窗口、优先级、decode latency、decode miss 行为 |
| route selection | 决定请求走哪条内部链路 | 路由粒度、是否支持并行路径、是否保序 |
| arbiter | 多个请求争用同一出口时决定顺序 | 仲裁策略、QoS 输入、饥饿保护、抢占边界 |
| adapter | 处理宽度、时钟、协议或 burst 差异 | 转换规则、额外 buffering、是否拆分 transaction |
| return path | 把 response/data 送回发起方 | 匹配键、返回带宽、错误传播、释放条件 |

## Address Decoder：把地址空间变成路径选择

decoder 的设计动机是把全局地址空间压缩成目标端口选择。它不仅决定“访问谁”，还决定 decode miss、重叠窗口、alias 和安全隔离如何处理。

| 设计点 | 取舍 | 错误建模的后果 |
| --- | --- | --- |
| 单级 decoder | 延迟低，适合目标数量少的互连 | 目标增多后组合路径变长 |
| 分层 decoder | 容易配合层级互连和局部地址段 | decode miss 可能需要跨层返回 |
| 可编程窗口 | 支持 boot remap、device relocation | 需要建模初始化时序和锁定状态 |
| 固定窗口 | 逻辑简单，验证边界清楚 | 灵活性低，SKU 变化时改 RTL 成本高 |

decoder 还承担错误路径责任。一个 unmapped access 不能悬空；它要么被本层互连转换成 DECERR/SLVERR 类 response，要么被路由到 default slave。建模时要明确错误由哪一级产生，以及错误 response 是否消耗 return path 带宽。

## Arbiter：把共享点变成顺序

arbiter 的设计动机是让多个 master 能共用出口、slave 或内部链路。它把并发请求压成一个可执行顺序，因此它是 latency jitter、fairness 和 QoS 的主要来源。

| 仲裁策略 | 适合场景 | 代价 |
| --- | --- | --- |
| fixed priority | debug、实时中断、低延迟控制路径 | 低优先级路径需要饥饿保护 |
| round robin | 多 master 带宽共享 | 单个高优先级流不会自动获得更低延迟 |
| weighted round robin | CPU、DMA、display 等流量比例可控 | 权重配置和验证状态空间增加 |
| deadline / QoS aware | 实时显示、音频、网络收发 | 需要 QoS 信号可信，且更难做形式化覆盖 |

arbiter 不是孤立组件。若它后面的 slave 或 adapter 回压，仲裁结果可能保持不变，导致队头事务阻塞后续事务。模型要记录仲裁发生在 request 进入前、进入后，还是 output 可用后；这决定等待时间统计和 starvation 判断。

## Mux、Demux 与 Crossbar：连接能力不是免费并发

mux/demux 负责把多个输入连接到多个输出。shared bus、bus matrix 和 crossbar 的差别，不是命名层级，而是同一周期内可以建立多少条不冲突路径。

| 结构 | 并发能力 | 设计收益 | 成本 |
| --- | --- | --- | --- |
| shared bus | 单一共享传输 | 面积小、控制简单、容易观察 | master 数量增加后带宽被串行化 |
| bus matrix | 多输入多输出，但共享若干内部点 | 比 shared bus 更容易支持局部并行 | 仲裁点和阻塞关系不直观 |
| full crossbar | 不同 input/output 可并行 | 高并发、适合多 master 多 slave | 面积、布线、验证复杂度上升 |

crossbar 也不会自动消除阻塞。两个 master 访问同一个 slave 时仍要仲裁；一个 slave 的 return path 变慢时，read data 仍可能占住 buffer；若内部实现按目标端口分队列，访问 A 的慢事务未必阻塞访问 B，若按 master 单队列实现，则慢事务可能造成 head-of-line blocking。

## FIFO 与 Buffer：用空间换时序、突发和解耦

FIFO 的设计动机不是“缓存一点数据”这么简单，而是把两个节奏不同的边界解耦：master 突发与 slave 消化速度、宽总线与窄外设、快时钟域与慢时钟域、request path 与 response path。

| FIFO 位置 | 解决的问题 | 需要暴露给模型的参数 |
| --- | --- | --- |
| ingress FIFO | master 突发进入互连时的短期吸收 | 深度、几乎满阈值、是否按目标隔离 |
| egress FIFO | slave 或 adapter 前的节奏转换 | backpressure 触发点、是否保序 |
| CDC FIFO | 时钟域 crossing | 写读时钟比、同步延迟、满空判断 |
| response FIFO | read data / write response 返回 | 匹配规则、释放顺序、错误优先级 |

buffer 会改变可观察行为。它可以提升吞吐，也可能掩盖下游拥塞，让上游在若干周期后才感知 stall。建模时不能只写“有 buffer”，而要写出深度、排队粒度和满时传播路径。

## Adapter：转换协议时也在转换语义

adapter 包括 width adapter、clock bridge、protocol bridge、burst splitter、ID remapper 和 attribute mapper。它们的共同点是：输入事务和输出事务不再一一等价。

| 转换类型 | 典型变化 | 风险点 |
| --- | --- | --- |
| width adaptation | 一个宽 beat 拆成多个窄 beat，或多个窄 beat 合并 | byte lane、WSTRB、read-modify-write |
| clock crossing | request/response 被 CDC FIFO 重新节拍化 | 延迟分布、满空状态、reset 顺序 |
| protocol bridge | AXI 转 APB、AHB 转 APB 等 | outstanding 收缩、burst 终止、错误映射 |
| ID remap | 内部 ID 空间小于 master ID 空间 | slot 耗尽、response 匹配、ordering 约束 |
| attribute map | cacheable、bufferable、secure、QoS 被重写或丢弃 | 软件语义偏差、安全边界破坏 |

adapter 是性能结论最容易漂移的位置。AXI master 发出 16-beat burst，不代表外设侧也看到 16-beat burst；上游支持多个 outstanding，不代表 bridge 后面还有同样的并发窗口。

## 回压如何扩散

互连建模必须描述 backpressure 的扩散路径。一个 slave 变慢时，影响范围取决于队列和仲裁点的放置。

| 队列设计 | 慢 slave 对其他目标的影响 | 建模判断 |
| --- | --- | --- |
| 每 master 单队列 | 慢目标可能阻塞同 master 后续访问其他目标 | 需要建模 head-of-line blocking |
| 每目标队列 | 慢目标主要阻塞访问同目标的流 | 需要建模目标队列深度 |
| 每 ID/source 队列 | 不同事务流更容易并行 | 需要建模 ID 分配和 slot 上限 |
| 共享 response FIFO | 慢返回或大 read data 可能阻塞其他 response | 需要建模 return path 带宽 |

回压不是只沿 request path 传播。read data path、write response path、CDC FIFO、width adapter 内部队列都可能反向影响 request 接收能力。若模型只看 master 到 slave 的正向路径，就会低估 stall。

## 例子：DMA 写 APB 外设

考虑一个 DMA 通过 AXI interconnect 写一个 APB 外设寄存器。软件看到的是“DMA 写寄存器”，硬件路径里却至少发生了地址 decode、出口仲裁、AXI 到 APB 转换、写响应返回。

| 阶段 | 发生的事件 | 组件责任 | 建模状态 |
| --- | --- | --- | --- |
| T0 | DMA 发出 AXI AW/W | ingress buffer 接收地址与数据 | `fifo_push`、master outstanding +1 |
| T1 | 地址命中 APB window | decoder 选择 bridge 出口 | `decode_done`、目标端口 = APB bridge |
| T2 | CPU debug port 也在访问同一 bridge | arbiter 选择一个请求进入 bridge | `arbiter_grant`、未获 grant 的请求排队 |
| T3 | AXI write 被 bridge 转成 APB setup/access | protocol adapter 收缩 outstanding，拆掉 burst 语义 | `adapter_split`、APB transaction active |
| T4 | APB 外设拉低 PREADY | bridge 无法完成 access | bridge egress 队列占用，回压可能传回 AXI |
| T5 | APB 完成写入并给出 PSLVERR/OK | bridge 映射成 AXI BRESP | `response_match`、错误映射 |
| T6 | DMA 接收 B response | return path 释放 slot | `response_release`、master outstanding -1 |

这个例子说明，协议名不能替代路径模型。AXI 侧可以发起 outstanding，APB 侧却一次只执行一个 access；AXI 侧的 burst 能力也可能在 bridge 处被拆掉或禁止。若模型只记录“DMA 访问 APB”，就会漏掉 arbiter 排队、bridge slot、PREADY stall 和 BRESP 映射。

## 常见误解

| 误解 | 更准确的判断 |
| --- | --- |
| crossbar 等于无阻塞 | crossbar 只增加不冲突路径的并发；同一 slave、共享 return path 或共享 buffer 仍会阻塞 |
| buffer 只会提升吞吐 | buffer 也会增加排队延迟，并把下游拥塞延后暴露给上游 |
| protocol adapter 只是信号转换 | adapter 会改变 outstanding、burst、ordering、错误映射和 attribute 传播 |

## 一条路径的建模清单

建模一条互连路径时，至少回答这些问题：

| 问题 | 为什么重要 |
| --- | --- |
| 地址在哪里 decode，decode miss 谁负责 | 决定错误 response 和访问覆盖 |
| 哪些 master 在同一仲裁点竞争 | 决定 latency jitter 和 QoS 设计 |
| 队列按 master、目标、ID 还是 channel 划分 | 决定 head-of-line blocking |
| burst 在哪里被拆分或合并 | 决定带宽、WSTRB 和 completion 语义 |
| width/clock/protocol 在哪里转换 | 决定额外延迟和 backpressure 边界 |
| response 如何匹配回发起方 | 决定 outstanding 上限和释放条件 |
| 错误是否占用正常返回路径 | 决定错误风暴下的系统可恢复性 |

## 一句话理解

互连组件不是静态方框，而是把 transaction 逐步改写、排队、转换和释放的一组路径责任。

## 建模启示

互连组件要按“路径责任”建模，而不是按图纸上的方框名建模。decoder 负责地址到路径的映射，arbiter 负责共享点顺序，mux/crossbar 负责连接能力，FIFO 负责节奏解耦，adapter 负责语义转换，return path 负责完成与释放。

性能模型要把每个共享点、队列深度、仲裁策略、转换延迟和回压方向显式列出。事件模型要能表达 `decode_done`、`arbiter_grant`、`fifo_push/pop`、`adapter_split/merge`、`response_match/release` 这些状态变化。功能模型要把 decode miss、错误返回、attribute 传播、ID 匹配、burst 拆分和 completion 条件落到具体组件。只有这样，后续分析 bridge、CDC、DMA、DDR controller 或 debug path 时，才能解释“为什么这里慢”以及“为什么这里不能只看协议名”。
