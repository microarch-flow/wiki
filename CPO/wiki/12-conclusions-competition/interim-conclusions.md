# 阶段性研究结论

上级：[12 研究结论与竞争观察框架](./README.md)

相关：[CPO 在解决什么问题](../01-overview/problem-statement.md)、[成本、量产与 adoption 约束](../09-supply-chain-geography/cost-yield-adoption.md)

## 结论 1：CPO 是系统瓶颈驱动，不是器件驱动

如果只从器件角度看 CPO，很容易误判它的重要性。  
更准确的理解是：

- 它首先是交换和计算系统扩展问题
- 其次才是硅光、激光器和封装问题

也就是说，决定 CPO 是否成立的第一变量，不是某个 modulator 指标，而是：

- bandwidth density
- electrical I/O power
- system scaling pressure

## 结论 2：AI / HPC 比通用网络更可能先推 CPO

原因不是 AI 更喜欢新技术，而是：

- AI factory 对网络总带宽更极端
- 系统功耗更敏感
- 机架与机群布线复杂度更高

这些场景更容易把传统 pluggable 路线逼到边界。

## 结论 3：external laser、chiplet optical I/O、polymer waveguide interface 都不是边角问题

它们之所以反复出现，是因为它们分别对应三类核心矛盾：

- external laser：热与维护
- chiplet optical I/O：系统级可集成性
- polymer waveguide / connectorization：装配与可靠性

如果一个研究或公司路线完全绕开这三类问题，通常还不够成熟。

## 结论 4：先进封装能力重要，但不是单独决定因素

很多人会把 CPO 直接看成先进封装问题，这不够准确。

更合理的理解是：

- 没有先进封装平台，CPO 很难成
- 但只有先进封装，没有平台需求和运维接受度，也很难形成主流 adoption

## 结论 5：CPO 的 adoption 速度将慢于技术想象速度

原因很直接：

- 它动了维护粒度
- 它放大了良率耦合
- 它要求更多跨公司协同
- 它的收益只在部分场景足够大

所以 CPO 大概率不是“一刀切替代 pluggable”，而是先在最痛的场景分层导入。

## 一句话总结

CPO 最应该被理解成：在 AI / HPC 驱动下，由系统 I/O 瓶颈、先进封装能力、光电器件路线和可维护性约束共同推出来的一条高复杂度集成路线。
