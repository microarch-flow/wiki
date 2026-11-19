# CDC 与 RDC

## 前置知识

先明确各接口的发送时钟、接收时钟与复位域。[微架构设计](02_microarchitecture_design.md)给出定义入口。

## 为什么跨域问题危险

异步时钟之间没有固定相位关系。信号在接收寄存器的采样窗口内变化，寄存器可能进入亚稳态。同步器给亚稳态更多恢复时间。实际失效率受单元、频率、翻转率和物理实现影响。多个信号分别同步时，还可能在不同接收周期稳定。 [AMD 同步器失效率说明](https://docs.amd.com/r/en-US/ug949-vivado-design-methodology/Optimizing-for-MTBF)

## 常见 CDC 场景

| 输入与要求 | 可选结构 | 要检查的条件 |
| --- | --- | --- |
| 低速单比特电平 | 目的域同步链 | 电平保持足够久。检查恢复时间及后端实现 |
| 脉冲或单个事件 | 受约束的脉冲同步、翻转或请求／应答 | 事件间隔、两端复位、目的时钟是否继续 |
| 低速多比特配置 | 数据保持与请求／应答 | 采样前数据稳定，直到返回确认 |
| 连续多比特事务 | 异步 FIFO | 读写域满空条件、突发、反压、指针跨域和复位 |

逐位同步数据总线会丢失同一事务的一致性。灰码指针属于特定结构。接收端可跳过中间指针值，物理偏斜仍需保证相邻源端更新的变化在传输中不会被混合。 [Intel 双时钟 FIFO 实现约束](https://www.intel.com/content/www/us/en/docs/programmable/683241/24-3/user-configurable-timing-constraint.html)

## 亚稳态、同步器和 Async FIFO

同步链降低亚稳态传播概率。同步级数、单元和布局由目标平台、可靠性和延迟要求决定。异步 FIFO 用读写指针和占用边界控制访问。确定深度时检查突发量、生产与消费速率和反压可达性。若生产率能无限期大于消费率，任何有限深度都需要反压或明确丢弃规则。

## RDC 特有问题

即使两个模块使用同一个时钟，若源寄存器异步复位，输出也可以在目的寄存器采样窗口中变化。目的域仍可运行时，应检查源复位是否经隔离、同步或协议控制。异步断言、同步释放是一种局部复位策略。域间还需定义复位顺序、在途事务和重新可用条件。 [Accellera CDC/RDC 1.0](https://accellera.org/images/downloads/standards/cdc/CDC_Standard_v1.0.pdf)

## CDC/RDC 工具流程

输入包括时钟、复位及其关系、IP 接口模型、低功耗状态和跨域约束。工具识别越域、重汇合、复位传播及预期结构。人工复核功能协议和规则豁免。标准化的 CDC/RDC 描述可用于 IP 到 SoC 的交接。

## 与 STA 的关系

同步相关时钟仍按其关系检查。异步路径不按固定相位计算普通 setup 和 hold。根据同步拓扑，还可能需要最大数据延迟或总线偏斜检查。核对例外命中的路径、约束优先关系及同步链后级的时序。 [Intel 跨域路径约束](https://www.intel.com/content/www/us/en/docs/programmable/683243/25-1/constraining-cdc-paths.html)

<span class="micro-legacy-anchor" id="agent-生成-rtl-的跨域风险"></span><span class="micro-legacy-anchor" id="创业公司视角"></span>

## 典型场景

**教学假设。** 目的域理想采样时刻为 0 ns 和 10 ns。源域的完成位在 2 ns 和 5 ns 各翻转一次。两次采样都是旧值，接收端可能丢掉两个事件。给普通翻转同步器增加同步级数仍需满足事件间隔。商业宏也有专用的间隔和复位要求。 [AMD 脉冲同步宏的输入条件](https://docs.amd.com/r/en-US/pg382-xpm-cdc-generator/XPM_CDC_PULSE)

在[SRAM＋DMA 规格](../01_product_definition_and_architecture/02_spec_definition.md#典型场景)中，完成状态保持到目的端确认。源端收到跨域返回的确认后，才释放事务槽。复位按规格清除该握手的状态，并在两端初始化完成后重新接收。若下一代需要多个完成事件在途，需用有容量与反压定义的队列等结构承载。

## 角色、节奏、成本与接口

RTL 负责人记录每个跨域的结构和协议。验证人员检查复位及反压的边界。STA 和物理实现人员复核对应约束和布局。下游交付记录应包含域定义、已检查路径、例外及依据，以及 IP 核验的版本。

## 后续阅读

- [低功耗设计](07_low_power_design.md)
- [前端交接评审](08_signoff_criteria.md)
- [静态时序分析](../03_backend_physical_design/05_static_timing_analysis.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** 同步链、脉冲宏、FIFO 跨域约束及 IP 抽象边界见所列资料。
- **教学假设。** 0、2、5、10 ns 仅为采样反例。DMA 握手受指定复位和在途条件约束。
- **待项目核实。** 实际可接受失效率、时钟变化范围、约束语法和例外范围。
