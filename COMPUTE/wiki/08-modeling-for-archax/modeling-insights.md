# 面向 archax 的建模启示:把 COMPUTE 主线翻译成可建模量

上级:[08 · 面向 archax 的建模](./README.md)
相关:[计算 / 通信比(全域纲领)](../01-overview/compute-communication-ratio.md) 及其余各篇的"建模启示"小节
主线:[计算 / 通信比](../01-overview/compute-communication-ratio.md)——本篇:把贯穿全域的比值做成 Execution IR 的一等派生量。

> **本篇是 COMPUTE 域唯一显式使用 archax 术语(Resource / Topology / Interaction / Capability、Execution IR、M1/M2、S1)的章节。** 其余各篇的"建模启示"只讲通用仿真抽象。本篇把那些通用结论汇总、并映射到 archax 的具体抽象层。把它当作"从知识到工具"的转换层来读。

---

## 这页在回答什么问题

前面七章每篇都有"建模启示"小节,讲的是通用仿真抽象(状态变量、事件类型、可折叠/必须保留)。本篇做两件事:(1) 把这些散落的结论**汇总成 7 条**,对应 Pope 讲座文末的 7 条 modeling insight;(2) 把每条**映射到 archax 的四元抽象**——Resource(资源)、Topology(拓扑)、Interaction(交互)、Capability(能力)——以及 data-movement-first、Execution IR 唯一外部接口这些核心方法论。

---

## archax 四元抽象速记

为后文映射方便,先固定术语(本篇默认你已熟悉,这里只作锚点):

- **Resource**:做功/存储的实体(算术单元、RF、scratchpad、HBM)。
- **Topology**:Resource 之间的连接结构(阵列布局、SM 网格、vector↔matrix 边界)。
- **Interaction**:Resource 间的数据移动语义(配置流 vs 稳态流、cache vs scratchpad)。
- **Capability**:Resource 能做什么、多快、多大(峰值 MACs、位宽、面积)。
- **Execution IR**:唯一外部接口,暴露可审计物理量——data movement bytes、读写次数、theoretical MACs、reuse rate。

---

## 1. 计算 / 通信比应成为一等公民的物理量

**COMPUTE 来源**:[纲领篇](../01-overview/compute-communication-ratio.md) 全篇——同一 trade-off 在六个层级反复出现。

**archax 映射**:Execution IR 里 `data movement bytes / theoretical MACs` 这个比值**不是某一层的指标,而是贯穿全层级的不变量**。建议把它做成可在**任意聚合粒度(PE / array / core / chip)上求值的派生量**,而不只在顶层算一次。同一 workload 在 PE 粒度比值可能很高(阵列内复用好),chip 粒度却很低(跨 SM 搬运吃掉收益)——两个数都要能取到。

**落地**:`reuse rate` 和 `bytes_moved` 作为 Execution IR 的一等字段,在 Topology 的每个聚合节点上可求和、可求比。这是 data-movement-first 原则的量化骨架。

---

## 2. 位宽的二次缩放必须显式建模,不能线性近似

**COMPUTE 来源**:[quadratic-bitwidth-scaling](../02-datapath-foundations/quadratic-bitwidth-scaling.md)、[number-formats-for-ai](../02-datapath-foundations/number-formats-for-ai.md)。

**archax 映射**:这是 **Capability** 的建模约束。乘法器面积 ∝ 位宽²。若 Capability 用"FLOP 随位宽线性"近似(像 B200 前的 Nvidia spec),会系统性低估低精度的面积/能效收益。建模 FP4/FP8 的 area 与 throughput 应**以 p×q 为基**,并显式标注 **FP4↔FP8 的非 fungible 程度**作为一个架构参数 `k ∈ [2×, 4×]`(来自二次缩放、die area 分配、搬运对齐的混合)。

**落地**:`Capability{mul_bits, acc_bits, fungibility_k}`,area = `f(mul_bits²) + c_exp`,峰值算力按二次而非线性缩放。

---

## 3. register file ↔ systolic array 的面积预算应是显式探索维度

**COMPUTE 来源**:[mux-and-data-movement-cost](../02-datapath-foundations/mux-and-data-movement-cost.md) + [array-sizing-tradeoff](../03-systolic-array/array-sizing-tradeoff.md)。

**archax 映射**:这是 **microarchitecture M1 结构层**的一个坐标轴。"数据搬运 vs 计算"的面积账(24p:4p、大阵列摊薄 RF)是一个可参数化的 sizing 旋钮,应进入 Pareto 前沿三元组里 microarchitecture 组合的一个坐标。

**必须显式建模的状态变量**:array 边长 `N`、RF entry 数、RF 端口数、每周期跨 RF 边界的 byte 数。`RF_cost_per_PE = RF_area / N²`(随阵列变大下降)与 `utilization`(随阵列变大、矩阵变小下降)反向,最优在二者乘积最大处。

---

## 4. weight-stationary 的 trickle-feed 是"带宽而非延迟",建模时分离这两个量

**COMPUTE 来源**:[weight-loading-and-trickle-feed](../03-systolic-array/weight-loading-and-trickle-feed.md)。

**archax 映射**:这是 **Interaction** 抽象的核心区分。权重载入(罕见、可慢、窄带宽)与向量流(每周期、x 量级带宽)是两条**语义完全不同**的数据移动。Interaction 应能区分"一次性配置流"与"稳态数据流",并对前者**只计带宽/面积**、对后者**计延迟+带宽**。

**落地**:`Interaction{kind ∈ {config, steady}}`。config 流(权重载入)延迟摊到 ~0(发生频率极低),只计布线带宽/面积;steady 流(激活)计延迟+带宽。这也是 3D 笔记里"宽而慢 vs SerDes"区分的同源问题。⚠️ 例外:MoE 频繁切权重块时,config 流不再可摊薄,进入热路径。

---

## 5. cache vs scratchpad 是两种不可混淆的 Interaction 语义

**COMPUTE 来源**:[cache-vs-scratchpad](../06-memory-discipline/cache-vs-scratchpad.md)(强链 [`RAM/.../scratchpad-vs-cache`](../../../RAM/wiki/03-sram-applications/scratchpad-vs-cache.md))。

**archax 映射**:这是 **Interaction** 的第二个关键区分。隐式 cache(硬件决定来源、非确定性命中)与显式 scratchpad(软件指令决定来源、确定性)在仿真里要用不同模型:

- **cache**:需要命中率 / 替换策略 / 非确定性 latency 分布。
- **scratchpad**:编译期可解析的确定性访存。

**落地**:**事件类型** `ScratchpadAccess`(确定 latency)vs `CacheAccess`(带命中/未命中分支)。对 archax 的目标(面向 Groq 式静态、编译器决定数据放置的架构),**scratchpad 模型是默认**,但保留 cache 语义建模能力以做对照。

---

## 6. 顶层"粗粒度 vs 细粒度"是 system-level S1 的一个根决策

**COMPUTE 来源**:[gpu-as-tiled-tpu](../07-chip-organization/gpu-as-tiled-tpu.md)。

**archax 映射**:这是 **Topology** 在 **system-level S1** 的根决策。粗粒度(大 array,跨单元数据贵)vs 细粒度(小 array 平铺,局部便宜跨片贵)是一条分类轴;splittable systolic array 是这条轴上的**非端点解**。

**落地**:跨单元数据移动的边界带宽(TPU 的"2 条线" vs GPU 的"16 条线")应是一个可量化参数,直接喂给 data-movement-first 的代价函数。splittable 建模为**可变 `array_edge`**——运行时按 workload 矩阵尺寸可切,目标最大化 `effective_macs = peak_macs × utilization`。

---

## 7. 时钟/流水层大多可折叠,但反馈环是必须保留的例外

**COMPUTE 来源**:[pipeline-register-insertion](../04-clocking-and-pipeline/pipeline-register-insertion.md) + [feedback-loop-clock-constraint](../04-clocking-and-pipeline/feedback-loop-clock-constraint.md)。

**archax 映射**:这是 **Capability**(频率上限)的建模边界。pipeline register insertion 是纯 area↔frequency trade-off,M2 cycle-level 之下大多可抽象掉。**唯一必须保留的**是带反馈环逻辑(累加器/规约)设定的关键路径下界——它给出"这个微架构能跑多快"的硬上限,直接影响 `throughput = 每周期工作量 × 频率` 的频率项。

**落地**:前馈块和反馈块用两套模型。前馈块 `max_freq` 可通过增加流水深度提升(可折叠);反馈块 `max_freq = 1 / loop_critical_path_ns` 是固定下界,只能改环内进位结构提升。若 archax 要在 M2 层给可信频率估计,需对累加器/规约的反馈环**单独建模其关键路径**,而非把所有逻辑当可任意切分的流水线。注意 `acc_bits` 同时进数值正确性模型和频率上限模型——这个耦合必须显式保留。

---

## 汇总:7 条 → archax 四元抽象映射表

| # | 启示 | 主要落点 | 关键状态变量 / 事件 |
|---|---|---|---|
| 1 | 计算/通信比是一等派生量 | Execution IR | `bytes_moved`、`theoretical_macs`、`reuse_rate`(任意粒度可求) |
| 2 | 位宽二次缩放 | Capability | `mul_bits²`、`acc_bits`、`fungibility_k` |
| 3 | RF↔array 面积预算 | microarch M1 | `N`、`RF_entries`、`RF_ports`、`RF_cost_per_PE` |
| 4 | 配置流 vs 稳态流 | Interaction | `kind ∈ {config, steady}` |
| 5 | cache vs scratchpad | Interaction | 事件 `ScratchpadAccess` / `CacheAccess` |
| 6 | 粗粒度 vs 细粒度 | Topology / S1 | `granularity`、`boundary_bw`、可变 `array_edge` |
| 7 | 反馈环关键路径 | Capability(频率) | `loop_critical_path_ns`、`acc_bits` |

---

## 本篇在主线上的位置

这一篇把[计算 / 通信比](../01-overview/compute-communication-ratio.md)从"知识主线"转成"建模主线":它**就是把比值做成 Execution IR 一等派生量**(第 1 条),其余 6 条是这个比值在 Resource/Topology/Interaction/Capability 各抽象层的具体落点。COMPUTE 域到此闭环——从一个逻辑门的 p×q,到整片芯片的跨单元带宽,同一个比值贯穿始终,最终成为 archax 里可审计、可在任意粒度求值的物理量。

---

## 建模启示

(本篇即建模启示的汇总章,不再单设。上面 7 条 + 映射表即是。)

**一条贯穿性的实现建议**:不要为每个抽象层各造一套指标。`bytes_moved` / `theoretical_macs` / `reuse_rate` 这三个量,定义一次,在 Topology 的每个聚合节点(PE → array → core → chip)上递归求和、求比。这样计算 / 通信比就天然是"任意粒度可求值的派生量"(第 1 条),而 7 条启示就是这套递归求值在不同 Resource 类型上的参数化——这正是 data-movement-first 原则落到 Execution IR 的方式。
