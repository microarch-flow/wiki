# 布局规划怎样决定宏、引脚与供电

<span class="micro-legacy-anchor" id="floorplanning"></span><span class="micro-legacy-anchor" id="前置知识"></span>

## 核心概念

布局规划先安排尺寸大、位置受约束的对象，例如 SRAM 宏、模拟块、I/O 和凸点。标准单元随后填入可用区域。布局规划的输出包括可用面积、宏及端口位置、放置与布线限制、电源网初案。 [OpenROAD 布局规划](https://openroad.readthedocs.io/en/latest/main/openroad/ifp/README.html)

## 关键活动顺序

1. 根据网表、宏尺寸、封装接口和面积预算确定 die 与 core 边界。
2. 按端口方向、逻辑连接和电源需求摆放宏。给布线、缓冲器和电源连接预留空间。
3. 试放置和全局布线，检查拥塞、跨宏路径与电源网供给。
4. 调整宏方向、通道、端口或面积。结构性瓶颈反馈给微架构。

<span class="micro-legacy-anchor" id="先进节点与-2816nm-差异"></span><span class="micro-legacy-anchor" id="常见坑"></span><span class="micro-legacy-anchor" id="创业公司取舍"></span>

## 关键决策点

平均利用率不能解释局部拥塞。例如，两组 SRAM 将大量引脚对准同一窄通道，标准单元虽然有足够面积，局部金属和过孔资源可能不足。调转宏方向、扩大通道或改变数据路径都可能缓解问题，同时影响线长、面积和电源网。 [OpenROAD 全局布线](https://openroad.readthedocs.io/en/latest/main/openroad/grt/README.html)

<span class="micro-legacy-anchor" id="工具名"></span><span class="micro-legacy-anchor" id="角色与典型时长"></span><span class="micro-legacy-anchor" id="成本视角"></span>

## 上下游接口

上游交付初版网表、宏视图、时序边界与封装约束。实现团队输出布局约束、试放结果和未解决的风险。封装或 IP 端口变化时，需要重新检查宏、端口与供电的契约。

## 典型场景

**教学假设。** SRAM＋DMA 模块的写请求、应答和时钟连接集中在宏一侧。试布线报告提示宏外溢出。分别移动宏、调整引脚位置或修改流水线，比较相同估算条件下的拥塞和路径预算。将选择依据交给 RTL、时序和封装团队。

## 后续阅读

- [放置](02_placement.md)
- [封装如何进入芯片项目](../04_tapeout_and_post_silicon/03_packaging.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** 布局规划和全局布线的输入、输出可以用 OpenROAD 项目文档核对。
- **教学假设。** SRAM 放置场景用于解释局部拥塞。
- **待项目核实。** 目标工艺资源、宏电源方式、最小通道及实际布局方案。
