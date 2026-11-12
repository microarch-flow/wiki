# 07 工作负载与案例

这一部分把 DMA 放到具体系统和 workload 里看。前面几章已经建立了概念、微架构、软件契约和系统集成主线；这一章回答的是：为什么不同系统里的 DMA 会长成不同样子，它们各自最核心的约束是什么，以及建模时该保留哪些状态。

## 推荐阅读顺序

1. [AI 加速器里的 DMA](./ai-accelerator-dma.md)
2. [CPU / GPU / NPU 系统中的 DMA 分工](./cpu-gpu-npu-comparison.md)
3. [嵌入式多媒体与存储/网络路径](./embedded-storage-network.md)
4. [HBM 到 Tile 的数据供给链](./hbm-to-tile-data-supply-chain.md)
5. [AXI DMA 案例卡](./axi-dma-case-card.md)
6. [PCIe NIC DMA 案例卡](./pcie-nic-dma-case-card.md)
7. [NVMe / 存储路径中的 DMA](./nvme-storage-dma-case-card.md)
8. [GPU Copy Engine 案例卡](./gpu-copy-engine-case-card.md)
9. [AI Local DMA 案例卡](./ai-local-dma-case-card.md)

## 本章输出物

- 一张系统画像：不同 DMA 类型最核心的路径、瓶颈和完成语义是什么
- 一条案例化主线：同样叫 DMA，为什么 CPU/SoC、GPU、NIC、NVMe、NPU 的关注点会完全不同
- 一组建模入口：每种案例最少要保留哪些状态和事件，才能解释真实系统行为
