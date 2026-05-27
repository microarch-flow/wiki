# 高频问题:最容易混淆的概念

上级:[参考资料](README.md)
相关:[术语表](glossary.md), [关键指标速查表](key-metrics-table.md), [工艺与封装选型决策树](decision-tree-process-and-package.md)

## 这页在回答什么问题

先进封装里哪些概念最容易混淆，应该如何快速纠正。本页用于复习、自测和概念澄清。

## 高频问题

| 问题 | 简答 | 继续阅读 |
| --- | --- | --- |
| TSV 等于 3DIC 吗 | 不等于。TSV 是垂直互连能力，3DIC 是垂直堆叠结构 | [TSV](../04-back-end-packaging/3d-routes/tsv-through-silicon-via.md) |
| HBM 等于 3DIC 吗 | HBM 内部是 3D memory stack，但 logic + HBM package 多为 2.5D 集成 | [HBM 案例](../04-back-end-packaging/hbm-as-case-study/README.md) |
| CoWoS 等于 silicon interposer 吗 | 不等于。CoWoS-S 是硅中介层，R/L 分别引入 RDL 和局部硅互连 | [CoWoS-S/R/L](../04-back-end-packaging/2.5d-routes/cowos-s-r-l-comparison.md) |
| Fan-out 比 Si interposer 更先进吗 | 不是高低关系，是目标函数不同 | [Fan-out RDL](../04-back-end-packaging/2.5d-routes/fan-out-rdl-overview.md) |
| Embedded bridge 是缩小版 interposer 吗 | 不是。它是局部硅互连 + 全局低成本平台 | [Embedded Bridge](../04-back-end-packaging/2.5d-routes/embedded-bridge-emib-and-cowos-l.md) |
| 2.5D 比 3D 落后吗 | 不是代际高低，2.5D 对 logic + HBM 仍是强路线 | [2.5D 路线](../04-back-end-packaging/2.5d-routes/README.md) |
| Hybrid bonding 会替代 micro-bump 吗 | 它在极高密度场景更有价值，但 micro-bump 仍有成熟窗口 | [Micro-bump vs Hybrid Bonding](../04-back-end-packaging/3d-routes/micro-bump-vs-hybrid-bonding.md) |
| 先进封装只是连线吗 | 不是，还包括 PI、SI、热、应力、测试、良率和产业链 | [跨工艺共性问题](../06-cross-cutting-engineering/README.md) |
| PI 是 die 内部问题吗 | 不是。先进封装中 PDN 跨 board、substrate、interposer/RDL、bump 和 die | [PI/PDN/Decap](../06-cross-cutting-engineering/power-delivery-pi-pdn-decap.md) |
| 热能靠最后加散热器解决吗 | 不能。热路径由 die placement、stack、TIM/lid 和 package 结构决定 | [热路径](../06-cross-cutting-engineering/thermal-path-and-management.md) |
| Warpage 只是外观问题吗 | 不是。它影响 bonding、bump、测试接触和板级组装 | [CTE/Warpage](../06-cross-cutting-engineering/stress-warpage-cte.md) |
| 有平台名就等于量产能力相同吗 | 不等于。还要看客户导入、良率、材料设备、测试和供应链闭环 | [产业地图](../07-industry-map/README.md) |
| OSAT 会被 foundry packaging 替代吗 | 不会简单替代。两者在协同方式、客户来源和平台能力上不同 | [OSAT 版图](../07-industry-map/osat-landscape-ase-amkor-jcet-tongfu.md) |
| 3DIC 最难的是 bonding 吗 | Bonding 关键，但热、应力、薄 die、测试和良率共同决定难度 | [3DIC 热应力](../04-back-end-packaging/3d-routes/3dic-thermal-and-stress-challenges.md) |
| 学路线名够了吗 | 不够。还要理解失效模式、测试、良率和产业链 | [失效模式总览](../06-cross-cutting-engineering/failure-modes-catalog.md) |

## 最容易混的三组词

| 词组 | 正确区分 |
| --- | --- |
| W2W / D2W vs F2F / F2B | 前者是制造组织，后者是 die 朝向 |
| RDL vs substrate | RDL 是封装级重布线网络，substrate 是最终连接 board 的承载平台 |
| CP/KGD vs final test | 前者在封装前控制物料质量，后者验证封装后成品 |

## 一句话理解

先进封装的高频误区大多来自把能力、结构、工艺、平台名和量产能力混在一起。

## 架构师启示

架构师遇到概念争议时，应先把词拆回对象层级：这是材料、工艺、结构、平台、测试节点，还是产业链能力。层级拆清楚，路线判断才会清楚。
