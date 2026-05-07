# DMA IP 评估清单

上级：[08 DMA IP 与产业视角](./README.md)

相关：[DMA 引擎的组成](../03-dma-microarchitecture/engine-components.md)、[优化与调参手册](../06-performance-modeling/optimization-playbook.md)

## 这页在回答什么问题

当你要评估一套 DMA IP、自研 DMA 方案或第三方控制器时，应该看什么。

## 功能层

- 支持哪些传输路径
- 是否支持 scatter-gather / linked list / cyclic
- 是否支持多通道、多优先级、多队列
- 完成、中断、错误上报是否清晰

## 系统层

- coherent / non-coherent 模式
- IOMMU / SMMU / virtualization 能力
- 与 NoC / AXI / PCIe / local SRAM 的耦合方式
- 安全隔离和 fault containment

## 性能层

- 最大 outstanding
- burst 策略
- 回包重组能力
- 可观测计数器和调试接口

## 软件层

- driver 复杂度
- queue/ring 模型是否清晰
- runtime / compiler 是否容易接入

## 一句话理解

评估 DMA IP，不能只看峰值带宽，必须同时看语义完整度、系统适配性、调优空间和可观测性。
