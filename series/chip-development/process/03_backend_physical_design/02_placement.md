# Placement

## 前置知识

- 建议先读 [Floorplanning](./01_floorplanning.md)。
- 建议理解 [Placement](../00_overview/05_glossary.md#placement)、[STA](../00_overview/05_glossary.md#sta)、[PPA](../00_overview/05_glossary.md#ppa)、[ECO](../00_overview/05_glossary.md#eco)。

## 核心概念

Placement 把综合后的标准单元放到具体物理位置。它不仅影响面积，还直接影响 wire length、拥塞、时序、功耗、clock tree 复杂度和后续 routing 成功率。现代 placement 是 timing-driven、congestion-driven、power-aware 的优化过程，不是把 cell 塞进空白区域。

Placement 阶段会第一次比较真实地暴露 RTL 结构的物理代价：宽 mux、长 fanout 控制信号、大仲裁器、跨 block 数据路径、集中式 scheduler、过宽 bus 都会变成线长、拥塞和 timing path。

## 关键活动顺序

1. 导入 floorplan、网表、SDC、UPF、library、RC tech、DEF。
2. 检查 design setup：unconstrained path、missing lib、illegal macro、power intent、dont_touch 约束。
3. 运行 initial placement，获得 cell density、wirelength、拥塞热图和 early timing。
4. 做 pre-CTS optimization：buffer insertion、cell sizing、logic restructuring、useful replication、tie cell、scan reorder。
5. 检查 congestion、timing、power、legalization 和 placement rule。
6. 与 floorplan 迭代：调整 blockage、region、macro channel、pin location、utilization。
7. 生成 placement checkpoint，供 CTS 使用。
8. 记录需要前端修复的问题：RTL 重构、pipeline、约束修正、层次调整。

## 工具名

常见工具包括 Cadence Innovus、Synopsys IC Compiler II/Fusion Compiler、Siemens Aprisa。STA 交互使用 PrimeTime 或 Tempus。功耗估算可结合 Cadence Joules/Voltus、Synopsys PrimePower、Ansys RedHawk-SC。等价检查涉及 Synopsys Formality、Cadence Conformal。

## 角色与典型时长

Placement owner 通常是 physical implementation engineer，STA engineer 和 RTL owner 必须参与关键路径分析。小 block placement 可以数天形成可用结果；复杂 block 或 SoC 级 placement closure 可能需要数周到数月反复迭代。先进节点下，placement 对 routing congestion、pin access、cell row 规则和 variation 更敏感，不能只看 pre-route timing。

## 关键决策点

- 是否提高 cell utilization：提高利用率省面积，但可能增加拥塞和线长。
- 是否打散逻辑层次：flatten 有利于优化，但损害可维护性、ECO 和层次化 signoff。
- 是否复制高 fanout logic：可改善时序和拥塞，但增加面积和功耗，也可能影响验证/LEC。
- 是否接受 early timing violation：少量可解释 violation 可以后续修；结构性长路径必须早反馈前端。
- 是否修改 RTL pipeline：后端优化有边界，跨越大物理距离的单周期路径通常不应硬扛。

## 先进节点与 28/16nm 差异

28nm/16nm 的 placement 仍可较多依赖后续 buffering 和 sizing 修复。7nm 及以下，标准单元高度更低、pin access 更难、metal stack 更紧张、variation 更强，placement 必须更早考虑 routing feasibility、cell orientation、coloring/multi-patterning、local congestion 和 power density。

先进节点常见情况是 pre-route timing 看似可修，但 detail route 后寄生和 DRC detour 使 timing 变差。因此 placement 阶段不能只看 [WNS/TNS](../00_overview/05_glossary.md#wnstns)，还要看拥塞、global route estimate、pin access 和关键路径物理分布。

## 常见坑

- 用 pre-route timing 过度乐观判断项目状态。
- 把所有 violation 都交给后端工具自动修，未区分物理可修与架构不可修。
- 高 fanout reset/enable/debug 信号没有早期处理。
- dont_touch 设置过多，阻止工具优化。
- 过早冻结 RTL，导致 placement 发现的问题无法回前端。
- 忽略 scan chain reorder，导致测试逻辑线长和拥塞异常。
- 只追求面积，导致后续 CTS/routing/STA 全部恶化。

## 上下游接口

Placement 上游接收 floorplan 和前端网表约束。下游交给 CTS 的结果包括合法化 placement、pre-CTS timing、congestion map、优化后的网表、scan reorder、placement DEF 和风险清单。

Placement 对前端的反馈非常关键。它会告诉 RTL/架构团队哪些信号 fanout 过大、哪些路径跨物理边界、哪些 mux/arbiter 不适合目标频率、哪些模块层次不利于优化。对 generator/agent 生成 RTL 的团队，placement feedback 应回灌到生成器约束，而不是只手工 patch 一版网表。

## 创业公司取舍

创业公司不要一开始就设定过高频率和过高 utilization。第一颗芯片的目标应是可闭合、可调试、可复现，而不是每平方毫米极限性能。若后端外包，内部要要求服务商定期提供 congestion map、top critical paths、area/power trend、QoR dashboard，而不是只等最终 GDS。

可以加速的是自动 QoR dashboard、脚本化 regression、物理反馈自动分类；不能加速的是架构级 placement 问题的决策，因为这需要前端、架构、后端共同判断。

## 典型场景

一个集中式 command scheduler 控制 128 个 compute lanes。RTL 仿真清楚，综合面积也能接受。Placement 后发现 scheduler 的 valid/ready/control 信号扇出巨大，穿越整个 array，buffer tree 占面积并造成拥塞，时序也持续失败。后端可复制部分控制逻辑，但根本修复是把 scheduler 分层，下放局部仲裁，或增加 pipeline。这个例子说明：软件式“集中控制”在硬件物理实现中经常变成长线和拥塞。

## 后续阅读

- [Clock Tree Synthesis](./03_clock_tree_synthesis.md)
- [Static Timing Analysis](./05_static_timing_analysis.md)
- [Routing](./04_routing.md)
- [先进节点特殊考虑](./08_advanced_node_considerations.md)

## 参考公开来源

- [Cadence Innovus Implementation System](https://www.cadence.com/en_US/home/resources/datasheets/innovus-implementation-system-ds.html)
- [Synopsys IC Compiler II](https://www.synopsys.com/implementation-and-signoff/physical-implementation/ic-compiler.html)
- [Synopsys PrimeTime](https://www.synopsys.com/implementation-and-signoff/signoff/primetime.html)
- [Cadence Tempus 相关产品页面](https://www.cadence.com/en_US/home/tools/digital-design-and-signoff.html)

## 内容可信度说明

- **公开信息（高可信）**：placement、timing-driven optimization、congestion-driven implementation、PPA closure 是公开 EDA flow 基本内容。
- **行业惯例（中可信）**：placement QoR 指标、critical path review、fanout replication、scan reorder 和 RTL feedback 是常见工程实践。
- **经验性观察（中低可信）**：集中式控制、宽 mux、长 bus 在 AI 芯片中常成为 placement/timing 问题。
- **不确定/需向资深工程师确认（低可信）**：具体工具选项、cell utilization 阈值、优化策略和 foundry-certified flow 细节。
