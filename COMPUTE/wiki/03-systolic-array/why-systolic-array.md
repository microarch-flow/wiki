# 为什么要 systolic array:把循环上提一层,翻转计算 / 通信比

上级:[03 · systolic array](./README.md)
相关:[mux 与数据搬运成本](../02-datapath-foundations/mux-and-data-movement-cost.md)、[dataflow 分类](./dataflow-taxonomy.md)、[权重载入与 trickle-feed](./weight-loading-and-trickle-feed.md)、[阵列 sizing](./array-sizing-tradeoff.md)
主线:[计算 / 通信比](../01-overview/compute-communication-ratio.md)——本篇是主线第一次**大幅抬高比值**:compute 涨 x·y,通信只涨 x。

---

## 这页在回答什么问题

[mux-and-data-movement-cost](../02-datapath-foundations/mux-and-data-movement-cost.md) 留下一个 1:6 的劣势:裸 datapath 上,搬运碾压计算。systolic array 怎么把它翻转?核心一句话:**把矩阵乘的循环再往上提两层,固化进硬件——让一份跨边界的数据搬运,喂给一整片在做乘加的 PE。**

---

## 1. 从"固化一次 MAC"到"固化整个矩阵-向量乘"

回顾抽象层级的爬升:

```
datapath:       把"一次 MAC"固化进硬件        → 每次 MAC 要 3 个 mux 喂数(1:6 劣势)
systolic array: 把"整个矩阵-向量乘"固化进硬件  → 一份向量喂一整列 PE
```

**因为** 更大粒度的固定功能逻辑,能让进出口的"税"摊得更薄;**所以** 不再为每一次乘加单独付 mux 选数的成本,而是让数据在阵列里"流过"一排排 PE,每个 PE 顺手做一次乘加。

---

## 2. 比值翻转的算术:净赚一个 y 倍

设阵列 x 列 × y 行。做一次矩阵-向量乘:

```
compute(有用乘加):  x · y       ← 阵列里每个 PE 都做一次 MAC
communication(跨边界):  x       ← 只有进出的向量跨阵列边界
                     ─────────────────────────────────
比值 = compute / comm = x·y / x = y
```

对比裸 datapath 的 ~1:6,systolic array 的比值变成 **y**(阵列行数量级)。**净赚一个 y 倍的 advantage**——这就是把循环上提的全部收益。

> 直觉来源:矩阵乘有"额外一维"。你做大量乘法(x·y 次)才出一组点积值,所以可以**在出一个值之前,把大量乘法塞进去**——计算 / 通信比天然有利,只要你别在每次乘加时都跨边界搬数。systolic array 就是把"跨边界"推迟到只在向量进出时发生。

```
        in: v0  v1  v2          ← 输入向量从顶部灌入,逐拍向下流
            │   │   │
        ┌───▼───▼───▼───┐
        │  PE  PE  PE   │       ← 每个 PE 内驻留一个权重,做 MAC
        │  PE  PE  PE   │          数据在阵列内"流过",不回 RF
        │  PE  PE  PE   │
        └───┬───┬───┬───┘
            ▼   ▼   ▼
        out(沿列累加,从底部出)   ← 只有这里和顶部跨边界
```

注意图里:**阵列内部 PE 之间的数据传递是局部的、短距离的**(隔壁 PE),不经过昂贵的全局 mux/RF;只有最顶(灌输入)和最底(出结果)跨阵列边界。分母从"每次 MAC 一组 mux"压成"每个向量一次进出"。

---

## 3. 这解决的正是 datapath 的病

把 §2 和 [datapath 的病](../02-datapath-foundations/mux-and-data-movement-cost.md#3-为什么无脑加大-register-file会被反噬) 对照:

| | 裸 datapath(CUDA core) | systolic array |
|---|---|---|
| 每次 MAC 的取数 | 3 个 n×p mux,贵且每次都付 | 数据从隔壁 PE 流入,局部短线 |
| 比值 | ~1:6(搬运碾压) | y(计算碾压) |
| 灵活性 | 任意指令、任意取数 | 只会做矩阵乘 |
| 代价 | 灵活但搬运昂贵 | 专用但搬运便宜 |

**取舍判断**:systolic array 用**通用性**换**比值**。它只会做矩阵(乘加)运算,但对 AI 这种"算术几乎全是矩阵乘"的负载,放弃的通用性几乎不疼,换来的比值翻转极其值钱。这就是 Tensor Core / TPU MXU 存在的理由,也是 Volta 之后 GPU 必须加 Tensor Core 的原因。

> ⚠️ 常见误解:以为 systolic array 的优势是"PE 多、并行度高"。并行度只是表象;真正的优势是**比值翻转**——同样多的乘法器,在 systolic 组织下分母小得多。把同样多的 MAC 单元摊在一个带 mux 的 RF 旁边,比值仍是 1:6,不会因为数量多就变好。

---

## 4. 三个还没回答的问题(本章后续)

systolic array 把比值翻转了,但留下三个工程问题,本章后三篇逐一回答:

1. **数据让谁驻留、谁流动?** 权重驻留是一种选择(weight-stationary),还有 output-stationary、row-stationary。各自适配什么 workload?→ [dataflow-taxonomy](./dataflow-taxonomy.md)
2. **驻留的权重最初怎么装进去?** 既然驻留,载入是一次性的,该优化带宽还是延迟?→ [weight-loading-and-trickle-feed](./weight-loading-and-trickle-feed.md)
3. **阵列该多大、RF 该多大?** 比值随阵列变大而变好,但有约束。→ [array-sizing-tradeoff](./array-sizing-tradeoff.md)

---

## 5. 与 CIM 的边界

systolic array 让权重**就地驻留**在 PE 的数字 register 里——这看起来很像存内计算。但边界清晰:

- **systolic array**:权重存在数字 register 里,每个 cycle 仍要把权重**读出**送进乘法器,再算。它是冯·诺依曼式"取数后计算",只是把"取"的距离缩到隔壁。
- **CIM**:权重存在存储 cell 里,**读出即计算**(模拟域 bitline 累加,或数字 macro 就地 MAC),省掉了"权重→乘法器"这段搬运。

**边界一句话:驻留处是否就是计算处。** systolic 是"驻留处紧挨计算处";CIM 是"驻留处就是计算处"。详见 [`CIM/.../digital-cim-deep-dive`](../../../CIM/wiki/03-compute-paradigms/digital-cim-deep-dive.md) 与 [`CIM/.../sram-cim-deep-dive`](../../../CIM/wiki/02-memory-technologies/sram-cim-deep-dive.md)。这条边界也是 archax 建模时"权重搬运要不要计入"的分水岭。

---

## 6. 本篇在主线上的位置

这是[计算 / 通信比](../01-overview/compute-communication-ratio.md)主线的**第一次大幅抬升**:通过把循环上提两层、固化整个矩阵-向量乘,比值从裸 datapath 的 ~1:6 翻转成 y(阵列行数量级)。手段是"放大固定功能逻辑的粒度,摊薄进出口的税"——这个"大粒度摊薄固定成本"的论点会在 [array-sizing](./array-sizing-tradeoff.md) 和 [gpu-as-tiled-tpu](../07-chip-organization/gpu-as-tiled-tpu.md) 再现。

---

## 建模启示

- **systolic array 在性能建模里可折叠成一个"宏 PE"**:输入 `x` 量级带宽 + 内部 `x·y` 个 MAC/cycle(满载时)。阵列内部 PE 间的局部传递通常**不必逐 PE 建模搬运**,因为它是短线、低能耗、不跨昂贵边界。
- **必须显式建模的状态变量**:阵列维度 `x`(列)、`y`(行)、进出口带宽(`x` 量级)、阵列利用率(矩阵小于阵列时 PE 空转)。
- **核心派生量**:`useful_macs / boundary_bytes = y`(满载时)。利用率不足时实际比值下降——小矩阵喂大阵列,分子缩水但分母不变。这是建模时必须捕捉的"阵列填充率"效应。
- **可折叠**:PE 内部乘法器结构(交给 [02 章](../02-datapath-foundations/dadda-and-adder-trees.md))、阵列内局部布线。
- **关心跨单元数据时必须保留**:阵列边界带宽——它衔接片上互连(见 [NOC noc-meets-memory-system](../../../NOC/wiki/05-system-integration/noc-meets-memory-system.md)),是 data-movement-first 代价函数的输入。
- **事件/数据结构草图**:`ArrayOp{x, y, util} → {macs = x·y·util, boundary_bytes = x·bytes}`。比值 = macs / boundary_bytes,可在阵列粒度求值。
