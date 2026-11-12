# CPU / GPU / NPU 系统中的 DMA 分工

上级：[07 工作负载与案例](./README.md)

相关：[DMA 分类框架](../01-overview/taxonomy.md)、[AI 加速器里的 DMA](./ai-accelerator-dma.md)、[GPU Copy Engine 案例卡](./gpu-copy-engine-case-card.md)

## 这页在回答什么问题

为什么不同计算平台都需要 DMA，但它们关心的重点完全不同；以及同样叫 DMA，CPU/SoC、GPU、NPU 为什么会在软件接口、性能瓶颈和完成语义上分化成三套画像。

## CPU / SoC：DMA 更像系统基础设施

在 CPU/SoC 世界里，DMA 主要服务于 I/O、memory hierarchy 和 OS/driver 协同。它的关键问题通常是：

- 如何减轻 CPU 对外设或大块搬运的逐次介入
- 如何与 cache coherence、IOMMU、interrupt 和 AXI 共享仲裁协同
- 如何在通用软件栈里定义清楚 buffer 生命周期与完成语义

所以 CPU/SoC DMA 更关注软件语义、地址空间和协议边界，而不一定追求极端的数据供给节拍。

## GPU：DMA 更像异步数据通路

GPU 世界里的 DMA 常以 copy engine、async memcpy、stream transfer 的形式出现。它最重要的价值不是“能拷贝”，而是让 host-device 或 device-device 数据传输尽量不阻塞 compute queue。

因此 GPU DMA 更关心：

- host-device 链路效率
- copy 与 kernel 的并行
- pinned memory、stream、event 与 completion 的协同
- 多 engine、多 stream 的并发管理

它更像一条异步数据通路，而不是简单的 I/O 搬运器。

## NPU / AI accelerator：DMA 更像供数调度器

NPU 世界里的 DMA 则进一步从“异步数据通路”演化成“供数调度器”。它直接决定 local memory 是否 ready、NoC 上的 refill / writeback 是否平衡、compute 是否持续饱和。

所以 NPU DMA 更关心：

- tile 粒度与 double buffering
- local SRAM port / bank 冲突
- outstanding 与 HBM latency hiding
- NoC traffic pattern 与 multi-stream 调度

它面对的不是“尽量不阻塞 CPU/GPU”，而是“尽量不让 compute 阵列断供”。

## 这三类系统最核心的差别在哪里

如果把三者压成一句话：

- CPU/SoC DMA 更偏系统软件与 I/O 语义
- GPU DMA 更偏异步数据通道与 compute-overlap
- NPU DMA 更偏片上供数与执行节拍

它们共享 descriptor、queue、completion 这些名词，但“慢”是什么意思、“完成”是什么意思、“最值得调的旋钮”是什么，往往完全不同。

## 常见误解

常见误解：`所有 DMA 优化思路都能跨平台复用`。实际上 CPU/SoC、GPU、NPU 的关键约束差异很大，移植调优策略时必须先换系统画像。

常见误解：`GPU 和 NPU DMA 只是带宽不同`。实际上 GPU 更强调 host/device 异步协同，NPU 更强调片上供数节拍。

常见误解：`CPU 系统里的 DMA 不需要关心 steady-state`。实际上 NIC、NVMe、display、camera 这些路径同样高度依赖 steady-state，只是形态不同。

## 一句话理解

同样叫 DMA，CPU 系统更关注软件和 I/O 契约，GPU 更关注异步数据通路，NPU 更关注片上供数与执行节拍。

## 建模启示

这页适合先定义三类案例的 profile，而不是直接混进一个统一模型。

```text
DMAPlatformProfile {
  platform: cpu_soc | gpu | npu
  dominant_path
  completion_boundary
  main_bottleneck_class
}
```

在 `07-workloads-case-studies` 里，这类 profile 最适合作为 `Topology` 与 `Interaction` 的选择器。不同平台的主瓶颈和 completion 语义不同，模型不应强行共用一套默认假设。
