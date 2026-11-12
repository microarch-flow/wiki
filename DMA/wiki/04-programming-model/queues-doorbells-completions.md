# 队列、Doorbell 与 Completion

上级：[04 软件栈与编程模型](./README.md)

相关：[软件栈与编程模型](./software-stack.md)、[同步、一致性与常见错误](./synchronization-errors.md)、[PCIE：队列、Doorbell、Completion 与 MSI-X](../../../series/interconnect/PCIE/wiki/04-data-path-dma-interrupts/queues-doorbells-completions-msix.md)

## 这页在回答什么问题

为什么现代 DMA 的软件接口通常都围绕 queue、doorbell 和 completion 组织；以及这三个对象如何共同决定吞吐、正确性和软件可见时序。

## Queue 解决的是批量提交，而不是只是“排队”

寄存器 DMA 的最大问题之一，是每笔任务都要单独配置、单独启动、单独等待。只要任务频率提高，这条路径很快就会让 CPU 成为瓶颈。queue 的设计动机，就是让软件把一批任务先放进可复用容器里，再由 DMA 持续消费。于是软件和硬件的关系从“逐笔对话”变成“维护共享任务池”。

queue 的真正价值不在“有个数组能存 descriptor”，而在于它把提交开销摊薄，并允许 DMA 在硬件侧形成 steady-state。代价是软件现在必须维护 producer/consumer 边界、队列深度、槽位复用和 completion 回收。

## Doorbell 解决的是“何时值得让硬件开始看”

有了 queue 之后，DMA 仍然需要知道“哪里有新任务可取”。doorbell 就是这个通知机制。它最常见的形式是一次 MMIO write、寄存器更新或某种事件触发。名字不重要，关键是它定义了硬件开始观察 queue 的时刻。

把 doorbell 想成前台按铃通知后厨“新单已经可以取了”比较合适。这个类比的边界也很重要：铃声只代表“去看任务池”，不代表任务内容一定已经安全摆好。因此在真实系统里，doorbell 前通常还需要保证 descriptor、payload 和相关元数据已经对 DMA 可见。否则就是典型的“铃响了，但菜单还没写完”。

## Completion 解决的是软件世界何时可以继续

queue 和 doorbell 解决的是提交侧；设备报告的消费、完成和所有权状态决定回收侧。软件需要根据具体接口判断何时可以：

- 复用 queue entry
- 回收或复用 buffer
- 唤醒下游消费者
- 统计错误并推进状态机

completion record、event queue item 或 status bit 表示状态；interrupt 和 polling 是发现状态的方法，可以用于同一个 completion record。中断只是服务提示，软件仍须检查有效状态和具体命令。

## 必须把三种“完成”区分开

这一页最关键的主定义是把下面三种状态拆开：

- `descriptor consumed`
- `transfer visible`
- `software completion event`

不同 DMA IP 文档里，`completion` 可能偏向其中任何一种。NIC/NVMe 常把 host 软件可见的完成队列项叫 completion；某些 AXI DMA 文档则可能把 descriptor 消耗或最后一笔 data write 完成直接叫 done。设备取走 descriptor 不自动意味着软件可覆盖它：只有接口提供消费确认并明确允许复用时，才可提前回收该 descriptor/SQ 槽；若设备还会回写该槽，就要等契约规定的安全边界。命令的数据 buffer 则须等相关传输完成并完成所有权与可见性交接，即使 descriptor 槽已回收也不能提前复用。参见 [NVMe 命令提交与完成流程](https://nvmexpress.org/wp-content/uploads/NVM-Express-1_1b-1.pdf)和 [AMD AXI DMA 的 descriptor 状态](https://docs.amd.com/r/en-US/pg021_axi_dma/Scatter/Gather-Mode)。

## Interrupt、polling 和 completion record 的 trade-off

interrupt 的优点是软件空闲时几乎零轮询成本，缺点是高频小任务下开销和抖动都可能很大。polling 的优点是延迟可控、避免中断风暴，缺点是会消耗 CPU 时间并可能制造 cache 干扰。completion record 或 event queue 则更适合高吞吐系统，因为它们把“完成信息”本身结构化了，软件可以批量消费。

因此没有一种发现方式天然最好。低频控制路径常用 interrupt；高速系统可批量轮询 completion queue，也可通过合并中断唤醒后批量消费同一队列。polling/interrupt 是发现方式，批量消费及 interrupt moderation 是可分别配置的策略；混合系统也可在轮询和中断之间切换。

## 一个简化流程图

```text
CPU/runtime:
  fill descriptor(s)
  -> make visible
  -> ring doorbell

DMA engine:
  fetch descriptor
  -> 按接口契约报告 descriptor 消费（若允许，可提前回收槽位）
  -> execute transfer
  -> record completion

CPU/runtime:
  poll / interrupt
  -> consume completion
  -> 按命令完成和所有权契约回收 data buffer
```

这个流程图故意把 `make visible` 单独列出来，因为它正是很多人省略后出 bug 的那一步。若接口没有提前回收 descriptor 的保证，就应等接口规定的后续状态，不得仅凭 fetch 推断。

## 常见误解

常见误解：`doorbell 就是 start`。实际上 doorbell 更准确地说是“硬件现在可以去看任务池”，它依赖前面的可见性已经成立。

常见误解：`completion 就是数据搬完`。实际上 completion 可能指 descriptor 已消费、数据已写回或软件已收到事件中的任意一层。

常见误解：`queue 深度越大越好`。实际上 queue 过深但 completion 回收跟不上时，只会把积压和尾延迟后移。

## 一句话理解

queue、doorbell 和 completion 共同定义了 DMA 的软件时序边界，没有这三者的清晰契约，就很难得到既正确又高吞吐的系统。

## 建模启示

这页适合把软件前端和硬件后端之间的共享队列显式建出来。event-driven 仿真里，至少应显式表示 `queue_fill_level`、`doorbell_pending`、`completion_queue_depth` 和 `software_reclaim_rate`。

例如 4 槽 submission ring 保留一个空槽，最大可用容量为 3；producer 和已安全回收的 descriptor 索引均按 4 取模，`(prod+1)%4==reclaim` 表示满。初始两者为 0；软件写槽 0、1、2 后 `prod=3`，队列满。设备按契约取走槽 0 并允许 descriptor 复用，软件将 `reclaim=1`，即可再写槽 3、令 `prod=0`；此时再次满。槽号回卷不表示数据 buffer 可复用：buffer 仍须等相应命令完成及所有权/可见性交接。另一方案使用 phase/wrap 位以区分满空，不能仅看 `prod==cons`。

一个模型应把 submission 和 completion 的生产/消费、容量与 phase 分开；下图只是状态草图：

```text
DMAQueue {
  sq_capacity; sq_prod; sq_device_cons; sq_reclaim; sq_phase
  cq_capacity; cq_device_prod; cq_software_cons; cq_phase
  slot_owners; data_buffer_owners
}
```

如果只关心平均吞吐，且已经证明通知和 completion 回收不会限制任务槽或 buffer 复用，可以将其等效成固定开销；如果关心正确性、interrupt moderation 或小包/小 tile 高频压力，就必须显式保留这些索引和事件顺序。
