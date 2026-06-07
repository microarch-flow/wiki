# 频率 ≠ 吞吐:为什么把时钟推到极致反而更慢

上级:[04 · 时钟与流水](./README.md)
相关:[pipeline register 插入](./pipeline-register-insertion.md)、[全局时钟同步](./global-clock-synchronization.md)、[反馈环的时钟约束](./feedback-loop-clock-constraint.md)
主线:[计算 / 通信比](../01-overview/compute-communication-ratio.md)——本篇:分母(同步)花过头,比值反降,吞吐反降。

---

## 这页在回答什么问题

[pipeline register 插入](./pipeline-register-insertion.md) 说切逻辑插 register 能提频提吞吐。那把时钟推到极致(切到不能再切)是不是吞吐最大?**恰恰相反。** 本篇点破"高频率 = 高吞吐"这个最常见的误解,给出吞吐的正确分解,并把它接回 batch size 那条更大的张力。

---

## 1. 极端案例:频率推到极致,面积全花在同步上

把一个 register + 一个 AND 门组成极小环路,关键路径只有一个门,能跑到 **5–6 GHz**。看起来很快。但看面积构成:

```
极小流水级:  [1 个 AND 门] ─│reg│
              ↑ 逻辑:1 门当量
                            ↑ register:~6–10 门当量
              ────────────────────────────────
              面积里 ~90% 是 register(同步),~10% 才是逻辑(计算)
```

**几乎所有面积都花在同步(register)上,而非做有用功的逻辑。** 你确实跑到了 5–6 GHz,但每个 register 只夹着 1 个门的有用计算——单位面积的有用功极低。

> ⚠️ 常见误解:把"高时钟频率"等同于"高吞吐"。频率只是吞吐的一个因子;另一个因子是**每周期每单位面积做了多少有用功**。把频率推到极致,是用面积效率换频率,后者的损失可能压倒前者的收益。

---

## 2. 吞吐的正确分解

> **吞吐 = (每周期做的有用功 / 面积) × (每秒周期数)**
>
> 即:吞吐 = 面积效率 × 频率

两个因子互相拉扯:

- **提频**(多插 register):频率 ↑,但每级有用功被 register 面积稀释 → 面积效率 ↓。
- **降频**(少插 register,每级塞更多逻辑):面积效率 ↑(register 占比小),但频率 ↓。

把频率推到极致 = 面积效率塌到极低 = **两个因子相乘后,吞吐反而下降**。你得到的是**低延迟 + 低吞吐**:每个操作很快出结果(延迟低),但单位面积每秒的总操作数很少(吞吐低)。

```
            频率低、每级逻辑厚           频率高、每级逻辑薄
面积效率:   高(register 占比小)        低(register 主导)
频率:       低                          高
吞吐(乘积): ← 中间某处最大 →            两端都不是最优
```

最优点在中间——这正是 [门深预算 ~10–30 门/级](./global-clock-synchronization.md#2-时钟周期由最长关键路径决定) 的来源:不是越短越好,而是平衡面积效率和频率的甜点。

---

## 3. 这是 batch size 张力的同一张面孔

频率推太高 = 牺牲面积效率 = 减少了可榨取的并行度。这和**推理服务里的 batch size 张力是同一个东西**:

| | 低延迟取向 | 高吞吐取向 |
|---|---|---|
| 频率维度 | 频率推到极致(每级薄) | 频率适中(每级厚、面积效率高) |
| batch 维度 | batch 小(单用户首 token 快) | batch 大(每小时总 token 多) |
| 得到 | 低延迟,低吞吐 | 高延迟,高吞吐 |

**因为** 两者都是在"让单个操作更快"和"让单位资源的总产出更高"之间选边,**所以** 它们是同一张力的两个面孔。频率推太高,就像 batch 压太小——优化了延迟,牺牲了吞吐。

> 这条张力是 MatX 和整个 AI 推理硬件的核心矛盾:Pope 的 inference 工作(PaLM 540B,大 batch 76% MFU vs 低 batch 29ms/token)正是在这条 Pareto 前沿上找点。负载侧如何用 MQA/GQA 降 KV 搬运来改善 decode 的吞吐/延迟,见 [`Workload/.../attention-variants-and-efficiency`](../../../../workload-wiki/01-foundation-model-components/attention-variants-and-efficiency.md)。

---

## 4. 本篇在主线上的位置

这一篇点破了主线上一个反直觉的拐点:**分母(同步 register)花过头,比值反而降。** 抬比值不是单调地"多切、提频",而是在面积效率和频率之间找平衡点。频率只是吞吐的一个因子,另一个是单位面积的有用功;把前者推到极致会塌掉后者。这和 batch size 张力同源——都是延迟与吞吐的根本权衡。本章到此完成:同步有代价([§global](./global-clock-synchronization.md))、可花分母换频率([§pipeline](./pipeline-register-insertion.md))、反馈环设硬下界([§feedback](./feedback-loop-clock-constraint.md))、但花过头反降吞吐(本篇)。

---

## 建模启示

- **频率不是越高越好,是吞吐这个乘积里的一个因子。** archax 在评估一个微架构时,目标函数应是 `throughput = area_efficiency × frequency`,而非单独最大化 frequency。
- **必须显式建模的状态变量**:`useful_work_per_cycle_per_area`(面积效率)、`frequency`。两者都随 `pipeline_depth` 变化但方向相反——存在一个使乘积最大的最优深度。
- **核心派生量**:`throughput = (useful_macs_per_cycle / area) × f`。扫描 `pipeline_depth` 时,throughput 是单峰的,峰值对应 ~10–30 门/级。
- **关心延迟 vs 吞吐取舍时必须保留**:这是和 batch size 同一维度的 Pareto 轴。建模时 `frequency` 和 `batch_size` 应是同一张延迟-吞吐 Pareto 图上的两个旋钮,不要分开优化。
- **事件/数据结构草图**:`MicroArch{pipeline_depth, batch} → {latency, throughput}`,在延迟-吞吐平面上画出 Pareto 前沿。频率推到极致和 batch 压到 1 都落在"低延迟低吞吐"那个角——通常不是想要的工作点。
