# 摩尔定律放缓如何把封装推到前台

上级:[后道封装](./README.md)
相关:[为什么工艺红利在让位于封装红利](../01-overview/why-process-and-packaging-matter-now.md), [工艺节点演化与 PPA 取舍](../02-front-end-fabrication/process-nodes-and-ppa-tradeoffs.md), [HBM 如何把产业逼向 2.5D 和 3D](./hbm-as-case-study/why-hbm-forces-2.5d-3d.md)

## 这页在回答什么问题

为什么先进封装在 AI/HPC、chiplet 和 HBM 时代突然变成主角。原因不是单一“摩尔定律结束”，而是工艺 scaling、memory bandwidth、die size、功耗密度和良率经济学同时把系统推向 package 级重组。

## 工艺 scaling 的收益变得不均匀

先进节点仍然提供更高 logic density 和更好能效，但收益不再均匀作用到整颗 SoC。Logic 可以受益，SRAM scaling 变慢，analog/I/O/PHY 迁移收益有限，global wire 和 BEOL 拥塞不按 logic density 理想缩放。一个 SoC 里不能完美缩放的部分越多，单纯换节点的系统收益越受限制。

这让架构师开始拆分目标函数：哪些功能必须用最先进 logic 节点，哪些功能可以留在成熟节点，哪些带宽和容量问题需要通过封装而不是 transistor scaling 解决。

## Memory wall 把封装推到前面

AI/HPC 的算力增长需要外存带宽同步增长。继续依赖较远的板级内存连接，会面对 I/O 数量、单 pin 速率、功耗、SI/PI 和板级面积压力。HBM 用超宽近距接口解决带宽密度和每 bit 能耗问题，但它要求 memory stack 靠近 logic die，并使用比传统 substrate 更高密度的封装互连。

这就是 HBM 把先进封装变成必答题的原因。RAM wiki 的 [HBM 协议](../../RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io.md) 解释了它为什么用宽接口而不是单纯拉高频率；本 wiki 后续会解释这个宽接口如何落到 2.5D/3D package。

## 大 die 的经济性逼出 chiplet

随着单 die 面积增大，reticle、缺陷密度、良率和 mask 成本会共同推高风险。Chiplet 把一个大系统拆成多个 die，有机会改善单 die 良率、复用 IP、混合节点和扩展 SKU。

但 chiplet 不是免费午餐。它需要封装内 D2D 互连、KGD、协议/PHY、package routing、热管理和更复杂测试。NoC wiki 的 [chiplet 与 die-to-die 互连](../../NOC/wiki/06-ai-noc-specifics/chiplet-and-die-to-die-interconnect.md) 从通信层解释了跨 die 代价；本章从封装层解释这些代价为什么存在。

## 功耗密度让 package 成为热和供电系统

AI/HPC die 的功耗密度上升后，package 不再只是信号引出层。电流要从 board、substrate、interposer/RDL、bump、BEOL 进入 die；热要从 die、TIM、lid、散热器以及部分底部路径离开系统。HBM、chiplet 和 interposer 会改变热源位置和热阻网络。

若 package PDN 或热路径不闭合，架构里增加 compute 单元只会带来 throttling、IR drop、可靠性风险或无法达到目标频率。先进封装因此成为 PPA 的组成部分，而不是制造收尾。

## 测试和良率决定能否量产

越复杂的 package，越需要把测试节点前移。CP、KGD、中间模块测试和 final test 共同决定有效良率。封装把多个 die 组合起来后，单个对象的残余 defect 会被组合放大；失效越晚暴露，报废成本越高。

这解释了为什么先进封装平台不是“能做样品”就够。量产能力需要互连、热、应力、供电、测试和良率学习同时稳定。

## 常见误解

常见误解是“先进封装火起来只是因为工艺不行了”。更准确的说法是：工艺仍然重要，但系统瓶颈从单个 transistor 扩展到 die 间带宽、memory adjacency、功耗密度和有效良率，封装成为新的优化维度。

另一个误解是“封装红利主要是省成本”。在高端 AI/HPC 中，先进封装往往先是性能和可行性需求，成本是后续优化目标。没有足够封装密度和热/供电能力，系统甚至无法达到目标规格。

## 一句话理解

先进封装走到前台，是因为系统瓶颈从单 die PPA 扩展到 memory bandwidth、die size、power delivery、thermal 和组合良率。

## 架构师启示

如果我在架构探索中发现性能受外存带宽限制，继续缩节点或增加 compute 可能不是最优解。更关键的问题可能是 HBM stack 数量、2.5D 路线、D2D 互连密度、package PDN 和热路径能否支撑目标吞吐。

一个具体决策例子：当单 die 方案受 reticle/良率限制时，chiplet 看起来有吸引力；但如果应用需要强 all-to-all 低延迟通信，D2D 和 package fabric 可能吞掉收益。架构师必须把封装互连放进 topology 和 cost model，而不是只比较 die 面积。
