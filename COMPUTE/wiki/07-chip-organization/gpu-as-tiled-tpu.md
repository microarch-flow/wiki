# GPU = 一堆平铺的小 TPU:顶层布局的粗粒度 vs 细粒度

上级:[07 · 芯片顶层组织](./README.md)
相关:[阵列 sizing](../03-systolic-array/array-sizing-tradeoff.md)、[CPU vs GPU 核面积](./cpu-vs-gpu-core-area.md)、[dataflow 分类](../03-systolic-array/dataflow-taxonomy.md)
外部锚点:Reiner Pope / MatX 访谈(Cheeky Pint、Chipstrat,2026);Dwarkesh × Pope《Chip design from the bottom up》§GPU vs TPU
主线:[计算 / 通信比](../01-overview/compute-communication-ratio.md)——本篇:顶层布局是比值在跨单元数据移动上的最后一战。

---

## 这页在回答什么问题

GPU 和 TPU 在顶层长得很不一样:GPU 是规则网格的众多 SM,TPU 是少数粗粒度大单元。但 Pope 的本质洞察是:**把一个 TPU 缩小,就是一个 SM;GPU = 把许多小 TPU 平铺满整片。** 本篇讲这个等价、粗粒度 vs 细粒度的尖锐 trade-off,以及 MatX 的 splittable systolic array 如何想"两列都要"。

---

## 1. 两种顶层组织

```
GPU:  规则网格的众多近似相同 SM        TPU:  少数粗粒度大单元
  ┌──┬──┬──┬──┐                         ┌──────────────┐
  │SM│SM│SM│SM│                         │  Matrix Unit  │  (大 systolic array)
  ├──┴──┴──┴──┤                         ├──────────────┤
  │    L2     │                         │  Vector Unit  │
  ├──┬──┬──┬──┤                         ├──────────────┤
  │SM│SM│SM│SM│                         │  Matrix Unit  │
  └──┴──┴──┴──┘                         └──────────────┘
  每个 SM 内:小 tensor core + 小 vector unit + SRAM
```

**本质洞察**:把一个 TPU 缩小(小 matrix unit + 小 vector unit),就成了一个 SM。**GPU = 把许多小 TPU 平铺满整片;SM 里的 tensor core 类比 TPU 的 MXU。** 二者不是两种架构,而是同一架构在"单元粒度"这个旋钮上的两个取值:TPU 取"少而大",GPU 取"多而小"。

---

## 2. 粗粒度 vs 细粒度:一张尖锐的对比表

这是承接 [阵列 sizing](../03-systolic-array/array-sizing-tradeoff.md) 那个"阵列多大"的决策,升级到了**整片芯片的布局**层级:

| | TPU(粗粒度) | GPU(细粒度) |
|---|---|---|
| systolic array | 可做大 → 更好摊薄 RF 成本(承接 §03.4) | 被约束成小单元 |
| vector↔matrix 数据通路 | 只能走少数边界(示意:~2 条线) | SM 内可走多条(示意:~16 条线) |
| 跨单元数据移动 | SM 内省能、距离短;跨 SM 才贵 | —— |
| 适合的 workload | 大而规则的矩阵乘 | 不规则、需要局部灵活性 |

> 表中"2 条线 vs 16 条线"是**示意性对比**,用于说明粗/细粒度的边界带宽差异量级,不是某款硬件的实测参数。

**核心权衡(把表读成一句话)**:

- **因为** TPU 把 vector 和 matrix 粗粒度分离,大量数据要挤过那少数几条边界线,**所以** vector↔matrix 数据通路是 TPU 的瓶颈——大阵列摊薄了 RF(分子受益),但跨边界带宽成了新的分母瓶颈。
- **而** GPU 到处都是 vector unit,数据走更多线、距离更短(还省能),**所以** GPU 在 SM 内数据移动便宜——**但一旦跨 SM 就变复杂变贵**(要走 L2、跨片布线)。

```
TPU:  [大 Matrix]══2 线══[Vector]    ← 阵列内极省,但 matrix↔vector 这道关窄
GPU:  [小M]─16线─[V] [小M]─16线─[V]  ← SM 内宽松省能,但 SM 之间要走远路
       └──────── 跨 SM:贵 ────────┘
```

**取舍判断**:workload 是大而规则的矩阵乘(大 batch 推理、大 GEMM)→ 粗粒度 TPU,大阵列摊薄 RF 的收益压倒边界瓶颈。workload 不规则、需要局部灵活性、数据在小范围内频繁交换 → 细粒度 GPU,SM 内便宜的数据移动胜出,代价是跨 SM 贵。

---

## 3. MatX 的方向:splittable systolic array

Pope 公开确认 MatX 在做 **splittable systolic array**——"既能当大阵列、也能拆成小阵列"。这是想在 §2 那张表里**两列都要**:

- 当大阵列用时:拿到 TPU 的 RF 摊薄优势(大粒度摊薄固定成本)。
- 拆成小阵列用时:拿到 GPU 那种"小阵列环绕 SRAM"的局部数据通路灵活性。
- 同时丢掉支撑 CUDA 通用架构所需、占面积的那些东西(如 [§cpu-vs-gpu 的 branch predictor](./cpu-vs-gpu-core-area.md) 一类)。

```
splittable:  ┌─────────────┐         ┌──┬──┬──┬──┐
             │  大阵列模式  │  ⇄拆⇄   │  │  │  │  │
             │ (摊薄 RF)   │         │  小阵列网格 │ (局部灵活)
             └─────────────┘         └──┴──┴──┴──┘
             大 batch 规则 GEMM       小 batch / 不规则 shape
```

**这正好对应 MatX 的整体架构方向**:splittable array + SRAM-first + HBM 混合,面向大 MoE 推理。两个研究增量值得一并记住:

- **HBM + SRAM 混合**:现有 AI 芯片逼你二选一——HBM 高吞吐但高延迟,SRAM 低延迟但低吞吐(容量小)。MatX 把权重放进快 SRAM、推理数据放进大 HBM,试图同时拿低延迟和高吞吐。这呼应 [dataflow 篇的小 batch 反例](../03-systolic-array/dataflow-taxonomy.md#6-一个常被忽略的反例小-batch-让所有-stationary-都失效)——SRAM 驻留权重让 decode 不必每步从 HBM 重搬。详见 [`RAM/.../hbm-vs-lpddr-for-npu`](../../../RAM/wiki/09-ai-chip-memory-architecture/hbm-vs-lpddr-for-npu.md)。
- **splittable 本质**:在 §2 那张表里"两列都要"——大阵列的 RF 摊薄 + 小阵列的数据通路灵活性。它是 [array-sizing](../03-systolic-array/array-sizing-tradeoff.md#4-sizing-是一个-pareto-决策不是单一最优) 那条 Pareto 轴上的一个**非端点解**:不固定在"大"或"小",而是运行时可切。

---

## 4. 跨单元数据移动衔接片上互连

粗/细粒度的本质都是"跨单元数据移动有多贵"。这正是 COMPUTE↔NOC 的接口:

- TPU 的 vector↔matrix 边界、GPU 的跨 SM 路径,都要落到片上互连上。这些流如何在拓扑上路由、带宽够不够,见 [`NOC/.../noc-meets-memory-system`](../../../NOC/wiki/05-system-integration/noc-meets-memory-system.md) 和 [`NOC/.../traffic-patterns-and-characterization`](../../../NOC/wiki/05-system-integration/traffic-patterns-and-characterization.md)。
- COMPUTE 这边只定义"边界带宽"这个接口量(2 线 vs 16 线的量级),NOC 那边负责"这些字节怎么走"。

---

## 5. 本篇在主线上的位置

顶层布局是[计算 / 通信比](../01-overview/compute-communication-ratio.md)的**最后一战,战场是跨单元数据移动**:粗粒度 TPU 用大阵列摊薄 RF(抬比值),代价是 vector↔matrix 边界变窄(新瓶颈);细粒度 GPU 让 SM 内数据移动便宜,代价是跨 SM 变贵。splittable systolic array 想在这条轴上动态取最优。这把全域反复出现的"大粒度摊薄固定成本"(systolic 摊 mux → 大阵列摊 RF → 粗粒度摊整片布局)推到了最高抽象层,主线在此收口。

---

## 建模启示

- **顶层"粗粒度 vs 细粒度"是 system-level 的一个根决策,跨单元数据移动的边界带宽是核心可量化参数。** §2 那张表就是一条分类轴:粗粒度(大 array、跨单元数据贵)vs 细粒度(小 array 平铺、局部便宜跨片贵)。
- **必须显式建模的状态变量**:`unit_granularity`(单元粒度:大 array 边长 vs SM 数量)、`vector_matrix_boundary_bw`(边界带宽,TPU 的"2 线" vs GPU 的"16 线")、`cross_unit_bw`(跨 SM/跨 tile 带宽)。这些直接喂给 data-movement-first 的代价函数。
- **splittable 建模为可变 `array_edge`**:不是固定值,而是运行时按 workload 矩阵尺寸可切的旋钮,目标是最大化 [effective_macs = peak_macs × utilization](../03-systolic-array/array-sizing-tradeoff.md#建模启示)。
- **关心 system-level Pareto 时必须保留**:边界带宽与跨单元带宽——它们决定"数据能不能喂到算力单元",是 data-movement-first 代价函数的主输入。
- **可折叠**:SM 内部的具体微架构(交给 [03 章](../03-systolic-array/)、[07 cpu-vs-gpu](./cpu-vs-gpu-core-area.md));跨单元路由细节(交给 NOC 域)。
- **事件/数据结构草图**:`Topology{granularity, boundary_bw, cross_unit_bw}`;splittable 额外带 `array_edge: variable`。计算 / 通信比在此以"跨单元 bytes_moved / 单元内 macs"的形式求值,粗粒度在单元内比值高、跨单元比值低,细粒度反之——最优布局是让 workload 的数据局部性匹配单元粒度。
