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

- `submission queue / ring`：软件生产描述符，设备消费；队尾或有效位按接口契约标识已发布项目。
- `doorbell`：软件更新 MMIO 寄存器，通知设备检查已发布任务；它本身不是命令完成。
- `completion queue entry (CQE)`：设备生产命令状态，软件消费；软件检查有效位或 phase、命令标识和状态后回收，必要时更新消费指针。
- `MSI-X`：设备向已配置的消息目的地址发通知，请求 CPU 服务队列；一次中断可覆盖多个 CQE，也可能因屏蔽、合并或轮询而暂时没有中断。CQE 的有效状态才是判定具体命令的依据。

## 为什么这是最重要的软件契约

因为它把三种不同可见性绑在一起：

- memory 可见性
- device 内部状态推进
- CPU 通知机制

软件必须先按 DMA 映射和发布规则使描述符对设备可见，再写 doorbell。设备依接口约定先发布 CQE 再通知；CPU 按有效位及 DMA 同步规则读取。中断到达本身既不替代 CQE 检查，也不自动完成非一致缓存同步。

## 一句话理解

queue、doorbell、completion 和 MSI-X 共同构成了 PCIE 设备最常见的一条控制提交到完成通知主线。
