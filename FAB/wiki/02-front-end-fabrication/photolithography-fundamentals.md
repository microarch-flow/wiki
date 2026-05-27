# 光刻:把版图变成芯片的核心步骤

上级:[前道工艺](./README.md)
相关:[EUV 与多重曝光:7nm 之下的两条路](./euv-and-multi-patterning.md), [Design Rule 和 PDK:架构师与工艺的接口](./design-rule-and-pdk.md), [工艺节点演化与 PPA 取舍](./process-nodes-and-ppa-tradeoffs.md)

## 这页在回答什么问题

光刻为什么是把版图转成芯片结构的核心瓶颈。重点不是光学公式，而是理解 patterning 能力如何决定设计规则、成本、良率和节点 scaling。

## 光刻在做什么

光刻的任务是把 mask 上的图形转移到 wafer 表面的 photoresist，再让后续刻蚀、离子注入、沉积或电镀只作用在指定区域。简化流程是：

```text
wafer surface prepared
  -> photoresist coating
  -> alignment to previous layer
  -> exposure through mask
  -> develop resist pattern
  -> etch / implant / deposit according to pattern
  -> strip resist and clean
```

光刻不是单独制造电路，它给后续加工定义空间边界。每一层都要和前一层对准；每一层的线宽、间距、角落、via、contact 都必须落在工艺能稳定复制的窗口内。设计规则本质上就是把这些可制造窗口翻译成设计团队可用的几何约束。

## 为什么光刻决定 scaling 节奏

当特征尺寸逼近曝光系统可稳定分辨的极限时，单次曝光很难直接得到目标图形。工程上可以通过更短波长、更高 NA、更复杂 mask、OPC/RET、多重图形化和更严格 layout rule 继续推进，但代价是成本、周期、overlay 风险和设计限制上升。

这就是为什么节点 scaling 不是“把版图缩小 0.7 倍”。若图形不能稳定制造，缩小后的版图不会带来可量产产品。光刻能力越接近极限，PDK 会给出越多限制，例如固定 track、高度受限 cell、单向金属、via enclosure、minimum spacing、coloring rule 等。

## 架构师真正关心的接口

| 光刻约束 | 传到设计侧的形式 | 架构影响 |
| --- | --- | --- |
| 最小线宽/间距 | design rule、routing pitch | 标准单元密度、BEOL routing |
| overlay 误差 | via/contact margin、enclosure | via 阻抗、良率、面积浪费 |
| 图形复杂度 | restricted design rule | layout 灵活性下降 |
| 多重图形化 | coloring、mask count、cycle time | 物理设计复杂度和成本上升 |
| 工艺窗口 | yield learning、binning spread | 节点成熟度和产品风险 |

光刻对架构的影响经常是间接的。架构师不会选择曝光剂量，却会感受到标准单元库密度、SRAM compiler 形态、routing congestion、时序收敛难度和 mask 成本。

## 常见误解

常见误解是“光刻就像打印照片，分辨率越高越好”。实际光刻是多层对准和可重复制造问题。一个图形能在实验条件下出现，不等于能在整片 wafer、数十层、数万片量产中稳定出现。

另一个误解是“只要有更短波长，设计就自由了”。更短波长会缓解部分 patterning 压力，但也引入新材料、光源、mask、resist、缺陷和设备成本问题。EUV 让先进节点减少部分多重图形化，但没有消除设计规则和良率约束。

## 一句话理解

光刻把 layout 几何变成可加工图形，它通过设计规则和 PDK 把制造极限传导到架构可行性上。

## 架构师启示

如果我看到某节点宣称更高 logic density，要追问这是否来自更 aggressive 的 standard cell、更多 restricted rule、更多 mask 和更难的 routing。密度收益如果换来物理收敛困难，最终可能被 buffer、spacing、power grid 和 timing closure 吃掉。

在早期架构估算里，不能只用理想缩放因子压面积。更稳妥的做法是把 logic、SRAM、analog/I/O 和 routing overhead 分开，因为光刻和设计规则对它们的收益不同。
