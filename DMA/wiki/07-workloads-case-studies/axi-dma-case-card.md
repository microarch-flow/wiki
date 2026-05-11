# AXI DMA 案例卡

上级：[07 工作负载与案例](./README.md)

相关：[AXI / PCIe 视角下的 DMA](../05-system-integration/axi-pcie-view.md)、[地址、描述符与 Burst](../02-fundamentals/address-descriptor-burst.md)

## 这页在回答什么问题

把一个典型片上 `AXI DMA` 放回 SoC 环境中，应该如何理解它的职责、瓶颈和设计重点。

## 典型系统位置

- 位于 AXI interconnect 上
- 面向 DDR、片上 SRAM、外设 FIFO 或 accelerator buffer
- 常和 CPU、cache、NoC、memory controller 共用片上带宽

## 它通常在解决什么问题

- 把流式外设数据搬进内存
- 把内存数据送到 accelerator 或外设
- 用较低 CPU 开销完成大块 memory-to-memory 搬运

## 核心机制

- descriptor/linked-list
- AXI read/write burst
- multiple outstanding transaction
- interrupt 或 polling completion

## First Bring-Up 先看什么

- 当前路径是 coherent 还是 non-coherent
- descriptor/buffer 写进的是物理地址还是 IOVA
- cache flush / invalidate 和 barrier 语义是否匹配
- 对齐、page 边界和 burst 拆分规则是否满足

## 最常见瓶颈

- burst 长度太短
- 边界拆分过多
- descriptor 提交频率太高
- DDR / AXI 仲裁不利

## 最值得抄走的判断

AXI DMA 的瓶颈往往不是“DMA 算法”，而是 `burst 组织 + AXI 仲裁 + 内存端行为`。

## 一句话理解

AXI DMA 是最典型的“片上数据搬运器”，理解它能帮助你建立 DMA 与总线、内存、外设协同的基本判断。
