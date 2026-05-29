# 05 系统集成

这一部分把 DMA 放回完整系统里看。前面几章已经说明 DMA 任务如何被描述、硬件如何执行、软件如何同步；这一章回答的是：当 DMA 真正挂到 AXI、NoC、DDR/HBM、local SRAM、PCIe 和外设上时，它会如何被系统资源塑形，又会如何反过来塑形系统流量。

## 推荐阅读顺序

1. [DMA 与 NoC](./dma-and-noc.md)
2. [DMA 与 Local Memory / DDR / HBM](./dma-and-memory-system.md)
3. [SoC 外设与 I/O DMA](./soc-peripheral-io.md)
4. [AXI / PCIe 视角下的 DMA](./axi-pcie-view.md)

## 本章输出物

- 一条系统主线：DMA 的性能上限由 `端点 + 互连 + memory system + 软件节拍` 共同钳制
- 四条横向链接：DMA 如何映射到 AXI、DRAM row locality、NoC traffic pattern、PCIe TLP/completion
- 一套系统建模入口：Resource、Topology、Interaction、Capability 如何在 DMA 问题上落地
