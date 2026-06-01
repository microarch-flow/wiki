# AXI DMA 案例卡

上级：[07 工作负载与案例](./README.md)

相关：[AXI / PCIe 视角下的 DMA](../05-system-integration/axi-pcie-view.md)、[地址、描述符与 Burst](../02-fundamentals/address-descriptor-burst.md)、[BUS：AXI Channel、ID 与 Outstanding](../../../BUS/wiki/03-on-chip-protocol-families/axi-channel-id-outstanding.md)

## 这页在回答什么问题

把一个典型片上 `AXI DMA` 放回 SoC 环境中，应该如何理解它的职责、瓶颈和设计重点；以及为什么它最值得看的不是“DMA 名字”，而是它作为 AXI master 如何组织事务。

## 典型系统位置

AXI DMA 通常位于片上互连上，连接 DDR、片上 SRAM、外设 FIFO 或 accelerator buffer。它与 CPU、cache、memory controller、其他 master 共享同一套片上 fabric，因此它从一开始就是系统共享资源的参与者，而不是独占通道。

## 它通常在解决什么问题

典型职责包括：

- 把流式外设数据搬进内存
- 把内存数据送到 accelerator 或外设
- 用较低 CPU 开销完成大块 memory-to-memory 搬运

从功能上看并不神秘，但关键在于它如何把逻辑任务翻译成 `AR/AW/R/W/B` 事务，并在共享 AXI fabric 上维持 forward progress。

## 核心机制

一张最小画像通常包含：

- descriptor / linked-list 或简单 ring
- AXI read / write burst
- multiple outstanding transaction
- interrupt 或 polling completion

这里最关键的判断是：AXI DMA 的瓶颈往往不是“会不会搬”，而是 burst 是否够长、对齐与边界拆分是否合理、read/write 回包是否能稳定闭环。

## First bring-up 最值得先看什么

如果一张 AXI DMA 卡在 bring-up，优先问这几个问题：

- 当前路径是 coherent 还是 non-coherent
- descriptor / buffer 中写的是物理地址还是 IOVA
- cache flush / invalidate 与 barrier 顺序是否匹配
- 对齐、page 边界和 burst 拆分是否满足实现要求
- AXI `R/B` 返回是否正常闭环

这几个问题能迅速把问题压缩到地址、可见性还是事务路径层面。

## 最常见瓶颈

AXI DMA 最常见的性能瓶颈包括：

- burst 太短，header 与握手开销占比高
- 边界拆分过多，逻辑任务碎成很多小事务
- descriptor 提交过碎，软件控制开销高
- DDR / AXI 仲裁对该流量不友好
- completion 可见性或回收路径慢于数据路径

## 常见误解

常见误解：`AXI DMA 慢主要是 DMA engine 不够强`。实际上很多时候真正卡在 AXI burst 形状、仲裁和 memory return path。

常见误解：`AXI 上数据路径通了，就说明 DMA 没问题`。实际上 `R/B` 路径、completion 和缓存可见性同样必须闭环。

常见误解：`AXI DMA 只是基础案例，不需要系统级看`。实际上它是理解 DMA 如何映射到 BUS / RAM / software contract 的最好案例之一。

## 一句话理解

AXI DMA 是最典型的片上数据搬运器，理解它的关键不是背接口，而是看它如何把 descriptor 变成 AXI 事务，并在共享 fabric 上维持 steady-state。

## 建模启示

这张案例卡最适合把 AXI DMA 抽成 `descriptor -> burst sequence -> completion` 三段。

```text
AXIDMAProfile {
  burst_len
  max_outstanding
  split_rate
  completion_mode
}
```

在 `07-workloads-case-studies` 里，这类 profile 最适合映射到 `Interaction` 与 `Capability`。若只关心吞吐，可以忽略 completion mode；若关心软件行为和尾延迟，就必须保留。
