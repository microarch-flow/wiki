# 03 · Systolic Array:把循环上提一层,翻转计算 / 通信比

[02 章](../02-datapath-foundations/) 留下一个 1:6 的劣势:裸 datapath 上搬运碾压计算。本章给解——把矩阵乘的循环再往上提两层、固化进硬件,让一份跨边界搬运喂一整片做乘加的 PE,比值从 1:6 翻转成 y(阵列行数量级)。

## 篇目

1. **[为什么要 systolic array](./why-systolic-array.md)**
   compute 涨 x·y、通信只涨 x、净赚 y 倍;用通用性换比值;与 CIM 的边界(驻留处是否就是计算处)。

2. **[Dataflow 分类:weight / output / row stationary](./dataflow-taxonomy.md)** `[补全]`
   让哪个张量驻留 = 消除哪个张量的搬运;三种 stationary 的尖锐对比 + 什么 workload 选谁;小 batch 让所有 dataflow 失效的反例。

3. **[权重载入与 trickle-feed](./weight-loading-and-trickle-feed.md)**
   载入只发生一次→优化带宽而非延迟;daisy-chain 把布线压在 x 量级;"配置流 vs 数据流"二分的原型。

4. **[阵列 sizing:阵列多大、RF 多大](./array-sizing-tradeoff.md)**
   一对抢面积的耦合变量;大阵列摊薄 RF(128×128 TPU);利用率与跨边界布线的反向约束;splittable 的动机。

## 本章在主线上的位置

这是主线的**第一次大幅抬升**:从裸 datapath 的 1:6 劣势翻转到 y 的优势。核心手段是"放大固定功能逻辑的粒度,摊薄进出口的税"——这个论点本章出现两次(systolic 摊薄 mux、大阵列摊薄 RF),并将在 [§07 GPU=平铺 TPU](../07-chip-organization/gpu-as-tiled-tpu.md) 升级为全局布局决策。

→ 阵列要跑多快?进入 [04 · 时钟与流水](../04-clocking-and-pipeline/)。
