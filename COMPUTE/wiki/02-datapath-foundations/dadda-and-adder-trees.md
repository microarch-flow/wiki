# 压缩树与进位结构:Wallace、Dadda 与最终加法器

上级:[02 · datapath 基础](./README.md)
相关:[从门搭 MAC](./multiply-accumulate-from-gates.md)、[面积随位宽二次缩放](./quadratic-bitwidth-scaling.md)、[反馈环的时钟约束](../04-clocking-and-pipeline/feedback-loop-clock-constraint.md)
主线:[计算 / 通信比](../01-overview/compute-communication-ratio.md)——压缩树是"把 p×q 个部分积搬成一个和"的纯通信结构,本篇是分母侧的精打细算。

> **[补全] 篇**:基准长文只点到 Dadda multiplier。本篇补全 Wallace vs Dadda 的对比、carry-save 为何避开进位链、以及最终 vector-merge 加法器的进位结构选择——这三者共同决定乘法器的关键路径,直接喂给 [04 时钟章](../04-clocking-and-pipeline/global-clock-synchronization.md)。

---

## 这页在回答什么问题

[上一篇](./multiply-accumulate-from-gates.md)把"用 full adder 沿列压缩部分积"当黑盒。本篇打开它,回答三个问题:(1) 同样是 3→2 压缩,**Wallace 和 Dadda** 差在哪、各放弃了什么;(2) 为什么压缩树要用 **carry-save** 而不是逐列等进位;(3) 压缩到最后那两行,用什么**进位结构**的加法器合并——这一步常常是整个乘法器的关键路径所在。

---

## 1. 问题:p×q 个部分积,怎么加成一个数最省最快

部分积阵列是一个高度不齐的"比特山":中间列最高(多到 min(p,q) 个比特),两端列矮。把它加成最终的 p+q 位结果,有两种朴素做法都不好:

- **逐列 ripple**:一列一列加、进位逐列传递。慢——进位链长度 ∝ 位宽,延迟线性累积。
- **直接做一棵加法器**:忽略了"很多比特在同一列、可以并行压缩"的结构。

好的做法分两段:**先用 carry-save 压缩树把比特山压到只剩 2 行(高度从 ~p 降到 2),再用一个快速进位加法器把这 2 行合并成最终结果。** Wallace 和 Dadda 都是第一段的调度策略。

---

## 2. carry-save:为什么压缩树不在中途传播进位

full adder 是 3→2 compressor:吃 3 个同列比特,吐 1 个 sum(留本列)+ 1 个 carry(进高一列)。关键在于——**压缩树里这些 carry 不立刻被消化,而是和别的比特一起留到下一层再压**。

```
第 k 层:每列若有 ≥3 个比特,用 full adder 压;carry 甩到高一列下一层
         ────────────────────────────────────────────────
         好处:任何一层的延迟 = 1 个 full adder 延迟(常数!)
                与位宽无关,因为没有任何一层在等进位逐列传播
```

这就是 **carry-save**(进位保存):进位被"保存"为额外的一行比特,而不是当场沿列传播。**因为** 不等进位,**所以** 每一层的延迟是常数(一个 full adder),整棵树的延迟 ∝ log(高度) 而非 ∝ 位宽。这是压缩树相对 ripple 的根本优势,也是它在主线上的意义:用并行结构把"加法这件通信"的延迟从线性压到对数。

> ⚠️ 常见误解:以为乘法器慢在"乘法本身"。乘法(AND 生成部分积)是一层门,极快。慢的是**把部分积加起来**——所以乘法器优化的主战场是加法树的结构,不是乘法。

---

## 3. Wallace vs Dadda:同为 3→2,调度相反

两者都用 full adder(3→2)和 half adder(2→2)把比特山压到高度 2,但**何时压**的策略相反:

| | Wallace | Dadda |
|---|---|---|
| 策略 | **尽早压缩**:每一层尽可能多地压掉比特 | **尽晚压缩**:只压到"不超过下一个 Dadda 高度上界"为止 |
| full/half adder 数 | 偏多(尤其 half adder 多) | **最少**(half adder 用得很省) |
| 最终加法器宽度 | 略窄 | 略宽(因为压得晚,末行更长) |
| 布线 | 略规则 | 略不规则 |
| 层数(延迟) | 二者相同,都 ∝ log(高度) | 相同 |

**取舍判断**:

- **Dadda 通常更省面积**——它推迟压缩,用尽可能少的 full/half adder 达到同样的高度上界,因此 adder 数最少。代价是末级加法器更宽、布线略不规则。**面积敏感、追求 adder 数最少时选 Dadda**,这也是为什么基准长文直接以 Dadda 为标准做法。
- **Wallace 更直观、布线略规则**,但 adder(尤其 half adder)用得多,面积略大。两者关键路径层数相同,所以**性能上几乎打平,差别主要在面积**。

> 一个类比(仅此一处):Wallace 像"能压就压"的激进减脂,Dadda 像"算好目标体重再精确减到刚好"——殊途同归到高度 2,但 Dadda 路上少做了很多无用功(多余的 half adder)。用完即弃,回到精确语言:二者层数相同,差异在 adder 计数与末级加法器宽度。

这也解释了上一篇那个 `full adder 数 ≈ p×q` 为何只是**首阶估计**:Wallace 和 Dadda 在同一个 p×q 下用的 full/half adder 数并不相同,精确计数依赖调度与列高度分布。

---

## 4. 最后一步:vector-merge 加法器的进位结构

压缩树把比特山压到只剩 2 行(一行 sum、一行 carry)。**最后必须把这 2 行真正相加**——而这一步,carry 必须沿位宽传播了,躲不掉。这个最终加法器(vector-merge adder / final CPA)的进位结构选择,常常是整个乘法器的**关键路径**:

```
压缩树输出:  sum  行 ─┐
             carry 行 ─┴─▶ [final CPA] ─▶ p+q 位结果
                            ↑ 这里 carry 必须沿位宽传播,延迟取决于进位结构
```

| 进位结构 | 延迟 | 面积 | 适用 |
|---|---|---|---|
| **Ripple-carry** | ∝ 位宽(慢) | 最小 | 窄位宽、不在关键路径时 |
| **Carry-lookahead (CLA)** | ∝ log,分组并行算进位 | 中 | 通用折中 |
| **Prefix(Kogge-Stone 等)** | ∝ log,进位树最浅 | 大(布线多) | 宽位宽、频率敏感、在关键路径时 |

**判断**:乘加位宽小(如 4-bit 乘 + 8-bit 累加)时,final CPA 不长,ripple 或简单 CLA 就够;一旦累加位宽大、或这条路径决定时钟频率,就上 Kogge-Stone 一类前缀加法器,用面积(布线)换关键路径的对数延迟。**这正是局部的计算 / 通信比决策:进位传播是"通信",前缀加法器是花面积把这段通信并行化。**

> 衔接 [04 时钟章](../04-clocking-and-pipeline/feedback-loop-clock-constraint.md):如果这个加法器在一个**累加反馈环**里(running sum),它的关键路径就成了时钟周期的硬下界——不能靠插 pipeline register 绕过,因为会破坏累加语义。所以"final CPA 用什么进位结构"在反馈环里不只是面积问题,而是频率上限问题。

---

## 5. 本篇在主线上的位置

压缩树是把 p×q 个部分积"搬运"并归约成一个和的纯分母结构。carry-save 用并行把这段通信的延迟从线性压到对数;Wallace/Dadda 在面积维度上精打细算;final CPA 的进位结构在延迟与面积间权衡。三者都不增加有用计算(分子恒为一次乘加),只优化为完成这次乘加所付的归约代价——**把比值往上推,靠的是让分母的加法树更快更省。**

---

## 建模启示

- **对性能/面积建模通常可整体折叠**:一个乘法器折叠成 `area ∝ p×q` + `latency ≈ t_AND + t_tree·log(min(p,q)) + t_CPA(位宽, 进位结构)`。Wallace vs Dadda 的差别对系统级吞吐几乎不可见,可折叠成一个面积系数。
- **必须保留的状态变量**:`acc_bits`(决定 final CPA 宽度)、`carry_structure ∈ {ripple, cla, prefix}`(决定该路径延迟)。当且仅当这个加法器落在**反馈环关键路径**上时,这两个量必须显式保留,因为它们决定频率上限。
- **关心面积账时**:Dadda 比 Wallace 省的那几个 half adder 在 PE 级可忽略,但乘以一个 128×128 阵列的 16384 个 PE 就不可忽略——所以**阵列级面积建模**应保留压缩树类型作为一个面积系数,PE 级则可折叠。
- **事件/数据结构草图**:`Multiplier{p, q, acc_bits, tree∈{wallace,dadda}, carry∈{ripple,cla,prefix}} → {area, critical_path_ns}`。`critical_path_ns` 馈入 [频率建模](../04-clocking-and-pipeline/frequency-is-not-throughput.md)。
