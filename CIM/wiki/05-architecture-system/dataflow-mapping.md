# 数据流与算子映射

## 为什么这一页重要

很多 CIM 设计在阵列层可以跑通矩阵乘，但真正一落到模型，就会遇到映射、切分、缓存和归约问题。这一页的核心任务，是把“一个能算的阵列”变成“一个能跑 workload 的系统”。

## 重点问题

- 是 `weight-stationary`、`input-stationary` 还是 `output-stationary`
- GEMM / Conv / Attention 分别如何切分到 array
- 激活和 partial sum 如何在 tile 间流动

## 三种常见数据流

### Weight-stationary

思路是尽量让权重驻留在阵列内，输入流过阵列，结果在外部累加或输出。

适合：

- 权重固定或复用高的算子
- MVM / GEMM 风格计算

代价：

- 输入搬运仍可能显著
- 多批次或多层之间的数据调度需要仔细设计

### Input-stationary

思路是尽量让输入驻留，权重分批加载。

适合：

- 输入复用率高的场景
- 某些局部卷积或窗口式访问

代价：

- 如果权重规模大，权重搬运成本会上升

### Output-stationary

思路是让 partial sum 尽量本地保留，减少中间结果移动。

适合：

- 归约成本高
- 需要多周期累加的设计

代价：

- 本地存储和控制复杂度可能增加

## 不同算子的映射关注点

### GEMM / MVM

这是最自然的 CIM 映射对象。主要看：

- 矩阵如何按阵列尺寸切块
- 权重是否能常驻
- partial sum 是否需要跨 tile 合并

### Conv

卷积通常要先考虑：

- 是否做 `im2col` 或其他 lowering
- lowering 带来的额外 buffer 成本是否值得
- 局部窗口复用是否能被阵列利用

### Attention

attention 不能只看一个矩阵乘，而要拆成：

- projection
- score 计算
- softmax
- value aggregation
- KV cache 访问

不同子步骤适合的硬件路径并不相同。

## 建议统一分析项

- 张量布局
- tiling 策略
- 映射粒度
- 片上缓存需求
- 控制流复杂度

## 做映射分析时建议补的字段

- array shape
- tile shape
- layer shape
- 数据流类型
- 权重是否常驻
- 激活来源
- partial sum 合并位置
- host 参与点

## 一个最常见的系统瓶颈

阵列本身不是瓶颈，但：

- 切块过碎导致 NoC 和 buffer 开销变大
- 归约路径过长导致吞吐下降
- host 与 accelerator 切换频繁导致延迟恶化

因此，映射设计本质上是在平衡：

- 阵列利用率
- 数据复用
- 通信开销
- 控制复杂度

## 后续可补充内容

- GEMM 映射例子
- Conv lowering 例子
- Attention / KV cache 映射例子
