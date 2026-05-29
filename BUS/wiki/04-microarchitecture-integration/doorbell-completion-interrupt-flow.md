# Doorbell、Completion 与 Interrupt Flow

上级：[04 微架构与系统集成](./README.md)

相关：[DMA Wiki 首页](../../../DMA/wiki/README.md)、[MMIO、Cache 与 Interrupt 视角](./mmio-cache-interrupt-view.md)、[IOMMU、SMMU 与 DMA 寻址](./iommu-smmu-dma-addressing.md)、[AXI 与 DMA 的系统接口](./axi-dma-system-interface.md)、[PCIE Wiki: 队列、Doorbell、Completion 与 MSI-X](../../../PCIE/wiki/04-data-path-dma-interrupts/queues-doorbells-completions-msix.md)

## 这页在回答什么问题

想象一个**外卖下单流程**：你准备好订单详情，按下"下单"按钮（doorbell）；外卖员送到后在门口放好并拍照（completion record）；你手机收到"已送达"通知（interrupt）；你点击"确认收货"（clear/EOI）。

从 BUS 视角看，这不是三个独立按钮，而是一条跨越 cacheable memory、MMIO register、DMA master、interrupt controller 和 CPU ISR 的**事件链**。正确性取决于顺序：订单详情必须先于"下单"按钮可见（别人看到你按了按钮但不知道你点了啥），照片必须先于通知可见（你收到通知去开门发现外卖还没到），"确认收货"必须真正传到骑手端（不然骑手以为你没收到会再送一次）。

## 三个对象的职责

| 对象 | 软件视角 | BUS 视角 | 关键风险 |
| --- | --- | --- | --- |
| doorbell | “有新任务了” | CPU 发起的 MMIO write | descriptor 尚未对 device 可见 |
| completion record | “任务结果写在这里” | device/DMA 发起的 memory write | CPU cache 看不到最新结果 |
| status register | “设备内部状态” | MMIO read/write 或内部状态镜像 | read/write side effect |
| interrupt | “该处理完成事件了” | event 进入 interrupt controller，再唤醒 CPU | interrupt 早于 status/completion 可见 |
| clear / EOI | “本次中断处理完” | CPU 发起 MMIO write | clear 被延迟或顺序错误导致重复中断 |

设计动机是把控制、数据和通知解耦。doorbell 只传递“任务可取”的提示，不承载完整任务；completion record 把结果放在 memory，避免通过低速寄存器搬数据；interrupt 避免 CPU 频繁轮询。代价是系统必须维护跨路径 ordering。

## 提交路径：Descriptor 先于 Doorbell

一次典型提交路径如下：

| 阶段 | 事件 | BUS 路径 | 正确性条件 |
| --- | --- | --- | --- |
| T0 | 软件填写 descriptor / queue entry | CPU -> cacheable memory | descriptor 内容完整 |
| T1 | 软件执行 cache clean / barrier | CPU cache / memory system | descriptor 对 DMA 可见 |
| T2 | 软件写 doorbell register | CPU -> MMIO -> device | doorbell write 不能越过 descriptor 可见性 |
| T3 | device 看到 doorbell | device local state | queue index / producer pointer 更新正确 |
| T4 | DMA 读取 descriptor | DMA -> IOMMU/SMMU -> memory | 地址翻译、权限、cache 可见性正确 |
| T5 | DMA 开始 data movement | DMA read/write path | 数据路径获得资源 |

doorbell 是控制面 MMIO write。它的完成不等于 DMA 已经读到 descriptor，只表示 doorbell transaction 被设备侧接收或排队。若 descriptor 仍在 CPU cache 中，device 会读到旧内容；若 doorbell write 被提前观察，device 会在任务内容未稳定时启动。

## 完成路径：Completion 先于 Interrupt

完成路径的核心顺序是：结果先写可见，再通知 CPU。

| 阶段 | 事件 | BUS 路径 | 正确性条件 |
| --- | --- | --- | --- |
| T0 | DMA 完成 data movement | DMA data path | data write response 已满足设备定义 |
| T1 | device/DMA 写 completion record | DMA -> memory | completion 内容完整且对 CPU 可见 |
| T2 | device 更新 status bit | device internal 或 MMIO visible state | status 与 completion 一致 |
| T3 | device 触发 interrupt | device -> interrupt controller | interrupt 不早于 completion/status 可见 |
| T4 | CPU 进入 ISR | interrupt controller -> CPU | ISR 能定位 completion |
| T5 | CPU 读 completion/status | CPU -> memory/MMIO | cache invalidate 或 coherent visibility 正确 |
| T6 | CPU 写 clear/EOI | CPU -> MMIO | clear/EOI 到达对应目标 |

如果 T3 早于 T1/T2 可见，ISR 会读到旧 completion 或空队列。若 T6 没有真正到达设备或 interrupt controller，CPU 可能反复进入同一个中断。建模时必须把 interrupt 看成“提示去看状态”，而不是完成本身。

## Polling 与 Interrupt 的差异

completion 可以通过 polling 或 interrupt 被 CPU 发现。两者共享 completion/status 路径，但等待方式和风险不同。

| 方式 | BUS 行为 | 收益 | 代价 |
| --- | --- | --- | --- |
| polling memory completion | CPU 反复读 memory 中的 completion record | 低通知延迟，适合高频队列 | 占用 BUS/cache，需处理 cache 可见性 |
| polling MMIO status | CPU 反复读 status register | 简单直接，适合低频控制 | MMIO read 慢，可能有 read side effect |
| interrupt | device 触发 interrupt，CPU ISR 读取状态 | CPU 空闲成本低，适合低到中频事件 | interrupt latency、聚合、丢/重入风险 |
| hybrid | 短期 polling，超时后睡眠等中断 | 平衡延迟和 CPU 成本 | 状态机更复杂 |

polling 不是没有 ordering 问题。CPU 读取 memory completion 前仍需要 cache 可见性；读取 MMIO status 时仍可能触发 side effect。interrupt 也不是自动正确，它只是把 CPU 从等待状态唤醒。

## Doorbell、Queue Pointer 与 Lost Wakeup

queue 型设备通过 producer/consumer pointer 描述任务位置。doorbell 可能写入队列索引，也可能只写一个“有新任务”的提示。

| 设计 | 优点 | 风险 |
| --- | --- | --- |
| doorbell 写 producer index | device 可精确知道新任务范围 | index 与 descriptor 可见性必须匹配 |
| doorbell 写无意义触发值 | 寄存器简单，软件可批量提交 | device 需要从 memory 读取 pointer |
| memory-mapped producer pointer + doorbell | 减少寄存器语义 | pointer cache 可见性成为关键 |
| interrupt coalescing | 降低中断频率 | completion 到通知之间延迟增加 |

lost wakeup 的典型来源是状态和通知顺序不一致。例如软件检查 completion queue 为空后准备睡眠，而 device 在睡眠前写入 completion 但 interrupt 被错误 mask；或 CPU 清 interrupt 时，device 又产生新 completion，但 clear 语义把新事件一起清掉。BUS 模型要能表达 status、mask、pending、clear 和 completion pointer 的先后关系。

## Error Completion 与 Fault

任务完成不只包括 success。DMA translation fault、target slave error、timeout、descriptor 格式错误，都可能生成 error completion 或 status。

| 错误来源 | Completion 语义 | BUS 关注点 |
| --- | --- | --- |
| IOMMU translation fault | completion 标记地址或权限错误 | fault record 与 completion 的顺序 |
| descriptor fetch error | 任务无法启动或部分启动 | descriptor read response、DMA state |
| data movement error | 读/写目标失败 | error response、partial completion |
| timeout | device 等待目标过久 | timeout status、资源释放 |
| interrupt delivery error | completion 已有但 CPU 未被唤醒 | polling/debug path 可否发现 |

error completion 的价值在于释放软件等待。若设备发生 fault 但不写 completion、不置 status、不触发 interrupt，软件只能看到队列停止。模型要明确错误是否写 completion、是否触发 interrupt、是否需要 driver 清 fault 后继续。

## 例子：Descriptor、Doorbell、Completion、中断

下面是一条完整事件链，适合用作驱动和 BUS 模型的对照。

| 阶段 | 事件 | 必要顺序 |
| --- | --- | --- |
| T0 | CPU 写 descriptor 到 memory | descriptor fields 全部完成 |
| T1 | CPU clean cache / barrier | descriptor 对 DMA 可见 |
| T2 | CPU 写 MMIO doorbell | 不能早于 T1 被 device 观察 |
| T3 | DMA 读取 descriptor | 看到 T0 的内容 |
| T4 | DMA 读源/写目的数据 | data response 决定任务状态 |
| T5 | DMA 写 completion record | completion 对 CPU 可见 |
| T6 | DMA/device 更新 status 或 queue consumer | status 与 completion 一致 |
| T7 | device assert interrupt | 不能早于 T5/T6 |
| T8 | CPU ISR 读 completion/status | 需要 cache/coherence 或 MMIO side effect 规则 |
| T9 | CPU 写 clear/EOI | 不能清掉尚未处理的新事件 |

这个表的重点不是固定周期，而是 happens-before 关系。BUS 模型要说明哪些关系由 barrier 保证，哪些由设备内部状态机保证，哪些由 interrupt controller 或 bridge 约束。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| doorbell 写完成就代表任务开始 | doorbell 只表示控制写被接收，descriptor 可见性和 DMA fetch 仍要满足 |
| interrupt 就是 completion | interrupt 只是通知，completion/status 才是软件判断完成的依据 |
| polling 不需要 barrier 或 cache 处理 | polling memory completion 仍受 cache 可见性影响 |
| clear interrupt 是最后一步，顺序无所谓 | clear/EOI 顺序错误会导致重复中断或丢事件 |

## 一句话理解

doorbell、completion 和 interrupt 是一条跨 memory、MMIO 和异步通知的 BUS 事件链，正确性来自它们之间的可见顺序。

## 建模启示

这类流程要按 happens-before 建模，而不是按“软件调用了 start、硬件发了 interrupt”建模。性能模型要记录 doorbell MMIO latency、descriptor fetch latency、data movement latency、completion write latency、interrupt delivery latency、polling 频率和 clear/EOI latency。功能模型要记录 cache 可见性、barrier、queue pointer、status bit、interrupt pending/mask、error completion、fault record 和 clear 语义。

事件模型建议显式表达 `descriptor_write_done`、`descriptor_visible_to_dma`、`doorbell_write_accept`、`descriptor_fetch_done`、`data_move_done`、`completion_write_visible`、`status_update_visible`、`interrupt_assert`、`isr_completion_read`、`interrupt_clear_done`。这些事件的顺序决定软件看到的是正常完成、空队列中断、重复中断、丢事件，还是 DMA 任务无声停止。
