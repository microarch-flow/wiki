# 刻蚀、薄膜沉积、CMP:三大支柱工艺

上级:[前道工艺](./README.md)
相关:[前道工艺的整体节奏:FEOL/MOL/BEOL](./process-flow-overview.md), [光刻:把版图变成芯片的核心步骤](./photolithography-fundamentals.md), [BEOL 的金属互联:从 M0 到 redistribution](./interconnect-stack-beol.md)

## 这页在回答什么问题

光刻定义图形后，刻蚀、沉积和 CMP 如何把图形变成真实材料结构。理解这三类工艺，是为了知道为什么层数、平整度、界面和金属互联会限制 PPA 与良率。

## 三件事的分工

光刻只是告诉 wafer “哪里要加工”。真正形成结构需要三类动作：

| 工艺 | 动作 | 在芯片里形成什么 | 架构相关影响 |
| --- | --- | --- | --- |
| Etching | 去掉指定区域材料 | trench、via、gate pattern、contact opening | 尺寸控制、线边粗糙、短路/开路风险 |
| Deposition | 增加指定材料层 | dielectric、metal、barrier、gate stack | RC、漏电、界面质量、可靠性 |
| CMP | 抛光和平坦化 | 平整表面、多层堆叠基础 | overlay、后续光刻、金属厚度均匀性 |

这三件事不断循环，才形成 FEOL 器件、MOL contact 和 BEOL 金属栈。它们不是背景工艺，而是决定工艺窗口和良率的核心。

## 刻蚀: 把图形变成几何边界

刻蚀负责把 photoresist 定义的图形转移到下层材料。先进节点里，刻蚀最怕的不是“有没有挖开”，而是线宽、侧壁形状、选择比、残留、损伤和均匀性。一个 via 稍微偏小会增加电阻，偏大可能影响间距和可靠性；一条 metal trench 侧壁粗糙会影响 RC 和 electromigration。

对架构师而言，刻蚀问题会表现为设计规则和良率边界。更密的 layout、更窄的 wire、更小的 via 可以提高密度，但也会提高制造窗口压力。

## 沉积: 用材料建立电、介质和界面

沉积把绝缘层、金属层、barrier、seed、gate stack 等材料放到 wafer 上。材料选择决定电阻、电容、漏电、击穿、应力和界面可靠性。BEOL 中低 k dielectric 可以降低电容、改善延迟，但机械强度和工艺集成更脆弱；铜互联降低电阻，但需要 barrier 和可靠的填充/平坦化。

沉积对架构的影响经常通过 RC 和可靠性传导。一个高频 NoC 或宽 bus 不只消耗逻辑面积，也消耗金属资源，并受线电阻、电容、via 和 EM 约束。

## CMP: 让多层结构还能继续叠

CMP 的核心价值是平坦化。没有足够平整的表面，下一层光刻无法稳定对焦和对准，多层金属堆叠会很快失控。随着 BEOL 层数增加，CMP 从辅助步骤变成维持整个堆叠可制造性的关键。

CMP 的难点是它同时影响局部和全局。局部图形密度不同会导致 dishing、erosion 或厚度不均；全局不平整会影响后续 overlay 和金属电阻。架构师在 floorplan 中制造大面积密集 SRAM、稀疏逻辑或宽电源网时，都会间接改变图形密度和工艺均匀性需求。

## PPA 影响表

| 工艺问题 | 表现 | PPA/可靠性影响 |
| --- | --- | --- |
| Etch profile 偏差 | wire/via 尺寸偏离 | RC 漂移、短路/开路、timing variation |
| Deposition 厚度不均 | 金属/介质参数变化 | IR drop、leakage、breakdown margin |
| Barrier/界面问题 | Cu diffusion、界面弱化 | 长期可靠性和 EM 风险 |
| CMP dishing/erosion | 金属厚度局部变薄 | 电阻上升、局部热点、yield loss |
| 多层累积误差 | overlay 与平整度恶化 | 高层 routing、top metal 和 pad 风险 |

## 常见误解

常见误解是“光刻决定精度，其他步骤只是按图加工”。实际加工步骤会改变图形结果，刻蚀侧壁、沉积覆盖、CMP 平整度都会让最终结构偏离理想版图。

另一个误解是“CMP 只是磨平表面”。在先进 BEOL 中，CMP 决定后续层是否还能准确制造，也会影响金属厚度、电阻、可靠性和良率。

## 一句话理解

刻蚀定义几何边界，沉积建立材料结构，CMP 维持多层堆叠的平整性；三者共同把 layout 变成可工作的物理芯片。

## 架构师启示

如果我在 floorplan 中安排超宽 NoC、大片 SRAM 和高功耗 compute tile，制造侧看到的不只是面积，而是图形密度、金属占用、局部热和 PDN 压力。BEOL 层数和 CMP 平整度会影响这些结构是否能稳定制造。

这会改变架构探索中的面积估算方式。宏块之间的 routing channel、power grid 和 keep-out 不能都当作固定比例 overhead；当互联变宽、频率变高、功耗密度增加时，这些 overhead 会被工艺加工窗口放大。
