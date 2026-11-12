# 微架构设计

## 前置知识

- 建议先读 [产品规格定义](../01_product_definition_and_architecture/02_spec_definition.md)。
- 建议先读 [架构探索](../01_product_definition_and_architecture/03_architecture_exploration.md)。
- 建议先读 [RTL 设计工程实践](./01_rtl_design_practices.md)。
- 术语准备：[Architecture](../00_overview/05_glossary.md#architecture)、[Microarchitecture](../00_overview/05_glossary.md#microarchitecture)、[NoC](../00_overview/05_glossary.md#noc)、[SRAM Compiler](../00_overview/05_glossary.md#sram-compiler)。

## 架构和微架构的区别

[Architecture](../00_overview/05_glossary.md#architecture) 定义芯片对软件、客户和系统呈现什么能力，例如指令集、编程模型、内存一致性、数据精度和外部接口。[Microarchitecture](../00_overview/05_glossary.md#microarchitecture) 定义这些能力如何用硬件实现，例如 pipeline 级数、队列深度、仲裁策略、buffer 组织、SRAM 端口、状态机、时钟域和错误处理。

软件背景的人常把微架构看成“实现细节”，但在芯片里很多“细节”会决定能不能 tapeout。一个没有定义清楚的 FIFO 深度、仲裁优先级或 SRAM 读写冲突语义，可能导致性能模型失真、RTL 重写、验证空间爆炸或后端时序失败。

## 微架构规格应该包含什么

一份可执行的微架构规格至少包含：

| 内容 | 要回答的问题 |
|---|---|
| 模块边界 | 哪些模块存在，谁负责什么状态 |
| 时钟和复位 | 每个模块在哪个 clock/reset domain |
| 数据路径 | 数据每拍如何流动，pipeline latency 是多少 |
| 控制路径 | 任务如何启动、暂停、取消、完成、报错 |
| buffer/queue | 深度、满空、读写冲突、backpressure |
| 仲裁 | 多请求同时到达时优先级和公平性 |
| 寄存器模型 | 软件可见配置、状态、计数器和 side effect |
| 异常行为 | 非法配置、ECC 错误、timeout、overflow |
| 性能假设 | 峰值、瓶颈、stall 原因、利用率测量 |
| 验证映射 | 每条需求如何被 test/assertion/coverage 覆盖 |
| 后端约束 | macro 位置假设、关键路径、时钟频率目标 |
| DFT/Debug | scan、MBIST、JTAG、trace、性能计数器需求 |

微架构规格不是论文式文档，而是 RTL 和验证共同执行的合同。每一处“未定义”最终都会变成工程争议。

## 从 C Model 到 cycle-aware 模型

[C Model](../00_overview/05_glossary.md#c-model) 通常先保证功能正确。进入微架构阶段后，需要补充 cycle-aware 或 transaction-level 模型。它不一定要精确到每根线，但要表达 latency、throughput、resource conflict、queue occupancy、memory bandwidth、backpressure 和调度策略。

对 AI 芯片，功能模型能告诉你矩阵乘结果是否正确，但不能告诉你 tile scheduler 是否会饿死某类任务、SRAM bank conflict 是否让利用率下降、DMA burst 和 compute pipeline 是否互相堵塞、NoC 拥塞是否导致尾延迟恶化、小 batch decode 是否被启动开销吞掉。如果没有 cycle-aware 反馈，RTL 团队可能在实现一个性能上不可达的架构。

## Pipeline、Buffer 和 SRAM

Pipeline 是微架构最基本的结构。关键决策包括级数、每级功能、寄存器切分、stall/flush 机制、异常传播和 valid bit 语义。深 pipeline 有利于高频，但增加 latency、控制复杂度和验证成本；浅 pipeline 简单，但可能达不到频率。

先进节点下，逻辑延迟不再是唯一限制，长线、扇出、macro 距离和拥塞也会影响时序。因此 pipeline 切分不能只看 RTL 表达式复杂度，还要听后端 early feedback。例如一个大 crossbar 在 RTL 看起来只是 mux，物理上可能是跨区域长线和高功耗热点。

AI 芯片通常被片上存储和数据搬运限制。微架构必须定义每个 buffer 的作用：吸收突发、解耦生产消费、复用权重、保存中间激活、跨时钟同步或隐藏外部内存延迟。使用 [SRAM Compiler](../00_overview/05_glossary.md#sram-compiler) 生成 memory macro 时，要尽早确认容量、位宽、端口数、读延迟、byte write、ECC、banking 和物理尺寸。多端口 SRAM 面积和功耗昂贵，很多“方便的”多读多写结构在真实工艺上不可接受。

## 仲裁、寄存器和软件契约

仲裁器决定共享资源如何分配。简单 fixed priority 容易验证、面积小，但可能饿死低优先级请求。round-robin 更公平，但状态更多。QoS 和 deadline-aware 仲裁更接近系统需求，但验证复杂度明显增加。仲裁策略必须和性能模型一致，不要在 C model 中假设理想带宽，RTL 中才发现 DMA、compute、debug、firmware 都要争同一 NoC port。

寄存器不是后期随手加的 debug 接口，而是硬件和软件的 ABI。必须定义地址、字段、reset value、读写权限、write-one-to-clear、read side effect、保留位、错误码、中断、doorbell 和性能计数器。建议用 SystemRDL、IP-XACT、PeakRDL 或内部 schema 生成寄存器 RTL、C header、文档和验证模型。手写寄存器容易出现 RTL、软件头文件和文档不一致。

## 角色、时长和评审

微架构由架构师、RTL lead、验证 lead、编译器/runtime、DFT、后端/STA 顾问共同评审。Block 级微架构通常需要数周到数月；SoC 级微架构会在 RTL 和验证阶段持续迭代。具体时长取决于模块规模、IP 复用程度、目标频率和团队经验。

评审不应只看框图。每个关键模块要有时序图、状态图、队列行为、异常流程、寄存器说明、关键路径猜测、验证点和 rejected alternatives。评审常问：是否存在不受控组合路径；reset 后能否进入稳定 idle；backpressure 会不会形成死锁；buffer 深度依据是什么；哪些行为架构可见，哪些只是实现选择；性能不达标时是否有可调参数或 ECO 空间。

## 典型场景

某 NPU tile 支持矩阵乘和 elementwise fusion。架构模型假设权重从 SRAM 连续读取，MAC 阵列每拍满载。微架构评审发现 SRAM macro 只有一读一写端口，而同一拍需要读权重、读 activation、写 partial sum。若强行实现，会导致复制 SRAM 或降低频率。

团队改成多 bank 结构，并在 scheduler 中加入 bank conflict 规避。C model 增加 bank-aware 模拟，验证计划增加随机 shape 和 bank conflict coverage。这个修改降低峰值宣传指标，但让 RTL、后端和真实 workload 性能更可信。

## 创业公司视角

创业公司可以简化文档形式，但不能跳过微架构思考。建议每个模块至少有一页“硬件合同”：接口、时序、状态、异常、reset、coverage、owner。Agent 可以从这份合同生成 RTL 和 test skeleton，但合同本身必须由资深 RTL/架构/验证工程师共同评审。

第一颗芯片少做过度参数化。参数化看起来利于复用，但每个参数组合都扩大验证空间。除非 generator 和验证基础设施很强，否则应冻结少量可验证配置。

## 后续阅读

- [RTL 设计工程实践](./01_rtl_design_practices.md)
- [前端验证方法学](./03_verification_methodology.md)
- [CDC 与 RDC](./06_cdc_and_rdc.md)
- [前端签核标准](./08_signoff_criteria.md)

## 参考公开来源

- [Accellera IP-XACT](https://accellera.com/downloads/standards)
- [Accellera SystemRDL](https://accellera.com/downloads/standards)
- [IEEE 1800-2023 SystemVerilog 标准页面](https://standards.ieee.org/standard/1800-2023.html)

## 内容可信度说明

- **公开信息（高可信）**：IP-XACT、SystemRDL、SystemVerilog 等标准可公开查证；SRAM compiler、NoC、寄存器模型是 SoC 微架构常见组成。
- **行业惯例（中可信）**：微架构规格包含模块边界、pipeline、buffer、仲裁、寄存器、异常、验证映射和后端约束；评审需要 RTL、验证、后端、软件共同参与。
- **经验性观察（中低可信）**：第一颗芯片应控制参数化和动态调度复杂度；AI 芯片常被数据搬运和 bank conflict 限制，而不是只被 MAC 数量限制。
- **不确定/需向资深工程师确认（低可信）**：具体 SRAM macro 选择、NoC 拓扑、仲裁策略、pipeline 级数和后端反馈阈值需要结合 PDK、目标频率和 workload 确认。
