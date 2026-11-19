# 时钟树综合怎样影响 setup 和 hold

<span class="micro-legacy-anchor" id="clock-tree-synthesis"></span><span class="micro-legacy-anchor" id="前置知识"></span>

## 核心概念

时钟树综合（CTS）将时钟分发到寄存器、存储宏等接收点。工具按接收点、时钟定义和库构造可实现的分发网络，并检查延迟、偏斜、转换时间、负载与资源占用。插入延迟描述沿时钟路径花费的时间。偏斜描述相关接收点的到达时间差。 [OpenROAD CTS](https://openroad.readthedocs.io/en/latest/main/openroad/cts/README.html) · [AMD 时序报告字段](https://docs.amd.com/r/en-US/ug906-vivado-design-analysis/Table-Columns)

## 关键活动顺序

1. 审查主时钟、生成时钟、门控和测试时钟的定义及端点。
2. 结合已放置网表、库与布线条件构造时钟分发网络。
3. 以传播时钟重新检查路径及门控，对受影响的 setup、hold 和转换时间做修复。
4. 检查时钟线资源、功耗和供电，并在后续布线和提取后回归。 [OpenROAD 时序修复](https://openroad.readthedocs.io/en/latest/main/openroad/rsz/README.html)

<span class="micro-legacy-anchor" id="先进节点与-2816nm-差异"></span><span class="micro-legacy-anchor" id="常见坑"></span><span class="micro-legacy-anchor" id="创业公司取舍"></span>

## 关键决策点

设接收时钟相对发送时钟晚到。对于同一时钟域的典型单周期路径，在其他条件固定时，这给下一拍 setup 更多时间，同时推迟同拍 hold 要求。实际分析要使用该路径的边沿关系、角落、时钟路径变化和不确定度。 [setup 关系](https://docs.amd.com/r/2026.1-English/ug906-vivado-design-analysis/Setup/Recovery-Relationship?contentId=vOSoXJu3asbkH1uyuWp0Lg) · [hold 关系](https://docs.amd.com/r/2026.1-English/ug906-vivado-design-analysis/Hold/Removal-Relationship?contentId=dZBm6BfVStfa~EyRyUpHjA)

## 典型场景

**教学假设。** 见[静态时序例题](05_static_timing_analysis.md#典型场景)。接收端多 30 ps 的到达差，能将 setup 由 −20 ps 改为 +10 ps，却让原本为 0 ps 的 hold 变为 −30 ps。复核另一端点及各模式后，再决定改变时钟树或修数据最短路径。

<span class="micro-legacy-anchor" id="工具名"></span><span class="micro-legacy-anchor" id="角色与典型时长"></span>

## 上下游接口

CTS 接收放置网表、时钟约束、库和测试模式定义。交付时钟网表、树的物理实现、到达与偏斜数据及需复查的时序风险。门控或测试时钟无法实现时，回到 RTL、DFT 或时钟架构核对设计。

## 后续阅读

- [静态时序分析](05_static_timing_analysis.md)
- [布线与寄生提取](04_routing.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** CTS、时钟延迟及 setup／hold 关系见工具文档。
- **教学假设。** 30 ps 偏斜算例保持其他变量固定。
- **待项目核实。** 各模式的时钟关系、库、电气限值和实际签核裕量。
