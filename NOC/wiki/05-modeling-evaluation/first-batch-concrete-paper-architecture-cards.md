# 第一批具体论文卡与架构实例卡

上级：[建模与评估](./README.md)

相关：[第一批真实 NoC / Accelerator Case Cards](./first-batch-real-noc-accelerator-case-cards.md)、[AI Accelerator NoC Case Cards 与论文卡模板](./ai-accelerator-noc-case-cards-templates.md)

## 为什么要从 archetype 继续走到具体卡

archetype（架构原型）能帮你快速分类。  
具体卡则能逼你开始回答：

- 这个案例到底公开了哪些 NoC（片上网络）线索
- 哪些是可以拿来建模的
- 哪些只是营销表述

## Card 1：Google TPU 类阵列数据流

### Problem

- 如何在大规模矩阵计算中稳定供给数据

### NoC-Relevant Details

- 强规则数据流
- 强编译器映射
- 更偏阵列式数据移动，而不是复杂动态 packet fabric（数据包交换网络）

### What I Can Reuse

- 把规则 array 视为一种“高度结构化局部互连”参考
- 研究 dataflow（数据流）与 placement（放置策略）的耦合

### What I Still Doubt

- 不同 TPU 代际在片上互连细节公开程度有限

## Card 2：Cerebras WSE 类二维扩展

### Problem

- 如何在超大规模片上系统里保持可扩展通信

### NoC-Relevant Details

- 超大二维组织
- 强规则扩展
- 长路径和全局同步成为关键问题

### What I Can Reuse

- 思考二维扩展到极大规模时热点与长线代价

### What I Still Doubt

- 公开材料通常更偏系统叙事，具体 router（路由器）/ flow control（流量控制）细节有限

## Card 3：Tenstorrent / Tensix 类 tile dataflow

### Problem

- 如何让 tile（计算单元）、stream（数据流）、DMA（直接内存访问）、local memory（本地存储）协同工作

### NoC-Relevant Details

- tile-to-tile stream 很关键
- control / stream / DMA 的并存很关键
- destination buffering（目的端缓冲）/ local memory arbitration（本地存储仲裁）很关键

### What I Can Reuse

- 最接近你的主学习对象
- 很适合映射到 AI dataflow NoC simulator

### What I Still Doubt

- 公开资料是否足够支撑细粒度 cycle-accurate（周期精确）模型

## Card 4：Groq 类编译驱动静态通路

### Problem

- 如何尽可能把动态调度复杂度前移到编译期

### NoC-Relevant Details

- source-routing（源路由）/ static scheduling（静态调度）视角特别重要
- 路径静态化后，热点与灵活性的平衡很关键

### What I Can Reuse

- 研究 compiler-driven NoC（编译器驱动的片上网络）的价值边界

### What I Still Doubt

- 公开资料中的实现细节仍有限，需要谨慎外推

## 怎么用这批具体卡

每次看新论文或新架构时，优先加三句：

- 它更接近哪张已有卡
- 它在哪个 NoC 维度上不同
- 这个差异值得在 simulator（模拟器）里试什么实验

## 本页结论

这批具体卡的作用，不是替代正式论文阅读，而是先把“哪些公开案例对你的 NoC 主线最有参考价值”固定下来，避免后续阅读发散。
