# 阵列 sizing:systolic array 多大、register file 多大

上级:[03 · systolic array](./README.md)
相关:[为什么要 systolic array](./why-systolic-array.md)、[dataflow 分类](./dataflow-taxonomy.md)、[GPU = 平铺的 TPU](../07-chip-organization/gpu-as-tiled-tpu.md)
主线:[计算 / 通信比](../01-overview/compute-communication-ratio.md)——本篇是"大粒度摊薄固定成本"的量化:阵列越大,RF 成本摊得越薄。

---

## 这页在回答什么问题

systolic array 把比值翻转成 y(阵列行数)。那是不是阵列越大越好?本篇回答最核心的一对耦合 sizing 决策:**systolic array 多大 vs register file 多大**——它们抢同一份面积,而阵列越大,RF 成本摊得越薄,但灵活性和利用率会受限。

---

## 1. 一对抢面积的耦合变量

阵列和它周边的 register file / vector unit 抢同一片硅:

```
面积预算(固定)
  ├── systolic array(做 MAC,分子)        ← 越大,比值越高(§why-systolic 的 y)
  └── register file / vector unit(喂数,分母) ← 越大,越灵活,但吃掉阵列的面积
```

- **大 RF** → 更灵活、application-level 性能更高(能缓存更多操作数、支持更复杂的数据重排),但吃掉本可给阵列的面积。
- **大阵列** → 比值更高(y 更大)、单位面积算力更高,但灵活性低,且对小矩阵利用率差(PE 空转)。

**常用方法:给数据搬运设一个面积预算**(比如"RF 占 10%、阵列占 90%"),再据此反推 RF 大小。这把一个模糊的"多大合适"变成一个可执行的预算分配。

---

## 2. 为什么大阵列摊薄 RF 成本

关键论点(会在 [GPU vs TPU](../07-chip-organization/gpu-as-tiled-tpu.md) 再现):**阵列越大,同一份 RF 喂的 PE 越多,RF 的固定成本被摊得越薄。**

```
小阵列(64×64):   一份 RF 喂 4096 个 PE,RF 成本 / PE 高
大阵列(128×128): 一份 RF 喂 16384 个 PE,RF 成本 / PE 降到 1/4
                  ───────────────────────────────────────
                  RF(分母的一部分)固定,PE(分子)翻 4 倍 → 比值更高
```

**因为** RF / vector unit 是一份相对固定的开销,**所以** 让它服务更多 PE,就把这份分母摊到更多分子上——这是"大粒度摊薄固定成本"在阵列层级的体现,和 [systolic 上提循环摊薄 mux](./why-systolic-array.md) 是同一个道理,只是粒度更大一层。

> **真实硬件锚点**:老 TPU 是 **128×128** 的这种阵列,是已知最高效的矩阵乘电路。这个尺寸不是随便定的——它在"摊薄 RF""利用率""单阵列布线可控"之间取了一个被验证有效的点。

---

## 3. 大阵列的代价:利用率与跨边界布线

阵列不是越大越好,有两个反向约束:

### 3.1 利用率:小矩阵喂大阵列,PE 空转

⚠️ 常见误解:以为大阵列总是更快。**当矩阵小于阵列时,多出的 PE 空转,分子缩水但分母(布线、RF)不变,比值反而下降。** 128×128 阵列处理一个 32×32 的矩阵,只有 1/16 的 PE 在干活。所以阵列尺寸要和典型 workload 的矩阵尺寸匹配——这又是 COMPUTE↔Workload 的接口。

### 3.2 跨边界布线:大阵列的进出口变窄(相对)

阵列越大,内部 PE 越多,但跨边界(顶部灌输入、底部出输出)的线数只随边长 x 线性增长。大阵列意味着**大量数据要挤过相对更窄的边界**——这正是 [GPU vs TPU 那张表](../07-chip-organization/gpu-as-tiled-tpu.md#92-粗粒度-vs-细粒度的-trade-off) 里"TPU 只有 2 条边界线"的来源。粗粒度大阵列摊薄了 RF,但代价是 vector↔matrix 数据通路变成瓶颈。

---

## 4. sizing 是一个 Pareto 决策,不是单一最优

把 §1–§3 合起来,阵列 sizing 没有唯一最优解,而是一条 Pareto 前沿:

| 选择 | 比值(摊薄 RF) | 利用率(小矩阵) | 数据通路灵活性 | 适合 |
|---|---|---|---|---|
| 大阵列(TPU 式 128×128) | 高 | 对小矩阵差 | 跨边界窄(瓶颈) | 大而规则的矩阵乘 |
| 小阵列(GPU SM 内) | 低 | 对小矩阵好 | 跨边界宽、距离短 | 不规则、需局部灵活 |
| splittable(MatX) | 想两者都要 | 可切分适配 | 可大可小 | 见 [gpu-as-tiled-tpu §9.3](../07-chip-organization/gpu-as-tiled-tpu.md#93-matx-的方向splittable-systolic-array) |

**取舍判断**:workload 是大而规则的矩阵乘(大 batch 推理、大 GEMM)→ 大阵列摊薄 RF 的收益压倒利用率损失;workload 不规则、矩阵尺寸多变(小 batch、动态 shape)→ 小阵列保利用率和灵活性。**splittable systolic array 就是想在这张表上"两列都要"**——大阵列的 RF 摊薄 + 小阵列的灵活性。

---

## 5. 本篇在主线上的位置

阵列 sizing 是[计算 / 通信比](../01-overview/compute-communication-ratio.md)主线的一个核心 sizing 旋钮:把阵列做大,用"大粒度摊薄固定成本"把 RF 这份分母摊到更多 PE 上,抬高比值——但受利用率(小矩阵 PE 空转)和跨边界布线(vector↔matrix 瓶颈)两个反向约束。最优点不是端点,而是 Pareto 前沿上一个匹配 workload 矩阵尺寸的位置。这条"大阵列摊薄 RF"的逻辑会在 [§07 顶层布局](../07-chip-organization/gpu-as-tiled-tpu.md) 升级为"粗粒度 TPU vs 细粒度 GPU"的全局决策。

---

## 建模启示

- **阵列边长与 RF 大小应是一个显式的、耦合的探索维度。** 它们抢同一面积预算,是 archax microarchitecture 层 Pareto 前沿的一个坐标轴。
- **必须显式建模的状态变量**:`array_edge N`(边长)、`RF_entries`、`RF_ports`、`area_budget_split`(RF vs array 的面积分配比)、每周期跨 RF 边界的字节数。
- **核心派生量**:`RF_cost_per_PE = RF_area / N²`(随阵列变大而下降)与 `utilization = min(matrix_dim, N)² / N²`(随阵列变大、矩阵变小而下降)。两者反向,比值的最优点在二者乘积最大处。
- **关心面积账时必须保留**:RF 端口数和深度——它决定 RF 面积,也决定能同时喂多少 PE。
- **关心利用率时必须保留**:典型 workload 的矩阵尺寸分布——它和 `array_edge` 一起决定填充率。小矩阵多的 workload,大阵列的比值优势被利用率吃掉。
- **事件/数据结构草图**:`ArraySizing{N, RF_entries, RF_ports} → {area, RF_cost_per_PE, peak_macs = N²}`;配合 workload 的矩阵尺寸分布算出 `effective_macs = peak_macs · utilization`。这正是 [splittable array](../07-chip-organization/gpu-as-tiled-tpu.md) 想优化的目标:让 N 可变以最大化 effective_macs。
