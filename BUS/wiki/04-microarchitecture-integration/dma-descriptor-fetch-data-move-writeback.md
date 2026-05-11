# DMA Descriptor Fetch、Data Move 与 Writeback

上级：[04 微架构与系统集成](./README.md)

相关：[AXI 与 DMA 的系统接口](./axi-dma-system-interface.md)、[Doorbell、Completion 与 Interrupt Flow](./doorbell-completion-interrupt-flow.md)

## 这页在回答什么问题

一次完整 DMA 任务，从软件提交到硬件完成，通常会分成哪几个总线阶段，以及每个阶段可能卡在哪。

## 常见三段链路

### 1. Descriptor Fetch

DMA 先去内存中取：

- source / destination address
- length
- control flag
- next pointer 或 queue metadata

这一步的问题常见在：

- descriptor 本身还没写完整
- cache clean / visibility 没做好
- fetch 和 data path 抢同一个 AXI port

### 2. Data Move

DMA 再发起真正的大块读写。  
这里的核心问题是：

- burst 是否合理
- outstanding 是否足够
- source 和 destination 是否落在热点路径
- response path 会不会先堵

### 3. Writeback / Completion

任务完成后，DMA 往往还要：

- 更新 completion record
- 写状态位
- 触发 interrupt 或 event

这里的问题常见在：

- completion 写回可见性不足
- interrupt 比写回先到
- writeback 被普通 data write 拖延

## 为什么这三段必须分开看

因为“DMA 慢”可能慢在完全不同的地方：

- 慢在 descriptor fetch，说明控制提交链路有问题
- 慢在 data move，说明主数据面有问题
- 慢在 writeback，说明软件看到完成的路径有问题

## 继续阅读

- 如果你在追 `软件提交流程和硬件完成通知怎么闭环`：看 [Doorbell、Completion 与 Interrupt Flow](./doorbell-completion-interrupt-flow.md)
- 如果你在追 `descriptor 可见性和 barrier 为什么会出问题`：看 [AXI 属性、Cacheability 与 Barrier](./axi-attributes-cacheability-barrier.md)
- 如果你在追 `data move 进 DDR 后为什么变形`：看 [AXI 到 DDR Controller 的路径](./axi-to-ddr-controller-path.md)
- 如果你在追 `completion 为什么偶发丢失`：看 [DMA Completion 丢失案例卡](../06-scenarios-case-studies/dma-completion-missing-case-card.md)

## 一句话理解

DMA 任务不是一笔事务，而是一串 `取任务 -> 搬数据 -> 回写完成` 的总线阶段；不拆开看，就很难准确定位瓶颈。
