# Systolic array：用局部传递和复用组织计算

上级：[03 · systolic array](./README.md)
相关：[dataflow 分类](./dataflow-taxonomy.md)、[权重加载](./weight-loading-and-trickle-feed.md)、[阵列 sizing](./array-sizing-tradeoff.md)

## 工作方式

Systolic array 由多个处理单元（PE）和邻近连接组成。输入数据沿预定方向传播；PE 执行乘加并保存或传递部分和。具体采用 weight-stationary、output-stationary 等 dataflow 时，驻留和移动的张量不同。输入、权重和结果仍须跨越阵列边界。

## 一个具单位的阵列边界例子

假设 `y=3` 行、`x=2` 列，对一个长度为 3 的输入向量计算两个输出。每个权重和输入为 1 B，每个输出为 4 B。一次计算完成 6 MAC；假设权重已驻留，3 B 输入和 8 B 输出跨越阵列边界，则强度为 `6/(3+8)=6/11 MAC/B`。若 6 B 权重也在同一窗口首次加载，强度为 `6/17 MAC/B`。

这是手算假设，不是实测阵列。它只统计指定阵列边界，未统计 PE 间传递、RF 内部读写或片外存储。复用次数、换 tile、填充和输出位宽可能改变有效 MAC 数或跨边界字节。同步和纯 backpressure stall 若只延长完成时间，没有引发重传或额外读写，则不改变该窗口内的字节和 MAC/B，却降低 MAC/s；若重传或重新加载，需将额外字节计入。其他边界需要独立计数。若峰值并行度为 `x*y MAC/cycle`，也仍需根据真实利用率与频率得到有效吞吐。

## 面积和带宽不能由此直接推出

[三个 mux 与乘法器的 `24p/4p` 代理](../02-datapath-foundations/mux-and-data-movement-cost.md)是静态结构估算；本页 `MAC/B` 是某工作量跨特定边界的流量指标。两者单位和分母不同，不能说前者“翻转”为后者，也不能从阵列行数推断实芯片面积或任务加速比。

复用有潜在收益，也需承担权重存储、阵列互连、控制、启动与排空、低填充率和供数压力。比较其他结构时应固定功能、精度、工作量和统计边界，分别比较面积、延迟、吞吐与能耗。

## 5. 与 CIM 的边界

普通 systolic PE 从本地寄存器等存储中读取权重，由独立算术电路计算。CIM 则在 memory cell 或其阵列读出路径中执行部分计算。局部驻留不等同于 CIM；具体分类见 [CIM taxonomy](../../../CIM/wiki/01-overview/cim-pim-nmc-taxonomy.md)。

## 建模启示

记录阵列形状、dataflow、输入/输出/权重位宽、复用次数、tile 与填充、PE 利用率、阵列边界及其他层的流量。记录冷启动、换 tile、供数和结果回收。事件可表示为 `LoadWeight`、`FeedInput`、`Mac`、`MovePartialSum` 和 `EmitOutput`；按依赖及资源计算时间，再分别输出 MAC/B、MAC/s、面积与能耗。
