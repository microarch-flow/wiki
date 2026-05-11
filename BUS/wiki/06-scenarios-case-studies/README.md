# 06 典型系统与案例

这一部分把 BUS 放回具体系统里看，帮助你建立“为什么这里这样设计”的判断。

## 本章入口

1. [MCU / SoC / AI 芯片中的 BUS 对照](./mcu-soc-ai-bus-comparison.md)
2. [AXI Crossbar 案例卡](./axi-crossbar-case-card.md)
3. [APB Peripheral Subsystem 案例卡](./apb-peripheral-subsystem-case-card.md)
4. [CPU 读 MMIO 卡死案例卡](./cpu-mmio-read-hang-case-card.md)
5. [DMA Completion 丢失案例卡](./dma-completion-missing-case-card.md)
6. [IOMMU Fault 案例卡](./iommu-fault-case-card.md)
7. [AXI vs TileLink 对照](./axi-vs-tilelink-comparison.md)
8. [AI 芯片里的 BUS vs NoC](./bus-vs-noc-in-ai-chip.md)
9. [APB、MMIO 与普通内存的软件模型对照](./apb-mmio-memory-software-model.md)

## 一句话总纲

脱离系统场景谈 BUS，容易把协议能力和系统需求错配；真正的判断来自具体场景里的 `流量类型、成本边界、扩展规模`。
