# 掩模制作与晶圆制造

<span class="micro-legacy-anchor" id="mask-making-and-wafer-fab"></span>

## 前置知识

先看[流片交接](01_tapeout_process.md)发出了哪些数据。

## 核心概念

掩模版（reticle）承载光刻所用的图形。曝光视场是每次在晶圆上成像的区域。掩模组包含该制程与设计需要的掩模。光刻机将掩模图形投影到光刻胶。EUV 掩模以反射方式工作。工艺按层重复薄膜、曝光、刻蚀、注入或平坦化等步骤。 [ASML 光刻系统与掩模](https://www.asml.com/en/products/euv-lithography-systems) · [ASML 芯片制造](https://www.asml.com/en/technology/all-about-microchips/how-microchips-are-made)

## 关键活动顺序

1. 代工方检查提交版图、层与制程选择。
2. 工厂或掩模供应方按工艺做图形修正、制版数据准备和掩模检验。
3. 晶圆按工艺路线加工。线内量测和工艺监控支持过程控制。
4. 按项目执行晶圆验收／工艺参数测量，再进入对应的裸片筛选与封装交接。

工艺监控用测试结构观察制程状态。晶圆筛测在规定条件下对产品裸片分档。两类数据的对象与判据要在良率分析时对齐。 [FAB 晶圆工艺流程](../../FAB/wiki/02-front-end-fabrication/process-flow-overview.md) · [FAB 晶圆筛测](../../FAB/wiki/03-wafer-test-and-cp/cp-test-methodology.md)

## Mask 为什么贵

成本由需制作和验证的图形、掩模类型、改动层与制造路线共同决定。MPW 通过共享掩模降低单项目制版投入。实际可选节点、面积、批量和样品交付形式由该次服务规定。 [TSMC 掩模服务](https://www.tsmc.com/english/dedicatedFoundry/services/mask_services) · [TSMC CyberShuttle](https://www.tsmc.com/english/dedicatedFoundry/services/cyberShuttle)

## Wafer Fab 流程量级

项目排期至少分别估计提交到掩模放行、晶圆在制、出厂检查、封装及测试。区分物理工艺时间与排队、返工、样片转运及合约交期。统计时注明起点和终点。 [芯片项目成本结构](../00_overview/03_cost_structure.md)

<span class="micro-legacy-anchor" id="典型设备和工具"></span><span class="micro-legacy-anchor" id="角色与典型时长"></span><span class="micro-legacy-anchor" id="典型场景"></span>

## 上下游接口

设计公司的代工接口负责候选、样品数、批次标识、交付状态及异常追踪。制造与测试团队使用晶圆或裸片的批次、坐标、筛测条件和分档记录连接后续对象。详细工艺见 [FAB 晶圆前道](../../FAB/wiki/02-front-end-fabrication/README.md)。

## 后续阅读

- [晶圆筛测与 KGD](../../FAB/wiki/03-wafer-test-and-cp/README.md)
- [封装如何进入芯片项目](03_packaging.md)
- [MPW 多项目晶圆策略](../06_cross_cutting_topics/04_mpw_shuttle_strategy.md)

<span class="micro-legacy-anchor" id="关键决策点"></span><span class="micro-legacy-anchor" id="常见坑"></span><span class="micro-legacy-anchor" id="创业公司取舍"></span><span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** 光刻、掩模服务和共享制版的机制见 ASML 与 TSMC 资料。
- **行业做法。** 参数测量、筛测和样件交接按项目采用。
- **待项目核实。** 工序排期、在制状态、掩模范围、批量和接收条件。
