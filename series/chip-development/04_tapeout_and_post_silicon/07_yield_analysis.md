# Yield Analysis

## 前置知识

- 建议先读 [Characterization](./06_characterization.md)。
- 建议理解 [Yield](../00_overview/05_glossary.md#yield)、[Wafer Test](../00_overview/05_glossary.md#wafer-test)、[Final Test](../00_overview/05_glossary.md#final-test)、[ATE](../00_overview/05_glossary.md#ate)、[Probe Card](../00_overview/05_glossary.md#probe-card)。

## 核心概念

良率是可销售良品占比，但它不是一个单一数字。常见层次包括 wafer sort yield、package yield、final test yield、system-level yield 和 field return rate。良率直接影响单颗成本和毛利，同一片 wafer 上可售 die 越少，单位芯片成本越高。

大 die AI 芯片良率压力更大：面积大意味着随机缺陷命中概率更高，先进节点工艺窗口更窄，HBM/先进封装又增加 package yield 风险。首批样品能跑 demo 不代表量产可赚钱。

## 良率影响因素

- Defect density 和工艺成熟度。
- Die size 和 critical area。
- 设计 margin：timing、IR、EM、thermal、SI。
- DFT/test coverage：scan、MBIST、ATPG、BIST。
- 封装复杂度：FC-BGA、2.5D、HBM、chiplet。
- ATE 程序质量：test escape 和 overkill。
- Wafer location、lot、tool、process excursion。

## Yield Learning Flow

1. 收集 wafer sort、final test、ATE log、fail bin、wafer map。
2. 分类 fail：DC、scan、MBIST、interface、functional、power、speed、package。
3. 做 wafer map 分析：center-edge、cluster、scratch、lot-to-lot pattern。
4. 用 scan diagnosis、MBIST fail address、ATPG pattern 定位可能 defect。
5. 关联 layout：fail 是否集中在某 macro、某区域、某金属层、某 IP。
6. 做 failure analysis：X-ray、C-SAM、SEM/FIB、delayer、emission 等。
7. 判断归因：随机缺陷、系统性工艺、设计 margin、封装、测试程序。
8. 修改 test limit、DFT、layout、工艺或设计，进入 yield ramp。

## 角色与典型时长

角色包括 yield engineer、test engineer、DFT、foundry yield team、OSAT、failure analysis、design owner、product engineer。早期 yield learning 需要数周到数月，并随着 wafer 批次和样品数量增加而改善。量产良率爬坡需要统计数据，不能靠几个样品判断。

## 关键决策点

- Fail 是设计 bug 还是制造缺陷：设计 bug 需要 ECO/respin/workaround，随机缺陷需要工艺或测试优化。
- Test limit 是否过严：过严会 overkill，降低良率；过松会 test escape，伤害客户质量。
- 是否做 redundancy/repair：SRAM repair、disable bad unit、binning 可改善可售率，但增加设计和测试复杂度。
- 是否接受降级销售：低频 bin、禁用部分单元、不同 SKU。
- 是否要求 foundry/OSAT 分析：涉及责任边界和商务谈判。

## 成本视角

单位芯片成本与 wafer price、die size、wafer sort yield、package yield、final test yield、封装成本和测试时间相关。大 die 先进节点如果良率从 80% 降到 40%，单位 die 成本可能接近翻倍；实际模型还要考虑可售 bin 和封装前后筛选。

ATE 时间也是成本。复杂 AI SoC 的测试如果从几十秒增加到数分钟，量产测试成本会明显上升。DFT 和 BIST 的目标不是追求测试多，而是在 coverage、测试时间和诊断能力之间平衡。

## 先进节点与成熟节点差异

先进节点 defect density、variation、功耗密度和 design rule 复杂度让 yield ramp 更难。大 die AI 芯片可能考虑 chiplet、冗余、repair、binning 来改善商业良率。成熟节点良率通常更可预测，但大 die、模拟 IP、封装和测试仍可能成为风险。

## 常见坑

- 把首批少量样品成功当作良率结论。
- 没有 wafer map 和样品追踪，无法分析空间相关性。
- DFT 覆盖不足，fail 只能归为 unknown。
- Test limit 直接沿用 characterization 初稿，没有随数据更新。
- 忽略 package yield，把 wafer sort pass 当最终 yield。
- 与 foundry/OSAT 缺少清晰 failure ownership，问题来回甩锅。

## 上下游接口

上游来自 wafer fab、wafer sort、OSAT、final test、characterization、DFT。下游影响 production ramp、成本模型、SKU/binning、customer qualification、respin 决策。

Yield analysis 会反推设计：如果 fail 集中在某 SRAM macro，需要看 MBIST/repair；如果边缘 die fail 多，要看工艺均匀性或电源/thermal margin；如果某 pattern fail，要看 ATPG/scan diagnosis 和 layout。

## 创业公司取舍

创业公司要在商业计划中预留 yield ramp。样片能 demo 不等于毛利成立。第一颗芯片如果 die 很大、封装复杂、测试覆盖不足，即使功能正确，也可能因为良率和测试成本无法商业化。

可以外包 ATE 和 failure analysis，但内部必须懂良率数据如何影响成本、客户承诺和下一版设计。CEO/CTO 至少要能读懂 wafer map、fail bin、yield trend 和 test escape 风险。

## 典型场景

某 AI 芯片 wafer sort 显示 scan pass 率高，但 final test 后良率下降。分析发现高功耗 workload 下部分封装样品 fail，wafer sort 未覆盖该功耗场景。进一步 thermal/PI 分析发现封装供电和散热 margin 不足。修复不是 RTL bug，而是封装、test limit、功耗模式和客户规格共同调整。

## 后续阅读

- [Silicon Revision](./08_silicon_revision.md)
- [Qualification and Reliability](../05_production_and_lifecycle/01_qualification_and_reliability.md)
- [Volume Ramp](../05_production_and_lifecycle/02_volume_ramp.md)
- [成本结构](../00_overview/03_cost_structure.md)

## 参考公开来源

- [JEDEC JESD47 overview via TI reliability testing reference](https://www.ti.com/quality-reliability/reliability/testing.html)
- [Teradyne semiconductor test overview](https://www.teradyne.com/)
- [Advantest semiconductor test overview](https://www.advantest.com/)
- [Siemens Tessent diagnosis resources](https://www.siemens.com/en-us/products/ic/tessent/offerings/)

## 内容可信度说明

- **公开信息（高可信）**：yield、wafer sort、final test、ATE、probe card、scan diagnosis、failure analysis 的基本概念。
- **行业惯例（中可信）**：fail bin、wafer map、yield learning、test limit 调整和 foundry/OSAT 协作流程。
- **经验性观察（中低可信）**：大 die AI 芯片良率和封装良率可能成为商业化主要风险。
- **不确定/需向资深工程师确认（低可信）**：defect density、yield model、良率目标、foundry 责任边界和具体 FA 结论。
