# 04 微架构与系统集成

这一部分关注 BUS 在真实芯片里是怎么落地的。

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

## 一句话总纲

BUS 一旦进入真实芯片，就不再是抽象协议，而是 `decoder + arbiter + crossbar + bridge + FIFO + adapter` 的组合工程。
