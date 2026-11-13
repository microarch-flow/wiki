# 学习路径与各章节依赖关系

<span id="这页在回答什么问题"></span>
<span id="先修知识与学习次序"></span>

上级：[RAM 阅读路线](./README.md)

相关：[RAM 分类与命名](../../01-memory-hierarchy/01-system-basics/taxonomy.md) · [存储系统建模模板](../02-reference/memory-modeling-template.md)

<p class="ram-problem-lede">先确定要回答的问题，再选择阅读路径。理解器件原理、构建 DRAM 命令模型和分析 NPU 片上 buffer，需要的细节并不相同。</p>

本文给出章节地图和几条按目标选择的路径。它们是阅读建议，不是要求每位读者先完成全部底层章节。遇到不熟悉的概念时，可以沿链接回读。

## 1. 每一章负责回答什么？

| 章节 | 主要问题 |
| --- | --- |
| [存储系统概览](../../01-memory-hierarchy/README.md) | 存储资源有哪些角色？请求、工作负载和设计约束如何联系起来？ |
| [SRAM 基础](../../02-sram/foundations/README.md) | 6T cell、读写路径、端口和阵列组织如何工作？ |
| [SRAM 应用形态](../../02-sram/applications/README.md) | Cache、scratchpad、register file 和其他角色如何使用存储资源？ |
| [DRAM 基础](../../03-dram/foundations/README.md) | 1T1C cell、row buffer、bank 和刷新带来哪些约束？ |
| [DRAM 协议层](../../03-dram/protocols/README.md) | 控制器使用什么命令、时序和接口访问 DRAM？ |
| [Memory Controller](../../04-dram-controller/README.md) | 请求如何映射、排队和调度？哪些资源会竞争？ |
| [系统视角](../../01-memory-hierarchy/01-system-basics/README.md) | 多层存储与互连怎样共同影响延迟和有效带宽？ |
| [封装与集成](../../06-system-integration/packaging/README.md) | DIMM、堆叠和封装连接怎样影响系统选择？ |
| [AI 芯片内存架构](../../01-memory-hierarchy/04-npu-case/README.md) | NPU 怎样安排 buffer、数据复用和外存供数？ |
| [参考资料](../02-reference/README.md) | 术语、时序、检查清单和建模模板如何查阅？ |

如果希望系统学习，可以按上表从概览读到 AI 芯片章节，并在需要时查阅参考资料。这个顺序先介绍部件，再组合成系统；它不是唯一的学习顺序。

## 2. 想先建立全貌：从请求和指标入手

1. 从[存储系统为何难设计](../../01-memory-hierarchy/01-system-basics/problem-statement.md)看一次请求如何经过多层资源。
2. 用 [RAM 分类与命名](../../01-memory-hierarchy/01-system-basics/taxonomy.md)区分单元、角色、接口和集成方式，再用[速度·容量·成本·功耗](../../01-memory-hierarchy/01-system-basics/memory-hierarchy-tension.md)确定比较指标。
3. 阅读[局部性与数据搬运](../../01-memory-hierarchy/01-system-basics/locality-working-set-data-movement.md)，了解访问序列和工作集如何影响跨层流量。
4. 转到[存储层次与系统角色](../../01-memory-hierarchy/01-system-basics/memory-hierarchy-as-system.md)，把不同存储资源和数据路径放回同一个系统。

这条路径适合先建立系统地图。它不会完整解释 SRAM 电路或 DRAM 命令；需要判断器件内部行为时，应回读相应基础章节。

## 3. 想建立 DRAM 命令模型：从行状态到调度

1. 先读[1T1C 存储单元](../../03-dram/foundations/1t1c-cell-destructive-read.md)和 [Row buffer](../../03-dram/foundations/row-buffer-as-cache.md)，理解开行、感测和已打开行的作用。
2. 再读 [DRAM 命令集](../../03-dram/protocols/commands-act-rd-wr-pre.md)和 [DRAM 时序参数](../../03-dram/protocols/timing-parameters-trcd-trp-tras.md)，确认命令、参考边沿和模式条件。
3. 在控制器章节，先看[地址映射](../../04-dram-controller/address-mapping-channel-rank-bank-row-col.md)，再看[命令调度与 FR-FCFS](../../04-dram-controller/command-scheduling-fr-fcfs.md)和[刷新调度](../../04-dram-controller/refresh-management-distributed-postponed.md)。这个顺序先说明请求落在哪里，再讨论何时服务。
4. 用[控制器仿真建模](../../04-dram-controller/mc-modeling-for-simulation.md)和 [DRAM 时序速查](../02-reference/timing-parameter-cheatsheet.md)检查模型状态、时序与参数来源。

如果问题是比较 page policy、地址映射或刷新对延迟的影响，模型通常需要表达相应的行状态、队列、时序和资源竞争。具体保留哪些状态，应由问题与目标协议决定；只填一个平均延迟，不能独立推导这些策略变化的影响。

## 4. 想分析 NPU 片上 buffer：从资源到搬运

1. 读 [SRAM 宏接口与读写语义](../../02-sram/foundations/sram-macro-interface-and-semantics.md)、[SRAM 端口与代价](../../02-sram/foundations/single-port-dual-port-multi-port.md)、[SRAM 阵列组织](../../02-sram/foundations/sram-array-organization.md)和 [bank 地址映射与冲突](../../02-sram/foundations/sram-bank-address-mapping-conflicts.md)，确定接口、端口、bank 和共享通路的含义。
2. 读 [Cache 与 scratchpad](../../01-memory-hierarchy/02-access-paths/cache-vs-scratchpad.md)和 [NPU 的 SRAM buffer](../../02-sram/applications/npu-weight-buffer-activation-buffer.md)，区分数据角色与管理方式。
3. 按问题选择 [Weight buffer 设计](../../01-memory-hierarchy/04-npu-case/weight-buffer-design.md)、[激活缓冲与双缓冲](../../01-memory-hierarchy/04-npu-case/activation-buffer-and-double-buffering.md)和[片上带宽预算](../../01-memory-hierarchy/04-npu-case/on-chip-bandwidth-budget.md)。
4. 如果涉及 DMA 与计算的交接，再看 DMA 专题的[同步、一致性与常见错误](../../../microarchitecture/DMA/wiki/04-programming-model/synchronization-errors.md)。

分析双缓冲时，要确认数据何时可见、何时允许覆盖，以及搬运和计算是否真的有独立资源。若问题还涉及外存选型或控制器瓶颈，应补读 DRAM 协议、控制器和封装章节，不能只用片上 buffer 参数代替外存路径。

## 5. 想定位系统瓶颈：先统一观察边界

先读[带宽与延迟](../../01-memory-hierarchy/03-performance/bandwidth-vs-latency-fundamental.md)和[峰值与有效带宽](../../01-memory-hierarchy/03-performance/effective-bandwidth-vs-peak.md)，明确观察的是哪条路径、哪段时间和哪些字节。再读 [Cache miss 的处理](../../01-memory-hierarchy/02-access-paths/cache-dram-coordination.md)，沿请求路径检查缓存、互连、控制器和存储器。

如果怀疑请求集中到少数 bank，继续看[地址映射](../../04-dram-controller/address-mapping-channel-rank-bank-row-col.md)；如果怀疑排队或命令选择影响结果，继续看[命令调度与 FR-FCFS](../../04-dram-controller/command-scheduling-fr-fcfs.md)。行命中率或接口利用率都需要结合请求供给和观测点解释，不能单独证明瓶颈在哪里。

## 6. 先修知识与推荐顺序有什么区别？

有些概念是回答特定问题的必要前提。例如，要解释一条 DDR4 轨迹中的 ACT 到 RD 间隔，就需要知道命令含义、目标模式和时序参考边沿。只知道“DRAM 有延迟”，不能判断该轨迹是否合法。

另一些内容是为了建立更完整的理解而推荐先读。例如，比较 SRAM bank 冲突时，可以先依据目标宏的端口和地址映射建模，不必先模拟每根位线的电气行为。但如果要解释 cell 稳定性或电路时序，就需要回到相应电路和器件资料。

模型细节应随问题选择。[gem5 的 SimpleMemory 文档](https://www.gem5.org/documentation/general_docs/stdlib_api/gem5.components.memory.simple.html)描述了用延迟和带宽配置的简化存储系统；[gem5 的控制器说明](https://www.gem5.org/2020/05/27/memory-controller.html)则讨论队列、调度和存储接口。两类模型能回答的问题不同。它们的参数和结果都需要限定工作条件，不能仅凭模型存在就当作真实芯片测量。

## 一句话理解

先选目标和观察边界，再补回答该问题所需的前提；完整阅读顺序有助于建立全貌，但不是所有任务的强制入口。

## 建模启示

可以用四个问题检查选定的抽象：

1. **输入是什么？**例如地址、请求大小、到达时间和数据依赖。
2. **资源和状态是什么？**例如端口、bank、队列，或需要时的 DRAM 行状态与时序约束。
3. **输出和观察边界是什么？**例如请求何时被接纳、数据何时可用、在哪个接口统计字节。
4. **参数和结论适用于哪里？**记录协议、器件、时钟、工作负载和校准来源，并说明模型不能区分的情况。

这些问题用于选择模型，而不是要求所有模型都模拟到相同层级。参考资料可随时查阅：[术语表](../02-reference/glossary.md)、[存储系统建模模板](../02-reference/memory-modeling-template.md)和相关检查清单都不要求先按顺序读完。
