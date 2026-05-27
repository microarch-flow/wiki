# 全球产业链全景图

上级:[产业地图](README.md)
相关:[材料供应链](materials-supply-chain.md), [设备厂商版图](equipment-vendors.md), [基板与载板供应](substrate-and-carrier-supply.md)

## 这页在回答什么问题

先进封装产业链的关键层级是什么，各层之间如何协同，为什么 AI/HPC 封装会把 foundry、OSAT、HBM、材料、设备和基板绑定得更紧。

## 六层结构

| 层级 | 代表角色 | 主要责任 |
| --- | --- | --- |
| 系统需求 | 云厂商、AI ASIC/GPU/CPU/networking 厂商 | 定义带宽、功耗、HBM、chiplet 和产品形态 |
| 先进逻辑 | Foundry、IDM | 制造 compute/I/O/base die，并与封装协同 |
| Memory | HBM 厂 | 提供 HBM stack 和代际路线 |
| 封装平台 | Foundry packaging、OSAT | CoWoS/InFO/SoIC、EMIB/Foveros、I-Cube/X-Cube、Fan-out/Bridge |
| 支撑供应链 | 基板、材料、设备 | 决定工艺窗口、产能和可靠性 |
| 设计与验证 | EDA、仿真、ATE、可靠性 | PI/SI/thermal/mechanical co-design 与测试闭环 |

先进封装越高端，越不能把这些层级割裂。HBM 需求会影响封装平台，封装平台会影响基板尺寸和材料，材料与设备又决定良率和扩产速度。

## 两类平台组织方式

第一类是 foundry/IDM 深度集成模式。TSMC、Intel、Samsung 都把先进逻辑与先进封装作为平台能力来组织，优势是前端工艺、封装、设计生态和客户导入可以更早协同。

第二类是 OSAT 平台模式。ASE、Amkor、JCET、Tongfu、Huatian 等承担封装组装、测试和部分先进封装平台能力，优势是服务多客户、多工艺来源，但与最先进逻辑节点的协同方式取决于客户和生态。

## AI/HPC 为什么改变产业链

AI/HPC package 常包含高功耗 logic die、多颗 HBM stack、大尺寸 interposer/RDL、复杂 substrate、强 PDN、严格热路径和多阶段测试。这让产业链从“封装外包”变成“系统级共同设计”。

```text
HBM bandwidth
  -> 2.5D/3D platform
  -> substrate/material/equipment capacity
  -> test/reliability feedback
```

## 产业链风险点

| 风险点 | 影响 |
| --- | --- |
| HBM 供给 | 决定高端 AI package 的 memory 配套 |
| CoWoS-like 产能 | 决定 logic + HBM 高密度集成能力 |
| ABF/substrate | 决定大尺寸 package 承载能力 |
| Hybrid bonding 设备 | 决定 3DIC 高密度连接窗口 |
| RDL/underfill/mold 材料 | 决定 warpage、cracking 和可靠性 |
| ATE/中测 | 决定高价值对象的良率经济性 |

## 一句话理解

先进封装产业链是一条从系统需求到逻辑、HBM、封装平台、基板材料设备、测试可靠性的闭环链条。

## 架构师启示

架构师要把产业链能力当作系统约束。若产品依赖多 HBM stack 和大尺寸 2.5D 平台，就不能只问设计是否可行，还要问 HBM、substrate、封装产能、材料窗口和测试能力是否同时可得。
