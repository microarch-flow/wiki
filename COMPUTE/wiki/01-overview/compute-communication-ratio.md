# 计算 / 通信比:贯穿 COMPUTE 全域的不变量

上级:[COMPUTE 域总览](./README.md)
相关:[算力单元要解决什么问题](./problem-statement.md)、[原语→阵列→流水→布局 学习路线](./taxonomy-and-roadmap.md)
外部锚点:Dwarkesh Patel × Reiner Pope《Chip design from the bottom up》(2026-05);Reiner Pope,[*Would Strassen matmuls be useful in AI if data movement were free?*](https://reiner.org/strassen)(2025-06)

---

## 这页在回答什么问题

整个 COMPUTE 域只有一条主线:**芯片面积里真正做乘加的逻辑是零头,绝大部分面积花在把数据从一个地方搬到另一个地方——选数、存储、同步、布线。** 每一层的设计动作,本质都是在抬高同一个比值:

```
                有用的计算量(乘加次数)
计算 / 通信比 = ────────────────────────────
                为支撑这些计算而付的数据搬运 / 开销
```

这一页是全域的**纲领**。它定义这个不变量、给出它在六个抽象层级上的统一表格,并约定其余各篇如何回指这里。读完之后,后面每一篇你都应该能在收尾处自己回答一句:"本篇的机制把这个比值往哪个方向推?"

---

## 1. 为什么是"比值",而不是"算力"

直觉会以为芯片设计在最大化算力(每秒多少 FLOP)。这是错的方向。算力(分子)是容易的——多堆乘法器即可;难的是**喂得起**这些乘法器:把操作数搬到它面前、把结果搬走、让它和邻居在同一拍上握手。

衡量一个算力单元好不好,看的不是它能算多快,而是**它为了算这么快,付出了多少不做算术的面积和能量**。这就是为什么主线是一个比值而非一个绝对量:

- 分子 = 有用计算。在 AI 场景里几乎总是 **MAC(乘加)次数**,因为矩阵乘的最内层循环就是一次乘加(见 [multiply-accumulate-from-gates](../02-datapath-foundations/multiply-accumulate-from-gates.md))。
- 分母 = 一切非算术开销:mux 选数、register file 读写、cache/scratchpad 存储、时钟同步的 register、跨单元布线。

> ⚠️ 常见误解:把"算力单元的面积"等同于"算术单元的面积"。在一个 Volta 之前的 CUDA core 里,真正做乘加的逻辑只占 ~1/8,**七八成面积花在软件完全不可见的数据搬运上**(24p 门 vs 4p 门,见 [mux-and-data-movement-cost](../02-datapath-foundations/mux-and-data-movement-cost.md))。"算力"这个词掩盖了真正的成本结构。

这条原则有一个最干净的反证:**Strassen 矩阵乘**把乘法次数从 O(n³) 降到 O(n^2.81),却从不用于 AI。Pope 的分析给出两层原因——(a) Strassen 的复杂数据搬运吃掉了算术节省(data-movement-first);(b) 更根本的是,在低 baseline 精度下,**用 Strassen 换速度,远不如直接降位宽换速度划算**。一个削减分子运算数的算法,在一个"分母才是瓶颈、且分子可以靠降精度二次缩水"的硬件上毫无用武之地。这正是本域主线的最纯表述:**优化对象不是算术,是数据搬运。**

---

## 2. 同一个 trade-off 在六个层级各出现一次

下表是全域的骨架。每一行都是后续某个章节的一句话浓缩;每一章都是某一行的展开。

| 层级 | 计算项(分子) | 通信 / 开销项(分母) | 抬比值的手段 | 展开章节 |
|---|---|---|---|---|
| 比特精度 | p×q(乘法器面积) | —— | 降位宽(面积二次缩放) | [§02 quadratic-bitwidth](../02-datapath-foundations/quadratic-bitwidth-scaling.md) |
| datapath | p×q(一次 MAC) | 3·n·p(三个 mux 选数) | —— **这是问题,不是解** | [§02 mux-cost](../02-datapath-foundations/mux-and-data-movement-cost.md) |
| systolic array | x·y(阵列内每个 PE 做 MAC) | x(只有进出向量跨边界) | 权重就地驻留 + 复用 | [§03 why-systolic-array](../03-systolic-array/why-systolic-array.md) |
| pipeline | 每周期做的有用功 | pipeline register 面积 | 切到"够用就好",别过切 | [§04 frequency-is-not-throughput](../04-clocking-and-pipeline/frequency-is-not-throughput.md) |
| FPGA vs ASIC | 真实门 | LUT / mux 可配置开销(~10×) | 流片固化 | [§05 lut-mux-overhead](../05-fpga-vs-asic/lut-mux-and-10x-overhead.md) |
| 顶层布局 | systolic array 大小 | vector↔matrix 跨边界布线 | 粗粒度摊薄 RF 成本 | [§07 gpu-as-tiled-tpu](../07-chip-organization/gpu-as-tiled-tpu.md) |

记住这张表。它不是某一篇的内容,而是**整个域的索引**:任何一篇文章如果你读完答不上来"它在哪一行、把比值推向哪边",那就是没读懂。

---

## 3. 三个推比值的根本动作

把上表六行抽象一下,所有抬比值的手段其实只有三类:

### 3.1 降低分子的单位成本(降精度)

乘法器面积 ∝ p×q ∝ 位宽²。位宽减半 → 面积降到 1/4,不是 1/2。这是低精度算术对神经网络如此有效的**单一最根本原因**,比线性直觉划算一倍。Nvidia 从 B300 起标 FP4 比 FP8 快 3×(理论极限 4×),正是承认了这条二次律。

### 3.2 放大粒度,摊薄分母(固定功能逻辑上提循环)

datapath 把"一次 MAC"固化进硬件;systolic array 再上提两层循环,把整个矩阵-向量乘固化进硬件。**因为** 更大粒度的固定功能逻辑,可以让进出口的"税"摊得更薄:compute 涨 x·y,通信只涨 x,净赚一个 y 倍。这个"大粒度摊薄固定成本"的论点会在 §03(大阵列摊薄 RF)和 §07(粗粒度 TPU vs 细粒度 GPU)反复出现。

### 3.3 把分母从运行时随机变成编译期确定(确定性 discipline)

cache 让硬件偷偷决定数据从哪来 → 非确定性延迟。scratchpad 把这个决策做成显式指令 → 确定性延迟。这不直接改变比值的大小,但改变了**分母的可预测性**——对一个把"data movement bytes"当作可审计物理量来建模的工具链(如 archax)而言,确定性比平均更快更重要(见 [cache-vs-scratchpad](../06-memory-discipline/cache-vs-scratchpad.md))。

---

## 4. 这条主线和其他域的接口

COMPUTE 域讲的是"数据搬到之后**怎么算、为什么算力单元长这样**"。它的分母(数据搬运)正是其他几个域的主体:

- **↔ RAM**:scratchpad vs cache 的确定性语义。COMPUTE 从"算力单元要确定性延迟"出发,RAM 从存储器件出发,在 [`RAM/.../data-movement-first-principle`](../../../RAM/wiki/09-ai-chip-memory-architecture/data-movement-first-principle.md) 与 [`scratchpad-vs-cache`](../../../RAM/wiki/03-sram-applications/scratchpad-vs-cache.md) 会合。
- **↔ CIM**:systolic array 的权重就地驻留(存在数字 register、仍取数后计算)vs CIM 的存内计算(权重存在 cell、读出即算)。边界在"权重驻留处是否就是计算处",见 [`CIM/.../digital-cim-deep-dive`](../../../CIM/wiki/03-compute-paradigms/digital-cim-deep-dive.md)。
- **↔ NOC / DMA**:systolic array 进出口带宽、跨 SM/跨 tile 数据移动如何衔接片上互连,见 [`NOC/.../noc-meets-memory-system`](../../../NOC/wiki/05-system-integration/noc-meets-memory-system.md)。
- **↔ FAB**:门数 → die area → 成本/良率。COMPUTE 给"省多少门",FAB 给"这些门占多少 mm²、$3000 万 tape-out 的出处",见 [`FAB/.../process-nodes-and-ppa-tradeoffs`](../../../FAB/wiki/02-front-end-fabrication/process-nodes-and-ppa-tradeoffs.md)。
- **↔ Workload**:低精度二次缩放、batch size↔吞吐/延迟,挂到 workload 特征。见 [`Workload/.../attention-variants-and-efficiency`](../../../../workload-wiki/01-foundation-model-components/attention-variants-and-efficiency.md)(MQA/GQA 降 KV 搬运)与 [`Workload/.../cnn-backbone`](../../../../workload-wiki/01-foundation-model-components/cnn-backbone.md)(卷积复用结构)。

---

## 5. 本篇在主线上的位置

这一篇**就是主线本身**。它不把比值往任何方向推,而是定义这个比值、并把它确立为一个**可在任意聚合粒度(PE / array / core / chip)求值的派生量**。其余每一篇都是它的一行展开,收尾都回指这里。

---

## 建模启示

**计算 / 通信比应是 archax 里一等公民的派生量,而非某一层的指标。** 本篇的核心建模主张:

- **必须显式建模的量**:`useful_MACs`(理论乘加数)和 `bytes_moved`(跨某个边界的数据搬运字节)。比值 = 前者 / 后者。
- **关键设计决策**:这个比值要能在**任意聚合粒度**上求值——单个 PE、一个 array、一个 core、整片 chip。不要只在顶层算一次。同一份 workload 在 PE 粒度可能比值很高(阵列内复用好),在 chip 粒度却很低(跨 SM 搬运吃掉收益),这两个数都要能取到。
- **可折叠的细节**:只关心比值时,门级的具体压缩树结构、register 的具体触发方式都可折叠成"面积权重"和"字节计数",不必逐门仿真。
- **数据结构草图**:把每条 data movement 记成一个事件 `Move{src, dst, bytes, when, kind ∈ {config, steady}}`,把每次算术记成 `Compute{macs, precision, when}`;比值就是在任意空间/时间窗口上对二者求和后相除。`kind` 字段区分一次性配置流(权重载入)与稳态数据流(向量流),前者只计带宽/面积、后者计延迟+带宽——这个区分在 [weight-loading-and-trickle-feed](../03-systolic-array/weight-loading-and-trickle-feed.md) 展开。

> 详细的 archax Resource/Topology/Interaction/Capability 映射见 [08-modeling-for-archax/modeling-insights](../08-modeling-for-archax/modeling-insights.md)。本域其余各篇的"建模启示"只讲通用仿真抽象,不绑定 archax 术语。
