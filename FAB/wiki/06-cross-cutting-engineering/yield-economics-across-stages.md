# 良率经济学:前道、中测、封装、终测的良率累积

上级:[跨工艺共性问题](README.md)
相关:[晶圆测试与 CP](../03-wafer-test-and-cp/README.md), [KGD](../03-wafer-test-and-cp/kgd-known-good-die.md), [终测与可靠性](../05-final-test-and-reliability/README.md)

## 这页在回答什么问题

为什么先进封装的良率不能只看单颗 die 良率，而要看 die、HBM stack、interposer、assembly、中测、final test 的累积经济性。

## 良率会跨阶段相乘

一个多 die package 的最终有效良率来自多阶段叠加。前道 die 良率、CP 筛选准确性、KGD 策略、interposer/RDL 良率、assembly 良率、中间测试和 final test 都会影响最终成本。

```text
effective yield
  = die quality
  x KGD screening
  x package component yield
  x assembly yield
  x final test pass rate
```

公式不必按单一数学模型死记。关键是理解：越多高价值对象被绑定在一起，坏件越晚被发现，经济损失越大。

## 为什么 KGD 重要

KGD 的意义是避免坏 die 进入高成本封装链。2.5D 和 3DIC 中，logic die、HBM stack、interposer 或 base die 都可能是高价值对象。坏件混入后续 assembly，会浪费其他好件和工艺成本。

| 阶段 | 如果漏测会怎样 |
| --- | --- |
| CP 漏掉坏 logic die | 浪费 HBM、interposer、substrate 和 assembly |
| HBM stack 筛选不足 | 高价值 package 后段报废 |
| Interposer/RDL 问题未拦截 | 多颗好 die 被绑定到坏平台 |
| Assembly 缺陷未中测 | final test 才暴露，定位更难 |

## D2W 与 W2W 的经济性

D2W 可以先筛选 die，再逐颗贴到 wafer 或 base die 上，适合异构、高价值、不同尺寸对象。W2W 并行度高，但上下 wafer 坏点耦合更强，更适合规则、高良率结构。

选择不是只看工艺能否实现，而是看有效良率和报废成本。

## 中间测试的价值

中间测试把失效拦在 final package 之前。例如 HBM stack 完成后测试、interposer module 形成后测试、3D bonding 后检查，都可以减少高价值对象继续投入坏结构的概率。

```text
test earlier
  -> scrap cheaper object
  -> protect later high-value assembly
```

## 测试成本和漏测风险

测试也有成本。测试时间、ATE 资源、fixture、温度条件和 pattern 数量都会影响成本。工程目标不是把所有测试项塞满，而是把测试点放在报废成本跳升之前。

## 一句话理解

先进封装的良率经济学就是尽量在更早、更便宜的阶段拦住坏件，避免多个高价值 KGD 被绑定后才发现失败。

## 架构师启示

架构师定义 chiplet 数量、HBM stack 数量和 3D 堆叠方式时，也在定义组合良率。高带宽方案如果需要绑定太多高价值对象，却缺少中间测试和失效隔离，系统成本会被有效良率吞掉。
