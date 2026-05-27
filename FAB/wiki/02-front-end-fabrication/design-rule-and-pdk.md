# Design Rule 和 PDK:架构师与工艺的接口

上级:[前道工艺](./README.md)
相关:[工艺节点、封装路线、测试阶段的命名体系](../01-overview/taxonomy.md), [光刻:把版图变成芯片的核心步骤](./photolithography-fundamentals.md), [工艺节点演化与 PPA 取舍](./process-nodes-and-ppa-tradeoffs.md)

## 这页在回答什么问题

架构师不直接操作工艺 recipe，为什么仍然必须理解 design rule 和 PDK。因为它们是工艺能力进入 RTL、floorplan、IP、SRAM、时序、功耗和封装接口的正式边界。

## Design Rule 是制造窗口的设计语言

Design rule 把制造可行性翻译成设计几何约束，例如最小线宽、间距、via enclosure、metal density、keep-out、antenna rule、颜色规则和特定层的使用限制。它不是为了让 layout 工程师麻烦，而是为了保证光刻、刻蚀、沉积、CMP、可靠性和良率能在量产中闭合。

对架构师而言，design rule 会间接决定标准单元密度、macro 形态、routing congestion、power grid、I/O ring、bump map 和封装接口。越先进的节点，规则越 restricted，layout 自由度越低，架构层面的 floorplan 选择越早影响物理收敛。

## PDK 是工艺到设计的契约

PDK，process design kit，是 foundry/工艺平台把制造能力交给设计团队的接口集合。它包括 design rules、device models、DRC/LVS deck、parasitic extraction、layer stack、reliability rule、standard cell library、SRAM compiler、I/O/PHY 支持和 corner 定义等。

```text
process capability
  -> PDK / libraries / SRAM compiler / IP
  -> physical design / signoff
  -> manufacturable tapeout
```

架构师不会逐条读 DRC deck，但需要知道 PDK 的成熟度决定哪些架构假设能落地。没有成熟 SRAM compiler，片上存储容量模型就缺支撑；没有目标 PHY，外部接口或 D2D 方案就只是纸面选择；corner 和 voltage range 不支撑，低功耗模式就难以成为产品规格。

## PDK 如何影响早期架构

| PDK/规则对象 | 架构侧影响 | 需要早问的问题 |
| --- | --- | --- |
| Standard cell library | logic density、frequency、leakage | high-performance 与 low-power 库如何组合 |
| SRAM compiler | cache/scratchpad 容量、banking、Vmin | 宏尺寸、端口数、repair、低压能否支持 |
| Metal stack | NoC、global bus、clock、PDN | 上层金属和 top metal 是否足够 |
| I/O/PHY IP | HBM/DDR/PCIe/D2D 接口 | 目标接口是否在该节点/封装可用 |
| Reliability rules | EM/IR、ESD、latch-up、aging | 峰值功耗和寿命目标是否闭合 |
| Bump/pad rules | die-package interface | floorplan 与 package co-design 是否可行 |

## 为什么架构师要关心 rule，而不是只等后端

很多物理不可行来自架构阶段的隐性承诺。例如，在模型中把 SRAM bank 数量翻倍，后端会面对 macro placement、routing channel、power grid 和时钟问题；把 HBM interface 放在某一边，封装团队会面对 bump map、interposer routing 和热耦合；把频率目标写得过高，signoff 会面对 wire delay、IR drop 和 corner margin。

PDK 不是后端团队的局部工具，而是架构假设的边界条件。早期架构模型越接近 PDK 真实资源，后期返工越少。

## 常见误解

常见误解是“PDK 是 physical design 才用的东西”。实际 PDK 中的库、SRAM compiler、PHY、metal stack 和 corner 会直接决定架构选项。没有这些信息，架构模型只能做抽象趋势判断，不能做产品级可行性判断。

另一个误解是“design rule 越激进，架构越受益”。激进规则可能提高密度，但也可能降低 routability、增加 DRC 修复、拉长时序收敛周期，并推高良率风险。密度和可实现性必须一起评估。

## 一句话理解

Design rule 和 PDK 是工艺能力进入架构与物理设计的接口，决定哪些 PPA 假设能从模型走到可制造版图。

## 架构师启示

如果我在选节点时只问“这个节点有多少密度提升”，问题不够。应同时问：目标 SRAM compiler 是否支持所需容量、banking 和电压；HBM/D2D/PCIe PHY 是否可用；metal stack 是否支撑 NoC 和 PDN；bump map 是否能和封装路线匹配。

一个具体决策例子：若架构需要超大 SRAM scratchpad 和极宽片上 NoC，PDK 中 SRAM macro 尺寸、端口配置、top metal 资源和 IR rule 可能比纯 logic density 更决定成败。这个信息应该在 architecture exploration 阶段进入约束，而不是等 P&R 后才发现。
