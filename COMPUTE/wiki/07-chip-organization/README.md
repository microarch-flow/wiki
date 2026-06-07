# 07 · 芯片顶层组织:从一个核到一片芯片

[02–06 章](../02-datapath-foundations/) 搭出门、阵列、流水、存储。本章把它们拼成核、再拼成整片芯片,并回答三个顶层问题:CPU 和 GPU 核的面积差在哪、芯片为什么时钟这么快、GPU 和 TPU 的顶层布局如何取舍。

## 篇目

1. **[CPU vs GPU core:面积都花在哪了](./cpu-vs-gpu-core-area.md)**
   排除法:cache/RF/ALU 都不是关键区别;真正大头是 branch predictor;AI 无复杂分支→砍掉几乎无损;这是一连串"砍分母"专门化中的一个。

2. **[脑 vs 芯片:为什么时钟这么快,降频能不能省能](./brain-vs-chip-power.md)**
   存算一体不是脑独有;快时钟为高吞吐(batch 1000 vs batch 1);动态功耗∝翻转次数,降频近线性省总能但非单次能效;⚠️先进节点 leakage 侵蚀降频收益(现实修正)。

3. **[GPU = 一堆平铺的小 TPU](./gpu-as-tiled-tpu.md)** ← 主线收口
   缩小 TPU = 一个 SM;粗粒度 vs 细粒度对比表(2 线 vs 16 线示意);跨 SM 才贵;MatX splittable array + HBM+SRAM 混合"两列都要"。

## 本章在主线上的位置

本章是[主线](../01-overview/compute-communication-ratio.md)的收口:
- §cpu-vs-gpu:专门化 = 砍掉 AI 不需要的分母(分支预测)。
- §brain-vs-chip:功耗视角的比值(每次翻转能量 vs 总翻转数)。
- §gpu-as-tiled-tpu:顶层布局是比值在**跨单元数据移动**上的最后一战。"大粒度摊薄固定成本"在此推到最高层(systolic 摊 mux → 大阵列摊 RF → 粗粒度摊整片布局)。

→ 怎么把这一切喂进仿真器?进入 [08 · 面向 archax 的建模](../08-modeling-for-archax/)。
