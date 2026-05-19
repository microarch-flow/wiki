# 队列、Doorbell、Completion 与 MSI-X

上级：[04 数据路径、DMA 与中断](./README.md)

相关：[BUS Wiki: Doorbell、Completion 与 Interrupt Flow](../../../BUS/wiki/04-microarchitecture-integration/doorbell-completion-interrupt-flow.md)

## 这页在回答什么问题

为什么现代 PCIE 设备的软件接口几乎总绕不开 queue、doorbell、completion 和 MSI-X。

## 一条典型控制到完成链路

1. 软件在 host memory 写 submission queue 或 descriptor ring
2. 软件通过 BAR 里的 MMIO doorbell 告诉设备有新任务
3. 设备 DMA 读队列并执行
4. 设备把完成信息写回 completion queue 或 status memory
5. 设备触发 MSI-X，或者软件轮询看到完成

## 四个对象分别做什么

- `queue / ring`：承载批量任务描述
- `doorbell`：低开销提交通知
- `completion`：把完成事实写成 host 可见记录
- `MSI-X`：把“该处理完成了”的通知推给 CPU

## 为什么这是最重要的软件契约

因为它把三种不同可见性绑在一起：

- memory 可见性
- device 内部状态推进
- CPU 通知机制

这三者任何一个顺序处理不好，都会出现诡异 bug。

## 一句话理解

queue、doorbell、completion 和 MSI-X 共同构成了 PCIE 设备最常见的一条控制提交到完成通知主线。
