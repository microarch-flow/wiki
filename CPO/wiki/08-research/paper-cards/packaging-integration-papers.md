# 封装集成类论文卡片

上级：[论文卡片库](./README.md)

相关：[封装与集成路线](../../03-architecture-platform/packaging-routes.md)

## 这一类论文主要看什么

这一类论文关注：

- 光引擎怎样进入封装
- ASIC、driver、TIA、PIC 怎样布局
- 光纤、波导、散热结构如何协同

## 推荐优先收集的论文类型

### 类型 1：共封装布局与互连结构

记录重点：

- 光引擎摆放方式
- 电逃逸路径
- 封装平台类型

### 类型 2：耦合与组装方法

记录重点：

- 对位容差
- 耦合损耗
- 节拍与量产可行性

### 类型 3：可测试封装设计

记录重点：

- 测试点如何预留
- 如何做封装后联调

## 论文卡片槽位

### 卡片 A：`Optoelectronic Glass Substrates for Co-packaging of Optics and ASICs`

- 标题：Optoelectronic Glass Substrates for Co-packaging of Optics and ASICs
- 作者 / 单位：Lars Brusberg 等 / Corning Research & Development
- 时间：2020
- 类型：OFC 论文
- 链接：https://opg.optica.org/abstract.cfm?uri=OFC-2020-Th3I.5
- 核心问题：能否通过带集成波导和耦合结构的玻璃封装基板，为 optics 与 ASIC 共封装提供高通道数互连平台
- 关键贡献：提出了面向下一代数据中心的光电封装基板思路，把 substrate 本身也变成光互连平台的一部分
- 关键代价：它更像平台方向探索，不等于已经证明完整制造生态成熟
- 我最该记住的一句话：CPO 不只是把光引擎放进封装，连封装基板本身都可能被重新定义

### 卡片 B：`Co-Packaged Optics (CPO) Technology Full Module Test Vehicle Demonstrations`

- 标题：Co-Packaged Optics (CPO) Technology Full Module Test Vehicle Demonstrations
- 作者 / 单位：John U. Knickerbocker 等 / IBM Research
- 时间：2025
- 类型：ECTC 论文
- 链接：https://research.ibm.com/publications/co-packaged-optics-cpo-technology-full-module-test-vehicle-demonstrations
- 核心问题：如何把 PIC、polymer optical waveguide、ferrule 等做成完整 CPO 模块，并验证 reflow 与可靠性兼容性
- 关键贡献：给出了 full module test vehicle、两种装配顺序、JEDEC 可靠性应力测试，以及 50 μm pitch 接口和更小 pitch 可行性的结果
- 关键代价：证明了“模块级可行”，但不代表已经解决所有系统级散热和运维问题
- 我最该记住的一句话：真正有价值的 CPO 论文，会开始谈完整模块、装配顺序和 JEDEC 可靠性，而不是只谈单一器件

### 卡片 C：`Co-packaged optics module with single mode polymer waveguide`

- 标题：Co-packaged optics module with single mode polymer waveguide
- 作者 / 单位：Akihiro Horibe 等 / IBM Research
- 时间：2025
- 类型：IEDM 邀请报告
- 链接：https://research.ibm.com/publications/co-packaged-optics-module-with-single-mode-polymer-waveguide
- 核心问题：单模 polymer waveguide 能否支持更高 lane density、较低插损和 optics-last assembly
- 关键贡献：报告了两种 substrate 配置、机械/热机械可靠性测试，以及 `<1.2–2.0 dB` 插损和 optics-last assembly 可行性
- 关键代价：依然主要集中在封装与接口工程层，不直接回答大规模系统部署收益
- 我最该记住的一句话：封装路线一旦开始讨论 optics-last assembly，说明它在认真面对量产流程问题
