# 良率、缺陷密度与裸片面积

<span class="micro-legacy-anchor" id="良率与缺陷密度从工艺到经济的桥"></span>

上级：[晶圆筛测与 CP](README.md)
相关：[筛测覆盖、过杀和漏检](test-cost-vs-coverage-tradeoff.md) · [跨阶段良率与成本](../06-cross-cutting-engineering/yield-economics-across-stages.md)

## 这页在回答什么问题

哪些指标能描述裸片制造和筛选？面积与缺陷密度怎样进入良率模型？

## 良率不是单个百分比

写良率时先明确投入对象、分子、阶段、规格和时间窗。制造后真良品比例、CP 通过比例、通过品中的真良比例、封装通过比例与终测分档各有自己的判据。

**教学假设。** 1,000 个裸片进入 CP。900 个真良品全通过，100 个坏品中有 90 个被拦截。CP 通过率为 910÷1,000，即 91%。坏品检出率为 90÷100，即 90%。通过品中坏品比例为 10÷910，约 1.10%。实际测试通常无法预先知道每件产品的真实状态。例题定义它以便区分分母。 [测试成本和覆盖率](test-cost-vs-coverage-tradeoff.md)

测算跨阶段交付时，使用前一阶段进入的总体作为下一阶段的条件。使用独立的单件概率相乘时，需要验证有关独立性假设。资格鉴定结果应随报告记录样本、条件和覆盖范围，并作为放行证据使用。 [跨阶段良率与成本](../06-cross-cutting-engineering/yield-economics-across-stages.md) · [TI 资格鉴定](https://www.ti.com/en-us/quality-reliability/faqs)

## 缺陷密度与面积

在均匀随机、命中即失效且无修复的简化模型中，若一件产品上的致命缺陷数服从泊松分布，随机缺陷良率等于零次命中的概率。

**Y = exp(−D₀ × A)**

D₀ 是所计缺陷的密度，A 是相应有效敏感面积。例如采用缺陷数/cm² 和 cm²，则乘积无量纲。用整颗裸片面积代替 A 是近似。真实设计的敏感面积随层、缺陷类别、尺寸和几何布局变化。缺陷聚集、系统性失效、存储冗余及修复需要另外建模。 [Stapper，IBM 制造良率原始论文](https://bitsavers.org/pdf/ibm/IBM_Journal_of_Research_and_Development/332/ibmrd3302G.pdf)

## 为什么 chiplet 会出现

切分会减少每片裸片单独承受的缺陷面积。按相同缺陷密度和相同总敏感面积，若必须直接组装多颗独立且未经筛选的裸片，零致命缺陷概率仍是各片概率的乘积，其指数中的总面积未变。可单独筛选、异构工艺、可售分档和裸片复用会改变经济性。新增的组装、连接和测试会引入其他条件。 [KGD 的筛选判据与残余风险](kgd-known-good-die.md)

## 良率学习与架构风险

选型要读取目标工艺、批次、版图与失效模式的证据。制造和组装的相关性会改变概率估算。由量产良率分析页说明如何关联批次、复验及定位。 [量产良率分析](../../../process/04_tapeout_and_post_silicon/07_yield_analysis.md)

<span class="micro-legacy-anchor" id="常见误解"></span><span class="micro-legacy-anchor" id="架构师启示"></span>

## 一句话理解

先固定良率的对象与分母，再选择随机缺陷模型或筛选概率。用预测值做比较时，记录模型未覆盖的失效和边界条件。
