# 队列、Doorbell 与 Completion

上级：[04 软件栈与编程模型](./README.md)

相关：[软件栈与编程模型](./software-stack.md)、[同步、一致性与常见错误](./synchronization-errors.md)、[PCIE：队列、Doorbell、Completion 与 MSI-X](../../PCIE/wiki/04-data-path-dma-interrupts/queues-doorbells-completions-msix.md)

## 这页在回答什么问题

为什么现代 DMA 的软件接口通常都围绕 queue、doorbell 和 completion 组织；以及这三个对象如何共同决定吞吐、正确性和软件可见时序。

## Queue 解决的是批量提交，而不是只是“排队”

寄存器 DMA 的最大问题之一，是每笔任务都要单独配置、单独启动、单独等待。只要任务频率提高，这条路径很快就会让 CPU 成为瓶颈。queue 的设计动机，就是让软件把一批任务先放进可复用容器里，再由 DMA 持续消费。于是软件和硬件的关系从“逐笔对话”变成“维护共享任务池”。

queue 的真正价值不在“有个数组能存 descriptor”，而在于它把提交开销摊薄，并允许 DMA 在硬件侧形成 steady-state。代价是软件现在必须维护 producer/consumer 边界、队列深度、槽位复用和 completion 回收。

## Doorbell 解决的是“何时值得让硬件开始看”

有了 queue 之后，DMA 仍然需要知道“哪里有新任务可取”。doorbell 就是这个通知机制。它最常见的形式是一次 MMIO write、寄存器更新或某种事件触发。名字不重要，关键是它定义了硬件开始观察 queue 的时刻。

把 doorbell 想成前台按铃通知后厨“新单已经可以取了”比较合适。这个类比的边界也很重要：铃声只代表“去看任务池”，不代表任务内容一定已经安全摆好。因此在真实系统里，doorbell 前通常还需要保证 descriptor、payload 和相关元数据已经对 DMA 可见。否则就是典型的“铃响了，但菜单还没写完”。

## Completion 解决的是软件世界何时可以继续

queue 和 doorbell 解决的是提交侧，completion 解决的是回收侧。没有 completion，软件就不知道何时可以：

- 复用 queue entry
- 回收或复用 buffer
- 唤醒下游消费者
- 统计错误并推进状态机

completion 的形式很多：interrupt、polling 命中、completion record、event queue item、status bit。它们在实现上不同，但本质都在定义“哪个完成阶段对软件可见了”。

## 必须把三种“完成”区分开

这一页最关键的主定义是把下面三种状态拆开：

- `descriptor consumed`
- `transfer visible`
- `software completion event`

不同 DMA IP 文档里，`completion` 可能偏向其中任何一种。NIC/NVMe 常把 host 软件可见的完成队列项叫 completion；某些 AXI DMA 文档则可能把 descriptor 消耗或最后一笔 data write 完成直接叫 done。软件若不把这三者区分开，就会在 queue 复用、buffer 生命周期和中断处理上不断踩坑。

## Interrupt、polling 和 completion record 的 trade-off

interrupt 的优点是软件空闲时几乎零轮询成本，缺点是高频小任务下开销和抖动都可能很大。polling 的优点是延迟可控、避免中断风暴，缺点是会消耗 CPU 时间并可能制造 cache 干扰。completion record 或 event queue 则更适合高吞吐系统，因为它们把“完成信息”本身结构化了，软件可以批量消费。

所以没有一种 completion 机制天然最好。小频率控制路径喜欢 interrupt；高速 steady-state 更偏 batching + polling 或 completion queue；混合系统则常常用 moderation 策略在两者之间折中。

## 一个简化流程图

```text
CPU/runtime:
  fill descriptor(s)
  -> make visible
  -> ring doorbell

DMA engine:
  fetch descriptor
  -> execute transfer
  -> record completion

CPU/runtime:
  poll / interrupt
  -> consume completion
  -> recycle entry/buffer
```

这个流程图故意把 `make visible` 单独列出来，因为它正是很多人省略后出 bug 的那一步。

## 常见误解

常见误解：`doorbell 就是 start`。实际上 doorbell 更准确地说是“硬件现在可以去看任务池”，它依赖前面的可见性已经成立。

常见误解：`completion 就是数据搬完`。实际上 completion 可能指 descriptor 已消费、数据已写回或软件已收到事件中的任意一层。

常见误解：`queue 深度越大越好`。实际上 queue 过深但 completion 回收跟不上时，只会把积压和尾延迟后移。

## 一句话理解

queue、doorbell 和 completion 共同定义了 DMA 的软件时序边界，没有这三者的清晰契约，就很难得到既正确又高吞吐的系统。

## 建模启示

这页适合把软件前端和硬件后端之间的共享队列显式建出来。event-driven 仿真里，至少应显式表示 `queue_fill_level`、`doorbell_pending`、`completion_queue_depth` 和 `software_reclaim_rate`。

一个够用的数据结构是：

```text
DMAQueue {
  prod_idx
  cons_idx
  visible_idx
  completion_idx
}
```

如果只关心平均吞吐，可以把 doorbell 和 completion 合并成固定前后处理开销；如果关心正确性、interrupt moderation 或小包/小 tile 高频压力，就必须显式保留这些索引和事件顺序。
