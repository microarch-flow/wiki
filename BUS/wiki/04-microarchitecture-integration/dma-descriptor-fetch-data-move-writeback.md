# DMA Descriptor Fetch、Data Move 与 Writeback

上级：[04 微架构与系统集成](./README.md)

相关：[AXI 与 DMA 的系统接口](./axi-dma-system-interface.md)、[Doorbell、Completion 与 Interrupt Flow](./doorbell-completion-interrupt-flow.md)、[IOMMU、SMMU 与 DMA 寻址](./iommu-smmu-dma-addressing.md)、[AXI 属性、Cacheability 与 Barrier](./axi-attributes-cacheability-barrier.md)

## 这页在回答什么问题

一次 DMA 任务就像一次**快递取件 + 送件 + 回执**的完整流程：快递员先去取件点拿到包裹单（descriptor fetch），然后去发件人那里取货、送到收件人那里（data move），最后回来填写送达回执并通知调度中心（writeback/completion）。

把 DMA 拆成这三段，是为了精准定位”哪里出了问题”——不能笼统地说”快递慢”。是取包裹单的路上堵了（descriptor fetch 慢）？还是搬货过程中遇到大件需要多趟（data move 受限）？还是送达后回执一直没交回调度中心（writeback/completion 路径出问题）？

## 三段链路的责任边界

| 阶段 | 发起方 | BUS 事务 | 成功条件 | 常见失败点 |
| --- | --- | --- | --- | --- |
| descriptor fetch | DMA | read descriptor memory | 读到完整、最新、合法 descriptor | cache 可见性、IOMMU fault、descriptor port 被阻塞 |
| data move | DMA | read source / write destination | 源数据读到，目的数据写完并收到 response | burst/边界、DDR 热点、target error、backpressure |
| writeback/completion | DMA/device | write completion/status，触发 event | CPU 能看到完成状态 | writeback 排队、cache 不可见、interrupt 早到 |

这三段之间有顺序依赖，但不一定使用同一条 AXI path。一个 DMA 可能用独立 descriptor port、data read/write port 和 completion writeback port；也可能所有流量共用同一个 AXI master。不同接口组织会改变阻塞关系。

## Descriptor Fetch：任务是否真的被 DMA 看到

descriptor 包含 source、destination、length、stride、control flags、next pointer、interrupt enable 等字段。DMA fetch descriptor 前，软件必须保证 descriptor 内容对 DMA 可见。

| 问题 | BUS 层原因 | 可观察症状 |
| --- | --- | --- |
| DMA 读到旧 descriptor | CPU cache 未 clean，或 barrier 顺序不足 | DMA 搬错地址、长度为旧值 |
| descriptor fetch fault | IOMMU/SMMU mapping 或权限错误 | DMA error、fault record、任务不启动 |
| descriptor fetch 被饿死 | 与 data burst 共用 AXI port/ID，优先级过低 | doorbell 后长时间无数据搬运 |
| descriptor 格式错误 | DMA 读到了内容，但字段不合法 | DMA internal error 或 error completion |
| next pointer 错误 | queue 链表或 ring metadata 不一致 | DMA 跳到错误任务或停止 |

descriptor fetch 的设计取舍是可靠启动和吞吐并行。独立 descriptor port 能避免大数据流阻塞任务获取，但会增加 SMMU context、QoS 和权限配置；共用 port 逻辑简单，却容易让 control flow 被 data flow 淹没。

## Data Move：主数据面不是只看带宽

data move 是 DMA 的大流量阶段。它可能是 memory-to-memory、memory-to-device、device-to-memory，也可能带 scatter-gather、stride 或二维搬运。

| 设计点 | 对 BUS 的影响 | 建模参数 |
| --- | --- | --- |
| burst length | 决定地址开销和 DDR 效率 | AxLEN、边界切分、target 最大 burst |
| alignment | 决定 narrow transfer 或拆分 | 地址对齐、WSTRB、byte lane |
| outstanding depth | 隐藏 memory latency | DMA slot、AXI ID、interconnect/slave slot |
| read/write overlap | 提升吞吐 | read buffer、write buffer、turnaround |
| source/destination placement | 决定热点和路径 | DDR bank、SRAM port、APB bridge、SMMU |
| QoS | 保护实时或批量任务 | priority、限速、仲裁策略 |

data move 的瓶颈可能在 DMA 内部 buffer，也可能在 interconnect、SMMU、DDR controller、SRAM bank、APB bridge 或 response path。若只记录“DMA 带宽”，就无法解释同一 DMA 在不同源/目的组合下表现不同。

## Writeback / Completion：软件何时看见结束

DMA 完成 data move 后，仍要把结果反馈给软件。反馈可以是 completion record、status bit、error code、interrupt 或多个机制组合。

| 完成机制 | BUS 事务 | 风险 |
| --- | --- | --- |
| memory completion record | DMA write memory | CPU cache 看不到最新 completion |
| MMIO status update | device 内部状态或寄存器可见 | read side effect、clear 顺序 |
| interrupt/event | 通知 CPU 或 interrupt controller | interrupt 早于 completion 可见 |
| error writeback | 写 fault/error code | error 与任务 ID 对不上 |
| queue consumer update | 写回 consumer pointer | pointer 与 completion record 顺序不一致 |

writeback 的设计目标是让软件明确知道任务是否完成、是否出错、出错在哪个阶段。它的数据量小，但它定义“软件可见结束”。如果 writeback 与 data write 共用同一 AXI port，completion 可能排在数据突发之后；如果 writeback 发生但 interrupt 丢失，polling 或 debug path 必须能发现完成。

## 端到端阶段表

下面是一条完整 DMA 任务的事件链：

| 阶段 | 事件 | BUS 路径 | 关键状态 |
| --- | --- | --- | --- |
| T0 | CPU 写 descriptor | CPU -> memory | descriptor fields 完整 |
| T1 | CPU clean/cache maintenance + barrier | cache/memory system | descriptor 对 DMA 可见 |
| T2 | CPU 写 doorbell | CPU -> MMIO -> DMA | DMA task active |
| T3 | DMA fetch descriptor | DMA -> SMMU -> memory | descriptor read response |
| T4 | DMA 解析 descriptor | DMA internal | source/destination/length 合法 |
| T5 | DMA 发起 source read | DMA -> SMMU/interconnect -> source | read outstanding、R response |
| T6 | DMA 发起 destination write | DMA -> destination | W/B response、write buffer |
| T7 | DMA drain data responses | response path | data phase complete |
| T8 | DMA write completion | writeback path -> memory/status | completion visible |
| T9 | DMA assert interrupt 或 event | interrupt path | CPU 可被唤醒 |
| T10 | CPU ISR/poll 读取 completion | CPU -> memory/MMIO | cache/coherence 正确 |

这个表的核心是每个阶段都有独立失败模式。T3 fault 表示任务没有进入 data move；T6 error 表示数据面失败；T8/T9 出错表示硬件可能完成了任务，但软件没有可靠看到完成。

## 分段定位 DMA 问题

| 现象 | 更可能的阶段 | 该看什么 |
| --- | --- | --- |
| doorbell 后没有 AXI data | descriptor fetch | descriptor read、SMMU fault、DMA start 状态 |
| DMA 有 read 无 write | data move 内部 | read buffer、write target、descriptor direction |
| 带宽低但无错误 | data move | burst、outstanding、DDR/bridge 热点、QoS |
| 数据搬完但软件等待超时 | writeback/completion | completion write、interrupt pending、cache visibility |
| completion 有错误码 | 取决于错误码 | descriptor fault、data response、timeout、permission |
| 多任务队列乱序 | descriptor/writeback | queue pointer、ID/channel、completion mapping |

这种分段方法的价值是避免误判。descriptor fetch 阶段的 IOMMU fault 不应被归因到 DDR 带宽；writeback 被阻塞也不代表 data move 没完成。

## Error Completion 与资源释放

DMA 任务失败后，系统需要知道两个问题：软件能否看见错误，硬件资源是否释放。

| 错误点 | 正确处理 | 资源释放风险 |
| --- | --- | --- |
| descriptor read fault | 写 error completion 或置 fault status | descriptor slot 若不释放，队列停住 |
| source read error | 标记 data read failure | 已发出的 write 是否需要 drain/abort |
| destination write error | 标记 write failure | write buffer、outstanding slot 是否释放 |
| timeout | 生成 timeout status | 等待中的 transaction 是否可取消 |
| writeback error | 保留 internal done + error 状态 | 软件可能永远看不到完成 |

error completion 不只是调试信息。它是驱动状态机继续前进的条件。若错误没有 completion，也没有 interrupt/status，软件只能看到 DMA 卡住；若错误 completion 早于未完成的 data response，又可能让软件复用 buffer 时破坏数据。

## 与 Cache、Barrier、IOMMU 的关系

三段链路分别依赖不同的系统条件：

| 阶段 | Cache / Barrier | IOMMU / SMMU | Ordering |
| --- | --- | --- | --- |
| descriptor fetch | CPU 写 descriptor 后需要对 DMA 可见 | descriptor IOVA 要有 read permission | descriptor visible 先于 doorbell |
| data move read | source buffer 对 DMA 可见 | source mapping 和权限正确 | source read 完成先于对应 write |
| data move write | destination buffer 可被 DMA 写 | destination mapping 和权限正确 | write response 决定数据写入完成语义 |
| writeback | completion 对 CPU 可见 | completion buffer mapping 正确 | completion visible 先于 interrupt |
| CPU consume | CPU invalidate 或 coherent read | CPU 使用自己的地址视图 | ISR/poll 不能早于 completion 可见 |

IOMMU 解决地址和权限，cache maintenance 解决可见性，barrier 解决顺序。三者缺一项，DMA 任务都可能表现为“偶发错误”。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| DMA start 后就进入数据搬运 | DMA 还要先 fetch descriptor，且 fetch 可能 fault 或被阻塞 |
| data move 完成就是软件可见完成 | writeback、status、interrupt 和 cache 可见性还要成立 |
| DMA 慢就是 DDR 慢 | descriptor、SMMU、bridge、writeback 和 interrupt path 都可能是瓶颈 |
| error completion 可有可无 | 没有 error completion，软件无法可靠释放任务和 buffer |

## 一句话理解

DMA 任务是一条 `提交任务 -> 读取任务 -> 搬运数据 -> 写回完成 -> 通知软件` 的 BUS 状态机，每段都有独立的路径、属性和失败模式。

## 继续阅读

- 如果你在追 `软件提交流程和硬件完成通知怎么闭环`：看 [Doorbell、Completion 与 Interrupt Flow](./doorbell-completion-interrupt-flow.md)
- 如果你在追 `descriptor 可见性和 barrier 为什么会出问题`：看 [AXI 属性、Cacheability 与 Barrier](./axi-attributes-cacheability-barrier.md)
- 如果你在追 `data move 进 DDR 后为什么变形`：看 [AXI 到 DDR Controller 的路径](./axi-to-ddr-controller-path.md)
- 如果你在追 `completion 为什么偶发丢失`：看 [DMA Completion 丢失案例卡](../06-scenarios-case-studies/dma-completion-missing-case-card.md)

## 建模启示

DMA descriptor fetch、data move 和 writeback 要按阶段分别建模。性能模型要记录 descriptor fetch latency、data read/write bandwidth、burst、outstanding、SMMU miss、目标热点、writeback latency、interrupt latency 和每段共享的仲裁点。功能模型要记录 descriptor 可见性、doorbell 顺序、source/destination mapping、AXI response、error completion、completion visibility、interrupt pending/clear 和 DMA slot release。

事件模型建议显式表达 `descriptor_visible_to_dma`、`doorbell_accept`、`descriptor_fetch_issue`、`descriptor_fetch_done`、`data_read_issue`、`data_read_done`、`data_write_issue`、`data_write_done`、`dma_error_record`、`completion_write_visible`、`interrupt_assert`、`dma_slot_release`。这些事件让模型能区分“任务没取到”“数据没搬完”“完成没写回”和“软件没被通知”四类完全不同的问题。
