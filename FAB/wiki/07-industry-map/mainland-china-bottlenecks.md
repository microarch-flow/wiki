# 大陆先进封装:材料、基板、设备分别卡在哪

上级:[产业地图](README.md)
相关:[大陆 vs 台积电](mainland-china-vs-tsmc-real-gap.md), [材料供应链](materials-supply-chain.md), [设备厂商版图](equipment-vendors.md)

## 这页在回答什么问题

大陆先进封装追赶的瓶颈分别落在材料、基板、设备、HBM、客户导入和系统协同的哪些位置，为什么问题不是单个封测厂能否做出样品。

## 先看系统链条

AI/HPC 先进封装需要同时具备：先进逻辑 die、HBM stack、高密度 2.5D/3D 平台、高端 substrate、RDL/underfill/mold/bonding 材料、关键设备、PI/SI/thermal/mechanical co-design、测试可靠性和客户量产导入。

```text
logic + HBM + advanced package + substrate + materials + equipment + test
```

大陆的短板更像系统链条不均衡，而不是某一个环节完全为空。

## 材料瓶颈

材料瓶颈集中在高端 substrate dielectric、RDL dielectric、underfill/mold、temporary bonding adhesive、hybrid bonding 表面体系、TIM 和可靠性材料。高端材料难点在一致性、工艺窗口、可靠性数据和客户认证周期。

| 材料方向 | 影响 |
| --- | --- |
| ABF/build-up dielectric | 高端 substrate 层数、细线和稳定性 |
| RDL dielectric | fine line/space、warpage、cracking |
| Underfill/mold | bump fatigue、delamination、warpage |
| Bonding materials/surface | hybrid bonding 界面质量 |
| TIM | 高功耗 package 热路径 |

## 基板瓶颈

高端 AI/HPC package 需要大尺寸、高层数、高 I/O、高电流、低 warpage 的 substrate。大陆 substrate 能力在中低端和部分高端方向持续推进，但 AI/HPC 顶级封装需要的 ABF substrate、交付一致性和大尺寸良率仍是关键门槛。

## 设备瓶颈

先进封装设备包括 RDL 图形化和电镀、TSV、thin wafer handling、die bonder、TCB、hybrid bonding、inspection/metrology、ATE 和可靠性设备。瓶颈不只在“有没有设备”，还在设备精度、稳定性、吞吐、recipe 生态和与材料的联合调试。

## HBM 与客户导入瓶颈

高端 AI package 需要 HBM 配套。若 HBM stack 供给、测试、接口协同和客户导入不完整，即使封装平台具备部分能力，也难进入最高价值产品。客户导入带来的量产数据反馈同样重要，它会持续改善良率、热机械模型和测试策略。

## 一句话理解

大陆先进封装的瓶颈不是单点“会不会封装”，而是材料、基板、设备、HBM、客户导入和系统协同能否共同支撑 AI/HPC 级量产闭环。

## 架构师启示

若架构要落在大陆供应链，必须更早评估可获得的 HBM、substrate、RDL 密度、材料认证、设备窗口和测试能力。架构目标需要和可量产供应链一起收敛，而不是等后期再替换平台。
