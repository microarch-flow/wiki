# 先进封装分类框架:2D/2.5D/3D

上级:[后道封装](./README.md)
相关:[工艺节点、封装路线、测试阶段的命名体系](../01-overview/taxonomy.md), [2.5D 路线](./2.5d-routes/README.md), [3D 路线](./3d-routes/README.md)

## 这页在回答什么问题

2D、2.5D、3D、interposer、RDL、bridge、TSV、Hybrid Bonding 这些词为什么不能放在同一层分类。正确分类要先问 die 怎么摆，再问靠什么载体连接、用什么连接工艺、如何制造和测试。

## 第一维: die 怎么摆

```text
2D:
  die(s) on substrate, package-level connection

2.5D:
  dies side-by-side on high-density intermediate platform

3D:
  dies stacked vertically with high-density vertical connection
```

2D 的核心是平面封装和板级/基板级互连。2.5D 的核心是多个 die 并排放在 interposer、RDL 或 bridge 这类高密度中介平台上。3D 的核心是 die 在垂直方向堆叠，并用 micro-bump、hybrid bonding、TSV 等结构实现上下连接。

2.5D 不是 3D 的低级版本。对于 logic + HBM，2.5D 常常是更现实的系统最优点：HBM stack 自身是 3D memory，logic 与 HBM 之间采用并排近距互连，可以避免把高功耗 logic 和 memory 直接垂直叠在一起带来的热和测试压力。

## 第二维: 中间互连载体是什么

| 载体 | 用在哪里 | 解决的问题 | 主要代价 |
| --- | --- | --- | --- |
| Organic substrate | 2D/传统 FC-BGA/部分 MCM | 机械支撑、板级引出、成本 | 线宽线距和局部互连密度有限 |
| Silicon interposer | 2.5D | 极高 routing density、HBM 友好 | 成本、面积、TSV、warpage |
| Fan-out RDL | 2D/2.5D-like RDL platform | 扇出、多 die、较灵活平台 | die shift、RDL cracking、平整度 |
| Embedded bridge | 2.5D 局部高密度 | 只在关键区域提供硅级互连 | 桥区过渡、对位和协同复杂 |
| Active base die | 3D/高级异构集成 | 底层提供逻辑/互连/电源管理 | 热、良率和设计复杂度 |

这个维度解释了为什么“先进封装就是 CoWoS”是不准确的。高密度封装可以靠 full silicon interposer、RDL interposer、local bridge、fan-out 或 3D stacking 实现，不同路线优化目标不同。

## 第三维: 连接工艺是什么

| 连接工艺 | 主要对象 | 关键 trade-off |
| --- | --- | --- |
| C4 / solder bump | die 到 substrate | 成熟、pitch 较大、适合常规 flip-chip |
| Micro-bump | die 到 interposer / die-to-die | 成熟度高，pitch 受焊料和可靠性限制 |
| Hybrid Bonding | die-to-die / wafer-to-wafer | pitch 可大幅缩小，但表面平整度、洁净度和对准要求极高 |
| TSV | 硅内垂直通路 | 让信号/电源穿过硅，但带来面积、应力和工艺复杂度 |
| RDL via / Cu trace | 封装级重布线 | 灵活扇出和连接，但受材料、应力和线宽线距限制 |

连接工艺不是结构分类。TSV 可以出现在 silicon interposer，也可以出现在 HBM stack；Hybrid Bonding 是键合机制，不等于 3DIC 全部；RDL 是封装级重布线，不只属于 fan-out。

## 第四维: 制造组织方式

制造组织方式回答“对象以什么形态进入 assembly”。

| 方式 | 典型含义 | 适合条件 | 主要代价 |
| --- | --- | --- | --- |
| Chip-first fan-out | die 先埋入，再做 RDL | 成本敏感、较成熟扇出 | die shift 和 mold 影响 RDL |
| Chip-last / RDL-first | 先做 RDL，再贴 die | fine-pitch、多 die、高密度 | 对位、carrier、接合要求高 |
| W2W / WoW | wafer 对 wafer 键合 | 规则、尺寸匹配、高良率 | 坏 die 耦合强 |
| D2W / CoW | known-good die 贴到 wafer | 异构、高价值、KGD 可用 | 节拍、handling、对位复杂 |

这部分会在 [Chip-first vs Chip-last](./2.5d-routes/fan-out-chip-first-vs-chip-last.md) 和 [W2W vs D2W](./3d-routes/w2w-vs-d2w.md) 展开。

## 快速对照

| 问题 | 如果答案是 | 优先看 |
| --- | --- | --- |
| 需要 logic + HBM 超宽近距互连吗 | 是 | 2.5D interposer/RDL/bridge |
| 只需要中等密度多 die 扇出吗 | 是 | fan-out RDL |
| 只有局部 D2D 密度极高吗 | 是 | embedded bridge |
| 需要垂直堆叠压缩距离和 footprint 吗 | 是 | 3DIC |
| 需要异构 die 且良率必须可控吗 | 是 | D2W + KGD |
| 成本和成熟度优先，带宽密度不极端吗 | 是 | 2D/传统 flip-chip/substrate |

## 常见误解

常见误解是“2.5D 是过渡，3D 是终点”。实际 2.5D 和 3D优化不同问题。2.5D 擅长横向集成大功耗 logic 与 HBM，3D 擅长垂直压缩互连距离和 footprint。

另一个误解是“用了 TSV 就是 3D”。TSV 是硅内垂直通孔能力，可能用于 2.5D silicon interposer，也可能用于 HBM stack 或 3DIC。结构分类要看 die 如何组织，而不是看是否出现某个工艺组件。

## 一句话理解

先进封装分类要按结构、载体、连接工艺和制造组织方式拆开；平台名只是这些底层维度的组合。

## 架构师启示

如果我在方案文档里写“采用 2.5D 先进封装”，信息还不够。需要明确是 full silicon interposer、RDL interposer 还是 embedded bridge，die-to-die 连接是 micro-bump 还是更高密度键合，是否依赖 KGD，以及 package 是否能支撑热和供电。

一个具体决策例子：两个 chiplet 间高带宽但只在局部区域通信，embedded bridge 可能比 full interposer 更经济；compute die 周围要放多个 HBM stack，full interposer 或 RDL/interposer 混合路线更可能合适；logic-on-cache 垂直堆叠才进入 3DIC 主战场。
