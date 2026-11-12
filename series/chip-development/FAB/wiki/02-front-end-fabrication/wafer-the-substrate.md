# 一切的起点:wafer 是什么、怎么来的

上级:[前道工艺](./README.md)
相关:[一片 wafer 到一颗成品芯片的完整路径](../01-overview/from-wafer-to-product.md), [良率与缺陷密度:从工艺到经济的桥](../03-wafer-test-and-cp/yield-and-defect-density.md), [工艺节点演化与 PPA 取舍](./process-nodes-and-ppa-tradeoffs.md)

## 这页在回答什么问题

wafer 为什么不只是“硅片”，而是整个制造、良率和成本模型的坐标系。理解 wafer 的意义，是为了把 die 面积、缺陷密度、边缘损失和测试 map 这些架构经济性问题联系起来。

## Wafer 是制造坐标系

现代主流逻辑制造以 300 mm wafer 为主要载体。前道工艺并不是一次制造一颗芯片，而是在一整片 wafer 上重复形成数十到数百甚至更多个 die。每个 die 来自同一套 mask 与工艺步骤，但因为位置、缺陷、工艺均匀性和局部图形密度不同，最终电性和良率不会完全一致。

这件事改变了架构师看 die 面积的方式。一个 die 变大，不只是单颗面积增加；它还会减少每片 wafer 上可切出的 die 数，增加边缘不可用面积比例，并提高被随机缺陷击中的概率。大 die 的成本不是线性上升，而会通过 die per wafer 和 yield 同时恶化。

## 从晶体到 wafer

wafer 的上游过程可以压成下面的对象流：

```text
high-purity silicon
  -> single-crystal ingot
  -> sliced wafers
  -> lapping / polishing
  -> cleaned prime wafer
  -> processed wafer in fab
```

对架构师而言，关键不是拉晶和抛光细节，而是 wafer 必须提供足够平整、洁净、晶向一致和低缺陷的基底。前道后续每一层图形都在这个基底上叠加，若起点平整度、颗粒、晶体缺陷或污染控制不好，后续光刻、薄膜、CMP 和器件电性都会受到影响。

## Die 面积如何进入经济模型

可以用简化关系建立直觉：

```text
good dies per wafer
  ~= dies per wafer x die yield

die yield
  falls as die area and defect density increase
```

真实良率模型会比这更复杂，但方向足够清楚：面积越大，单颗 die 包含的潜在缺陷命中区域越大；节点越先进、层数越多、工艺窗口越窄，缺陷与系统性失效管理越关键。

| 架构选择 | wafer 级后果 | 产品级影响 |
| --- | --- | --- |
| 更大 monolithic die | 每片 wafer die 数减少，随机缺陷命中概率上升 | 单颗成本和良率风险上升 |
| 切成多个 chiplet | 单 die 面积下降，前道良率改善机会增加 | 封装、D2D、KGD 和组合良率变重要 |
| 增加片上 SRAM | 面积与 Vmin/bitcell 良率压力上升 | cache/scratchpad 成本不一定随节点理想缩放 |
| 增加大规模 I/O ring | pad/bump 区域和外围结构变大 | die floorplan 与封装接口耦合 |

## Wafer map 是风险地图

CP 后会得到 wafer map：每个 die 的 pass/fail、binning、速度、漏电或其他测试分类。这个 map 对先进封装很重要，因为封装前需要决定哪些 die 能进入高价值 package。对于 3DIC 或 HBM 邻接系统，KGD 不是质量口号，而是避免把坏 die 组装进昂贵 package 的经济前提。

常见误解是把 wafer yield 看成制造团队的局部指标。实际它会反向影响架构切分：当 monolithic die 面积过大时，chiplet 可能用更复杂封装换取更好的前道良率；当 chiplet 数量过多时，组合良率和封装成本又可能抵消前道收益。

## 一句话理解

Wafer 是前道制造的批量坐标系；die 面积、缺陷密度和 wafer map 决定了架构方案的第一层成本与良率边界。

## 架构师启示

如果我在决定 800 mm² 级 monolithic die 还是多个 200 mm² 级 chiplet，wafer 视角会改变判断。前者可能省掉 D2D 与复杂封装，但会承受更差 dies-per-wafer 与 die yield；后者可能改善单 die 良率，却把问题转移到封装路线、KGD、D2D PHY 和组合良率。

因此，面积模型不应只输出 `area_mm2`，还应连接到 `dies_per_wafer`、缺陷密度假设、binning 策略和封装组合良率。没有这层模型，架构探索会系统性低估大 die 的经济风险。
