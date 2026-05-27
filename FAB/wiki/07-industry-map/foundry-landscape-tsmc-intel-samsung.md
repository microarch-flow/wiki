# 代工厂版图:TSMC/Intel/Samsung

上级:[产业地图](README.md)
相关:[全球产业链全景图](industry-chain-overview.md), [OSAT 版图](osat-landscape-ase-amkor-jcet-tongfu.md), [大陆 vs 台积电](mainland-china-vs-tsmc-real-gap.md)

## 这页在回答什么问题

TSMC、Intel、Samsung 在先进封装中的位置分别是什么，它们为什么不能只按“封装厂”理解，而要看先进逻辑、封装平台、设计生态和客户导入的组合。

## TSMC

TSMC 的公开平台以 3DFabric 组织前端 3D stacking 和后端先进封装。公开资料中，SoIC 属于前端 3D silicon stacking，CoWoS 和 InFO 属于后端封装家族，用于 HPC、AI 和高带宽 memory 场景。

| 平台 | 技术含义 |
| --- | --- |
| CoWoS-S/R/L | 2.5D logic + HBM / chiplet 集成平台族 |
| InFO | Fan-out / RDL 相关封装平台 |
| SoIC | 前端 3D stacking，支持 chiplet 级堆叠 |
| 3DFabric | 把前端 3D 与后端封装组合成平台叙事 |

TSMC 的关键不只是某一条封装路线，而是先进逻辑、先进封装、OIP 生态和 AI/HPC 客户导入形成闭环。

## Intel Foundry

Intel 的公开封装叙事围绕 EMIB、Foveros 和 Foveros Direct。EMIB 是 embedded bridge 2.5D 路线，Foveros 家族覆盖 2.5D/3D 组织方式，Foveros Direct 强调 Cu-to-Cu hybrid bonding 和高密度 die-to-die 连接。

| 平台 | 技术含义 |
| --- | --- |
| EMIB | substrate 内嵌 silicon bridge，支持 logic-logic 和 logic-HBM 连接 |
| Foveros-S/R | 硅 interposer 或 RDL interposer 的 2.5D 组织 |
| Foveros Direct 3D | active base die 上的 3D stacking，使用 hybrid bonding |
| EMIB 3.5D | 横向 bridge 与垂直 Foveros 组合 |

Intel 的路线特征是 bridge 与 3D 组合鲜明，适合观察“局部高密度 + 垂直堆叠”如何替代部分 full interposer 场景。

## Samsung Foundry

Samsung Foundry 的公开先进封装包括 I-Cube、H-Cube、X-Cube 等家族。I-Cube 面向 2.5D 逻辑与 HBM/芯粒集成，X-Cube 面向 3D IC 垂直堆叠。

| 平台 | 技术含义 |
| --- | --- |
| I-CubeS | silicon interposer 2.5D |
| I-CubeE | bridge-like / embedded interconnect 方向 |
| H-Cube | 大尺寸 hybrid substrate 方向 |
| X-Cube | 3DIC 垂直堆叠 |

Samsung 的特点是同时具备 foundry、memory 和先进封装叙事，因此在 logic + HBM 协同上有结构基础。

## 三者对照

| 维度 | TSMC | Intel Foundry | Samsung Foundry |
| --- | --- | --- | --- |
| 核心平台表达 | 3DFabric / CoWoS / InFO / SoIC | EMIB / Foveros / Foveros Direct | I-Cube / H-Cube / X-Cube |
| 2.5D 路线 | CoWoS-S/R/L | EMIB、Foveros-S/R | I-CubeS/E、H-Cube |
| 3D 路线 | SoIC | Foveros Direct | X-Cube |
| 产业特征 | foundry + packaging 生态闭环强 | bridge + 3D 组合突出 | foundry + memory + package 组合 |

## 一句话理解

TSMC、Intel、Samsung 的先进封装竞争不是单个 package 名词竞争，而是先进逻辑、2.5D/3D 平台、HBM 协同、设计生态和量产导入的系统能力竞争。

## 架构师启示

架构师选平台时，应把平台名翻译成结构能力：全局 interposer、局部 bridge、RDL interposer、3D hybrid bonding、HBM 协同和测试支持。不同 foundry 的平台组合会改变 chiplet 切分、NoC 形态、热路径和良率策略。
