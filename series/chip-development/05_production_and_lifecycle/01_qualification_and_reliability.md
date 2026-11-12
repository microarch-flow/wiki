# Qualification and Reliability：可靠性认证

## 前置知识

- 建议先读 [Characterization](../04_tapeout_and_post_silicon/06_characterization.md)。
- 建议先读 [Yield Analysis](../04_tapeout_and_post_silicon/07_yield_analysis.md)。
- 建议理解 [Qualification](../00_overview/05_glossary.md#qualification)、[Reliability](../00_overview/05_glossary.md#reliability)、[HTOL](../00_overview/05_glossary.md#htol)、[ESD](../00_overview/05_glossary.md#esd)、[Latch-up](../00_overview/05_glossary.md#latch-up)、[JEDEC](../00_overview/05_glossary.md#jedec)。

## 核心概念

Qualification 是证明某个芯片、封装、工艺和制造流程组合适合进入目标市场的证据集合。Reliability 是芯片在温度、电压、湿度、机械应力、电气应力和长期使用下维持功能的能力。两者不是“测一次没坏就行”，而是用受控 stress test 暴露潜在失效机制，并定义产品可出货边界。

常见参考体系包括 JEDEC JESD47 的集成电路 stress-test-driven qualification 思路，以及汽车领域的 AEC-Q100。消费级 AI 加速器不一定需要汽车级要求，但客户，尤其是云厂商、服务器厂商和工业客户，通常会要求明确的可靠性数据、变更通知机制和失效分析流程。

## 关键活动顺序

第一步是定义 qualification plan。质量和产品工程团队根据目标市场、封装、工艺节点、工作电压、温度范围、使用寿命和客户要求，选择测试项目、样本量、lot 覆盖和 pass/fail 标准。这个计划必须在量产前完成，而不是客户问起时临时补。

第二步是准备 qualification lots。样品通常要覆盖代表性 wafer lot、封装 lot 和测试流程。只拿一小批表现最好的实验样品去做 stress test，不能代表量产风险。AI 芯片如果有大 die、先进封装或 HBM/高速接口，还要特别关注封装翘曲、热循环、underfill、micro-bump、SerDes margin 和散热路径。

第三步是执行 stress tests。常见项目包括 HTOL、temperature cycling、high temperature storage、unbiased/bias HAST、ESD、latch-up、electromigration 相关评估、package moisture sensitivity、board-level 或 system-level 可靠性测试。不同市场的组合不同，具体要求应由质量工程师和客户质量团队确认。

从工程目的看，HTOL 主要暴露长期工作寿命和电压/温度加速下的器件退化；temperature cycling 关注封装、焊点、材料热膨胀不匹配；HAST/湿热关注封装密封、腐蚀和潮湿环境；ESD/latch-up 关注制造、运输和使用中的电气冲击；package moisture sensitivity 关注回流焊和吸湿导致的分层/爆米花风险。典型测试持续时间从小时、天到千小时量级不等，具体由标准、客户要求和加速模型决定。release gate 不应只看“全部 pass”，还要看样本 lot 代表性、deviation、FA 结论和是否需要客户 waiver。

第四步是分析结果和失效。失败不是简单判定“不合格”，而是要做 failure analysis：确认是设计缺陷、工艺波动、封装问题、测试误判、ESD damage、板级应力还是操作失误。常用手段包括 curve trace、X-ray、SAT、decap、SEM、FIB、emission microscopy、ATE retest 和 scan diagnosis。

第五步是 release 或 requalification。如果测试通过，质量团队发布 qualification report，产品工程更新 datasheet、test limits 和出货条件。如果设计、工艺、封装、assembly site、test flow 或关键材料发生变化，可能需要 partial 或 full requalification。

## 典型工具和设备

可靠性测试会用到温箱、湿热箱、HTOL board、burn-in 系统、ESD/latch-up tester、thermal cycling chamber、HAST chamber、ATE、curve tracer、X-ray、SAM/SAT、SEM/FIB、ATE data analysis 平台和质量管理系统。软件侧常见的是 JMP、Spotfire、YieldHUB、PDF Solutions Exensio、内部数据仓库或 Python/R 分析脚本。

创业公司不一定购买完整实验室设备。可行方式是使用第三方 reliability lab 和 failure analysis lab，但内部必须有人能定义测试计划、解释结果并决定是否接受风险。

## 角色、周期和成本

主要角色包括 quality/reliability engineer、product engineer、test engineer、package engineer、foundry/OSAT interface、failure analysis engineer、program manager 和客户质量接口。系统软件团队也应参与，因为很多 AI 芯片的 stress 或系统级可靠性需要运行 workload、firmware、driver 和 thermal policy。

周期通常是数周到数月量级，取决于测试项目和 stress 时长。成本包括样品、socket/board、实验室服务费、工程人力、ATE 时间、FA 分析、retest 和潜在的设计修改。先进节点和先进封装的可靠性成本更高，因为样品本身昂贵、失效机制更多、分析难度更大。

量级上，早期商业级芯片的第三方可靠性测试和基础 FA 可以从数万美元到数十万美元量级起步；复杂封装、汽车级/工业级要求、大量样本、多轮 requalification 或高端 FA 可能进入更高量级。这里不能用固定数字预算，因为样本量、测试矩阵、封装、客户要求和失败重测次数会强烈改变成本。创业公司至少要在项目预算里单独列出 qual/FA reserve，而不是把它塞进“实验杂费”。

## 关键决策点

第一个决策是 qualification scope。消费、数据中心、工业、汽车的要求不同。过度 qualification 会拖慢首版产品并消耗现金；不足 qualification 会在客户现场暴露问题。

第二个决策是 pass/fail 的商业含义。某个 stress test 出现少量 failure，可能是测试夹具问题，也可能是系统性失效苗头。创业公司不能让销售压力直接覆盖质量判断，应建立 failure review board。

第三个决策是 requalification 门槛。更换 OSAT、封装基板、underfill、test site、wafer fab site、IP revision 或 metal ECO 都可能改变可靠性风险。是否需要重新认证，必须在变更前确认。

## 上下游接口

上游来自 [post-silicon characterization](../04_tapeout_and_post_silicon/06_characterization.md)、[yield analysis](../04_tapeout_and_post_silicon/07_yield_analysis.md)、封装规格、test limits 和客户需求。下游输出是 qualification report、reliability derating、datasheet 条件、production release 决策、客户质量材料和量产监控计划。

如果 characterization 还没有稳定，qualification 计划会失真。例如电压/频率表后来改了，HTOL stress 条件可能需要重做；封装热阻估错，温度 stress 可能没有覆盖真实使用场景。

## 典型场景

一个 AI 推理芯片完成首硅 bring-up 后，在 0-70C 商用温度范围内跑通 benchmark。团队计划给服务器客户送样。质量团队要求先完成代表性 lot 的 HTOL、temperature cycling、ESD/latch-up、package moisture sensitivity 和 board-level thermal cycling。测试中发现高温高压下某个 SRAM BIST fail rate 升高。后续 FA 发现不是 SRAM bitcell 问题，而是某个电源域在 stress board 上 IR drop 偏大。最终团队修正 stress board 设计，并增加量产 test 中的电源监控项。

如果团队跳过这一步，客户现场可能在高温机柜里出现间歇性故障，问题难以复现，RMA 成本和客户信任损失会远高于前期测试成本。

最终 release 决策材料通常应包含 qualification report、stress 条件和样本表、failure/deviation 清单、FA summary、test limit 版本、datasheet 条件、客户 waiver 或内部 risk acceptance。没有这些材料，量产批准只是口头判断。

## 创业公司取舍

可以省的是自建完整可靠性实验室。早期可以外包 stress test、FA 和部分质量文档准备。不能省的是内部质量 owner、变更控制、样品追溯、测试条件定义和失败解释能力。没有内部 owner，外包实验室只能给测试结果，不能替你判断产品是否能卖。

第一颗芯片应避免承诺超出能力的市场。比如如果团队没有汽车质量体系，不应轻易把产品定位为车规；如果目标是数据中心，则应优先准备长期负载、热管理、PCIe/网络稳定性、firmware recoverability 和系统级 RAS 证据。

## 常见坑

- 把 qualification 当成客户材料包装，而不是真实风险发现机制。
- 只测裸芯片功能，不覆盖封装、板级、散热和系统软件组合。
- 没有 requalification 规则，后续换供应商或改材料时引入隐性风险。
- stress test 条件和 datasheet 条件不一致，导致报告无法支持产品声明。
- 失败样品没有保存和追溯，FA 无法复盘。

## 后续阅读

- [量产爬坡](./02_volume_ramp.md)
- [供应链](./03_supply_chain.md)
- [现场支持](./04_field_support.md)

## 参考公开来源

- [JEDEC JESD47 standard page](https://www.jedec.org/standards-documents/docs/jesd47)
- [AEC-Q100 overview by Renesas](https://www.renesas.com/en/products/automotive-products/aec-q100)
- [Texas Instruments reliability testing overview](https://www.ti.com/quality-reliability/reliability/testing.html)

## 内容可信度说明

- **公开信息（高可信）**：JEDEC/AEC qualification 思路、HTOL、temperature cycling、ESD、latch-up、HAST 等可靠性测试类别。
- **行业惯例（中可信）**：qualification plan、representative lot、failure analysis、release gate 和 requalification 的工程流程。
- **经验性观察（中低可信）**：创业公司应外包实验室能力但保留内部质量判断权。
- **不确定/需向资深工程师确认（低可信）**：具体样本量、stress 条件、客户接受标准和不同 foundry/OSAT 对变更的 requalification 要求。
