# AXI 与 DMA 的系统接口

上级：[04 微架构与系统集成](./README.md)

相关：[AXI Channel、ID 与 Outstanding](../03-on-chip-protocol-families/axi-channel-id-outstanding.md)、[AXI Burst、Alignment 与 Boundary](../03-on-chip-protocol-families/axi-burst-alignment-boundary.md)、[Doorbell、Completion 与 Interrupt Flow](./doorbell-completion-interrupt-flow.md)、[IOMMU、SMMU 与 DMA 寻址](./iommu-smmu-dma-addressing.md)、[DMA Wiki 首页](../../../DMA/wiki/README.md)

## 这页在回答什么问题

DMA 接到 AXI 上后，不只是“多了一个 AXI master”。一个 DMA engine 同时有控制面、descriptor fetch、data read、data write、writeback/completion、interrupt/status 等多条路径。它们可能共用 AXI port，也可能拆成多个 AXI master/slave interface；拆分方式会直接决定吞吐、回压、错误归因和软件可见完成时间。

本页关注 DMA 与 AXI 系统接口的建模边界：哪些路径是 CPU 控制 DMA，哪些路径是 DMA 访问 memory，哪些路径负责完成通知，哪些路径会经过 IOMMU/SMMU、cache/coherent fabric、DDR controller 或 APB bridge。

## DMA 至少有四类 BUS 责任

| 责任 | 典型接口 | 发起方 | 主要语义 |
| --- | --- | --- | --- |
| register/control | AXI-Lite/APB/AHB slave | CPU/debug 写 DMA 寄存器 | 配置、start、stop、status、error |
| descriptor fetch | AXI master read | DMA 读 memory | 读取任务元数据、queue entry、next pointer |
| data movement | AXI master read/write | DMA 读源、写目的 | 高吞吐 burst、outstanding、response |
| completion/writeback | AXI master write 或 MMIO/status | DMA 写完成记录、状态 | 软件可见完成、错误状态、interrupt 触发 |

把这些责任拆开，是为了避免控制路径被大数据流量淹没，也为了让 descriptor、data 和 completion 可以使用不同 QoS、ID、outstanding、cache 属性和错误处理策略。代价是 DMA 内部状态机和 AXI 接口数量增加，验证要覆盖多路径之间的 ordering。

## 控制面接口：CPU 看到的 DMA

控制面是 CPU 或 debug master 通过 MMIO 配置 DMA 的路径。它强调可诊断性和明确软件语义，不强调大吞吐。

| 控制面访问 | BUS 语义 | 风险 |
| --- | --- | --- |
| 写配置寄存器 | MMIO write，可能有 side effect | 写顺序错误导致 DMA 用旧配置启动 |
| 写 start/doorbell | MMIO write 触发任务 | descriptor 尚未对 DMA 可见 |
| 读 status/error | MMIO read，可能清状态或 latch 状态 | read side effect 改变现场 |
| 写 clear/reset | MMIO write 改变 DMA 状态机 | 清错时机可能丢 completion |
| debug 访问 DMA register | debug master 走同一或旁路 MMIO path | 与软件访问竞争，权限要定义 |

控制面接口常使用 AXI-Lite、APB 或窄 AXI slave port。设计取舍是简单可靠还是高并发。控制寄存器路径若和数据路径共用 bridge，低速 APB stall 可能拖住状态读取；若拆成独立低速路径，软件控制更稳定，但寄存器和数据状态之间要定义同步关系。

## Descriptor Fetch：任务元数据路径

descriptor fetch 是 DMA 从 memory 读取任务描述的路径。它位于 doorbell 之后、data movement 之前，是控制面与数据面的交界。

| Descriptor 字段 | 影响的 AXI 行为 |
| --- | --- |
| source address | 生成 data read transaction |
| destination address | 生成 data write transaction |
| length / stride | 决定 burst 数量、边界和拆分 |
| control flags | 决定 interrupt、writeback、cache 属性或 channel |
| next pointer / queue metadata | 决定是否继续 fetch 下一任务 |

descriptor fetch 的风险来自可见性和优先级。CPU 写 descriptor 后需要让 DMA 可见；IOMMU/SMMU 需要允许 DMA 读取 descriptor；descriptor read 若与大数据流共用同一 AXI ID 或 port，可能被 data burst 饿死，导致 DMA 看起来“还没开始”。

## 数据面接口：吞吐来自多项约束

数据面是 DMA 作为 AXI master 发起读写的主要路径。它的性能取决于 burst、outstanding、ID、目标热点、read/write 混合、response path 和下游 DDR/SRAM 行为。

| 设计点 | 收益 | 代价或风险 |
| --- | --- | --- |
| 较大 burst | 提高地址开销效率 | 受 4KB boundary、目标接受能力和 latency tail 限制 |
| 更深 outstanding | 隐藏 memory latency | 消耗 interconnect/DDR slot，错误恢复更复杂 |
| 独立 read/write port | 减少内部耦合 | 面积、仲裁和 QoS 配置增加 |
| 多 AXI ID / channel | 支持多队列并发 | response 匹配、ordering 和 backpressure 更难验证 |
| QoS 标记 | 保护实时或高优先级 DMA | 配置错误会影响 CPU/display 等其他流量 |

DMA 的 AXI master 不能只按峰值带宽建模。若源和目的都在同一 DDR controller，read/write 会在 controller 内竞争；若目的落在 APB bridge，宽 burst 会被拆成低速访问；若经过 IOMMU/SMMU，translation miss 会额外占用 memory path。

## Writeback 与 Completion：软件看到的结束

DMA 数据搬完，不代表软件已经看到完成。completion/writeback 路径负责把结果写回 memory 或 status，并触发 interrupt 或供 polling 读取。

| 完成动作 | BUS 路径 | 建模关注点 |
| --- | --- | --- |
| 写 completion record | DMA AXI write -> memory | completion 对 CPU cache 可见 |
| 更新 status register | DMA internal state 或 MMIO visible state | status 与 completion 顺序 |
| 触发 interrupt | device -> interrupt controller | interrupt 不早于 completion/status 可见 |
| 写 error record | DMA writeback 或 MMIO status | fault 类型、任务 ID、地址 |
| 清理内部 slot | DMA state release | 后续任务是否被阻塞 |

writeback 的数据量小于 data movement，却更影响软件可见的完成时间。若 writeback 与大数据写共用同一个 AXI port，completion 可能排在大量 data write 后面；若 interrupt 早于 writeback，CPU ISR 会读到旧 completion；若 error completion 不释放 DMA slot，队列会停住。

## 单 Port 与多 Port DMA

DMA 可以用一个 AXI master 处理 descriptor/data/writeback，也可以拆成多条 master port。

| 结构 | 收益 | 风险 |
| --- | --- | --- |
| 单 AXI master port | RTL 简单，资源少，ordering 容易理解 | descriptor、data、writeback 互相阻塞 |
| descriptor 独立 read port | 任务获取不易被 data burst 饿死 | 多 port 仲裁和权限配置增加 |
| data read/write 分离 | 提高双向吞吐，便于 QoS | read/write completion 和错误聚合更复杂 |
| writeback 独立 port | completion latency 更稳定 | 小流量 port 也要配置属性、权限和错误路径 |
| per-channel port | 多队列隔离强 | 面积和系统集成复杂度上升 |

接口拆分不是越多越好。拆分能隔离流量，也会增加 IOMMU context、firewall rule、AXI ID space、QoS 配置和 debug 可见性。建模时要把“同一个 DMA”拆成多个 BUS 参与者，而不是只给 DMA 一个总带宽参数。

## AXI ID、Queue 与 Channel 映射

AXI ID 可以用来区分 DMA 内部 channel、queue、descriptor flow 或 data flow，但 ID 映射必须与 ordering 语义匹配。

| 映射方式 | 收益 | 风险 |
| --- | --- | --- |
| 所有流量共用一个 ID | 保序简单 | outstanding 并发受限，head-of-line blocking 明显 |
| descriptor/data/writeback 分 ID | 降低互相阻塞 | 需要定义 completion 与 data 的顺序 |
| per channel 分 ID | 多队列并行 | response 匹配和错误归因更复杂 |
| ID remap by interconnect/SMMU | 节省系统 ID 空间 | 内部 slot 耗尽会反向 backpressure |

ID 不是性能开关。增加 ID 只能帮助互连和 slave 区分事务流，不能突破目标端口、SMMU translation queue、DDR controller 或 DMA 内部 buffer 的限制。模型要同时记录 ID space 和每个 service point 的 slot。

## 例子：双 Port DMA 的任务流

一个 DMA 有 register slave port、descriptor read port、data read/write port、writeback port。一次任务可以拆成下面的 BUS 事件：

| 阶段 | 事件 | 接口 | 关键状态 |
| --- | --- | --- | --- |
| T0 | CPU 写 descriptor | CPU memory path | descriptor 内容完整 |
| T1 | CPU 写 doorbell/start | DMA register slave | `doorbell_write_accept` |
| T2 | DMA 读 descriptor | descriptor read port | IOMMU translation、descriptor visible |
| T3 | DMA 发起 source read | data read port | burst、outstanding、read response |
| T4 | DMA 发起 destination write | data write port | write data、BRESP、target backpressure |
| T5 | DMA 写 completion record | writeback port | completion visible to CPU |
| T6 | DMA assert interrupt | interrupt path | ISR 可读到 completion/status |

这个例子说明，DMA 的“开始”和“完成”都不是单一 AXI transaction。开始依赖 descriptor 可见性和 doorbell；完成依赖 data response、writeback、status 和 interrupt 的顺序。

## 错误归因

DMA 相关错误需要按接口归因，否则容易把控制面、翻译层和数据面混在一起。

| 错误现象 | 可能位置 | 诊断线索 |
| --- | --- | --- |
| doorbell 后 DMA 不启动 | control path、descriptor visibility、IOMMU descriptor fault | start bit、descriptor read、fault status |
| data move 慢 | data AXI port、DDR/SRAM 热点、SMMU miss、QoS | outstanding、burst、translation miss、memory counter |
| completion 丢失 | writeback path、cache visibility、interrupt path | completion record、status bit、interrupt pending |
| DMA hang | target no response、bridge timeout、slot 未释放 | last issued transaction、timeout status、AXI response |
| 只在多队列下出错 | ID/queue/channel 映射 | response matching、per-channel ordering |

错误模型要回答两个问题：错误发生在哪条接口路径，错误是否释放 DMA 内部资源。只记录“DMA error”不足以定位问题。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| DMA 接 AXI 就是一个 master port | DMA 至少包含控制、descriptor、data、writeback/interrupt 多类 BUS 责任 |
| 数据面带宽够，DMA 就快 | descriptor fetch、SMMU miss、writeback 和 interrupt 都会影响软件可见完成 |
| 多 AXI ID 等于高性能 | ID 还受内部 slot、目标端口、translation queue 和 response path 限制 |
| completion 小，可以忽略 | completion 是软件可见结束点，排队或不可见会变成“任务没完成” |

## 一句话理解

DMA 接 AXI 是把控制、取任务、搬数据、写完成和发通知接入同一个事务系统，而不是把一个 master 口连到互连上。

## 建模启示

AXI + DMA 要按职责路径建模。性能模型要分别记录 register slave、descriptor read、data read、data write、writeback、interrupt/status 的 latency、bandwidth、outstanding、QoS、ID、SMMU/IOMMU 影响和共享仲裁点。功能模型要记录 doorbell 顺序、descriptor 可见性、cache/coherence、地址翻译、错误 response、completion 可见性、interrupt pending/clear 和 DMA slot 释放。

事件模型建议显式表达 `dma_register_write`、`doorbell_write_accept`、`descriptor_fetch_issue`、`descriptor_fetch_done`、`data_read_issue`、`data_write_issue`、`data_response_done`、`completion_write_issue`、`completion_visible`、`dma_interrupt_assert`、`dma_slot_release`。这些事件能把“DMA 慢”“DMA 没完成”“DMA fault”拆成具体 BUS 路径上的状态变化。
