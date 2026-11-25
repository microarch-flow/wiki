# CPO 学习顺序导航页

上级：[学习顺序导航](README.md)

## 先选要回答的问题 {#start}

<span id="这页怎么用"></span>
<span id="如果你时间很少"></span>

第一次接触 CPO，可以先跟一个比特走。准备做器件、封装或互连研究，可以从下列工程问题直接进入。做产业调查则先辨认合作方提供哪一环，再核对公开证据。

## 第一次阅读，先指出转换发生在哪里 {#first}

<span id="路径-a只想先快速建立整体概念"></span>

1. [沿一个比特走完整条电光链路](../04-optical-engine/optical-link-basics.md)。在图上指出哪段高速电连接缩短了，从一根光纤的四个波长中找出一路，再算这一路的余量。
2. [CPO 在解决什么问题](../01-overview/problem-statement.md)。在端口数和线速相同的条件下，检查哪些系统指标可能变化。
3. [CPO 与相邻概念](../01-overview/taxonomy.md)。分别给一项设计标出引擎位置、光源位置和工艺。需要快速回顾各类问题时，使用[一页版总览](../13-one-page-summary/cpo-one-page.md)。

## 做工程分析，按系统边界选下一站 {#engineering}

<span id="路径-b想系统学习技术与工程逻辑"></span>

- **画数据和供光路径。** [系统栈](../03-architecture-platform/system-stack.md)说明 SerDes、光源、光引擎和可选重定时器的位置；回到[光引擎](../04-optical-engine/optical-link-basics.md#modulation)可看驱动电压如何控制光功率。
- **遇到误码。** 先在[预算参考面](../04-optical-engine/optical-link-basics.md#budget)核对同一波长的收发规格，再到[测试与故障定位](../05-electrical-thermal-reliability/reliability-test.md)区分光路、电路和装配问题。有关电采样窗口的先修见[电路到时序](../../../microarchitecture/02-pipeline/electrical-timing-foundations.md)。
- **评估是否能量产或维修。** 查看[功耗与热](../05-electrical-thermal-reliability/bandwidth-power-thermal.md)、[制造流程](../06-manufacturing/process-flow.md)和[已知良品与装配良率](../06-manufacturing/known-good-die-and-yield.md)。判断一个失效部件会连带更换什么，取决于封装和维修边界。

## 读论文时怎样保留可复核的证据 {#papers}

<span id="路径-c想按论文把-cpo-学透"></span>

从[十篇入门文献](../08-research/reading-pack-cpo-top-10.md)或[四天阅读计划](../08-research/4-day-study-plan.md)选择主题。[完整论文卡](../08-research/detailed-cards/README.md)举例说明如何分析论证；[论文短卡库](../08-research/paper-cards/README.md)便于按器件、封装、功耗与热查找材料。

## 查行业与公司时从谁开始 {#industry}

<span id="路径-d想重点理解产业链供应链和公司生态"></span>

[产业角色](../02-industry/value-chain.md)和[供应链分层](../09-supply-chain-geography/supply-chain-stack.md)先说明各方提供什么，再用[区域分布](../09-supply-chain-geography/regional-landscape.md)、[合作关系](../10-company-ecosystem/partnership-map.md)、[公司深卡](../11-deep-company-cards/README.md)和[平台与部件的风险](../12-conclusions-competition/winners-components-risks.md)核实具体项目。[来源表](../18-sources-and-updates/company-ecosystem-sources.md)记录公司与合作信息的出处。

<span id="路径-e想重点看中国大陆机会"></span>

关注中国大陆时，按[已有位置](../15-china-opportunities/china-position.md)、[机会环节](../15-china-opportunities/opportunity-areas.md)、[约束条件](../15-china-opportunities/constraints.md)、[跟踪方法](../15-china-opportunities/how-to-track-china.md)阅读，可依次查产品、测试与客户资格证据。

## 对比两种方案时，要固定什么？ {#boundaries}

<span id="一句话总结"></span>

光引擎缩短高速电连接以后，计算整端功耗要包括 SerDes、驱动、激光、接收放大及有关温控。封装是否能稳定对位、测试是否能定位故障、现场要换哪个单元，都影响最终成本。比较可插拔与共封装设计，应先固定两边的净速率、距离、环境和可维护性要求。不同系统可以给出不同的选择。[系统收益与代价](../01-overview/problem-statement.md) · [采用条件与限制](../07-applications-economics/adoption-barriers.md)

<span id="如果你想把它讲给别人听"></span>

做汇报可用[一页版总览](../13-one-page-summary/cpo-one-page.md)、[研究汇报模板](../17-report-template/cpo-report-template.md)和[术语索引](../14-indexes/term-index.md)。需要说明商业进展时，用[阶段性结论](../12-conclusions-competition/interim-conclusions.md)和[商用证据比较方法](../12-conclusions-competition/who-scales-first.md)区分已确认事项和待检验假设。
