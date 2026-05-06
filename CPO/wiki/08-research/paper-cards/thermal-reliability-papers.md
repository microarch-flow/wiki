# 热与可靠性类论文卡片

上级：[论文卡片库](./README.md)

相关：[案例：热与可靠性论文怎么读](../case-studies/thermal-reliability-paper.md)

## 这一类论文主要看什么

这一类论文通常决定你能不能把 demo 变成可部署系统。

重点问题包括：

- 高热交换 ASIC 会不会压缩光器件工作窗口
- 热循环和应力会不会破坏耦合与封装可靠性
- 失效后能否定位并隔离

## 推荐优先收集的论文类型

### 类型 1：热建模与热点控制

记录重点：

- 热源分布
- 稳态与瞬态温升
- 光器件性能漂移

### 类型 2：可靠性与寿命评估

记录重点：

- 热循环
- 老化与漂移
- 长期稳定性

### 类型 3：测试与失效诊断

记录重点：

- 测试覆盖率
- 封装后可见性
- 现场失效隔离能力

## 论文卡片槽位

### 卡片 A：`Experimental Identification of the Failure Modes and Failure Mechanisms of Fiber to Waveguide Couplings Under Cyclic Tensile Loading`

- 标题：Experimental Identification of the Failure Modes and Failure Mechanisms of Fiber to Waveguide Couplings Under Cyclic Tensile Loading
- 作者 / 单位：Assane Dione 等 / IBM
- 时间：2023
- 类型：ECTC 论文
- 链接：https://research.ibm.com/publications/experimental-identification-of-the-failure-modes-and-failure-mechanisms-of-fiber-to-waveguide-couplings-under-cyclic-tensile-loading
- 核心问题：fiber-to-waveguide attach 在循环拉伸载荷下会如何失效
- 关键贡献：把粘接、strain relief、装配选择与失效模式直接联系起来，说明光纤与波导连接不是“装上去就行”，而是长期可靠性核心
- 关键代价：它聚焦的是一类具体机械失效，不等于覆盖全部 CPO 热-机械可靠性问题
- 我最该记住的一句话：很多 CPO 风险不是带宽不够，而是 attach 结构经不起长期机械应力

### 卡片 B：`Improved connectorization of compliant polymer waveguide ribbon for silicon nanophotonics chip interfacing to optical fibers`

- 标题：Improved connectorization of compliant polymer waveguide ribbon for silicon nanophotonics chip interfacing to optical fibers
- 作者 / 单位：Yoichi Taira 等 / IBM
- 时间：2015
- 类型：ECTC 论文
- 链接：https://research.ibm.com/publications/improved-connectorization-of-compliant-polymer-waveguide-ribbon-for-silicon-nanophotonics-chip-interfacing-to-optical-fibers
- 核心问题：怎样在单模光学高精度要求和高吞吐微电子装配能力之间做工程桥接
- 关键贡献：提出利用自对准方法来缩小单模光学对位精度与常规装配能力之间的鸿沟，并强调 connectorization 的机械可靠性和可制造性
- 关键代价：这更像一块基础拼图，不能单独代表完整 CPO 系统成熟
- 我最该记住的一句话：光封装的大问题，常常藏在“如何把实验室对准变成制造流程”里

### 卡片 C：如何把热与可靠性文献读对

- 如果一篇论文只给你链路指标，不谈 attach、stress、reflow、humidity、thermal cycling，它对量产判断的帮助通常有限
- 热与可靠性文献的价值在于告诉你系统最脆弱的地方在哪里
