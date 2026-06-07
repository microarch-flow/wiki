# Pipeline register 插入:切逻辑换频率的纯 area↔frequency 交易

上级:[04 · 时钟与流水](./README.md)
相关:[全局时钟同步](./global-clock-synchronization.md)、[反馈环的时钟约束](./feedback-loop-clock-constraint.md)、[频率 ≠ 吞吐](./frequency-is-not-throughput.md)
主线:[计算 / 通信比](../01-overview/compute-communication-ratio.md)——本篇:用更多分母(register)换更高频率,是一笔纯交易,但有上限。

---

## 这页在回答什么问题

[全局时钟同步](./global-clock-synchronization.md) 说时钟周期由最长关键路径决定。那想提频,就得缩短关键路径。最朴素的手段:**把一团逻辑云从中间切两半,中间插一个 register。** 本篇讲这个手段的机制、它纯粹的 area↔frequency 交易性质,以及为什么它在芯片里是大量的、半自动的设计工作。

---

## 1. 机制:切一刀,频率翻倍

一团组合逻辑云,延迟决定了它所在的时钟周期。从中间切开,插一个 register:

```
[─────────── 长逻辑云(延迟 T) ───────────]
         ↓ 中间插一个 register
[──── 半段(T/2)────]─│reg│─[──── 半段(T/2)────]
```

**因为** 每半段延迟减半(T → T/2),关键路径缩短一半;**所以** 时钟周期可减半 → 频率翻倍 → 吞吐翻倍。代价:**多一个 register 的面积**(~6–10 门当量)。

数据现在要两拍才穿过原来的逻辑(流水线 latency +1 拍),但每拍都能接收新数据(throughput 翻倍)。这是流水线的本质:**用延迟换吞吐**。

---

## 2. 这是纯粹的 area↔frequency 交易

把它和[全局时钟同步](./global-clock-synchronization.md)的门深预算挂起来:

```
切之前:逻辑深 30 门 → 一个周期装不下高频 → 频率受限
切之后:两段各 15 门 → 每段都能塞进更短周期 → 频率翻倍,代价 1 个 register
```

**这是一个纯粹的时钟速度 ↔ 面积 trade-off**:每多插一个 register,就多花一份面积,换来一段更短的关键路径(更高频率潜力)。没有别的隐藏成本(除了 latency 增加,但流水化负载不在乎 latency)。

在芯片里**大量插这种 register 是设计工作的一大部分**,由综合工具自动 retiming + 设计师手工平衡共同完成——目标是把每一级的门深都压到 ~10–30 之间(见 [门深预算](./global-clock-synchronization.md#2-时钟周期由最长关键路径决定)),让没有任何一级成为拖慢全片的关键路径。

---

## 3. 边界:不是所有逻辑都能随便切

⚠️ 常见误解:以为"插 register 提频"是免费午餐,切得越多越快。两个边界:

1. **过切会降吞吐**(下一篇 [频率≠吞吐](./frequency-is-not-throughput.md)):切到极致,register 面积主导,面积效率崩塌,吞吐反而降。register 不是免费的——它本身占 ~6–10 门当量,远大于它锁存的那点逻辑。
2. **反馈环不能切**(下一篇 [feedback-loop](./feedback-loop-clock-constraint.md)):带自反馈的逻辑(如累加器),从中间插 register 会**改变语义**,不是单纯变慢。这是硬约束,不是 trade-off。

所以"插 register 提频"只在**前馈逻辑、且没切过头**时是那个干净的 area↔frequency 交易。这两个边界是本章后两篇的主题。

---

## 4. 本篇在主线上的位置

pipeline register 是[计算 / 通信比](../01-overview/compute-communication-ratio.md)里一个**可调的分母**:花 register 面积(分母)换更高频率,从而在同样的算术单元上跑出更高吞吐。在没切过头、非反馈环的前提下,这是一笔干净的交易——分母增一点,频率增一倍。但它有两个边界(过切、反馈环),让这笔交易在极端处失效。本篇确立"切逻辑换频率"的机制,后两篇划定它的失效边界。

---

## 建模启示

- **pipeline register insertion 在 archax 当前抽象层级大多可折叠。** 它是纯 area↔frequency trade-off,M2 cycle-level 之下大多可抽象掉——建模时把一个逻辑块当成"流水深度 d、吞吐 1/cycle、latency d"即可,不必逐级建模 register 位置。
- **必须显式建模的状态变量**:`pipeline_depth d`(影响 latency,不影响稳态 throughput)、每级 `gate_depth`(决定能否达到目标频率)、register 面积开销。
- **可折叠**:前馈流水线的具体 register 位置 → 折叠成 `(latency = d cycles, throughput = 1/cycle)`。综合工具的 retiming 细节不必建模。
- **不可折叠的例外**:反馈环——它**不能**用"增加流水深度"建模,因为插 register 改变语义。反馈环的关键路径是频率硬下界,必须单独建模,见 [feedback-loop-clock-constraint](./feedback-loop-clock-constraint.md)。
- **事件/数据结构草图**:`PipelinedBlock{depth, gate_depth_per_stage} → {latency = depth, throughput = 1, max_freq = 1/(gate_depth_per_stage · gate_delay)}`。前馈块用这个;反馈块走另一套模型。
