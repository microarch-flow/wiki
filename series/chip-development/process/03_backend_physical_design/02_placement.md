# 标准单元放置怎样平衡时序与拥塞

<span class="micro-legacy-anchor" id="placement"></span><span class="micro-legacy-anchor" id="前置知识"></span>

## 核心概念

放置根据布局规划为标准单元确定位置。全局放置尝试降低线长、密度代价和关键路径开销。详细放置将单元移动到合规站点，处理重叠及局部布局规则。 [OpenROAD 全局放置](https://openroad.readthedocs.io/en/latest/main/openroad/gpl/README.html) · [详细放置](https://openroad.readthedocs.io/en/latest/main/openroad/dpl/README.html)

## 关键活动顺序

1. 接收网表、宏和 I/O 位置、放置限制、可用站点及约束。
2. 迭代全局放置。检查连线估长、路径裕量和局部密度。
3. 详细放置并核对合法性，必要时调整单元大小、缓冲器或区域约束。
4. 比较放置后检查点和报告。把不能靠局部修改解决的问题反馈给布局规划或 RTL。

<span class="micro-legacy-anchor" id="先进节点与-2816nm-差异"></span><span class="micro-legacy-anchor" id="常见坑"></span><span class="micro-legacy-anchor" id="创业公司取舍"></span>

## 关键决策点

如果将所有关键单元挤进同一区域，几何距离可能下降，局部布线压力也可能上升。先统计最差区域的线资源需求和供给，再决定加密、疏散或调整宏布局。放置期寄生多由位置或全局路由估算，布线后使用实际线和过孔重新提取。 [OpenROAD 寄生估算](https://openroad.readthedocs.io/en/latest/main/openroad/est/README.html)

<span class="micro-legacy-anchor" id="工具名"></span><span class="micro-legacy-anchor" id="角色与典型时长"></span>

## 上下游接口

输出合法放置的检查点、拥塞和时序估计、缓冲器等变更记录。CTS 接收时钟端点与放置结果。若链重排或拥塞修复改变网表或位置，需要更新后续检查输入。

## 典型场景

**教学假设。** 同一条路径在放置估算中很短。全局布线发现线路必须绕过宏，估计延迟增加。团队可以换宏方向、移动相关单元或改流水边界。比较时使用同一网表版本、同一角落及相同估算阶段。

## 后续阅读

- [时钟树综合](03_clock_tree_synthesis.md)
- [布线与寄生提取](04_routing.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** OpenROAD 分别提供全局放置和详细放置。
- **教学假设。** 绕宏示例用来说明估算会随物理阶段改变。
- **待项目核实。** 目标工艺的布局约束、资源余量及报告中的 QoR 变化。
