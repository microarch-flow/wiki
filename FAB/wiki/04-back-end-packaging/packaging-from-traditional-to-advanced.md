# 从传统封装到先进封装:演化逻辑

上级:[后道封装](./README.md)
相关:[先进封装分类框架:2D/2.5D/3D](./packaging-taxonomy.md), [摩尔定律放缓如何把封装推到前台](./why-advanced-packaging-now.md), [为什么工艺红利在让位于封装红利](../01-overview/why-process-and-packaging-matter-now.md)

## 这页在回答什么问题

传统封装和先进封装的差别到底是什么。核心不是名字是否高级，而是 package 是否从保护和引出，变成多 die 高密度互连、供电、散热、测试和产品形态的共同承载层。

## 传统封装的目标函数

传统封装的核心任务可以压成四件事：

```text
protect die
  -> connect die to package pins/balls
  -> provide mechanical support
  -> provide basic thermal path
```

单 die wire bond、flip-chip BGA、QFN、FC-BGA 等传统或主流封装，重点在于把一个 die 可靠地接到板级系统。即使封装会影响电源、信号和散热，架构层面仍可把 die 看成主要系统边界。

这种模式适合单 die SoC、成本敏感产品、板级互连足够支撑带宽的系统。它的优势是成熟、成本可控、供应链宽、测试和失效定位相对直接。

## 先进封装改变了系统边界

先进封装出现的原因不是“封装厂想做更复杂”，而是系统需求突破了传统 package 和 PCB 的能力边界。HBM 需要超宽近距接口；大 die 遇到 reticle、良率和成本压力；chiplet 需要封装内 D2D 互连；AI/HPC 功耗密度要求更强 PDN 和热路径。

先进封装的目标函数变成：

```text
integrate multiple valuable dies
  -> provide high-density in-package interconnect
  -> manage power / signal / thermal / stress
  -> preserve testability and effective yield
```

这意味着 package 本身开始承载架构功能。die 的相对位置、封装内互连层级、HBM 邻接、substrate 能力、interposer/RDL/bridge 选择都会改变系统可达 PPA。

## 演化路径

| 阶段 | 核心结构 | 解决的问题 | 新引入的代价 |
| --- | --- | --- | --- |
| Wire bond / leadframe | die 通过金线或引脚引出 | 低成本连接与保护 | I/O 密度和电性能有限 |
| Flip-chip / FC-BGA | die 通过 bump 面阵连接 substrate | 更高 I/O、更好供电和散热 | substrate 和 bump 可靠性更关键 |
| Fan-out / RDL | 用 RDL 扇出 die I/O 或连接多 die | 更薄、更灵活、更高封装级布线 | die shift、RDL stress、warpage |
| 2.5D interposer/bridge | 多 die 并排高密度互连 | logic + HBM、chiplet 高带宽 | interposer/RDL/bridge 成本与良率 |
| 3DIC | die 垂直堆叠 | 更短互连、更高带宽密度 | 热、bonding、测试和良率耦合 |

这不是严格代际替代。传统封装仍适合大量产品；先进封装只在带宽密度、面积、功耗或系统集成收益足以覆盖复杂度时成立。

## 为什么先进封装不是“更贵外壳”

先进封装的价值来自改变数据移动路径。HBM 不是通过板级长走线提供带宽，而是通过 stack 和 2.5D/3D 集成把超宽接口拉到 logic die 附近。Chiplet 不是简单把 die 摆在一起，而是用 package 内互连重建单 die 内部曾经由 BEOL 承担的部分通信。

这和 NoC wiki 的 [chiplet 与 die-to-die 互连](../../NOC/wiki/06-ai-noc-specifics/chiplet-and-die-to-die-interconnect.md) 直接相关：跨 die 通信不是片上多几个 hop，而是换了物理层级。package 互连的带宽密度、延迟、功耗、可靠性和测试机制都不同。

## 常见误解

常见误解是“先进封装就是把多个 die 放到一个壳里”。实际难点在于高密度连接、供电完整性、热路径、机械应力、测试节点和组合良率同时闭合。

另一个误解是“先进封装会替代传统封装”。更准确的判断是：当系统需要极高带宽密度、异构节点组合、HBM 邻接或 3D 堆叠时，先进封装成为必要选项；当产品目标是成本、成熟度和简单供应链，传统封装仍是更优解。

## 一句话理解

传统封装把 die 接到系统，先进封装把多个 die 在 package 内重新组织成一个受互连、供电、热、测试和良率共同约束的系统。

## 架构师启示

如果我在做产品定义，判断是否需要先进封装的第一问不是“能不能用先进平台”，而是传统 substrate 和板级互连是否已经无法满足带宽密度、功耗或尺寸目标。如果没有这些硬约束，先进封装可能只是增加成本和风险。

一个具体例子：一个边缘 NPU 如果外存带宽和 die 面积都可由成熟单 die + LPDDR 满足，先进封装价值有限；一个数据中心 AI accelerator 如果需要多 HBM stack 和多 compute chiplet，传统封装会在互连密度、供电和热路径上失效，2.5D/3D 才进入主选项。
