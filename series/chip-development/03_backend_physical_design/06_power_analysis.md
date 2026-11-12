# Power Analysis

## 前置知识

- 建议先读 [Static Timing Analysis](./05_static_timing_analysis.md)。
- 建议理解 [PPA](../00_overview/05_glossary.md#ppa)、[IR Drop](../00_overview/05_glossary.md#ir-drop)、[EM](../00_overview/05_glossary.md#em)、[低功耗设计](../02_frontend_design_and_verification/07_low_power_design.md)。

## 核心概念

Power analysis 包括功耗估算、电源完整性和可靠性分析。功耗本身分为 dynamic power、leakage power、short-circuit power。电源完整性关注 [IR Drop](../00_overview/05_glossary.md#ir-drop)、dynamic voltage drop、电源噪声、decap、package/board 供电路径。可靠性关注 [EM](../00_overview/05_glossary.md#em)、热和长期寿命。

AI 芯片功耗分析特别重要，因为 workload 会造成大规模同步切换，SRAM/NoC/compute array 的 activity 高且集中。平均功耗可接受不代表瞬态电压下降可接受。硅上失败可能表现为高负载场景随机错误、频率降级、温度敏感或良率问题。

## 关键活动顺序

1. 建立功耗场景：典型 workload、峰值 workload、idle、boot、scan、BIST、低功耗模式。
2. 准备 activity：SAIF/VCD/FSDB、vectorless estimate、emulation trace、软件 workload trace。
3. 做 early power estimate：RTL/综合/placement 阶段估算功耗趋势。
4. 设计 power grid：ring、stripe、mesh、via array、decap、power switch。
5. 静态 IR 分析：平均电流下的电压下降。
6. 动态 IR 分析：时序相关 switching 下的瞬态电压下降。
7. EM 分析：电源网、信号线、clock net、via 的电流密度。
8. Thermal/package 联合评估，必要时反馈封装、散热和 workload 限制。
9. 修复：加宽电源网、增加 via/decap、调整 placement、降低 activity、clock gating、power gating、软件调度限制。
10. 生成 power signoff 报告和风险清单。

## 工具名

常见工具包括 Cadence Voltus、Ansys RedHawk-SC、Synopsys PrimePower/Fusion Power、Synopsys PrimeRail。实现工具 Innovus、IC Compiler II/Fusion Compiler 也有 power-aware implementation 能力。activity 生成来自 VCS、Xcelium、Verilator、emulation 平台或软件性能模型。

## 角色与典型时长

Power integrity engineer 是核心 owner，physical design、package、architecture、RTL、software/runtime 团队都要参与。Block 级 power 分析可数天到数周；全芯片动态 IR/EM/thermal closure 可能持续数周到数月。先进节点和高功耗 AI 芯片中，power closure 与 timing closure 同等重要。

## 关键决策点

- 用什么 workload 做 signoff：过弱会漏峰值风险，过强会过度设计。
- Power grid 强度：太弱 IR/EM 失败，太强占 routing resource 和面积。
- Decap 放置：可缓解动态 IR，但占面积并可能增加 leakage。
- Clock/power gating 策略：省功耗但增加验证、DFT、UPF 和后端复杂度。
- 是否限制软件调度：可以降低峰值电流，但影响性能和产品承诺。

## 先进节点与 28/16nm 差异

7nm 及以下电源电压更低，电压裕量更小；金属线更细，via resistance 和 EM 风险更突出；功耗密度更高，热和局部 IR drop 更难处理。相比 28nm，先进节点不是简单“更省电”，因为在高频高密度设计中，供电和散热常成为限制。

先进封装、HBM、chiplet 或 2.5D/3D 还会把 package/thermal/PDN 问题提前到架构阶段。只做 die 内 power signoff 不够，还要考虑 package 和 board 供电路径。

## 常见坑

- 只有 vectorless power，没有真实 workload activity。
- 使用宣传 workload 做性能，使用温和 workload 做 power signoff。
- 忽略 scan/BIST 模式功耗，ATE 测试时过流。
- UPF 与实际 power switch/isolation/retention 不一致。
- 后期才加 decap 或 power stripe，挤占 routing 并引入 timing 问题。
- 没有把 IR drop 对 timing 的影响纳入 STA。
- 忽略软件调度对瞬态电流的影响。

## 上下游接口

Power analysis 上游依赖 RTL activity、网表、placement/routing、power grid、package model、library power model、UPF 和 workload 定义。下游影响 STA、routing、floorplan、package、thermal、量产测试和软件 runtime policy。

Power feedback 会反推前端和软件。例如某个矩阵算子让所有 tile 同周期启动，动态 IR 超标；硬件可加 decap 和 power grid，但更有效可能是 runtime 做 staggered launch，或硬件增加启动节流。对 AI 芯片公司，软件和后端必须共同定义 power virus 和 realistic workload。

## 创业公司取舍

创业公司不能只用峰值 TOPS 做产品定义，必须定义功耗和散热边界。第一颗芯片可以通过保守频率、限制峰值并发、简化 power domain、预留 decap 和选择较稳妥封装来降低风险。

可以省的是复杂 DVFS 和极致低功耗优化；不能省的是 IR/EM signoff、真实 workload power 分析和 package/thermal 早期评估。功耗问题一旦到硅后才发现，通常只能降频、限流或 respin。

## 典型场景

NPU 在单 tile benchmark 下功耗正常，但全芯片跑 transformer attention 时，多个 tile、NoC 和 SRAM 同时高活动，动态 IR 超标。仿真功能没有错，但硅上可能在高温低压角随机出错。修复方案包括增强局部 power mesh、增加 decap、调整 clock gating、修改 runtime 调度让 tile 分批启动，并把该 workload 加入 signoff power suite。

## 后续阅读

- [DRC/LVS Signoff](./07_drc_lvs_signoff.md)
- [先进节点特殊考虑](./08_advanced_node_considerations.md)
- [封装](../04_tapeout_and_post_silicon/03_packaging.md)
- [AI 芯片特有考虑](../06_cross_cutting_topics/06_ai_chip_specific.md)

## 参考公开来源

- [Cadence Voltus IC Power Integrity Solution](https://www.cadence.com/en_US/home/resources/datasheets/voltus-ic-power-integrity-solution-gt-ds.html)
- [Ansys RedHawk-SC](https://www.ansys.com/en-gb/products/semiconductors/ansys-redhawk-sc)
- [Synopsys PrimeTime](https://www.synopsys.com/implementation-and-signoff/signoff/primetime.html)
- [Synopsys StarRC](https://www.synopsys.com/implementation-and-signoff/signoff/starrc.html)

## 内容可信度说明

- **公开信息（高可信）**：IR drop、EM、dynamic/static power、Voltus、RedHawk-SC 等工具用途公开可查。
- **行业惯例（中可信）**：power signoff workload、dynamic IR、decap、package-aware analysis 是常见实践，但细节高度项目相关。
- **经验性观察（中低可信）**：AI 芯片常因真实 workload activity 与早期估算不一致产生 power closure 风险。
- **不确定/需向资深工程师确认（低可信）**：具体 IR/EM 阈值、power virus 定义、thermal model、package PDN 模型和 foundry 可靠性规则。
