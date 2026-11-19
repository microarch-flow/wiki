# 布线与寄生提取怎样影响签核

<span class="micro-legacy-anchor" id="routing"></span><span class="micro-legacy-anchor" id="前置知识"></span>

## 核心概念

布线把网表中的连接落实到金属线和过孔。全局布线给容量规划和路由引导。详细布线选择具体形状、层与过孔，并处理局部设计规则。提取工具根据版图与工艺模型计算线阻、对地电容及耦合。 [OpenROAD 全局布线](https://openroad.readthedocs.io/en/latest/main/openroad/grt/README.html) · [详细布线](https://openroad.readthedocs.io/en/latest/main/openroad/drt/README.html) · [OpenRCX](https://openroad.readthedocs.io/en/latest/main/openroad/rcx/README.html)

## 关键活动顺序

1. 接收放置、时钟树、供电网、阻挡和可用金属资源。
2. 先评估容量和溢出，再完成可落地的连线。
3. 修复接入、间距、天线效应等相关问题。按工艺要求加填充。
4. 按实际版图提取寄生，复核时序、信号完整性和物理规则。修改线形、过孔或填充时更新受影响的报告。

## SI/Crosstalk 检查

相邻导线耦合会改变信号延迟或造成噪声。影响与几何位置、耦合量、驱动和同时切换窗口有关。减小耦合可用增加间距、换层或屏蔽，代价是额外布线面积、线长或负载。封装链路采用相应参考面和模型。 [封装信号完整性](../../FAB/wiki/06-cross-cutting-engineering/signal-integrity-in-package.md)

<span class="micro-legacy-anchor" id="先进节点与-2816nm-差异"></span><span class="micro-legacy-anchor" id="常见坑"></span><span class="micro-legacy-anchor" id="创业公司取舍"></span>

## 关键决策点

试布线可暴露走线资源不足。若所有方案都绕过拥塞区而破坏路径预算，先重审宏、引脚、资源切分和流水边界。越靠近流片，越需要以同一版图复核受影响的签核项。 [片内互连与 BEOL](../../FAB/wiki/02-front-end-fabrication/interconnect-stack-beol.md)

<span class="micro-legacy-anchor" id="工具名"></span><span class="micro-legacy-anchor" id="角色与典型时长"></span>

## 上下游接口

交付包含物理实现检查点、版图和提取结果。典型文件包括物理数据库或 DEF、版图 OASIS／GDSII、以及交给 STA 的 SPEF。工程工具的本地检查与流片签核采用的规则、版图输入和配置需要对齐。

## 典型场景

**教学假设。** 两条原来相隔较远的总线被绕到同层并行。提取看到耦合增加。时序团队按切换窗口检查受害路径，设计团队比较换层与加间距，并检查修改后是否引入新的拥塞和规则违例。

## 后续阅读

- [静态时序分析](05_static_timing_analysis.md)
- [DRC 与 LVS 签核](07_drc_lvs_signoff.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** 布线和寄生提取的阶段见 OpenROAD 文档。
- **教学假设。** 总线耦合场景用于解释物理反馈。
- **待项目核实。** 可用金属层、寄生模型、SI 检查边界和规则集。
