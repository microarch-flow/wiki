# IP 分析模板

上级：[09 参考资料与研究模板](./README.md)

## 这页在回答什么问题

分析一份 DMA IP 手册、第三方控制器或自研方案时，应该按什么结构记录，才能支持后续方案比较和集成决策。

## 推荐结构

```md
# IP 名称

## 定位

- 用于什么系统：
- 主要传输路径：
- 总线 / 互连环境：
- 控制模型：
- coherent / IOMMU 假设：
- 完成语义边界：

## 功能能力

- descriptor / queue 模型：
- scatter-gather：
- coherent / IOMMU：
- channels / QoS：

## 微架构能力

- outstanding：
- reorder / completion：
- stride / 2D / 3D：
- observability：
- fault / timeout / release：

## 软件与系统接入

- driver 模型：
- interrupt / polling / completion queue：
- virtualization / isolation：
- integration 风险：

## 最适合的场景

- 

## 主要短板

- 
```

## 为什么 IP 模板里要单列“integration 风险”

因为很多 DMA IP 方案纸面功能很强，但一旦接进真实系统，风险不在功能缺失，而在地址空间、completion 契约、fault containment 或 observability 不足。把这些内容放在同一张卡里，后续评审才不会只剩参数比较。

## 常见误解

常见误解：`IP 分析模板和论文模板差不多`。实际上 IP 分析更强调系统接入、软件契约和可诊断性。

常见误解：`只要功能都支持，integration 风险不会高`。实际上很多高风险点恰恰出现在功能边界和完成语义上。

## 一句话理解

分析 DMA IP，最重要的是把 `功能、微架构、系统接入、可诊断性和风险` 放在同一张卡里看。
