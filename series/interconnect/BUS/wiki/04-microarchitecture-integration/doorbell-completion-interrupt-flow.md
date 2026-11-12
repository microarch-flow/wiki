# Doorbell、Completion 与 Interrupt Flow

上级：[04 微架构与系统集成](./README.md)

相关：[DMA Wiki 首页](../../../../../DMA/wiki/README.md)、[MMIO、Cache 与 Interrupt 视角](./mmio-cache-interrupt-view.md)、[IOMMU、SMMU 与 DMA 寻址](./iommu-smmu-dma-addressing.md)、[AXI 与 DMA 的系统接口](./axi-dma-system-interface.md)、[PCIE Wiki: 队列、Doorbell、Completion 与 MSI-X](../../../PCIE/wiki/04-data-path-dma-interrupts/queues-doorbells-completions-msix.md)

## 这页在回答什么问题

想象一个**外卖下单流程**：你准备好订单详情，按下"下单"按钮（doorbell）；外卖员送到后在门口放好并拍照（completion record）；你手机收到"已送达"通知（interrupt）；你点击"确认收货"（clear/EOI）。

从 BUS 视角看，这是一条跨越 memory、MMIO register、DMA master、interrupt controller 和 CPU ISR 的**事件链**。提交时，descriptor 要在设备观察到 doorbell 前按接口要求对 DMA 可见。完成时，有的设备保证写达到指定观察点后才通知；有的允许提前通知，但要提供可靠重试。CPU 还须按 DMA 映射契约取得数据可见性。clear/EOI 必须送达正确目标，并遵守设备对新事件的处理规则。

## 三个对象的职责

| 对象 | 软件视角 | BUS 视角 | 关键风险 |
| --- | --- | --- | --- |
| doorbell | “有新任务了” | CPU 发起的 MMIO write | descriptor 尚未对 device 可见 |
| completion record | “任务结果写在这里” | device/DMA 发起的 memory write | CPU cache 看不到最新结果 |
| status register | “设备内部状态” | MMIO read/write 或内部状态镜像 | read/write side effect |
| interrupt | “该检查完成状态了” | event 进入 interrupt controller，再通知 CPU | 提前通知却无可靠重试，或 CPU 未按映射契约同步 |
| clear / EOI | “本次中断处理完” | CPU 发起 MMIO write | clear 被延迟或顺序错误导致重复中断 |

设计动机是把控制、数据和通知解耦。doorbell 只传递“任务可取”的提示，不承载完整任务；completion record 把结果放在 memory，避免通过低速寄存器搬数据；interrupt 避免 CPU 频繁轮询。代价是系统必须维护跨路径 ordering。

## 提交路径：Descriptor 先于 Doorbell

一次典型提交路径如下：

| 阶段 | 事件 | BUS 路径 | 正确性条件 |
| --- | --- | --- | --- |
| T0 | 软件填写 descriptor / queue entry | CPU -> cacheable memory | descriptor 内容完整 |
| T1 | 软件按映射契约同步并排序 | CPU cache / memory system | descriptor 对 DMA 可见 |
| T2 | 软件写 doorbell register | CPU -> MMIO -> device | doorbell write 不能越过 descriptor 可见性 |
| T3 | device 看到 doorbell | device local state | queue index / producer pointer 更新正确 |
| T4 | DMA 读取 descriptor | DMA -> IOMMU/SMMU -> memory | 地址翻译、权限、cache 可见性正确 |
| T5 | DMA 开始 data movement | DMA read/write path | 数据路径获得资源 |

doorbell 是控制面 MMIO write。它的完成不等于 DMA 已经读到 descriptor，只表示 doorbell transaction 被设备侧接收或排队。若 descriptor 仍在 CPU cache 中，device 会读到旧内容；若 doorbell write 被提前观察，device 会在任务内容未稳定时启动。

## 完成路径：写先于通知的接口示例

本例假设设备接口规定：结果写先达到指定观察点，再通知 CPU；CPU 随后按 DMA 映射契约获取可见性。非一致系统不要求设备直接更新 CPU cache。其他接口若允许提前通知，驱动还需要该接口提供的可靠重试或 polling 机制。

| 阶段 | 事件 | BUS 路径 | 正确性条件 |
| --- | --- | --- | --- |
| T0 | DMA 完成 data movement | DMA data path | data write response 已满足设备定义 |
| T1 | device/DMA 写 completion record | DMA -> memory | completion 内容完整，并达到设备规定的通知前观察点 |
| T2 | device 更新 status bit | device internal 或 MMIO visible state | status 与 completion 一致 |
| T3 | device 触发 interrupt | device -> interrupt controller | 设备保证 completion/status 写与通知的约定顺序 |
| T4 | CPU 进入 ISR | interrupt controller -> CPU | ISR 能定位 completion |
| T5 | CPU 获取并读 completion/status | CPU -> memory/MMIO | 非一致映射按 DMA API 同步后读取；一致映射按要求排序 |
| T6 | CPU 写 clear/EOI | CPU -> MMIO | clear/EOI 到达对应目标 |

如果设备在规定观察点之前通知，或 CPU 未按映射契约同步，ISR 可能读到旧 completion 或空队列。若 T6 没有真正到达设备或 interrupt controller，CPU 可能反复进入同一个中断。建模时必须把 interrupt 看成“提示去看状态”，而不是完成本身。

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

lost wakeup 的典型来源是状态和通知顺序不一致。例如软件检查 completion queue 为空后准备睡眠，而 device 写入 completion 时 interrupt 被错误 mask；或 CPU 清 interrupt 时，新 completion 的 pending 也被清掉。仅执行“arm、复查、普通 sleep”仍不够：ISR 可能在复查之后、sleep 之前处理并清除中断，此时对尚未睡眠线程的唤醒会丢失。

一种可行契约是：设备在 arm/clear 竞争期间锁存 pending，或保证条件仍满足时重触发；软件先登记等待者，再 arm 并复查；最终条件检查和进入阻塞必须由能保留竞争唤醒的同步原语连接。示意如下，`state_lock` 在 ISR 与线程之间按平台要求安全使用，等待原子操作会释放锁并在返回前重新取得锁：

```text
重复直到目标命令的完成状态已处理：
    加锁(state_lock)
    登记等待者()
    解锁(state_lock)
    按设备契约 arm 通知
    加锁(state_lock)
    如果 软件中无该命令的持久完成状态 且 设备状态未就绪：
        等待并原子释放锁(state_lock)  # 醒来后重新持锁；可能虚假唤醒
    撤销等待者()
    解锁(state_lock)
    检查并处理可用完成项
```

ISR 或完成处理者在清除通知前，按契约将结果保存为等待者可检查的持久软件状态，并在更新条件后唤醒等待队列；其他消费者不能先把该状态抹掉。若事件发生在最终检查和阻塞之间，同步原语保证它要么使检查看到新状态，要么唤醒已登记的等待者。设备状态可以是无破坏性读取的 MMIO 状态；检查 streaming DMA buffer 前须先按协议取得所有权并按 DMA API 同步，不能在设备仍拥有它时直接读取。实际代码应使用平台的等待队列、锁及中断 API，并按设备规定处理屏障、mask 和 clear；例如 Linux [等待队列文档](https://docs.kernel.org/6.11/kernel-hacking/hacking.html#wait-queues-include-linux-wait-h)要求先排队再检查条件。若设备既不锁存也不重触发，则还需其接口提供其他可靠的复查或恢复机制。BUS 模型要表达 status、mask、pending、clear 和 completion pointer 的先后关系。

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
| T1 | CPU 按映射契约同步并排序 | descriptor 对 DMA 可见 |
| T2 | CPU 写 MMIO doorbell | 不能早于 T1 被 device 观察 |
| T3 | DMA 读取 descriptor | 看到 T0 的内容 |
| T4 | DMA 读源/写目的数据 | data response 决定任务状态 |
| T5 | DMA 写 completion record | 写达到设备规定的通知前观察点 |
| T6 | DMA/device 更新 status 或 queue consumer | status 与 completion 一致 |
| T7 | device assert interrupt | 不能早于 T5/T6 |
| T8 | CPU ISR 取得所有权，按映射契约同步并读 completion/status | 一致映射仍须满足排序；MMIO 按副作用规则访问 |
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
