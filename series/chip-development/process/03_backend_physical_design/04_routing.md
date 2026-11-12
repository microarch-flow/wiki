# Routing

## 前置知识

- 建议先读 [Clock Tree Synthesis](./03_clock_tree_synthesis.md)。
- 建议理解 [Routing](../00_overview/05_glossary.md#routing)、[DRC](../00_overview/05_glossary.md#drc)、[STA](../00_overview/05_glossary.md#sta)、[GDSII](../00_overview/05_glossary.md#gdsii)。

## 核心概念

Routing 把 placement 和 CTS 后的所有电气连接映射到金属层和通孔。它分为 global routing、detail routing、post-route optimization 和 signoff cleanup。Routing 不是简单“连线”，它决定寄生电阻电容、串扰、DRC、[Antenna Effect](../00_overview/05_glossary.md#antenna-effect)、EM、timing 和最终可制造性。

先进节点下，routing 是后端风险最高的环节之一。因为金属层资源有限、设计规则复杂、pin access 困难、EUV/multi-patterning 约束多、via 电阻高，工具可能为了满足 DRC 绕远路，从而恶化 timing 和功耗。

## 关键活动顺序

1. 检查 post-CTS design：clock tree、placement legality、power grid、blockage、routing layer constraint。
2. Global route：估计 routing demand、拥塞、层分配和主要路径。
3. Detail route：生成具体金属线和 via，满足 DRC。
4. Post-route extraction：抽取 SPEF，获取更真实寄生。
5. Post-route optimization：修 setup/hold、transition、capacitance、SI、DRV。
6. 修 DRC/antenna/short/open，必要时调整 placement 或 floorplan。
7. 做 clock/data shielding、NDR、critical net reroute。
8. 进入 signoff extraction、STA、power、DRC/LVS 闭环。

## SI/Crosstalk 检查

[Signal Integrity](../00_overview/05_glossary.md#signal-integrity) 在 routing 后进入硬检查。并行长线、低电压、强耦合电容和高频切换会造成 crosstalk delay、noise bump、glitch 或误触发。后端通常要做 SI-aware extraction 和 STA，检查 aggressor/victim 关系、delta delay、noise margin、shielding、NDR 和关键网间距。修复手段包括加大 spacing、shielding、换 routing layer、buffering、降 slew、调整 placement 或让前端降低并发切换。

对 AI 芯片，宽 activation/weight bus、NoC link、HBM/DDR 周边和时钟邻近的高速控制线是重点。SI 修复不是 routing 的孤立问题，因为加 spacing 会消耗 routing resource，加 buffer 会增加功耗和延迟，shielding 会占用金属层，最终还要回 STA、power 和 DRC。

## 工具名

主流实现工具包括 Cadence Innovus、Synopsys IC Compiler II/Fusion Compiler、Siemens Aprisa。寄生抽取工具包括 Synopsys StarRC、Cadence Quantus。物理验证包括 Siemens Calibre、Synopsys IC Validator、Cadence Pegasus。STA 使用 PrimeTime 或 Tempus。

## 角色与典型时长

Routing owner 是 physical design engineer，STA、power integrity、physical verification engineer 都会参与 closure。小 block routing 可能数天到数周；复杂 SoC 或先进节点 routing closure 可能持续数周到数月。越先进节点，routing DRC 和寄生对 timing 的影响越需要反复迭代。

## 关键决策点

- 金属层分配：高层金属低阻适合长线和 clock/power，但资源有限。
- NDR/shielding：关键网使用更宽线距或屏蔽可改善 SI/timing，但占 routing resource。
- 拥塞处理：是局部 reroute、cell spreading、macro move，还是前端重构。
- Antenna 修复：插 diode、jumper 或改变 routing，可能影响面积和 timing。
- ECO 策略：post-route ECO 应尽量局部，避免破坏已闭合区域。

错误决策会出现连锁反应。例如为修一条 timing path 加宽加屏蔽，可能挤占邻近信号，引入新 DRC 和拥塞；为修 antenna 加 diode，可能增加负载导致 setup 变差。

## 先进节点与 28/16nm 差异

28nm/16nm routing 已经需要重视 DRC 和寄生，但 7nm 及以下的 routing 复杂度明显更高。常见差异包括更严格的 spacing/end-of-line/via 规则、更复杂的 pin access、更多 patterning/coloring 约束、更高的 wire resistance、更强的 coupling capacitance 和更明显的 variation。

先进节点 routing closure 不能只依赖实现工具内部 DRC。通常需要尽早引入 signoff deck 做 incremental check，否则最后 Calibre/ICV/Pegasus 报出大量 signoff DRC 会导致 tapeout 延误。

## 常见坑

- Floorplan 阶段低估 routing channel，routing 才发现不可达。
- 只看 global route 拥塞平均值，忽略局部 pin access 热点。
- 后期大量 ECO，破坏已清理的 DRC 和 timing。
- Critical net 没有提前保护，detail route 后寄生超预期。
- Antenna、fill、density 后处理影响 timing，却没有回 STA。
- 不区分 tool DRC 和 signoff DRC，以为实现工具 clean 就能 tapeout。
- 忽略 analog/PHY/IP 的 routing keepout 和噪声隔离要求。

## 上下游接口

Routing 上游依赖 floorplan、placement、CTS、电源网格、routing constraints 和 design rules。下游输出 GDS/OASIS、DEF、SPEF、DRC/LVS 输入、post-route timing/power 数据。

Routing feedback 会反推 placement 和 floorplan：如果拥塞来自局部 utilization，可 spread cell；如果来自 macro pin 或 channel，则要调整 floorplan；如果来自 RTL 结构，如超宽总线或集中 mux，则要前端重构。对 AI 芯片，routing feedback 往往是“你的数据流在物理上太集中”的证据。

## 创业公司取舍

创业公司应尽早跑 trial route，而不是等所有 RTL 完美后才进入后端。Trial route 可以用来验证架构物理可行性。若采用外包，合同应要求阶段性 routing congestion、DRC trend、post-route timing 和 extraction 报告。

不要为了节省面积把 routing resource 压到极限。先进节点 mask/respin 要区分情况：MPW 可能把单项目成本压到数万到数十万美元量级；metal-only ECO 通常低于 full-layer respin，但仍可能是数十万到数百万美元量级；7nm 以下 full mask 或 full-layer respin 通常可能进入数百万到千万美元量级。具体数字高度依赖 foundry、节点和商务条件，但结论很稳定：留 routing margin 通常比临近 tapeout 才解决拥塞更便宜。

## 典型场景

一个 NPU 使用 1024-bit 内部数据总线连接 SRAM bank 和 compute array。RTL 视角只是一个宽接口，floorplan 也能放下。Routing 后发现总线集中穿过两个 macro channel，detail route 大量绕线，寄生超预期，setup violation 增加，DRC 修复又进一步恶化拥塞。最终团队把总线切成多条局部通道，调整 bank 位置，并在接口增加 pipeline。物理反馈改变了微架构。

## 后续阅读

- [Static Timing Analysis](./05_static_timing_analysis.md)
- [DRC/LVS Signoff](./07_drc_lvs_signoff.md)
- [先进节点特殊考虑](./08_advanced_node_considerations.md)
- [Tapeout 流程](../04_tapeout_and_post_silicon/01_tapeout_process.md)

## 参考公开来源

- [Synopsys IC Compiler II](https://www.synopsys.com/implementation-and-signoff/physical-implementation/ic-compiler.html)
- [Cadence Innovus Implementation System](https://www.cadence.com/en_US/home/resources/datasheets/innovus-implementation-system-ds.html)
- [Synopsys StarRC](https://www.synopsys.com/implementation-and-signoff/signoff/starrc.html)
- [Cadence Quantus](https://www.cadence.com/en_US/home/tools/digital-design-and-signoff/silicon-signoff.html)
- [Siemens Calibre nmDRC](https://www.siemens.com/en-us/products/ic/calibre-design/physical-verification/design-rule-checking/)

## 内容可信度说明

- **公开信息（高可信）**：global/detail routing、寄生抽取、DRC、antenna、post-route optimization 属于公开 EDA flow。
- **行业惯例（中可信）**：NDR、shielding、trial route、incremental DRC、ECO routing 策略因项目和节点而异。
- **经验性观察（中低可信）**：AI 芯片宽总线、SRAM channel、NoC 热点常导致 routing closure 风险。
- **不确定/需向资深工程师确认（低可信）**：具体层规则、antenna 修复策略、signoff deck 版本和 foundry waiver 政策。
