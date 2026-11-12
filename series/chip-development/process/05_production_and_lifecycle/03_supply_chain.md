# Supply Chain：供应链

## 前置知识

- 建议先读 [Foundry Relationships](../06_cross_cutting_topics/02_foundry_relationships.md)。
- 建议先读 [Packaging](../04_tapeout_and_post_silicon/03_packaging.md) 和 [Volume Ramp](./02_volume_ramp.md)。
- 建议理解 [Foundry](../00_overview/05_glossary.md#foundry)、[OSAT](../00_overview/05_glossary.md#osat)、[Wafer Start](../00_overview/05_glossary.md#wafer-start)、[Lead Time](../00_overview/05_glossary.md#lead-time)、[PCN](../00_overview/05_glossary.md#pcn)、[Traceability](../00_overview/05_glossary.md#traceability)。

## 核心概念

芯片供应链不是“下单制造”这么简单。它包含 wafer fab、mask、probe、dicing、package substrate、assembly、final test、burn-in、reliability lab、failure analysis、物流、库存、分销、客户质量和变更通知。每个环节都有 lead time、产能约束、质量风险和商业条款。

AI 芯片供应链尤其复杂，因为产品往往 die 大、功耗高、封装要求高、基板层数多、可能依赖 HBM 或高速 SerDes，且客户通常要求稳定供货和长期软件支持。架构团队如果在产品定义阶段没有考虑封装和供应链，后期会被 cost、capacity 和良率反向约束。

## 关键活动顺序

第一步是供应链架构设计。团队要决定 foundry、工艺节点、封装类型、OSAT、ATE 平台、基板供应商、散热方案、物流模式和是否使用 turnkey 服务。这个选择应在 [工艺节点选择](../01_product_definition_and_architecture/05_process_node_selection.md) 和 [IP 策略](../01_product_definition_and_architecture/04_ip_strategy.md) 阶段就开始，而不是 tapeout 后。

第二步是供应商导入。需要 NDA、技术评估、报价、产能讨论、质量协议、数据接口、工程联系人、变更流程和付款条款。Foundry/OSAT 不只是 vendor，更像长期生产伙伴。创业公司信用弱，通常需要通过投资人、设计服务公司、IP vendor 或已有关系获得入口。

第三步是物料和产能计划。供应链团队把客户 forecast 转化为 wafer start、mask、substrate、package materials、ATE slot、socket/probe card、库存和物流计划。先进封装和高层基板的 lead time 可能很长，缺一个小物料就会让整批产品延迟。

第四步是生产执行和追溯。每颗芯片应能追溯到 wafer lot、wafer number、die location、package lot、test program version、bin、date code 和出货客户。没有追溯，现场问题会扩大成全批次不确定风险。

第五步是供应风险管理。包括 second source、buffer stock、capacity reservation、end-of-life notice、export control、地缘风险、质量异常、供应商财务健康和突发停产。创业公司不一定能做完整冗余，但必须知道自己的单点故障在哪里。

## 工具和系统

常用系统包括 PLM、ERP、MES、QMS、供应商 portal、forecast/APS 工具、库存系统、RMA 系统和数据仓库。小团队早期可以用更轻量的数据库和流程表，但字段必须设计正确：part number、revision、lot、wafer、package lot、test program、firmware/compiler 版本、customer shipment 和 PCN 状态。

具体产品名举例：ERP 常见 SAP、Oracle NetSuite、Oracle Fusion；PLM/QMS 可见 Arena、Oracle Agile PLM、Siemens Teamcenter、MasterControl；MES/制造执行可能是 Siemens Opcenter/Camstar 或供应商自有系统；客户和支持侧可能使用 Salesforce、Zendesk、ServiceNow、Jira；供应风险和料号情报可参考 SiliconExpert、IHS/ S&P Global 等服务。早期不必全买，但数据模型要能迁移到这些系统。

工程数据和运营数据必须打通。比如一个 field failure 需要从客户序列号追到 package lot，再追到 wafer map 和 CP/FT 结果；如果系统软件版本也影响问题复现，还要追到 driver、firmware 和 compiler release。

## 角色、周期和成本

主要角色包括 operations lead、supply chain manager、foundry interface、OSAT interface、test operations、quality engineer、product engineer、finance、legal 和 sales operations。早期创业公司常由 CTO 或硬件负责人兼任供应链决策，但执行层面仍需要有经验的人建立流程。

供应链周期通常以数周到数月计，先进节点 wafer、先进封装基板和 HBM 可能更长。成本包括 wafer、mask amortization、封装、测试、基板、socket/probe card、物流、保险、关税、库存资金占用、报废和供应商 NRE。先进 AI 芯片的封装和测试成本可能成为单位成本的重要部分。

量级上，成熟封装和标准测试的单位成本可能在可控范围内，但先进封装、高层基板、HBM、复杂 socket/load board、长 test time 会把 NRE 和单位成本显著抬高。供应链预算还要准备数月库存和在制品现金占用；对创业公司，库存不是会计小项，而是直接影响 runway 的现金支出。

## 关键决策点

第一个决策是 turnkey vs 自己管理供应链。Turnkey 可以降低协调难度，适合缺经验团队；缺点是透明度、议价能力和问题定位能力下降。关键产品不应完全依赖黑盒 turnkey。

第二个决策是单一供应商还是双源。先进节点和先进封装通常难以真正 second source，因为 PDK、IP、封装工艺和测试平台耦合强。成熟封装、基板、物流和部分测试服务更容易做备选。

第三个决策是库存策略。过低库存会断供，过高库存会占用现金并承担 revision 过期风险。芯片库存和软件库存不同，已经封装测试的芯片如果遇到硬件 bug 或客户需求变化，可能无法简单“升级”。

第四个决策是变更控制。更换材料、site、测试程序、封装版本、firmware 或 datasheet 条件都可能需要 PCN 或客户批准。为了省成本偷偷改流程，是严重质量风险。

第五个决策是合规和地区风险。AI 芯片可能受到出口管制、客户地区限制、先进封装/HBM allocation、EDA/IP license 地域条款和供应商安全审查影响。创业公司不能只问“技术能不能做”，还要问“能不能合法卖、能不能持续供、客户是否允许导入”。

## 上下游接口

上游是产品定义、工艺节点、封装、test program、qualification 和客户需求。下游是 volume ramp、客户交付、现场支持、RMA 和 EOL。供应链还会反向影响架构：如果高带宽内存供应不稳定，架构路线可能需要调整；如果封装基板成本过高，产品价格模型可能不成立。

## 典型场景

一家公司设计了依赖 HBM 的 AI 训练芯片，性能指标很强，但 tapeout 后才发现 HBM allocation、interposer、CoWoS/2.5D 封装产能和高层基板 lead time 都需要提前锁定。结果硅片可用但无法按客户窗口交付系统。这个错误不是 RTL 错，而是产品定义阶段没有把供应链当架构约束。

另一个常见场景是使用某 OSAT 的封装流程通过 pilot build，但量产时基板供应商切换了材料批次，导致高温下 warpage 增加，final test fail 上升。如果没有 lot traceability 和 PCN 流程，团队会误以为是随机良率波动。

## 创业公司取舍

可以外包执行，但不能放弃供应链可见性。创业公司至少要掌握 BOM、关键供应商、lead time、capacity commitment、质量协议、追溯字段、PCN 流程和成本模型。对于第一颗芯片，选择成熟封装和可获得的供应链往往比追求理论最优封装更务实。

如果你的战略是“快速迭代芯片”，供应链要支持小批量、可重复、可追溯的迭代，而不是只追求最低大批量单价。MPW、shuttle、turnkey、成熟封装和标准 ATE 平台可能比极限先进封装更符合 V1。

## 常见坑

- 只和 foundry 谈 wafer，不提前锁定 OSAT、基板和 ATE。
- 客户 forecast 不分 commit 和 upside，导致产能和库存判断失真。
- 没有 PCN 流程，供应商小改动造成客户质量争议。
- 版本命名混乱，silicon revision、package revision、board revision、firmware version 和 compiler version 对不上。
- 只看单价，不看 lead time、良率、报废、现金占用和现场质量成本。

## 后续阅读

- [量产爬坡](./02_volume_ramp.md)
- [现场支持](./04_field_support.md)
- [Turnkey Services](../06_cross_cutting_topics/05_turnkey_services.md)

## 参考公开来源

- [SEMI T26 supply-chain traceability description](https://store-us.semi.org/products/t02600-semi-t26-specification-for-electronic-supply-chain-traceability-using-distributed-ledger-technology-3)
- [TSMC Open Innovation Platform overview](https://www.tsmc.com/english/dedicatedFoundry/oip)
- [ASE technology services overview](https://www.aseglobal.com/en/technology)

## 内容可信度说明

- **公开信息（高可信）**：foundry、OSAT、wafer start、lead time、traceability、PCN 和供应链基本结构。
- **行业惯例（中可信）**：供应商导入、产能计划、lot traceability、turnkey 取舍和变更控制流程。
- **经验性观察（中低可信）**：AI 芯片创业公司常低估基板、封装、HBM、ATE 和库存对交付能力的影响。
- **不确定/需向资深工程师确认（低可信）**：具体供应商价格、allocation 条款、地缘合规要求、客户质量协议和第二供应源可行性。
