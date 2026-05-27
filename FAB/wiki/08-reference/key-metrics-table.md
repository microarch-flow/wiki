# 关键指标速查表

上级:[参考资料](README.md)
相关:[2.5D 路线 trade-off](../04-back-end-packaging/2.5d-routes/2.5d-routes-tradeoff-map.md), [Micro-bump vs Hybrid Bonding](../04-back-end-packaging/3d-routes/micro-bump-vs-hybrid-bonding.md), [产业地图](../07-industry-map/README.md)

## 这页在回答什么问题

如何把不同封装路线、连接工艺和平台能力放到同一张表里比较。本页提供定性速查，不替代具体平台数据。

## 路线级指标

| 维度 | Si interposer | Fan-out/RDL | Embedded bridge | 3DIC |
| --- | --- | --- | --- | --- |
| 局部互连密度 | 很高 | 中高 | 局部很高 | 极高 |
| 全局尺寸扩展 | 中 | 高 | 高 | 低到中 |
| HBM 适配 | 强 | 中到强 | 局部强 | 取决于结构 |
| PI/PDN 支撑 | 强 | 中到强 | 中到强 | 强但复杂 |
| 热风险 | 高 | 中到高 | 中到高 | 极高 |
| Warpage 风险 | 高 | 高 | 中到高 | 高 |
| 测试复杂度 | 高 | 中到高 | 高 | 极高 |
| 成本压力 | 高 | 中 | 中到高 | 高 |

读表时要看目标函数：Si interposer 强在全局硅级密度，Fan-out/RDL 强在折中，bridge 强在局部高密度，3DIC 强在垂直短互连。

## 连接工艺指标

| 维度 | Micro-bump | Hybrid bonding |
| --- | --- | --- |
| 连接机制 | 凸点连接 | Cu/介质直接键合 |
| Pitch 潜力 | 高 | 更高 |
| 互连寄生 | 较高 | 更低 |
| 工艺窗口 | 较宽 | 更窄 |
| 平坦度要求 | 高 | 更高 |
| 主要风险 | bump fatigue、underfill、热循环 | 洁净度、对位、界面可靠性 |
| 适合场景 | 成熟高密度封装 | 极高密度 3DIC |

## CoWoS-S/R/L 速查

| 平台 | 全局平台 | 局部密度 | 尺寸扩展 | 主要代价 |
| --- | --- | --- | --- | --- |
| CoWoS-S | silicon interposer | 很强 | 受大硅平台约束 | 成本、warpage、良率 |
| CoWoS-R | RDL interposer | 中高 | 更强 | 极限密度低于 S |
| CoWoS-L | RDL + local silicon interconnect | 局部很强 | 强 | 混合平台协同复杂 |

## 产业链指标

| 维度 | 需要看什么 |
| --- | --- |
| Foundry 协同 | 先进逻辑、封装、PDK/DFT、客户导入是否协同 |
| HBM 协同 | HBM stack 供给、接口、测试和热设计是否配套 |
| Substrate | 大尺寸、高层数、高电流、warpage 控制 |
| Materials | RDL dielectric、underfill、mold、TIM、bonding surface |
| Equipment | RDL、TSV、thin die、hybrid bonding、inspection、ATE |
| Reliability | 中测、final test、stress test、FA 闭环 |

## 一句话理解

关键指标速查表用来比较目标函数：密度、尺寸、成本、热、PI、SI、良率、测试和产业链可得性。

## 架构师启示

架构师不要只用“先进”比较路线。应把目标带宽、power-per-bit、package 尺寸、HBM 数量、良率和测试约束放到同一张指标表里，选择最能闭合的路线。
