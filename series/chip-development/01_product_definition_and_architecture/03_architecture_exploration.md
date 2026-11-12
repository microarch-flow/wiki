# 架构探索

## 前置知识

- 建议先读 [市场与 Workload 分析](./01_market_and_workload_analysis.md)。
- 建议先读 [规格定义](./02_spec_definition.md)。
- 建议理解 [PPA](../00_overview/05_glossary.md#ppa)、[C Model](../00_overview/05_glossary.md#c-model) 和 [Microarchitecture](../00_overview/05_glossary.md#microarchitecture)。

## 架构探索的目标

架构探索是在产品目标、workload、成本和实现风险之间寻找可落地方案。它不是单纯追求最高峰值性能，也不是写一个漂亮的 C++ 模型。它要回答：在目标市场和预算下，什么硬件结构最可能被实现、验证、制造、编程并卖出去。

对 AI 芯片，架构探索通常围绕计算阵列、片上存储、外部内存、数据流、互连、精度、调度、软件栈和封装展开。一个架构方案只有在 workload 上有效利用、在工艺节点上可实现、在验证范围内可收敛、在软件栈上可使用，才算有意义。

## 从 Architecture 到 Microarchitecture

[Architecture](../00_overview/05_glossary.md#architecture) 定义对软件和系统可见的能力，例如编程模型、tensor 指令、内存模型和同步机制。Microarchitecture 定义具体实现，例如 pipeline、buffer、arbiter、DMA engine、[NoC](../00_overview/05_glossary.md#noc) router、scheduler、cache、banking 和 clock domain。

软件背景的人常把 C model 中的函数调用关系误认为硬件结构。硬件不是顺序执行的函数集合。硬件有并行资源、时钟周期、端口冲突、仲裁、背压、复位、时序路径和物理布线。架构探索如果不引入资源和时序概念，模型会高估性能。

例如 C model 里一次 tensor load 可能只是数组读取，但真实硬件里要经过 descriptor fetch、地址转换、DMA、NoC、SRAM bank、ECC、队列仲裁和 backpressure。每个环节都可能成为瓶颈。

## 关键探索维度

| 维度 | 需要探索的问题 | 错误后果 |
|---|---|---|
| 计算阵列 | systolic、SIMD、vector、tensor core、scalar control 比例 | 峰值高但利用率低 |
| 数据流 | weight stationary、output stationary、row/column tiling、fusion | 数据搬运压倒计算 |
| 片上存储 | SRAM 容量、bank、port、scratchpad/cache | 面积过大或带宽不足 |
| 外部内存 | DDR、GDDR、HBM、LPDDR、CXL memory | 成本、封装和带宽不匹配 |
| 精度 | FP16、BF16、FP8、INT8、INT4、混合精度 | 模型 accuracy 或硬件复杂度失控 |
| 互连 | crossbar、NoC、hierarchical fabric | 拥塞、时序和功耗问题 |
| 软件栈 | compiler、runtime、kernel library、debug tools | 硬件能力无法释放 |
| 可验证性 | 状态空间、corner case、可观测性 | tapeout 前无法建立信心 |
| 可实现性 | 频率、面积、功耗、floorplan 风险 | 后端无法收敛 |

对 7nm 及以下先进节点，互连、SRAM、功耗密度和物理实现风险更重要。逻辑晶体管密度提高不代表所有结构都能线性扩展。大阵列、宽总线和复杂 NoC 可能在 floorplan、routing、IR drop 和 timing 上付出很高代价。

## 建模层次

第一层是 analytical model，用公式快速估算 compute、bandwidth、SRAM 容量、die area 和功耗趋势。它适合快速筛掉明显不可行方案。

第二层是 trace-driven simulator，用 workload trace 模拟调度、内存访问、buffer 占用和队列行为。它适合发现利用率、带宽和资源冲突问题。

第三层是 cycle-level 或近似 cycle-level model，用 C++、SystemC 或自研框架模拟关键模块时序。它适合验证微架构参数，例如 FIFO depth、pipeline latency、bank conflict 和 arbitration。

第四层是 RTL prototype 或 high-level synthesis prototype。它适合校准面积、频率和功耗估算，但不应太早把探索锁死为单一 RTL。

第五层是 early synthesis 和 physical feedback。用 Synopsys Design Compiler、Cadence Genus、Fusion Compiler、Innovus 或 OpenROAD 类流程做早期综合和布局估计，校准架构模型中的面积和频率假设。商业项目尤其需要用真实工艺库和 SRAM compiler 数据校准。

## 工具和基础设施

常见工具包括 Python、C++、SystemC、gem5、Ramulator/DRAMSim 类内存模型、MLIR/TVM/XLA 编译器 IR、PyTorch/ONNX workload exporter、自研 trace simulator、Synopsys Design Compiler、Cadence Genus、Cadence Innovus、Synopsys PrimeTime、Siemens Questa、Synopsys VCS、Cadence Xcelium 等。

开源生态可以支持早期研究和可复现 demo，例如 MLIR、TVM、Verilator、OpenROAD、Yosys、CIRCT。但先进节点商业流片仍高度依赖 foundry PDK、商业 EDA、IP vendor 支持和 signoff 流程。开源工具适合提高透明度和自动化，不应被误解为能绕开先进节点的商业闭环。

## 探索流程

第一步是建立 baseline。选择一个保守架构，跑通 workload、性能模型、面积估算和软件映射。没有 baseline，就无法判断新想法是否真的更好。

第二步是定义设计变量。变量包括阵列尺寸、SRAM 容量、bank 数、NoC 带宽、DMA channel、外部内存类型、精度组合、频率目标和 power mode。变量不能无限多，否则探索空间不可解释。

第三步是运行设计空间搜索。可以用脚本、数据库和 AI Agent 自动批量生成配置、运行模型、收集结果、画 Pareto 曲线。这里自动化很有价值，但必须保证模型可信。

第四步是做实现校准。对候选方案做早期 RTL、综合、SRAM macro 查询和后端 floorplan 估计。没有物理反馈的架构探索容易过度乐观。

第五步是形成 architecture decision record。记录为什么选择某方案，拒绝了哪些方案，假设是什么，风险是什么，未来如何扩展。这个记录比最终 PPT 更重要，因为后续 bug triage 和版本迭代会回看这些假设。

## 角色和典型时长

架构探索的 owner 通常是芯片架构负责人，但不能只由架构团队完成。必须参与的角色包括 workload/应用工程师、编译器/runtime 工程师、性能建模工程师、RTL lead、验证 lead、后端/STA 顾问、DFT/test 顾问和产品负责人。AI 芯片如果涉及 HBM、chiplet 或高速接口，还需要 IP、封装和供应链角色提前参与。

时间上，第一轮架构探索可能在数周内筛掉明显不可行方案；形成可进入规格冻结的候选架构通常需要数月。复杂 AI SoC 的架构探索会贯穿前端开发，直到早期综合、floorplan 和软件映射结果持续校准模型。创业公司可以加速实验循环，但不应把未校准模型直接当作 RTL 开工依据。

## 关键决策点

第一个决策是片上 SRAM 和外部内存的比例。AI 芯片常被内存限制。SRAM 增大能提高复用和降低外部带宽，但会增加面积、漏电、floorplan 难度和 MBIST 复杂度。HBM 能提供高带宽，但带来先进封装、供应链和成本压力。

第二个决策是可编程性和专用化程度。越专用，能效可能越好，但模型变化和软件支持风险越大。越通用，生态更稳，但很难在能效上形成差异。创业公司第一颗芯片通常需要在一个清晰 workload 上专用，同时保留软件 fallback。

第三个决策是精度路线。INT4/FP8 等低精度可以提高吞吐和降低带宽，但需要模型、量化、编译器和客户接受度支持。不要只看硬件面积收益，要验证 accuracy 和软件流程。

第四个决策是频率目标。高频率会提高性能指标，但会放大时序、功耗和后端风险。对创业公司，过激频率目标可能比稍大面积更危险。

第五个决策是 debug 和 observability。性能计数器、trace、error logging 和 internal state snapshot 会占面积，但能显著降低硅后定位难度。第一颗芯片尤其不应省掉关键观测点。

## 与上下游接口

上游输入来自 workload、规格和成本目标。下游输出进入模块划分、微架构设计、RTL 计划、验证计划、IP 选择、工艺节点选择和后端预研。

架构探索必须与 [IP 策略](./04_ip_strategy.md) 同步。如果架构依赖 HBM、PCIe Gen5/Gen6、UCIe 或高性能 [SerDes](../00_overview/05_glossary.md#serdes)，就必须尽早确认 IP 是否可获得、是否支持目标工艺、交付内容是否包括硬核 layout、是否有验证 IP、是否有封装和板级约束。

架构探索也必须与 [工艺节点选择](./05_process_node_selection.md) 同步。一个在 5nm 可行的阵列，在 16nm 可能面积过大；一个在 28nm 成本合理的控制芯片，在 3nm 可能 NRE 完全不合理。

## 常见错误

第一个错误是用峰值 [TOPS](../00_overview/05_glossary.md#tops) 代表架构性能。真实 workload 利用率、内存瓶颈和软件开销会让峰值数字失真。

第二个错误是模型没有校准。C++ 模型跑得很快，不代表硬件能同样并行。必须用 RTL、综合、SRAM 数据和历史项目经验校准。

第三个错误是把编译器问题推迟。AI 芯片架构如果没有编译器共同设计，很可能得到难以映射的数据流和过多手工 kernel。

第四个错误是忽略验证复杂度。一个理论上很优雅的乱序调度、动态压缩或复杂一致性协议，可能让验证状态空间爆炸。创业公司不应在第一颗芯片里堆太多难验证机制。

第五个错误是忽略物理设计。宽总线、大 crossbar、多端口 SRAM、全局同步信号都可能在后端变成灾难。架构师需要早期听后端工程师的反馈。

## 创业公司视角下的取舍

创业公司最该自研的是差异化架构、编译器映射和性能模型。最不该自研的是与差异化无关、又极难验证或认证的基础 IP，例如成熟 PCIe PHY、DDR/HBM PHY、高速 SerDes。控制面 CPU 可以考虑成熟 RISC-V 或 Arm IP，取决于授权、生态和开放策略。

快速迭代最适合发生在模型、架构参数、RTL 生成模板、验证用例和编译器 mapping 上。不能指望每次架构想法都通过流片验证。第一颗芯片可以加入可配置性和观测点，为第二颗芯片积累数据，但不要把第一颗芯片做成“所有未来想法的容器”。

## 典型场景

团队比较两种 LLM 推理架构。方案 A 是超大矩阵乘阵列，峰值 TOPS 很高；方案 B 阵列较小，但 SRAM bank、DMA、KV cache 访问和调度更贴近小 batch decode。早期 PPT 中方案 A 更好看，但 trace simulator 显示目标客户场景下方案 A 利用率长期低于预期，外部带宽成为瓶颈。后端预估还显示方案 A 的全局互连和功耗密度风险高。

团队最终选择方案 B，并把营销指标从峰值 TOPS 调整为目标模型的 tokens/s/W、p99 latency 和可复现 benchmark。这个选择牺牲了宣传数字，但降低了首颗芯片失败概率。

## 后续阅读

- [04_ip_strategy.md](./04_ip_strategy.md)
- [05_process_node_selection.md](./05_process_node_selection.md)
- [06_milestones_and_signoffs.md](./06_milestones_and_signoffs.md)
- [微架构设计](../02_frontend_design_and_verification/02_microarchitecture_design.md)
- [AI 芯片特有的考虑](../06_cross_cutting_topics/06_ai_chip_specific.md)

## 参考公开来源

- [MLIR Project](https://mlir.llvm.org/)
- [Apache TVM Documentation](https://tvm.apache.org/docs/)
- [gem5 Simulator](https://www.gem5.org/)
- [OpenROAD Project](https://theopenroadproject.org/)
- [Cadence Genus Synthesis Solution](https://www.cadence.com/en_US/home/tools/digital-design-and-signoff/synthesis/genus-synthesis-solution.html)

## 内容可信度说明

- **公开信息（高可信）**：常见 EDA、仿真、编译器和开源工具存在；架构探索需要关注性能、功耗、面积、内存和软件映射。
- **行业惯例（中可信）**：多层模型、trace-driven simulation、设计空间搜索、早期综合和 physical feedback 的组合方法。
- **经验性观察（中低可信）**：创业公司容易被峰值 TOPS 误导；第一颗 AI 芯片应优先控制验证、软件和物理实现风险。
- **不确定/需向资深工程师确认（低可信）**：具体节点下的面积/频率/功耗估算、SRAM compiler 特性、HBM 供应和封装可行性、特定架构在客户 workload 上的真实收益。
