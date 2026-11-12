# 市场与 Workload 分析

## 前置知识

- 建议先读 [本目录 README](./README.md)。
- 建议先读 [完整芯片生命周期总览](../00_overview/01_full_lifecycle.md)。
- 成本判断可参考 [芯片项目成本结构总览](../00_overview/03_cost_structure.md)。

## 核心问题

市场与 workload 分析要回答的不是“AI 市场很大”，而是“哪一类客户、哪一组模型、哪一种部署形态，会因为你的芯片而改变采购决策”。

AI 芯片的产品定义必须从真实 [Workload](../00_overview/05_glossary.md#workload) 出发。这里的 workload 不是一个单独模型名称，而是输入尺寸、batch size、序列长度、精度、稀疏性、算子组合、内存访问模式、延迟约束、吞吐目标、并发模式和软件栈约束的组合。一个面向 LLM decode 的芯片和一个面向图像 encoder 的芯片，即使都宣称支持 INT8/FP16，也可能需要完全不同的内存层级、调度策略和片上互连。

如果早期 workload 选错，后果会在后续阶段放大。架构探索会优化错误目标，规格会写成不可验证的营销指标，RTL 会实现大量对客户无价值的功能，硅后 benchmark 也无法说服客户。

## 从市场切到工程输入

市场分析应分成四层。

第一层是客户场景。客户是在数据中心、边缘服务器、机器人、车载、消费电子还是工业设备中使用芯片。不同场景决定功耗包络、可靠性要求、软件集成方式和销售周期。数据中心客户可能更看重总拥有成本、软件生态和多机扩展；边缘客户可能更看重板级功耗、温度、长期供货和 [BOM](../00_overview/05_glossary.md#bom)。

第二层是应用任务。AI 芯片不能只说“支持 AI”。需要明确是 LLM 推理、训练、推荐、视觉、多模态、语音、传统 ML 还是混合 workload。每类任务的瓶颈不同。LLM decode 常受 memory bandwidth 和 KV cache 访问影响；prefill 更偏矩阵乘吞吐；推荐模型可能受 embedding lookup 和不规则访问影响；视觉模型可能更依赖卷积、attention、resize、后处理和 pipeline。

第三层是模型和算子。需要列出代表性模型、层类型、算子分布、shape 范围、精度策略和动态行为。对创业公司，模型集合不宜过宽。第一版芯片应选择能体现差异化、又能被软件团队稳定支持的集合，而不是追逐所有热门模型。

第四层是系统约束。芯片是否挂在 PCIe 上，是否需要 [HBM](../00_overview/05_glossary.md#hbm)，是否使用 DDR/GDDR，是否需要以太网或片间互连，host CPU 如何调度，是否支持虚拟化，多租户隔离是否必要。这些约束会影响 [SoC](../00_overview/05_glossary.md#soc) 规格，而不只是 NPU 规格。

## Workload 数据应包含什么

| 数据 | 说明 | 下游用途 |
|---|---|---|
| 模型版本 | 具体模型、参数量、结构变体 | 防止 benchmark 漂移 |
| 输入 shape 分布 | batch、sequence length、image size、token pattern | 决定 buffer 和调度 |
| 算子图 | matmul、conv、softmax、norm、activation、sampling 等 | 决定硬件功能覆盖 |
| 数据精度 | FP32、FP16、BF16、INT8、INT4、混合精度 | 决定 datapath 和累加策略 |
| 内存 trace | 权重、activation、KV cache、DMA 访问 | 决定片上 SRAM 和外部带宽 |
| 延迟和吞吐目标 | p50/p99 latency、tokens/s、QPS | 决定产品可销售指标 |
| 软件约束 | compiler、runtime、framework、kernel fusion | 决定硬件可用性 |
| 客户验收方式 | 客户 benchmark、开源 benchmark、私有模型 | 决定 validation 计划 |

这里要区分 [Verification](../00_overview/05_glossary.md#verification) 和 [Validation](../00_overview/05_glossary.md#validation)。verification 关注设计是否符合规格，validation 关注产品是否满足真实客户需求。市场和 workload 分析主要服务 validation，但它也会转化为 verification 的 test plan 和 coverage 目标。

## 工具和方法

早期可以用 Python、C++、PyTorch、ONNX、TVM、MLIR、LLVM、自研 trace 工具和性能模型。重点不是工具名称，而是数据能否闭环到架构决策。

| 类别 | 示例 | 用途 |
|---|---|---|
| 模型分析 | PyTorch profiler、TensorBoard profiler、ONNX Runtime profiling | 获取算子耗时和 shape |
| 编译器 IR | MLIR、TVM Relay/TIR、XLA HLO | 分析图优化和 kernel 映射 |
| 性能建模 | C++ model、Python simulator、SystemC、gem5 部分组件 | 估算吞吐、延迟和资源冲突 |
| 内存分析 | 自研 trace、cache simulator、DRAMSim 类工具 | 估算带宽和局部性 |
| Benchmark 管理 | MLPerf Inference、客户私有 benchmark、自研回归集 | 对齐市场指标 |

如果目标是全栈开源，workload 选择还要考虑可公开复现实验。客户私有模型可以用于商业验证，但开源芯片需要能用公开模型和脚本展示可重复的性能，否则社区无法验证你的主张。

## 角色分工

产品负责人负责定义目标客户和使用场景。系统架构师把客户语言翻译为芯片指标。编译器和 runtime 工程师判断模型能否稳定映射到硬件。架构建模工程师把 workload 转成性能模型输入。商务和销售团队收集客户验收标准。财务或运营负责人把性能目标和成本模型关联起来。

软件背景创始人可以强力参与 workload 分析，因为这里需要系统理解、模型理解和软件栈理解。但需要避免一个误区：不要只从模型代码推导硬件。真实客户的部署环境、数据形态、批处理策略、服务质量目标和运维约束，常常比论文模型更能决定芯片是否有价值。

## 关键决策点

第一个决策是目标市场是否足够窄。第一颗芯片如果同时想服务训练、推理、边缘、数据中心、视觉和 LLM，架构和软件复杂度会失控。窄不是市场小，而是第一版可验证边界清晰。

第二个决策是优化指标。[TOPS](../00_overview/05_glossary.md#tops) 容易宣传，但客户可能更关心 tokens/s/W、端到端 latency、每美元吞吐、内存容量、软件迁移成本或稳定性。如果错误优化 TOPS，可能做出利用率很低的阵列。

第三个决策是 benchmark 可信度。内部 benchmark 必须有版本、脚本、输入、精度、后处理和统计方法。否则不同团队会拿不同数字争论，规格冻结时没有共同事实基础。

第四个决策是是否支持动态 shape 和新模型。支持越灵活，硬件和编译器复杂度越高；支持越窄，产品寿命可能越短。创业公司通常应定义“硬件快路径”和“软件 fallback 路径”，而不是把所有变化都硬化到第一颗芯片里。

## 典型时长和交付物

市场与 workload 分析通常需要数周到数月，取决于客户访问深度、模型复杂度和团队已有资产。创业公司早期可以先做约 4 到 8 周的快速收敛形成第一版 workload pack，但这个范围只是项目管理量级，不是行业承诺；后续仍要在架构探索中滚动更新。

主要交付物包括 workload list、模型和输入版本、trace 数据、性能基线、客户需求假设、竞品对比、不可支持列表、benchmark 运行脚本和第一版产品指标草案。不可支持列表很重要，它明确告诉团队第一颗芯片不做什么，防止范围无限膨胀。

## 与上下游阶段的接口

上游输入来自公司战略、客户访谈、竞品分析和融资假设。下游输出进入 [规格定义](./02_spec_definition.md)、[架构探索](./03_architecture_exploration.md)、[IP 策略](./04_ip_strategy.md) 和 [工艺节点选择](./05_process_node_selection.md)。

workload 分析还会影响后续 [UVM](../00_overview/05_glossary.md#uvm) 验证、emulation 场景、硅后 bring-up benchmark 和客户 demo。如果早期没有保留可复现 trace，硅后出现性能差距时很难定位是模型变化、编译器问题、硬件瓶颈还是测量方式不同。

## 常见错误

一个常见错误是只看平均算力，不看内存访问。AI 芯片的有效性能经常受数据搬运限制，尤其是 KV cache、embedding、不规则访问和小 batch 场景。

第二个错误是把开源模型当作客户模型。开源模型适合复现实验，但客户私有模型可能有不同 shape、量化策略、后处理和服务约束。

第三个错误是忽略软件栈成熟度。硬件理论上支持某种算子，不代表编译器能稳定生成高效代码，也不代表 runtime 能在客户系统中可靠调度。

第四个错误是 benchmark 不固定。模型版本、输入数据、精度、batch size、编译器 flag 和驱动版本变化都会改变结果。芯片项目需要把 benchmark 当作工程资产管理，而不是临时脚本。

## 创业公司视角下的取舍

创业公司不应该在第一阶段追求覆盖所有 workload。更实际的策略是选择一个足够痛、足够可展示、足够可复现的目标场景。对开源 AI 芯片，建议至少保留一组公开 benchmark 和一组客户私有 benchmark。公开 benchmark 用来建立社区可信度，私有 benchmark 用来验证商业价值。

可以省钱的地方是市场研究形式、早期工具链、自动化 trace 收集和开源模型实验。不能省的是客户真实输入、benchmark 可复现性、性能模型校准和不支持范围的明确化。早期省掉这些工作，后面通常会变成架构返工或客户导入失败。

## 典型场景

某团队想做面向 LLM 推理的芯片，最初只设定“INT4 超高峰值算力”。workload 分析后发现，目标客户主要跑 7B 到 70B 模型，batch size 很小，p99 latency 很重要，KV cache 容量和带宽比峰值矩阵乘更关键。团队还发现客户需要与现有 PyTorch serving 框架集成，不能接受完全专有的软件栈。

如果团队继续按峰值 TOPS 设计，可能会做出大阵列但外部内存和调度不足，最终 demo 只能在大 batch synthetic matmul 上好看。正确调整后，团队把指标改为端到端 tokens/s/W、受支持模型列表、KV cache 策略、host 接口和编译器支持范围，并在架构探索中比较 HBM、GDDR 和 DDR 方案。

## 后续阅读

- [02_spec_definition.md](./02_spec_definition.md)
- [03_architecture_exploration.md](./03_architecture_exploration.md)
- [06_milestones_and_signoffs.md](./06_milestones_and_signoffs.md)
- [AI 芯片特有的考虑](../06_cross_cutting_topics/06_ai_chip_specific.md)

## 参考公开来源

- [MLCommons MLPerf Inference](https://mlcommons.org/benchmarks/inference/)
- [PyTorch Profiler Documentation](https://pytorch.org/tutorials/recipes/recipes/profiler_recipe.html)
- [ONNX Runtime Performance](https://onnxruntime.ai/docs/performance/)
- [Apache TVM Documentation](https://tvm.apache.org/docs/)
- [LLVM MLIR Project](https://mlir.llvm.org/)

## 内容可信度说明

- **公开信息（高可信）**：PyTorch profiler、ONNX Runtime、TVM、MLIR、MLPerf 等工具和 benchmark 体系公开存在；AI workload 需要关注算子、shape、精度和内存访问。
- **行业惯例（中可信）**：用 workload pack、trace、性能模型和 benchmark 脚本驱动架构探索；把客户 benchmark 和公开 benchmark 分开管理。
- **经验性观察（中低可信）**：创业公司第一颗芯片应缩小 workload 范围；软件背景团队容易高估模型代码代表性、低估部署和内存瓶颈。
- **不确定/需向资深工程师确认（低可信）**：具体客户验收 benchmark、私有模型分布、竞品真实性能、不同市场对 TOPS、latency、TCO 的权重。
