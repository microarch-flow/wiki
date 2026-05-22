# 04 微架构与系统集成

这一章讨论 BUS 在芯片里如何落地。前面章节把 BUS 拆成 transaction、ordering、backpressure、协议 channel 和 response；第 04 章把这些概念放进真实系统路径：互连组件、bridge、CDC、MMIO、boot、debug、DMA、IOMMU、DDR controller 和 interrupt flow。

## 本章入口

1. [互连组件与数据路径分解](./interconnect-components.md)
2. [Bridge、CDC 与 Width Adapter](./bridge-cdc-width-adaptation.md)
3. [Shared Bus、Bus Matrix 与 Crossbar](./shared-bus-bus-matrix-crossbar.md)
4. [MMIO、Cache 与 Interrupt 视角](./mmio-cache-interrupt-view.md)
5. [Boot Path 与地址映射初始化](./boot-path-address-map-initialization.md)
6. [Debug Path 与 System Access](./debug-path-system-access.md)
7. [IOMMU、SMMU 与 DMA 寻址](./iommu-smmu-dma-addressing.md)
8. [Doorbell、Completion 与 Interrupt Flow](./doorbell-completion-interrupt-flow.md)
9. [AXI 与 DMA 的系统接口](./axi-dma-system-interface.md)
10. [DMA Descriptor Fetch、Data Move 与 Writeback](./dma-descriptor-fetch-data-move-writeback.md)
11. [AXI 属性、Cacheability 与 Barrier](./axi-attributes-cacheability-barrier.md)
12. [AXI 到 DDR Controller 的路径](./axi-to-ddr-controller-path.md)
13. [Read/Write Combine 与 Bus Turnaround](./read-write-combine-turnaround.md)
14. [Row Locality、Return Path 与 AXI 体验](./row-locality-return-path-axi-experience.md)
15. [CPU、DMA、外设与内存之间的总线路径](./dma-cpu-peripheral-memory-path.md)

## 本章主线

第 04 章的核心判断是：BUS 一旦进入真实芯片，就不再是抽象协议，而是 `decoder + arbiter + crossbar + bridge + FIFO + adapter + controller + software contract` 的组合工程。

| 主题 | 关键问题 |
| --- | --- |
| 互连组件 | transaction 在哪里 decode、排队、仲裁、转换和释放 |
| bridge / CDC / width adapter | 协议、时钟和数据粒度转换如何改变语义 |
| shared bus / matrix / crossbar | 并发能力如何换取面积、布线和验证复杂度 |
| MMIO / cache / interrupt | 软件可见语义如何落到 BUS 属性和顺序上 |
| boot / debug | 非运行态路径如何保持最小可达和可诊断 |
| DMA / IOMMU / doorbell | 任务提交、翻译、搬运、完成和通知如何闭环 |
| AXI / DDR | 通用 transaction 如何进入受物理时序约束的 controller |

## 阅读顺序

建议按本章入口顺序阅读。前 3 篇建立互连组件和拓扑视角；第 4 到第 8 篇把软件语义、boot/debug、DMA 翻译和 interrupt flow 放进 BUS；第 9 到第 15 篇集中分析 DMA 与 DDR controller 的端到端路径。

若只想定位 DMA 类问题，可以从 [AXI 与 DMA 的系统接口](./axi-dma-system-interface.md) 开始，再读 [DMA Descriptor Fetch、Data Move 与 Writeback](./dma-descriptor-fetch-data-move-writeback.md)、[Doorbell、Completion 与 Interrupt Flow](./doorbell-completion-interrupt-flow.md) 和 [IOMMU、SMMU 与 DMA 寻址](./iommu-smmu-dma-addressing.md)。

若只想定位 DDR/AXI 体验问题，可以从 [AXI 到 DDR Controller 的路径](./axi-to-ddr-controller-path.md) 开始，再读 [Read/Write Combine 与 Bus Turnaround](./read-write-combine-turnaround.md) 和 [Row Locality、Return Path 与 AXI 体验](./row-locality-return-path-axi-experience.md)。

## 建模启示

第 04 章给模型提供系统集成层的状态变量。性能模型需要记录互连队列、仲裁点、bridge slot、CDC FIFO、DMA outstanding、IOMMU translation queue、DDR scheduler、return path 和 interrupt latency。功能模型需要记录 MMIO side effect、cache/coherence、barrier、地址翻译、错误返回、boot/debug 可达性、completion 可见性和 clear/EOI 顺序。

这一章的建模原则是：不要把 BUS 当成一条连线，也不要把协议名当成行为结论。每个软件流程都要拆成事件链，例如 `doorbell_write_accept`、`descriptor_fetch_done`、`data_write_done`、`completion_visible`、`interrupt_assert`、`clear_done`。只有把这些事件落到具体路径，才能解释系统为什么慢、为什么 hang、为什么 fault，以及软件为什么看不到硬件已经完成的事。
