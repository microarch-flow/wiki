# DMA IP 评估清单

上级：[08 DMA IP 与产业视角](./README.md)

相关：[DMA 引擎的组成](../03-dma-microarchitecture/engine-components.md)、[优化与调参手册](../06-performance-modeling/optimization-playbook.md)、[观测、计数器与调试路径](../06-performance-modeling/debug-observability.md)

## 这页在回答什么问题

当你要评估一套 DMA IP、自研 DMA 方案或第三方控制器时，应该问哪些问题；以及为什么“功能支持列表”通常远远不够。

## 先问它要服务哪条系统路径

在打开 feature list 前，第一件事应该是确认目标系统画像：

- 它搬的是哪条路径：peripheral、memory-to-memory、host-device、local-to-local
- 它的完成语义是偏硬件闭环，还是偏软件可见
- 它最主要面对的是 CPU/driver、device firmware，还是 compiler/runtime

这一步很关键，因为 DMA IP 的很多能力是否有价值，都取决于它服务哪条路径。面向固定外设流的 DMA，不需要照抄 PCIe device DMA 的 queue 模型；面向多租户设备的 DMA，则不能只满足 MCU 级别的简单完成语义。

## 功能层该看什么

功能层最少要看：

- 支持哪些传输路径
- 是否支持 scatter-gather / linked-list / cyclic / ring
- 是否支持多通道、多优先级、多队列
- completion、中断、错误上报是否清晰

这里的关键不是“feature 越多越好”，而是 feature 是否正好覆盖目标场景。多余的通用性会带来状态复杂度，缺失的能力则会把复杂度外包给软件。

## 微架构层该看什么

微架构层最有价值的几个问题是：

- 最大 outstanding 能到什么量级
- burst 策略和边界拆分如何组织
- response / completion 的回包组织能力如何
- stride / 2D / 3D 地址生成支持到什么程度
- fault / timeout / resource release 路径是否明确

这一层决定的是“这套 IP 能否真正兑现其 feature list”。很多 DMA 看起来功能都支持，但一到复杂流量和深队列 steady-state 就露出微架构短板。

## 系统接入层该看什么

系统接入层通常比 feature list 更能决定实际价值。要重点问：

- coherent / non-coherent 模式如何支持
- IOMMU / SMMU / virtualization 如何接入
- 与 AXI / PCIe / NoC / local SRAM 的耦合方式是什么
- fault containment 和 context isolation 是否完整

如果这些边界讲不清，DMA IP 即使单独功能不错，放进真实系统里也容易变成后期 integration 成本。

## 软件层和可观测性层不能后看

很多评审容易把软件接口和 observability 放到最后，甚至当成附属项。但对 DMA 来说，它们经常直接决定 bring-up 和优化成本。至少要看：

- driver 模型是否清晰
- queue / ring / completion 契约是否稳定
- runtime / compiler 是否容易接入
- counter、histogram、phase state 是否足够定位问题

没有这些，DMA IP 的硬件能力再强，也可能在系统里不好用。

## 一个更实用的评估顺序

1. 先判定系统画像是否匹配。
2. 再看功能层有没有关键缺口。
3. 再看微架构是否足以兑现这些功能。
4. 再看系统接入与软件契约是否完整。
5. 最后看 observability 和调优空间是否足够。

这个顺序能避免评审一开始就被 feature list 或 marketing number 带偏。

## 常见误解

常见误解：`评估 DMA IP 主要看峰值带宽`。实际上带宽只反映局部上界，不反映完成路径、隔离和调优空间。

常见误解：`功能支持到位就够了`。实际上很多问题会在微架构兑现能力、系统接入和 observability 层暴露。

常见误解：`软件接口是后面的事`。实际上 queue、completion、error handling 契约如果不清楚，集成成本会很高。

## 一句话理解

评估 DMA IP，不能只看它“会不会搬”，必须同时看 `系统画像匹配度、微架构兑现能力、系统接入完整性和可诊断性`。

## 建模启示

这一页适合把评估问题显式参数化，形成可复用模板。

```text
DMAIPEval {
  path_match
  feature_fit
  microarch_headroom
  integration_risk
  observability_score
}
```

如果只做早期筛选，可以把每项压成高/中/低；如果做深入方案评审，则应把每项展开成具体问题和证据来源。
