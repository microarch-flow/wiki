# TileLink 概览

上级：[03 片上总线协议族](./README.md)

相关：[AXI / AHB / APB 对照](./axi-ahb-apb-comparison.md)、[Coherent Bus vs Non-Coherent Bus](./coherent-bus-vs-noncoherent-bus.md)、[AXI vs TileLink 对照](../06-scenarios-case-studies/axi-vs-tilelink-comparison.md)

## 这页在回答什么问题

TileLink 相比 AXI/AHB/APB 这类更常见的 AMBA 协议族，提供了什么不同的组织思路，为什么它在 RISC-V、Chisel 和生成式 SoC 生态里更常见。

## TileLink 强调参数化互连框架

如果 AXI 是**标准化的乐高积木**——形状固定、种类丰富、全世界的乐高都能互拼，那 TileLink 更像 **3D 打印的模块化组件**——你可以根据需要定制每个零件的参数，但需要在同一个打印生态里才能无缝组合。

TileLink 是定义通道、消息与事务规则的协议族；Rocket Chip 的 Diplomacy 是可用于协商节点能力和生成互连的框架，两者不是同一个东西。协议提供不同层级，生成框架可按节点支持能力组合简单外设、uncached 和 coherence 路径。

所以比较 TileLink 和 AXI，不应该只问“谁更快”。更有效的问题是：系统是在拼接成熟商用 IP，还是在生成一套可参数化 fabric；互连需要的是标准生态兼容，还是节点能力可组合和一致性语义可裁剪。

容易误解：TileLink 是 AXI 的替代品。实际上，它更像一套适合特定 SoC 生成生态的事务框架；对外接商用 IP 时仍可能通过 bridge 转成 AXI、APB 或其他协议。

## TileLink 有复杂度层次

TileLink 可以按能力层次理解：

| 层次 | 主要用途 | 大致语义 |
|---|---|---|
| TL-UL | 简单 uncached 访问 | 类似低复杂度 request/response，适合寄存器和简单 memory-mapped 访问 |
| TL-UH | 支持更高能力的 uncached 访问 | 可支持更丰富的 burst、source 并发和高吞吐路径 |
| TL-C | coherent 访问 | 加入 cache coherence 相关 acquire/probe/release/grant 等语义 |

这个表只给出架构入口，不替代 TileLink 规范。关键点是：TileLink 把“从简单外设到 coherent memory”的能力放在同一协议家族中，并通过参数决定节点到底支持哪些操作。一个 peripheral 不需要承担 TL-C 的 coherence 状态；一个 cacheable agent 则需要参与更复杂的 coherent transaction。

容易误解：TileLink 节点都一样复杂。实际上，TileLink 的重要价值正是让不同节点承担不同能力，复杂度可以随节点角色裁剪。

## 角色和能力比信号名更重要

TileLink 语境里，client、manager、source、sink 这些角色比“总线两端接了什么信号”更关键。Client 发起请求，manager 管理地址范围和响应；source ID 用来区分 client 侧未完成事务，sink ID 在某些返回和授予路径中帮助匹配后续状态。

TL-UL 和 TL-UH 使用 A/D 请求与响应；TL-C 还使用 B/C/E 完成一致性事务：

| 通道 | 方向 | 典型消息和职责 |
|---|---|---|
| A | client → manager | Get、Put、Acquire 请求 |
| B | manager → client | Probe，请求检查或撤销权限 |
| C | client → manager | ProbeAck/ProbeAckData；也可主动 Release |
| D | manager → client | AccessAck/Data、ReleaseAck、Grant/Data |
| E | client → manager | GrantAck，携带 sink 确认授予 |

普通 Get 的 `source` 在请求尚未获得响应期间必须唯一，包括首个 D 响应 beat 被接受的那个周期。TileLink v1.8.1 将消息的首 beat 握手定义为消息 received；因此四拍 AccessAckData 的 D0 握手后，下一周期可用同一 source 发新的 Get。旧响应的其余 beat 仍按 D 通道消息顺序接收，接收方必须保留旧 burst 的上下文。实现也可保守地等到末拍后才复用。规范依据为 [SiFive TileLink v1.8.1](https://sifive.cdn.prismic.io/sifive/7bef6f5c-ed3a-4712-866a-1a2e0c6b7b13_tilelink_spec_1.8.1.pdf) §5.1、§6.4。

TL-C 的 Grant/Data 使用 sink 标识授予，client 发 E GrantAck，manager 还须等待相应 Grant 数据全部传送与确认后回收授予状态。B Probe 由 C ProbeAck/Data 应答；它不是软件完成队列。

这和 AXI 的 master/slave、ID/outstanding 有相似目标：都要解决 request/response 匹配和并发状态。但 TileLink 更强调在生成时把能力参数描述清楚，例如某个 manager 支持哪些 opcode、最大 transfer size、是否支持 acquire、是否 cacheable、是否要求 FIFO ordering。

从建模视角看，TileLink 的节点参数就是协议能力边界。一个节点是否支持并发、是否支持 coherence、是否需要按 FIFO 返回、是否允许特定 size 或 mask，都会直接决定性能和正确性。

容易误解：TileLink 难点在记通道名。实际上，难点在节点能力和 transaction 类型是否匹配；信号只是这些能力的载体。

## Coherence 是 TileLink 的重要扩展点

TileLink-C 能表达 cache coherence 相关事务，例如获取权限、探测其他 cache、释放或授予 cache line 状态。它面向的是 03 章前一页讨论的共享内存可见性问题：多个 cacheable agent 访问同一份 memory 时，系统必须维护 ownership、副本和可见顺序。

这和 TL-UL/TL-UH 的普通 uncached transaction 不同。Uncached path 只需要把 request 送到 manager，再把 response 返回 client；coherent path 还要处理权限状态、probe、release、grant 和可能的数据干预。

因此，TileLink 的优势不是“默认提供一致性”，而是能在同一生态中表达从 non-coherent 到 coherent 的能力阶梯。系统仍然要按路径决定哪些节点参与 coherence，哪些只做 device/MMIO 或 uncached memory access。

容易误解：用了 TileLink 就自动解决 cache coherence。实际上，只有参与 coherent domain、并正确配置节点能力和内存属性的路径才承担一致性语义。

## 和 AXI 的比较边界

AXI 的优势是生态兼容和高性能通用接口。CPU、DMA、DDR controller、accelerator、commercial IP、verification IP 和 EDA 生态对 AXI 支持广泛，跨公司和跨 IP 集成更直接。

TileLink 的优势是生成式组合。对 RocketChip、Chipyard、Chisel/RISC-V 一类设计，TileLink 可以把节点能力、地址映射、参数协商和一致性边界放进生成流程。它减少的是“手工拼接口”的成本，而不是自动消除所有验证成本。

一个构造对比：

| 维度 | AXI | TileLink |
|---|---|---|
| 生态 | 商用 IP 和工具链广泛 | RISC-V/Chisel/生成式 SoC 生态强 |
| 组织方式 | 标准接口能力明确 | 节点能力参数化 |
| Coherence | 通过特定扩展或其他一致性协议承担 | TL-C 可表达一致性事务 |
| 集成边界 | bridge/IP 集成成熟 | 生成流程内组合更自然 |
| 主要风险 | 能力强但集成状态复杂 | 参数配置和节点能力误配 |

这张表不应该被读成“谁更先进”。AXI 更适合成熟 IP 拼装和广泛兼容，TileLink 更适合可生成、可裁剪、协议能力随节点配置的 SoC 设计。

## 一句话理解

TileLink 的核心价值是把简单访问、高能力 uncached 访问和 coherent 访问放进同一套参数化事务框架里；它不是为了替代所有总线，而是服务生成式 SoC 里的能力裁剪和节点组合。

## 建模启示

建模 TileLink 时，不要只写“这是 TileLink”。模型要记录每个节点的能力参数：支持哪些 transaction 类型，最大 transfer size，source ID 数量，是否要求 FIFO ordering，是否支持 acquire/probe/release/grant，地址范围由哪个 manager 负责。

对 TL-UL/TL-UH 路径，模型重点接近普通 request/response：请求队列、source 匹配、manager 服务时间、response 返回和 backpressure。对 TL-C 路径，模型必须增加 coherence 状态：cache-line permission、probe、release、grant、ownership 和可能的数据转发。

与 AXI 和 PCIe 对比时，要先把能力对齐。TileLink 的 source 在首响应 beat 接受后的下一周期可重用，并不代表旧 burst 数据已经收完；AXI 可以有多个同 ID 在途事务，其响应匹配与同 ID 顺序规则另行约束，不能照搬 TileLink source 生命周期。PCIe non-posted Request 的 Tag 需跟踪该请求的 Completion，直到数据完整或终止状态结束，见 [PCIe Completion](../../../PCIE/wiki/04-data-path-dma-interrupts/pcie-read-completion-latency.md)。比较应落到端点能力、队列、返回匹配、coherence 范围和 bridge 成本上。

如果系统边缘通过 bridge 连接 AXI/APB，模型还要保留协议转换带来的 latency、error mapping、burst/size/mask 转换和 ordering 改变。TileLink 的参数化优势只在边界被正确建模时才会反映到系统行为里。
