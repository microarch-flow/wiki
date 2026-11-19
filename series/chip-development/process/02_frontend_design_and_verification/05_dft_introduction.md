# 可测性设计（DFT）与制造测试

<span class="micro-legacy-anchor" id="dft-引入"></span>

## 前置知识

先了解[综合准备需要哪些输入与检查](04_synthesis_preparation.md)。实际制造测试可继续读[晶圆筛测与 KGD](../../FAB/wiki/03-wafer-test-and-cp/README.md)和[成品终测](../../FAB/wiki/05-final-test-and-reliability/final-test-methodology.md)。

## DFT 解决什么问题

生产测试需要在有限时间、引脚和设备条件下控制芯片，并观察与物理缺陷有关的响应。DFT 在设计中提供测试访问、内部控制和观测结构。测试工程根据测试目标与接受条件，在晶圆或封装件上执行筛选和分档。 [OpenROAD DFT 模块](https://openroad.readthedocs.io/en/latest/main/openroad/dft/README.html) · [OCP 多芯粒测试](https://www.opencompute.org/documents/chiplet-integration-workflows-1-pdf)

## 常见 DFT 结构

| 结构 | 作用和边界 |
| --- | --- |
| Scan chain | 测试模式下移入状态，捕获响应，再移出供比较 |
| Scan compression | 压缩测试数据或响应。有效性和测试功耗需结合网表及向量检查 |
| MBIST | 用测试控制器对存储宏运行规定的访问序列。若有修复结构，还需验证配置、执行及复测 |
| LBIST | 使用片内逻辑生成激励并压缩响应，按设计目标和覆盖分析安排使用 |
| 测试访问端口和边界扫描 | 通过规定接口访问测试数据。边界扫描可检查板级连接，核内仪器访问还需对应网络及协议 |
| Test point | 在难控制或难观察的位置提供额外测试访问，增加面积和约束 |

测试访问端口、边界扫描和 IJTAG 的标准描述不同层次。是否通过同一个端口访问，取决于芯片的实现和测试模式。 [IEEE 1149.1 范围](https://standards.ieee.org/ieee/1149.1/4484/) · [IEEE 1687 项目资料](https://standards.ieee.org/ieee/1687/10896/)

## 为什么 DFT 要早介入

封装引脚、测试时钟、电源岛和存储宏接口在设计阶段确定。DFT 团队据此规划访问和测试模式。Scan 单元替换、链连接与重排可跨越综合和布局步骤。链或网表变化后，应重新验证相关向量、时序和测试条件。OpenROAD 给出一种放置前替换、放置后建链的流程实例。 [OpenROAD DFT 流程](https://openroad.readthedocs.io/en/latest/main/openroad/dft/README.html)

## RTL 对 DFT 的影响

明确可控的复位、测试时钟、测试模式和低功耗状态。为存储宏准备测试接口。触发器、隔离和时钟门控在测试模式下应有清楚的控制规则。功能模式与测试模式各自验证，特别检查测试电流和对正常访问的隔离。

## ATPG、覆盖率和成本

ATPG 是生成测试向量的活动。输入包括可测网表、测试时钟与模式、约束及故障模型。输出包括向量和故障分类报告。测试工程根据设备和封装访问条件将向量转换、验证并部署。 [Synopsys TestMAX ATPG](https://www.synopsys.com/implementation-and-signoff/test-automation/testmax-atpg.html)

报告应写清楚故障模型、纳入分母的故障、如何处理不可测故障以及被检测的数量。故障模型覆盖率衡量向量对该模型的效果。晶圆筛选通过率和漏检率根据实际测试总体和判据计算。 [筛选分母和过杀](../../FAB/wiki/03-wafer-test-and-cp/test-cost-vs-coverage-tradeoff.md)

## DFT 与低功耗、后端和封测

晶圆筛测可使用已规划的探针访问、结构测试和存储测试。封装后还能覆盖组装引入的问题及实际封装接口。多芯粒产品可能需要封装内再测芯粒、测 D2D 连线或在中间工序做筛选。要把同一故障的检测位置、可访问边界和测试条件一起评审。 [OCP 多芯粒测试](https://www.opencompute.org/documents/chiplet-integration-workflows-1-pdf)

## 角色、节奏、成本与接口

DFT 组向 RTL、后端和测试组交付时钟、复位、电源和端口的测试约束，以及结构、向量与覆盖信息。测试组向设计和质量组返回失败日志和诊断条件。量产前应检查设备资源、工装、测试时长、并测、功耗与判据。

<span class="micro-legacy-anchor" id="创业公司视角"></span>

## 典型场景

**教学假设。** DMA 算例使用一个 SRAM 宏。功能验证向 DMA 发请求并比较内存数据。生产测试可以通过 MBIST 单独访问该宏，按故障模型和宏支持条件筛查。若宏处于可关断的电源域，要逐项验证在测试模式下的供电、时钟和访问能力。

## 后续阅读

- [晶圆测试与 CP](../../FAB/wiki/03-wafer-test-and-cp/README.md)
- [KGD 的筛选判据与残余风险](../../FAB/wiki/03-wafer-test-and-cp/kgd-known-good-die.md)
- [成品终测](../../FAB/wiki/05-final-test-and-reliability/final-test-methodology.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** 扫描结构、ATPG 和多芯粒测试流程可参考所列工具文档与产业白皮书。
- **行业做法。** DFT 交付物和生产测试工序以设计和产品目标为准。
- **教学假设。** SRAM 的访问与电源条件用于说明设计和生产检查的边界。
- **待项目核实。** 故障模型、覆盖目标、限值、引脚访问和测试合同。
