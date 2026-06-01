# 旋钮敏感度与耦合

上级：[06 性能建模与调优](./README.md)

相关：[优化与调参手册](./optimization-playbook.md)、[参数与公式速查](./parameter-reference.md)、[模型数据结构与事件规范](./model-schema.md)、[从抽象模型到系统诊断](./modeling-method.md)

## 这页在回答什么问题

[optimization-playbook](./optimization-playbook.md) 反复说"旋钮互相耦合""越大越好是错的""过某点收益递减甚至反噬"——这些判断都对，但没给出**耦合结构本身**。架构探索工具的核心动作是剪枝设计空间：你需要知道哪个旋钮影响哪个指标、是单调还是非单调、拐点大概在哪、哪两个旋钮必须一起扫。这页把这些显式列成表，让扫参从"全排列"变成"有结构的搜索"。

## 先区分单调旋钮和非单调旋钮

这是剪枝的第一刀。**单调旋钮**可以二分/爬坡找最优；**非单调旋钮**有内部拐点，必须 sweep 才能看到反噬，不能靠"往大拧"。

- 单调（在合理区间内）：`data_width`、`num_channels`（隔离需求驱动）。
- 非单调（有拐点，必须 sweep）：`burst_len`、`max_outstanding`、`queue_depth`、`tile_bytes`。
- 模式选择（无大小关系，是离散 trade-off）：`priority_mode`、`completion_mode`。

非单调旋钮的拐点来源都能在 [parameter-reference](./parameter-reference.md) 的公式里找到：outstanding 拐点来自 Little's Law 的足够点，burst 拐点来自效率公式与占路时间的平衡，tile 拐点来自 buffer 容量与 row locality 的拉锯。

## 敏感度矩阵：旋钮 × 指标

每格表示"增大该旋钮，对该指标的主导效应"。↑ 改善、↓ 恶化、∩ 先升后降（有拐点）、— 基本无关、◇ 取决于模式。

| 旋钮 ＼ 指标 | 有效带宽 | 尾延迟(P99) | overlap 成立 | 稳定性/可诊断性 |
| --- | --- | --- | --- | --- |
| `burst_len` ↑ | ∩（先升，过长压控制流） | ↓（占路时间↑） | — | ↓（大 burst 放大热点） |
| `max_outstanding` ↑ | ∩（到足够点后平） | ∩（过点后 return path 堆积） | ↑ | ↓ |
| `queue_depth` ↑ | ↑（喂得更满） | ↓（completion backlog↑） | ↑ | ↓ |
| `tile_bytes` ↑ | ↑（burst/row locality 好） | — | ↓（吃 buffer，双缓冲难） | — |
| `num_channels` ↑ | ↑（并行/隔离） | ↑（关键流不被压） | ↑ | ↑ |
| `priority_mode` ◇ | — | ◇（保护关键小流则↑） | — | ◇ |
| `completion_mode` ◇ | — | ◇（poll 低延迟 / batch 高吞吐） | — | ◇ |

读法：一个旋钮在"有效带宽"列是↑、在"尾延迟"列是↓，就是典型的**吞吐换尾延迟**——这正是不能单目标拧到底的原因。

## 耦合关系：哪些旋钮必须一起扫

独立扫单个旋钮会得到错误最优，因为它们共享同一资源或公式变量。下面是必须成组扫的耦合簇：

| 耦合簇 | 旋钮 | 为什么不能独立扫 | 公式来源 |
| --- | --- | --- | --- |
| latency-hiding 簇 | `max_outstanding` × `queue_depth` × `interconnect_RTT` | 三者共同决定 Little's Law 的足够点；只扫一个会把另一个的不足误判成它的拐点 | 公式 2 |
| 粒度簇 | `burst_len` × `tile_bytes` × `row_hit_prob` | tile 决定 burst 形状，burst 决定 row locality；分开扫看不到 DRAM 侧真实收益 | 公式 3、4 |
| 供数簇（AI） | `tile_bytes` × buffer 数 × `T_compute` | 决定 overlap 是否成立，单看 DMA 侧会漏判断流条件 | 公式 5 |
| 完成路径簇 | `completion_mode` × `queue_depth` × consumer 速率 | 决定软件可见尾延迟与 backlog，与数据路径带宽无关 | 公式 6 |

实践含义：探索时**按簇分组做二维/三维 sweep**，簇之间可近似正交、先固定其余簇。这把"N 个旋钮全排列"降成"几个低维 sweep"，是设计空间剪枝的主要杠杆。

## 一个减少 sweep 次数的优先级

1. **先固定模式旋钮**（priority/completion）到合理默认，它们是离散 trade-off，留到最后调。
2. **先扫粒度簇**：burst×tile 进入合理区间，因为它常是最大单项收益（[optimization-playbook](./optimization-playbook.md) 同序）。
3. **再扫 latency-hiding 簇**：在固定粒度下找 outstanding/queue 拐点。
4. **多流场景才扫供数簇和完成路径簇**：单流系统可跳过。
5. **最后回到模式旋钮**：在确定的工作点上比较 priority/completion 策略。

反过来做（先调 QoS、再调粒度）通常只会放大噪声——因为粒度没对时，模式旋钮的效应被淹没。

## 把敏感度用进模型

在 [model-schema](./model-schema.md) 的 `DMAModel` 上，敏感度矩阵对应"哪些 `Knobs` 字段对哪些 `Metrics` 字段有梯度"。架构探索工具可以据此：

- 对 — 格的旋钮-指标对**跳过 sweep**，直接固定默认。
- 对 ∩ 格**必须 sweep** 且记录拐点位置，不能用二分。
- 对耦合簇**联合采样**，而不是逐参 OAT（one-at-a-time）。

这样模型既能覆盖关键 trade-off，又不会在无关维度上浪费仿真预算。

## 常见误解

常见误解：`每个旋钮独立扫到最优，组合起来就是全局最优`。实际上耦合簇内独立扫会得到错误拐点。

常见误解：`所有旋钮越大越好或都有拐点`。实际上要先分单调/非单调/模式三类，处理方式完全不同。

常见误解：`敏感度只影响调优，不影响建模`。实际上它直接决定模型该在哪些维度保精度、哪些维度可固定，是剪枝设计空间的依据。

## 一句话理解

把旋钮分成单调/非单调/模式三类，用"旋钮×指标"敏感度矩阵和"必须一起扫"的耦合簇，把全排列扫参降成几个低维 sweep——这是架构探索剪枝设计空间的核心结构。
