# 良率与缺陷密度:从工艺到经济的桥

上级:[中测:CP 阶段](./README.md)
相关:[一切的起点:wafer 是什么、怎么来的](../02-front-end-fabrication/wafer-the-substrate.md), [工艺节点演化与 PPA 取舍](../02-front-end-fabrication/process-nodes-and-ppa-tradeoffs.md), [良率经济学:前道、中测、封装、终测的良率累积](../06-cross-cutting-engineering/yield-economics-across-stages.md)

## 这页在回答什么问题

缺陷密度如何把 die 面积、工艺成熟度和封装复杂度转成产品经济性。架构师不需要做 fab 良率工程，但需要理解为什么大 die、先进节点和多 die package 会把良率变成架构问题。

## 良率不是单个百分比

芯片产品的良率是多阶段结果。前道有 wafer/die 良率，CP 有筛选覆盖率，封装有 assembly 良率，final test 有产品规格通过率，可靠性还有寿命筛选和认证风险。

各阶段可使用条件概率计算合格品占投入品的比例，但先要定义总体与判定。例如单 die 流程中，`P(最终为真良品且通过全部筛测) = P(前道真良品) × P(CP通过 | 真良品) × P(组装成功 | 前述条件) × P(终测通过 | 前述条件)`。每一项都以此前条件为前提；若使用无条件良率直接相乘，则需要额外的独立性假设。多 die 场景还要定义输入 KGD 的数量、相关性及报废口径。

筛测通过率不是筛测后的纯度。假设投入 1000 个 die，其中 900 个真良品全部通过，100 个坏品中检出 90 个：共 910 个通过，其中仍有 10 个坏品。通过品中的漏检比例为 `10/910 ≈ 1.10%`；每投入 die 得到真良品的比例为 `900/1000 = 90%`；坏品检出率为 `90/100 = 90%`。此例没有过杀。指标与分母详见[测试成本和覆盖率](test-cost-vs-coverage-tradeoff.md)。

可靠性资格试验的置信度是对规定条件下证据的统计描述，不是逐件制造良率，不能当成一个额外良率因子相乘。先进封装中坏件越晚被发现，通常损失越大。

## 缺陷密度与面积

随机缺陷模型的直觉是：die 面积越大，被缺陷击中的概率越高；缺陷密度越高，良率越低。简化泊松模型常写成：

```text
yield ~= exp(-D0 x A)
```

其中 `D0` 是缺陷密度，`A` 是 die 面积。真实量产会使用更复杂模型，并考虑缺陷聚集、系统性失效、冗余、repair 和工艺学习，但这个简化式足以解释为什么大 die 会有良率压力。

## 为什么 chiplet 会出现

Chiplet 的一个动机是把一个超大 die 切成多个较小 die，降低每个 die 被随机缺陷击中的概率，同时允许不同功能使用不同节点。这个收益不是免费的，因为 package 需要把多个 die 重新连接起来，并引入 D2D、KGD、封装良率和测试复杂度。

| 方案 | 良率收益 | 新增风险 |
| --- | --- | --- |
| Monolithic die | 无 D2D/复杂封装，系统内部连接最直接 | 大面积 die 前道良率差、reticle/成本压力 |
| Chiplet | 单 die 面积下降，异构节点更灵活 | KGD、D2D、封装 assembly、组合良率 |
| 3DIC | 更短互连、更高带宽密度 | bonding、热、测试不可达、stack 良率 |
| HBM package | 外存带宽密度大幅提高 | HBM stack、interposer/RDL、热和测试成本 |

## 良率学习与架构风险

工艺成熟度会随着量产学习改善。早期节点缺陷密度和参数分布更不稳定，成熟节点更可预测。架构师选择前沿节点时，不只是选择 PPA 上限，也在选择良率爬坡风险和产品 schedule 风险。

多 die 封装也有类似学习曲线。即使每个 die 前道良率不错，assembly 中的 bump、bonding、underfill、warpage、interposer/RDL defect 都会影响最终良率。良率学习需要可观测性；如果失效在 stack 内部且难以定位，学习速度会变慢。

## 常见误解

常见误解是“chiplet 一定提高良率”。只有当小 die 前道良率收益大于封装、D2D、KGD 和组合良率代价时，chiplet 才会提高产品经济性。

另一个误解是“良率只是制造问题”。实际良率受架构选择影响：die 面积、macro 数量、SRAM repair、接口数量、HBM stack 数量、封装路线和测试可达性都会改变有效良率。

## 一句话理解

良率是架构选择和制造现实之间的经济桥梁；die 面积、缺陷密度、封装对象数量和测试覆盖率共同决定最终产品成本。

## 架构师启示

如果我比较一个 700 mm² 单 die 与四个 180 mm² chiplet，不能只说 chiplet die 更小所以良率更好。必须把每个 chiplet 的 KGD 概率、D2D link 良率、interposer/RDL 良率、assembly 良率和 final test escape 都纳入总模型。

一个具体决策例子：若某 chiplet 切分方案减少了前道报废，但把 D2D link 数量翻倍，并要求更大 interposer，那么良率收益可能被封装风险吃掉。架构探索应输出 total cost/yield，而不是只输出 die area。
