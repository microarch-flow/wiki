# RAM Wiki 系统性重写 Prompt（含新目录设计）

## 你的任务

我（Biao）有一份位于 `./RAM/wiki/` 的存储器知识 wiki，由 AI 批量生成，**内容停留在"教科书定义层"**：罗列特性、给出术语、但不讲设计动机、不讲 trade-off、不讲它在 cycle-level 仿真里如何体现。同时原 wiki **几乎只覆盖了 DRAM，缺失 SRAM 主线**，结构上也不适合系统性学习。

我需要你做两件事：

1. **按下方给出的新目录结构**重新组织整个 wiki（旧目录可作为内容参考，但结构推翻）
2. **按"架构师深度 + 建模者视角"的标准**重写每一篇

---

## 关于我（你需要校准深度的依据）

- **身份**：System Software Architect，约 7 年经验，覆盖系统软件工具链 + AI 芯片架构建模与探索
- **强项**：gem5 仿真、SystemC、编译器工具链、RTL 级工作；曾在 Black Sesame Technologies 做自动驾驶芯片软件
- **当前目标**：构建商用 AI 加速器架构探索工具链（archax），方法论已固化——以 deterministic NPU 为目标，系统级抽象采用 Resource/Topology/Interaction/Capability，遵循"数据搬运优先"原则
- **学习存储器的目的**：体系结构基础需要补全；终极目标是把 SRAM/DRAM/HBM 的物理与系统行为内化，让架构探索框架能正确建模存储层次
- **读者水平假设**：理解 cache hierarchy、virtual memory、DMA、AXI 这些概念的字面含义；做过 gem5 内存子系统的仿真工作；但对存储器**物理层与电路层**的设计动机理解不深，需要被讲清楚"**为什么**会演化成今天这样、**代价是什么**、**仿真里要怎么建模**"

---

## 新目录结构

以下是重写后的目录结构。**每个文件的标题就是它要回答的核心问题**，不要把它们写成"X 介绍"或"X 详解"。

```
./RAM/wiki/
├── 01-overview/
│   ├── README.md
│   ├── problem-statement.md                          # 为什么存储器是体系结构里最难的部分
│   ├── memory-hierarchy-tension.md                   # 速度、容量、成本、功耗——四角矛盾的根源
│   ├── sram-dram-divergence.md                       # 同样是 RAM，为什么 SRAM 和 DRAM 走向了完全不同的工程路径
│   ├── learning-roadmap.md                           # 学习路径与各章节依赖关系
│   └── taxonomy.md                                   # RAM 家族的分类与命名体系
│
├── 02-sram-foundations/                              # SRAM 主线：从最小完备模型出发
│   ├── README.md
│   ├── 6t-cell-bistable-storage.md                   # 6T cell 为什么是 6 个晶体管——双稳态如何对抗扰动
│   ├── wordline-bitline-sense-amp.md                 # 字线、位线、读出放大器：SRAM 的电路骨架
│   ├── read-write-cycle-timing.md                    # SRAM 一次读/写的 cycle-by-cycle 行为
│   ├── single-port-dual-port-multi-port.md           # 单口、双口、多口 SRAM——端口数为什么是关键代价
│   ├── sram-array-organization.md                    # bank/sub-array/mat：SRAM 阵列怎么划分才高效
│   ├── sram-process-scaling-challenge.md             # 为什么 SRAM 在先进制程下不再 scale
│   └── sram-power-leakage-retention.md               # 漏电、保持电压、low-power SRAM 设计
│
├── 03-sram-applications/                             # SRAM 的应用形态：register file / cache / scratchpad
│   ├── README.md
│   ├── register-file-as-sram.md                      # Register file 为什么是一种特殊 SRAM
│   ├── cache-sram-tag-data-arrays.md                 # Cache 里的 SRAM：tag 阵列与 data 阵列的差异
│   ├── scratchpad-vs-cache.md                        # Scratchpad 和 cache 都是 SRAM，差异在哪
│   ├── npu-weight-buffer-activation-buffer.md        # NPU 里的 SRAM buffer：weight/activation/accumulator
│   └── tcm-itcm-dtcm-in-mcu.md                       # MCU 里的 TCM——为什么实时性需要确定性 SRAM
│
├── 04-dram-foundations/                              # DRAM 主线：从单元到阵列
│   ├── README.md
│   ├── 1t1c-cell-destructive-read.md                 # 1T1C cell——一颗电容为什么改变了一切
│   ├── refresh-the-fundamental-cost.md               # 刷新：DRAM 的原罪和它的代价
│   ├── row-column-decode-sense-amplify.md            # 行列解码与读出放大：为什么 DRAM 必须"先开行"
│   ├── row-buffer-as-cache.md                        # Row buffer：DRAM 内部的小 cache
│   ├── bank-organization-parallelism.md              # Bank 为什么是 DRAM 并行性的最小单位
│   ├── bank-group-prefetch-burst.md                  # Bank group、prefetch、burst：高频接口下的必然演化
│   └── dram-process-stacking-trends.md               # DRAM 工艺路线：平面 → 堆叠 → 3D
│
├── 05-dram-protocol-families/                        # DRAM 协议层
│   ├── README.md
│   ├── commands-act-rd-wr-pre.md                     # ACT/RD/WR/PRE：DRAM 命令集为什么长这样
│   ├── timing-parameters-trcd-trp-tras.md            # 关键 timing 参数：tRCD/tRP/tRAS/tCL 的物理来源
│   ├── why-double-data-rate.md                       # DDR：为什么要在时钟两边都传数据
│   ├── ddr-generation-evolution.md                   # DDR1 → DDR5：每一代的核心改变是什么
│   ├── lpddr-low-power-mobile.md                     # LPDDR：为了功耗放弃了什么
│   ├── gddr-graphics-bandwidth.md                    # GDDR：为带宽放弃了什么
│   ├── hbm-stacked-wide-io.md                        # HBM：从协议层面看它和 DDR 的根本不同
│   └── ddr-lpddr-gddr-hbm-tradeoff-map.md            # 四种 DRAM 协议的 trade-off 全景图
│
├── 06-memory-controller/                             # MC 单独成章：DRAM 系统的核心
│   ├── README.md
│   ├── why-mc-is-the-real-bottleneck.md              # 为什么说 DRAM 的实际性能由 MC 决定
│   ├── command-scheduling-fr-fcfs.md                 # 命令调度：FR-FCFS 及其变体
│   ├── page-policy-open-close-adaptive.md            # Open/close/adaptive page policy 的权衡
│   ├── refresh-management-distributed-postponed.md   # Refresh 调度：分散刷新、推迟刷新、bank-level refresh
│   ├── write-buffer-write-drain.md                   # 写缓冲与 write drain：为什么读优先
│   ├── address-mapping-channel-rank-bank-row-col.md  # 地址映射：物理地址到 channel/rank/bank/row/col 的拆分艺术
│   ├── qos-multi-master-arbitration.md               # 多 master 场景下的 QoS 与公平性
│   └── mc-modeling-for-simulation.md                 # MC 在 cycle-level 仿真里的建模方法
│
├── 07-system-architecture/                           # 系统视角：把存储器拼回完整系统
│   ├── README.md
│   ├── bandwidth-vs-latency-fundamental.md           # 带宽与延迟：为什么不能兼得
│   ├── effective-bandwidth-vs-peak.md                # 峰值带宽 vs 有效带宽：损失发生在哪里
│   ├── cache-dram-coordination.md                    # Cache 和 DRAM 如何协同——miss 之后发生了什么
│   ├── numa-multi-channel-multi-socket.md            # 多通道、多 socket、NUMA：扩展带宽的代价
│   ├── memory-hierarchy-as-system.md                 # 把 register/cache/scratchpad/DRAM/HBM 看作一个系统
│   ├── sram-vs-dram-access-pattern.md                # SRAM 和 DRAM 在访问模式上的根本区别（压轴对比）
│   └── why-systems-choose-different-memory.md        # MCU/CPU/GPU/NPU 选择不同存储器的逻辑
│
├── 08-packaging-integration/                         # 封装与集成
│   ├── README.md
│   ├── dimm-sodimm-traditional-forms.md              # 传统封装：DIMM/SODIMM 的电气与机械约束
│   ├── pop-mcp-mobile-integration.md                 # PoP/MCP：移动端的集成方式
│   ├── hbm-2.5d-3d-tsv.md                            # HBM 的 2.5D/3D 集成与 TSV 技术
│   ├── why-hbm-is-expensive.md                       # HBM 的成本结构
│   └── future-packaging-cxl-near-memory.md           # CXL、近存计算、未来封装方向
│
├── 09-ai-chip-memory-architecture/                   # AI 芯片场景重点章节
│   ├── README.md
│   ├── npu-memory-hierarchy.md                       # NPU 的存储层次：L0/L1/L2 SRAM + HBM/LPDDR
│   ├── weight-buffer-design.md                       # Weight buffer 的容量与组织：从 model size 反推
│   ├── activation-buffer-and-double-buffering.md     # Activation buffer 与 double buffering：data movement 与 compute 的重叠
│   ├── on-chip-bandwidth-budget.md                   # NPU 的 on-chip 带宽预算从哪来、到哪去
│   ├── hbm-vs-lpddr-for-npu.md                       # NPU 选 HBM 还是 LPDDR——决策框架
│   ├── data-movement-first-principle.md              # "数据搬运优先"原则在 NPU 设计中的体现
│   └── memory-bound-vs-compute-bound.md              # Memory bound vs compute bound 的本质与缓解策略
│
└── 10-reference/                                     # 参考资料
    ├── README.md
    ├── first-principles.md                           # 存储器设计的第一性原理清单
    ├── glossary.md                                   # 术语表
    ├── high-frequency-questions.md                   # 高频问答
    ├── timing-parameter-cheatsheet.md                # DRAM timing 参数速查
    ├── sram-design-checklist.md                      # SRAM 设计/选型 checklist
    ├── dram-debug-checklist.md                       # DRAM 系统调试 checklist
    └── memory-modeling-template.md                   # 存储器在架构探索中的建模模板
```

**目录结构的关键设计决策**：

1. **SRAM 在前、DRAM 在后**：SRAM 是"理解 RAM 本质"的最小完备模型——6T cell、字线/位线、sense amp，所有基本概念在 SRAM 里就是干净的。DRAM 是在此基础上叠加了"破坏性读出 + 周期性刷新 + 行缓冲 + 高速接口"等一层层复杂性。这个顺序让"基础物理 → 工程复杂度"的演化路径自然展开
2. **SRAM 分两章**（foundations + applications）：因为 SRAM 的复杂度主要在"它被怎么用"上，cell 本身相对简单。把应用形态独立成章，正好把 register file/cache/scratchpad/NPU buffer 这些容易混淆的概念厘清
3. **DRAM 也分两章**（foundations + protocols）：物理层和协议层的设计动机完全不同，混在一起讲会丢失因果关系
4. **Memory Controller 独立成章**：MC 是协议视角和系统视角的桥梁，集中讲 scheduling/page policy/refresh/QoS——这是你做 NPU 架构建模时绕不开的部分
5. **AI 芯片场景独立成章并放在最后**：作为前面所有知识的应用场景，而非平行主线
6. **"SRAM vs DRAM 访问模式对比"放在 system view 的压轴位置**：只有前面把两者都讲完后，对比才有真正的深度

---

## 重写的深度定位

### 正文：架构师视角

每一个概念必须回答这三个问题中的至少两个：

1. **设计动机**：这个机制是为了解决什么物理/电气/系统约束？如果没有它会怎样？
2. **Trade-off**：选择这个设计放弃了什么？竞争方案是什么？什么场景下另一个方案更好？
3. **演化路径**：这个设计是从什么前身演化来的？比如 DDR 的 prefetch 深度是怎么从"cell 慢 / IO 快"的剪刀差反推出来的？

**严禁**只写"X 是什么，包含 A/B/C 三类"这种平铺罗列。如果一个段落只是在定义术语，必须紧跟一段"为什么需要这个区分"。

### 每篇文末固定小节：「建模启示」

在每篇文档末尾，加一个标题为 `## 建模启示` 的小节，回答：

- 这个机制在 cycle-level / event-driven 仿真里应该如何抽象？
- 哪些状态变量是必须显式建模的？哪些可以抽象掉？
- 如果只关心性能（latency / bandwidth / SLA），哪些细节可以折叠？如果关心功能验证，哪些细节必须保留？
- 至少给出一个具体的状态变量名 / 事件类型名 / 数据结构草图，禁止只讲抽象方法论

这一小节**不需要**和 archax 的具体术语（Resource/Topology/Interaction/Capability）强行绑定——只在 `06-memory-controller/` 的最后一篇、`07-system-architecture/` 章节和 `09-ai-chip-memory-architecture/` 章节里才显式使用这套抽象。其他章节保持存储器知识本身的纯粹性。

### 类比的使用原则

**适度类比，关键处用**：

- 只在引入一个**反直觉**或**初学者最容易混淆**的概念时使用类比（如：destructive read 为什么必须 write back、row buffer 为什么是"小 cache"、prefetch 深度为什么是"cell-IO 频率剪刀差"的产物、sense amp 为什么必须先 precharge）
- **一个概念至多一个类比**，类比之后立刻回到精确语言
- **避免**过度通俗化的类比
- 如果某概念在精确语言里就能讲清楚，**不要为了"通俗"硬加类比**
- 类比要**有张力**：好的类比应该揭示一个非平凡的结构相似性

---

## 内容质量的具体标准

### 必须做到

1. **每个设计决策都要有"因为...所以..."**：例如不要只说"DRAM 需要 refresh"，要说"因为 1T1C cell 用电容存储电荷、电容会通过亚阈值漏电和结漏电流逐渐放电，典型保持时间在 64ms 量级；为了在这个时间内重新写回所有 cell，又不能完全占用 bank，所以诞生了 distributed refresh、bank-level refresh 等调度策略"
2. **对比要尖锐**：SRAM vs DRAM、open vs close page policy、HBM vs GDDR vs LPDDR、scratchpad vs cache，每一对比都要给出"什么场景选谁，代价是什么"的明确判断
3. **波形/时序示例**：在讲 DRAM 命令时序、SRAM 读写 cycle、refresh 调度等时，至少给一个 ASCII 时序图或 markdown 表格表示的 cycle-by-cycle 行为
4. **真实硬件锚点**：尽量提到真实场景的具体数字（DDR5 的 tRCD 量级、HBM3 的 stack 配置、典型 NPU 的 on-chip SRAM 容量量级、DRAM cell 的保持时间）。如果不确定具体数字，明确说"典型量级在 X-Y 之间"而不是编造
5. **指明常见误解**：每个核心概念后给一句"常见误解：...，实际上：..."
6. **物理层和系统层都要触及**：讲 DRAM 不能只讲协议时序，要讲到电容电荷、sense amp 工作原理；但也不能只讲电路，要回到系统看它带来的约束

### 必须避免

1. **不要使用 emoji**
2. **不要堆砌 bullet list**：能用连贯论述讲清的不要拆成 bullet。bullet 只用于真正的并列枚举
3. **不要写"通常""一般""有时"这种含糊词**——要么给条件，要么给具体例子
4. **不要在每段开头都用粗体小标题**——这是 AI 生成内容的典型坏味道
5. **不要重复**：同一个概念在同一篇文档里不要换着说法讲两遍
6. **不要"水"过渡句**：诸如"接下来我们看看..."这类承上启下的废话直接删
7. **不要假装有经验**：case study 如果是构造的，明确写"构造案例"；不要用"在实际项目中我们..."这种伪装

---

## 工作流程

### Step 1：先阅读理解全局

在动笔之前，**完整阅读** `./RAM/wiki/` 旧目录下所有现有文件，以及 `./RAM/raw/` 下的 `chat_0.md`、`chat_1.md`、`chat_2.md`（这些是原始素材，可能有可复用的内容）。建立对现有材料的全局认识，识别：

- 哪些旧文件的内容可以作为新目录某一篇的素材
- 哪些内容需要彻底推翻
- 哪些 SRAM 相关内容完全缺失，需要从零写起
- raw 目录里有没有未被旧 wiki 吸收的有价值素材

### Step 2：备份旧 wiki，按新目录建空骨架

1. 先把现有的 `./RAM/wiki/` 整体重命名为 `./RAM/wiki.old/` 作为备份
2. 按新目录结构在 `./RAM/wiki/` 下建立空骨架（所有目录 + 每个 .md 文件含标题但内容为空 + 占位说明）
3. 让我 review 骨架，确认无误后才开始填内容

### Step 3：按章节顺序重写，不跳跃

按 `01 → 10` 的顺序重写。**不要并行处理多个章节**，因为后面章节会引用前面章节的术语，必须先把前面的语言体系建立起来。

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

- `02-sram-foundations/`、`04-dram-foundations/`：偏物理与电路，可以较长，需要时序图
- `05-dram-protocol-families/`、`06-memory-controller/`：协议与算法层，每篇要有具体的命令序列或调度示例
- `07-system-architecture/`、`09-ai-chip-memory-architecture/`：系统层，需要数据流图或带宽预算表
- `10-reference/`：checklist / glossary 类，保持简短紧凑

### Step 5：交叉引用

重写时**主动建立**文件之间的交叉引用。SRAM 章节讲到 sense amp 时，应该链接到 DRAM 的 sense amp 讨论并指出差异；DRAM 的 row buffer 应该链接到 cache 的概念并指出"它为什么不完全是 cache"。原 wiki 的链接太稀疏，重写后应当形成一张有内在结构的知识网。

### Step 6：在 06 末篇、07、09 章节才显式连接 archax 方法论

只有在 `06-memory-controller/mc-modeling-for-simulation.md`、`07-system-architecture/` 章节和 `09-ai-chip-memory-architecture/` 章节里，可以在「建模启示」小节中显式提到 Resource/Topology/Interaction/Capability 这套抽象，讨论"如果用这套抽象来描述这个存储行为，每个轴上是什么"。其他章节保持知识本身的独立性，不要硬塞框架术语。

---

## 一个示范：`04-dram-foundations/refresh-the-fundamental-cost.md` 应该怎么写

如果这篇只写"DRAM 每隔 64ms 需要刷新所有 cell"，那就是失败的写法。应该这样组织：

**核心问题**：Refresh 不是 DRAM 的一个"特性"，而是它的"原罪"——理解 refresh 就等于理解 DRAM 为什么和 SRAM 走向了完全不同的演化路径。

正文应该讲：

- 1T1C cell 用电容存储电荷，电容必然漏电（亚阈值漏电、结漏电流、栅氧化层漏电），物理上不可消除
- 保持时间为什么定在 64ms（典型值）——这是 worst case cell 的保留电荷能被 sense amp 正确判别的时间上限
- 为什么所有 cell 必须在 64ms 内被 refresh 一遍——一旦超过，数据就丢了
- Refresh 的代价不只是"时间损失"，而是：(a) bank 被占用期间无法服务正常访问；(b) refresh 期间的功耗峰值；(c) 现代 DRAM 容量上升导致 refresh 总开销占比上升（DDR4 之后已经到 20% 量级）
- 工程上的应对：distributed refresh（把 refresh 摊开）、bank-level refresh（只锁一个 bank）、postponed refresh（推迟一部分换灵活性）、fine-grained refresh（DDR4+ 引入）
- 为什么 LPDDR 引入了 self-refresh 和 partial-array self-refresh——移动场景的功耗权衡
- 为什么 HBM 的 refresh 调度比 DDR 更复杂——堆叠后 die 温度变化大，refresh interval 需要动态调整

然后「建模启示」回答：在 cycle-level 仿真里，refresh 不能简单建模为"每隔 7.8us 阻塞 bank 一次"，而要建模成一个**带状态的调度问题**——MC 的 refresh queue、postpone 计数、当前 bank 的 refresh credit、温度反馈（在精确建模温度时）。如果只关心 SLA-level 性能，可以折叠为"每个 bank 每 X 周期损失 Y% 带宽"的简化模型；如果关心 worst-case latency 分析，refresh 必须显式建模为可被 schedule 的事件。

**这就是我要的深度**。请用类似的方式重写每一篇。

---

## 开始之前

1. 先告诉我你**完整读完旧 `./RAM/wiki/` 和 `./RAM/raw/`** 之后对原内容的整体诊断：
   - 旧 wiki 哪些内容可以作为新结构里某篇的素材（请列对应关系）
   - raw 目录里有没有未被吸收的有价值素材
   - 新目录里哪些文件需要完全从零写起（特别是 SRAM 部分）
2. 然后告诉我你打算如何分批次提交重写（建议按文件而不是按章节批量提交，每个文件都让我能 review）
3. 等我确认后再开始建空骨架（Step 2）

不要急着动手。重写质量取决于你对全局的理解和对新目录设计的认同。如果你看完旧内容和新目录后认为目录还有可改进的地方，请提出，等我确认再改。