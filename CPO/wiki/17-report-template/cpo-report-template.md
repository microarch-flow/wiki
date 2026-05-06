# CPO 研究汇报模板

上级：[17 研究汇报模板](./README.md)

相关：[CPO 一页版总览](../13-one-page-summary/cpo-one-page.md)、[阶段性研究结论](../12-conclusions-competition/interim-conclusions.md)

## 用法说明

这不是固定 PPT，而是一套“讲 CPO 时最不容易跑偏”的结构。

你可以把它用于：

- 10 分钟快速汇报
- 30 分钟内部分享
- 研究 memo
- 投资/战略初判

## 版本 A：10 分钟快速汇报

### 1. 一句话定义

`CPO 是把高速 I/O 的光电转换从模块级前移到封装级，以缓解高带宽系统中的电链路功耗和密度瓶颈。`

### 2. 为什么现在重要

- AI / HPC 对网络带宽和能效的要求更极端
- pluggable 路线在部分高端场景逼近边界

### 3. 它的核心价值

- 更高带宽密度
- 更短高速电通道
- 潜在更优系统能效

### 4. 它的核心代价

- 热
- 测试
- 良率
- 维护复杂度

### 5. 结论

- CPO 不会一刀切替代 pluggable
- 更可能先在 AI / HPC 高端场景落地

## 版本 B：30 分钟内部分享

建议按 8 页讲：

### 第 1 页：定义与问题

讲：

- CPO 是什么
- 它和 pluggable / NPO 的关系

参考页：

- [CPO 一页版总览](../13-one-page-summary/cpo-one-page.md)
- [CPO 分类框架](../01-overview/taxonomy.md)

### 第 2 页：为什么现在重要

讲：

- AI / HPC 驱动
- bandwidth density
- electrical I/O power

参考页：

- [CPO 在解决什么问题](../01-overview/problem-statement.md)

### 第 3 页：系统与技术主线

讲：

- external laser
- optical I/O chiplet
- silicon photonics
- advanced packaging

参考页：

- [系统栈与接口位置](../03-architecture-platform/system-stack.md)
- [路线索引表](../14-indexes/route-index.md)

### 第 4 页：工程难点

讲：

- 热
- 测试
- 良率
- reliability

参考页：

- [带宽、功耗与热](../05-electrical-thermal-reliability/bandwidth-power-thermal.md)
- [测试、可靠性与失效定位](../05-electrical-thermal-reliability/reliability-test.md)

### 第 5 页：供应链结构

讲：

- 平台方
- optical engine / PIC
- laser
- packaging / assembly / test
- system integration

参考页：

- [供应链分层地图](../09-supply-chain-geography/supply-chain-stack.md)

### 第 6 页：重点公司和生态

讲：

- Broadcom
- NVIDIA
- Cisco
- Ayar Labs
- AMD

参考页：

- [合作关系图](../10-company-ecosystem/partnership-map.md)
- [重点公司深卡](../11-deep-company-cards/README.md)

### 第 7 页：竞争判断

讲：

- 谁最可能先落地
- 哪条路线更像主线
- 谁更像平台赢家，谁更像关键拼图

参考页：

- [谁最可能先规模化落地](../12-conclusions-competition/who-scales-first.md)
- [平台赢家、关键拼图与风险点](../12-conclusions-competition/winners-components-risks.md)

### 第 8 页：结论与跟踪框架

讲：

- 当前判断
- 未来 1 到 2 年看什么信号

参考页：

- [如何持续跟踪 CPO 竞争格局](../12-conclusions-competition/how-to-track.md)

## 版本 C：研究 memo 模板

可以直接按下面结构写：

### 1. 结论先行

- 我对 CPO 的核心判断是什么
- 它更像中短期主题，还是长期方向

### 2. 问题定义

- CPO 在解决什么
- 为什么今天比过去更重要

### 3. 技术与工程判断

- 技术主线是什么
- 工程难点是什么

### 4. 产业链与公司判断

- 谁控制平台
- 谁是关键拼图
- 谁最值得跟踪

### 5. 风险

- adoption
- yield
- reliability
- serviceability

### 6. 观察指标

- 下一季度或下一年该看什么

## 做汇报时最常见的错误

### 错误 1：把 CPO 讲成单纯光通信升级

不对。它首先是系统 I/O 架构变化。

### 错误 2：只讲技术优势，不讲维护和良率

不对。这样结论会失真。

### 错误 3：只讲公司名，不讲它们控制哪一段

不对。会变成新闻罗列。

## 一句话总结

一份好的 CPO 汇报，不是把技术术语堆满，而是把“为什么需要、为什么难、谁最可能先做成、接下来该看什么”讲清楚。
