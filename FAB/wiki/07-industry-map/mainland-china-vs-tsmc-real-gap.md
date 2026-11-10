# 大陆 vs 台积电:在 AI 封装上的真实差距

上级:[产业地图](README.md)
相关:[大陆先进封装瓶颈](mainland-china-bottlenecks.md), [Foundry 版图](foundry-landscape-tsmc-intel-samsung.md), [从架构需求反推工艺与封装选型](../06-cross-cutting-engineering/from-architecture-to-process-selection.md)

## 这页在回答什么问题

大陆先进封装平台与台积电体系在 AI/HPC 封装上的差距到底是什么，为什么不能只用“有没有 2.5D/3D 能力”来判断。

## 建立可比对象

地区生态与一家 foundry 范围不同，不能直接对两者排名。应选择某厂、某路线和目标产品，固定 HBM 代际、封装面积、接口、批量与时期，再比较同口径证据。

| 项目 | 必须核验 | 缺少证据时 |
| --- | --- | --- |
| 平台与结构 | 具体 interposer、RDL 或 bridge 配置与设计规则 | 标为未披露，不推断不存在 |
| 材料和供电/热 | 指定结构、材料、热边界及 SI/PI 签核 | 列为待测，不能由平台名给数值 |
| 测试和资格 | 测试覆盖、应力、样本量与客户认证阶段 | 区分研发样片、工程试产和资格验证 |
| 持续交付 | 同期间合格率分母、批量、交期和产品范围 | 不给出生产差距的数量结论 |

[TSMC 2025 年报](https://investor.tsmc.com/static/annualReports/2025/english/pdf/2025_tsmc_ar_e_ch5.pdf)描述其 CoWoS 平台；这是一家公司的披露，不能单独证明其他供应商的能力。

## 为什么样品能力不等于量产能力

先进封装做出样品和稳定交付 AI/HPC package 是两件事。量产要求长期良率、热机械可靠性、测试覆盖、返修/失效分析、substrate 供给和产能节奏都稳定。

```text
demo package
  -> engineering sample
  -> customer qualification
  -> stable high-volume manufacturing
```

不同供应商在各阶段的证据可能不同；缺少同口径资料时不能判断差距大小。

## 可核验的建设方向

对具体项目，可评估以下建设方向，并以产品规格、客户资格和交付记录检验：

| 路径 | 目标 |
| --- | --- |
| 强化高端 substrate | 支撑大尺寸 AI package |
| 补材料和设备窗口 | 降低 warpage、cracking、bonding defect |
| 做深 Fan-out/RDL/bridge | 先在局部高密度和中高端 chiplet 场景积累 |
| 建立中测和可靠性数据 | 改善有效良率和客户信任 |
| 绑定真实系统需求 | 用客户产品反馈推动平台成熟 |

## 一句话理解

只有选定同口径的厂商、产品、时间与证据，才能判断各个封装环节的差异。

## 架构师启示

架构师如果面向大陆平台设计产品，需要把封装能力和供应链边界前置到架构定义中。可行路线可能不是直接复刻 CoWoS-S，而是围绕可获得 substrate、RDL、bridge、HBM 和测试能力做系统折中。
