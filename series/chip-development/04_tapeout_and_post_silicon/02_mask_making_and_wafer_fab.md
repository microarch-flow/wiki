# Mask Making and Wafer Fab

## 前置知识

- 建议先读 [Tapeout Process](./01_tapeout_process.md)。
- 建议理解 [Mask Cost](../00_overview/05_glossary.md#mask-cost)、[Wafer](../00_overview/05_glossary.md#wafer)、[MPW Multi Project Wafer](../00_overview/05_glossary.md#mpw-multi-project-wafer)、[Foundry](../00_overview/05_glossary.md#foundry)。

## 核心概念

Mask set 是把设计图形转化为光刻用光罩的一整套版。Reticle 是光刻机曝光时使用的版图窗口。Wafer fab 是在晶圆上通过多轮沉积、光刻、刻蚀、离子注入、CMP、金属互连和钝化等工艺制造芯片。

这一步是“快速迭代芯片”的硬边界之一。GDS 进入 mask/fab 后，RTL 修复已经来不及。你可以自动化 checklist、减少人为错误、提高 tapeout 准备效率，但不能把 mask 制作、曝光、工艺步骤和 fab 排队压缩成软件发版速度。

## Mask 为什么贵

先进节点 mask 成本高，原因包括更多工艺层、更复杂的 OPC/RET、EUV/DUV 组合、多重图形化、更严设计规则、更昂贵的 mask blank 和 inspection。公开量级上，成熟节点 full mask 可能是数十万到数百万美元；7nm 及以下先进节点 full mask 通常是数百万到千万美元量级。具体报价高度依赖 foundry、节点、mask 层数、商务关系和是否 shuttle。

MPW 把多个设计拼到同一 reticle/wafer 上，共享 mask 和制造成本，适合原型验证。它的限制是面积、IO、封装、时间窗口、数量和 foundry 支持，不能等同于量产 dedicated wafer。

## Wafer Fab 流程量级

晶圆制造包含很多重复步骤：薄膜沉积、光刻、刻蚀、离子注入、退火、CMP、金属层形成、via、钝化、晶圆级检查。先进节点层数多、工艺窗口窄，cycle time 通常更长。

典型 fab 周期是数周到数月量级，取决于节点、工艺复杂度、foundry 产能、lot 优先级、是否 hot lot、是否 MPW、是否有工艺 hold。创业公司不能默认“tapeout 后几周就拿到芯片”，必须向 foundry 或服务商确认真实 schedule。

## 关键活动顺序

1. Foundry 接收 tapeout package 并做 incoming data check。
2. Mask data prep：fracturing、OPC、RET、mask inspection 数据准备。
3. Mask shop 制作并检查 mask set。
4. Wafer lot release，进入 fab 工艺流程。
5. 工艺中执行多轮 inline metrology 和 process control。
6. Wafer 完成后做 wafer acceptance 或 parametric test。
7. 进入 wafer sort 或送往 OSAT 封装，视项目流程而定。

## 典型设备和工具

Mask/fab 阶段的具体工具多数在 foundry 和 mask shop 内部，设计团队通常只能看到接口和结果。典型类别包括 mask data preparation/fracturing 工具、OPC/RET 工具、e-beam mask writer、mask inspection/repair 设备、ASML DUV/EUV lithography scanner、deposition/etch/implant/CMP 工艺设备、CD-SEM、overlay metrology、defect inspection、inline parametric test 和 wafer acceptance test。

这些设备不是创业公司要购买的资产，但 CEO/CTO 需要理解它们带来的周期和不透明性。Fab 阶段很多异常只能通过 foundry 报告、parametric data、wafer map、ATE 结果和后续 failure analysis 间接推断。

## 角色与典型时长

Foundry interface owner、后端/CAD、foundry AE、mask shop、fab operations、test engineer、项目经理参与。设计团队在 fab 内部可见性有限，通常只能看到里程碑、lot 状态、parametric 数据摘要或异常通知。周期从数周到数月，先进节点和紧张产能下更不可控。

## 关键决策点

- MPW 还是 dedicated wafer：MPW 省成本但限制多；dedicated wafer 更接近量产但 NRE 高。
- 是否申请 hot lot：可缩短周期，但成本高且不一定可获得。
- 首版节点选择：成熟节点降低学习成本，先进节点提高性能/能效但放大现金流风险。
- 多少 wafer 数量：样片太少不足以做 yield/characterization；太多会浪费 NRE。
- 是否同步准备封装和测试：等 wafer 完成再准备会拖慢 bring-up。

## 常见坑

- 把 foundry 给的典型 cycle time 当作承诺，不留 buffer。
- MPW 样片成功后误以为量产 dedicated wafer 风险相同。
- 低估 mask data prep 和 foundry incoming check 发现问题的时间。
- 没有确认 wafer 到 OSAT 的物流、报关、保险和责任边界。
- 没有准备 wafer sort/封装/test program，导致 wafer 完成后等待。
- 以为 fab 阶段能看到所有制造细节，实际很多数据受 foundry NDA 和内部流程限制。

## 上下游接口

上游输入是 tapeout package、foundry 提交表、商务订单和 schedule。下游输出是完成制造的 wafer、parametric data、wafer map、工艺异常报告、可进入 wafer sort 或封装的材料。

如果 fab 后出现低良率，设计团队需要结合 DFT、ATE log、wafer map 和 failure analysis 判断是随机缺陷、系统性工艺问题、设计 margin 不足还是封装/测试问题。

## 创业公司取舍

创业公司第一颗芯片若核心风险是架构和软件，MPW 或成熟节点 test chip 是合理策略。若直接上先进节点 dedicated tapeout，必须确保融资覆盖 mask、wafer、封装、测试、bring-up、respin 和时间延误。不要把“快速迭代”的融资叙事建立在 fab 周期可任意压缩的假设上。

## 典型场景

团队完成 7nm tapeout 后认为六周可拿到芯片。实际 foundry incoming check 要求修正一处 layer map 配置，mask data prep 排队，fab lot 进入普通优先级，封装 substrate 也未准备好。最终从 tapeout 到可上电样片经历数月。问题不在某个工程师慢，而是供应链和制造流程本身需要提前管理。

## 后续阅读

- [Packaging](./03_packaging.md)
- [Post-silicon Bring-up](./04_post_silicon_bringup.md)
- [Yield Analysis](./07_yield_analysis.md)
- [MPW 策略](../06_cross_cutting_topics/04_mpw_shuttle_strategy.md)

## 参考公开来源

- [TSMC Open Innovation Platform overview](https://www.tsmc.com/english/dedicatedFoundry/oip)
- [ASML EUV lithography overview](https://www.asml.com/en/technology/lithography-principles/euv-lithography)
- [SEMI semiconductor manufacturing overview](https://www.semi.org/en)

## 内容可信度说明

- **公开信息（高可信）**：mask、reticle、photolithography、wafer fab、MPW 与 dedicated wafer 的基本概念。
- **行业惯例（中可信）**：mask data prep、foundry incoming check、fab cycle time、hot lot 和 wafer handoff 的项目管理影响。
- **经验性观察（中低可信）**：创业公司常低估 fab 排队、mask check、封装准备和测试程序并行开发的重要性。
- **不确定/需向资深工程师确认（低可信）**：具体 mask cost、wafer cost、cycle time、EUV 层数、hot lot 可用性和 foundry 数据透明度。
