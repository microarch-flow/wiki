# CPU vs GPU core:面积都花在哪了

上级:[07 · 芯片顶层组织](./README.md)
相关:[mux 与数据搬运成本](../02-datapath-foundations/mux-and-data-movement-cost.md)、[cache vs scratchpad](../06-memory-discipline/cache-vs-scratchpad.md)、[GPU = 平铺的 TPU](./gpu-as-tiled-tpu.md)
主线:[计算 / 通信比](../01-overview/compute-communication-ratio.md)——本篇:专用化 = 砍掉 AI workload 不需要的分母(分支预测)。

---

## 这页在回答什么问题

CPU core 比 GPU core 大得多。大头在哪?直觉会说"cache""ALU""register file",但这些都不是关键区别。本篇回答:**CPU 面积的真正大头是 branch predictor(分支预测器),而 GPU 几乎没有对应物——砍掉它是 GPU 相对 CPU 的主要面积收益来源。** 这是"为 AI 专门化"省面积的典型案例。

---

## 1. 排除法:哪些不是关键区别

CPU 仍是 von Neumann 架构:~100 核 × ~16 路向量 ≈ 1000 路并行。单核很大,但逐项排查:

| 部件 | CPU 占面积 | GPU 有对应物吗 | 是关键区别吗 |
|---|---|---|---|
| cache + register file | 大 | 有(GPU 也有大量片上存储) | ❌ 不是 |
| ALU 本身 | 很小 | 有 | ❌ 不是 |
| **branch predictor** | **大** | **几乎没有** | ✅ **是** |

cache 和 RF 占大量面积,但 GPU 也有对应物(甚至更多片上 SRAM),所以不是区别所在。ALU 本身很小,不值一提。**真正的区别是 branch predictor**——CPU 里一大块面积专门预测"下一个分支在哪、跳到哪",GPU 没有。

---

## 2. branch predictor 在解决什么物理约束

为什么 CPU 要花这么大面积预测分支?因为分支解析慢,而时钟想跑快:

```
取指 → 判 boolean → 更新 PC → 从指令存储取目标   ≈ 5 ns(≈ 200 MHz)
但我想跑 1~2 GHz(周期 0.5~1 ns)
```

**因为** 处理一条分支指令到知道"该跳哪"要 ~5 ns,而想跑的时钟快得多(5~10 倍);**所以** 不能等分支结果出来再取下一条指令——那样每遇到分支就要停 ~5 个周期。必须在分支结果出来**之前**就先跑后续指令(赌一个方向),赌错了就回滚、跳到正确目标。

**branch predictor 的职责就是提前 ~5 个周期预测分支走向**,让流水线在还没解析到那条分支时就开始执行"对的"路径。预测越准,流水线停顿越少——这就是为什么现代 CPU 在分支预测上堆了巨大面积(历史表、BTB、神经分支预测器等)。

---

## 3. 为什么 GPU/TPU 能砍掉它,几乎无损

AI 加速器(TPU/GPU)的 workload **分支极少**——矩阵乘是规则的多重循环,控制流简单、可预测,几乎没有数据依赖的分支跳转。

**所以** 砍掉 branch predictor 这块面积**几乎无损**:没有复杂控制流,就不需要花面积去赌分支方向。省下的面积全部还给算术单元(更大的 systolic array、更多 PE)。

```
CPU core:  [大 branch predictor] + [收紧的并行算术] → 单核大,擅长复杂控制流
GPU core:  [无 branch predictor] + [大量并行算术]   → 单核小,擅长规则数据并行
```

这就是"砍掉分支预测 + 收紧 register file,是 GPU 相对 CPU 的主要收益来源"的含义——**不是 GPU 的乘法器更好,而是它砍掉了通用性需要、但 AI 不需要的那块分母。**

> ⚠️ 常见误解:以为 GPU 比 CPU 快是因为"核多""频率高"或"乘法器强"。根本是 workload 专门化:AI 没有复杂分支,所以可以砍掉 CPU 为通用控制流付的巨大面积税,把硅全投给算术和片上存储。

---

## 4. 这是一系列"砍分母"专门化中的一个

CPU→GPU/TPU 的专门化,本质是一连串"砍掉 AI 不需要的分母":

- 砍 **branch predictor**(本篇):AI 无复杂分支。
- 砍 **cache 非确定性**,换 [scratchpad](../06-memory-discipline/cache-vs-scratchpad.md):AI 访问模式静态可知,不需要硬件赌局部性。
- 砍 **每次 MAC 的 mux 选数**,换 [systolic array](../03-systolic-array/why-systolic-array.md):AI 算术规则,可固化循环。

每一刀都是同一个逻辑:**通用性需要的某块分母,在 AI 规则负载下变成纯浪费,砍掉它把硅还给分子。** 这正是 [MatX splittable array](./gpu-as-tiled-tpu.md#93-matx-的方向splittable-systolic-array) 想做到极致的——拿到 GPU 的局部灵活性,同时丢掉支撑 CUDA 通用架构所需、占面积的那些东西(如分支预测一类)。

---

## 5. 本篇在主线上的位置

CPU vs GPU 的面积分歧,是[计算 / 通信比](../01-overview/compute-communication-ratio.md)在"专门化"维度的体现:**砍掉 AI workload 不需要的分母(分支预测),把面积还给分子。** GPU 不是有更强的算术,而是有更少的为通用性付的开销。这条逻辑串起全域多个"砍分母"动作,并直接通向下一篇——GPU 把这些省下的硅,组织成了一堆平铺的小 TPU。

---

## 建模启示

- **专门化的收益建模为"砍掉某类分母面积"。** CPU→GPU 的差异不在算术单元的吞吐,而在 `overhead_area`(分支预测、复杂控制)被移除。建模时一个 core 的面积 = `compute_area + storage_area + control_overhead_area`,GPU 把最后一项压到接近零。
- **必须显式建模的状态变量**:`branch_predictor_area`、`control_overhead_area`、`has_complex_control ∈ {true, false}`。AI 加速器设为 false,这块面积归零并回流到算术。
- **可折叠**:branch predictor 的内部结构(BTB、历史表)对面积建模可折叠成一个面积数;对 AI 加速器建模可直接置 0(无复杂分支)。
- **关心 CPU 对照时必须保留**:`branch_misprediction_penalty` 和 `prediction_accuracy`——它们决定通用负载的有效 IPC,但对无分支的 AI 负载不相关。
- **事件/数据结构草图**:`Core{type, compute_area, storage_area, control_overhead_area}`;`type == GPU/TPU ⟹ control_overhead_area ≈ 0`。省下的面积换算成额外的 `array_edge` 或 PE 数,直接抬高峰值 macs。
