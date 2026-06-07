# 04 · 时钟与流水:同步的代价

[03 章](../03-systolic-array/) 把比值翻转了,但留下一个问题:阵列要跑多快?本章讲同步的物理代价。核心认识:**register 不做任何有用计算,它只为"让上亿单元对上拍"付面积——所以时钟/流水层是纯分母,而且花过头会反噬吞吐。**

## 篇目

1. **[全局时钟同步](./global-clock-synchronization.md)**
   为什么用全局时钟而非软件锁;时钟周期 = 最长关键路径;TSMC ~10ps 门延迟 → 每周期 ~10–30 门深预算;25% margin 是工程确定性不是赌概率。

2. **[Pipeline register 插入](./pipeline-register-insertion.md)**
   切逻辑插 register → 频率翻倍、代价一个 register;纯 area↔frequency 交易;两个失效边界(过切、反馈环)。

3. **[反馈环的时钟约束](./feedback-loop-clock-constraint.md)** ← 最硬约束
   累加器为什么不能插 register(劈成奇偶两条链);反馈环关键路径 = 时钟周期最硬下界;只能靠改环内进位结构提频,不能靠流水化绕过。

4. **[频率 ≠ 吞吐](./frequency-is-not-throughput.md)**
   register ~6–10 门当量;吞吐 = 面积效率 × 频率;推频到极致 = 低延迟低吞吐;和 batch size 同源张力。

## 本章在主线上的位置

时钟/流水层是[主线](../01-overview/compute-communication-ratio.md)里**纯分母**的一章:同步无有用功,代价由关键路径门深定量。可以花分母(register)换频率,但反馈环设了硬下界,且花过头会反噬吞吐。要点:**频率只是吞吐的一个因子,不是吞吐本身。**

→ 这些门要不要做成可重配?进入 [05 · FPGA vs ASIC](../05-fpga-vs-asic/)。
