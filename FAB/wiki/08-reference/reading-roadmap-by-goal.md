# 按目标的学习路径

上级:[参考资料](README.md)
相关:[学习路线](../01-overview/learning-roadmap.md), [高频问题](high-frequency-questions.md), [工艺与封装选型决策树](decision-tree-process-and-package.md)

## 这页在回答什么问题

如果学习目标不同，应该按什么顺序阅读这套 wiki。本页给出最短路径。

## 建立完整框架

1. [问题定义](../01-overview/problem-statement.md)
2. [从晶圆到产品](../01-overview/from-wafer-to-product.md)
3. [分类框架](../01-overview/taxonomy.md)
4. [前道与后道](../01-overview/front-end-vs-back-end.md)
5. [后道封装](../04-back-end-packaging/README.md)
6. [跨工艺共性问题](../06-cross-cutting-engineering/README.md)

读完这条路径，应能回答 wafer、die、package、front-end、back-end、2.5D、3DIC、test 和 reliability 的基本关系。

## 搞懂 AI/HPC + HBM 封装

1. [为什么先进封装变重要](../01-overview/why-process-and-packaging-matter-now.md)
2. [HBM 如何把产业逼向 2.5D 和 3D](../04-back-end-packaging/hbm-as-case-study/why-hbm-forces-2.5d-3d.md)
3. [HBM stack 是怎么制造出来的](../04-back-end-packaging/hbm-as-case-study/hbm-stack-manufacturing.md)
4. [AI GPU + HBM 封装对象关系](../04-back-end-packaging/hbm-as-case-study/ai-gpu-hbm-package-architecture.md)
5. [CoWoS-S/R/L](../04-back-end-packaging/2.5d-routes/cowos-s-r-l-comparison.md)
6. [PI/PDN/Decap](../06-cross-cutting-engineering/power-delivery-pi-pdn-decap.md)
7. [热路径](../06-cross-cutting-engineering/thermal-path-and-management.md)

## 搞懂 2.5D 路线

1. [2.5D 路线](../04-back-end-packaging/2.5d-routes/README.md)
2. [Si Interposer](../04-back-end-packaging/2.5d-routes/si-interposer-fundamentals.md)
3. [Fan-out RDL](../04-back-end-packaging/2.5d-routes/fan-out-rdl-overview.md)
4. [Chip-first vs Chip-last](../04-back-end-packaging/2.5d-routes/fan-out-chip-first-vs-chip-last.md)
5. [Embedded Bridge](../04-back-end-packaging/2.5d-routes/embedded-bridge-emib-and-cowos-l.md)
6. [2.5D trade-off](../04-back-end-packaging/2.5d-routes/2.5d-routes-tradeoff-map.md)

## 搞懂 3DIC

1. [3D 路线](../04-back-end-packaging/3d-routes/README.md)
2. [3DIC 基础](../04-back-end-packaging/3d-routes/3dic-fundamentals.md)
3. [TSV](../04-back-end-packaging/3d-routes/tsv-through-silicon-via.md)
4. [Micro-bump vs Hybrid Bonding](../04-back-end-packaging/3d-routes/micro-bump-vs-hybrid-bonding.md)
5. [W2W vs D2W](../04-back-end-packaging/3d-routes/w2w-vs-d2w.md)
6. [SoIC F2F/F2B/CoW/WoW](../04-back-end-packaging/3d-routes/soic-face-to-face-to-back.md)
7. [3DIC 热与应力](../04-back-end-packaging/3d-routes/3dic-thermal-and-stress-challenges.md)

## 做工程判断

1. [从架构需求反推工艺与封装选型](../06-cross-cutting-engineering/from-architecture-to-process-selection.md)
2. [关键指标速查表](key-metrics-table.md)
3. [良率经济学](../06-cross-cutting-engineering/yield-economics-across-stages.md)
4. [失效模式总览](../06-cross-cutting-engineering/failure-modes-catalog.md)
5. [Final Test](../05-final-test-and-reliability/final-test-methodology.md)
6. [失效分析](../05-final-test-and-reliability/failure-analysis-flow.md)

## 看产业链

1. [产业地图](../07-industry-map/README.md)
2. [全球产业链全景图](../07-industry-map/industry-chain-overview.md)
3. [Foundry 版图](../07-industry-map/foundry-landscape-tsmc-intel-samsung.md)
4. [OSAT 版图](../07-industry-map/osat-landscape-ase-amkor-jcet-tongfu.md)
5. [材料供应链](../07-industry-map/materials-supply-chain.md)
6. [设备厂商版图](../07-industry-map/equipment-vendors.md)
7. [大陆先进封装瓶颈](../07-industry-map/mainland-china-bottlenecks.md)

## 一句话理解

按目标阅读比从头硬读更有效：框架、HBM、2.5D、3DIC、工程判断和产业链各有最短路径。

## 架构师启示

架构师应优先走“工程判断”路径，再按项目风险补读 HBM、2.5D、3DIC 或产业链。这样能更快把知识转成路线选择、风险识别和设计约束。
