# 为什么必须在 wafer 阶段测试

上级:[中测:CP 阶段](./README.md)
相关:[一切的起点:wafer 是什么、怎么来的](../02-front-end-fabrication/wafer-the-substrate.md), [KGD:HBM/3DIC 时代的必要前提](./kgd-known-good-die.md), [良率经济学:前道、中测、封装、终测的良率累积](../06-cross-cutting-engineering/yield-economics-across-stages.md)

## 这页在回答什么问题

为什么 wafer 阶段就要测试，而不是等封装完成后统一 final test。核心原因是：测试越早，单次发现问题的成本越低；封装越复杂，坏 die 漏到后面的代价越高。

## Wafer sort 的经济动机

前道完成后，wafer 上同时存在好 die、坏 die、边缘风险 die、速度不同的 die 和漏电不同的 die。若不在 wafer 阶段筛选，坏 die 会继续消耗切割、贴装、基板、interposer、RDL、HBM stack、underfill、molding 和终测资源。

测试前移的经济逻辑可以写成：

```text
cost of finding defect
  wafer sort < die attach < package assembly < final test < field failure
```

越晚发现问题，报废对象越完整、价值越高。对于单 die 低成本 package，晚一点发现坏 die 的损失还可控；对于 AI/HPC 先进封装，一个坏 die 可能让整个 package 报废。

## Wafer 阶段能看到什么

CP 可以在封装前观察 die 的基本电性和可测逻辑。它能做 continuity、leakage、IDDQ/电流类测试、scan、memory BIST、repair、部分功能模式、速度/功耗初筛和 binning。它还能生成 wafer map，帮助识别随机缺陷、边缘效应、系统性工艺问题和 spatial pattern。

CP 看不到或看不全的也很重要。封装后的高速 I/O、完整热环境、package PDN、HBM 连接、板级信号路径、机械应力后行为，都需要后续测试覆盖。所以 CP 的目标不是“一次测完”，而是尽早筛掉不值得继续投资的 die。

## Wafer map 的价值

Wafer map 不只是 pass/fail 表。它是前道工艺与后道封装之间的决策接口。

| Wafer map 信息 | 决策用途 |
| --- | --- |
| pass/fail die 分布 | 决定哪些 die 可切割进入封装 |
| speed bin | 决定产品 bin 或高低频 SKU |
| leakage bin | 决定功耗 bin 或移动/服务器用途 |
| memory repair 信息 | 决定 eFuse/repair 和可用容量 |
| 空间分布 pattern | 反馈工艺异常、边缘效应和良率爬坡 |

对于 D2W 或 chiplet package，wafer map 还影响 die picking。系统会优先挑选通过测试、bin 匹配、位置合适和风险较低的 die 进入高价值 assembly。

## 为什么先进封装更依赖 wafer sort

先进封装把多个对象绑定在一起，组合良率会放大单个对象的不确定性。若每个 die 在进入 package 前都没有足够筛选，最终 package 良率会迅速下降。HBM stack 也是同样逻辑：它在进入 logic + HBM package 前，自己已经要经过多层制造和测试筛选。

常见误解是“final test 更完整，所以 wafer sort 可以简化”。实际 final test 更完整，但它发生得更晚。CP 的价值在于便宜地拦截明显坏件和风险件，保护后续封装投资；final test 的价值在于验证封装后产品规格。

## 一句话理解

Wafer sort 存在的根本原因是把坏 die 尽量拦在封装前，用较低测试成本保护后续更高价值的 package 资源。

## 架构师启示

如果我选择 D2W 3DIC 或多 chiplet 封装，就必须关心 CP 覆盖率。D2W 的优势是能先筛 KGD 再贴装；如果 CP 无法有效发现关键 defect，这个优势会缩水，组合良率会被坏 die 漏检拖垮。

一个具体决策例子：若某 chiplet 只有封装后才能测到关键高速 D2D PHY defect，那么它进入 package 前并不是真正的 KGD。架构师需要推动 DFT 或 wafer-level test access，让关键接口在封装前至少被部分覆盖。
