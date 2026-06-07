# Dataflow 分类:weight / output / row stationary 的尖锐对比

上级:[03 · systolic array](./README.md)
相关:[为什么要 systolic array](./why-systolic-array.md)、[权重载入与 trickle-feed](./weight-loading-and-trickle-feed.md)、[阵列 sizing](./array-sizing-tradeoff.md)
主线:[计算 / 通信比](../01-overview/compute-communication-ratio.md)——三种 stationary 是同一比值在"复用哪个张量维度"上的三种下注。

> **[补全] 篇**:基准长文只讲 weight-stationary。本篇补全 output-stationary、row-stationary、no-local-reuse 的对比,给出"什么 workload 选谁、代价是什么"的明确判断,并挂到 Workload 域的负载复用结构。

---

## 这页在回答什么问题

systolic array 让数据在阵列里流动、让某个张量驻留以复用。但**让哪个张量驻留**是个选择,不同选择叫不同的 dataflow。本篇回答:weight-stationary、output-stationary、row-stationary 各自固定什么、复用什么、放弃什么,以及**什么负载该选哪个**。这是把抽象的"复用"落到具体 workload 的关键一篇。

---

## 1. 三个张量,谁动谁不动

矩阵乘 `out[i,k] += in[i,j] · w[j,k]` 涉及三个张量:输入(激活)`in`、权重 `w`、输出(部分和)`out`。systolic array 里这三者中:**一个驻留(stationary)、一个流动(streaming)、一个累积/移动**。选哪个驻留,就是选哪个张量的**复用免费**(不跨边界搬运)。

```
            驻留(reuse 免费)    流动           累积
weight-stationary    权重 w        激活 in        部分和 out 沿列累加
output-stationary    部分和 out    激活 in + 权重 w 都流入
row-stationary       行级混合(见 §4)
```

**核心权衡**:驻留的那个张量,它的数据搬运成本被摊薄到接近零;但另外两个必须流动,它们的搬运成本就成了分母的主体。**所以选 dataflow = 选哪个张量的搬运最该被消除**——而这取决于哪个张量最大、复用机会最多,这是 workload 的属性。

---

## 2. Weight-stationary:复用权重(基准长文的选择)

```
        in 流入 →  ┌──────────────┐
                   │ w  w  w  w   │  ← 权重就地驻留,长时间不变
                   │ w  w  w  w   │     每个权重被多个输入复用
                   └──────┬───────┘
                          ▼ 部分和沿列累加流出
```

- **固定**:权重 `w`,载入一次、反复用。
- **流动**:激活 `in`(逐拍流入);部分和沿列累加流出。
- **赢在哪**:**权重大、且被大量输入复用**时。AI 推理权重固定,一组权重要处理整个 batch / 整个序列的激活 → 权重复用次数极高 → 把权重搬运摊到接近零最划算。这是 TPU MXU、多数推理加速器的默认。
- **代价**:激活和部分和都要流动;若 batch 小(激活少),权重复用次数低,载入成本摊不开——见 §5 的 batch 依赖。

> 这也是为什么权重载入可以"慢但窄"(trickle-feed):权重要在阵列里待很久,载入是一次性的,优化带宽而非延迟。详见 [weight-loading-and-trickle-feed](./weight-loading-and-trickle-feed.md)。

---

## 3. Output-stationary:复用部分和

```
        in 流入 ↘   ↙ w 流入
              ┌──────────────┐
              │ Σ  Σ  Σ  Σ   │  ← 部分和驻留在 PE 里原地累加
              │ Σ  Σ  Σ  Σ   │     激活和权重都流过
              └──────────────┘
              算完才把最终 out 写出
```

- **固定**:输出部分和 `out`,在 PE 里原地累加,直到 reduction 完成才写出。
- **流动**:激活 `in` 和权重 `w` 都流入。
- **赢在哪**:**reduction 维度(j)很深**时。部分和(psum)需要高精度(见 [精度非对称](../02-datapath-foundations/multiply-accumulate-from-gates.md#2-精度非对称乘法用低精度累加用高精度)),如果让它流动,每一步都要把高精度 psum 进出存储,搬运很贵。output-stationary 把 psum 钉在 PE 里原地累加,**避免了高精度部分和的反复进出**——深 GEMM、深 reduction 时这是主要省点。
- **代价**:权重不再复用免费,权重也得流动;权重大时不划算。

**weight- vs output-stationary 的尖锐判断**:

| | weight-stationary | output-stationary |
|---|---|---|
| 消除的搬运 | 权重搬运 | 高精度部分和搬运 |
| 赢的场景 | 权重大、复用多(推理、大 batch) | reduction 深、psum 精度高 |
| 输的场景 | batch 小,权重复用不足 | 权重大,权重流动成本高 |
| 真实锚点 | TPU MXU | 部分 GPU Tensor Core 配置、深 GEMM kernel |

---

## 4. Row-stationary:综合复用(Eyeriss)

row-stationary(Eyeriss 提出)不固定单一张量,而是**在 PE 行级别同时复用多种张量**:每个 PE 处理一行卷积,行内复用权重、跨行复用激活、纵向累加部分和。

- **赢在哪**:**卷积**——卷积的 sliding window 让相邻输出共享大量输入像素,row-stationary 能同时榨取 weight reuse、input reuse、psum reuse 三种局部性。
- **代价**:控制和布线更复杂(不像 weight-stationary 那样规则),映射更难。
- **真实锚点**:Eyeriss(MIT),专为 CNN 能效优化。

> 还有一种 **no-local-reuse**:不让任何张量驻留 PE,全靠全局 buffer。它放弃了 PE 级复用,极少单独用,通常作为对照基线。

---

## 5. 挂 Workload:复用结构决定该选谁

dataflow 的选择**不是硬件单方面决定的,而是 workload 的复用结构决定的**:

| Workload | 复用结构 | 倾向的 dataflow |
|---|---|---|
| **CNN** | sliding window,输入/权重/psum 三重局部性 | row-stationary(Eyeriss)或 weight-stationary |
| **Transformer(大 batch 推理)** | 权重固定,大量 token 复用同一权重 | weight-stationary |
| **Transformer(小 batch / decode)** | 权重复用低(每步一个 token),memory-bound | weight-stationary 也难摊开权重载入 → 见 §6 |
| **深 GEMM / 大 reduction** | reduction 维度深,psum 精度高 | output-stationary |

> 这正是 COMPUTE↔Workload 的接口:COMPUTE 提供 dataflow 的硬件机制,Workload 提供"这个负载的复用维度在哪、有多大"。见 [`Workload/.../cnn-backbone`](../../../../workload-wiki/01-foundation-model-components/cnn-backbone.md)(卷积三重局部性 → row-stationary)、[`Workload/.../attention-and-transformer`](../../../../workload-wiki/01-foundation-model-components/attention-and-transformer.md)(权重固定、大 batch 复用 → weight-stationary)、[`Workload/.../attention-variants-and-efficiency`](../../../../workload-wiki/01-foundation-model-components/attention-variants-and-efficiency.md)(MQA/GQA 改变 KV 复用维度)。

> 衔接 CIM:CIM 的存内计算天然是一种极致的 weight-stationary(权重存在 cell 里读出即算),它的 dataflow 选择见 [`CIM/.../dataflow-mapping-on-cim`](../../../CIM/wiki/05-architecture-and-system/dataflow-mapping-on-cim.md)。区别在 systolic 仍把权重读出送乘法器,CIM 读出即算。

---

## 6. 一个常被忽略的反例:小 batch 让所有 stationary 都失效

⚠️ 常见误解:以为选对 dataflow 就能保证高比值。**小 batch / decode 场景下,任何 dataflow 都救不了比值。** 因为:

- weight-stationary 靠"一组权重处理大量激活"摊薄权重载入。但 decode 每步只处理**一个** token → 权重复用次数 ≈ 1 → 权重载入成本完全摊不开 → 变成 memory-bound,算力单元饿死。

这时瓶颈不在 dataflow,而在**权重从 HBM 搬进来的带宽**——见 [`RAM/.../memory-bound-vs-compute-bound`](../../../RAM/wiki/09-ai-chip-memory-architecture/memory-bound-vs-compute-bound.md)。这也是 MatX 用 SRAM 驻留权重的动机:把权重放进片上 SRAM,decode 时不必每步从 HBM 重搬。dataflow 选择只在 compute-bound 区间有意义。

---

## 7. 本篇在主线上的位置

三种 stationary 是[计算 / 通信比](../01-overview/compute-communication-ratio.md)在"**复用哪个张量维度**"上的三种下注:weight-stationary 消除权重搬运、output-stationary 消除高精度 psum 搬运、row-stationary 综合榨取卷积局部性。选对 dataflow = 把 workload 最大的那个张量的搬运摊到接近零,从而抬高比值。但小 batch 会让分子(复用)枯竭,此时换 dataflow 无济于事——瓶颈退回到存储带宽。

---

## 建模启示

- **dataflow 是 archax 里一个一等的探索维度**,不是实现细节。它决定哪个张量的 `movement_bytes` 被消除。建模时应把 `dataflow ∈ {WS, OS, RS, NLR}` 作为 microarchitecture 的一个坐标轴。
- **必须显式建模的状态变量**:每个张量(in/w/out)的 `reuse_factor`(被复用次数)与 `movement_bytes`。选定 dataflow 后,驻留张量的 movement_bytes → ~0,流动张量 → 全额。
- **核心派生量**:`总搬运 = Σ_tensor (movement_bytes_t)`,随 dataflow 和 workload 复用结构变化。计算 / 通信比 = useful_macs / 总搬运。
- **关心性能时必须保留**:`batch_size` / reuse_factor——它决定 dataflow 收益能否兑现。小 batch 下驻留张量的载入成本摊不开,模型必须能切到 memory-bound 分支(交给 RAM 域)。
- **事件/数据结构草图**:`Dataflow{kind, stationary_tensor} → {moved: [in_bytes, w_bytes, out_bytes]}`,其中 `stationary_tensor` 对应项置 ~0。三种 dataflow 在同一 workload 上各算一次总搬运,取最小者即该 workload 的最优 dataflow。
