# DMA IP 与厂商图谱

上级：[08 DMA IP 与产业视角](./README.md)

相关：[DMA IP 评估清单](./dma-ip-checklist.md)、[DMA 分类框架](../01-overview/taxonomy.md)

## 这页在回答什么问题

如果把 DMA 当作一类 IP 或系统能力来研究，应该先按什么维度切市场与产品形态；以及为什么“谁家有 DMA IP”本身不是最有价值的问题。

## 先按系统位置和主路径分，再看厂商和产品

研究 DMA IP 时，最容易犯的错误是先按厂商名单或营销名字分类。这样做会很快得到很多标签，却很难建立判断力。更稳的做法是先按系统位置和主传输路径切市场：

- SoC / MCU 通用 DMA controller
- 高速 I/O 设备里的 device DMA
- GPU / accelerator / AI 内部专用 DMA
- 面向特定协议或外设的专用 DMA block

这种切法的价值在于，它先保住“这类 IP 到底服务哪条系统路径、承担哪类完成语义、被什么资源钳制”这些更本质的问题。厂商和产品名称应该是第二层信息，而不是第一层。

## 真正值得关注的是哪几类产品差异

一旦系统位置确定，接下来最有价值的差异通常不是品牌，而是这些结构性问题：

- 它面向哪类总线和地址空间
- 它的控制模型是寄存器、descriptor、ring 还是 command queue
- 它是否支持 coherent、IOMMU、virtualization
- 它的 performance knobs 和 observability 是否充分

换句话说，DMA IP 的价值不在“有没有 scatter-gather”这类孤立 feature，而在这组 feature 是否和目标系统路径一起成立。

## 为什么厂商图谱仍然有价值

虽然不应该先按厂商研究，但厂商视角仍然有用，因为它能帮助你快速判断某类产品的典型偏好。例如，有些 IP 长于 MCU/外设 DMA，强调低复杂度和稳定节拍；有些长于 PCIe / device DMA，强调 queue、completion 和虚拟化；有些则更偏 AI / local DMA，强调 stride、outstanding 和片上耦合。

这类“家族画像”有助于你在看文档前就建立合理预期：这份 IP 手册最可能把复杂度放在哪，最可能在哪些方面留下空白。

## 研究 DMA IP 时最不值钱的信息

最不值钱的通常是脱离条件的峰值数字，例如“最大带宽 X GB/s”“支持 N 个通道”。这些数字当然不能完全忽略，但它们如果没有上下文，几乎不能用于方案判断。因为：

- 峰值带宽不说明 completion 路径能否闭环
- 通道数不说明资源是否真分离
- 支持 coherent 不说明一致性流量代价
- 支持 2D/3D 不说明 memory system 是否喜欢这种访问形状

所以厂商图谱页真正要做的不是列参数，而是先把“看参数之前该先确认什么”讲清楚。

## 常见误解

常见误解：`DMA IP 差异主要看峰值带宽和通道数`。实际上这些只反映局部上界，不反映系统匹配度。

常见误解：`不同厂商的 DMA IP 可以按功能勾选表直接对比`。实际上如果系统位置和完成语义不同，功能表很容易误导。

常见误解：`AI DMA、PCIe DMA、MCU DMA 都是 DMA，所以放在一起看没有问题`。实际上可以放在一起看，但前提是先保留各自的系统画像。

## 一句话理解

DMA IP 的价值不在“有没有”，而在它是否匹配目标系统的数据路径、完成语义、隔离要求和调优需求。

## 建模启示

这一页适合把 IP 研究对象先压成 profile，而不是一开始就抄规格表。

```text
DMAIPClass {
  system_position
  dominant_path
  control_model
  visibility_model
}
```

若只想做粗筛，这四项就足够把大多数产品放进正确篮子；若要做深入评审，再逐步补 `outstanding_depth`、`virtualization`、`observability` 等能力项。
