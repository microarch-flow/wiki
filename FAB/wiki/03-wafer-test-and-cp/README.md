# 中测:CP 阶段

上级:[芯片制造与封测 Wiki 总览](../01-overview/README.md)
相关:[一片 wafer 到一颗成品芯片的完整路径](../01-overview/from-wafer-to-product.md), [前道工艺](../02-front-end-fabrication/README.md), [终测与可靠性](../05-final-test-and-reliability/README.md)

## 这页在回答什么问题

为什么 wafer 做完后不能直接切割封装，而要先在 wafer 阶段做 CP/wafer sort。这个章节把前道良率接到后道封装：坏 die 越晚被发现，损失越大；封装越复杂，测试越必须前移。

## CP 在整条链路中的位置

CP，circuit probing 或 wafer sort，发生在 processed wafer 完成之后、die singulation 和封装之前。它的核心目标是用 probe card 接触 wafer 上的 test pad 或 bump，尽早判断每个 die 是否值得进入后续流程。

```text
processed wafer
  -> wafer sort / CP
       functional test
       parametric test
       scan / memory BIST / repair data
       speed / leakage binning
  -> wafer map
  -> die singulation
  -> KGD selection
  -> package assembly
```

CP 不是 final test 的替代品。CP 的环境、接触条件、散热和测试覆盖率都受 wafer 阶段限制；final test 会在封装后验证 package 级功能、速度、热、电源和 I/O 行为。两者分工不同：CP 是封装前筛选，final test 是产品级确认。

## 本章文件关系

| 文件 | 主要问题 | 后续使用 |
| --- | --- | --- |
| [why-wafer-sort-exists.md](./why-wafer-sort-exists.md) | 为什么必须在 wafer 阶段拦截坏 die | KGD、良率经济学 |
| [cp-test-methodology.md](./cp-test-methodology.md) | CP 具体测什么、怎么形成 wafer map | final test、binning |
| [kgd-known-good-die.md](./kgd-known-good-die.md) | 为什么 known-good die 是 HBM/3DIC 前提 | 2.5D/3D 封装 |
| [yield-and-defect-density.md](./yield-and-defect-density.md) | 缺陷密度如何把面积变成经济问题 | chiplet 选型 |
| [test-cost-vs-coverage-tradeoff.md](./test-cost-vs-coverage-tradeoff.md) | 为什么测试覆盖率不能无限提高 | DFT、产品成本 |

## 测试前移的核心逻辑

传统低复杂度单 die 封装中，坏 die 进入封装造成的损失相对有限。先进封装改变了损失结构：一个坏 compute die 可能拖累多个 HBM stack、interposer、substrate 和多轮 assembly；一个坏 HBM stack 也可能报废整套高价值 package。

因此，CP 的价值不只是提高出货质量，而是保护后续高价值资源。对于 D2W、HBM、3DIC 和多 chiplet package，KGD 是降低组合良率风险的前提。

## 一句话理解

CP 是把前道制造结果转成 wafer map 和 KGD 决策的风险控制节点，它决定哪些 die 值得进入昂贵封装。

## 架构师启示

如果我在架构阶段选择多 chiplet 或 HBM package，必须同时定义测试前移策略。否则模型只看到“小 die 良率更高”，却没有看到每个 package 需要多个 KGD、多个中间测试点和更复杂的失效隔离。

一个具体例子：4 个 compute chiplet 加 8 个 HBM stack 的 package，不应只按 12 个对象的 nominal 良率相乘，还要问每类对象在进入 assembly 前能否被足够筛选，哪些 defect 只能在 package 后暴露，以及暴露时损失了多少封装成本。
