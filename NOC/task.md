# NoC Wiki 系统性重写 Prompt（含新目录设计）

## 你的任务

我（Biao）有一份位于 `./NOC/wiki/` 的片上网络知识 wiki，由 AI 批量生成。和我之前重写过的 BUS、RAM wiki 不同，这份 NoC wiki 不仅**内容停留在"教科书定义层"**，**目录结构本身也有严重问题**：

1. `04-ai-dataflow-system` 大章节塞了 20 篇文件，AI 特有话题和通用系统集成话题混杂
2. `03-topology-routing` 把 topology 和 routing 混在一起，但两者在概念上正交（同一 topology 可以跑不同 routing 算法）
3. `05-modeling-evaluation` 混了两件不同粒度的事——"评估方法论"和"仿真器实现"
4. CPU NoC 和 AI NoC 在目录里没有明确的主辅关系

我需要你做两件事：

1. **按下方给出的新目录结构**重新组织整个 wiki（旧目录作为内容参考，但结构推翻重建）
2. **按"架构师深度 + 建模者视角"的标准**重写每一篇

---

## 关于我（你需要校准深度的依据）

- **身份**：System Software Architect，约 7 年经验，覆盖系统软件工具链 + AI 芯片架构建模与探索
- **强项**：gem5 仿真、SystemC、编译器工具链、RTL 级工作；曾在 Black Sesame Technologies 做自动驾驶芯片软件
- **当前目标**：构建商用 AI 加速器架构探索工具链（archax），方法论已固化——以 deterministic NPU 为目标，系统级抽象采用 Resource/Topology/Interaction/Capability，遵循"数据搬运优先"原则，双层探索循环
- **学习 NoC 的目的**：终极目标是把 NoC 层面的设计权衡和实际行为内化，让架构探索框架能正确建模 NPU 互连。我特别关心 deterministic NPU 场景下的 NoC 设计——这意味着 source routing、静态调度、可分析的 latency 上界等话题对我比 adaptive routing/动态拥塞控制更重要
- **已经具备的相关背景**：刚刚完成了 BUS wiki 的重写，已经熟悉 AXI 五通道/outstanding/QoS 等总线概念；RAM wiki 也已完成，熟悉 DRAM bank 并行、memory controller 调度等。NoC 的某些话题（如 backpressure、QoS、地址映射）会和 BUS/RAM 的概念有交集，重写时应当**明确指出交集和差异**，而不是把 NoC 当作孤立话题讲
- **读者水平假设**：理解 packet/flit/router 这些术语的字面含义，但需要被讲清楚"**为什么**会演化成今天这样、**代价是什么**、**仿真里要怎么建模**"

---

## 新目录结构

```
./NOC/wiki/
├── 01-overview/
│   ├── README.md
│   ├── problem-statement.md                          # 为什么单一总线/crossbar 在多核/多 tile 场景下崩溃，必须演化为网络
│   ├── bus-vs-noc-vs-crossbar.md                     # 从 BUS 到 NoC：三种互连范式的本质区别和适用边界
│   ├── learning-roadmap.md                           # 学习路径与各章节依赖关系
│   └── taxonomy.md                                   # NoC 的分类体系（topology/routing/flow-control/QoS 几个正交维度）
│
├── 02-router-microarchitecture/                      # 路由器微架构：NoC 的最小可工作单元
│   ├── README.md
│   ├── packet-flit-phit-hierarchy.md                 # Packet/Flit/Phit 的层级——为什么必须分三层
│   ├── router-pipeline-stages.md                     # Router 的经典 5 级流水：BW/RC/VA/SA/ST
│   ├── input-buffer-organization.md                  # 输入缓冲组织：FIFO/VC buffer 的结构与代价
│   ├── virtual-channel-fundamentals.md               # VC 为什么存在——HoL blocking 与 deadlock avoidance 两件事
│   ├── allocator-design-vc-switch.md                 # VC allocator 和 switch allocator：仲裁的核心
│   ├── credit-based-flow-control.md                  # Credit 机制：为什么这是 NoC 主流的 backpressure 方案
│   ├── wormhole-vs-vct-vs-store-forward.md           # 三种 switching 策略的演化和适用场景
│   └── router-power-area-tradeoff.md                 # Router 的功耗、面积、性能三角
│
├── 03-topology/                                      # 拓扑：把 router 连起来的几何学
│   ├── README.md
│   ├── topology-design-metrics.md                    # 拓扑设计的核心指标：diameter/bisection/degree/path diversity
│   ├── mesh-and-torus.md                             # Mesh 和 Torus：为什么 NPU 上 mesh 几乎一统天下
│   ├── ring-and-hierarchical-ring.md                 # Ring 和分层 ring：低 radix 拓扑的复兴
│   ├── tree-and-fat-tree.md                          # Tree/Fat-tree：bisection 友好但物理实现难
│   ├── crossbar-and-concentrated-mesh.md             # Crossbar 与 concentrated mesh：什么时候"不分层"反而更好
│   ├── flattened-butterfly-dragonfly.md              # 高维拓扑：HPC 来的灵感在芯片上能落地多少
│   ├── topology-physical-realization.md              # 拓扑落到 floorplan：metal layer/线长/拥塞带来的真实约束
│   └── topology-selection-framework.md               # 选拓扑的决策框架：从 workload 反推
│
├── 04-routing-and-flow-control/                      # 路由与流控：拓扑之上的策略
│   ├── README.md
│   ├── routing-algorithm-classes.md                  # 路由算法的分类：deterministic/oblivious/adaptive
│   ├── dimension-order-routing.md                    # XY routing：最简单也最被低估的路由
│   ├── deadlock-avoidance-turn-model.md              # Deadlock 的形成与 turn model 的避免策略
│   ├── adaptive-routing-tradeoffs.md                 # Adaptive routing：用什么换什么
│   ├── source-routing-for-deterministic-systems.md   # Source routing：为什么 NPU 和编译器友好的系统都偏爱它
│   ├── arbitration-policies.md                       # 仲裁策略：round-robin/age-based/priority 及其代价
│   ├── qos-and-priority-classes.md                   # NoC 上的 QoS：和 BUS QoS 的本质区别
│   └── deadlock-livelock-starvation.md               # 三种病态：定义、来源、检测和预防
│
├── 05-system-integration/                            # NoC 作为系统部件：通用的集成话题
│   ├── README.md
│   ├── ni-network-interface-design.md                # NI 的职责：协议转换、packetization、ordering
│   ├── address-map-and-routing-table.md              # 地址映射到 NoC：destination decode 的几种实现
│   ├── dma-engine-noc-interaction.md                 # DMA engine 怎么使用 NoC——request/response 调度
│   ├── traffic-patterns-and-characterization.md      # 流量模式：uniform/hotspot/bit-reverse 等及其意义
│   ├── multiple-physical-networks.md                 # 多物理网络：为什么 request/response/coherence 要分网
│   ├── noc-meets-memory-system.md                    # NoC 和 DRAM/SRAM 子系统的衔接点
│   └── noc-vs-bus-revisited.md                       # 重新审视 NoC vs BUS：在哪些场景下边界开始模糊
│
├── 06-ai-noc-specifics/                              # AI NoC 专题：只放 AI 特有话题
│   ├── README.md
│   ├── why-ai-noc-is-different.md                    # AI workload 的流量特征如何重塑 NoC 设计
│   ├── broadcast-multicast-tree.md                   # 广播/多播：weight 分发与 activation 复制的硬件支持
│   ├── reduction-and-collective-networks.md          # Reduction 网络：从 all-reduce 看片上 collective 的硬件化
│   ├── deterministic-noc-and-static-scheduling.md    # Deterministic NoC：可分析、可调度、为编译器服务
│   ├── tile-architecture-and-noc.md                  # Tile 架构下 NoC 的角色：从 tile interface 反推 NoC 需求
│   ├── memory-centric-noc.md                         # Memory-centric NoC：HBM 接入与 bank 级路由
│   ├── chiplet-and-die-to-die-interconnect.md        # Chiplet 时代：D2D 互连与片上 NoC 的接合
│   ├── compiler-noc-co-design.md                     # 编译器和 NoC 的协同：从 source routing 到流量调度
│   ├── workload-gemm-on-noc.md                       # 案例：GEMM 在 NoC 上的流量与瓶颈
│   ├── workload-attention-prefill.md                 # 案例：Attention prefill 阶段的 NoC 行为
│   ├── workload-attention-decode-kv-cache.md         # 案例：Decode 阶段 KV cache 访问的 NoC 模式
│   └── workload-moe-routing.md                       # 案例：MoE 的 expert routing 对 NoC 的需求
│
├── 07-evaluation-methodology/                        # 评估方法论：纯方法层
│   ├── README.md
│   ├── metrics-latency-throughput-saturation.md      # 核心指标：latency-throughput 曲线与饱和点
│   ├── from-workload-to-traffic-trace.md             # 从 workload 推导出 traffic trace 的方法
│   ├── modeling-layers-analytical-event-cycle.md     # 三层建模：解析模型 / 事件驱动 / cycle-accurate
│   ├── power-area-modeling.md                        # 功耗与面积建模：从 router 微架构反推
│   ├── stall-taxonomy-and-attribution.md             # NoC 上的 stall 分类与归因方法
│   ├── architecture-exploration-loop.md              # 架构探索的迭代框架：从假设到结论
│   └── case-card-template.md                         # 评估案例卡片模板
│
├── 08-simulator-construction/                        # 仿真器实现：从方法论落到代码
│   ├── README.md
│   ├── simulator-design-spec.md                      # 仿真器的设计 spec：输入、输出、状态、事件
│   ├── core-data-structures.md                       # 核心数据结构：router/link/packet/event-queue
│   ├── event-driven-vs-cycle-accurate.md             # 两种实现路线的工程取舍
│   ├── router-pipeline-pseudocode.md                 # Router 流水的伪代码实现
│   ├── traffic-injection-and-tracing.md              # 流量注入与 trace 收集机制
│   ├── verification-and-calibration.md               # 仿真器自验证与校准（vs RTL 或参考实现）
│   └── implementation-roadmap.md                     # 分阶段实现路线图
│
└── 09-reference/                                     # 参考资料
    ├── README.md
    ├── glossary.md
    ├── checklists.md
    ├── high-frequency-questions.md
    └── noc-design-decision-tree.md                   # NoC 设计决策树（从 workload 到选型）
```

**目录结构的关键设计决策**：

1. **拓扑（03）和路由（04）拆开**：两者正交——同一个 mesh 可以跑 XY routing、odd-even routing、adaptive routing；同一个 ring 可以跑不同的 deadlock 避免策略。把它们硬绑在一起是 NoC 教学里常见的坏味道
2. **system-integration（05）和 ai-noc-specifics（06）分开**：通用集成话题（NI、DMA、地址映射、traffic patterns、多物理网络）属于"任何 NoC 都要面对的"；AI 专题（collective、multicast、deterministic scheduling、workload case）属于"AI workload 反推出的特殊设计"。混在一起会让你看不清"什么是 NoC 本身的，什么是 AI 加在上面的"
3. **evaluation-methodology（07）和 simulator-construction（08）分开**：这是你明确要求的拆分。07 讲"如何度量和评估一个 NoC 设计"，是方法层；08 讲"如何用代码实现一个 NoC 仿真器"，是工程层。两者本来就不是同一粒度的事
4. **AI NoC 是主线，CPU NoC 是对照点**：删除原 wiki 中的 `cpu-cache-coherent-noc-reference.md`。在 `06-ai-noc-specifics/why-ai-noc-is-different.md` 一篇里集中对照 CPU NoC（流量特征、coherence 需求、ordering 约束），其他章节如果需要可以一句话提到 CPU NoC 的对应做法，但不再单开篇幅
5. **deterministic NoC 单独成篇并放在 06 章节核心位置**：这是你做架构探索框架的关注点，必须单独深入
6. **chiplet 和 D2D 互连留在 AI 专题但不拓展过度**：D2D 本身可以是一整本书，wiki 里聚焦"它和片上 NoC 怎么衔接"，不深入 SerDes/UCIe 协议细节

---

## 重写的深度定位

### 正文：架构师视角

每一个概念必须回答这三个问题中的至少两个：

1. **设计动机**：这个机制是为了解决什么物理/时序/系统约束？如果没有它会怎样？
2. **Trade-off**：选择这个设计放弃了什么？竞争方案是什么？什么场景下另一个方案更好？
3. **演化路径**：这个设计是从什么前身演化来的？比如 wormhole switching 是怎么从 store-and-forward 反推出来的？credit-based flow control 是怎么从更早的 stop-and-go 演化来的？

**严禁**只写"X 是什么，包含 A/B/C 三类"这种平铺罗列。如果一个段落只是在定义术语，必须紧跟一段"为什么需要这个区分"。

### 每篇文末固定小节：「建模启示」

在每篇文档末尾，加一个标题为 `## 建模启示` 的小节，回答：

- 这个机制在 cycle-level / event-driven 仿真里应该如何抽象？
- 哪些状态变量是必须显式建模的？哪些可以抽象掉？
- 如果只关心性能（latency / throughput / saturation point），哪些细节可以折叠？如果关心 deadlock 验证或 worst-case latency 分析，哪些细节必须保留？
- 至少给出一个具体的状态变量名 / 事件类型名 / 数据结构草图，禁止只讲抽象方法论

这一小节**不需要**和 archax 的具体术语（Resource/Topology/Interaction/Capability）强行绑定——只在 `06-ai-noc-specifics/`、`07-evaluation-methodology/`、`08-simulator-construction/` 三个章节才显式使用这套抽象。其他章节保持 NoC 知识本身的纯粹性。

### 类比的使用原则

**适度类比，关键处用**：

- 只在引入一个**反直觉**或**初学者最容易混淆**的概念时使用类比（如：virtual channel 为什么不是真的物理 channel、wormhole 为什么得名 wormhole、credit 机制为什么不是简单的 ack、deadlock 的循环等待结构）
- **一个概念至多一个类比**，类比之后立刻回到精确语言
- **避免**过度通俗化的类比（"NoC 就像高速公路"这种已经成废话的）
- 如果某概念在精确语言里就能讲清楚，**不要为了"通俗"硬加类比**
- 类比要**有张力**：好的类比应该揭示一个非平凡的结构相似性

### 与 BUS、RAM 知识体系的衔接（这份 wiki 独有的要求）

我刚刚重写完 BUS 和 RAM 两份 wiki，已经形成了一套关于互连和存储的认知体系。NoC 与这两者有多个交集点，重写时**必须明确处理**：

1. **NoC 上的 QoS vs BUS 上的 QoS**：BUS 的 QoS 主要是 master 优先级，NoC 的 QoS 涉及 priority class + VC + flow control 的复合体——必须讲清差异
2. **NoC 的 credit-based flow control vs AXI 的 ready/valid handshake**：两者都是 backpressure 机制，但工作层级和代价完全不同
3. **NoC 上的地址映射 vs BUS 的 decode**：BUS decode 通常是固定的 address-to-slave 映射，NoC 的 destination decode 可能涉及路由表、source routing 等更复杂机制
4. **NoC 接 DRAM controller vs BUS 接 DRAM controller**：从 NoC 端到 MC 的接口与传统 BUS 端有何不同（NoC 流量到 MC 的乱序、合并、QoS 透传）
5. **多物理网络 vs BUS 的多通道分离**：AXI 的读写通道分离和 NoC 的 request/response 分网在思想上有共通处，但解决的问题不同

在相关篇章里，请**主动建立这种横向链接**，并明确指出"和 BUS/RAM 里的 X 概念相同点是 Y，差异在 Z"。这能帮我把三份 wiki 的知识连成网，而不是三个孤岛。

---

## 内容质量的具体标准

### 必须做到

1. **每个设计决策都要有"因为...所以..."**：例如不要只说"NoC 用 wormhole switching"，要说"因为 store-and-forward 要求每个 router 缓存整个 packet，对于一个 64B packet 在 128-bit 链路上就是 4 cycle 的纯延迟开销加上整 packet 的 buffer 容量；wormhole 让 flit 在 head flit 建立路径后接连流过，buffer 只需容纳少量 flit，代价是占用资源的时间跨度变长，从而引入 HoL blocking，而这又催生了 VC 设计"
2. **对比要尖锐**：mesh vs torus、wormhole vs VCT、deterministic vs adaptive、credit-based vs on/off、单物理网络 vs 多物理网络，每个对比都要给出"什么场景选谁，代价是什么"的明确判断
3. **时序/流水示例**：在讲 router pipeline、credit 回传、flit 流动等概念时，至少给一个 ASCII 时序图或 cycle-by-cycle 表格
4. **真实硬件锚点**：尽量提到真实场景的具体数字（典型 NPU mesh 的 router radix、VC 数量、buffer 深度、链路宽度量级）。如果不确定具体数字，明确说"典型量级在 X-Y 之间"而不是编造
5. **指明常见误解**：每个核心概念后给一句"常见误解：...，实际上：..."。NoC 是误解集中区——比如"VC 是物理 channel"、"adaptive routing 一定比 deterministic 好"、"mesh 总是优于 ring"——这些都需要主动澄清

### 必须避免

1. **不要使用 emoji**
2. **不要堆砌 bullet list**：能用连贯论述讲清的不要拆成 bullet。bullet 只用于真正的并列枚举
3. **不要写"通常""一般""有时"这种含糊词**——要么给条件，要么给具体例子
4. **不要在每段开头都用粗体小标题**——这是 AI 生成内容的典型坏味道
5. **不要重复**：同一个概念在同一篇文档里不要换着说法讲两遍；跨文件出现的概念，前面已讲清的后面只能引用不能重讲
6. **不要"水"过渡句**：诸如"接下来我们看看..."这类承上启下的废话直接删
7. **不要假装有经验**：workload case study 必须基于公开论文/资料，明确标注来源；构造案例明确写"构造案例"；不要用"在实际项目中我们..."这种伪装

---

## 工作流程

### Step 1：先阅读理解全局

在动笔之前，**完整阅读** `./NOC/wiki/` 旧目录下所有现有文件以及 `SUMMARY.md`。建立对现有材料的全局认识，识别：

- 哪些旧文件的内容可以作为新目录某一篇的素材（请列对应关系）
- 哪些内容需要彻底推翻
- 旧 wiki 里的 20 篇 04-ai-dataflow-system 文件分别该归到新目录的哪一篇
- 哪些主题在新目录里完全缺失，需要从零写起

### Step 2：备份旧 wiki，按新目录建空骨架

1. 先把现有的 `./NOC/wiki/` 整体重命名为 `./NOC/wiki.old/` 作为备份
2. 按新目录结构在 `./NOC/wiki/` 下建立空骨架（所有目录 + 每个 .md 文件含标题但内容为空 + 占位说明）
3. 让我 review 骨架，确认无误后才开始填内容

### Step 3：按章节顺序重写，不跳跃

按 `01 → 09` 的顺序重写。**不要并行处理多个章节**，因为后面章节会引用前面章节的术语，必须先把前面的语言体系建立起来。

每完成一个章节，**生成一个简短的总结**，告诉我：

- 这个章节里建立了哪些核心概念
- 这些概念会在后续哪些章节被使用
- 重写过程中有没有发现目录设计本身的问题（比如某篇应该拆/合）

如果你发现某个文件的主题本身就不应该存在、或者应该拆成两个文件、或者应该合并到另一篇——**先停下来告诉我，等我确认再动**，不要自作主张改目录结构。

### Step 4：每篇文档的输出格式

```
# 标题

上级：[link]
相关：[link], [link]

## 这页在回答什么问题
（一段，不超过 3 句话，必须是真问题不是"介绍 X"）

## 正文小节（自由组织，但每节都要有设计动机或 trade-off 分析）

## 一句话理解
（一句精确的话，不是空话）

## 建模启示
（cycle-level / event-driven 建模视角下，这个机制如何抽象；至少给一个具体的状态变量 / 事件类型 / 数据结构草图）
```

不同章节的篇幅期望：

- `02-router-microarchitecture/`、`04-routing-and-flow-control/`：偏微架构与算法，需要时序图和伪代码片段
- `03-topology/`：偏几何与物理实现，需要拓扑图（ASCII）和物理布局说明
- `06-ai-noc-specifics/` 的 workload case：每篇需要真实参考文献，给出流量特征图或表
- `07-evaluation-methodology/`、`08-simulator-construction/`：方法和工程层，需要清晰的步骤和接口定义
- `09-reference/`：checklist / glossary 类，保持简短紧凑

### Step 5：交叉引用

重写时**主动建立**三类交叉引用：

1. **NoC 内部的交叉引用**：例如 `04-routing-and-flow-control/deadlock-avoidance-turn-model.md` 应该链接到 `02-router-microarchitecture/virtual-channel-fundamentals.md`，因为 deadlock 避免与 VC 设计紧密相关
2. **与 BUS wiki 的链接**：在涉及 QoS、handshake、地址映射等话题时，链接到 BUS wiki 对应文件，并明确指出异同
3. **与 RAM wiki 的链接**：在 `05-system-integration/noc-meets-memory-system.md` 和 `06-ai-noc-specifics/memory-centric-noc.md` 这类文件里，链接到 RAM wiki 的 memory controller、bank parallelism 等章节

### Step 6：在 06、07、08 章节才显式连接 archax 方法论

只有在 `06-ai-noc-specifics/`、`07-evaluation-methodology/`、`08-simulator-construction/` 三个章节里，可以在「建模启示」小节中显式提到 Resource/Topology/Interaction/Capability 这套抽象。其他章节保持知识本身的独立性。

---

## 一个示范：`02-router-microarchitecture/virtual-channel-fundamentals.md` 应该怎么写

如果这篇只写"VC 是把一个物理 channel 复用成多个逻辑 channel，用于避免 HoL blocking 和 deadlock"，那就是失败的写法。

**核心问题**：VC 看似只是"buffer 多开几路"的小机制，实际上它是 NoC 设计里的枢纽——它**同时**解决了两件不同的问题（HoL blocking 缓解 + deadlock avoidance），而这两件事的耦合带来了 NoC 设计里最难的取舍之一。

正文应该讲：

- 没有 VC 时的 NoC 是什么样：单 FIFO 输入 buffer，一旦队头 flit 因下游拥塞被卡住，后面所有 flit 都被堵住，即便它们去往的方向是畅通的——这就是 HoL blocking
- 引入 VC 的第一个动机：把单个物理输入 port 上的 buffer 拆成多个逻辑队列，让不同 destination 或 priority 的 flit 走不同 VC，绕开 HoL
- 引入 VC 的第二个动机（更关键）：通过给路由路径上的不同"循环段"分配不同 VC，可以打破环状依赖，从而避免 deadlock。这是 turn model 之外的另一种 deadlock 避免思路
- 这两个动机的耦合带来的设计难题：VC 数量增加能更好缓解 HoL 但增加 allocator 复杂度（VC allocator 的仲裁规模是 N×N，N 是 VC 数）；VC 数量在 deadlock-free 路由里是被路由算法约束的（如 dateline 方案要求至少 2 VC），所以"为 HoL 多加 VC"和"为 deadlock 加 VC"在数量上可能冲突
- VC 的状态变量：每个 VC 维护 input buffer、output VC binding、credit counter——这些状态决定了 router 流水的复杂度
- 真实 NPU 上的典型选择：很多 deterministic NPU NoC 只用 2-4 个 VC，因为静态调度本身就消除了大部分 HoL 风险，VC 主要承担 deadlock 避免的功能；而通用 CPU NoC（如 cache-coherent NoC）VC 数往往更多（8 个以上），因为需要分多类消息（request/response/snoop/coherence ack 等），每类一个或多个 VC
- 常见误解：VC 是物理资源——实际上 VC 共享同一物理 channel 的带宽，VC 数量增加不增加链路带宽，只是更精细地复用它

然后「建模启示」回答：在 cycle-level 仿真里，VC 必须显式建模为 router 内部状态机的一部分。最小状态集合包括：每个 input VC 的 buffer 占用（队列）、每个 VC 的 output binding（被分配到的下游 VC）、每个 VC 的 credit counter（下游剩余 buffer 数）。事件类型上，VC allocator 决策、switch allocator 决策、credit 回传都是独立事件。如果只关心 saturation throughput 不关心 worst-case latency，VC binding 可以简化为静态映射；如果关心 deadlock-free 性质验证，VC 状态必须完整且可追踪。

**这就是我要的深度**。请用类似的方式重写每一篇。

---

## 开始之前

1. 先告诉我你**完整读完旧 `./NOC/wiki/`** 之后对原内容的整体诊断：
   - 旧 wiki 哪些内容可以作为新结构里某篇的素材（请列对应关系，特别是 04-ai-dataflow-system 那 20 篇的分流方案）
   - 哪些内容质量太差需要彻底推翻，从零写起
   - 新目录里哪些文件在旧 wiki 里完全没有对应素材
2. 然后告诉我你打算如何分批次提交重写（建议按文件而不是按章节批量提交，每个文件都让我能 review）
3. 等我确认后再开始建空骨架（Step 2）

不要急着动手。这份 wiki 涉及目录大改 + 内容重写双重任务，先把分流方案和目录设计确认下来比快速动手重要得多。