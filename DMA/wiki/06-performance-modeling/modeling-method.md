# 从抽象模型到系统诊断

上级：[06 性能建模与调优](./README.md)

相关：[NOC：建模层次](../../NOC/wiki/05-modeling-evaluation/modeling-layers.md)、[AI 加速器里的 DMA](../07-workloads-case-studies/ai-accelerator-dma.md)

## 这页在回答什么问题

如果要建一个能解释 DMA 行为的模型，应该从哪里开始，按什么层次逐步补真实度。

## 第一层：理想带宽模型

回答：

- 理论上多久能搬完
- 哪个链路先达到上限

它适合建立上界，不适合解释 stall。

## 第二层：事务与队列模型

加入：

- descriptor/submit 开销
- outstanding limit
- request/response 分离
- queue 等待

这层开始能解释大量真实性能损失。

## 第三层：系统耦合模型

再加入：

- NoC 注入/回压
- local memory bank/port
- DDR/HBM latency 波动
- 多流优先级冲突

这层才足够支撑架构判断。

## 一个建模原则

先回答“哪一类约束在主导”，再决定是否加细节。  
不要一开始就做全精度仿真。

## 一句话理解

对 DMA 建模，关键不是先做最复杂，而是先做能稳定定位主瓶颈的最小分层模型。
