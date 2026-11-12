# Advanced Node Considerations

## 前置知识

- 建议先读本目录 [Floorplanning](./01_floorplanning.md) 到 [DRC/LVS Signoff](./07_drc_lvs_signoff.md)。
- 建议先读 [工艺节点选择](../01_product_definition_and_architecture/05_process_node_selection.md)。
- 建议理解 [PDK](../00_overview/05_glossary.md#pdk)、[Mask Cost](../00_overview/05_glossary.md#mask-cost)、[PPA](../00_overview/05_glossary.md#ppa)。

## 核心概念

先进节点这里主要指 7nm 及以下，包括 7nm、5nm、3nm 等 FinFET/GAA 相关工艺。它们提供更高密度、更低能耗潜力和更高性能上限，但代价是设计规则复杂、mask 成本高、EDA 和 IP 成本高、signoff 难度高、foundry 关系门槛高。

先进节点不是“同样设计自动缩小”。线延迟、wire RC、via resistance、variation、power density、IR/EM、pin access、DFM、multi-patterning/EUV、library 选择、thermal 和 package 都会改变设计方法。对 AI 芯片，先进节点的价值来自高密度算力和能效，但风险也集中在功耗密度、SRAM、NoC、HBM/先进封装和后端 closure。

## 关键活动顺序

1. 工艺选择前建立 PPA/cost/risk 模型：性能目标、die size、IP availability、mask/NRE、volume。
2. 获取 foundry PDK、reference flow、standard cell、SRAM compiler、IO/PHY/IP 支持。
3. 早期 floorplan 和 trial implementation，验证目标频率和拥塞是否现实。
4. 建立 [MMMC](../00_overview/05_glossary.md#mmmc)/OCV/signoff methodology，确认工具版本和 foundry certification。
5. 做 power/thermal/package 联合评估。
6. 在前端阶段就引入 physical feedback：pipeline、banking、NoC、clock/power domain、macro strategy。
7. 进行 incremental signoff：DRC、STA、IR/EM、SI、DFM 不能等最后。
8. tapeout 前严格控制 ECO 和版本冻结。

## 工具名

先进节点通常强依赖 foundry-qualified EDA flow。常见工具包括 Synopsys Fusion Compiler/IC Compiler II、Cadence Innovus、PrimeTime、Tempus、StarRC、Quantus、Calibre、IC Validator、Pegasus、Voltus、RedHawk-SC。具体工具版本和 deck 组合必须按 foundry 要求确认。

## 角色与典型时长

先进节点需要更资深的 physical design lead、STA lead、power integrity lead、CAD/flow lead、foundry interface owner 和 IP integration owner。即使设计团队很强，先进节点全芯片后端 closure 通常也是数月量级工作。节点越先进，前期准备和 signoff 迭代越不能压缩。

## 7nm 以下与 28/16nm 的核心差异

- 成本：先进节点 full mask 通常是数百万到千万美元量级，具体取决于 foundry、节点、reticle、商务和 shuttle 条件；MPW 可显著降低单项目试验成本，但面积、封装和 schedule 受限；28nm 成本低很多。
- 规则：先进节点 DRC/DFM 规则更多且上下文相关，signoff runtime 和 debug 成本更高。
- 线延迟：晶体管变快不代表长线更快，wire delay 更主导。
- 变异：OCV/AOCV/POCV/LVF 等更重要，STA corner 和 derate 更复杂。
- 电源：电压更低、功耗密度高、IR/EM/thermal 更难。
- IP：高速 SerDes、PCIe、DDR/HBM、SRAM compiler、PLL、IO 都更依赖 vendor/foundry 成熟度。
- 团队：成熟节点可用较轻流程做原型；先进节点需要高纪律的 signoff 和版本管理。

## 关键决策点

- 是否真的需要先进节点：如果瓶颈是软件栈、内存带宽、客户验证或架构未定，先进节点可能放大风险。
- 首版是否用成熟节点/MPW 验证架构：可降低成本和学习风险，但性能宣传受限。
- 是否采用 chiplet/先进封装：可改善良率和复用，但系统复杂度大增。
- 是否买 hard IP：自研先进节点 PHY/SerDes/HBM controller 对创业公司通常不现实。
- 是否追求极限频率：先进节点高频 closure 昂贵，可能不如通过架构并行度和软件调度解决。

## 常见坑

- 把先进节点当作性能问题的万能解。
- 低估 IP 授权、EDA license、foundry access 和 signoff 成本。
- 只看标准单元密度，不看 SRAM、analog、IO、power grid 和 routing。
- 用 28nm 的后端经验管理 5nm 项目。
- 没有早期 physical prototyping，导致 RTL 冻结后才发现 PPA 不可实现。
- 忽略 package/thermal，导致 die 内设计成立但系统不可用。
- 认为 AI agent 可以跳过 foundry rule、signoff 和资深工程判断。

## 上下游接口

先进节点选择会反推产品定义、IP 策略、架构、RTL、验证、后端、封装、供应链和融资计划。上游的频率、面积、功耗、接口和工艺选择直接决定后端难度；下游的 foundry、mask、wafer、封装、测试成本决定商业可行性。

Physical feedback 在先进节点必须前移。架构探索阶段就应做粗粒度 floorplan、SRAM banking、NoC wirelength、power estimate 和 timing feasibility，而不是等 RTL 完成后再发现物理不可行。

## 创业公司取舍

如果第一颗芯片目标是证明架构和软件生态，成熟节点或 MPW test chip 可能更务实。如果目标是直接进入高性能 AI 市场，先进节点可能不可避免，但必须匹配融资、团队、IP、foundry 和客户验证周期。

快速迭代可以压缩架构探索、RTL 生成、仿真自动化、CI、文档一致性和部分后端脚本化；不能压缩 foundry PDK 获取、IP bring-up、physical signoff、mask 制作、wafer fab、封装、可靠性认证这些物理和供应链环节。

## Respin 成本边界

先进节点修改要区分类型。Metal-only ECO 如果预留 spare cell 且改动局部，可能只需要部分金属层 mask，成本和周期低于全层 respin，但仍可能达到数十万到数百万美元量级。Full-layer respin 或 full mask set 通常是数百万到千万美元量级，并叠加 wafer、封装、测试、工程人力和机会成本。MPW shuttle 能降低原型成本，但不能代表量产 mask 成本，也不适合承载所有系统级风险。

这些数字只能作为公开量级判断，不能替代 foundry 报价。对创业公司来说，关键不是记住某个数，而是知道“后端多花几周做 signoff closure”与“硅后 respin”不是同一数量级的风险。

## 典型场景

团队计划 5nm 首发 AI SoC，目标频率很高，并假设 RTL 自动生成能把开发压到数月。早期 trial implementation 显示 compute array 本身面积可控，但 SRAM macro 占比高，NoC 和 HBM 接口周边拥塞，dynamic IR 超标，STA 关键路径主要是跨 cluster wire。团队最终决定先用成熟节点 MPW 验证 tile 和编译器，同时继续做 5nm physical prototyping。这不是退缩，而是把架构风险和先进节点量产风险拆开。

## 后续阅读

- [后端外包](./09_backend_outsourcing.md)
- [工艺节点选择](../01_product_definition_and_architecture/05_process_node_selection.md)
- [Foundry 关系](../06_cross_cutting_topics/02_foundry_relationships.md)
- [MPW 策略](../06_cross_cutting_topics/04_mpw_shuttle_strategy.md)
- [快速迭代真实约束](../07_for_software_background_founders/05_fast_iteration_realities.md)

## 参考公开来源

- [Synopsys IC Compiler II](https://www.synopsys.com/implementation-and-signoff/physical-implementation/ic-compiler.html)
- [Synopsys PrimeTime](https://www.synopsys.com/implementation-and-signoff/signoff/primetime.html)
- [Siemens Calibre nmDRC](https://www.siemens.com/en-us/products/ic/calibre-design/physical-verification/design-rule-checking/)
- [Ansys RedHawk-SC](https://www.ansys.com/en-gb/products/semiconductors/ansys-redhawk-sc)

## 内容可信度说明

- **公开信息（高可信）**：先进节点需要复杂 STA、DRC、power integrity、foundry-qualified flow 和高成本 mask，这些方向公开可查。
- **行业惯例（中可信）**：7nm 以下设计中 wire RC、variation、IR/EM、pin access、DFM 更关键是业界普遍经验。
- **经验性观察（中低可信）**：创业公司应拆分架构验证风险和先进节点量产风险，避免首版同时挑战所有不确定性。
- **不确定/需向资深工程师确认（低可信）**：具体节点成本、PDK access 条件、mask 报价、tool certification、foundry rule 和 shuttle 可用性。
