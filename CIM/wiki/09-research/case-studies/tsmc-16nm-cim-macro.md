# TSMC 16nm CIM Macro

## 基本信息

- 类型：研究案例
- 路线：`SRAM / CMOS-compatible CIM`
- 归类：更接近片上 `CIM macro`
- 关键词：`16nm`, `edge AI`, `microscaling`, `CIM macro`

## 这是什么

TSMC Research 页面公开展示了一项与清华大学等合作的 `16nm` CIM macro 研究，主题是面向 edge AI 的多模式 gain-cell CIM macro。

这个案例的意义主要不在于“它是不是已经是量产产品”，而在于它代表了先进工艺、学术界和产业研究机构仍然在持续推进 CMOS-compatible CIM 宏设计。

## 为什么它重要

这个案例适合拿来理解 `SRAM-CIM` 路线的三个特点：

- 它强调与先进 `CMOS` 工艺结合
- 它关注的是片上 macro 级能效和边缘 AI 场景
- 它更接近“如何把 CIM 融入 SoC 体系”，而不是依赖新型非易失器件

## 应该如何看这类结果

这类研究通常最容易被误读。需要分清：

- 这是 `macro-level` 结果，不等于完整 chip 结果
- 高能效指标通常依赖特定精度和特定 workload
- 真实系统收益还取决于 buffer、NoC、controller 和外部存储访问

因此，这个案例最适合拿来训练这样一种判断：

一个很强的片上 CIM 宏，离“一个端到端更优的 AI 芯片”还有多远。

## 从技术路线看

### 它代表哪条路线

- `SRAM-CIM` 或至少是强 `CMOS` 兼容的片上 CIM 宏路线
- 更偏 edge AI，而非大容量外部内存路线

### 它的价值点

- 先进工艺下的高能效研究
- 片上集成可行性
- 对低功耗推理和小型模型更有现实意义

### 它的边界

- 容量仍然有限
- 很难单独承载大模型工作集
- 不能直接外推成大模型 system-level 收益

## 用本 wiki 的框架做判断

### 技术路线

- `SRAM-CIM`
- `macro-centric`

### 计算模式

- 更偏片上近数据计算
- 需要结合具体论文细节判断其 digital / analog / mixed-signal 属性

### 更适合的工作负载

- edge inference
- always-on AI
- 小模型或结构规整的算子

### 主要分析重点

- 它的 bitcell / macro 结构是什么
- 指标是否包含外围成本
- 它是否能自然接入 tile 和 SoC
- 其结果是研究样片、测试芯片还是接近产品化 IP

## 这个案例最适合放在哪条学习主线里

- `02-memory-technologies`：理解 SRAM-CIM
- `04-circuit-macro`：理解宏设计指标
- `05-architecture-system`：理解 macro 和 chip 的距离
- `07-workloads`：理解 edge AI 的适配性

## 参考来源

- TSMC Research 页面：<https://research.tsmc.com/page/artificial-intelligence/1.html>
