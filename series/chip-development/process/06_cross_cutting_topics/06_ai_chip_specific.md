# AI Chip Specific：AI 芯片特有考虑

## 前置知识

- 建议先读 [Workload Analysis](../01_product_definition_and_architecture/01_market_and_workload_analysis.md)。
- 建议先读 [Architecture Exploration](../01_product_definition_and_architecture/03_architecture_exploration.md)。
- 建议理解 [Workload](../00_overview/05_glossary.md#workload)、[TOPS](../00_overview/05_glossary.md#tops)、[NPU](../00_overview/05_glossary.md#npu)、[NoC](../00_overview/05_glossary.md#noc)、[HBM](../00_overview/05_glossary.md#hbm)。

## 核心概念

AI 芯片不是一个大矩阵乘法器。可销售产品由 workload coverage、编译器、runtime、memory hierarchy、NoC、DMA、host interface、power/thermal、封装、系统软件、开发者体验和客户部署共同决定。峰值 TOPS 是必要但远不充分的指标。

AI workload 变化快，模型结构、精度、batch、sequence length、KV cache、稀疏性、MoE、算子融合和内存访问模式会持续变化。芯片硬件一旦流片就很难改变，因此架构必须在固定硬件和变化软件之间找到可编程性边界。

## 关键活动顺序

第一步是 workload 定义。明确目标是云推理、边缘推理、训练、推荐、视觉、LLM decode、prefill、batch offline 还是实时低延迟。每类场景的瓶颈不同，不能用一个 TOPS 指标覆盖。

第二步是软件栈先行。需要 compiler IR、operator coverage、quantization、scheduler、runtime、driver、firmware、debug tools、profiling tools 和 model zoo。没有软件栈，客户无法使用硬件。

第三步是 memory/system co-design。AI 芯片常被 memory bandwidth、SRAM 容量、NoC 拥塞、DMA overlap、host-device transfer 和 cache/KV cache 策略限制。算力阵列设计必须和数据搬运一起评估。

第四步是 power/thermal/package co-design。AI 芯片高功耗、高电流、高带宽，封装、电源、散热和板级设计会约束可持续性能。数据中心客户关心的是 sustained performance per watt，而不是短时间峰值。

第五步是系统验证。除了 RTL/UVM，还要做 compiler correctness、numerical accuracy、long-running workload、multi-card、PCIe/CXL/Ethernet、thermal throttling、RAS、firmware recovery 和客户模型验证。

## 工具和基础设施

架构探索可用 C++/Python simulator、SystemC、gem5、Timeloop/Accelergy、内部 trace simulator、TVM/MLIR/LLVM 相关工具、PyTorch/TensorFlow/ONNX workload trace。RTL/验证和后端仍使用常规 EDA。系统软件需要 profiler、debugger、benchmark harness、CI farm、model regression 和 telemetry。

AI 芯片团队还需要数据集和模型管理。benchmark 不能只跑公开小模型，应覆盖目标客户模型的 shape、precision、batch、sequence、sparsity 和部署约束。客户模型往往受保密限制，因此需要安全的数据接入和脱敏流程。

## 角色、周期和成本

角色包括 AI architect、compiler engineer、runtime/driver/firmware、ML framework engineer、RTL/verification、NoC/memory architect、package/thermal、system validation、FAE 和 product。AI 芯片的组织风险在于硬件和软件各自优化局部目标，最后产品不可用。

周期上，软件栈必须早于硅片成熟。编译器和 runtime 如果等首硅回来再开发，会浪费样片窗口。架构模拟和 compiler prototype 应在 RTL 大规模实现前启动；driver/firmware/bring-up 软件应在 tapeout 前准备；客户模型 regression 和 profiler 需要贯穿硅后和量产。

成本包括硬件 NRE、软件团队、模型适配、benchmark infrastructure、系统验证集群、开发板、客户支持和长期软件维护。对 AI 芯片公司，软件团队成本不是附属项，而是核心 NRE。成本主导项通常包括：持续的软件/编译器团队、系统验证服务器或加速卡集群、开发板和整机、客户模型适配、HBM/先进封装/基板、功耗散热方案和 FAE 支持。HBM/先进封装不仅提高单颗成本，还会带来 allocation、良率、封装周期和现金流风险。

## 关键决策点

第一个决策是目标 workload 范围。支持所有模型等于支持不了任何模型。第一颗芯片应选择清晰的主战场，并定义不支持什么。

第二个决策是可编程性 vs 专用化。越专用，PPA 越好但适应模型变化越差；越通用，软件灵活但硬件效率下降。创业公司要用客户价值而不是技术偏好做选择。

第三个决策是 HBM/先进封装。HBM 提供带宽，但带来成本、供应、封装、良率和散热风险。第一颗芯片是否用 HBM，应由 workload 和资金决定，不应只为了对标高端 GPU。

第四个决策是开源软件栈。开源 compiler/runtime 能提高采用和 debug 效率，但需要维护能力和文档质量。只开源 RTL 而软件闭源，AI 客户通常仍难以评估。

第五个决策是多芯片扩展。AI 产品常需要 scale-out，涉及 PCIe/CXL/Ethernet、collective、调度、容错和机柜散热。V1 如果完全不考虑系统扩展，后续产品定位会受限。

CXL 不是“多一个接口”这么简单。它要求主机平台、协议 IP、验证环境、软件栈、内存一致性/语义、生态成熟度和客户系统支持。对 V1，PCIe 或以太网方案可能更现实；是否上 CXL 应由目标客户系统和时间窗口决定。

## 上下游接口

上游输入是市场和 workload，输出到架构、RTL、验证、后端和封装。硅后和量产阶段的性能、功耗、温度、客户模型和软件 bug 会反向影响下一版架构。AI 芯片的产品迭代不是单纯 silicon revision，而是 silicon + compiler + runtime + system 的共同迭代。

## 典型场景

团队设计一个 INT8 峰值 TOPS 很高的推理芯片，但客户主要跑 LLM decode，瓶颈在 KV cache、memory bandwidth、low batch latency 和算子调度。结果峰值算力利用率很低。正确做法是在产品定义阶段用客户 workload trace 驱动架构，评估 end-to-end latency、tokens/s、功耗和软件适配，而不是只比较矩阵乘峰值。

另一个场景是硬件支持某稀疏格式，但 compiler 无法稳定生成高效代码，客户模型也不匹配。硬件特性没有软件闭环，就只是面积和验证成本。

如果 AI 芯片决策错误，后果会跨越全流程。架构阶段选错 workload，RTL 和后端越努力只会把错误产品做得更完整；软件栈滞后，首硅 bring-up 会变成硬件 demo 而不是客户验证；封装和散热低估，实验室峰值性能无法在机柜持续；客户模型覆盖不足，销售承诺会变成 FAE 和编译器团队的长期债务。

## 创业公司取舍

第一颗 AI 芯片应避免“想做小 NVIDIA”。务实策略是选择一个高价值、边界清楚、软件可控的 workload，做出稳定端到端体验。快速迭代可以体现在模型 trace -> 架构模拟 -> RTL 生成 -> 验证 -> 编译器回归的闭环，而不是承诺几个月内量产复杂先进节点高端芯片。

## 常见坑

- 用 TOPS 代替真实 workload 指标。
- 硬件先行，软件栈滞后。
- SRAM/NoC/DMA/host interface 低估，算力阵列空转。
- 忽略 thermal throttling，demo 性能无法持续。
- 编译器 workaround 没有进入验证和客户文档。
- 客户模型变化后，硬件缺乏可编程余量。

## 后续阅读

- [Workload Analysis](../01_product_definition_and_architecture/01_market_and_workload_analysis.md)
- [Architecture Exploration](../01_product_definition_and_architecture/03_architecture_exploration.md)
- [Fast Iteration Realities](../07_for_software_background_founders/05_fast_iteration_realities.md)
- [Open Source Silicon](./03_open_source_silicon.md)

## 参考公开来源

- [MLIR project](https://mlir.llvm.org/)
- [TVM documentation](https://tvm.apache.org/docs/)
- [OpenXLA project](https://openxla.org/)
- [NVIDIA TensorRT documentation](https://docs.nvidia.com/deeplearning/tensorrt/)

## 内容可信度说明

- **公开信息（高可信）**：AI workload、compiler/runtime、HBM、NoC、memory bandwidth、thermal 和 TOPS 局限的基本概念。
- **行业惯例（中可信）**：workload-driven architecture、software-first validation、system-level benchmarking 和 AI 芯片软硬协同。
- **经验性观察（中低可信）**：第一颗 AI 芯片应选择窄而清晰的 workload，而不是追求通用 GPU 式覆盖。
- **不确定/需向资深工程师确认（低可信）**：具体客户模型需求、HBM allocation、先进封装成本、竞争产品性能和软件生态接受度。
