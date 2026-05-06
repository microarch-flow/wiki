# CIM 在解决什么问题

## 一句话定义

`Compute-In-Memory` 的核心目标不是简单把算力做得更高，而是把适合靠近数据的计算推进到存储阵列内部或附近，以减少数据搬运带来的能耗和带宽损失。

## 为什么会出现 CIM

传统处理器、GPU、NPU 的主路径大致如下：

```text
DRAM / HBM
  ↓
SRAM / Cache / Scratchpad
  ↓
MAC Array / Tensor Core / Vector Unit
```

这条路径的问题是，权重、激活和中间结果需要在多个层级之间反复流动。很多情况下，真正昂贵的不是一次乘加，而是把数据搬来搬去。

因此，CIM 要解决的不是抽象意义上的“算得更快”，而是更具体的几个系统问题：

- `memory wall`：存储访问速度和带宽逐渐成为系统瓶颈
- `data movement energy`：数据搬运能耗在很多 AI 任务中高于计算本身
- `memory-bound workload`：一些负载不是算不动，而是喂不饱

## CIM 试图改变什么

与传统路径相比，CIM 会把部分计算推进到 memory array 附近：

```text
Memory Array
  + local compute
  + local reduction
  + local ADC / DAC / SA / logic
```

这里有两个常见误解需要先避免：

- CIM 不等于“所有计算都在内存里做”
- CIM 也不等于“任何带内存的加速器都叫 CIM”

更准确的说法是：CIM 只把最适合靠近数据的那一部分操作下沉，例如矩阵向量乘、点积、位运算和局部归约。

## 哪些数据搬运最值得减少

研究或评估任何一条 CIM 路线时，都应先问清楚它减少的是哪一层搬运：

- 权重从 `DRAM / HBM` 到片上 buffer 的搬运
- 激活在层间和 tile 间的搬运
- `KV cache` 在 decode 阶段的大量访问
- partial sum 在多个 macro 或 tile 之间的归约搬运

如果这个问题没有回答清楚，那么高能效指标通常很难转化成真实系统收益。

## 与 AI workload 的关系

不同任务的瓶颈不同，CIM 的价值也不同。

| workload | 主要瓶颈 | CIM 潜在价值 |
| --- | --- | --- |
| CNN | 结构规整，权重复用高 | 适合作为早期映射对象 |
| Transformer prefill | 大矩阵计算，算力密集 | 不一定优于成熟 GPU / NPU |
| Transformer decode | batch 小，KV cache 压力大 | 更可能受益于 PIM / CIM |
| Long context | memory bandwidth 压力大 | near-memory / PIM 更有潜力 |
| MoE | 路由和稀疏访问复杂 | 有机会，但系统难度高 |

## 判断一条 CIM 路线是否成立的起点

后续每看一个宏、芯片、公司或论文，都应该先回答这三个问题：

1. 它到底减少了哪一级数据搬运？
2. 它针对的是哪类 workload 的什么瓶颈？
3. 它的收益是 `macro-level` 还是 `system-level`？

## 本页建议继续补充

- Memory wall 简史
- Data movement energy 对比表
- Prefill / Decode / Long context 的瓶颈拆解
