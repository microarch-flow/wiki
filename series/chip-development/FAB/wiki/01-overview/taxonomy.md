# 工艺节点、封装路线、测试阶段的命名体系

上级:[芯片制造与封测 Wiki 总览](./README.md)
相关:[前道与后道:产业分工和技术差异](./front-end-vs-back-end.md), [先进封装分类框架:2D/2.5D/3D](../04-back-end-packaging/packaging-taxonomy.md), [高频问题:最容易混淆的概念](../08-reference/high-frequency-questions.md)

## 这页在回答什么问题

工艺节点、FEOL/BEOL、2.5D/3D、TSV、Hybrid Bonding、CP、Final Test 这些词分别属于哪一层命名体系。目标是先把分类维度拆开，避免把结构、材料、连接工艺、制造组织方式和厂商平台名混为一谈。

## 工艺节点不是几何尺寸

`7nm`、`5nm`、`3nm` 这类节点名已经不是某个单一晶体管尺寸的直接测量值，而是工艺平台代际名称。节点真正影响架构的是标准单元密度、SRAM bitcell 缩放、频率/电压空间、漏电、金属栈、设计规则、成本和良率成熟度。

因此，节点选择不能只按数字大小排序。一个先进节点可能给逻辑密度和能效带来收益，但 SRAM 不一定同比缩小，模拟/I/O 也可能不适合迁移。架构师更应该把节点看成一组 PPA、设计规则、IP 可用性和经济性的组合，而不是“越小越好”的线性等级。

## 制造阶段命名

| 名称 | 层级 | 含义 | 容易混淆点 |
| --- | --- | --- | --- |
| FEOL | die 内 | 晶体管本体形成 | 不是封装前段 |
| MOL | die 内 | transistor 到局部互联的连接 | 常被简化进 FEOL/BEOL |
| BEOL | die 内 | 金属互联层形成 | 和封装后道不是一回事 |
| Wafer sort / CP | 测试 | wafer 阶段探针测试 | 不是 final test |
| Assembly / packaging | die 外 | die 到 package 的组装 | 不只是外壳保护 |
| Final test | 测试 | package 后测试与 binning | 不能替代 CP |
| Reliability qualification | 认证 | 寿命、应力、环境验证 | 不等于普通功能测试 |

这个命名体系的价值在于定位问题。若 NoC 路径时序收敛困难，先看 BEOL、floorplan 和时钟；若 HBM 连接良率不稳，问题更可能在 KGD、interposer/RDL、bump/bonding 或 package assembly；若出货后温度循环失效，问题可能在材料界面、CTE mismatch 或 bump fatigue。

## 封装结构命名

封装分类首先看 die 如何摆放。

| 分类 | 结构直觉 | 典型目标 | 主要代价 |
| --- | --- | --- | --- |
| 2D | 单 die 或多 die 在 package/substrate 上平面连接 | 成本、成熟度、通用产品 | 带宽密度和距离受限 |
| 2.5D | 多个 die 并排放在高密度中介平台上 | logic + HBM、多 chiplet | interposer/RDL/bridge 成本与良率 |
| 3D | die 垂直堆叠 | 更高带宽密度、更短互连、更小 footprint | 热、bonding、测试、良率耦合 |

`2.5D` 不是比 `3D` 落后一代，而是不同目标函数。logic die 与 HBM 并排集成时，2.5D 往往是更现实的系统最优解，因为它在带宽密度、散热、测试和良率之间取得平衡。3D 可以进一步缩短互连，但会显著增强热与良率耦合。

## 中间载体命名

另一条维度是 die 之间靠什么载体连接。

| 载体 | 作用 | 典型场景 |
| --- | --- | --- |
| Organic substrate | package 级支撑、供电、板级引出 | 传统封装、大多数 package |
| Silicon interposer | 高密度硅中介层，可含 TSV | logic + HBM 2.5D |
| RDL interposer / fan-out RDL | polymer dielectric + Cu RDL 重布线 | fan-out、多 die、较大平台扩展 |
| Embedded bridge | 局部硅桥提供高密度 D2D | chiplet 局部高带宽 |
| Glass substrate / glass core | 更平整、更大尺寸潜力的平台材料方向 | 未来大尺寸高密度 package |

载体分类不能和 2D/2.5D/3D 混成一层。Silicon interposer 常用于 2.5D，但“用了 silicon”不等于 3D；RDL 可以用于 fan-out，也可以成为 2.5D RDL interposer；embedded bridge 是局部高密度能力，不是缩小版 full interposer。

## 连接工艺命名

| 工艺 | 解决的问题 | 不是 |
| --- | --- | --- |
| C4 / solder bump | die 到 substrate 或 package 的成熟互连 | 不是高密度 3D 连接的上限方案 |
| Micro-bump | 细 pitch die-to-die / die-to-interposer 连接 | 不是 Hybrid Bonding 的同义词 |
| Hybrid Bonding | Cu-Cu + dielectric 直接键合 | 不是“更小的 bump”，因为没有 solder bump |
| TSV | 硅内垂直通孔 | 不是 3DIC 的定义本身 |
| RDL | 重布线层 | 不是只属于 fan-out，也可服务 interposer/bridge |

常见混淆是把 TSV 当成 3DIC，把 Hybrid Bonding 当成 micro-bump 的缩小版，把 RDL 当成几根封装铜线。更准确的说法是：TSV 是垂直通路能力，Hybrid Bonding 是直接键合机制，RDL 是封装级重布线平台。

## 制造组织方式命名

3DIC 里还要区分 W2W、D2W、WoW、CoW 这类制造组织方式。它们回答的是“两个对象以 wafer 还是 die 的形态进行对准和键合”，不是回答“这是 2.5D 还是 3D”。

W2W/WoW 适合规则、尺寸匹配、良率足够高的 wafer-to-wafer 堆叠，吞吐和对准一致性有优势，但坏 die 容易随整片绑定进入组合。D2W/CoW 可以先筛选 KGD，再把 die 贴到 wafer 上，更适合异构 die 和高价值组合，但 throughput、对位和 handling 更复杂。

## 平台名是商品名，不是分类法

CoWoS、InFO、SoIC、EMIB、Foveros、I-Cube、X-Cube、FOCoS 这类名字是厂商平台或商品名。它们有技术含义，但不能替代底层分类。分析平台时应先拆成四个问题：

```text
die 怎么摆: 2D / 2.5D / 3D
中间靠什么: substrate / silicon interposer / RDL / bridge
连接怎么做: bump / micro-bump / hybrid bonding / TSV
制造怎么组织: W2W / D2W / chip-first / chip-last
```

这样做可以避免把平台名背成分类法。例如 CoWoS-S、CoWoS-R、CoWoS-L 都属于 CoWoS 家族，但中间载体分别偏 silicon interposer、RDL interposer、RDL + local silicon interconnect；它们对应的是不同 trade-off，而不是同一技术的简单版本号。

## 一句话理解

正确的命名顺序是先分清结构、载体、连接工艺和制造组织方式，再把厂商平台名映射到这些底层维度上。

## 架构师启示

如果我在评估一个 chiplet 方案，不能只写“采用先进封装”。我至少要明确：这是 2.5D 并排还是 3D 堆叠；靠 silicon interposer、RDL 还是 embedded bridge；连接是 micro-bump 还是 Hybrid Bonding；KGD 和测试流程如何组织。每一项都会改变带宽密度、功耗、热、良率、成本和供应链选择。

一个具体例子：若目标只是两个 compute chiplet 间数百 GB/s 级互连，embedded bridge 或 RDL 可能已经足够；若目标是多个 HBM stack 与大 compute die 的 TB/s 级聚合带宽，full silicon interposer 或 CoWoS 类平台更可能进入候选；若目标是 logic-on-logic 超短距离互连，Hybrid Bonding 和 3DIC 才成为核心问题。
