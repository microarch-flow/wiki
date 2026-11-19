# 功耗、压降与电迁移分别检查什么

<span class="micro-legacy-anchor" id="power-analysis"></span>

## 前置知识

先了解[低功耗设计](../02_frontend_design_and_verification/07_low_power_design.md)和[封装供电完整性](../../FAB/wiki/06-cross-cutting-engineering/power-delivery-pi-pdn-decap.md)。

## 核心概念

功耗估算说明何处消耗多少电能。压降分析用电流与供电网络估计实际节点电压。电迁移（EM）评估金属和过孔在指定电流、温度及时间条件下的可靠性。三项分析共用部分输入，各自有不同的输出和通过判据。 [OpenROAD 静态 IR 分析](https://openroad.readthedocs.io/en/latest/main/openroad/psm/README.html)

## 关键活动顺序

1. 定义功能负载、空闲、启动、低功耗切换和测试模式。给出活动来源及观测时间窗口。
2. 使用网表、库及活动估算功耗，注明输入是向量、测量还是无向量估计。按所用库的计量边界组合开关、内部与漏电功耗。
3. 根据芯片电源网、凸点和封装供电模型计算稳态压降。用适当的瞬态模型分析并发切换和供电响应。
4. 按规则检查线与过孔的电流和温度条件。需要时把电压和温度返回时序分析。
5. 迭代电源网、布置、去耦、节流或时钟控制。复查修改后的负载、延迟和产线测试。

<span class="micro-legacy-anchor" id="先进节点与-2816nm-差异"></span><span class="micro-legacy-anchor" id="常见坑"></span><span class="micro-legacy-anchor" id="创业公司取舍"></span>

## 关键决策点

平均功耗合格只给出对应窗口的均值。相同均值下，同步启动很多单元可能造成更大的瞬时电流。要对齐负载、电压、电流测量参考点、供电源和散热边界。补充静态分析、瞬态分析和寿命限值所需的不同条件。 [封装供电路径](../../FAB/wiki/06-cross-cutting-engineering/power-delivery-pi-pdn-decap.md) · [封装热路径](../../FAB/wiki/06-cross-cutting-engineering/thermal-path-and-management.md)

## 典型场景

**教学假设。** 一条供电支路的源端电压为 0.80 V，等效串联电阻 10 mΩ，稳态电流 2 A。仅计算该支路，电阻压降为 20 mV，负载端电压为 0.78 V。此例忽略回流路径、动态电感、电容和其他支路的耦合。

| 报告 | 主要输入 | 怎样读结果 |
| --- | --- | --- |
| 功耗 | 库、活动、工作电压与时间窗 | 查看平均或瞬时功耗及各模块贡献 |
| 静态 IR | 电流、金属和供电边界 | 查最坏节点、局部电压和关联路径 |
| 瞬态压降 | 活动波形、PDN 与封装模型 | 查最低电压、持续时间和测试场景 |
| EM | 线／过孔几何、电流统计、温度与目标寿命 | 用对应工艺限值评估，记录检查规则和场景 |

若只是把同时启动改成分批，先确认峰值电压及长窗口功耗，再测吞吐、延迟和产品限制。任何新的节流策略要有真实控制方式。 [FAB 热路径与控制策略](../../FAB/wiki/06-cross-cutting-engineering/thermal-path-and-management.md)

<span class="micro-legacy-anchor" id="工具名"></span><span class="micro-legacy-anchor" id="角色与典型时长"></span>

## 上下游接口

上游由产品和软件组提供负载，设计组提供网表与电源意图，封装及板级组提供边界模型。下游收到按版本绑定的功耗、电压和电流结果，以及需要调整的设计或工作条件。

## 后续阅读

- [静态时序分析](05_static_timing_analysis.md)
- [封装如何进入芯片项目](../04_tapeout_and_post_silicon/03_packaging.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** 静态 IR 模块与报告可参考 OpenROAD。瞬态及寿命检查需要适用的物理模型和规则。
- **教学假设。** 0.78 V 是单电阻模型的结果。
- **待项目核实。** 活动数据、压降限值、封装边界与目标工艺的 EM 判据。
