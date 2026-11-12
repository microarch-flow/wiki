# 案例索引

上级：[09 参考资料与研究模板](./README.md)

相关：[工作负载与案例](../07-workloads-case-studies/README.md)、[DMA 对照矩阵](../08-industry-ip/dma-comparison-matrix.md)

## 这页在回答什么问题

如果你想把 DMA wiki 继续扩成案例库，当前有哪些页面已经形成了稳定系统画像；以及后续补新案例时，应该按什么口径接入，而不是重新发散出一套新分类。

## 当前已有案例页

- [AXI DMA 案例卡](../07-workloads-case-studies/axi-dma-case-card.md)
- [PCIe NIC DMA 案例卡](../07-workloads-case-studies/pcie-nic-dma-case-card.md)
- [NVMe / 存储路径中的 DMA](../07-workloads-case-studies/nvme-storage-dma-case-card.md)
- [GPU Copy Engine 案例卡](../07-workloads-case-studies/gpu-copy-engine-case-card.md)
- [AI Local DMA 案例卡](../07-workloads-case-studies/ai-local-dma-case-card.md)
- [HBM 到 Tile 的数据供给链](../07-workloads-case-studies/hbm-to-tile-data-supply-chain.md)
- [AI 加速器里的 DMA](../07-workloads-case-studies/ai-accelerator-dma.md)
- [CPU / GPU / NPU 系统中的 DMA 分工](../07-workloads-case-studies/cpu-gpu-npu-comparison.md)
- [嵌入式多媒体与存储/网络路径](../07-workloads-case-studies/embedded-storage-network.md)

## 下一批建议补的案例

- camera / ISP DMA
- display / multimedia scanout DMA
- RDMA / SmartNIC DMA
- CXL 相关 DMA / memory movement
- chiplet / die-to-die 数据移动路径

## 新增案例时建议固定补的四件事

每新增一页案例，至少要补四件事：

1. 它处在系统哪里，主要搬哪条路径。
2. 它最核心的完成语义和稳态目标是什么。
3. 它最常见的瓶颈是什么，为什么不是别的地方。
4. 最小建模 profile 需要保留哪些状态或事件。

只要这四件事都在，案例页就能接回 01-08 章主线；缺任何一项，案例通常都会退化成“有趣的对象介绍”。

## 常见误解

常见误解：`案例库就是持续加名词`。实际上案例库的价值在于持续建立可比较的系统画像。

常见误解：`同类案例只要列一个就够了`。实际上同类路径里 completion 语义、steady-state 目标和瓶颈位置往往仍然会显著不同。

## 一句话理解

案例索引的价值不在“收集很多 DMA 名字”，而在于持续维护一套可比较、可回接主线的系统画像库。
