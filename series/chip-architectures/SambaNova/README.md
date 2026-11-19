# SambaNova SN40L 怎样把算子图放到 PCU 和 PMU

<div class="chip-legacy-anchors" aria-hidden="true"><span id="sambanova-rdu-rda"></span></div>

SambaNova SN40L 把一段算子图映射成片上的粗粒度流水线。计算单元处理数据，存储单元暂存结果并决定读写顺序，网络连接各个流水级。关键问题是中间张量能否以后一阶段需要的布局留在片上。本文以 SN40L 为主，涉及两代时单独标明。 [SN40L 论文](https://arxiv.org/html/2405.07518v1)

<div class="chip-legacy-anchors" aria-hidden="true"><span id="pcupattern-compute-unit可配置计算流水线"></span><span id="pmupattern-memory-unit可编程-memory-流水线不是普通-sram"></span><span id="rdnreconfigurable-dataflow-network三张并行物理网络"></span><span id="agcuaddress-generation-coalescing-unitdataflow-与外部世界的边界"></span></div>

## 计算、缓冲和网络怎样分工

| 单元 | 输入和配置 | 职责 |
| --- | --- | --- |
| PCU（模式计算单元） | 数据流和所选计算模式 | 以矩阵阵列或向量流水线等配置处理数据。 |
| PMU（模式存储单元） | SRAM、地址生成及数据对齐配置 | 暂存中间结果，按下一阶段需要的布局组织读写。 |
| RDN（可重构数据流网络） | 软件配置的路由和来自各单元的流 | 连接 PCU、PMU 与其他单元，分别承载向量、标量和控制流量。 |
| AGCU（地址生成与合并单元） | 片上流或外存读写命令 | 在数据流单元和系统接口之间生成并合并访问，连接内存、主机或对端 RDU。 |

编译器为算子、缓冲和流量分配资源。向量和标量网络支持按维度寻路，也支持软件配置的流路由。控制网络传递同步和流程控制令牌。向量流的序号可被 PMU 用来计算写地址，帮助来自多个发送端的数据按程序需要的顺序落位。 [SN40L 论文，第 IV 节](https://arxiv.org/html/2405.07518v1#S4)

<div class="chip-legacy-anchors" aria-hidden="true"><span id="执行模型spatial-dataflow不是-kernel-by-kernel"></span><span id="编译器与-runtime复杂度的真正所在"></span><span id="sambanova-的下注"></span></div>

## 一次布局变换怎样留在片上

假设图中有两次矩阵乘，第二次需要第一步结果的转置布局。编译器可以把前后两个矩阵乘映射到不同 PCU，把中间张量分块映射到一个或多个 PMU。

例如，第一段按行生成一个 2 × 3 分块。第一行是 a、b、c，第二行是 d、e、f。若下一段按行读取转置后的 3 × 2 分块，PMU 可以按 a、d、b、e、c、f 的顺序供数。这个例子只表示数据顺序。实际映射还要检查地址生成和存储 bank 能否以所需速率提供这组访问。

若 PMU 的读写模式可以生成目标布局，后一段直接消费重新排布的数据流。能否避免中间张量落到片外，取决于块的峰值存活容量、访问模式和可用的 RDN 路由。若前一段生产快于后一段消费，也要处理缓冲占满后的反压。论文第 III 节用实际图段比较了不同融合程度，图 4 展示了分配计算级和中间缓冲的一种实现。 [SN40L 论文，第 III 节](https://arxiv.org/html/2405.07518v1#S3)

<div class="chip-legacy-anchors" aria-hidden="true"><span id="关键参数sn40l单-rdusocket-口径"></span><span id="三层-memorysram-hbm-ddr为-genaicoe-而设"></span><span id="芯片迭代sn10-sn40l"></span></div>

## 从单 RDU 的三层存储到系统

这里采用 SN40L 论文的单 RDU（单 socket）口径。该器件是双 die 封装。下表 SRAM 是分布于 PMU 的总量。Hot Chips 演讲把相同标称数字写作 MB、GB、TB。引用时标明所用资料和单位。 [SN40L 论文](https://arxiv.org/html/2405.07518v1) · [Hot Chips 2024 演讲](https://hc2024.hotchips.org/assets/program/conference/day1/48_HC2024.Sambanova.Prabhakar.final-withoutvideo.pdf)

| 位置 | 论文容量 | 典型用途 |
| --- | --- | --- |
| 片上 PMU SRAM | 520 MiB | 计算流水线的输入和中间结果。 |
| 封装内 HBM | 64 GiB | 当前活跃模型的高带宽供数。 |
| 可插拔 DDR | 最高 1.5 TiB | 存放更多模型参数，按需向 HBM 搬运。 |

比较跨设备容量时，还要记录 socket 数、已装 DDR 和运行时保留空间。片上 RDN、封装内 die-to-die 以及多 RDU 间 P2P 是三条不同范围的路径。SN10 是前一代，历史演讲中的容量和图映射属于当时的器件。 [SN40L 论文，第 IV 节](https://arxiv.org/html/2405.07518v1#S4) · [SN10 历史资料](https://www.hc33.hotchips.org/assets/program/conference/day2/SambaNova%20HotChips%202021%20Aug%2023%20v1.pdf)

<div class="chip-legacy-anchors" aria-hidden="true"><span id="coecomposition-of-expertssambanova-的系统级叙事"></span><span id="该警惕的点批判"></span></div>

## 专家组合为何单独计模型切换

论文的 CoE（Composition of Experts）实验由路由模型选择要调用的独立专家模型。若目标专家只在 DDR，系统先把权重搬到 HBM，再执行专家。实际时延包括路由、权重移动和专家执行。不同批次可能选到不同专家，重复使用已驻留的权重有助于减少搬运。模型内部的 MoE 层及其专家通信属于另一个层级。 [SN40L 论文，第 II 和 VI 节](https://arxiv.org/html/2405.07518v1) · [MoE 工作负载](../../workload/06-chip-workload-analysis/moe-workload.md)

论文用 8 socket 的 SN40L 节点实测，并用已发表的模型时延和规格估计 DGX 对照。结果还固定了 TP8，并区分批大小、专家数和输出长度。解读模型切换或总体时延时，应分别记录这些条件与数据的采集方式。 [SN40L 论文，第 VI-B 节](https://arxiv.org/html/2405.07518v1#S6.SS2)

<div class="chip-legacy-anchors" aria-hidden="true"><span id="融资和经营情况"></span><span id="从中该获取的经验教训"></span><span id="与-cerebras-graphcore-的对照"></span></div>

## 接下来怎么读

- 对照功能切片固定、执行时间由编译器安排的路线。 [Groq 第一代 TSP](../groq-tsp/README.md)
- 查阅原文中的历史产业背景和 SN10 资料入口。 [原稿存档](https://github.com/microarch-flow/chip-architecture-wiki/blob/3086204c049a762eb59033f8141fba9e91f4c669/SambaNova/README.md)
