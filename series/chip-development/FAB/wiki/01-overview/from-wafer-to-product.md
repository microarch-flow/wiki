# 一片 wafer 到一颗成品芯片的完整路径

上级:[芯片制造与封测 Wiki 总览](./README.md)
相关:[前道与后道:产业分工和技术差异](./front-end-vs-back-end.md), [为什么必须在 wafer 阶段测试](../03-wafer-test-and-cp/why-wafer-sort-exists.md), [从传统封装到先进封装:演化逻辑](../04-back-end-packaging/packaging-from-traditional-to-advanced.md)

## 这页在回答什么问题

一片 wafer 如何经过前道、中测、切割、封装、终测，最后变成可以交付的芯片产品。核心不是背流程，而是理解每个阶段在筛掉什么风险、增加什么价值、引入什么约束。

## 端到端对象流

从物理对象看，芯片产品经历的是下面这条路径：

```text
bare silicon wafer
  -> processed wafer with many dies
  -> probed wafer with pass/fail map
  -> singulated known-good / suspect dies
  -> assembled package
  -> tested and qualified product
  -> board / module / system
```

前道制造把一片空白硅片变成包含大量 die 的 processed wafer。每个 die 里已经有 transistor、local interconnect、BEOL 金属层、pad 或 bump landing structure。这个阶段结束后，芯片在电路意义上已经存在，但还不是产品，因为它没有被筛选、切割、保护、引出、散热和系统连接。

CP，也就是 wafer sort，把 probe card 接触 wafer 上的 pad 或 bump，对每个 die 做电性与功能筛选。它的价值是尽早发现坏 die，尤其在先进封装中，坏 die 如果进入 2.5D/3D package，会拖累更昂贵的 HBM、interposer、substrate 和其他 good die。

切割把 wafer 上的 die 分离出来。之后封装流程根据产品形态不同而分叉：传统单 die 封装把一个 die attach 到 substrate 或 leadframe，再 wire bond 或 flip-chip 连接；先进封装会把多个 die、HBM stack、interposer、RDL、bridge、substrate 组合成更复杂的 package。

终测和可靠性验证确认封装后的产品在目标电压、频率、温度、机械和寿命条件下仍然满足规格。封装会引入新的风险，例如 bump fatigue、warpage、delamination、underfill void、thermal coupling 和 package-level SI/PI 问题，所以通过 CP 的 die 不等于已经可以出货。

## 每个阶段在改变什么

| 阶段 | 输入 | 输出 | 主要风险筛选 | 架构相关性 |
| --- | --- | --- | --- | --- |
| Wafer fabrication | 空白 wafer、mask、process recipe | processed wafer | 缺陷密度、器件/互联参数、工艺窗口 | 节点、面积、频率、SRAM、BEOL |
| Wafer sort / CP | processed wafer | die map、KGD 候选 | 功能、电性、部分速度/功耗异常 | 多 die 封装前的筛选策略 |
| Singulation | wafer | individual dies | 崩边、裂纹、薄 die handling | 3DIC 与大 die 风险 |
| Package assembly | die、substrate、interposer、RDL、HBM | package | 对位、键合、warpage、界面缺陷 | D2D、HBM、热、供电 |
| Final test | package | binning 后产品 | 封装后功能、频率、功耗、温度行为 | SKU、binning、产品成本 |
| Reliability qualification | package / sample lot | 认证结论 | 热循环、湿度、应力、老化 | 目标市场与寿命要求 |

这张表的重点是：每个阶段既增加价值，也增加不可逆成本。越晚发现问题，报废对象越贵。一个坏 transistor 只损失一个 die；一个坏 HBM stack、interposer 或 bonding defect 可能报废整个高价值 package。

## 单 die 与多 die 的差异

传统单 die 产品中，前道良率和终测 binning 是主线。封装当然重要，但封装对象相对单一，坏 die 进入封装造成的损失较可控。

多 die 与 HBM package 改变了风险结构。一个 package 可能包含 compute die、I/O die、HBM stack、silicon interposer、RDL、substrate 和大量 micro-bump。若每个对象单独良率都高，组合后仍可能因为乘法效应变低。因为这些对象一旦组装在一起，某个关键连接或某个 die 失效就可能让整套 package 失去价值，所以 KGD、分阶段测试和封装良率会变成架构级问题。

## 常见误解

常见误解是“wafer 做完就等于芯片做完”。实际上，wafer 做完只得到大量裸 die，产品还需要测试、切割、封装、终测和可靠性验证。对于 HBM 和 chiplet 产品，后半段不是简单包装，而是决定带宽、功耗、热、机械可靠性和成本的系统集成。

另一个误解是“测试只是最后验一下”。实际测试是分阶段风险控制。CP 是为了避免坏 die 进入昂贵封装；中间测试是为了在复杂 assembly 过程中定位问题；final test 是为了确认封装后产品满足规格；可靠性验证是为了确认它能在目标寿命内工作。

## 一句话理解

从 wafer 到产品是一条逐步增加价值、逐步筛选风险的链路；越复杂的封装，越需要把测试和良率前移。

## 架构师启示

如果我在评估 monolithic die 与 chiplet 方案，不能只比较 die 面积和 NoC/D2D 性能。monolithic die 的主要风险在前道大 die 良率；chiplet 方案把部分风险转移到 KGD、封装 assembly、die-to-die 连接和组合良率。若单个 chiplet 良率更高，但 package 里 die 数量、HBM stack 数量和互连数量大幅增加，最终成本不一定下降。

架构评审中应该显式画出产品对象树：哪些 die、几个 HBM stack、什么 interposer 或 RDL、几个测试节点、哪个阶段能发现哪类 defect。没有这张对象树，就很容易把“设计能工作”误判成“产品能量产”。
