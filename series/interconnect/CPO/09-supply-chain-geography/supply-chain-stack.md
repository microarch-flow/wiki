# 供应链分层地图

上级：[09 供应链与区域格局](./README.md)

相关：[产业链与角色](../02-industry/value-chain.md)、[生态关系图与协作逻辑](../02-industry/ecosystem-relationships.md)

## 为什么要单独做这一页

前面的产业链章节已经告诉你“有哪些角色”，但如果你真的要做供应链研究，还要再往下拆一层：

- 谁控制核心芯片
- 谁控制光引擎
- 谁控制激光器
- 谁控制封装装配
- 谁控制系统集成和客户入口

这几个层级如果不拆开，供应链会看起来像一锅粥。

## 可以把 CPO 供应链拆成 8 层

### 第 1 层：需求与系统定义层

这一层决定：

- 为什么需要 CPO
- 用在什么系统
- 愿不愿意为它付出维护复杂度

典型角色：

- hyperscaler
- AI 集群运营方
- 网络设备 OEM
- 系统架构主导方

这一层握的是“问题定义权”。

## 第 2 层：交换芯片与计算互连主控层

这一层决定：

- 交换 ASIC 怎样演进
- SerDes 规模和速率怎样演进
- 封装边界和热预算怎样定义

典型角色：

- switch ASIC vendor
- high-speed interconnect platform vendor

这一层握的是“系统接口与平台主导权”。

## 第 3 层：高速电接口与辅助芯片层

这里包括：

- SerDes
- DSP
- retimer
- driver
- TIA

这一层的重要性在于，它决定 CPO 不是简单“换成光”就结束，而是电光边界附近仍然有大量高速模拟/混合信号问题。

## 第 4 层：PIC / silicon photonics / optical engine 层

这一层包括：

- PIC 平台
- silicon photonics 工艺
- modulator / detector 集成
- optical engine 设计

这一层握的是“光电转换的核心功能能力”。

## 第 5 层：laser / III-V / external light source 层

这一层经常被低估，但它很关键，因为：

- 激光器寿命和热敏感性直接影响系统架构
- external laser 方案会改变维护边界
- III-V / InP 相关能力通常不完全掌握在交换芯片方手里

这一层握的是“光源能力与可靠性约束”。

## 第 6 层：封装平台与材料层

这一层包括：

- substrate
- interposer / bridge
- polymer waveguide
- fiber attach interface
- adhesive / ferrule / connector-related materials

这一层的重要性在于：CPO 成败很大程度上取决于“封装和连接结构能不能被稳定制造”，而不是只取决于器件能不能工作。

## 第 7 层：装配、测试与良率层

这里包括：

- OSAT
- advanced packaging assembly
- alignment / coupling
- KGD
- module test
- JEDEC / reliability qualification

这一层握的是“能不能量产”的最终判断权。

## 第 8 层：整机、部署与运维层

这一层包括：

- switch system integration
- rack / cluster deployment
- field service
- spare strategy
- TCO 管理

这一层握的是“客户是否接受”的最终决定权。

## 这 8 层里谁最关键

如果只看技术突破，很多人会把注意力放在第 4 层和第 5 层。  
但如果看产业落地，真正最关键的是：

- 第 1 层：需求是否足够痛
- 第 2 层：主平台厂商是否推动
- 第 7 层：量产和可靠性是否讲得通
- 第 8 层：运维团队是否接受

## 最容易误判的地方

### 误判 1：谁会做 PIC，谁就控制了 CPO

不对。PIC 很重要，但没有平台主控和系统入口，PIC 不足以单独定义路线。

### 误判 2：谁会封装，谁就掌握了最大价值

也不完全对。封装是关键约束，但如果没有系统主导方和客户场景，封装能力不会自动转化成大规模 adoption。

### 误判 3：供应链只是上下游串联

不对。CPO 的供应链是强耦合网络，不是线性流水线。

## 一句话理解

CPO 供应链不是“芯片厂 + 光模块厂”的简单升级版，而是“系统定义层、交换平台层、光引擎层、光源层、封装测试层、运维层”共同耦合的一张多层网络。
