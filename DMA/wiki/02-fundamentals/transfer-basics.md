# 传输对象与基本语义

上级：[02 基础对象与传输语义](./README.md)

相关：[地址、描述符与 Burst](./address-descriptor-burst.md)、[软件栈与编程模型](../04-programming-model/software-stack.md)、[队列、Doorbell 与 Completion](../04-programming-model/queues-doorbells-completions.md)

## 这页在回答什么问题

理解 DMA 时，最先该分清哪些对象和阶段；以及为什么“传输完成”这个词如果不先拆开，后面几乎所有讨论都会变得含糊。

## DMA 操作的不是裸地址，而是带约束的移动任务

最表层看，DMA 似乎只需要三样东西：源地址、目的地址、长度。很多入门介绍也确实停在这里，于是读者会形成一个危险直觉：DMA 只是地址区间之间的复制器。这个直觉在最简单的 memory-to-memory 例子里不完全错，但一旦进入外设、host-device 或 AI local DMA，问题就会立刻暴露出来。

因为 DMA 真正接到的不是“把 A 到 B 复制过去”这种裸命令，而是一条带约束的数据移动任务。它至少要包含：

- 数据从谁流向谁
- 这条路径的可见地址是什么
- 多大粒度发事务
- 搬完以后谁能在什么时刻观察到结果

同样是 `A -> B`，语义可能完全不同。`peripheral FIFO -> memory` 更像持续抽水；`HBM -> tile SRAM` 更像定时补数；`host memory -> NIC TX ring` 又带着 IOMMU、completion 和软件回收语义。DMA 统一的不是场景，而是“把带约束的数据移动任务变成独立执行流程”。

## 一次 DMA 任务至少跨四个阶段

后面全库会反复用到下面四个阶段。它们不一定由同一个模块命名，但语义上必须拆开：

1. `submit`：软件或 runtime 把任务声明给 DMA。
2. `accept/consume`：DMA 已经接走 descriptor 或 command。
3. `transfer complete`：数据搬运动作本身已经结束。
4. `consumer visible`：软件或下游消费者可以安全观察或复用结果。

很多文档把其中某一层直接叫 `completion`，这正是后续误解的来源。设备侧 DMA 可能在 descriptor 被取走时更新 queue head；AXI DMA 可能在最后一笔 write response 回来后置位 done；软件真正能读 buffer，则还要等 cache 可见性或 ownership 切换成立。你如果不先问清楚这里说的“完成”是哪一层，后面所有 latency 指标都可能被混在一起。

## 为什么“数据搬完”不等于“系统完成”

这是 DMA 里最常见也最昂贵的误解。数据已经到达目的端，只说明搬运动作在硬件通路上结束了；不代表软件一定能安全读，也不代表下游一定能立刻消费。non-coherent DMA 里，CPU 可能还持有旧 cache line。queue-based 设备 DMA 里，completion record 可能还没写回 host memory。AI local DMA 里，数据虽然到了 SRAM，但 consumer buffer 还没切换到 ready 状态。

把这件事想成签收流程最接近真实结构。货物送到了仓库门口，只代表运输结束；只有仓库系统登记入库、库位可见、下游领料口开放之后，业务系统才会认为“这批货可用了”。这个类比只在“运输完成”和“系统可消费”是不同阶段时成立；它不适用于那种目的端天然就是最终消费者、且不存在额外可见性层次的极简 DMA。

## 四类最基本的传输对象

如果从建模和接口设计角度看，DMA 至少围绕四类对象展开：

- `address object`：源、目的、stride、shape、address domain
- `data object`：bytes、beat width、packet/tile/frame 边界
- `control object`：descriptor、queue entry、doorbell、dependency token
- `completion object`：status bit、completion record、interrupt、event queue item

把这些对象分开很重要，因为它们演化速度并不一致。很多高性能 DMA 的地址对象和控制对象已经非常复杂，但 completion 对象仍然可能很原始；也有些外设 DMA 数据路径简单，却有很严格的完成和中断节拍要求。

## 常见误解

常见误解：`传输长度就是总线拍数`。实际上长度只描述逻辑传输大小，真正的拍数还受 beat width、burst 拆分、边界对齐和协议头开销影响。

常见误解：`DMA done interrupt 等于数据已经可安全消费`。实际上 interrupt 很多时候只表示某个完成阶段对软件可见，不保证 cache、一致性或 buffer ownership 都已经切换正确。

常见误解：`memory-to-memory DMA 没有协议语义`。实际上只要落到 AXI、NoC 或 PCIe，它就仍然受请求/响应、顺序、错误返回和回压语义约束。

## 一句话理解

DMA 的最小理解单元不是一段地址范围，而是一条跨越 `提交、搬运、可见性、完成通知` 多阶段的带约束数据移动任务。

## 建模启示

这页决定后面模型的最小事件集合。cycle-level 或 event-driven 仿真中，至少要把 `task_submit`、`task_accept`、`transfer_done`、`consumer_visible` 四类事件显式建出来，否则就无法正确统计 submit latency、service time 和 completion visibility latency。

一个足够通用的数据结构草图是：

```text
DMATask {
  src_addr
  dst_addr
  bytes
  attrs
  submit_ts
  accept_ts
  transfer_done_ts
  visible_ts
}
```

如果只关心吞吐，可以把 `accept_ts` 和 `visible_ts` 折叠掉；如果关心功能正确性、软件超时或 completion 语义，这两个时间点必须保留。
