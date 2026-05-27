# 非理想性总览：Noise、Mismatch、Variation、Retention

上级：[04 Circuit And Macro](./README.md)
相关：[Analog CIM 深入](../03-compute-paradigms/analog-cim-deep-dive.md), [ReRAM-CIM 深入](../02-memory-technologies/reram-cim-deep-dive.md), [FAB: Process Nodes and PPA](../../../FAB/wiki/02-front-end-fabrication/process-nodes-and-ppa-tradeoffs.md)

## 这页在回答什么问题

为什么 CIM 的难点不是“电路会有误差”这么简单？因为误差会从 device、array、peripheral、calibration 和模型层逐级传播，最终决定 macro 指标能否变成可部署 accuracy。

## 误差分层

| 层级 | 典型误差 | 影响 |
| --- | --- | --- |
| device | ReRAM conductance variation、Flash threshold drift、PCM resistance drift、SRAM Vt mismatch | weight state 和读出分布 |
| array | IR drop、sneak path、line resistance、coupling、read disturb | 大阵列 MVM 偏差和行列不均匀 |
| circuit | SA offset、ADC quantization、DAC mismatch、reference noise、thermal noise | 判决、量化和有效位数 |
| temporal | retention、aging、temperature drift、write noise | 校准失效和长期稳定性 |
| system | mapping mismatch、tile reduction error、model sensitivity | 最终 accuracy 和重训练成本 |

## 三条 Paradigm 的误差形态

Analog CIM 把误差放进数值路径本身。ReRAM/Flash 的 conductance 或 threshold 不稳定会直接变成 MAC 误差；SRAM charge/current-domain 路线会受 PVT、leakage、bitline mismatch 和 sense margin 影响。

Digital CIM 的误差更接近传统数字设计：timing violation、read disturb、soft error、faulty bit、popcount 或 accumulator bug。它仍需要 BIST、ECC、redundancy 和 corner signoff，但误差更容易离散建模。

Mixed-signal CIM 最复杂，因为 analog 误差和 digital correction 同时存在。校准可以降低 bias，却会引入存储、时间、能耗和软件模型复杂度；如果误差分布随温度或时间漂移，离线校准会失效。

## Memory Technology 的差异

SRAM-CIM 的主要风险是 read disturb、half-select disturb、multi-row activation、PVT、sense margin、bitline coupling、timing closure 和外围面积。ReRAM-CIM 的风险从 device 开始：forming、write variation、conductance drift、IR drop 和 sneak path。Flash-CIM 要面对 threshold drift、program variation 和 retention。PCM 的 resistance drift 是核心难点；MRAM 若做 read/sense-path compute，则重点是 read current、read/write disturb、sense margin、TMR variation 和 sense offset。

DRAM/HBM/GDDR-PIM 也有 DRAM refresh、retention、timing 和 PHY 问题，但它们不属于本页 CIM macro 非理想性主线；PIM 更关心 memory command、bank conflict、thermal 和 host offload。

## 校准的代价

校准不是免费按钮。它需要 reference、测试向量、存储校准参数、运行时更新策略和模型侧适配。小阵列切分可降低 IR drop 和 variation，却增加 ADC、buffer、controller 和 interconnect 数量。差分编码可抑制 common-mode error，却把 cell 数翻倍或增加读出次数。

## 一句话理解

CIM 非理想性是从 device 到模型的误差传播问题；analog/mixed-signal 路线尤其需要把误差预算当成架构对象，而不是电路脚注。

## 研究启示

研究应报告误差源、误差分布、是否可校准、校准频率、温度/老化条件和模型 accuracy 影响。产业实现更需要硅后统计和量产测试方法；没有 corner、retention 和 calibration cost 的 accuracy 数字很难说明产品价值。
