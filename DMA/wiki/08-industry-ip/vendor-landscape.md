# DMA IP 与厂商图谱

上级：[08 DMA IP 与产业视角](./README.md)

相关：[DMA IP 评估清单](./dma-ip-checklist.md)

## 这页在回答什么问题

如果把 DMA 当作一类 IP 或系统能力来研究，应该看哪些玩家和哪些产品形态。

## 可以按三类对象看

- SoC / MCU 通用 DMA controller
- 高速 I/O 设备里的 device DMA
- AI / accelerator 内部专用 DMA

如果要和 overview 里的 taxonomy 对齐，更稳妥的理解是：每一类对象其实都是 `系统位置 + 主传输路径 + 控制模式 + coherence/translation 假设` 的组合。

## 研究时更值得关注什么

- 面向哪类总线和地址空间
- 是否支持 scatter-gather / ring / 多通道
- 是否支持 coherent / IOMMU / virtualization
- 性能旋钮和观测能力是否充分

## 一句话理解

DMA IP 的价值不在“有没有”，而在它是否匹配目标系统的数据路径、隔离要求和调优需求。
