# CIM 论文阅读模板

上级：[09 研究前沿](README.md)
相关：[指标术语表](metrics-glossary.md), [研究视角与产业视角](research-vs-industry-perspective.md), [CIM/PIM/NMC 分类](../01-overview/cim-pim-nmc-taxonomy.md)

## 这页在回答什么问题

这页回答：读一篇 CIM/PIM/NMC 论文时，最少要记录哪些信息，才能避免后续比较失真。

复制下面模板时，不要只填标题和指标；重点是把 taxonomy、层级、开销范围和不能外推的边界写清楚。

```markdown
# 论文标题

## 基本信息

- 会议/期刊：
- 年份：
- 作者/机构：
- DOI/官方链接：
- 本 wiki taxonomy：CIM / PIM / NMC / boundary case
- memory technology：SRAM / ReRAM / PCM / Flash / MRAM / DRAM-HBM-GDDR / other
- compute paradigm：analog / digital / mixed-signal
- 结果层级：device / macro / tile / chip / card-module / system / simulation

## 这篇论文真正解决的问题

- 它解决的是 device、circuit、macro、architecture、software 还是 system 问题？
- 如果没有这个设计，瓶颈会是什么？
- 它和已有工作的关键差异是什么？

## 结构拆解

- cell/array 结构：
- 输入编码：
- 权重表示：
- 乘法方式：
- 累加方式：
- ADC/DAC/SA 或 digital peripheral：
- local buffer / NoC / reduction：
- host/controller/runtime 接口：

## 指标记录

- 性能：
- 能效：
- 面积：
- 精度：
- workload/model/dataset：
- precision：
- 是否 silicon measured：
- 是否包含 ADC/DAC/SA/buffer/NoC/DRAM/host：
- baseline：

## 不能外推的边界

- 哪些结果只在 macro/kernel 层成立？
- 哪些开销没有包含？
- 哪些 workload 不适合这个方案？
- 哪些假设依赖 calibration、retraining 或 compiler？

## 我的判断

- 技术贡献：
- 最大风险：
- 对 02/03/04/05/06/07 哪章最有帮助：
- 是否适合进入 08 产业分析：
- 后续要追的论文/数据：
```

阅读时还要额外记录一个“反证问题”：如果我要证明这篇论文对系统没有帮助，我会攻击哪个假设？常见攻击点包括 array utilization、write energy、ADC overhead、model accuracy recovery、host stall、memory bandwidth、thermal 和 yield。

## 一句话理解

论文模板的目的不是存档，而是强迫每篇论文暴露 taxonomy、层级、指标口径和外推边界。

## 研究启示

系统性研究笔记比单篇 summary 更重要。CIM/PIM/NMC 的论文指标跨层差异太大，只有统一模板才能积累可比较的知识库，避免下一次再把 macro 能效、card demo 和 system speedup 混在一起。
