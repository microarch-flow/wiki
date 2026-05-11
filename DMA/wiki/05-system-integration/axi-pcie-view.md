# AXI / PCIe 视角下的 DMA

上级：[05 系统集成](./README.md)

相关：[SoC 外设与 I/O DMA](./soc-peripheral-io.md)、[DMA 与 NoC](./dma-and-noc.md)

## 这页在回答什么问题

为什么同样叫 DMA，挂在 AXI 互连里的 DMA 和跑在 PCIe 设备里的 DMA，在约束和设计重点上会显著不同。

## AXI 视角常关心什么

- burst 长度和对齐
- multiple outstanding transaction
- read/write 通道解耦
- ID、乱序与返回路径

AXI DMA 更容易和片上 memory hierarchy、local SRAM、NoC 深耦合。

## PCIe 视角常关心什么

- host-device 地址映射
- posted/non-posted 行为
- PCIe read completion TLP 延迟
- DMA 与 descriptor ring、MSI-X、中断协同

这里的 `PCIe read completion` 是 PCIe 事务层语义，不要和软件侧说的 `DMA completion interrupt / completion record` 混成同一个 completion。

PCIe DMA 更强调设备和主机之间的系统契约。

## 一个有用的对照

AXI DMA 常像“片上供数器”，PCIe DMA 常像“设备侧搬运引擎”。  
两者都要处理队列和完成，但瓶颈与可见性语义不同。

## 一句话理解

从 AXI 看 DMA，更像片上数据路径问题；从 PCIe 看 DMA，更像 host-device 协议和软件栈协同问题。
